from typing import Any, Callable, Dict, List, Optional, Type, Union

from sembla.actions.utils import get_docs_from_actions
from sembla.schemas.base import BaseSchema
from sembla.schemas.system import (
    Action,
    ActionCall,
    ActionCallable,
    ActionOutput,
    Message,
    SystemState,
)


def create_system_prompt(
    instructions: str,
    actions: Optional[List[Action]],
    response_example: Optional[BaseSchema],
) -> str:
    """Create a system prompt from the given `task`, `actions`, and `response_schema`."""
    prompt = f"{instructions}\n"
    if actions:
        actions_docs = get_docs_from_actions(actions)
        prompt += "You have the following actions available:\n"
        prompt += actions_docs
        prompt += "\n\n"
    if response_example:
        prompt += "Your response must be in the following format:\n"
        prompt += f"{response_example.json(indent=2)}\n"
    return prompt
