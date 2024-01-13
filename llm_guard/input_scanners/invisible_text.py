import unicodedata

from llm_guard.util import logger

from .base import Scanner


class InvisibleText(Scanner):
    """
    A class for scanning if the prompt includes invisible characters.

    This class uses the unicodedata library to detect invisible characters in the output of the language model.
    """

    def __init__(self):
        """
        Initializes InvisibleText.
        """
        self._banned_categories = ["Cf", "Cc", "Co", "Cn"]

    @staticmethod
    def contains_unicode(text: str):
        return any(ord(char) > 127 for char in text)

    def scan(self, prompt: str) -> (str, bool, float):
        if not self.contains_unicode(prompt):
            return prompt, True, 0.0

        chars = []
        for char in prompt:
            if unicodedata.category(char) not in self._banned_categories:
                continue

            chars.append(char)
            prompt = prompt.replace(char, "")

        if chars:
            logger.warning(f"Found invisible characters {chars} in the prompt")

            return prompt, False, 1.0

        logger.debug(f"No invisible characters found")
        return prompt, True, 0.0
