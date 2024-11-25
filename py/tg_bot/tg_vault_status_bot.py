import nest_asyncio
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from web3 import Web3
from dotenv import load_dotenv
import os
from datetime import datetime

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
    "BEX PAW-HONEY": "0x1992b26E2617928966B4F8e8eeCF41C6e7A77010",
    "BEX HONEY-BLAU": "0x96aD477c75Df40717228B203be2b3A47E39B50BD",
    "BEND VDHONEY": "0x2E8410239bB4b099EE2d5683e3EF9d6f04E321CC",
    "KODIAK HONEY-USDC": "0xe5519D97eA854291c35a494b28929fA7abEf12e8",
    "KODIAK iBGT-WBERA": "0x7b15eeC57C60f8B68dF2b143c2CA5a772E787e86",
    "KODIAK YEET-WBERA": "0x175e2429bCb92643255abCbCDF47Fff63F7990CC",
    "KODIAK NECT-HONEY": "0x5693809338Ae09481B5Da3A916d1cD1193F1B99A",
    "KODIAK uniBTC-WBTC": "0xEF55f90b05f719a2760A70cB1462Ff00B90E28C1",
    "HONEYPOT WBERA-tHPOT": "0x12F45203b4dF96106fb18d557EE3224A4dC65637",
    "JUNKY juJNKY": "0x6582414E830d91C8016C10ceD72157106F908145",
    "TerpLayer tTERP": "0xC4f202b367FCB32F16305bd445E6AB4b445cb738",
    "Berally BRLY-ST": "0x6F2f268B8D7A47FFa5e40177A353e3fC2cfe10C8",
    "NOME STABLE-LP": "0xac9ca566459709931Bc869B43364b7445eaa4696",
    "Burrbear HONEY-USDC-NECT": "0x3f4fe6723AfbB97C9Cc51e08A5d266A96f631a9D",
    "Burrbear LBGT-WBERA": "0x7a6b92457e7D7e7a5C1A2245488b850B7Da8E01D",
    "Beraborrow sNECT": "0x72e222116fC6063f4eE5cA90A6C59916AAD8352a",
    "WeBera wbHONEY": "0x86DA232f6A4d146151755Ccf3e4555eadCc24cCF",
    "ZERU HONEY-ZERU-LP": "0x016044304A7e7Df23630D4B5796176097C6bd409"
}

LP_TOKENS = {
    "BEX HONEY-USDC": "0xD69ADb6FB5fD6D06E6ceEc5405D95A37F96E3b96",
    "BEX HONEY-WBERA": "0xd28d852cbcc68DCEC922f6d5C7a8185dBaa104B7",
    "BEX PAW-HONEY": "0xa51afAF359d044F8e56fE74B9575f23142cD4B76",
    "BEX HONEY-BLAU": "0x7d350B479d56ee8879c1361f478Fb2D6bF3b778b",
    "BEND VDHONEY": "0x1339503343be5626B40Ee3Aee12a4DF50Aa4C0B9",
    "KODIAK HONEY-USDC": "0xb73deE52F38539bA854979eab6342A60dD4C8c03",
    "KODIAK iBGT-WBERA": "0x7fd165B73775884a38AA8f2B384A53A3Ca7400E6",
    "KODIAK YEET-WBERA": "0xE5A2ab5D2fb268E5fF43A5564e44c3309609aFF9",
    "KODIAK NECT-HONEY": "0x63b0EdC427664D4330F72eEc890A86b3F98ce225",
    "KODIAK uniBTC-WBTC": "0xB67D60fc02E0870EdDca24D4fa8eA516c890152b",
    "HONEYPOT WBERA-tHPOT": "0x28feC64EaBc1e4Af7f5cD33d2bd20b01D5E8f203",
    "JUNKY juJNKY": "0xdCeBAf53b18986bdE2aEb400a9acC3341Bb6ce3A",
    "TerpLayer tTERP": "0xb18CEC4160E5310e79AEf0d06a8df223A35599cD",
    "Berally BRLY-ST": "0xE578502Aa99Bc89CD07E70c995e1AF89D5A129d5",
    "NOME STABLE-LP": "0x2405296F156f3E5a65FB967b153FE58bf2C6ECcf",
    "Burrbear HONEY-USDC-NECT": "0xf74a682b45F488DF08a77Dc6aF07364e94e4ED98",
    "Burrbear LBGT-WBERA": "0x6AcBBedEcD914dE8295428B4Ee51626a1908bB12",
    "Beraborrow sNECT": "0x3a7f6f2F27f7794a7820a32313F4a68e36580864",
    "WeBera wbHONEY": "0x556b758AcCe5c4F2E1B57821E2dd797711E790F4",
    "ZERU HONEY-ZERU-LP": "0x7a560f7336D75787F5DD12ea7082fa611c3F5dDB"
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
    message = f"Vault Ratios and Earned Tokens (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n\n"

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