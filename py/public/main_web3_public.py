import nest_asyncio
import asyncio
import logging
from telegram import Bot
from telegram.ext import ApplicationBuilder, ContextTypes
import requests
from web3 import Web3

nest_asyncio.apply()

# 로깅 설정
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot API token과 그룹 Chat ID
API_TOKEN = 'YOUR_BOT_API_TOKEN'
GROUP_CHAT_ID = "CHAT_ID"  # 실제로 사용 중인 그룹의 채팅 ID로 대체

# API 엔드포인트
API_URL = 'YOUR_API_URL'

# Web3 설정
WEB3_PROVIDER_URI = 'https://bartio.rpc.berachain.com' #예시
YOUR_WALLET_ADDRESS = 'WALLET_ADDRESS'
YOUR_PRIVATE_KEY = 'PRIVATE_KEY'

# Web3 초기화
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

# 스마트 컨트랙트 정보(예: ERC20 토큰 전송)
CONTRACT_ADDRESS = 'CONTRACT_ADDRESS'
CONTRACT_ABI = [
    
]

# ERC20 토큰 설정 - 토큰 컨트랙트 주소
TOKEN_ADDRESSES = {
    'DAI': '0x806Ef538b228844c73E8E692ADCFa8Eb2fCF729c',
    'HONEY': '0x0E4aaF1351de4c0264C5c7056Ef3777b41BD8e03' #예시
}
ERC20_ABI = [ #ERC20 토큰 공통 ABI
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

def fetch_result():
    """API에서 result 값을 가져오는 함수"""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # 요청 실패 시 예외 발생
        data = response.json()  # JSON 응답을 파이썬 객체로 변환
        return data['result']  # 'result' 필드의 값을 반환
    except requests.RequestException as e:
        logger.error(f"API 요청 중 에러 발생: {e}")
        return None

def interact_with_contract():
    """스마트 계약의 redeem 함수와 상호작용하는 함수"""
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
    # redeem 함수의 파라미터 설정
    asset_address = '0x806Ef538b228844c73E8E692ADCFa8Eb2fCF729c' #DAI
    amount = int(int(fetch_result())-int(10000000000000000))   # 예시 값, 실제 파라미터 값으로 교체
    receiver_address = '0x42742954F391a2FdAc26340f32eC18b1BD019C68'
    
    nonce = web3.eth.get_transaction_count(YOUR_WALLET_ADDRESS)
    gas_price = web3.eth.gas_price
    
    transaction = contract.functions.redeem(asset_address, amount, receiver_address).build_transaction({
        'chainId': 80084,
        'gas': 200000,
        'gasPrice': gas_price,
        'nonce': nonce
    })

    # 트랜잭션 서명
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=YOUR_PRIVATE_KEY)
    
    # 트랜잭션 전송
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    return web3.to_hex(tx_hash)  # 트랜잭션 해시 반환

async def repeat_message(context: ContextTypes.DEFAULT_TYPE):
    """API에서 받은 status 값을 그룹에 반복해서 보내는 함수"""
    status = round(int(fetch_result())*(0.000000000000000001), 2)
    if status is not None:
        message = f"Current DAI Vault Balance: {status}"  # 전송할 메시지
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
        
        # 특정 조건을 만족할 경우 트랜잭션 전송
        if status >= 1:  # 여기에 실제 트리거 조건을 설정하세요
            tx_hash = interact_with_contract()
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Contract interaction completed! Transaction Hash: {tx_hash}")

            # 확인 후 텔레그램 메시지 전송
            balance_message = "Your Account Balance:"
    
            # BERA (네이티브 토큰) 잔액 조회
            bera_balance = get_native_token_balance(YOUR_WALLET_ADDRESS)
            balance_message += f"\nBERA : {web3.from_wei(bera_balance, 'ether')}"
    
            # 다른 ERC20 토큰 잔액 조회
            for token in TOKEN_ADDRESSES:
                token_balance = get_token_balance(token, YOUR_WALLET_ADDRESS)
                formatted_balance = web3.from_wei(token_balance, 'ether')
                balance_message += f"\n{token} : {formatted_balance}"
    
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=balance_message)
    else:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="Failed to retrieve the status.")

def get_token_balance(token_name, address):
    """ERC20 토큰의 잔고를 조회"""
    token_contract = web3.eth.contract(address=TOKEN_ADDRESSES[token_name], abi=ERC20_ABI)
    balance = token_contract.functions.balanceOf(address).call()
    return balance

def get_native_token_balance(address):
    """네이티브 토큰의 잔고를 조회"""
    balance = web3.eth.get_balance(address)
    return balance

async def main():
    application = ApplicationBuilder().token(API_TOKEN).build()
    job_queue = application.job_queue
    job_queue.run_repeating(callback=repeat_message, interval=3, first=1)
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
