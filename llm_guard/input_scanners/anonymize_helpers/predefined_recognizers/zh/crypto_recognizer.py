from presidio_analyzer import Pattern
from presidio_analyzer.predefined_recognizers import CryptoRecognizer as PresidioCryptoRecognizer


class CryptoRecognizer(PresidioCryptoRecognizer):
    PATTERNS = [
        Pattern("Crypto (Medium)", r"[13][a-km-zA-HJ-NP-Z1-9]{26,33}", 0.5),
    ]
