from typing import Dict, Optional, Sequence

from llm_guard.input_scanners.ban_competitors import BanCompetitors as InputBanCompetitors

from .base import Scanner


class BanCompetitors(Scanner):
    """
    Scanner that detects if an output contains a competitor.

    It uses a named-entity recognition model to extract organization and match it against a list of competitors.
    """

    def __init__(
        self,
        competitors: Sequence[str],
        *,
        threshold: float = 0.5,
        redact: bool = True,
        model: Optional[Dict] = None,
    ):
        """
        Initializes BanCompetitors object.

        Parameters:
            competitors (Sequence[str]): List of competitors to ban.
            threshold (float, optional): Threshold to determine if an organization is present in the output. Default is 0.5.
            redact (bool, optional): Whether to redact the organization name. Default is True.
            model (Dict, optional): Model to use for named-entity recognition. Default is BASE model.

        Raises:
            ValueError: If no competitors are provided.
        """
        self._scanner = InputBanCompetitors(
            competitors,
            threshold=threshold,
            redact=redact,
            model=model,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
