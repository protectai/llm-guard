import hashlib
import logging
import os
import tempfile
from typing import Any, Dict, Optional

from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.settings import transient_settings
from presidio_anonymizer.core.text_replace_builder import TextReplaceBuilder

from .base import Scanner

log = logging.getLogger(__name__)

_default_detect_secrets_config = {
    "plugins_used": [
        {"name": "SoftlayerDetector"},
        {"name": "StripeDetector"},
        {"name": "SendGridDetector"},
        {"name": "NpmDetector"},
        {"name": "KeywordDetector", "keyword_exclude": ""},
        {"name": "IbmCosHmacDetector"},
        {"name": "DiscordBotTokenDetector"},
        {"name": "BasicAuthDetector"},
        {"name": "AzureStorageKeyDetector"},
        {"name": "ArtifactoryDetector"},
        {"name": "AWSKeyDetector"},
        {"name": "CloudantDetector"},
        {"name": "GitHubTokenDetector"},
        {"name": "IbmCloudIamDetector"},
        {"name": "JwtTokenDetector"},
        {"name": "MailchimpDetector"},
        {"name": "PrivateKeyDetector"},
        {"name": "SlackDetector"},
        {"name": "SquareOAuthDetector"},
        {"name": "TwilioKeyDetector"},
        {"name": "Base64HighEntropyString", "limit": 4.5},
        {"name": "HexHighEntropyString", "limit": 3.0},
    ]
}

# `REDACT_PARTIAL` will show only leading and trailing characters.
REDACT_PARTIAL = "partial"
#  `REDACT_ALL` will shadow the full secret.
REDACT_ALL = "all"
# `REDACT_HASH` will replace the full secret with its hashed value.
REDACT_HASH = "hash"


class Secrets(Scanner):
    """
    Secrets Scanner using the `detect-secrets` library.
    """

    def __init__(
        self,
        detect_secrets_config: Optional[Dict[str, Any]] = None,
        redact_mode: str = REDACT_ALL,
    ):
        """
        Initialize an instance of the Secrets scanner.

        Parameters:
        - detect_secrets_config (Dict, optional): Configuration dictionary for detect-secrets. If not provided, default settings are used.
        - redact_mode (str): Mode for redaction. Defaults to `REDACT_ALL`. Choices are `REDACT_PARTIAL`, `REDACT_ALL`, and `REDACT_HASH`.
        """
        if not detect_secrets_config:
            log.debug(f"No detect secrets config provided, using default")
            detect_secrets_config = _default_detect_secrets_config
        self._detect_secrets_config = detect_secrets_config
        self._redact_mode = redact_mode
        self._secrets = SecretsCollection()

    @staticmethod
    def redact_value(value: str, mode: str) -> str:
        if mode == REDACT_PARTIAL:
            redacted_value = f"{value[:2]}..{value[-2:]}"
        elif mode == REDACT_HASH:
            redacted_value = hashlib.md5(value.encode()).hexdigest()  # nosec
        elif mode == REDACT_ALL:
            redacted_value = "******"
        else:
            raise ValueError(f"redact mode wasn't recognized {mode}")

        return redacted_value

    def scan(self, prompt: str) -> (str, bool, float):
        risk_score = 0.0
        if prompt.strip() == "":
            return prompt, True, risk_score

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(prompt.encode("utf-8"))
        temp_file.close()

        with transient_settings(self._detect_secrets_config):
            self._secrets.scan_file(str(temp_file.name))

        secret_types = []
        text_replace_builder = TextReplaceBuilder(original_text=prompt)
        for file in self._secrets.files:
            for found_secret in self._secrets[file]:
                secret_types.append(found_secret.type)

                character_start_index = prompt.find(found_secret.secret_value, None, None)
                character_end_index = character_start_index + len(str(found_secret.secret_value))
                secret_value = text_replace_builder.get_text_in_position(
                    character_start_index, character_end_index
                )

                text_replace_builder.replace_text_get_insertion_index(
                    Secrets.redact_value(secret_value, self._redact_mode),
                    character_start_index,
                    character_end_index,
                )

        os.remove(temp_file.name)

        if secret_types:
            log.warning(f"Detected secrets in prompt: {secret_types}")
            return text_replace_builder.output_text, False, 1.0

        log.debug("No secrets detected in the prompt")

        return prompt, True, 0.0
