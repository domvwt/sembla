"""
This is an illustration of a functional framework for building AI agent systems.

The functions should be replaced with classes that implement the __call__
method and define the __init__ method to take in any necessary parameters.
OR we use higher-order functions to create the functions with parameters.
"""
from typing import List, Protocol

from .schemas.system import SystemState, TaskStatus


def manage_memory(system_state: SystemState) -> SystemState:
    """Move messages from the conversation buffer to the conversation history."""
    new_message = system_state.memory.conversation_buffer[-1]
    new_history = system_state.memory.conversation_history + [new_message]

    # TODO: Add logic to handle maximum history count / token count

    new_memory = system_state.memory.copy(update={"conversation_history": new_history})
    new_state = system_state.copy(update={"memory": new_memory})

    return new_state


def process_prompt(system_state: SystemState) -> SystemState:
    """Process the user's input before passing it to the model."""
    # TODO: Add processing logic here
    # This will be a sequence of prompt processors that do things like
    #       - Make sure all variables are defined
    #       - Ensure any available actions are defined
    #       - Construct the prompt from specified components
    #       - Look up relevant documents from the knowledge base
    return system_state


def generate_response(system_state: SystemState) -> SystemState:
    """Generate the agent's response."""
    # TODO: Add logic to generate response using the model and the processed prompt
    return system_state


def process_response(system_state: SystemState) -> SystemState:
    """Process the agent's response."""
    # TODO: Add processing logic here
    # This will be a sequence of response processors that do things like
    #       - Parse YAML/JSON
    #       - Check for errors in code blocks
    #       - Parse any actions called by the agent
    #       - Update the conversation buffer
    #       - Update the task status if necessary
    return system_state


def process_actions(system_state: SystemState) -> SystemState:
    """Process actions called by the agent."""
    # TODO: Add logic to process actions called by the agent
    return system_state


class StateOperator(Protocol):
    """A callable that takes in a system state and returns a new system state."""

    def __call__(self, system_state: SystemState) -> SystemState:
        ...


class AgentSystem:
    """A system that manages the agent's conversation with the user."""

    def __init__(self, components: List[StateOperator]):
        self._components = components

    def increment_cycle(self, system_state: SystemState) -> SystemState:
        """Increment the current cycle."""
        new_task = system_state.task.copy(
            update={"current_cycle": system_state.task.current_cycle + 1}
        )
        new_state = system_state.copy(update={"task": new_task})
        return new_state

    def termination_condition_met(self, system_state: SystemState) -> bool:
        """Check if the system should terminate."""
        if system_state.task.status == TaskStatus.COMPLETE:
            return True
        elif (
            system_state.task.max_cycles is not None
            and system_state.task.current_cycle >= system_state.task.max_cycles
        ):
            return True
        return False

    def run(self, system_state: SystemState) -> SystemState:
        """Run the system for a single cycle."""
        for component in self._components:
            system_state = component(system_state)
        system_state = self.increment_cycle(system_state)
        return system_state

    def loop(self, system_state: SystemState) -> SystemState:
        """Run the system indefinitely."""
        while not self.termination_condition_met(system_state):
            system_state = self.run(system_state)
            system_state = self.increment_cycle(system_state)
        return system_state


def init_autonomous_agent_system(components: List[StateOperator]) -> StateOperator:
    def increment_cycle(system_state: SystemState) -> SystemState:
        """Increment the current cycle."""
        new_task = system_state.task.copy(
            update={"current_cycle": system_state.task.current_cycle + 1}
        )
        new_state = system_state.copy(update={"task": new_task})
        return new_state

    def termination_condition_met(system_state: SystemState) -> bool:
        """Check if the system should terminate."""
        if system_state.task.status == TaskStatus.COMPLETE:
            return True
        elif (
            system_state.task.max_cycles is not None
            and system_state.task.current_cycle >= system_state.task.max_cycles
        ):
            return True
        return False

    def run_cycle(system_state: SystemState) -> SystemState:
        """Run the system for a single cycle."""
        for component in components:
            system_state = component(system_state)
        system_state = increment_cycle(system_state)
        return system_state

    def run_system(system_state: SystemState) -> SystemState:
        """Run the system indefinitely."""
        while not termination_condition_met(system_state):
            system_state = run_cycle(system_state)
        return system_state

    return run_system


def init_sequential_agent_system(components: List[StateOperator]) -> StateOperator:
    def run_system(system_state: SystemState) -> SystemState:
        """Run the system sequentially."""
        for component in components:
            system_state = component(system_state)
        # Increment the cycle
        new_task = system_state.task.copy(
            update={"current_cycle": system_state.task.current_cycle + 1}
        )
        new_state = system_state.copy(update={"task": new_task})
        return new_state

    return run_system


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
    system_state = SystemState(user_query="Hello, world!")
    system_state = system.loop(system_state)
    print(system_state)
