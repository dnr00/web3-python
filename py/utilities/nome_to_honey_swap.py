import nest_asyncio
import asyncio
import logging
import os
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()
nest_asyncio.apply()

# Web3 초기화
WEB3_PROVIDER_URI = 'https://bera-testnet.nodeinfra.com'  
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

# Web3 설정
YOUR_PRIVATE_KEY = os.getenv('MAIN_ACCOUNT')
account = web3.eth.account.from_key(YOUR_PRIVATE_KEY)
YOUR_WALLET_ADDRESS = account.address

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 컨트랙트 정보
CONTRACT_ADDRESS = '0x21e2C0AFd058A89FCf7caf3aEA3cB84Ae977B73D'
CONTRACT_ABI = [
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_crocSwapDex",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_crocImpact",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_crocQuery",
        "type": "address"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [],
    "name": "crocSwapDex",
    "outputs": [
      {
        "internalType": "contract CrocSwapDex",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "components": [
          {
            "internalType": "uint256",
            "name": "poolIdx",
            "type": "uint256"
          },
          {
            "internalType": "address",
            "name": "base",
            "type": "address"
          },
          {
            "internalType": "address",
            "name": "quote",
            "type": "address"
          },
          {
            "internalType": "bool",
            "name": "isBuy",
            "type": "bool"
          }
        ],
        "internalType": "struct SwapHelpers.SwapStep[]",
        "name": "_steps",
        "type": "tuple[]"
      },
      {
        "internalType": "uint128",
        "name": "_amount",
        "type": "uint128"
      },
      {
        "internalType": "uint128",
        "name": "_minOut",
        "type": "uint128"
      }
    ],
    "name": "multiSwap",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "out",
        "type": "uint128"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "components": [
          {
            "internalType": "uint256",
            "name": "poolIdx",
            "type": "uint256"
          },
          {
            "internalType": "address",
            "name": "base",
            "type": "address"
          },
          {
            "internalType": "address",
            "name": "quote",
            "type": "address"
          },
          {
            "internalType": "bool",
            "name": "isBuy",
            "type": "bool"
          }
        ],
        "internalType": "struct SwapHelpers.SwapStep[]",
        "name": "_steps",
        "type": "tuple[]"
      },
      {
        "internalType": "uint128",
        "name": "_amount",
        "type": "uint128"
      }
    ],
    "name": "previewMultiSwap",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "out",
        "type": "uint128"
      },
      {
        "internalType": "uint256",
        "name": "predictedQty",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "retire",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "stateMutability": "payable",
    "type": "receive"
  }
]

# 스왑 파라미터 정의
swap_steps = [{
    "poolIdx": 36001,
    "base": "0x0E4aaF1351de4c0264C5c7056Ef3777b41BD8e03",
    "quote": "0x9C1e26C5F666EB99Cce6795Fd0892e50929E242D",
    "isBuy": False
}]

amount = 10*(10**18)
min_out = 12000*(10**18)

def perform_multi_swap():
    """multiSwap 트랜잭션을 수행"""
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    nonce = web3.eth.get_transaction_count(YOUR_WALLET_ADDRESS)
    gas_price = web3.eth.gas_price

    transaction = contract.functions.multiSwap(swap_steps, amount, min_out).build_transaction({
        'chainId': 80084,
        'gas': 700000,
        'gasPrice': gas_price,
        'nonce': nonce,
        'value': 0
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=YOUR_PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
    logging.info(f"Transaction sent. Hash: 0x{tx_hash.hex()}")
        
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
    if tx_receipt['status'] == 1:
        logging.info("Transaction Status: Success")
    else:
        logging.warning("Transaction Status: Fail")

async def main():
    logging.info("Starting the script...")
    perform_multi_swap()
    logging.info("Script execution completed.")

if __name__ == '__main__':
    asyncio.run(main())
