import logging
from typing import List

import tiktoken

from sembla.schemas.system import Message, SystemState


def update_conversation_history(system_state: SystemState) -> SystemState:
    # Update the conversation history
    new_conversation_history = (
        system_state.memory.conversation_history
        + system_state.memory.conversation_buffer
    )

    # Remove the oldest messages from the conversation history if necessary
    while len(new_conversation_history) > system_state.memory.max_history_message_count:
        new_conversation_history = remove_earliest_non_system_message(
            new_conversation_history
        )

    # Remove the oldest tokens from the conversation history if necessary
    while (
        get_token_count(new_conversation_history, system_state.model.name)
        > system_state.memory.max_history_token_count
    ):
        new_conversation_history = remove_earliest_non_system_message(
            new_conversation_history
        )

    # Update the memory state
    new_memory_state = system_state.memory.copy(
        update={"conversation_history": new_conversation_history}
    )
    # Update the buffer
    new_memory_state = new_memory_state.copy(update={"conversation_buffer": []})
    # Update the token count
    new_memory_state = new_memory_state.copy(
        update={
            "message_count": len(new_conversation_history),
            "token_count": get_token_count(
                new_conversation_history, system_state.model.name
            ),
        }
    )

    return system_state.copy(update={"memory": new_memory_state})


def remove_earliest_non_system_message(
    conversation_history: List[Message],
) -> List[Message]:
    for i, msg in enumerate(conversation_history):
        if msg.role != "system":
            del conversation_history[i]
            break
    return conversation_history


def get_token_count(conversation_history: List[Message], model_name: str) -> int:
    return num_tokens_in_messages(conversation_history, model_name=model_name)


def get_max_token_count(model_name: str) -> int:
    # TODO: Update this since GPT-3 now comes in multiple context lengths
    if "gpt-3" in model_name:
        return 4097
    elif "gpt-4" in model_name:
        return 8192
    else:
        raise ValueError(f"Unknown model: {model_name}")


def num_tokens_in_messages(messages: List[Message], model_name="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    # Source: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        logging.debug("Model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model_name == "gpt-3.5-turbo":
        logging.debug(
            "gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301."
        )
        return num_tokens_in_messages(messages, model_name="gpt-3.5-turbo-0301")
    elif model_name == "gpt-4":
        logging.debug(
            "gpt-4 may change over time. Returning num tokens assuming gpt-4-0314."
        )
        return num_tokens_in_messages(messages, model_name="gpt-4-0314")
    elif model_name == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model_name == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model_name}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        num_tokens += len(encoding.encode(message.content))
        if message.name:
            num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
