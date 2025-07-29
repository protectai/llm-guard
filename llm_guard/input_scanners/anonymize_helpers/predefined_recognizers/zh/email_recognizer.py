from presidio_analyzer import Pattern
from presidio_analyzer.predefined_recognizers import EmailRecognizer as PresidioEmailRecognizer


class EmailRecognizer(PresidioEmailRecognizer):
    PATTERNS = [
        Pattern(
            "Email (Medium)",
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",  # noqa: E501
            0.5,
        ),
    ]
