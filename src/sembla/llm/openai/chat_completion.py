from typing import Dict

import openai

from sembla.schemas.system import AgentResponse, Message, SystemState


def convert_message_to_openai_format(message: Message) -> Dict[str, str]:
    return {"role": message.role, "content": message.content}


def generate_chat_completion(system_state: SystemState) -> SystemState:
    model = system_state.model.name
    temperature = system_state.model.temperature
    n = system_state.model.n
    frequency_penalty = system_state.model.frequency_penalty
    presence_penalty = system_state.model.presence_penalty

    conversation_history = system_state.memory.conversation_history
    max_completion_tokens = (
        system_state.memory.max_history_token_count - system_state.memory.token_count
    )
    max_completion_tokens = int(max_completion_tokens * 0.95)

    messages = [
        convert_message_to_openai_format(message) for message in conversation_history
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        n=n,
        max_tokens=max_completion_tokens,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    top_response = response.choices[0]
    message_content = top_response["message"]["content"].strip()
    agent_response = AgentResponse(raw_response=message_content)
    new_state = system_state.copy(update={"agent_response": agent_response})

    return new_state
