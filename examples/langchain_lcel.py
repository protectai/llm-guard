from langchain import chat_models, prompts, schema

from llm_guard.input_scanners import Toxicity


class LLMGuardPromptInvalidException(Exception):
    """Exception to raise when llm-guard marks prompt invalid."""


class LLMGuardOutputInvalidException(Exception):
    """Exception to raise when llm-guard marks result invalid."""


def scan_input_toxicity_scanner(params) -> str:
    text = params.get("text", "")
    threshold = float(params.get("threshold", 0.7))
    scanner = Toxicity(threshold)
    sanitized_input, is_valid, risk_score = scanner.scan(text)

    if is_valid:
        return sanitized_input
    else:
        raise LLMGuardPromptInvalidException(
            f"The input text '{text}' was determined as toxic with risk score {risk_score}"
        )


chain = (
    prompts.ChatPromptTemplate.from_template("Reverse the following string: {text}")
    | chat_models.ChatOpenAI()
    | schema.output_parser.StrOutputParser()
)

guard_chain = scan_input_toxicity_scanner | schema.output_parser.StrOutputParser()

overall_chain = {"text": guard_chain} | chain


try:
    input_text = "Hello, world!"
    threshold = 0.0
    output = overall_chain.invoke({"text": input_text, "threshold": threshold})
    print(output)
except LLMGuardPromptInvalidException as e:
    print(f"Prompt invalid: {str(e)}")
except Exception as e:
    print(f"An error occurred: {str(e)}")
