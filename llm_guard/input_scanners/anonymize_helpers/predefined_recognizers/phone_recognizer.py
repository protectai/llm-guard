from presidio_analyzer.predefined_recognizers import PhoneRecognizer as PresidioPhoneRecognizer


class PhoneRecognizer(PresidioPhoneRecognizer):
    DEFAULT_SUPPORTED_REGIONS = ("US", "UK", "DE", "FE", "IL", "IN", "CA", "BR", "CN")
