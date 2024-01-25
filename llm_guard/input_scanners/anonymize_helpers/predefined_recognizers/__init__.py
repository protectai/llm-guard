from typing import List

from presidio_analyzer import EntityRecognizer


def _get_predefined_recognizers(language: str) -> List[EntityRecognizer]:
    if language == "zh":
        from .zh import CryptoRecognizer, EmailRecognizer, IpRecognizer, PhoneRecognizer

        return [
            CryptoRecognizer,
            PhoneRecognizer,
            EmailRecognizer,
            IpRecognizer,
        ]
    else:
        return []


__all__ = [
    "_get_predefined_recognizers",
]
