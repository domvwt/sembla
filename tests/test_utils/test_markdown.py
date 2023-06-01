import pytest

from sembla.utils import markdown as md


def test_split_markdown_sections():
    markdown = "# Section 1\nLine 1\n\n# Section 2\nLine 1\nLine 2\n"
    expected_sections = ["# Section 1\nLine 1", "# Section 2\nLine 1\nLine 2"]
    assert md.split_sections(markdown) == expected_sections


def test_extract_code_from_markdown():
    markdown = """\
# Section 1

```python
print("Hello, Sembla!")
```

# Section 2

```python
print("Hello, Askr!")
```
"""
    expected_code = [
        'print("Hello, Sembla!")',
        'print("Hello, Askr!")',
    ]
    assert md.extract_codeblocks(markdown) == expected_code
