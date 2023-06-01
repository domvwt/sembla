import ast
import json
import re
import subprocess
from collections import defaultdict
from functools import wraps
from pathlib import Path
from tempfile import NamedTemporaryFile
from textwrap import dedent

import requests
import wikipedia

import sembla.utils.markdown as md
from sembla.actions.ai_assistant import query_assistant
from sembla.schemas.actions import Action


class TaskSubmission:
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return f"TaskSubmission(args={self.args}, kwargs={self.kwargs})"

    def __str__(self):
        return f"TaskSubmission(args={self.args}, kwargs={self.kwargs})"


def _truncate_output(output: str, max_length: int = 1000) -> str:
    if isinstance(output, str) and len(output) > max_length:
        output = output[:max_length]
        output += "..."
    return output


def truncate_output(func):
    """Decorator to truncate output of a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        return _truncate_output(output)

    return wrapper


# Special
def submit_completed_task(*args, **kwargs):
    """Submit completed task to the user."""
    return TaskSubmission(
        args,
        kwargs,
    )


def no_action(*args, **kwargs):
    """No action."""
    return "No action."


# Filesystem
def list_directory(directory):
    """List contents of `directory`."""
    directory = Path(directory)
    contents = [item.name for item in directory.iterdir()]
    markdown_contents = "\n".join([f"- {item}" for item in contents])
    return markdown_contents


def directory_tree(directory):
    """Get tree structure of `directory`."""

    def tree(directory, prefix=""):
        directory = Path(directory)

        if not directory.is_dir():
            raise ValueError(f"{directory} is not a directory.")

        entries = [
            entry for entry in directory.iterdir() if not entry.name.startswith(".")
        ]
        tree_string = ""

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            if entry.is_dir():
                tree_prefix = "└── " if is_last else "├── "
                tree_string += prefix + tree_prefix + entry.name + "\n"
                new_prefix = "    " if is_last else "│   "
                tree_string += tree(entry, prefix + new_prefix)
            else:
                tree_prefix = "└── " if is_last else "├── "
                tree_string += prefix + tree_prefix + entry.name + "\n"

        return tree_string

    return tree(directory)


def find_files(directory, pattern):
    """Find files in `directory` that match the `pattern`."""
    directory = Path(directory)
    matching_files = [str(file) for file in directory.glob(pattern)]

    if matching_files:
        result = "\n".join([f"- {file}" for file in matching_files])
    else:
        result = "none"

    return f"matching files:\n{result}"


def create_directory(directory):
    """Create `directory`."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return f"directory created: {directory}"


def create_file(filename):
    """Create `filename`"""
    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    # file_path.write_text(content)
    return f"file created: {filename}"


# NOTE: Agents read files out of curiosity(?!), wasting tokens and time.
# @truncate_output
def read_file(filename):
    """Read contents of `filename`."""
    file_path = Path(filename)
    return file_path.read_text()


def write_to_file(filename, content):
    """Write `content` to `filename`. Overwrites existing file."""
    file_path = Path(filename)
    file_path.write_text(content)
    return f"file updated: {filename}"


def append_to_file(filename, content):
    """Append `content` to `filename`."""
    file_path = Path(filename)
    file_path.write_text(file_path.read_text() + content)
    return f"file updated: {filename}"


def replace_in_file(filename, old, new):
    """Replace text `old` with `new` in `filename`."""
    file_path = Path(filename)
    file_path.write_text(file_path.read_text().replace(old, new))
    return f"file updated: {filename}"


# NOTE: Agents seem to like moving files around for no apparent reason.
def move_file(source, destination):
    """Move `source` to `destination`."""
    source_path = Path(source)
    destination_path = Path(destination)
    source_path.rename(destination_path)
    return f"file moved: {source} -> {destination}"


# def delete_file(filename):
#     """Delete `filename`."""
#     file_path = Path(filename)
#     file_path.unlink()
#     return f"file deleted: {filename}"


# Research
# def google_search(query):
#     """Search Google for `query` and return the results as a string."""
#     # You need to use the Google Search API and obtain an API key.
#     # TODO: Use serpapi here
#     pass


@truncate_output
def wikipedia_summary(query):
    """Search Wikipedia for `query`."""
    query = query.replace(" ", "")
    return wikipedia.summary(query)


# Development
# AI Assistant
def generate_code_for(requirements: str, goal: str, filename: str):
    """Generate code that meets `requirements` given `goal` for `filename`."""
    if len(filename) < 5:
        return f"filename must be at least 5 characters long: {filename}"
    prompt = f"""\
Write code file {filename} that meets requirements:\n{requirements}.
Additional context:\n{goal}
Include a module docstring at the top of the file.
Write one line of documentation for each function.
Make your code concise and efficient.
Code should be written in full with no placeholders.
"""
    response = query_assistant(prompt)
    code = md.get_largest_code_block(response)
    print(code)
    Path(filename).write_text(code)
    return f"""
code written to: {filename}
code:
{code}
recommendation: verify with static_code_analysis action
"""


