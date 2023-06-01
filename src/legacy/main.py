import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from textwrap import dedent
from typing import Optional

import openai
from rich import prompt as console_prompt
from rich.align import Align
from rich.console import Console
from rich.markdown import Markdown

from sembla.actions.tasks import TaskType
from sembla.agent import PreconfiguredAgents
from sembla.augmentations import ActorCriticAug, Flake8Aug
from sembla.schemas import SingleActionResponse
from sembla.utils import markdown as md

console = Console(width=80)


# TODO: These are in order of priority!!
# TODO: refactor this messy code
# TODO: implement async agents with asyncio (or similar)
# TODO: maybe some handlers should be renamed 'augmentations'? (deus ex reference)
# TODO: augs include: linting, self reflection, autonomy, possibly 'requires code block'
# TODO: actions could be augs if this should be refactored - don't think so though
# TODO: implement augs as callable classes so that they can have their own memory
# TODO: call something like an 'intercept response' method on response generation
# TODO: might need to have an utility agent to determine the language of a code block if we automatically lint it
# TODO: implement action cost, require plan to consider action budget


# TODO: Redefine the augmentations like this:
# TODO: Or we could use a class to define the augmentation so that it has its own memory :thinking:
# class AgentBase:
#     # ... (existing code) ...

#     def __init__(
#         self,
#         # ... (existing arguments) ...
#     ):
#         # ... (existing code) ...

#         self.decorators = []

#     def add_decorator(self, decorator):
#         self.decorators.append(decorator)

#     def generate_response(
#         self, prompt: str, role: str = "user", decorator_args=None
#     ) -> str:
#         """
#         Generate a response to a given prompt.

#         Args:
#             prompt: The prompt to generate a response to.
#             role: The role of the agent giving the prompt.
#             decorator_args: A dictionary containing decorator-specific arguments.

#         Returns:
#             The generated response.
#         """
#         if decorator_args is None:
#             decorator_args = {}

#         response_method = self._generate_response
#         for decorator in self.decorators:
#             response_method = decorator(response_method, **decorator_args.get(decorator, {}))
#         return response_method(prompt, role)

#     def _generate_response(self, prompt: str, role: str = "user") -> str:
#         if prompt:
#             self.conversation_history.add_message({"role": role, "content": prompt})
#         logging.info("User prompt: %s", prompt)
#         response = self.chat_completion.create()
#         return response
#
# def sample_decorator(func, multiplier):
#     def wrapper(prompt, role):
#         response = func(prompt, role)
#         return response * multiplier
#     return wrapper

# agent = AgentBase()
# agent.add_decorator(sample_decorator)

# decorator_args = {
#     sample_decorator: {"multiplier": 2}
# }

# response = agent.generate_response(prompt="Hello!", role="user", decorator_args=decorator_args)


def print_markdown(markdown_str: str, **kwargs):
    console.print(Markdown(markdown_str), **kwargs)


