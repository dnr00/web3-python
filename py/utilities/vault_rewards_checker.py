import nest_asyncio
from web3 import Web3
from datetime import datetime
from telegram import Bot
import logging
nest_asyncio.apply()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Berachain RPC URL (예시)
RPC_URL = 'https://bera-testnet.nodeinfra.com'
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# 사용자 지갑 주소
MY_ADDRESS = "0x42742954F391a2FdAc26340f32eC18b1BD019C68"

# Vault와 LP 토큰 컨트랙트 주소
VAULTS = {
    "BEX HONEY-USDC": "0xe3b9B72ba027FD6c514C0e5BA075Ac9c77C23Afa",
    "BEX HONEY-WBERA": "0xAD57d7d39a487C04a44D3522b910421888Fb9C6d",
    "BEX PAW-HONEY": "0x1992b26E2617928966B4F8e8eeCF41C6e7A77010",
    "BEND VDHONEY": "0x2E8410239bB4b099EE2d5683e3EF9d6f04E321CC",
    "KODIAK HONEY-USDC": "0xe5519D97eA854291c35a494b28929fA7abEf12e8",
    "KODIAK iBGT-WBERA": "0x7b15eeC57C60f8B68dF2b143c2CA5a772E787e86",
    "KODIAK YEET-WBERA": "0x175e2429bCb92643255abCbCDF47Fff63F7990CC",
    "KODIAK NECT-HONEY": "0x5693809338Ae09481B5Da3A916d1cD1193F1B99A",
    "HONEYPOT WBERA-tHPOT": "0x12F45203b4dF96106fb18d557EE3224A4dC65637",
    "ZERU HONEY-ZERU-LP": "0x016044304A7e7Df23630D4B5796176097C6bd409"
}

LP_TOKENS = {
    "BEX HONEY-USDC": "0xD69ADb6FB5fD6D06E6ceEc5405D95A37F96E3b96",
    "BEX HONEY-WBERA": "0xd28d852cbcc68DCEC922f6d5C7a8185dBaa104B7",
    "BEX PAW-HONEY": "0xa51afAF359d044F8e56fE74B9575f23142cD4B76",
    "BEND VDHONEY": "0x1339503343be5626B40Ee3Aee12a4DF50Aa4C0B9",
    "KODIAK HONEY-USDC": "0xb73deE52F38539bA854979eab6342A60dD4C8c03",
    "KODIAK iBGT-WBERA": "0x7fd165B73775884a38AA8f2B384A53A3Ca7400E6",
    "KODIAK YEET-WBERA": "0xE5A2ab5D2fb268E5fF43A5564e44c3309609aFF9",
    "KODIAK NECT-HONEY": "0x63b0EdC427664D4330F72eEc890A86b3F98ce225",
    "HONEYPOT WBERA-tHPOT": "0x28feC64EaBc1e4Af7f5cD33d2bd20b01D5E8f203",
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
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

def check_vault_ratios():
    message = f"LP Token in Vault (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n\n"

    for name, vault_address in VAULTS.items():
        try:
            vault_contract = w3.eth.contract(address=vault_address, abi=ABI)
            lp_token_contract = w3.eth.contract(address=LP_TOKENS[name], abi=ABI)
            
            total_supply = lp_token_contract.functions.totalSupply().call()
            vault_balance = lp_token_contract.functions.balanceOf(vault_address).call()
            
            total_supply_ether = w3.from_wei(total_supply, 'ether')
            vault_balance_ether = w3.from_wei(vault_balance, 'ether')
            
            ratio = (vault_balance / total_supply) * 100
            
            message += f"{name}: {vault_balance_ether:.6f}/{total_supply_ether:.6f} ({ratio:.2f}%)\n"
            
        except Exception as e:
            message += f"Error checking {name}: {str(e)}\n"

    return message

if __name__ == "__main__":
    result = check_vault_ratios()
    print(result)