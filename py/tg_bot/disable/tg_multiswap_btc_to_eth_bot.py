import nest_asyncio
import asyncio
import logging
from telegram.ext import ApplicationBuilder, ContextTypes
from web3 import Web3
from concurrent.futures import ThreadPoolExecutor
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

# Telegram Bot API 토큰과 그룹 채팅 ID
API_TOKEN = 'TG_API_TOKEN'
GROUP_CHAT_ID = 'GROUP_CHAT_ID'

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

# ERC20 토큰 설정 - 토큰 컨트랙트 주소
TOKEN_ADDRESSES = {
    'WETH': '0x6E1E9896e93F7A71ECB33d4386b49DeeD67a231A',
    'WBTC' : '0x286F1C3f0323dB9c91D1E8f45c8DF2d065AB5fae'
}
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

# 스왑 파라미터 정의
swap_steps = [{
    "poolIdx": 36000,
    "base": "0x286F1C3f0323dB9c91D1E8f45c8DF2d065AB5fae",
    "quote": "0x6E1E9896e93F7A71ECB33d4386b49DeeD67a231A",
    "isBuy": True
}]

amount = 1000000
min_out = 0

def perform_multi_swap():
    """multiSwap 트랜잭션을 수행"""
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    nonce = web3.eth.get_transaction_count(YOUR_WALLET_ADDRESS)
    gas_price = web3.eth.gas_price

    
    transaction = contract.functions.multiSwap(swap_steps, amount, min_out).build_transaction({
        'chainId': 80084,
        'gas': 1000000,
        'gasPrice': gas_price,
        'nonce': nonce
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=YOUR_PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction) # 로컬 환경에서는(아마 라이브러리 버전 문제) rawTransaction으로 수정
    return web3.to_hex(tx_hash)
    
async def wait_for_transaction_receipt(web3, tx_hash, timeout=30):
    with ThreadPoolExecutor() as pool:
        return await asyncio.get_event_loop().run_in_executor(pool, 
            web3.eth.wait_for_transaction_receipt, 
            tx_hash, 
            timeout
        )

def get_balance(token_address):
    token_contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)
    balance = token_contract.functions.balanceOf(YOUR_WALLET_ADDRESS).call()
    return web3.from_wei(balance, 'ether')

async def execute_and_report(context: ContextTypes.DEFAULT_TYPE):
    """스왑 트랜잭션을 실행한 후 트랜잭션 정보 보고 및 잔액 변화 보고"""
    tx_hash = perform_multi_swap()
    receipt = await wait_for_transaction_receipt(web3, tx_hash, timeout=30)  # 트랜잭션 영수증 기다림
    
    if receipt and receipt.status == 1:
        final_balance = get_balance(TOKEN_ADDRESSES["WETH"])  # 최종 잔액
        message_text = (f"Contract interaction completed! Transaction Hash: {tx_hash}\n"
                        f"Current Balance: {final_balance} WETH")
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message_text)
    elif receipt and receipt.status == 0:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Transaction failed! Transaction Hash: {tx_hash}")
    else:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="Failed to perform swap transaction or transaction timed out.")

async def main():
    application = ApplicationBuilder().token(API_TOKEN).build()
    job_queue = application.job_queue
    job_queue.run_repeating(callback=execute_and_report, interval=60, first=0)

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
