import unicodedata

from llm_guard.util import get_logger

from .base import Scanner

LOGGER = get_logger()


class InvisibleText(Scanner):
    """
    A class for scanning if the prompt includes invisible characters.

    This class uses the unicodedata library to detect invisible characters in the output of the language model.
    """

    def __init__(self) -> None:
        """
        Initializes InvisibleText.
        """
        self._banned_categories = ["Cf", "Co", "Cn"]

    @staticmethod
    def contains_unicode(text: str) -> bool:
        return any(ord(char) > 127 for char in text)

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        if not self.contains_unicode(prompt):
            return prompt, True, 0.0

        chars = []
        for char in prompt:
            if unicodedata.category(char) not in self._banned_categories:
                continue

            chars.append(char)
            prompt = prompt.replace(char, "")

        if chars:
            LOGGER.warning("Found invisible characters in the prompt", chars=chars)

            return prompt, False, 1.0

        LOGGER.debug("No invisible characters found")
        return prompt, True, 0.0
