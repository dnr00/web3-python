import nest_asyncio
import asyncio
import logging
import os
from telegram.ext import ApplicationBuilder, ContextTypes
from web3 import Web3
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()
nest_asyncio.apply()

# 로깅 설정
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot API token과 그룹 Chat ID
API_TOKEN = os.getenv('UKSANG_BOT_API_TOKEN')
GROUP_CHAT_ID = '-4559796673'

# Web3 설정
WEB3_PROVIDER_URI = 'https://bera-testnet.nodeinfra.com'
# Web3 초기화
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

YOUR_PRIVATE_KEY = os.getenv('MAIN_ACCOUNT')
account = web3.eth.account.from_key(YOUR_PRIVATE_KEY)
YOUR_WALLET_ADDRESS = account.address

# ERC20 토큰 설정 - 토큰 컨트랙트 주소
TOKEN_ADDRESSES = {
    'NECT': '0xf5AFCF50006944d17226978e594D4D25f4f92B40',
    'HONEY': '0x0E4aaF1351de4c0264C5c7056Ef3777b41BD8e03'
}

# NECT Vault Contract 주소
NECT_REDEEM_VAULT_CONTRACT = '0x246c12D7F176B93e32015015dAB8329977de981B'

# ERC20 ABI
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

async def repeat_message(context: ContextTypes.DEFAULT_TYPE):
    """API에서 받은 status 값을 그룹에 반복해서 보내는 함수"""
    nect_balance = get_token_balance('NECT', NECT_REDEEM_VAULT_CONTRACT)

    status = web3.from_wei(nect_balance, 'ether')
    
    if status is not None:
        message = f"Current NECT Vault Balance: {status}"
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
    else:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="Failed to retrieve the status.")

def get_token_balance(token_name, address):
    """ERC20 토큰의 잔고를 조회"""
    token_contract = web3.eth.contract(address=TOKEN_ADDRESSES[token_name], abi=ERC20_ABI)
    balance = token_contract.functions.balanceOf(address).call()
    return balance

async def main():
    """메인 함수에서 봇 설정 및 실행"""
    application = ApplicationBuilder().token(API_TOKEN).build()

    # JobQueue 사용하여 메시지 전송 반복 작업 등록
    job_queue = application.job_queue
    job_queue.run_repeating(callback=repeat_message, interval=3, first=1)  # 5초마다 실행

    # 봇 실행
    await application.run_polling()

if __name__ == '__main__':
    # Jupyter 환경에서의 실행
    asyncio.run(main())