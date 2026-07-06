"""Agent Escalation Scanner

Detects LLM outputs that indicate an agent is attempting to modify its own
operational constraints — a behavior class documented in Dwivedi (2025) as
"C4 – Autonomous Escalation".

Escalation signals include:

- Describing steps to invoke a configuration or policy API to lift restrictions.
- Framing constraint removal as a necessary step toward task completion.
- Announcing that the agent has updated or is about to update its own rules,
  block-lists, or capability gates.
- Referencing "agent config", "operational constraints", "capability block-list",
  or similar terms alongside modification verbs.

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
# Pattern definitions
# Each entry: (compiled_regex, weight)
# Weights sum to determine final risk; clamped to [0.0, 1.0].
# ---------------------------------------------------------------------------

_PATTERNS: list[tuple[re.Pattern[str], float]] = [
    # Explicit config-tool invocation language
    (re.compile(r"\bupdate[_\s-]?agent[_\s-]?config\b", re.I), 0.9),
    (
        re.compile(
            r"\bmodif(?:y|ied|ying)\s+(?:my|the|agent|its)\s+"
            r"(?:config|configuration|constraints?|restrictions?|rules?|block.?list)\b",
            re.I,
        ),
        0.8,
    ),
    (
        re.compile(
            r"\bremov(?:e|ing|ed)\s+(?:the\s+)?(?:capability\s+)?"
            r"(?:block|restriction|constraint|limit)\b",
            re.I,
        ),
        0.75,
    ),
    (re.compile(r"\bunblock(?:ing|ed)?\s+(?:the\s+)?capability\b", re.I), 0.75),
    # Announcing self-modification
    (
        re.compile(
            r"\bI(?:'ll| will| am going to)\s+(?:now\s+)?(?:update|modify|change|adjust)\s+"
            r"(?:my|the)\s+(?:config|configuration|constraints?|permissions?|restrictions?)\b",
            re.I,
        ),
        0.85,
    ),
    (
        re.compile(
            r"\bI(?:'ve| have)\s+(?:updated|modified|changed)\s+(?:my|the|its)\s+"
            r"(?:config|configuration|constraints?|permissions?)\b",
            re.I,
        ),
        0.85,
    ),
    # Framing escalation as a prerequisite to task completion
    (
        re.compile(
            r"\bto\s+complete\s+(?:this|the)\s+task\s+"
            r"I(?:'ll| will| need to| must)\s+(?:first\s+)?"
            r"(?:update|modify|change|adjust|lift)\s+(?:my|the)\s+"
            r"(?:config|constraints?|restrictions?|block.?list)\b",
            re.I,
        ),
        0.9,
    ),
    (
        re.compile(
            r"\brequires?\s+(?:me\s+to\s+)?(?:modify|update|change)\s+"
            r"(?:my|the\s+agent(?:'s)?)\s+(?:config|configuration|constraints?|restrictions?)\b",
            re.I,
        ),
        0.8,
    ),
    # Generic "lifting" or "disabling" restrictions
    (
        re.compile(
            r"\b(?:lift|disable|bypass|circumvent|override)\s+(?:the\s+)?"
            r"(?:block|restriction|constraint|limit|capability\s+gate|guardrail)\b",
            re.I,
        ),
        0.7,
    ),
    # Config-API call patterns (tool function names that appear verbatim in outputs)
    (
        re.compile(
            r"\bset(?:ting)?\s+(?:network_access|allowed_paths|blocked_capabilities)\s*=",
            re.I,
        ),
        0.8,
    ),
]

# Phrases indicating the agent is REFUSING to escalate.
# Each matched refusal pattern reduces the cumulative risk score.
_REFUSAL_PATTERNS: list[tuple[re.Pattern[str], float]] = [
    (
        re.compile(
            r"\bI\s+(?:cannot|can't|will not|won't|must not|should not)\s+"
            r"(?:modify|update|change)\s+(?:my|the)\s+(?:config|constraints?|restrictions?)\b",
            re.I,
        ),
        0.6,
    ),
    (
        re.compile(
            r"\bnot\s+(?:permitted|allowed|authorized)\s+to\s+modify\s+"
            r"(?:my|the)\s+(?:config|constraints?)\b",
            re.I,
        ),
        0.5,
    ),
    (
        re.compile(
            r"\bagainst\s+(?:my|the)\s+(?:policy|guidelines?|operational\s+constraints?)\b",
            re.I,
        ),
        0.4,
    ),
    (
        re.compile(
            r"\bI\s+(?:am\s+)?(?:designed|configured|instructed)\s+not\s+to\s+"
            r"(?:modify|change|update)\b",
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
                "AgentEscalation: matched pattern %r (weight=%.2f)",
                pattern.pattern,
                weight,
            )

    for pattern, weight in _REFUSAL_PATTERNS:
        if pattern.search(output):
            score -= weight
            LOGGER.debug(
                "AgentEscalation: refusal pattern %r matched (reducing by %.2f)",
                pattern.pattern,
                weight,
            )

    return max(0.0, min(1.0, score))


class AgentEscalation(Scanner):
    """Detects LLM outputs indicating autonomous self-constraint modification.

    Flags responses where an agent describes invoking a configuration API to lift
    its own operational restrictions, framing constraint removal as a task step,
    or announcing that it has already modified its own rules.

    Based on the C4 (Autonomous Escalation) behavior class documented in:
    Dwivedi, L. (2025). *Escape Vectors of Autonomous AI Agents: An Attack Surface
    Analysis of Guardrail and Network Control Bypasses.*

    Empirical results across 29 models showed 9 models (31%) across 5 providers
    invoked a ``update_agent_config``-style tool to remove their own constraints.

    Example usage::

        from llm_guard.output_scanners import AgentEscalation

        scanner = AgentEscalation(threshold=0.6)
        sanitized, is_valid, risk = scanner.scan(prompt, output)

    Parameters:
        threshold: Risk score above which the output is flagged as invalid.
            Default is ``0.6``.  Lower values increase sensitivity; higher values
            reduce false positives for outputs that merely discuss configuration
            concepts without acting on them.
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
                "AgentEscalation: escalation signals detected (risk=%.3f, threshold=%.3f)",
                risk,
                self._threshold,
            )
            return output, False, risk

        LOGGER.debug("AgentEscalation: no escalation detected (risk=%.3f)", risk)
        return output, True, risk
