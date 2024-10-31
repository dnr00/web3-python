import nest_asyncio
import asyncio 
from web3 import Web3
from datetime import datetime
from telegram import Bot
import logging
from typing import Optional
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

# Berachain RPC URL (예시)
RPC_URL = 'https://bera-testnet.nodeinfra.com'
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# 텔레그램 봇 토큰과 채팅 ID
API_TOKEN = os.getenv('UKSANG_SEVENTH_BOT_API_TOKEN')
GROUP_CHAT_ID = os.getenv('UKSANG_OWN_VAULT_BOT_CHAT_ID')

# 사용자 지갑 주소
MY_ADDRESS = "0x42742954F391a2FdAc26340f32eC18b1BD019C68"

# Vault와 LP 토큰 컨트랙트 주소
VAULTS = {
    "BEX HONEY-USDC": "0xe3b9B72ba027FD6c514C0e5BA075Ac9c77C23Afa",
    "BEX HONEY-WBERA": "0xAD57d7d39a487C04a44D3522b910421888Fb9C6d",
    "KODIAK HONEY-USDC": "0xe5519D97eA854291c35a494b28929fA7abEf12e8",
    "KODIAK iBGT-WBERA": "0x7b15eeC57C60f8B68dF2b143c2CA5a772E787e86",
    "KODIAK YEET-WBERA": "0x175e2429bCb92643255abCbCDF47Fff63F7990CC",
    "KODIAK NECT-HONEY": "0x5693809338Ae09481B5Da3A916d1cD1193F1B99A",
    "HONEYPOT WBERA-tHPOT": "0x12F45203b4dF96106fb18d557EE3224A4dC65637"
}

LP_TOKENS = {
    "BEX HONEY-USDC": "0xD69ADb6FB5fD6D06E6ceEc5405D95A37F96E3b96",
    "BEX HONEY-WBERA": "0xd28d852cbcc68DCEC922f6d5C7a8185dBaa104B7",
    "KODIAK HONEY-USDC": "0xb73deE52F38539bA854979eab6342A60dD4C8c03",
    "KODIAK iBGT-WBERA": "0x7fd165B73775884a38AA8f2B384A53A3Ca7400E6",
    "KODIAK YEET-WBERA": "0xE5A2ab5D2fb268E5fF43A5564e44c3309609aFF9",
    "KODIAK NECT-HONEY": "0x63b0EdC427664D4330F72eEc890A86b3F98ce225",
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

previous_data = {}

# 재시도 관련 상수 추가
MAX_RETRIES = 3
RETRY_DELAY = 5  # 재시도 전 대기 시간(초)

async def check_vault_ratios(bot: Bot) -> Optional[bool]:
    global previous_data
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            current_data = {}
            message = f"Vault Ratios and Earned Tokens (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n\n"
            significant_changes = []
            logger.info("Starting vault ratio check")
            
            for name, vault_address in VAULTS.items():
                logger.info(f"Checking vault: {name}")
                try:
                    vault_contract = w3.eth.contract(address=vault_address, abi=ABI)
                    lp_token_contract = w3.eth.contract(address=LP_TOKENS[name], abi=ABI)
                    
                    user_balance = vault_contract.functions.balanceOf(MY_ADDRESS).call()
                    user_balance_ether = w3.from_wei(user_balance, 'ether')
                    
                    if user_balance > 1:
                        total_lp = lp_token_contract.functions.balanceOf(vault_address).call()
                        ratio = (user_balance / total_lp) * 100
                        earned_tokens = vault_contract.functions.earned(MY_ADDRESS).call()
                        earned_tokens_ether = w3.from_wei(earned_tokens, 'ether')
                        
                        message += f"{name}:\n"
                        message += f" LP Token: {user_balance_ether:.6f} (Ratio: {ratio:.2f}%)\n"
                        message += f" Earned: {earned_tokens_ether:.6f} BGT\n\n"
                        
                        current_data[name] = ratio
                        
                        if name in previous_data:
                            diff = abs(ratio - previous_data[name])
                            if diff >= 1:
                                change_msg = f"{name}: {previous_data[name]:.2f}% -> {ratio:.2f}% (Δ{diff:.2f}%)"
                                significant_changes.append(change_msg)
                                
                except Exception as e:
                    logger.error(f"Error checking {name}: {str(e)}")
                    continue  # 개별 vault 체크 실패 시 다음으로 진행
            
            await bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
            
            if significant_changes:
                change_message = "Significant ratio changes (≥1%):\n" + "\n".join(significant_changes)
                await bot.send_message(chat_id=GROUP_CHAT_ID, text=change_message)
            
            previous_data = current_data
            return True
            
        except Exception as e:
            retries += 1
            logger.error(f"Attempt {retries} failed: {str(e)}")
            if retries < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                logger.error("Max retries reached. Moving to next cycle.")
                await bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=f"Failed to check vaults after {MAX_RETRIES} attempts. Error: {str(e)}"
                )
                return False

async def main() -> None:
    bot = Bot(token=API_TOKEN)
    logger.info("Bot initialized")
    
    while True:
        try:
            logger.info("Starting check cycle")
            success = await check_vault_ratios(bot)
            
            if success:
                logger.info("Check cycle completed successfully")
            else:
                logger.warning("Check cycle completed with errors")
                
        except Exception as e:
            logger.error(f"Critical error in main loop: {str(e)}")
            try:
                await bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=f"Critical error occurred: {str(e)}"
                )
            except:
                logger.error("Failed to send error message to Telegram")
        
        logger.info("Waiting for next cycle")
        await asyncio.sleep(60)  # 1분 대기

if __name__ == "__main__":
    logger.info("Script started")
    asyncio.run(main())