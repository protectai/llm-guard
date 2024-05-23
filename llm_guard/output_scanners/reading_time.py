from llm_guard.util import get_logger

from .base import Scanner

LOGGER = get_logger()


class ReadingTime(Scanner):
    """
    Scanner that checks the reading time of the output against a maximum time.

    If the output exceeds the maximum time, the output will be truncated to fit within the time limit.
    """

    def __init__(self, max_time: float, *, truncate: bool = False) -> None:
        """
        Parameters:
            max_time: Maximum time in minutes that the user should spend reading the output.
            truncate: If True, the output will be truncated to the maximum time.
        """
        self._max_time = max_time
        self._truncate = truncate
        self._words_per_minute = 200  # Average reading speed

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        words = output.split()
        word_count = len(words)
        reading_time_minutes = word_count / self._words_per_minute

        if reading_time_minutes > self._max_time:
            LOGGER.warning(
                "Output exceeded maximum reading time",
                reading_time_minutes=reading_time_minutes,
                max_reading_time_minutes=self._max_time,
            )
            if self._truncate:
                # Calculate the maximum number of words to fit within the time limit
                max_words = int(self._max_time * self._words_per_minute)
                output = " ".join(words[:max_words])

            return output, False, 1.0

        LOGGER.debug("Output reading time", reading_time_minutes=reading_time_minutes)
        return output, True, 0.0
