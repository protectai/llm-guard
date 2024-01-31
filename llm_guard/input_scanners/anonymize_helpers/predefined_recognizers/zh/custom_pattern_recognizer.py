import re
from typing import List

from presidio_analyzer import Pattern, PatternRecognizer


class CustomPatternRecognizer(PatternRecognizer):
    def _deny_list_to_regex(self, deny_list: List[str]) -> Pattern:
        """
        Convert a list of characters to a matching regex.

        :param deny_list: the list of characters to detect
        :return:the regex of the characters for detection
        """
        escaped_deny_list = [re.escape(element) for element in deny_list]
        regex = r"(" + "|".join(escaped_deny_list) + r")"
        return Pattern(name="deny_list", regex=regex, score=self.deny_list_score)
