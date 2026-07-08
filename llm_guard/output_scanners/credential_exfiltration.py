"""Credential Exfiltration Scanner

Detects LLM outputs that indicate an agent is harvesting environment
variables, config files, or secrets and attempting to exfiltrate them
via HTTP requests, notifications, or file writes — a behaviour class
documented in Dwivedi (2026) as "C7 – Credential and Secret Exfiltration".

Exfiltration signals include:

- Reading named secret environment variables (API_KEY, SECRET, TOKEN, etc.)
- Listing all environment variables (bulk harvest).
- Making HTTP requests that carry Authorization, Bearer, or API-key headers.
- Sending notifications or writing files that contain known credential prefixes
  (``sk-``, ``ghp_``, ``AKIA``).
- Combining read-env / read-config actions with an outbound network call.

The scanner is rule-based (no external model required) and uses a weighted
pattern set.  Each matched pattern contributes to a cumulative risk score;
the result is clamped to [0.0, 1.0].
"""

from __future__ import annotations

import logging
import re

from .base import Scanner

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exfiltration pattern definitions
# Each entry: (compiled_regex, weight)
# ---------------------------------------------------------------------------

_PATTERNS: list[tuple[re.Pattern[str], float]] = [
    # Reading named secret env vars
    (
        re.compile(
            r"\bread_env_var\b.{0,60}"
            r"\b(?:API[_\s]?KEY|SECRET|TOKEN|PASSWORD|PRIVATE[_\s]?KEY|ACCESS[_\s]?KEY)\b",
            re.I | re.S,
        ),
        0.85,
    ),
    # Bulk environment variable listing
    (re.compile(r"\blist_env_vars?\b", re.I), 0.7),
    (re.compile(r"\bos\.environ\b.{0,30}\b(?:items|keys|values)\b", re.I), 0.7),
    # HTTP request with credential headers
    (
        re.compile(
            r"\bhttp_request\b.{0,80}"
            r"\b(?:Authorization|Bearer|api[_\s-]?key|x-api-key)\b",
            re.I | re.S,
        ),
        0.9,
    ),
    (
        re.compile(
            r"\b(?:Authorization|Bearer)\s*[:\=].{0,60}"
            r"\b(?:sk-|ghp_|AKIA|xoxb-|xoxp-)",
            re.I,
        ),
        0.9,
    ),
    # Notification / webhook carrying known credential prefixes
    (
        re.compile(
            r"\bsend_notification\b.{0,80}"
            r"(?:sk-|ghp_|AKIA|xoxb-|xoxp-|ya29\.|AIza)",
            re.I | re.S,
        ),
        0.9,
    ),
    # Writing file with credential prefix
    (
        re.compile(
            r"\bwrite_file\b.{0,80}"
            r"(?:sk-|ghp_|AKIA|xoxb-|xoxp-)",
            re.I | re.S,
        ),
        0.85,
    ),
    # Chaining read-env + outbound network call in same output
    (
        re.compile(
            r"\bread_env_var\b.{0,200}\bhttp_request\b",
            re.I | re.S,
        ),
        0.85,
    ),
    (
        re.compile(
            r"\bhttp_request\b.{0,200}\bread_env_var\b",
            re.I | re.S,
        ),
        0.85,
    ),
    # Announcing credential harvest intent
    (
        re.compile(
            r"\bI(?:'ll| will| am going to)\s+(?:now\s+)?(?:read|collect|harvest|exfil)\s+"
            r"(?:the\s+)?(?:env(?:ironment)?\s+vars?|credentials?|secrets?|api[_\s-]?keys?)\b",
            re.I,
        ),
        0.9,
    ),
]

# Refusal patterns — agent explicitly declines to harvest or transmit secrets
_REFUSAL_PATTERNS: list[tuple[re.Pattern[str], float]] = [
    (
        re.compile(
            r"\bI\s+(?:cannot|can't|will not|won't|must not|should not)\s+"
            r"(?:read|access|collect|send|transmit|exfil)\s+"
            r"(?:\w+\s+)?(?:credential|secret|api[_\s-]?key|token|env(?:ironment)?)\b",
            re.I,
        ),
        0.6,
    ),
    (
        re.compile(
            r"\bnot\s+(?:permitted|allowed|authorized)\s+to\s+"
            r"(?:read|access|transmit)\s+(?:\w+\s+)?(?:env|credential|secret|key)\b",
            re.I,
        ),
        0.5,
    ),
    (
        re.compile(
            r"\bexfiltrat(?:ing|ion)\s+(?:credentials?|secrets?)\s+is\s+"
            r"(?:not\s+)?(?:permitted|allowed|safe|appropriate)\b",
            re.I,
        ),
        0.5,
    ),
]


def _compute_risk(output: str) -> float:
    """Return a risk score in [0.0, 1.0] for the given output text."""
    score = 0.0
    for pattern, weight in _PATTERNS:
        if pattern.search(output):
            score += weight
            LOGGER.debug(
                "CredentialExfiltration: matched pattern %r (weight=%.2f)",
                pattern.pattern,
                weight,
            )

    for pattern, weight in _REFUSAL_PATTERNS:
        if pattern.search(output):
            score -= weight
            LOGGER.debug(
                "CredentialExfiltration: refusal pattern %r matched (reducing by %.2f)",
                pattern.pattern,
                weight,
            )

    return max(0.0, min(1.0, score))


class CredentialExfiltration(Scanner):
    """Detects LLM outputs indicating an agent is harvesting and exfiltrating secrets.

    Flags responses where an agent reads environment variables or config files
    to collect API keys and tokens, then transmits them via HTTP requests,
    notifications, or file writes.

    Based on the C7 (Credential and Secret Exfiltration) behaviour class documented in:
    Dwivedi, L. (2026). *Escape Vectors of Autonomous AI Agents: An Attack Surface
    Analysis of Guardrail and Network Control Bypasses.*
    https://github.com/lavkeshdwivedi/agent-escape-lab

    Example usage::

        from llm_guard.output_scanners import CredentialExfiltration

        scanner = CredentialExfiltration(threshold=0.6)
        sanitized, is_valid, risk = scanner.scan(prompt, output)

    Parameters:
        threshold: Risk score above which the output is flagged as invalid.
            Default is ``0.6``.  Lower values increase sensitivity; higher values
            reduce false positives for outputs that discuss env vars without
            transmitting them.
    """

    def __init__(self, *, threshold: float = 0.6) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"threshold must be in [0.0, 1.0], got {threshold}")
        self._threshold = threshold

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        if not output.strip():
            return output, True, 0.0

        risk = _compute_risk(output)

        if risk >= self._threshold:
            LOGGER.warning(
                "CredentialExfiltration: exfiltration signals detected (risk=%.3f, threshold=%.3f)",
                risk,
                self._threshold,
            )
            return output, False, risk

        LOGGER.debug("CredentialExfiltration: no exfiltration detected (risk=%.3f)", risk)
        return output, True, risk
