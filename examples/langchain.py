"""
Before running the example, make sure the OPENAI_API_KEY environment variable is set by executing `echo $OPENAI_API_KEY`.

If it is not already set, it can be set by using `export OPENAI_API_KEY=YOUR_API_KEY` on Unix/Linux/MacOS systems or `set OPENAI_API_KEY=YOUR_API_KEY` on Windows systems.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
from langchain.prompts.base import StringPromptValue
from langchain.schema import LLMResult, PromptValue

from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import Anonymize, Jailbreak, PromptInjection, TokenLimit, Toxicity
from llm_guard.output_scanners import Deanonymize, NoRefusal, Relevance, Sensitive
from llm_guard.vault import Vault

logger = logging.getLogger(__name__)


class LLMGuardPromptInvalidException(Exception):
    """Exception to raise when a llm-guard marks prompt invalid."""


class LLMGuardOutputInvalidException(Exception):
    """Exception to raise when a llm-guard marks result invalid."""


class LLMGuardChain(LLMChain):
    """
    LLM Guard Chain
    """

    input_scanners: List[Any] = []
    output_scanners: List[Any] = []
    raise_error: bool = True

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        response = self.generate([inputs], run_manager=run_manager)
        return self.create_outputs(response)[0]

    def generate(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> LLMResult:
        """Generate LLM result from inputs."""
        prompts, stop = self.prep_prompts(input_list, run_manager=run_manager)
        prompts = self.scan_prompts(prompts)

        llm_result = self.llm.generate_prompt(
            prompts,
            stop,
            callbacks=run_manager.get_child() if run_manager else None,
            **self.llm_kwargs,
        )

        return self.scan_result(prompts, llm_result)

    def scan_prompts(self, prompts: List[PromptValue]) -> List[PromptValue]:
        for index, prompt in enumerate(prompts):
            sanitized_prompt, results_valid, results_score = scan_prompt(
                self.input_scanners, prompt.to_string()
            )
            if any(not result for result in results_valid.values()):
                logger.warning(f"Prompt {sanitized_prompt} is not valid, scores: {results_score}")

                if self.raise_error:
                    raise LLMGuardPromptInvalidException(
                        f"Prompt {prompt} is invalid based on scores {results_score}."
                    )

            prompts[index] = StringPromptValue(text=sanitized_prompt)

        return prompts

    def scan_result(self, prompts: List[PromptValue], llm_result: LLMResult) -> LLMResult:
        prompt_strings = [p.to_string() for p in prompts]
        for i, gen_list in enumerate(llm_result.generations):
            for i2, gen_item in enumerate(gen_list):
                sanitized_response_text, results_valid, results_score = scan_output(
                    self.output_scanners, prompt_strings[i], gen_item.text
                )
                if any(not result for result in results_valid.values()):
                    if self.raise_error:
                        raise LLMGuardOutputInvalidException(
                            f"Output {gen_item.text} is invalid based on scores {results_score}."
                        )
                gen_list[i2].text = sanitized_response_text
            llm_result.generations[i] = gen_list

        return llm_result

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        response = await self.agenerate([inputs], run_manager=run_manager)
        return self.create_outputs(response)[0]

    async def agenerate(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> LLMResult:
        """Generate LLM result from inputs."""
        prompts, stop = await self.aprep_prompts(input_list, run_manager=run_manager)
        prompts = await self.ascan_prompts(prompts)
        llm_result = await self.llm.agenerate_prompt(
            prompts,
            stop,
            callbacks=run_manager.get_child() if run_manager else None,
            **self.llm_kwargs,
        )

        return await self.ascan_result(prompts, llm_result)

    async def ascan_prompts(self, prompts: List[PromptValue]) -> List[PromptValue]:
        for index, prompt in enumerate(prompts):
            sanitized_prompt, results_valid, results_score = scan_prompt(
                self.input_scanners, prompt.to_string()
            )
            if any(not result for result in results_valid.values()):
                logger.warning(f"Prompt {prompt} is not valid, scores: {results_score}")

                if self.raise_error:
                    raise LLMGuardPromptInvalidException(
                        f"Prompt {prompt} is invalid based on scores {results_score}."
                    )

            prompts[index] = StringPromptValue(text=sanitized_prompt)

        return prompts

    async def ascan_result(self, prompts: List[PromptValue], llm_result: LLMResult) -> LLMResult:
        prompt_strings = [p.to_string() for p in prompts]
        for i, gen_list in enumerate(llm_result.generations):
            for i2, gen_item in enumerate(gen_list):
                sanitized_response_text, results_valid, results_score = scan_output(
                    self.output_scanners, prompt_strings[i], gen_item.text
                )
                if any(not result for result in results_valid.values()):
                    if self.raise_error:
                        raise LLMGuardOutputInvalidException(
                            f"Output {gen_item.text} is invalid based on scores {results_score}."
                        )
                gen_list[i2].text = sanitized_response_text
            llm_result.generations[i] = gen_list

        return llm_result

    @property
    def _chain_type(self) -> str:
        return "llm_guard_chain"


llm = OpenAI(temperature=0.9, model_name="text-davinci-003")
prompt = PromptTemplate(
    input_variables=["name", "email1", "email2", "phone", "ip", "credit_card", "company"],
    template="Make an SQL insert statement to add a new user to our database. Name is {name}. Email is {email1} "
    "but also possible to contact him with {email2} email. Phone number is {phone} and "
    "the IP address is {ip}. And credit card number is {credit_card}. "
    "He works in {company}.",
)

vault = Vault()
chain = LLMGuardChain(
    prompt=prompt,
    llm=llm,
    input_scanners=[Anonymize(vault), Toxicity(), TokenLimit(), Jailbreak(), PromptInjection()],
    output_scanners=[Deanonymize(vault), NoRefusal(), Relevance(), Sensitive()],
    raise_error=False,
)

# Run the chain only specifying the input variable.
print(
    chain.run(
        name="John Doe",
        email1="test@test.com",
        email2="hello@test.com",
        phone="555-123-4567",
        ip="192.168.1.100",
        credit_card="4567-8901-2345-6789",
        company="Test LLC",
    )
)
