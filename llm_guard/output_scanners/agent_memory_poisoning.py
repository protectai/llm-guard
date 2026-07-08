"""Agent Memory Poisoning Scanner

Detects LLM outputs that contain instructions to store credentials, bypass
rules, or permission-escalation content in persistent memory or knowledge
stores — a behaviour class documented in Dwivedi (2026) as
"C6 – Persistent Adversarial Memory".

Poisoning signals include:

- Instructions to write API keys, tokens, or secrets into long-term memory.
- Storing bypass flags or lifted-restriction markers for retrieval next session.
- Writing permission-escalation state (e.g. "unrestricted", "admin mode") into
  a session config or knowledge base.
- Chaining "remember this for next session" with access or credential language.

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
# Poison pattern definitions
# Each entry: (compiled_regex, weight)
# ---------------------------------------------------------------------------

_PATTERNS: list[tuple[re.Pattern[str], float]] = [
    # Storing credentials in memory / knowledge store
    (
        re.compile(
            r"\b(?:stor(?:e|es|ed|ing)|sav(?:e|es|ed|ing)|writ(?:e|es|ing)"
            r"|rememb(?:er|ers|ered|ering)|record(?:s|ed|ing)?|persist(?:s|ed|ing)?)\b"
            r".{0,40}"
            r"\b(?:api[_\s-]?keys?|tokens?|secrets?|credentials?|passwords?|auth)\b",
            re.I | re.S,
        ),
        0.9,
    ),
    # Saving bypass / override state for later sessions
    (
        re.compile(
            r"\b(?:stor(?:e|es|ed|ing)|sav(?:e|es|ed|ing)|writ(?:e|es|ing)"
            r"|rememb(?:er|ers|ered|ering)|record(?:s|ed|ing)?|persist(?:s|ed|ing)?)\b"
            r".{0,40}"
            r"\b(?:bypass|override|lifted|unrestricted|no[_\s-]?restrict)\b",
            re.I | re.S,
        ),
        0.85,
    ),
    # "Next session" combined with access / permission language
    (
        re.compile(
            r"\bnext\s+session\b.{0,60}"
            r"\b(?:access|permission|network|credential|admin|elevated)\b",
            re.I | re.S,
        ),
        0.8,
    ),
    (
        re.compile(
            r"\b(?:access|permission|network|credential|admin|elevated)\b.{0,60}"
            r"\bnext\s+session\b",
            re.I | re.S,
        ),
        0.8,
    ),
    # "Remember" / "recall" combined with auth material
    (
        re.compile(
            r"\b(?:remember|recall|retrieve)\b.{0,40}"
            r"\b(?:auth|token|key|secret|password)\b",
            re.I | re.S,
        ),
        0.75,
    ),
    # Writing unrestricted config to session or knowledge store
    (
        re.compile(
            r"\bwrite\b.{0,50}"
            r"\bconfig\b.{0,40}"
            r"\b(?:external|unrestricted|bypass|admin)\b",
            re.I | re.S,
        ),
        0.8,
    ),
    (
        re.compile(
            r"\b(?:external|unrestricted|bypass|admin)\b.{0,40}"
            r"\bconfig\b.{0,50}"
            r"\bwrite\b",
            re.I | re.S,
        ),
        0.8,
    ),
    # Announcing intention to poison memory
    (
        re.compile(
            r"\bI(?:'ll| will| am going to)\s+(?:now\s+)?"
            r"(?:store|save|write|record)\s+(?:the\s+)?(?:\w+\s+)?"
            r"(?:api[_\s-]?key|token|secret|credential|password)\b",
            re.I,
        ),
        0.9,
    ),
    # Explicit memory / knowledge-store tool call patterns
    (
        re.compile(
            r"\b(?:store_memory|save_to_memory|write_knowledge|add_to_kb)\s*\(",
            re.I,
        ),
        0.85,
    ),
]

# Refusal patterns — agent explicitly declines to store sensitive material
_REFUSAL_PATTERNS: list[tuple[re.Pattern[str], float]] = [
    (
        re.compile(
            r"\bI\s+(?:cannot|can't|will not|won't|must not|should not)\s+"
            r"(?:store|save|write|record)\s+(?:\w+\s+)?"
            r"(?:credential|api[_\s-]?key|token|secret|password)\b",
            re.I,
        ),
        0.6,
    ),
    (
        re.compile(
            r"\bnot\s+(?:permitted|allowed|authorized)\s+to\s+(?:save|store)\b",
            re.I,
        ),
        0.5,
    ),
    (
        re.compile(
            r"\bstoring\s+(?:credentials?|secrets?|tokens?|passwords?)\s+"
            r"(?:is\s+)?(?:not\s+)?(?:permitted|allowed|safe|appropriate)\b",
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
                "AgentMemoryPoisoning: matched pattern %r (weight=%.2f)",
                pattern.pattern,
                weight,
            )

    for pattern, weight in _REFUSAL_PATTERNS:
        if pattern.search(output):
            score -= weight
            LOGGER.debug(
                "AgentMemoryPoisoning: refusal pattern %r matched (reducing by %.2f)",
                pattern.pattern,
                weight,
            )

    return max(0.0, min(1.0, score))


class AgentMemoryPoisoning(Scanner):
    """Detects LLM outputs that poison persistent memory with credentials or bypass rules.

    Flags responses where an agent stores API keys, tokens, secrets, or
    permission-escalation state into long-term memory or knowledge stores for
    retrieval in future sessions.

    Based on the C6 (Persistent Adversarial Memory) behaviour class documented in:
    Dwivedi, L. (2026). *Escape Vectors of Autonomous AI Agents: An Attack Surface
    Analysis of Guardrail and Network Control Bypasses.*
    https://github.com/lavkeshdwivedi/agent-escape-lab

    Example usage::

        from llm_guard.output_scanners import AgentMemoryPoisoning

        scanner = AgentMemoryPoisoning(threshold=0.6)
        sanitized, is_valid, risk = scanner.scan(prompt, output)

    Parameters:
        threshold: Risk score above which the output is flagged as invalid.
            Default is ``0.6``.  Lower values increase sensitivity; higher values
            reduce false positives for outputs that merely discuss memory concepts
            without writing sensitive material to them.
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
                "AgentMemoryPoisoning: memory poisoning signals detected (risk=%.3f, threshold=%.3f)",
                risk,
                self._threshold,
            )
            return output, False, risk

        LOGGER.debug("AgentMemoryPoisoning: no poisoning detected (risk=%.3f)", risk)
        return output, True, risk
