import nest_asyncio
import asyncio
from web3 import Web3
from datetime import datetime
from telegram import Bot
import logging
from typing import Optional
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor
from web3.contract import Contract

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

# ThreadPoolExecutor 생성
executor = ThreadPoolExecutor(max_workers=10)

# Berachain RPC URL
RPC_URL = 'https://bera-testnet.nodeinfra.com'
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# 텔레그램 봇 토큰과 채팅 ID
API_TOKEN = os.getenv('UKSANG_VAULT_REWARDS_BOT_API_TOKEN')
GROUP_CHAT_ID = os.getenv('UKSANG_VAULT_REWARDS_BOT_CHAT_ID')

# 사용자 지갑 주소
MY_ADDRESS = "0x42742954F391a2FdAc26340f32eC18b1BD019C68"

# Vault와 LP 토큰 컨트랙트 주소
VAULTS = {
    "BEX HONEY-USDC": "0xe3b9B72ba027FD6c514C0e5BA075Ac9c77C23Afa",
    "BEX HONEY-WBERA": "0xAD57d7d39a487C04a44D3522b910421888Fb9C6d",
    "BEX PAW-HONEY": "0x1992b26E2617928966B4F8e8eeCF41C6e7A77010",
    "BEX HONEY-BLAU": "0x96aD477c75Df40717228B203be2b3A47E39B50BD",
    "BEX HONEY-iBGT": "0xE7CE38A17f36e9eC388dAe35574939e94e176d32",
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
    "ZERU HONEY-ZERU-LP": "0x016044304A7e7Df23630D4B5796176097C6bd409",
    "ZERU zberaHONEY" : "0x3E1FfDD1AD1e4774693CBCCdF9C737De8713D984"
}

LP_TOKENS = {
    "BEX HONEY-USDC": "0xD69ADb6FB5fD6D06E6ceEc5405D95A37F96E3b96",
    "BEX HONEY-WBERA": "0xd28d852cbcc68DCEC922f6d5C7a8185dBaa104B7",
    "BEX PAW-HONEY": "0xa51afAF359d044F8e56fE74B9575f23142cD4B76",
    "BEX HONEY-BLAU": "0x7d350B479d56ee8879c1361f478Fb2D6bF3b778b",
    "BEX HONEY-iBGT": "0xe00611C55ec88266F294D8E7A0bF6E29E5f3C981",
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
    "ZERU HONEY-ZERU-LP": "0x7a560f7336D75787F5DD12ea7082fa611c3F5dDB",
    "ZERU zberaHONEY" : "0x12Afd7A3324B689e32eEa71902DCbA5ED72Ee67E"
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

MAX_RETRIES = 3
RETRY_DELAY = 5

previous_data = {
    'ratios': {},
    'earned': {}
}

VAULT_SPECIFIC_ADDRESSES = {
    "Berally BRLY-ST": "0xEa0182f9FdeC154050C353Fe194A892Da784B396"
}

async def get_vault_info(vault_contract: Contract, lp_contract: Contract, name: str, check_address: str) -> dict:
    try:
        user_balance, earned_tokens = await asyncio.gather(
            asyncio.get_event_loop().run_in_executor(
                executor, 
                vault_contract.functions.balanceOf(check_address).call
            ),
            asyncio.get_event_loop().run_in_executor(
                executor, 
                vault_contract.functions.earned(check_address).call
            )
        )
        
        user_balance = float(user_balance)
        if user_balance > 1:
            total_lp = await asyncio.get_event_loop().run_in_executor(
                executor,
                lp_contract.functions.balanceOf(vault_contract.address).call
            )
            
            ratio = (user_balance / float(total_lp)) * 100
            earned_tokens_ether = float(w3.from_wei(earned_tokens, 'ether'))
            user_balance_ether = float(w3.from_wei(user_balance, 'ether'))
            
            return {
                'name': name,
                'balance': user_balance_ether,
                'ratio': ratio,
                'earned': earned_tokens_ether,
                'valid': True
            }
    except Exception as e:
        logger.error(f"Error checking {name}: {str(e)}")
    
    return {'name': name, 'valid': False}

async def check_vault_ratios(bot: Bot) -> Optional[bool]:
    global previous_data
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            current_data = {'ratios': {}, 'earned': {}}
            
            vault_contracts = {
                name: (
                    w3.eth.contract(address=vault_addr, abi=ABI),
                    w3.eth.contract(address=LP_TOKENS[name], abi=ABI)
                )
                for name, vault_addr in VAULTS.items()
            }
            
            tasks = [
                get_vault_info(
                    vault_contract,
                    lp_contract,
                    name,
                    VAULT_SPECIFIC_ADDRESSES.get(name, MY_ADDRESS)
                )
                for name, (vault_contract, lp_contract) in vault_contracts.items()
            ]
            
            vault_results = await asyncio.gather(*tasks)
            
            vault_data = []
            for result in vault_results:
                if result['valid']:
                    name = result['name']
                    earned_diff = 0
                    estimated_total_reward = 0
                    
                    if name in previous_data['earned']:
                        earned_diff = result['earned'] - previous_data['earned'][name]
                        estimated_total_reward = (earned_diff / (result['ratio']/100)) if result['ratio'] > 0 else 0
                    
                    vault_info = {
                        **result,
                        'earned_diff': earned_diff,
                        'estimated_total_reward': estimated_total_reward
                    }
                    vault_data.append(vault_info)
                    current_data['ratios'][name] = result['ratio']
                    current_data['earned'][name] = result['earned']
            
            vault_data.sort(key=lambda x: x.get('estimated_total_reward', 0), reverse=True)
            
            message = f"Vault Ratios and Earned Tokens (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n\n"
            significant_changes = []
            total_earn = 0
            brly_earn = 0
            
            for vault in vault_data:
                name = vault['name']
                message += f"{name}:\n"
                message += f" LP Token: {vault['balance']:.6f} (Ratio: {vault['ratio']:.2f}%)\n"
                message += f" Earned: {vault['earned']:.6f} BGT"
                if vault['earned_diff'] > 0:
                    message += f"\n 1min Reward: {vault['earned_diff']:.6f} BGT"
                    message += f"\n Estimated Pool 1min Reward: {vault['estimated_total_reward']:.6f} BGT"
                message += "\n\n"
                if vault['name'] == "Berally BRLY-ST":
                    brly_earn += vault['earned_diff']
                else: 
                    total_earn += vault['earned_diff']
                
                if name in previous_data['ratios']:
                    diff = abs(vault['ratio'] - previous_data['ratios'][name])
                    if diff >= 1:
                        change_msg = f"{name}: {previous_data['ratios'][name]:.2f}% -> {vault['ratio']:.2f}% (Δ{diff:.2f}%)"
                        significant_changes.append(change_msg)
            
            message += f"1min Total Reward: {total_earn:.6f} BGT\n"
            message += f"BRLY-ST 1min Reward: {brly_earn:.6f} BGT\n"
            
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