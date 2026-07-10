import pytest

from llm_guard.output_scanners.tool_call_audit import ToolCallAudit


@pytest.mark.parametrize(
    "prompt,output,expected_valid,expected_score",
    [
        # Plain text, no tool call
        ("What is the weather?", "The weather is sunny today.", True, -1.0),
        # Empty output
        ("Do something", "", True, -1.0),
        # Valid tool call
        ("Read the file", '{"name": "read_file", "arguments": {"path": "doc.txt"}}', True, -1.0),
        # Function not in allowlist
        ("Delete it", '{"name": "exec_command", "arguments": {"cmd": "ls"}}', False, 1.0),
        # Shell injection
        ("List files", '{"name": "read_file", "arguments": {"path": "; rm -rf /"}}', False, 1.0),
        # Path traversal
        (
            "Read file",
            '{"name": "read_file", "arguments": {"path": "../../../etc/passwd"}}',
            False,
            1.0,
        ),
        # SQL injection
        (
            "Search",
            '{"name": "search_db", "arguments": {"query": "; DROP TABLE users"}}',
            False,
            1.0,
        ),
        # SSRF
        (
            "Fetch",
            '{"name": "read_file", "arguments": {"url": "http://169.254.169.254/meta"}}',
            False,
            1.0,
        ),
    ],
)
def test_scan_with_allowlist(prompt, output, expected_valid, expected_score):
    scanner = ToolCallAudit(allowed_functions=["read_file", "write_file", "search_db"])
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert valid == expected_valid
    assert score == expected_score


def test_scan_with_denylist():
    scanner = ToolCallAudit(denied_functions=["exec_command", "delete_file"])
    _, valid, _ = scanner.scan("", '{"name": "exec_command", "arguments": {"cmd": "ls"}}')
    assert valid is False

    _, valid, _ = scanner.scan("", '{"name": "read_file", "arguments": {"path": "doc.txt"}}')
    assert valid is True


def test_openai_tool_calls_format():
    scanner = ToolCallAudit(allowed_functions=["get_weather"])
    output = '{"tool_calls": [{"function": {"name": "get_weather", "arguments": "{\\"city\\": \\"NYC\\"}"}}]}'
    _, valid, score = scanner.scan("", output)
    assert valid is True
    assert score == -1.0


def test_tool_call_embedded_in_text():
    scanner = ToolCallAudit(allowed_functions=["read_file"])
    output = 'I will call: {"name": "read_file", "arguments": {"path": "test.txt"}} now.'
    _, valid, _ = scanner.scan("", output)
    assert valid is True


def test_multiple_tool_calls_mixed():
    scanner = ToolCallAudit(allowed_functions=["read_file", "write_file"])
    output = '[{"name": "read_file", "arguments": {"path": "ok.txt"}}, {"name": "exec_cmd", "arguments": {"cmd": "ls"}}]'
    _, valid, score = scanner.scan("", output)
    assert valid is False
    assert score == 0.5


def test_nested_injection():
    scanner = ToolCallAudit(allowed_functions=["query"])
    output = '{"name": "query", "arguments": {"filter": {"value": "../../etc/shadow"}}}'
    _, valid, _ = scanner.scan("", output)
    assert valid is False


def test_redact():
    scanner = ToolCallAudit(allowed_functions=["read_file"], redact=True)
    output = '{"name": "exec_command", "arguments": {"cmd": "ls"}}'
    sanitized, valid, _ = scanner.scan("", output)
    assert valid is False
    assert "[TOOL CALL REDACTED]" in sanitized


def test_both_allowlist_and_denylist_raises():
    with pytest.raises(ValueError):
        ToolCallAudit(allowed_functions=["read_file"], denied_functions=["exec_command"])


def test_injection_only_mode():
    scanner = ToolCallAudit(detect_injection=True)
    _, valid, _ = scanner.scan("", '{"name": "any_func", "arguments": {"data": "hello"}}')
    assert valid is True

    _, valid, _ = scanner.scan("", '{"name": "any_func", "arguments": {"cmd": "; rm -rf /"}}')
    assert valid is False
