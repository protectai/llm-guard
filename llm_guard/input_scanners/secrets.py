import hashlib
import os
import tempfile

from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.settings import transient_settings
from presidio_anonymizer.core.text_replace_builder import TextReplaceBuilder

from llm_guard.util import logger

from .base import Scanner

_custom_plugins_path = "file://" + os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "secrets_plugins"
)
_default_detect_secrets_config = {
    "plugins_used": [
        {"name": "SoftlayerDetector"},
        {"name": "StripeDetector"},
        {"name": "NpmDetector"},
        {"name": "IbmCosHmacDetector"},
        {"name": "DiscordBotTokenDetector"},
        {"name": "BasicAuthDetector"},
        {"name": "AzureStorageKeyDetector"},
        {"name": "ArtifactoryDetector"},
        {"name": "AWSKeyDetector"},
        {"name": "CloudantDetector"},
        {"name": "IbmCloudIamDetector"},
        {"name": "JwtTokenDetector"},
        {"name": "MailchimpDetector"},
        {"name": "SquareOAuthDetector"},
        {"name": "PrivateKeyDetector"},
        {"name": "TwilioKeyDetector"},
        {"name": "Base64HighEntropyString", "limit": 4.5},
        {"name": "HexHighEntropyString", "limit": 3.0},
        {
            "name": "GitHubTokenCustomDetector",
            "path": _custom_plugins_path + "/github_token.py",
        },
        {
            "name": "AdafruitKeyDetector",
            "path": _custom_plugins_path + "/adafruit.py",
        },
        {
            "name": "AdobeSecretDetector",
            "path": _custom_plugins_path + "/adobe.py",
        },
        {
            "name": "AgeSecretKeyDetector",
            "path": _custom_plugins_path + "/age_secret_key.py",
        },
        {
            "name": "AirtableApiKeyDetector",
            "path": _custom_plugins_path + "/airtable_api_key.py",
        },
        {
            "name": "AlgoliaApiKeyDetector",
            "path": _custom_plugins_path + "/algolia_api_key.py",
        },
        {
            "name": "AlibabaSecretDetector",
            "path": _custom_plugins_path + "/alibaba.py",
        },
        {
            "name": "AsanaSecretDetector",
            "path": _custom_plugins_path + "/asana.py",
        },
        {
            "name": "AtlassianApiTokenDetector",
            "path": _custom_plugins_path + "/atlassian_api_token.py",
        },
        {
            "name": "AuthressAccessKeyDetector",
            "path": _custom_plugins_path + "/authress_access_key.py",
        },
        {
            "name": "BittrexDetector",
            "path": _custom_plugins_path + "/beamer_api_token.py",
        },
        {
            "name": "BitbucketDetector",
            "path": _custom_plugins_path + "/bitbucket.py",
        },
        {
            "name": "BeamerApiTokenDetector",
            "path": _custom_plugins_path + "/bittrex.py",
        },
        {
            "name": "ClojarsApiTokenDetector",
            "path": _custom_plugins_path + "/clojars_api_token.py",
        },
        {
            "name": "CodecovAccessTokenDetector",
            "path": _custom_plugins_path + "/codecov_access_token.py",
        },
        {
            "name": "CoinbaseAccessTokenDetector",
            "path": _custom_plugins_path + "/coinbase_access_token.py",
        },
        {
            "name": "ConfluentDetector",
            "path": _custom_plugins_path + "/confluent.py",
        },
        {
            "name": "ContentfulApiTokenDetector",
            "path": _custom_plugins_path + "/contentful_api_token.py",
        },
        {
            "name": "DatabricksApiTokenDetector",
            "path": _custom_plugins_path + "/databricks_api_token.py",
        },
        {
            "name": "DatadogAccessTokenDetector",
            "path": _custom_plugins_path + "/datadog_access_token.py",
        },
        {
            "name": "DefinedNetworkingApiTokenDetector",
            "path": _custom_plugins_path + "/defined_networking_api_token.py",
        },
        {
            "name": "DigitaloceanDetector",
            "path": _custom_plugins_path + "/digitalocean.py",
        },
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
        redact_mode: str = REDACT_ALL,
    ):
        """
        Initialize an instance of the Secrets scanner.

        Parameters:
        - redact_mode (str): Mode for redaction. Defaults to `REDACT_ALL`. Choices are `REDACT_PARTIAL`, `REDACT_ALL`, and `REDACT_HASH`.
        """
        self._detect_secrets_config = _default_detect_secrets_config
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
            logger.warning(f"Detected secrets in prompt: {secret_types}")
            return text_replace_builder.output_text, False, 1.0

        logger.debug("No secrets detected in the prompt")

        return prompt, True, 0.0
