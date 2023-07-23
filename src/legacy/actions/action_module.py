import inspect
import logging
from typing import Any, Callable, Iterable, List, Optional, Union

from sembla.schemas.system import Action, ActionCall, ActionOutput, Message

logging.basicConfig(level=logging.INFO)


class ActionModule:
    def __init__(self, actions: Iterable[Union[Action, Callable[[Any], str]]]):
        self.actions = [
            Action.from_callable(action)
            for action in actions
            if not isinstance(action, Action)
        ]
        self.action_dict = {action.name: action for action in self.actions}

    def perform_action(self, action_call: ActionCall) -> ActionOutput:
        action = self.action_dict.get(action_call.name, None)
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
                logging.error(f"Error while executing '{action}': {e}")
                return ActionOutput(
                    action=action_call,
                    output=[
                        Message(
                            role="user",
                            content=f"{type(e).__name__}: {e}",
                        )
                    ],
                )
        else:
            return ActionOutput(
                action=action_call,
                output=[
                    Message(
                        role="user",
                        content=f"Error: Action '{action_call.name}' not found.",
                    )
                ],
            )

    def get_api_docs(self):
        action_docs = []
        for action in self.action_dict.values():
            method_signature = inspect.signature(action.callable)
            method_doc = inspect.getdoc(action.callable)
            action_docs.append(f"{action.name}{method_signature}: {method_doc}")
        return "\n".join(action_docs)
