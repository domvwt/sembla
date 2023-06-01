import logging
from collections import deque
from typing import Dict, List, Optional

import tiktoken

Message = Dict[str, str]


def get_max_token_count(model: str) -> int:
    if "gpt-3" in model:
        return 4097
    elif "gpt-4" in model:
        return 8192
    else:
        raise ValueError(f"Unknown model: {model}")


class ConversationHistory:
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        max_history_message_count: int = 20,
        max_history_token_count: Optional[int] = None,
    ):
        self.model = model
        self.max_history_message_count = max_history_message_count
        self.max_history_token_count = max_history_token_count or get_max_token_count(
            model
        )
        self.conversation_history = []
        self.conversation_buffer = []

    def add_message(self, message: Message):
        self.conversation_history.append(message)
        self.conversation_buffer.append(message)

        while len(self.conversation_history) > self.max_history_message_count:
            self.remove_earliest_non_system_message()

        while self.get_token_count() > self.max_history_token_count:
            self.remove_earliest_non_system_message()

    def remove_earliest_non_system_message(self):
        for i, msg in enumerate(self.conversation_history):
            if msg["role"] != "system":
                del self.conversation_history[i]
                break

    def extend_history(self, history: List[Message]):
        for msg in history:
            self.add_message(msg)

    def get_token_count(self):
        return num_tokens_from_messages(self.conversation_history, model=self.model)

    def get_message_count(self):
        return len(self.conversation_history)


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    # Source: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logging.debug("Model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        logging.debug(
            "gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301."
        )
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        logging.debug(
            "gpt-4 may change over time. Returning num tokens assuming gpt-4-0314."
        )
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
