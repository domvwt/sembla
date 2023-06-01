from typing import Any, Callable, List, Optional

import yaml

from .base import BaseModel


class Action(BaseModel):
    name: str
    callable: Callable

    @classmethod
    def from_callable(cls, callable: Callable) -> "Action":
        return Action(
            name=callable.__name__,
            callable=callable,
        )


class ActionCall(BaseModel):
    action: str
    parameters: Optional[dict]


class SingleActionResponse(BaseModel):
    goal: str
    completed_tasks: List[str]
    reflections: List[str]
    plan: List[str]
    explain: List[str]
    action: ActionCall


class MultiActionResponse(BaseModel):
    goal: str
    completed_tasks: List[str]
    reflections: List[str]
    plan: List[str]
    explain: List[str]
    actions: List[ActionCall]


class ActionFeedback(BaseModel):
    action: ActionCall
    output: Any


# Sample data
response_data = {
    "goal": "<I must...>",
    "completed_tasks": ["<I have...>"],
    "reflections": ["<My last action succeeded/failed because...>"],
    "plan": ["<I will...>", "<I will...>"],
    "explain": ["<This will help...>"],
}

single_action_response_data = {
    **response_data,
    "action": {"action": "<command>", "parameters": {"<arg1>": "<input1>"}},
}

multi_action_response_data = {
    **response_data,
    "actions": [
        {"action": "<command1>", "parameters": {"<arg1>": "<input1>"}},
        {"action": "<command2>", "parameters": {"<arg2>": "<input2>"}},
    ],
}

# Create a response model instance
example_single_action_response = SingleActionResponse(**single_action_response_data)
example_multi_action_response = MultiActionResponse(**multi_action_response_data)

# Serialize the instance to JSON
serialized_json = example_single_action_response.json()

# Deserialize the JSON back to a ResponseModel instance
deserialized_response = SingleActionResponse.parse_raw(serialized_json)
