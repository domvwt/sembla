from enum import Enum, auto
from typing import Any, Dict, List, Optional

from sembla.schemas.actions import ActionCall, ActionFeedback

from .base import BaseModel


class ProcessorStatus(Enum):
    """
    ProcessorStatus is an Enum that represents the status of processor execution.

    Attributes:
        Success: The processor executed successfully.
        Warning: The processor executed successfully, but with warnings.
        Error: The processor failed to execute.
    """

    Success = auto()
    Warning = auto()
    Error = auto()


class ProcessorOutput(BaseModel):
    """
    ProcessorOutput represents the output of a processor.

    Attributes:
        status: The status of processor execution.
        message: Detailed information about the processing. Useful for debugging.
        feedback: Actionable feedback for the agent, based on the processing results.
        data: Additional data produced by the processor.
    """

    status: ProcessorStatus
    message: Optional[str] = None
    feedback: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class TaskStatus(Enum):
    """
    TaskStatus is an Enum that represents the status of a task.

    Attributes:
        Complete: The task that the agent was given has been completed.
        Incomplete: The task is not yet complete.
        Unknown: The task status is unknown.
    """

    Complete = auto()
    Incomplete = auto()
    Unknown = auto()


class ProcessedOutput(BaseModel):
    """
    ProcessedOutput is a class that represents processed output from the agent.

    Attributes:
        raw_response: The raw response from the agent.
        parsed_response: The parsed response from the agent.
        processor_outputs: The outputs of the processors that were applied to the response.
        processor_success: Whether the response was successfully processed.
        processor_feedback: The feedback from the processors that were applied to the response.
        called_actions: The actions that were called by the agent.
        action_feedback: The feedback from the actions that were called by the agent.
        task_status: The status of the task that the agent was given.
    """

    raw_response: str
    parsed_response: Optional[BaseModel] = None
    processor_outputs: Dict[str, ProcessorOutput] = {}
    processor_success: bool = True
    processor_feedback: List[str] = []
    called_actions: List[ActionCall] = []
    action_feedback: List[ActionFeedback] = []
    task_status: TaskStatus
