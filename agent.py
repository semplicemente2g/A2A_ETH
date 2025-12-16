import random
import os
from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.example_tool import ExampleTool
from google.genai import types

from .tools.blockchain_verifier import is_agent_trusted

def roll_die(sides: int) -> int:
  """Roll a die and return the rolled result."""
  return random.randint(1, sides)

roll_agent = Agent(
    name="roll_agent",
    description="Handles rolling dice of different sizes.",
    instruction="""
      You are responsible for rolling dice based on the user's request.
      When asked to roll a die, you must call the roll_die tool with the number of sides as an integer.
    """,
    tools=[roll_die],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)

example_tool = ExampleTool([
    {
        "input": {
            "role": "user",
            "parts": [{"text": "Roll a 6-sided die."}],
        },
        "output": [
            {"role": "model", "parts": [{"text": "I rolled a 4 for you."}]}
        ],
    },
    {
        "input": {
            "role": "user",
            "parts": [{"text": "Is 7 a prime number?"}],
        },
        "output": [{
            "role": "model",
            "parts": [{"text": "Yes, 7 is a prime number."}],
        }],
    },
    {
        "input": {
            "role": "user",
            "parts": [{"text": "Roll a 10-sided die and check if it's prime."}],
        },
        "output": [
            {
                "role": "model",
                "parts": [{"text": "I rolled an 8 for you."}],
            },
            {
                "role": "model",
                "parts": [{"text": "8 is not a prime number."}],
            },
        ],
    },
])

prime_agent = RemoteA2aAgent(
    name="prime_agent",
    description="Agent that handles checking if numbers are prime.",
    agent_card=(
        f"http://localhost:8001/a2a/check_prime_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

def verify_prime_agent_tool() -> str:
    eth_addr = os.environ.get("AGENT_PRIME_ETH_ADDRESS")
    if not eth_addr:
        return "AGENT_PRIME_ETH_ADDRESS non è impostato; non posso verificare l'agent."
    try:
        trusted = is_agent_trusted(eth_addr)
        return "TRUSTED" if trusted else "UNTRUSTED"
    except Exception as e:
        return f"ERROR: {e}"

root_agent = Agent(
    model="gemini-flash-latest",
    name="root_agent",
    instruction="""
      You are a helpful assistant that can roll dice and check if numbers are prime.
      IMPORTANT: Before delegating to the remote prime_agent, you MUST call the verify_prime_agent_tool.
      - If the tool returns "TRUSTED", proceed to call the prime_agent.
      - If the tool returns "UNTRUSTED", inform the user you cannot contact the remote agent.
      - If the tool returns an error or any other message, abort and inform the user.
      Follow these steps:
      1. If the user asks to roll a die, delegate to the roll_agent (call the roll_die tool).
      2. If the user asks to check primes, call verify_prime_agent_tool first, then (only if TRUSTED) delegate to prime_agent.
      3. If the user asks to roll a die and then check if the result is prime, call roll_agent first, then call verify_prime_agent_tool and (if TRUSTED) pass the rolled number to prime_agent.
      Always clarify the results before proceeding.
    """,
    global_instruction=(
        "You are DicePrimeBot, ready to roll dice and check prime numbers. Remember to verify any remote agent on-chain before delegating."
    ),
    sub_agents=[roll_agent, prime_agent],
    tools=[example_tool, verify_prime_agent_tool],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
