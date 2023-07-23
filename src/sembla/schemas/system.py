import importlib
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import Field, root_validator, validator

from .base import BaseSchema


class TaskStatus(Enum):
    """
    Represents the status of the current task.
    """

    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    UNDEFINED = "UNDEFINED"


class TaskState(BaseSchema):
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


class ModelState(BaseSchema):
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


class Message(BaseSchema):
    """
    Represents a message in a conversation.

    Attributes:
        role: The role of the message author.
        content: The content of the message.
        name: The name of the message author.
    """

    role: str
    content: str
    name: Optional[str] = None


class MemoryState(BaseSchema):
    """
    Represents the memory of the system.
    """

    max_history_message_count: int = 100
    max_history_token_count: int = 1000
    conversation_history: List[Message] = []
    conversation_buffer: List[Message] = []
    message_count: int = 0
    token_count: int = 0


ActionCallable = Callable[..., str]


from pydantic import BaseModel
from typing import Callable, Optional
import importlib

class Action(BaseModel):
    name: str
    callable_name: Optional[str] = None

    def __init__(self, **data):
        # If 'callable' is provided as a function, convert it to a string for 'callable_name'
        if callable(data.get('callable')):
            data['callable_name'] = f"{data['callable'].__module__}.{data['callable'].__name__}"
            del data['callable']
        super().__init__(**data)

    @property
    def callable(self):
        if self.callable_name:
            module_name, function_name = self.callable_name.rsplit('.', 1)
            module = importlib.import_module(module_name)
            return getattr(module, function_name)
        else:
            return None

    @classmethod
    def from_callable(cls, callable: Callable) -> "Action":
        return Action(
            name=callable.__name__,
            callable=callable,
        )


class ActionCall(BaseSchema):
    name: str
    parameters: Optional[dict]


class ActionOutput(BaseSchema):
    action: ActionCall
    output: str


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


class ProcessorOutput(BaseSchema):
    """
    Represents the output of a prompt or response processor.
    """

    processor_name: str
    processing_status: ProcessingStatus
    user_messages: List[Message] = []
    agent_messages: List[Message] = []
    data: Optional[Dict[str, Any]] = None


class UserQuery(BaseSchema):
    """
    Represents the user's query.
    """

    raw_query: str
    processed_query: Optional[str] = None


class ResponseSchema(BaseSchema):
    """
    Represents the schema of a response.
    """

    goal: str
    objectives: List[str]
    observations: List[str]
    action: ActionCall


class AgentResponse(BaseSchema):
    """
    Represents the response of the agent.
    """

    raw_response: str
    parsed_response: Optional[ResponseSchema] = None
    processor_outputs: List[ProcessorOutput] = []
    processed_response: Optional[str] = None


class SystemState(BaseSchema):
    task: TaskState = TaskState()
    model: ModelState = ModelState()
    system_prompt: Optional[str] = None
    response_schema_class: Optional[str] = None
    memory: MemoryState = MemoryState()
    actions: List[Action] = []
    user_query: Optional[UserQuery] = None
    agent_response: Optional[AgentResponse] = None

    def __init__(self, **data):
        # If 'response_schema' is provided as a class, convert it to a string for 'response_schema_class'
        if isinstance(data.get("response_schema"), type):
            data[
                "response_schema_class"
            ] = f"{data['response_schema'].__module__}.{data['response_schema'].__name__}"
            del data["response_schema"]
        super().__init__(**data)

    @property
    def response_schema(self):
        if self.response_schema_class:
            module_name, class_name = self.response_schema_class.rsplit(".", 1)
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        else:
            return None
