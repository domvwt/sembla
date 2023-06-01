import re
from typing import List


def split_sections(markdown: str) -> List[str]:
    """
    Split a Markdown document into sections.

    Args:
        markdown (str): The Markdown document.

    Returns:
        List[str]: The sections of the document.
    """
    sections = []
    current_section = []
    for line in markdown.splitlines():
        if line.startswith("#"):
            if current_section:
                sections.append("\n".join(current_section))
                current_section = []
        # Keep the line if it's not empty
        if line.strip():
            current_section.append(line)
    if current_section:
        sections.append("\n".join(current_section))
    return sections


def has_code_block(text: str) -> bool:
    """Check if `text` contains a markdown code block."""
    return bool(re.search(r"```(?:\w+\n)?(.*?)```", text, re.DOTALL))


def get_largest_code_block(text: str) -> str:
    """Return the largest markdown code block in `text`."""
    code_blocks = re.findall(r"```(?:\w+\n)?(.*?)```", text, re.DOTALL)
    try:
        return max(code_blocks, key=len).strip()
    except ValueError:
        raise ValueError("No code produced, agent response: " + text)


def has_demarked_document(text: str) -> bool:
    """Check if `text` contains a demarked document."""
    return bool(re.search(r"---\n(.*?)---", text, re.DOTALL))


def capture_all_documents(text: str) -> List[str]:
    """Capture documents between horizontal lines."""
    # Use a non-greedy match to capture each document.
    return list(re.findall(r"---\n(.*?)\n---", text, re.DOTALL))


def capture_document(text: str) -> str:
    """Capture a single document between horizontal lines."""
    # Use a non-greedy match to capture each document.
    captured = re.search(r"---\n(.*?)\n---", text, re.DOTALL)
    if captured:
        return captured.group(1)
    return ""
