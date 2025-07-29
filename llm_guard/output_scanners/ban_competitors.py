from __future__ import annotations

from llm_guard.input_scanners.ban_competitors import BanCompetitors as InputBanCompetitors
from llm_guard.model import Model

from .base import Scanner


class BanCompetitors(Scanner):
    """
    Scanner that detects if an output contains a competitor.

    It uses a named-entity recognition model to extract organization and match it against a list of competitors.
    """

    def __init__(
        self,
        competitors: list[str],
        *,
        threshold: float = 0.5,
        redact: bool = True,
        model: Model | None = None,
        use_onnx: bool = False,
    ) -> None:
        """
        Initializes BanCompetitors object.

        Parameters:
            competitors: List of competitors to ban.
            threshold: Threshold to determine if an organization is present in the output. Default is 0.5.
            redact: Whether to redact the organization name. Default is True.
            model: Model to use for named-entity recognition. Default is BASE model.
            use_onnx: Whether to use ONNX instead of PyTorch for inference. Default is False.

        Raises:
            ValueError: If no competitors are provided.
        """
        self._scanner = InputBanCompetitors(
            competitors,
            threshold=threshold,
            redact=redact,
            model=model,
            use_onnx=use_onnx,
        )

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        return self._scanner.scan(output)
