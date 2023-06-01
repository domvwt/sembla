import warnings
from typing import Iterable, Optional

from sembla.actions import ActionModule
from sembla.response.processor import ResponseProcessor
from sembla.schemas.responses import ProcessedOutput, TaskStatus


class ResponseHandler:
    def __init__(
        self,
        action_module: Optional[ActionModule] = None,
        response_processors: Optional[Iterable[ResponseProcessor]] = None,
        fail_fast: bool = True,
    ):
        self.action_module = action_module
        self.response_processors = response_processors or []
        self.fail_fast = fail_fast

    def handle_response(self, response: str) -> ProcessedOutput:
        processed_output = ProcessedOutput(
            task_status=TaskStatus.Unknown, raw_response=response
        )
        for response_processor in self.response_processors:
            processed_output = response_processor(processed_output)
            if self.fail_fast and not processed_output.processor_success:
                break
        if self.action_module:
            if not processed_output.called_actions:
                warnings.warn(
                    "An action module was provided but no actions were called by the agent. Did you forget to add an action processor?"
                )
            for action in processed_output.called_actions:
                action_result = self.action_module.perform_action(action)
                processed_output.action_feedback.append(action_result)
        return processed_output
