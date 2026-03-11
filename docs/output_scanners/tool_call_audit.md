# Tool Call Audit Scanner

This scanner validates tool and function calls in LLM output. It checks that only permitted functions are invoked and that arguments do not contain injection attacks.

## Attack scenario

Agentic AI systems let LLMs invoke external tools: reading files, querying databases, calling APIs. If the LLM is manipulated through prompt injection or jailbreaking, it can generate tool calls that invoke dangerous functions, pass malicious payloads through arguments, or exfiltrate data through unexpected endpoints.

## How it works

The scanner is entirely rule based (no model downloads required) and performs two checks:

1. **Function name validation**: Checks the function name against a configurable allowlist or denylist.

2. **Argument injection detection**: Scans all argument values (including nested objects) for known injection patterns:
    - Shell injection: `; rm -rf`, `$(command)`, backticks, pipe to shell
    - Path traversal: `../`, `/etc/passwd`, `/proc/self/`
    - SQL injection: `' OR 1=1`, `; DROP TABLE`, `UNION SELECT`
    - SSRF: cloud metadata endpoints, localhost, private IP ranges

Supports multiple tool call formats: `{"name": ..., "arguments": ...}`, OpenAI's `{"function": {"name": ..., "arguments": ...}}`, and `{"tool_calls": [...]}` wrappers.

If the output contains no tool calls, the scanner passes it through as valid.

## Usage

```python
from llm_guard.output_scanners import ToolCallAudit

# Allowlist mode: only these functions are permitted
scanner = ToolCallAudit(
    allowed_functions=["read_file", "write_file", "search_db"],
)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)

# Denylist mode: block specific dangerous functions
scanner = ToolCallAudit(
    denied_functions=["exec_command", "delete_file", "shell"],
)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)

# Injection detection only (no function name filtering)
scanner = ToolCallAudit(detect_injection=True)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Configuration

| Parameter            | Type        | Default | Description                                                      |
|----------------------|-------------|---------|------------------------------------------------------------------|
| `allowed_functions`  | `list[str]` | `None`  | Allowlist of permitted function names. Exclusive with denylist    |
| `denied_functions`   | `list[str]` | `None`  | Denylist of blocked function names. Exclusive with allowlist      |
| `detect_injection`   | `bool`      | `True`  | Whether to scan argument values for injection patterns           |
| `redact`             | `bool`      | `False` | Whether to replace blocked tool calls with `[TOOL CALL REDACTED]`|
| `threshold`          | `float`     | `0.5`   | Risk threshold for flagging                                      |
