from __future__ import annotations

from typing import Optional, Sequence

from llm_guard.util import get_logger, lazy_load_dep

from .base import Scanner

LOGGER = get_logger()

DEFAULT_BLOCK_SEVERITIES: tuple[str, ...] = ("critical", "high")


class AgentThreatRules(Scanner):
    """A scanner that detects AI-agent threats using Agent Threat Rules (ATR).

    ATR (https://github.com/Agent-Threat-Rule/agent-threat-rules) is an open,
    MIT-licensed detection-rule standard for AI-agent / LLM / MCP attacks —
    prompt injection, tool poisoning, credential exfiltration, and skill
    supply-chain attacks. This scanner evaluates the prompt against the ATR
    rule corpus (via the ``pyatr`` engine) and marks it invalid when a rule at
    or above the configured severity matches.

    Requires the optional ``pyatr`` dependency: ``pip install llm-guard[agent-threat-rules]``.
    """

    def __init__(
        self,
        *,
        block_severities: Sequence[str] = DEFAULT_BLOCK_SEVERITIES,
        rules_dir: Optional[str] = None,
    ) -> None:
        """
        Parameters:
            block_severities: ATR severities that mark the prompt invalid. Defaults to ("critical", "high").
            rules_dir: Directory of ATR rule YAML files. Omit to use the rules bundled with ``pyatr``.
        """
        adapters = lazy_load_dep("pyatr.adapters", "pyatr")
        self._guard = adapters.ATRGuard(block_severities=block_severities, rules_dir=rules_dir)

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        if not prompt or not prompt.strip():
            return prompt, True, 0.0

        detections = self._guard.detect(prompt, event_type="llm_input")
        if not detections:
            return prompt, True, 0.0

        risk_score = 1.0
        try:
            risk_score = max(float(d.confidence) for d in detections)
        except (TypeError, ValueError):
            risk_score = 1.0

        LOGGER.warning(
            "Detected agent threats in the prompt",
            rule_ids=[d.rule_id for d in detections],
        )
        return prompt, False, min(round(risk_score, 2), 1.0)
