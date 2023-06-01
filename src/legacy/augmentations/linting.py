import logging
import re
import subprocess
from collections import namedtuple
from pathlib import Path
from tempfile import NamedTemporaryFile
from textwrap import dedent
from typing import Optional

import flake8.api

from sembla.agent import AgentBase
from sembla.utils import markdown as md


class Flake8Aug:
    def __init__(
        self,
        actor: AgentBase,
    ):
        self.actor = actor
        self.conversation_history = self.actor._conversation_history

    def generate_response(self, prompt: str, role: str = "user"):
        response = self.actor.generate_response(prompt, role)
        while not md.has_code_block(response):
            prompt = """Provide completed code in a code block."""
            response = self.actor.generate_response(prompt)
        code_string = md.get_largest_code_block(response)
        errors = self.static_code_analysis(code_string)
        while errors:
            errors_prompt = f"""\
There are errors in your response. Return a revised version with the errors fixed.
{errors}
""".strip()
            response = self.actor.generate_response(errors_prompt)
            while not md.has_code_block(response):
                prompt = """Provide the completed code in a code block."""
                response = self.actor.generate_response(prompt)
            code_string = md.get_largest_code_block(response)
            errors = self.static_code_analysis(code_string)
        return response

    def static_code_analysis(self, code_string: str) -> Optional[str]:
        """Run static code analysis on a given code string."""
        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as temp_file:
            temp_file_name = temp_file.name
            Path(temp_file_name).write_text(code_string)
            subprocess.run(["black", temp_file_name], capture_output=True, text=True)
            subprocess.run(["isort", temp_file_name], capture_output=True, text=True)
            output = subprocess.run(
                ["flake8", "--select=E,F", "--max-line-length=120", temp_file_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            result = (str(output.stdout) + str(output.stderr)).strip()
            return result or None
