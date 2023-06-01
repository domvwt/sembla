# import os

# import pytest

# from sembla.actions import AgentCommands


# @pytest.fixture
# def agent_actions():
#     return AgentCommands()


# def test_list_files(agent_actions):
#     directory_path = os.path.dirname(os.path.abspath(__file__))
#     files = agent_actions.list_files(directory_path)
#     assert isinstance(files, str)
#     assert len(files) > 0


# def test_show_tree(agent_actions):
#     directory_path = os.path.dirname(os.path.abspath(__file__))
#     tree = agent_actions.show_tree(directory_path)
#     assert isinstance(tree, str)


# def test_read_file(agent_actions, tmp_path):
#     file_path = tmp_path / "test_read_file.txt"
#     file_content = "Hello, Sembla!"
#     file_path.write_text(file_content)

#     content = agent_actions.read_file(str(file_path))
#     assert content == file_content


# def test_write_file(agent_actions, tmp_path):
#     file_path = tmp_path / "test_write_file.txt"
#     file_content = "Hello, Sembla!"

#     agent_actions.write_file(str(file_path), file_content)

#     assert file_path.read_text() == file_content


# def test_update_file(agent_actions, tmp_path):
#     file_path = tmp_path / "test_update_file.txt"
#     file_content = "Hello, Sembla!"
#     file_path.write_text(file_content)

#     new_content = " How are you?"
#     agent_actions.update_file(str(file_path), new_content)

#     assert file_path.read_text() == file_content + new_content


# def test_delete_file(agent_actions, tmp_path):
#     file_path = tmp_path / "test_delete_file.txt"
#     file_content = "Hello, Sembla!"
#     file_path.write_text(file_content)

#     agent_actions.delete_file(str(file_path))

#     assert not file_path.exists()


# def test_parse_action(agent_actions):
#     # Test with valid action
#     sample_text = "```sembla-actions\nread_file('sample.txt')\n```"
#     action, parameters = agent_actions.parse_action(sample_text)
#     assert action == "read_file"
#     assert parameters == {"file_path": "sample.txt"}

#     # Test with no action
#     sample_text = "This text has no action block."
#     action, parameters = agent_actions.parse_action(sample_text)
#     assert action is None
#     assert parameters is None

#     # Test with action block but no valid action
#     sample_text = "```sembla-actions\nsome_invalid_action()\n```"
#     action, parameters = agent_actions.parse_action(sample_text)
#     assert action is None
#     assert parameters is None


# def test_execute_action(agent_actions, tmp_path):
#     # Test with valid action and parameters
#     file_path = tmp_path / "test_execute_read_file.txt"
#     file_content = "Hello, Sembla!"
#     file_path.write_text(file_content)

#     result = agent_actions.execute_action("read_file", {"file_path": str(file_path)})
#     assert result == file_content

#     # Test with invalid action
#     result = agent_actions.execute_action("invalid_action", {})
#     assert result is None

#     # Test with valid action and missing parameters
#     result = agent_actions.execute_action("read_file", {})
#     assert (
#         result
#         == "TypeError: read_file() missing 1 required positional argument: 'file_path'"
#     )
