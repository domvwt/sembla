import logging
from textwrap import dedent
from typing import Iterable, List, Optional, Union

from sembla.actions import ActionModule
from sembla.conversation_history import ConversationHistory, Message
from sembla.llm.openai.chat_completion import ChatCompletion
from sembla.prompt.handler import PromptHandler
from sembla.response.handler import ResponseHandler
from sembla.response.processor import ResponseProcessor
from sembla.schemas.actions import Action
from sembla.schemas.base import BaseModel


# TODO: Refactor this class so that it is more modular and easier to test.
# TODO: Get GPT-4 to do the refactoring.
# TODO: If the user wants a structured response, we should maybe add a parser to the response handler.
# TODO: Instead of supplying args, supply instances of modules.
# TODO: Model should also be an instance of a class.
# TODO: Might need to add an agent factory to facilitate building.
# TODO: Operator class: chat, prompt, auto, supervised, max_iterations, max_tokens, max_time
# TODO: Supervised agents require human approval to perform actions.
# TODO: Serialise all of this to JSON/YAML
# TODO: yaml can go with the prompt, or the prompt can also be a config setting?
# TODO: offer some predefined agents and simplified builders
class AgentBase:
    def __init__(
        self,
        model: Optional[str] = None,
        agent_role: str = ...,
        agent_instructions: Optional[str] = None,
        agent_actions: Optional[List[Action]] = None,
        example_response: Optional[BaseModel] = None,
        structured_response_format: Optional[str] = "yaml",
        response_processors: Optional[Iterable[ResponseProcessor]] = None,
        initial_memory: Optional[List[Message]] = None,
        max_history_message_count=50,
        max_history_token_count=None,
    ):
        if model is None:
            model = "gpt-3.5-turbo"

        if agent_actions:
            action_module = ActionModule(actions=agent_actions)
        else:
            action_module = None

        self.model = model
        self._task = agent_instructions
        self._task_types = agent_actions
        self._action_module = action_module
        self._response_format = example_response
        self._initial_memory = initial_memory
        self._conversation_history = ConversationHistory(
            model=model,
            max_history_message_count=max_history_message_count,
            max_history_token_count=max_history_token_count,
        )
        if example_response and structured_response_format:
            if structured_response_format == "yaml":
                example_response_str = example_response.to_yaml()
            elif structured_response_format == "json":
                example_response_str = example_response.to_json()
            else:
                raise ValueError(
                    f"Invalid structured_response_format: {structured_response_format}. "
                    "Must be one of: yaml, json"
                )
        else:
            example_response_str = None
        self._prompt_handler = PromptHandler(
            agent_role=agent_role,
            agent_instructions=agent_instructions,
            action_module=action_module,
            example_response=example_response_str,
        )
        system_prompt = self._prompt_handler.generate_system_prompt()
        self._conversation_history.add_message(
            {"role": "system", "content": system_prompt}
        )
        if initial_memory:
            self._conversation_history._extend_history(initial_memory)

        self._response_processors = response_processors
        self._response_handler = ResponseHandler(
            action_module=self._action_module,
            response_processors=self._response_processors,
        )

        self._chat_completion = ChatCompletion(
            model=model, conversation_history=self._conversation_history
        )

        # Print log messages
        logging.info(f"{type(self).__name__} initialized with model: {self.model}")
        logging.info(f"Agent Role: {agent_role}")
        logging.info(f"Agent Instructions: {agent_instructions}")

    def generate_response(self, prompt: str, role: str = "user") -> str:
        """
        Generate a response to a given prompt.

        Args:
            prompt: The prompt to generate a response to.
            role: The role of the agent giving the prompt.

        Returns:
            The generated response.
        """
        if prompt:
            self._conversation_history.add_message({"role": role, "content": prompt})
        logging.info("User prompt: %s", prompt)
        response = self._chat_completion.create()
        return response
