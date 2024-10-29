import nest_asyncio
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
import telegram
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler, CommandHandler
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()
nest_asyncio.apply()

# Web3 초기화
WEB3_PROVIDER_URI = 'https://bera-testnet.nodeinfra.com'  
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

# Web3 설정
MY_PRIVATE_KEY = os.getenv('MAIN_ACCOUNT')
account = web3.eth.account.from_key(MY_PRIVATE_KEY)
MY_WALLET_ADDRESS = account.address

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram Bot API 토큰과 그룹 채팅 ID
API_TOKEN = 'TG_API_TOKEN'
GROUP_CHAT_ID = 'GROUP_CHAT_ID'

# 컨트랙트 관련 설정
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

# ERC 20 토큰 관련 설정
TOKEN_ADDRESSES = {
    'WBTC': '0x286F1C3f0323dB9c91D1E8f45c8DF2d065AB5fae',
    'WETH': '0x6E1E9896e93F7A71ECB33d4386b49DeeD67a231A',
    'HONEY': '0x0E4aaF1351de4c0264C5c7056Ef3777b41BD8e03',
    'USDT' : '0x05D0dD5135E3eF3aDE32a9eF9Cb06e8D37A6795D'
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
swap_steps_weth = [{
    "poolIdx": 36001,
    "base": "0x0E4aaF1351de4c0264C5c7056Ef3777b41BD8e03",
    "quote": "0x6E1E9896e93F7A71ECB33d4386b49DeeD67a231A",
    "isBuy": True
}]

swap_steps_wbtc = [{
    "poolIdx": 36001,
    "base": "0x0E4aaF1351de4c0264C5c7056Ef3777b41BD8e03",
    "quote": "0x286F1C3f0323dB9c91D1E8f45c8DF2d065AB5fae",
    "isBuy": True
}]

amount = 10000000000000000000
min_out = 0


def perform_multi_swap_eth():
    """HONEY -> WETH 트랜잭션을 수행"""
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    nonce = web3.eth.get_transaction_count(MY_WALLET_ADDRESS)
    gas_price = web3.eth.gas_price

    transaction = contract.functions.multiSwap(swap_steps_weth, amount, min_out).build_transaction({
        'chainId': 80084,
        'gas': 700000,
        'gasPrice': gas_price,
        'nonce': nonce  
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=MY_PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction) # 로컬 환경에서는(아마 라이브러리 버전 문제) rawTransaction으로 수정
    return web3.to_hex(tx_hash)

def perform_multi_swap_btc():
    """HONEY -> WBTC  트랜잭션을 수행"""
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    nonce = web3.eth.get_transaction_count(MY_WALLET_ADDRESS)
    gas_price = web3.eth.gas_price

    transaction = contract.functions.multiSwap(swap_steps_wbtc, amount, min_out).build_transaction({
        'chainId': 80084,
        'gas': 700000,
        'gasPrice': gas_price,
        'nonce': nonce  
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=MY_PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction) # 로컬 환경에서는(아마 라이브러리 버전 문제) rawTransaction으로 수정
    return web3.to_hex(tx_hash)
 
def get_balance(token_address):
    token_contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)
    balance = token_contract.functions.balanceOf(MY_WALLET_ADDRESS).call()
    return web3.from_wei(balance, 'ether')

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE, modify_message=False):
    image_url = "https://media.tenor.com/oCaXNd6MwUEAAAAe/berachain.png"  # URL 사용 시
    keyboard = [
        [InlineKeyboardButton("HONEY -> BTC", callback_data='swap_btc')],
        [InlineKeyboardButton("HONEY -> ETH", callback_data='swap_eth')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = (f"하나 고르쇼")
    
    if modify_message and update.callback_query:
        try:
            await update.callback_query.message.edit_caption(caption=message_text, reply_markup=reply_markup)
        except telegram.error.BadRequest:
            await update.callback_query.message.edit_media(
                media=InputFile(media=image_url, caption=message_text),
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_photo(photo=image_url, caption=message_text, reply_markup=reply_markup)

async def edit_message_safely(query, caption, reply_markup):
    try:
        if query.message.caption != caption or query.message.reply_markup != reply_markup:
            await query.edit_message_caption(caption=caption, reply_markup=reply_markup)
    except telegram.error.BadRequest as e:
        if str(e) != 'Message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message':
            raise

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action = query.data
    
    keyboard = [[InlineKeyboardButton("처음으로", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if action == 'swap_btc':
            tx_hash = perform_multi_swap_btc()
            balance = get_balance(TOKEN_ADDRESSES['WBTC'])
            result_message = f"성공적으로 전송했다곰! 트랜잭션 해시: {tx_hash}\n변화된 WBTC 잔액: {balance*(10**10)} WBTC"
        elif action == 'swap_eth':
            tx_hash = perform_multi_swap_eth()
            balance = get_balance(TOKEN_ADDRESSES['WETH'])
            result_message = f"성공적으로 전송했다곰! 트랜잭션 해시: {tx_hash}\n변화된 WETH 잔액: {balance} WETH"
        elif action == 'start':
            # '처음으로' 버튼을 클릭했을 때 처리할 로직
            await handle_start(update, context, modify_message=True)
            return  # 'start' 액션을 처리한 후 나머지 코드를 건너뛰기 위해 return
        else:
            result_message = "잘못된 액션입니다."
    except Exception as e:
        result_message = f"트랜잭션 에러: {str(e)}"
    
    await edit_message_safely(query, result_message, reply_markup)

    if action == 'start':
        await handle_start(update, context, modify_message=True)
        
async def main() -> None:
    application = ApplicationBuilder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    await application.run_polling()
    

if __name__ == '__main__':
    asyncio.run(main())