"""
Wrapper functions for integrating feedback collection with llm-guard scanning.

This module provides thin wrapper functions around scan_prompt() and scan_output()
that optionally record scan results to a FeedbackCollector.

These wrappers are:
- Drop-in replacements (same signatures + optional collector parameter)
- Side-effect-free when collector is None or disabled
- Non-invasive (no modification to core scanning behavior)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from llm_guard import scan_output, scan_prompt

if TYPE_CHECKING:
    from llm_guard.input_scanners.base import Scanner as InputScanner
    from llm_guard.output_scanners.base import Scanner as OutputScanner

    from .collector import FeedbackCollector


def scan_prompt_with_feedback(
    scanners: Sequence[InputScanner],
    prompt: str,
    collector: FeedbackCollector | None = None,
    **kwargs,
) -> tuple[str, dict[str, bool], dict[str, float]]:
    """
    Wrapper around scan_prompt() with optional feedback collection.

    This function calls the standard scan_prompt() and optionally records
    the scan result to a FeedbackCollector for feedback tracking.

    The return value is EXACTLY the same as scan_prompt().

    Args:
        scanners: List of input scanners to apply.
        prompt: The input prompt to scan.
        collector: Optional FeedbackCollector instance. If None or disabled,
                  no feedback is recorded (zero overhead).
        **kwargs: Additional arguments passed to scan_prompt() (e.g., fail_fast).

    Returns:
        Tuple of (sanitized_prompt, results_valid, results_score)
        - sanitized_prompt: The sanitized prompt after all scanners
        - results_valid: Dict mapping scanner names to validity (bool)
        - results_score: Dict mapping scanner names to risk scores (float)

    Example:
        >>> from llm_guard.input_scanners import Toxicity
        >>> from llm_guard.feedback import FeedbackCollector, FeedbackCollectorConfig
        >>>
        >>> config = FeedbackCollectorConfig(enabled=True)
        >>> collector = FeedbackCollector(config)
        >>> scanners = [Toxicity()]
        >>>
        >>> sanitized, valid, scores = scan_prompt_with_feedback(
        ...     scanners,
        ...     "Hello world",
        ...     collector=collector
        ... )
    """
    # Call the core scan_prompt function
    sanitized_prompt, results_valid, results_score = scan_prompt(list(scanners), prompt, **kwargs)

    # Record to collector if provided and enabled
    if collector is not None:
        # Build scanner_results in the format expected by collector
        scanner_results = {}
        for scanner_name in results_valid.keys():
            scanner_results[scanner_name] = {
                "valid": results_valid[scanner_name],
                "score": results_score[scanner_name],
            }

        # Record the scan (collector handles enabled check internally)
        collector.record_scan(
            scan_type="prompt",
            scanner_results=scanner_results,
            prompt=prompt,
            output=None,
        )

    # Return EXACTLY the same values as scan_prompt
    return sanitized_prompt, results_valid, results_score


def scan_output_with_feedback(
    scanners: Sequence[OutputScanner],
    prompt: str,
    output: str,
    collector: FeedbackCollector | None = None,
    **kwargs,
) -> tuple[str, dict[str, bool], dict[str, float]]:
    """
    Wrapper around scan_output() with optional feedback collection.

    This function calls the standard scan_output() and optionally records
    the scan result to a FeedbackCollector for feedback tracking.

    The return value is EXACTLY the same as scan_output().

    Args:
        scanners: List of output scanners to apply.
        prompt: The original input prompt.
        output: The output to scan.
        collector: Optional FeedbackCollector instance. If None or disabled,
                  no feedback is recorded (zero overhead).
        **kwargs: Additional arguments passed to scan_output() (e.g., fail_fast).

    Returns:
        Tuple of (sanitized_output, results_valid, results_score)
        - sanitized_output: The sanitized output after all scanners
        - results_valid: Dict mapping scanner names to validity (bool)
        - results_score: Dict mapping scanner names to risk scores (float)

    Example:
        >>> from llm_guard.output_scanners import Toxicity
        >>> from llm_guard.feedback import FeedbackCollector, FeedbackCollectorConfig
        >>>
        >>> config = FeedbackCollectorConfig(enabled=True)
        >>> collector = FeedbackCollector(config)
        >>> scanners = [Toxicity()]
        >>>
        >>> sanitized, valid, scores = scan_output_with_feedback(
        ...     scanners,
        ...     "What is AI?",
        ...     "AI is artificial intelligence",
        ...     collector=collector
        ... )
    """
    # Call the core scan_output function
    sanitized_output, results_valid, results_score = scan_output(
        list(scanners), prompt, output, **kwargs
    )

    # Record to collector if provided and enabled
    if collector is not None:
        # Build scanner_results in the format expected by collector
        scanner_results = {}
        for scanner_name in results_valid.keys():
            scanner_results[scanner_name] = {
                "valid": results_valid[scanner_name],
                "score": results_score[scanner_name],
            }

        # Record the scan (collector handles enabled check internally)
        collector.record_scan(
            scan_type="output",
            scanner_results=scanner_results,
            prompt=prompt,
            output=output,
        )

    # Return EXACTLY the same values as scan_output
    return sanitized_output, results_valid, results_score
