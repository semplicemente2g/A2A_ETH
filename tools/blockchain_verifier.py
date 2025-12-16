import os
import json
from web3 import Web3

CONTRACT_INFO_PATH = os.path.join(os.path.dirname(__file__), "..", "contracts", "contract_info.json")

def load_contract_info():
    path = os.path.abspath(CONTRACT_INFO_PATH)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing contract info at {path}. Run deploy script first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def is_agent_trusted(agent_eth_address: str) -> bool:
    """Ritorna True se l'address è trusted on-chain."""
    INFURA_URL = os.environ.get("INFURA_URL")
    if not INFURA_URL:
        raise RuntimeError("ENV INFURA_URL non settata.")
    info = load_contract_info()
    abi = info["abi"]
    contract_addr = info["address"]

    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
    contract = w3.eth.contract(address=contract_addr, abi=abi)
    try:
        result = contract.functions.isTrusted(Web3.to_checksum_address(agent_eth_address)).call()
        return bool(result)
    except Exception as e:
        print("Error calling contract:", e)
        return False
