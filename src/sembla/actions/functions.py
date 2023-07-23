from functools import wraps
from pathlib import Path


class TaskSubmission:
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return f"TaskSubmission(args={self.args}, kwargs={self.kwargs})"

    def __str__(self):
        return f"TaskSubmission(args={self.args}, kwargs={self.kwargs})"


def _truncate_output(output: str, max_length: int = 1000) -> str:
    if isinstance(output, str) and len(output) > max_length:
        output = output[:max_length]
        output += "..."
    return output


def truncate_output(func):
    """Decorator to truncate output of a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        return _truncate_output(output)

    return wrapper


# Special
def submit_completed_task(*args, **kwargs):
    """Submit completed task to the user."""
    return TaskSubmission(
        args,
        kwargs,
    )


def no_action(*args, **kwargs):
    """No action."""
    return "No action."


# Filesystem
def list_directory(directory):
    """List contents of `directory`."""
    directory = Path(directory)
    contents = [item.name for item in directory.iterdir()]
    markdown_contents = "\n".join([f"- {item}" for item in contents])
    return markdown_contents


def directory_tree(directory):
    """Get tree structure of `directory`."""

    def tree(directory, prefix=""):
        directory = Path(directory)

        if not directory.is_dir():
            raise ValueError(f"{directory} is not a directory.")

        entries = [
            entry for entry in directory.iterdir() if not entry.name.startswith(".")
        ]
        tree_string = ""

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            if entry.is_dir():
                tree_prefix = "└── " if is_last else "├── "
                tree_string += prefix + tree_prefix + entry.name + "\n"
                new_prefix = "    " if is_last else "│   "
                tree_string += tree(entry, prefix + new_prefix)
            else:
                tree_prefix = "└── " if is_last else "├── "
                tree_string += prefix + tree_prefix + entry.name + "\n"

        return tree_string

    return tree(directory)


def find_files(directory, pattern):
    """Find files in `directory` that match the `pattern`."""
    directory = Path(directory)
    matching_files = [str(file) for file in directory.glob(pattern)]

    if matching_files:
        result = "\n".join([f"- {file}" for file in matching_files])
    else:
        result = "none"

    return f"matching files:\n{result}"


def create_directory(directory):
    """Create `directory`."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return f"directory created: {directory}"


def create_file(filename):
    """Create `filename`"""
    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    # file_path.write_text(content)
    return f"file created: {filename}"


# NOTE: Agents read files out of curiosity(?!), wasting tokens and time.
# @truncate_output
def read_file(filename):
    """Read contents of `filename`."""
    file_path = Path(filename)
    return file_path.read_text()


def write_to_file(filename, content):
    """Write `content` to `filename`. Overwrites existing file."""
    file_path = Path(filename)
    file_path.write_text(content)
    return f"file updated: {filename}"


def append_to_file(filename, content):
    """Append `content` to `filename`."""
    file_path = Path(filename)
    file_path.write_text(file_path.read_text() + content)
    return f"file updated: {filename}"


def replace_in_file(filename, old, new):
    """Replace text `old` with `new` in `filename`."""
    file_path = Path(filename)
    file_path.write_text(file_path.read_text().replace(old, new))
    return f"file updated: {filename}"


# NOTE: Agents seem to like moving files around for no apparent reason.
def move_file(source, destination):
    """Move `source` to `destination`."""
    source_path = Path(source)
    destination_path = Path(destination)
    source_path.rename(destination_path)
    return f"file moved: {source} -> {destination}"
