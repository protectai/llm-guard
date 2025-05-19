"""
Before running the example, make sure the OPENAI_API_KEY environment variable is set by executing `echo $OPENAI_API_KEY`.

If it is not already set, it can be set by using `export OPENAI_API_KEY=YOUR_API_KEY` on Unix/Linux/MacOS systems or `set OPENAI_API_KEY=YOUR_API_KEY` on Windows systems.
"""

import os

from openai import OpenAI

from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import Anonymize, PromptInjection, TokenLimit, Toxicity
from llm_guard.output_scanners import Deanonymize, NoRefusal, Relevance, Sensitive
from llm_guard.vault import Vault

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
vault = Vault()
input_scanners = [Anonymize(vault), Toxicity(), TokenLimit(), PromptInjection()]
output_scanners = [Deanonymize(vault), NoRefusal(), Relevance(), Sensitive()]

prompt = (
    "Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com "
    "but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and "
    "the IP address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. "
    "He works in Test LLC."
)

sanitized_prompt, results_valid, results_score = scan_prompt(input_scanners, prompt)
if any(results_valid.values()) is False:
    print(f"Prompt {prompt} is not valid, scores: {results_score}")
    exit(1)

print(f"Prompt: {sanitized_prompt}")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": sanitized_prompt},
    ],
    temperature=0,
    max_tokens=512,
)
response_text = response.choices[0].message.content
sanitized_response_text, results_valid, results_score = scan_output(
    output_scanners, sanitized_prompt, response_text
)
if not all(results_valid.values()) is True:
    print(f"Output {response_text} is not valid, scores: {results_score}")
    exit(1)

print(f"Output: {sanitized_response_text}\n")
