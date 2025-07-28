from llm_guard.input_scanners.emotion_detection import EmotionDetection as InputEmotionDetection

from .base import Scanner


class EmotionDetection(Scanner):
    """
    An emotion detection scanner for model outputs that uses the roberta-base-go_emotions model.
    It can detect and flag outputs containing specific emotions or high-intensity emotions.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize EmotionDetection scanner for outputs.

        Parameters:
            **kwargs: Arguments passed to the input emotion detection scanner.
        """
        self._scanner = InputEmotionDetection(**kwargs)

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        return self._scanner.scan(output)

    def get_emotion_analysis(self, output: str) -> dict[str, float]:
        """
        Get full emotion analysis for the given output.

        Parameters:
            output (str): The model output to analyze.

        Returns:
            Dict[str, float]: Dictionary mapping emotion labels to their scores.
        """
        return self._scanner.get_emotion_analysis(output)

    def scan_with_full_output(
        self, prompt: str, output: str
    ) -> tuple[str, bool, float, dict[str, float]]:
        """
        Scan the output and return full emotion analysis along with the standard results.

        Parameters:
            prompt (str): The input prompt (not used in emotion detection).
            output (str): The model output to scan.

        Returns:
            tuple[str, bool, float, Dict[str, float]]:
                - sanitized_output: The output (unchanged)
                - is_valid: Whether the output is valid
                - risk_score: The risk score
                - emotion_analysis: Full emotion analysis with scores
        """
        return self._scanner.scan_with_full_output(output)