# @truncate_output
# def write_documentation_for(filename):
#     """Write documentation for `filename`."""
#     code_path = Path(filename)
#     if not code_path.exists():
#         return f"file not found: {filename}"
#     code = code_path.read_text()
#     prompt = f"Write comments, docstrings, and typehints for:\n{code}."
#     response = query_assistant(prompt)
#     code = md.get_largest_code_block(response)
#     output_file = Path(filename)
#     output_file.write_text(code)
#     return f"""\ndocumentation written for: {filename}"""


@truncate_output
def execute_code(filename, command_line_args=None, output_filename=None):
    """Execute `filename` with `command_line_args`. Optionally write output to `output_filename`."""
    args = ["python", filename]
    if command_line_args:
        args.extend(command_line_args)
    result = subprocess.run(args, capture_output=True, text=True)
    if output_filename:
        output_file = Path(output_filename)
        output_file.write_text(result.stdout)
        return f"output written to: {output_filename}"
    return dedent(
        f"""\
```bash
> {' '.join(args)}
{result.stdout}
{result.stderr}
```
"""
    ).strip()


def read_documentation(filename):
    """Read the documentation for `filename`."""
    source_code = Path(filename).read_text()
    module = ast.parse(source_code)
    documentation = {}
    # Get module-level docstring
    documentation["module"] = ast.get_docstring(module)
    # Extract docstrings from classes and functions
    for node in module.body:
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            documentation[node.name] = ast.get_docstring(node)
        elif isinstance(node, ast.ClassDef):
            class_doc = {}
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef) or isinstance(
                    class_node, ast.AsyncFunctionDef
                ):
                    class_doc[class_node.name] = ast.get_docstring(class_node)
            documentation[node.name] = {
                "doc": ast.get_docstring(node),
                "methods": class_doc,
            }
    # Return documentation as a string
    return json.dumps(documentation, indent=2)


@truncate_output
def static_code_analysis(filename) -> str:
    """Run static code analysis on `filename`."""
    # subprocess.run(["black", filename], capture_output=True, text=True)
    # subprocess.run(["isort", filename], capture_output=True, text=True)
    output = subprocess.run(
        ["flake8", "--select=E,F", "--max-line-length=120", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    result = (str(output.stdout) + str(output.stderr)).strip()
    result = result or "No errors found."
    return f"""\
```bash
> flake8 {filename}
{result}
```
"""


def generate_test_cases(filename):
    """Generate test cases for `filename`."""
    code_path = Path(filename)
    if not code_path.exists():
        return f"file not found: {filename}"
    code = code_path.read_text()
    prompt = f"""\
Write unit tests for the following code.
Test will be run with pytest.
Code:\n{code}."
"""
    response = query_assistant(prompt)
    code = md.get_largest_code_block(response)
    # Add test_ prefix to filename.
    output_filename = f"test_{filename}"
    Path(output_filename).write_text(code)
    return f"""\
test cases written to: {output_filename}
recommendation: verify with run_test_cases action
"""


# Quality Assurance
def run_test_cases():
    """Run unit tests for project."""
    result = subprocess.run(["pytest"], capture_output=True, text=True)
    return dedent(
        f"""\
```bash
> pytest .
{result.stdout}
{result.stderr}
```
"""
    ).strip()


def fix_issues_in(filename, issues):
    """Fix `issues` in `filename`."""
    code_path = Path(filename)
    if not code_path.exists():
        return f"file not found: {filename}"
    code = code_path.read_text()
    prompt = f"Fix issues in the following code\nissues:\n{issues}\ncode:\n{code}."
    response = query_assistant(prompt)
    code = md.get_largest_code_block(response)
    Path(filename).write_text(code)
    return f"""
fixes implemented for: {filename}
recommendation: verify with static_code_analysis action
"""


# Design
# def generate_ui_prototype(input_data):
#     """Generate a UI prototype from `input_data` and return the URL."""
#     # You'll need to choose a specific library or method for generating UI prototypes.
#     pass


def generate_content_for(filename, brief, goal):
    """Generate content that meets `brief` given `goal` for `filename`."""
    if len(filename) < 5:
        return f"filename must be at least 5 characters long: {filename}"
    prompt = f"""
Write content for {filename} that meets the following requirements:\n{brief}.
Additional context:\n{goal}
There must be no additional dialogue in your response.
"""
    content = query_assistant(prompt)
    Path(filename).write_text(content)
    return f"""
content written to: {filename}
recommendation: verify contents with read_file action
"""
