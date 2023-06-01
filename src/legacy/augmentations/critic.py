import logging
import re
from typing import Optional

from sembla.agent import AgentBase, PreconfiguredAgents


class ActorCriticAug:
    def __init__(self, actor: AgentBase, critic: Optional[AgentBase] = None):
        self.actor = actor
        self.critic = critic if critic else PreconfiguredAgents.critic()
        self.conversation_history = self.actor._conversation_history

    def generate_response(self, prompt: str, role: str = "user"):
        logging.info("Query to actor:\n%s", prompt)
        response = self.actor.generate_response(prompt, role)
        logging.info("Response from actor:\n%s", response)
        message_to_critic = (
            f"TASK:\n{self.actor._task}\n"
            f"QUERY:\n{prompt.strip()}\n"
            f"RESPONSE:\n{response.strip()}\n"
        )
        logging.info("Query to critic:\n%s", message_to_critic)
        criticism = self.critic.generate_response(message_to_critic)
        logging.info("Response from critic:\n%s", criticism)
        # Regex search for 'no changes(s) required'
        regex = r"no changes? required"
        if re.search(regex, criticism, re.IGNORECASE):
            return response
        message_to_actor = f"""Revise your last response considering the following feedback:\n{criticism}"""
        final_response = self.actor.generate_response(message_to_actor)
        return final_response
