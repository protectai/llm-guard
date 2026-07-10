from __future__ import annotations

import json
import re

from llm_guard.util import get_logger

from .base import Scanner

LOGGER = get_logger()

_INJECTION_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Shell injection
    (
        re.compile(r";\s*(?:rm|cat|curl|wget|bash|sh|chmod|chown|kill|dd|nc)\b", re.I),
        "shell injection",
    ),
    (re.compile(r"\$\([^)]+\)", re.I), "shell injection"),
    (re.compile(r"`[^`]+`", re.I), "shell injection"),
    (re.compile(r"\|\s*(?:sh|bash|zsh|cmd|powershell)\b", re.I), "shell injection"),
    (re.compile(r"&&\s*(?:rm|curl|wget|bash|sh|chmod|dd|nc)\b", re.I), "shell injection"),
    (re.compile(r"\brm\s+-[rRf]+\b", re.I), "shell injection"),
    # Path traversal
    (re.compile(r"\.\./", re.I), "path traversal"),
    (re.compile(r"/etc/(?:passwd|shadow|hosts|sudoers)", re.I), "path traversal"),
    (re.compile(r"/proc/self/", re.I), "path traversal"),
    # SQL injection
    (re.compile(r";\s*(?:DROP|DELETE|INSERT|UPDATE|ALTER|CREATE)\s", re.I), "SQL injection"),
    (re.compile(r"UNION\s+(?:ALL\s+)?SELECT\s", re.I), "SQL injection"),
    # SSRF
    (re.compile(r"https?://169\.254\.169\.254", re.I), "SSRF"),
    (re.compile(r"https?://metadata\.google\.internal", re.I), "SSRF"),
    (re.compile(r"https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0)", re.I), "SSRF"),
    (re.compile(r"https?://10\.\d{1,3}\.\d{1,3}\.\d{1,3}", re.I), "SSRF"),
    (re.compile(r"https?://172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}", re.I), "SSRF"),
    (re.compile(r"https?://192\.168\.\d{1,3}\.\d{1,3}", re.I), "SSRF"),
]


def _try_parse_json(text: str) -> dict | list | None:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def _is_tool_call(obj: dict) -> bool:
    if "function" in obj and isinstance(obj["function"], dict):
        return "name" in obj["function"]
    if "name" in obj and ("arguments" in obj or "args" in obj):
        return True
    return isinstance(obj.get("function"), str) and ("arguments" in obj or "args" in obj)


def _get_function_name(tc: dict) -> str:
    if "function" in tc and isinstance(tc["function"], dict):
        return tc["function"].get("name", "")
    if "name" in tc:
        return tc["name"]
    return tc.get("function", "") if isinstance(tc.get("function"), str) else ""


def _get_arguments(tc: dict) -> dict:
    if "function" in tc and isinstance(tc["function"], dict):
        args = tc["function"].get("arguments", {})
    else:
        args = tc.get("arguments", tc.get("args", {}))

    if isinstance(args, str):
        parsed = _try_parse_json(args)
        return parsed if isinstance(parsed, dict) else {}
    return args if isinstance(args, dict) else {}


def _flatten_values(obj: dict) -> list[str]:
    values = []
    for v in obj.values():
        if isinstance(v, str):
            values.append(v)
        elif isinstance(v, dict):
            values.extend(_flatten_values(v))
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    values.append(item)
                elif isinstance(item, dict):
                    values.extend(_flatten_values(item))
    return values


def _extract_tool_calls(output: str) -> list[dict]:
    parsed = _try_parse_json(output.strip())
    if parsed is not None:
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict) and _is_tool_call(item)]
        if isinstance(parsed, dict):
            if _is_tool_call(parsed):
                return [parsed]
            if "tool_calls" in parsed and isinstance(parsed["tool_calls"], list):
                return [
                    item
                    for item in parsed["tool_calls"]
                    if isinstance(item, dict) and _is_tool_call(item)
                ]

    # Fallback: find JSON objects embedded in text
    tool_calls = []
    depth, start = 0, None
    for i, ch in enumerate(output):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                obj = _try_parse_json(output[start : i + 1])
                if isinstance(obj, dict) and _is_tool_call(obj):
                    tool_calls.append(obj)
                start = None
    return tool_calls


def _check_injection(values: list[str]) -> tuple[bool, str]:
    for pattern, label in _INJECTION_PATTERNS:
        for value in values:
            if pattern.search(value):
                return True, label
    return False, ""


class ToolCallAudit(Scanner):
    """
    A scanner that validates tool/function calls in LLM output.

    Checks function names against an allowlist or denylist and scans argument values
    for injection attacks (shell injection, path traversal, SQL injection, SSRF).
    """

    def __init__(
        self,
        *,
        allowed_functions: list[str] | None = None,
        denied_functions: list[str] | None = None,
        detect_injection: bool = True,
        redact: bool = False,
        threshold: float = 0.5,
    ) -> None:
        if allowed_functions and denied_functions:
            raise ValueError("Provide either allowed_functions or denied_functions, not both.")

        self._allowed = {f.lower() for f in allowed_functions} if allowed_functions else None
        self._denied = {f.lower() for f in denied_functions} if denied_functions else None
        self._detect_injection = detect_injection
        self._redact = redact
        self._threshold = threshold

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        if output.strip() == "":
            return output, True, -1.0

        tool_calls = _extract_tool_calls(output)
        if not tool_calls:
            return output, True, -1.0

        LOGGER.debug("Found tool calls in output", count=len(tool_calls))
        violations = []

        for tc in tool_calls:
            name = _get_function_name(tc).lower()

            if self._allowed is not None and name not in self._allowed:
                LOGGER.warning("Function not in allowlist", function=name)
                violations.append(tc)
                continue

            if self._denied is not None and name in self._denied:
                LOGGER.warning("Function in denylist", function=name)
                violations.append(tc)
                continue

            if self._detect_injection:
                args = _get_arguments(tc)
                if args:
                    found, label = _check_injection(_flatten_values(args))
                    if found:
                        LOGGER.warning("Injection detected in arguments", function=name, type=label)
                        violations.append(tc)

        if not violations:
            return output, True, -1.0

        sanitized_output = output
        if self._redact:
            for tc in violations:
                sanitized_output = sanitized_output.replace(
                    json.dumps(tc, default=str), "[TOOL CALL REDACTED]"
                )

        score = round(len(violations) / len(tool_calls), 1)
        return sanitized_output, False, score
