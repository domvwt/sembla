"""
This is an illustration of a functional framework for building AI agent systems. 

The functions should be replaced with classes that implement the __call__ 
method and define the __init__ method to take in any necessary parameters.
OR we use higher-order functions to create the functions with parameters.
"""
from typing import List, Protocol

from .schemas.system import SystemState, TaskStatus


def manage_memory(state: SystemState) -> SystemState:
    """Move messages from the conversation buffer to the conversation history."""
    new_message = state.memory.conversation_buffer[-1]
    new_history = state.memory.conversation_history + [new_message]

    # TODO: Add logic to handle maximum history count / token count

    new_memory = state.memory.copy(update={"conversation_history": new_history})
    new_state = state.copy(update={"memory": new_memory})

    return new_state


def process_prompt(state: SystemState) -> SystemState:
    """Process the user's input before passing it to the model."""
    # TODO: Add processing logic here
    # This will be a sequence of prompt processors that do things like
    #       - Make sure all variables are defined
    #       - Ensure any available actions are defined
    #       - Construct the prompt from specified components
    #       - Look up relevant documents from the knowledge base
    return state


def generate_response(state: SystemState) -> SystemState:
    """Generate the agent's response."""
    # TODO: Add logic to generate response using the model and the processed prompt
    return state


def process_response(state: SystemState) -> SystemState:
    """Process the agent's response."""
    # TODO: Add processing logic here
    # This will be a sequence of response processors that do things like
    #       - Parse YAML/JSON
    #       - Check for errors in code blocks
    #       - Parse any actions called by the agent
    #       - Update the conversation buffer
    #       - Update the task status if necessary
    return state


def process_actions(state: SystemState) -> SystemState:
    """Process actions called by the agent."""
    # TODO: Add logic to process actions called by the agent
    return state


class StateOperator(Protocol):
    """A callable that takes in a state and returns a new state."""

    def __call__(self, state: SystemState) -> SystemState:
        ...


class AgentSystem:
    """A system that manages the agent's conversation with the user."""

    def __init__(self, components: List[StateOperator]):
        self._components = components

    def increment_cycle(self, state: SystemState) -> SystemState:
        """Increment the current cycle."""
        new_task = state.task.copy(
            update={"current_cycle": state.task.current_cycle + 1}
        )
        new_state = state.copy(update={"task": new_task})
        return new_state

    def termination_condition_met(self, state: SystemState) -> bool:
        """Check if the system should terminate."""
        if state.task.status == TaskStatus.COMPLETE:
            return True
        elif (
            state.task.max_cycles is not None
            and state.task.current_cycle >= state.task.max_cycles
        ):
            return True
        return False

    def run(self, state: SystemState) -> SystemState:
        """Run the system for a single cycle."""
        for component in self._components:
            state = component(state)
        state = self.increment_cycle(state)
        return state

    def loop(self, state: SystemState) -> SystemState:
        """Run the system indefinitely."""
        while not self.termination_condition_met(state):
            state = self.run(state)
            state = self.increment_cycle(state)
        return state


def main():
    """Run the system."""
    system = AgentSystem(
        components=[
            process_prompt,
            manage_memory,
            generate_response,
            process_response,
            process_actions,
            manage_memory,
        ]
    )
    state = SystemState(user_input="Hello, world!")
    state = system.loop(state)
    print(state)
