from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

from .base import BaseModel


class TaskStatus(Enum):
    """
    Represents the status of the current task.
    """

    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    UNDEFINED = "UNDEFINED"


class TaskState(BaseModel):
    """
    Represents the state of the current task.

    Attributes:
        name: The name of the task.
        description: The description of the task.
        status: The status of the task.
        max_cycles: The maximum number of cycles to run the task for.
        current_cycle: The current cycle of the task.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.UNDEFINED
    max_cycles: Optional[int] = None
    current_cycle: int = 0


class ModelState(BaseModel):
    """
    Represents a model that is used by the system.

    Attributes:
        name: The name of the model.
        temperature: The temperature of the model.
        n: The number of responses to generate.
        max_tokens: The maximum number of tokens to generate.
        frequency_penalty: The frequency penalty of the model.
        presence_penalty: The presence penalty of the model.
    """

    name: str = "gpt-3.5-turbo"
    temperature: float = 0.2
    n: int = 1
    max_tokens: int = 2000
    frequency_penalty: float = 0
    presence_penalty: float = 0


class Message(BaseModel):
    """
    Represents a message in a conversation.

    Attributes:
        role: The role the message author.
        content: The content of the message.
        name: The name of the message author.
    """

    role: str
    content: str
    name: Optional[str] = None


class MemoryState(BaseModel):
    """
    Represents the memory of the system.
    """

    max_history_message_count: int = 100
    max_history_token_count: int = 1000
    conversation_history: List[Message] = []
    conversation_buffer: List[Message] = []
    message_count: int = 0
    token_count: int = 0


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


class ActionOutput(BaseModel):
    action: ActionCall
    agent_messages: List[Message] = []


class ProcessingStatus(Enum):
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
    Represents the output of a prompt or response processor.
    """

    processor_name: str
    processing_status: ProcessingStatus
    user_messages: List[Message] = []
    agent_messages: List[Message] = []
    data: Optional[Dict[str, Any]] = None


class SystemState(BaseModel):
    """
    Shared state for the system.
    """

    task: TaskState = TaskState()
    model: ModelState = ModelState()
    memory: MemoryState = MemoryState()
    user_query: Optional[str] = None
    available_actions: List[Action] = []
    prompt_processor_outputs: List[ProcessorOutput] = []
    processed_prompt: Optional[str] = None
    agent_response: Optional[str] = None
    response_processor_outputs: List[ProcessorOutput] = []
    processed_response: Optional[str] = None
