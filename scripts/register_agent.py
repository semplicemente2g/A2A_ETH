import os
import json
import sys
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACT_INFO_PATH = os.path.join(BASE_DIR, "contracts", "contract_info.json")

def load_contract_info():
    if os.path.exists(CONTRACT_INFO_PATH):
        with open(CONTRACT_INFO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    print(f"ERRORE: Non trovo il file {CONTRACT_INFO_PATH}")
    return None

def main():
    INFURA_URL = os.environ.get("INFURA_URL")
    DEPLOYER_PRIVATE_KEY = os.environ.get("DEPLOYER_PRIVATE_KEY")
    AGENT_ADDRESS = os.environ.get("AGENT_PRIME_ETH_ADDRESS")
    CHAIN_ID = int(os.environ.get("CHAIN_ID", "11155111"))

    if not (INFURA_URL and DEPLOYER_PRIVATE_KEY and AGENT_ADDRESS):
        print("ERRORE: Variabili d'ambiente mancanti nel file .env")
        print(f"- INFURA_URL: {'OK' if INFURA_URL else 'MANCANTE'}")
        print(f"- DEPLOYER_PRIVATE_KEY: {'OK' if DEPLOYER_PRIVATE_KEY else 'MANCANTE'}")
        print(f"- AGENT_PRIME_ETH_ADDRESS: {'OK' if AGENT_ADDRESS else 'MANCANTE'}")
        sys.exit(1)

    info = load_contract_info()
    if not info:
        print(f"- Manca contracts/contract_info.json; esegui prima deploy_registry.py")
        sys.exit(1)

    abi = info["abi"]
    contract_addr = info["address"]

    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
    if not w3.is_connected():
        print("ERRORE: Impossibile connettersi a Infura.")
        sys.exit(1)

    account = w3.eth.account.from_key(DEPLOYER_PRIVATE_KEY)
    deployer_address = account.address

    print(f"Deployer Account: {deployer_address}")
    print(f"Contract Address: {contract_addr}")
    print(f"Address da registrare: {AGENT_ADDRESS}")

    contract = w3.eth.contract(address=contract_addr, abi=abi)

    nonce = w3.eth.get_transaction_count(deployer_address)

    print("Invio transazione di registrazione...")

    tx_data = contract.functions.registerAgent(Web3.to_checksum_address(AGENT_ADDRESS)).build_transaction({
        "from": deployer_address,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
        "chainId": CHAIN_ID,
    })

    signed = account.sign_transaction(tx_data)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    print(f"Tx inviata! Hash: {tx_hash.hex()}")
    print("In attesa di conferma sul blocco...")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status == 1:
        print(f"SUCCESSO! Agent {AGENT_ADDRESS} è ora TRUSTED on-chain.")
    else:
        print("ERRORE: Transazione fallita (reverted).")

if __name__ == "__main__":
    main()
