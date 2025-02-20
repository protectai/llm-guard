import logging
from typing import Any, Dict, List, Optional, Union

from langchain.callbacks.manager import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.pydantic_v1 import BaseModel, root_validator
from langchain.schema.messages import BaseMessage

logger = logging.getLogger(__name__)

try:
    import llm_guard
except ImportError:
    raise ModuleNotFoundError(
        "Could not import llm-guard python package. Please install it with `pip install llm-guard`."
    )


class LLMGuardPromptException(Exception):
    """Exception to raise when llm-guard marks prompt invalid."""


class LLMGuardPromptChain(Chain):
    scanners: Dict[str, Dict] = {}
    """The scanners to use."""
    scanners_ignore_errors: List[str] = []
    """The scanners to ignore if they throw errors."""
    vault: Optional[llm_guard.vault.Vault] = None
    """The scanners to ignore errors from."""
    raise_error: bool = True
    """Whether to raise an error if the LLMGuard marks the prompt invalid."""

    input_key: str = "input"  #: :meta private:
    output_key: str = "sanitized_input"  #: :meta private:
    initialized_scanners: List[Any] = []  #: :meta private:

    @root_validator(pre=True)
    def init_scanners(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initializes scanners

        Args:
            values (Dict[str, Any]): A dictionary containing configuration values.

        Returns:
            Dict[str, Any]: A dictionary with the updated configuration values,
                            including the initialized scanners.

        Raises:
            ValueError: If there is an issue importing 'llm-guard' or loading scanners.
        """

        if values.get("initialized_scanners") is not None:
            return values
        try:
            if values.get("scanners") is not None:
                values["initialized_scanners"] = []
                for scanner_name in values.get("scanners"):
                    scanner_config = values.get("scanners")[scanner_name]
                    if scanner_name == "Anonymize":
                        scanner_config["vault"] = values["vault"]

                    values["initialized_scanners"].append(
                        llm_guard.input_scanners.get_scanner_by_name(scanner_name, scanner_config)
                    )

            return values
        except Exception as e:
            raise ValueError(
                f"Could not initialize scanners. Please check provided configuration. {e}"
            ) from e

    @property
    def input_keys(self) -> List[str]:
        """
        Returns a list of input keys expected by the prompt.

        This method defines the input keys that the prompt expects in order to perform
        its processing. It ensures that the specified keys are available for providing
        input to the prompt.

        Returns:
           List[str]: A list of input keys.

        Note:
           This method is considered private and may not be intended for direct
           external use.
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """
        Returns a list of output keys.

        This method defines the output keys that will be used to access the output
        values produced by the chain or function. It ensures that the specified keys
        are available to access the outputs.

        Returns:
            List[str]: A list of output keys.

        Note:
            This method is considered private and may not be intended for direct
            external use.

        """
        return [self.output_key]

    def _check_result(
        self,
        scanner_name: str,
        is_valid: bool,
        risk_score: float,
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ):
        if is_valid:
            return  # prompt is valid, keep scanning

        if run_manager:
            run_manager.on_text(
                text=f"This prompt was determined as invalid by {scanner_name} scanner with risk score {risk_score}",
                color="red",
                verbose=self.verbose,
            )

        if scanner_name in self.scanners_ignore_errors:
            return  # ignore error, keep scanning

        if self.raise_error:
            raise LLMGuardPromptException(
                f"This prompt was determined as invalid based on configured policies with risk score {risk_score}"
            )

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        raise NotImplementedError("Async not implemented yet")

    def _call(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        """
        Executes the scanning process on the prompt and returns the sanitized prompt.

        This internal method performs the scanning process on the prompt. It uses the
        provided scanners to scan the prompt and then returns the sanitized prompt.
        Additionally, it provides the option to log information about the run using
        the provided `run_manager`.

        Args:
            inputs: A dictionary containing input values
            run_manager: A run manager to handle run-related events. Default is None

        Returns:
            Dict[str, str]: A dictionary containing the processed output.

        Raises:
            LLMGuardPromptException: If there is an error during the scanning process
        """
        if run_manager:
            run_manager.on_text("Running LLMGuardPromptChain...\n")

        sanitized_prompt = inputs[self.input_keys[0]]
        for scanner in self.initialized_scanners:
            sanitized_prompt, is_valid, risk_score = scanner.scan(sanitized_prompt)
            self._check_result(type(scanner).__name__, is_valid, risk_score, run_manager)

        return {self.output_key: sanitized_prompt}


class LLMGuardOutputException(Exception):
    """Exception to raise when llm-guard marks output invalid."""


class LLMGuardOutputChain(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    scanners: Dict[str, Dict] = {}
    """The scanners to use."""
    scanners_ignore_errors: List[str] = []
    """The scanners to ignore if they throw errors."""
    vault: Optional[llm_guard.vault.Vault] = None
    """The scanners to ignore errors from."""
    raise_error: bool = True
    """Whether to raise an error if the LLMGuard marks the output invalid."""

    initialized_scanners: List[Any] = []  #: :meta private:

    @root_validator(pre=True)
    def init_scanners(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initializes scanners

        Args:
            values (Dict[str, Any]): A dictionary containing configuration values.

        Returns:
            Dict[str, Any]: A dictionary with the updated configuration values,
                            including the initialized scanners.

        Raises:
            ValueError: If there is an issue importing 'llm-guard' or loading scanners.
        """

        if values.get("initialized_scanners") is not None:
            return values
        try:
            if values.get("scanners") is not None:
                values["initialized_scanners"] = []
                for scanner_name in values.get("scanners"):
                    scanner_config = values.get("scanners")[scanner_name]
                    if scanner_name == "Deanonymize":
                        scanner_config["vault"] = values["vault"]

                    values["initialized_scanners"].append(
                        llm_guard.output_scanners.get_scanner_by_name(scanner_name, scanner_config)
                    )

            return values
        except Exception as e:
            raise ValueError(
                f"Could not initialize scanners. Please check provided configuration. {e}"
            ) from e

    def _check_result(
        self,
        scanner_name: str,
        is_valid: bool,
        risk_score: float,
    ):
        if is_valid:
            return  # prompt is valid, keep scanning

        logger.warning(
            f"This output was determined as invalid by {scanner_name} scanner with risk score {risk_score}"
        )

        if scanner_name in self.scanners_ignore_errors:
            return  # ignore error, keep scanning

        if self.raise_error:
            raise LLMGuardOutputException(
                f"This output was determined as invalid based on configured policies with risk score {risk_score}"
            )

    def scan(
        self,
        prompt: str,
        output: Union[BaseMessage, str],
    ) -> Union[BaseMessage, str]:
        sanitized_output = output
        if isinstance(output, BaseMessage):
            sanitized_output = sanitized_output.content

        for scanner in self.initialized_scanners:
            sanitized_output, is_valid, risk_score = scanner.scan(prompt, sanitized_output)
            self._check_result(type(scanner).__name__, is_valid, risk_score)

        if isinstance(output, BaseMessage):
            output.content = sanitized_output
            return output

        return sanitized_output


from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema.messages import SystemMessage
from langchain.schema.output_parser import StrOutputParser

llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106")

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="You are a helpful assistant, which creates the best SQL queries based on my command"
        ),
        HumanMessagePromptTemplate.from_template("{sanitized_input}"),
    ]
)

vault = llm_guard.vault.Vault()
use_onnx = True

llm_guard_prompt_scanner = LLMGuardPromptChain(
    vault=vault,
    scanners={
        "Anonymize": {"use_faker": True, "use_onnx": use_onnx},
        "BanSubstrings": {
            "substrings": ["Laiyer"],
            "match_type": "word",
            "case_sensitive": False,
            "redact": True,
        },
        "BanTopics": {"topics": ["violence"], "threshold": 0.7, "use_onnx": use_onnx},
        "Code": {"denied": ["go"], "use_onnx": use_onnx},
        "Language": {"valid_languages": ["en"], "use_onnx": use_onnx},
        "PromptInjection": {"threshold": 0.95, "use_onnx": use_onnx},
        "Regex": {"bad_patterns": ["Bearer [A-Za-z0-9-._~+/]+"]},
        "Secrets": {"redact_mode": "all"},
        "Sentiment": {"threshold": -0.05},
        "TokenLimit": {"limit": 4096},
        "Toxicity": {"threshold": 0.8, "use_onnx": use_onnx},
    },
    scanners_ignore_errors=[
        "Anonymize",
        "BanSubstrings",
        "Regex",
        "Secrets",
        "TokenLimit",
    ],  # These scanners redact, so I can skip them from failing the prompt
)

llm_guard_output_scanner = LLMGuardOutputChain(
    vault=vault,
    scanners={
        "BanSubstrings": {
            "substrings": ["Laiyer"],
            "match_type": "word",
            "case_sensitive": False,
            "redact": True,
        },
        "BanTopics": {"topics": ["violence"], "threshold": 0.7, "use_onnx": use_onnx},
        "Bias": {"threshold": 0.75, "use_onnx": use_onnx},
        "Code": {"denied": ["go"], "use_onnx": use_onnx},
        "Deanonymize": {},
        "FactualConsistency": {"minimum_score": 0.5, "use_onnx": use_onnx},
        "JSON": {"required_elements": 0, "repair": True},
        "Language": {
            "valid_languages": ["en"],
            "threshold": 0.5,
            "use_onnx": use_onnx,
        },
        "LanguageSame": {"use_onnx": use_onnx},
        "MaliciousURLs": {"threshold": 0.75, "use_onnx": use_onnx},
        "NoRefusal": {"threshold": 0.5, "use_onnx": use_onnx},
        "Regex": {
            "bad_patterns": ["Bearer [A-Za-z0-9-._~+/]+"],
        },
        "Relevance": {"threshold": 0.5, "use_onnx": use_onnx},
        "Sensitive": {"redact": False, "use_onnx": use_onnx},
        "Sentiment": {"threshold": -0.05},
        "Toxicity": {"threshold": 0.7, "use_onnx": use_onnx},
    },
    scanners_ignore_errors=["BanSubstrings", "Regex", "Sensitive"],
)

input_prompt = "Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com "
"but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and "
"the IP address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. "
"He works in Test LLC."
guarded_chain = (
    llm_guard_prompt_scanner  # scan input here
    | prompt
    | llm
    | (
        lambda ai_message: llm_guard_output_scanner.scan(input_prompt, ai_message)
    )  # scan output here and deanonymize
    | StrOutputParser()
)

result = guarded_chain.invoke(
    {
        "input": input_prompt,
    }
)

print("Result: " + result)
