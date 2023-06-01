import logging
from typing import Optional, Protocol, TypeVar, Union

import yaml
from pydantic import ValidationError

from sembla.schemas.responses import ProcessedOutput, ProcessorOutput, TaskStatus

ResponseSchema = TypeVar("ResponseSchema", bound=ProcessedOutput)


class ResponseProcessor(Protocol):
    """
    A response processor is a function that takes in a response from the agent
    and returns a processed response.
    """

    def __call__(self, response: ProcessedOutput) -> ProcessedOutput:
        """
        Process the response from the agent.

        Args:
            response: The response from the agent.

        Returns:
            The processed response.
        """
        raise NotImplementedError


class JsonParser:
    def __init__(
        self,
        response_schema: ResponseSchema,
        attempt_parse: bool = True,
        example_response: Optional[ResponseSchema] = None,
    ):
        self.response_schema = response_schema
        self.attempt_parse = attempt_parse
        self.example_response = example_response

    def __call__(self, response: ProcessedOutput) -> ProcessedOutput:
        """
        Parse JSON response from the agent.

        Args:
            response: The response from the agent.

        Returns:
            The processed response or an agent instruction.
        """
        try:
            response_text = response.raw_response
            if self.attempt_parse:
                # Select text occurring between the first '{' and the last '}'.
                first_brace = response_text.find("{")
                last_brace = response_text.rfind("}")
                json_str = response_text[first_brace : last_brace + 1]
            else:
                json_str = response_text
            parsed_response = self.response_schema.from_json(json_str)
            response.parsed_response = parsed_response
            return response
        except ValidationError as e:
            logging.error(f"Response could not be parsed: {e}")
            if self.example_response:
                example_response = self.example_response.to_json()
            else:
                example_response = self.response_schema.schema()
            agent_feedback = f"""Bad response. Expected format:\n{example_response}"""
            response.processor_feedback += agent_feedback
            response.processor_success = False
            return response


class YamlParser:
    def __init__(
        self,
        response_schema: ResponseSchema,
        attempt_parse: bool = True,
        example_response: Optional[ResponseSchema] = None,
    ):
        self.response_schema = response_schema
        self.attempt_parse = attempt_parse
        self.example_response = example_response

    def __call__(self, response: ProcessedOutput) -> ProcessedOutput:
        """
        Parse YAML response from the agent.

        Args:
            response: The response from the agent.

        Returns:
            The processed response or an agent instruction.
        """
        try:
            response_text = response.raw_response
            if self.attempt_parse:
                first_key = list(self.response_schema.schema()["properties"].keys())[0]
                last_key = list(self.response_schema.schema()["properties"].keys())[-1]
                first_key_index = response_text.find(first_key)
                last_key_index = response_text.rfind(last_key)
                yaml_str = response_text[
                    first_key_index : last_key_index + len(last_key)
                ]
            else:
                yaml_str = response_text
            parsed_response = self.response_schema.from_yaml(yaml_str)
            response.parse_response = parsed_response
            return parsed_response
        except ValidationError as e:
            logging.error(f"Response could not be parsed: {e}")
            if self.example_response:
                example_response = self.example_response.to_yaml()
            else:
                example_response = self.response_schema.schema()
                example_response = yaml.dump(example_response, default_flow_style=False)
            agent_feedback = f"""Bad response. Expected format:\n{example_response}"""
            response.processor_feedback += agent_feedback
            response.processor_success = False
            return response
