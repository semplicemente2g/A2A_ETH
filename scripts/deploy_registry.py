import os
import json
from web3 import Web3
from solcx import compile_source, install_solc
from dotenv import load_dotenv

# versione solc (>=0.8.0)
SOLC_VERSION = "0.8.19"

CONTRACT_PATH = "../contracts/AgentRegistry.sol"
OUTPUT_JSON = "../contracts/contract_info.json"

load_dotenv()  # legge le variabili da .env

def load_source():
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def main():
    INFURA_URL = os.environ.get("INFURA_URL")
    DEPLOYER_PRIVATE_KEY = os.environ.get("DEPLOYER_PRIVATE_KEY")
    CHAIN_ID = int(os.environ.get("CHAIN_ID", "5"))  # default Goerli/testnet
    if not INFURA_URL or not DEPLOYER_PRIVATE_KEY:
        raise SystemExit("Setta INFURA_URL e DEPLOYER_PRIVATE_KEY nelle env vars.")

    install_solc(SOLC_VERSION)
    source = load_source() 

    compiled = compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version=SOLC_VERSION,
    )
    contract_id, contract_interface = compiled.popitem()
    abi = contract_interface["abi"]        
    bytecode = contract_interface["bin"]    

    w3 = Web3(Web3.HTTPProvider(INFURA_URL))                    
    account = w3.eth.account.from_key(DEPLOYER_PRIVATE_KEY)    
    deployer_address = account.address

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(deployer_address)
    construct_txn = Contract.constructor().build_transaction(   
        {
            "from": deployer_address,
            "nonce": nonce,
            "gas": 6000000,
            "gasPrice": w3.eth.gas_price,
            "chainId": CHAIN_ID,
        }
    )

    signed = account.sign_transaction(construct_txn)               
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)  
    print("Deploy tx sent:", tx_hash.hex())
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)         
    print("Contract deployed at:", receipt.contractAddress)         

    info = {"address": receipt.contractAddress, "abi": abi}
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    print("Saved contract info to", OUTPUT_JSON)

if __name__ == "__main__":
    main()