import inspect
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from sembla.schemas.system import Action, ActionCall, ActionOutput, Message, SystemState


def execute_action_call(
    available_actions: List[Action], action_call: ActionCall
) -> ActionOutput:
    action_dict = {action.name: action for action in available_actions}
    action = action_dict.get(action_call.name, None)
    if action:
        try:
            if action_call.parameters:
                result = action.callable(**action_call.parameters)
            else:
                result = action.callable()
            return ActionOutput(
                action=action_call,
                output=result,
            )
        except Exception as e:
            return ActionOutput(
                action=action_call,
                output=f"{type(e).__name__}: {e}",
            )
    else:
        return ActionOutput(
            action=action_call,
            output=f"Error - Action not available: {action_call.name}",
        )


def get_docs_from_actions(actions: List[Action]) -> str:
    action_docs = []
    for action in actions:
        method_signature = inspect.signature(action.callable)
        method_doc = inspect.getdoc(action.callable)
        action_docs.append(f"{action.name}{method_signature}: {method_doc}")
    return "\n".join(action_docs)
