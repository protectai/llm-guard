import boto3

from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import Anonymize, PromptInjection, TokenLimit, Toxicity
from llm_guard.output_scanners import Deanonymize, NoRefusal, Relevance, Sensitive
from llm_guard.vault import Vault

# Specify the AWS region, Bedrock agent ID, alias ID, and session ID
region = ""
agent_id = ""
agent_alias_id = ""
session_id = ""


def invoke_agent(sanitized_prompt, region, agent_id, agent_alias_id, session_id):
    """
    Invokes the Bedrock agent with the provided parameters.

    Args:
        sanitized_prompt (str): The sanitized prompt to send to the agent.
        region (str): The AWS region where the agent is located.
        agent_id (str): The ID of the Bedrock agent.
        agent_alias_id (str): The alias ID of the Bedrock agent.
        session_id (str): The session ID for the agent invocation.

    Returns:
        str: The agent's response.
    """
    # Create a Bedrock Agent Runtime client
    bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=region)

    # Invoke the agent
    response = bedrock_agent_runtime.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId=session_id,
        inputText=prompt,
    )

    # Process the agent's response
    completion = ""
    for event in response.get("completion"):
        chunk = event["chunk"]
        completion += chunk["bytes"].decode()

    return completion


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

import boto3

from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import Anonymize, PromptInjection, TokenLimit, Toxicity
from llm_guard.output_scanners import Deanonymize, NoRefusal, Relevance, Sensitive
from llm_guard.vault import Vault

# Specify the AWS region, Bedrock agent ID, alias ID, and session ID
region = ""
agent_id = ""
agent_alias_id = ""
session_id = ""


def invoke_agent(sanitized_prompt, region, agent_id, agent_alias_id, session_id):
    """
    Invokes the Bedrock agent with the provided parameters.

    Args:
        sanitized_prompt (str): The sanitized prompt to send to the agent.
        region (str): The AWS region where the agent is located.
        agent_id (str): The ID of the Bedrock agent.
        agent_alias_id (str): The alias ID of the Bedrock agent.
        session_id (str): The session ID for the agent invocation.

    Returns:
        str: The agent's response.
    """
    # Create a Bedrock Agent Runtime client
    bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=region)

    # Invoke the agent
    response = bedrock_agent_runtime.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId=session_id,
        inputText=prompt,
    )

    # Process the agent's response
    completion = ""
    for event in response.get("completion"):
        chunk = event["chunk"]
        completion += chunk["bytes"].decode()

    return completion


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

response_text = invoke_agent(sanitized_prompt, region, agent_id, agent_alias_id, session_id)
sanitized_response_text, results_valid, results_score = scan_output(
    output_scanners, sanitized_prompt, response_text
)
if any(results_valid.values()) is False:
    print(f"Output {response_text} is not valid, scores: {results_score}")
    exit(1)

print(f"Output: {sanitized_response_text}\n")

sanitized_response_text, results_valid, results_score = scan_output(
    output_scanners, sanitized_prompt, response_text
)
if any(results_valid.values()) is False:
    print(f"Output {response_text} is not valid, scores: {results_score}")
    exit(1)

print(f"Output: {sanitized_response_text}\n")
