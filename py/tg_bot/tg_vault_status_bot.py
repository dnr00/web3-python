import nest_asyncio
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()
nest_asyncio.apply()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vault_checker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Berachain RPC URL
RPC_URL = 'https://bera-testnet.nodeinfra.com'
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# 텔레그램 봇 토큰
API_TOKEN = os.getenv('UKSANG_VAULT_BOT_API_TOKEN')
CHAT_ID = os.getenv('UKSANG_VAULT_BOT_CHAT_ID')

# Vault와 LP 토큰 컨트랙트 주소
VAULTS = {
    "BEX HONEY-USDC": "0xe3b9B72ba027FD6c514C0e5BA075Ac9c77C23Afa",
    "BEX HONEY-WBERA": "0xAD57d7d39a487C04a44D3522b910421888Fb9C6d",
    "KODIAK HONEY-USDC": "0xe5519D97eA854291c35a494b28929fA7abEf12e8",
    "KODIAK iBGT-WBERA": "0x7b15eeC57C60f8B68dF2b143c2CA5a772E787e86",
    "KODIAK YEET-WBERA": "0x175e2429bCb92643255abCbCDF47Fff63F7990CC",
    "HONEYPOT WBERA-tHPOT": "0x12F45203b4dF96106fb18d557EE3224A4dC65637"
}

LP_TOKENS = {
    "BEX HONEY-USDC": "0xD69ADb6FB5fD6D06E6ceEc5405D95A37F96E3b96",
    "BEX HONEY-WBERA": "0xd28d852cbcc68DCEC922f6d5C7a8185dBaa104B7",
    "KODIAK HONEY-USDC": "0xb73deE52F38539bA854979eab6342A60dD4C8c03",
    "KODIAK iBGT-WBERA": "0x7fd165B73775884a38AA8f2B384A53A3Ca7400E6",
    "KODIAK YEET-WBERA": "0xE5A2ab5D2fb268E5fF43A5564e44c3309609aFF9",
    "HONEYPOT WBERA-tHPOT": "0x28feC64EaBc1e4Af7f5cD33d2bd20b01D5E8f203"
}

# ABI
ABI = [
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "earned",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome! Please send me an Ethereum address to check vault ratios.')

async def check_vault_ratios(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    address = update.message.text.strip()
    if not w3.is_address(address):
        await update.message.reply_text("Invalid Ethereum address. Please try again.")
        return

    address = w3.to_checksum_address(address)
    message = f"Vault Ratios and Earned Tokens for {address}:\n\n"

    for name, vault_address in VAULTS.items():
        try:
            vault_contract = w3.eth.contract(address=vault_address, abi=ABI)
            lp_token_contract = w3.eth.contract(address=LP_TOKENS[name], abi=ABI)
            
            user_balance = vault_contract.functions.balanceOf(address).call()
            user_balance_ether = w3.from_wei(user_balance, 'ether')
            
            if user_balance > 1:
                total_lp = lp_token_contract.functions.balanceOf(vault_address).call()
                ratio = (user_balance / total_lp) * 100
                
                earned_tokens = vault_contract.functions.earned(address).call()
                earned_tokens_ether = w3.from_wei(earned_tokens, 'ether')
                
                message += f"{name}:\n"
                message += f"  LP Token: {user_balance_ether:.6f} (Ratio: {ratio:.2f}%)\n"
                message += f"  Earned: {earned_tokens_ether:.6f} BGT\n\n"
        except Exception as e:
            logger.error(f"Error checking {name}: {str(e)}")
            message += f"Error checking {name}\n"

    await update.message.reply_text(message)

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_vault_ratios))

    application.run_polling()

if __name__ == '__main__':
    main()