def main():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler("sembla.log", maxBytes=1000000, backupCount=5)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)

    # Remove all other handlers
    for handler in root_logger.handlers:
        if not isinstance(handler, logging.FileHandler):
            root_logger.removeHandler(handler)

    # Navigate to the root directory
    while not Path("src").exists():
        os.chdir("..")

    # Navigate to the workspace directory
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    os.chdir(workspace)

    print_markdown("---")
    console.print(Align.center("Welcome to [bold magenta]SEMBLA LABS[/bold magenta]!"))
    print_markdown("---")

    # Check that the API key is set
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("Please set the OPENAI_API_KEY environment variable")

    # Run the agents
    project_scope_path = Path("project_scope.md")
    if not project_scope_path.exists():
        project_scope = run_agent(
            PreconfiguredAgents.project_scoper(),
            initial_message=None,
            capture_document_single=True,
            output_path="project_scope.md",
        )
        project_scope_path.write_text(project_scope)
    project_scope = project_scope_path.read_text()

    technical_plan_path = Path("technical_plan.md")
    if not technical_plan_path.exists():
        technical_plan = run_agent(
            PreconfiguredAgents.technical_planner(), initial_message=project_scope
        )
        technical_plan_path.write_text(technical_plan)
    technical_plan = technical_plan_path.read_text()

    code_stubs_path = Path("code_stubs.md")
    if not code_stubs_path.exists():
        stub_generator_team = ActorCriticAug(
            actor=PreconfiguredAgents.stub_generator(),
        )
        code_stubs = run_agent(stub_generator_team, initial_message=technical_plan)
        assert isinstance(code_stubs, str)
        code_stubs_path.write_text(code_stubs)
    code_stubs = code_stubs_path.read_text()

    # CODE COMPLETION START
    sections = [
        section for section in md.split_sections(code_stubs) if section.startswith("##")
    ]
    filenames = []
    file_content = []
    for section in sections:
        filename = section.split("## ")[1].split("\n", 1)[0]
        if "__init__" in filename:
            continue
        # If the filename doesn't begin with 'src', add it
        if not filename.startswith("src"):
            filename = "src/" + filename
        filenames.append(filename)
        file_content.append(md.get_largest_code_block(section))

    for filename, stub_code in zip(filenames, file_content):
        code_path = Path(f"../workspace/{filename}")
        code_path.parent.mkdir(parents=True, exist_ok=True)
        message = f"""\
Reference:
{code_stubs}
Return code for {filename}
Completed code:
"""
        # NOTE: It's important to use a new agent for each code block
        code_completion_agent = PreconfiguredAgents.code_completer()
        code_completion_team = Flake8Aug(
            actor=code_completion_agent,
        )
        response = generate_response(code_completion_team, message)
        while not md.has_code_block(response):
            prompt = """Provide the completed code in a code block."""
            response = generate_response(code_completion_agent, prompt)
        code = md.get_largest_code_block(response)
        code_path.write_text(code)
        # Also create an __init__.py file in the directory
        init_path = code_path.parent / "__init__.py"
        if not init_path.exists():
            init_path.touch()
    # CODE COMPLETION END

    # UNIT TESTING START
    for filename in filenames:
        # Replace src with tests
        code_path = Path(f"../workspace/{filename}")
        test_path = code_path.parent / ("test_" + code_path.name)
        unit_testing_agent = PreconfiguredAgents.unit_tester()
        unit_testing_team = Flake8Aug(
            actor=unit_testing_agent,
        )
        code = code_path.read_text()
        if not code.strip():
            continue
        message = f"Write unit tests for:\n{code}"
        response = generate_response(unit_testing_team, message)
        while not md.has_code_block(response):
            prompt = """Provide the unit tests in a code block."""
            response = generate_response(unit_testing_agent, prompt)
        tests = md.get_largest_code_block(response)
        test_path.write_text(tests)
    # UNIT TESTING END

    configurator_input = technical_plan + "\n" + code_stubs
    project_config = run_agent(
        PreconfiguredAgents.project_configurator(), initial_message=configurator_input
    )
    Path("project_config.md").write_text(project_config)
    config_sections = [
        section
        for section in md.split_sections(project_config)
        if section.startswith("##")
    ]
    for section in config_sections:
        filename = section.split("## ")[1].split("\n", 1)[0]
        file_content = md.get_largest_code_block(section)
        file_path = Path(f"../workspace/{filename}")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file_content)


def run_agent(
    agent,
    initial_message: Optional[str] = None,
    capture_document_single: bool = False,
    output_path: Optional[str] = None,
) -> str:
    prompt = None
    response = ""
    captured_document = None
    if initial_message:
        response = generate_response(agent, initial_message)
    while True:
        print_conversation_history(agent, prompt)
        prompt = console.input("[bold]USER:[/bold] ")
        if prompt.lower() in ["exit", "quit", "bye", "done"]:
            if capture_document_single and not captured_document:
                console.print(
                    "[red][bold]SEMBLA:[/bold][/red] No document detected! I'll remind the agent to generate it..."
                )
                prompt = "Generate the final document with horizontal rules (---) indicating the start and end of the document."
                while not captured_document:
                    response = generate_response(agent, prompt, role="system")
                    captured_document = md.capture_document(response)
            if capture_document_single and captured_document:
                print_markdown("---")
                console.print("Final Document", style="bold gold1")
                print_markdown("---")
                print_markdown(captured_document)
                print_markdown("---")
            if console_prompt.Confirm.ask("Are you finished?", choices=["y", "n"]):
                if capture_document_single and captured_document and output_path:
                    Path(output_path).write_text(captured_document)
                    console.print(f"Output saved to {output_path}", style="bold blue")
                    return captured_document
                return response
        response = generate_response(agent, prompt)
        captured_document = md.capture_document(response)


def generate_response(agent, prompt, role="user") -> str:
    with console.status("Please wait..."):
        return agent.generate_response(prompt, role=role)


def print_conversation_history(agent, prompt=None):
    for item in agent.conversation_history.conversation_buffer:
        role = item["role"]
        content = item["content"]
        if not role == "system":
            print_markdown(f"{role.upper()}:", style="bold")
            print_markdown(content, style="italic")
