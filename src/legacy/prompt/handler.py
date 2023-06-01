import logging
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from pydantic import ValidationError

from sembla.actions import ActionModule

# Roles are stored in the roles directory at sembla/roles
# We traverse up until we see the src directory and then go into roles
ROLES_DIRECTORY_PATH = Path(__file__).parent.parent / "roles"


def get_role_prompt(prompt_name: str) -> str:
    """Get role prompt for an agent."""
    if not prompt_name.endswith(".md"):
        prompt_name += ".md"
    prompt_path = ROLES_DIRECTORY_PATH / prompt_name
    return prompt_path.read_text()


# TODO: Replace response_format with an example_response BaseResponse.
class PromptHandler:
    def __init__(
        self,
        agent_role: Optional[str] = None,
        agent_instructions: Optional[str] = None,
        action_module: Optional[ActionModule] = None,
        example_response: Optional[str] = None,
    ):
        self.agent_role = agent_role
        self.agent_instructions = agent_instructions
        self.action_module = action_module
        self.response_format = example_response

    def generate_system_prompt(
        self,
    ) -> str:
        """
        Generate system prompt for the agent.

        Returns:
            The system prompt.
        """
        if self.agent_role:
            agent_role = get_role_prompt(self.agent_role)
        else:
            agent_role = None
        if self.agent_instructions:
            instructions = f"Instructions:\n{self.agent_instructions}"
        else:
            instructions = None
        if self.action_module:
            action_api_docs = (
                f"Action API reference:\n{self.action_module.get_api_docs()}"
            )
        else:
            action_api_docs = None
        if self.response_format:
            response_format = f"Use the following schema to format your response:\n{self.response_format}"
        else:
            response_format = None
        prompt_components = [
            component.strip()
            for component in [
                agent_role,
                instructions,
                action_api_docs,
                response_format,
            ]
            if component
        ]
        system_prompt = "\n\n".join(prompt_components)
        return system_prompt
