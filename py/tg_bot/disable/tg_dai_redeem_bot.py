import nest_asyncio
import asyncio
import logging
import os
import json
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
API_TOKEN = 'TG_API_TOKEN'
GROUP_CHAT_ID = 'GROUP_CHAT_ID'

# Web3 설정
WEB3_PROVIDER_URI = 'https://bera-testnet.nodeinfra.com'
# Web3 초기화
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

YOUR_PRIVATE_KEY = os.getenv('MAIN_ACCOUNT')
account = web3.eth.account.from_key(YOUR_PRIVATE_KEY)
YOUR_WALLET_ADDRESS = account.address

# ERC20 토큰 설정 - 토큰 컨트랙트 주소
TOKEN_ADDRESSES = {
    'DAI': '0x806Ef538b228844c73E8E692ADCFa8Eb2fCF729c',
    'HONEY': '0x0E4aaF1351de4c0264C5c7056Ef3777b41BD8e03'
}

# DAI Vault Contract 주소
DAI_VAULT_CONTRACT_ADDRESS = '0xe8c4e92530F1A9d407891Edd00B335bC6676C68F'

# Honey Redeem Contract
REDEEM_CONTRACT_ADDRESS = '0xAd1782b2a7020631249031618fB1Bd09CD926b31'
CONTRACT_ABI = [
  {
    "inputs": [],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "target",
        "type": "address"
      }
    ],
    "name": "AddressEmptyCode",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "asset",
        "type": "address"
      }
    ],
    "name": "AssetNotRegistered",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "implementation",
        "type": "address"
      }
    ],
    "name": "ERC1967InvalidImplementation",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ERC1967NonPayable",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "EnforcedPause",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ExpectedPause",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "FailedInnerCall",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "assets",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "shares",
        "type": "uint256"
      }
    ],
    "name": "InsufficientAssets",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InvalidInitialization",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "expectedOwner",
        "type": "address"
      }
    ],
    "name": "MismatchedOwner",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NotInitializing",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NotVaultAdmin",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "rate",
        "type": "uint256"
      }
    ],
    "name": "OverOneHundredPercentRate",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      }
    ],
    "name": "OwnableInvalidOwner",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "OwnableUnauthorizedAccount",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "x",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "y",
        "type": "uint256"
      }
    ],
    "name": "PRBMath_MulDiv18_Overflow",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "x",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "y",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "denominator",
        "type": "uint256"
      }
    ],
    "name": "PRBMath_MulDiv_Overflow",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "UUPSUnauthorizedCallContext",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "slot",
        "type": "bytes32"
      }
    ],
    "name": "UUPSUnsupportedProxiableUUID",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "caller",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "expectedCaller",
        "type": "address"
      }
    ],
    "name": "UnauthorizedCaller",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "asset",
        "type": "address"
      }
    ],
    "name": "VaultAlreadyRegistered",
    "type": "error"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "feeReceiver",
        "type": "address"
      }
    ],
    "name": "FeeReceiverSet",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "assetAmount",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "mintAmount",
        "type": "uint256"
      }
    ],
    "name": "HoneyMinted",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "assetAmount",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "redeemAmount",
        "type": "uint256"
      }
    ],
    "name": "HoneyRedeemed",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "uint64",
        "name": "version",
        "type": "uint64"
      }
    ],
    "name": "Initialized",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "rate",
        "type": "uint256"
      }
    ],
    "name": "MintRateSet",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "OwnershipTransferred",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "Paused",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "rate",
        "type": "uint256"
      }
    ],
    "name": "RedeemRateSet",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "Unpaused",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "implementation",
        "type": "address"
      }
    ],
    "name": "Upgraded",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "vault",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "asset",
        "type": "address"
      }
    ],
    "name": "VaultCreated",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "UPGRADE_INTERFACE_VERSION",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract ERC20",
        "name": "asset",
        "type": "address"
      }
    ],
    "name": "createVault",
    "outputs": [
      {
        "internalType": "contract ERC4626",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "feeReceiver",
    "outputs": [
      {
        "internalType": "address",
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
        "internalType": "address",
        "name": "asset",
        "type": "address"
      }
    ],
    "name": "getMintRate",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "asset",
        "type": "address"
      }
    ],
    "name": "getRedeemRate",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "honey",
    "outputs": [
      {
        "internalType": "contract Honey",
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
        "internalType": "address",
        "name": "_governance",
        "type": "address"
      },
      {
        "internalType": "contract Honey",
        "name": "_honey",
        "type": "address"
      }
    ],
    "name": "initialize",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      }
    ],
    "name": "mint",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "numRegisteredAssets",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "pause",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract ERC20",
        "name": "asset",
        "type": "address"
      }
    ],
    "name": "pauseVault",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "paused",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "exactAmount",
        "type": "uint256"
      }
    ],
    "name": "previewHoneyToRedeem",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "previewMint",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "honeyAmount",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "honeyAmount",
        "type": "uint256"
      }
    ],
    "name": "previewRedeem",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "exactHoneyAmount",
        "type": "uint256"
      }
    ],
    "name": "previewRequiredCollateral",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "proxiableUUID",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "honeyAmount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      }
    ],
    "name": "redeem",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "name": "registeredAssets",
    "outputs": [
      {
        "internalType": "contract ERC20",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_feeReceiver",
        "type": "address"
      }
    ],
    "name": "setFeeReceiver",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract ERC20",
        "name": "asset",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "mintRate",
        "type": "uint256"
      }
    ],
    "name": "setMintRate",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract ERC20",
        "name": "asset",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "redeemRate",
        "type": "uint256"
      }
    ],
    "name": "setRedeemRate",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "transferOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "unpause",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract ERC20",
        "name": "asset",
        "type": "address"
      }
    ],
    "name": "unpauseVault",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
      },
      {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
      }
    ],
    "name": "upgradeToAndCall",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract ERC4626Vault",
        "name": "vault",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "newVaultImpl",
        "type": "address"
      }
    ],
    "name": "upgradeVault",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract ERC20",
        "name": "asset",
        "type": "address"
      }
    ],
    "name": "vaults",
    "outputs": [
      {
        "internalType": "contract ERC4626",
        "name": "vault",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      }
    ],
    "name": "withdrawAllFee",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract ERC20",
        "name": "asset",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "shares",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      }
    ],
    "name": "withdrawFee",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "assets",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]

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

#초기화 변수
EARNING_FILE = 'todays_earning_dai.json'
DAILY_EARNINGS_FILE = 'daily_earnings_dai.json'
todays_earning = Decimal(0)  # Today's Earning accumulation

def load_todays_earning():
    """파일에서 today's earning을 불러옵니다."""
    global todays_earning
    if os.path.exists(EARNING_FILE):
        try:
            with open(EARNING_FILE, 'r') as f:
                data = json.load(f)
                todays_earning = Decimal(data.get('todays_earning', 0))  # Decimal로 변환
        except (json.JSONDecodeError, ValueError):
            todays_earning = Decimal(0)

def save_todays_earning():
    """파일에 today's earning을 저장합니다."""
    global todays_earning
    with open(EARNING_FILE, 'w') as f:
        json.dump({'todays_earning': float(todays_earning)}, f)

def interact_with_contract(redeem_contract_balance):
    """스마트 계약의 redeem 함수와 상호작용하는 함수"""
    contract = web3.eth.contract(address=REDEEM_CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
    # redeem 함수의 파라미터 설정
    asset_address = TOKEN_ADDRESSES["DAI"] #DAI
    amount = int(redeem_contract_balance)-int(web3.to_wei(0.1, 'ether'))   # 예시 값, 실제 파라미터 값으로 교체
    receiver_address = YOUR_WALLET_ADDRESS
    
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
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction) # 로컬 환경에서는(아마 라이브러리 버전 문제) rawTransaction으로 수정
    
    return web3.to_hex(tx_hash)  # 트랜잭션 해시 반환

async def wait_for_transaction_receipt(web3, tx_hash, timeout=30):
    with ThreadPoolExecutor() as pool:
        return await asyncio.get_event_loop().run_in_executor(pool, 
            web3.eth.wait_for_transaction_receipt, 
            tx_hash, 
            timeout
        )

def ensure_valid_balance(balance_change):
    # 기본값 처리 또는 로그
    if balance_change <= 0 or not isinstance(balance_change, int):
        print("잘못된 잔액 변경 값!")
        return 0  # 또는 적절한 기본 값을 반환
    return balance_change

async def repeat_message(context: ContextTypes.DEFAULT_TYPE):
    """API에서 받은 status 값을 그룹에 반복해서 보내는 함수"""
    global todays_earning
    initial_balance = get_token_balance("DAI", YOUR_WALLET_ADDRESS)
    dai_vault_contract = web3.eth.contract(address=DAI_VAULT_CONTRACT_ADDRESS, abi=ERC20_ABI)
    redeem_contract_balance = dai_vault_contract.functions.balanceOf(REDEEM_CONTRACT_ADDRESS).call()

    status = web3.from_wei(redeem_contract_balance, 'ether')
    
    if status is not None:
        # 특정 조건을 만족할 경우 트랜잭션 전송
        if status >= 1:  
            message = f"Current DAI Vault Balance: {status}" 
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
            
            tx_hash = interact_with_contract(redeem_contract_balance)
            receipt = await wait_for_transaction_receipt(web3, tx_hash, timeout=30)

            if receipt and receipt.status == 1:
                final_balance = get_token_balance("DAI", YOUR_WALLET_ADDRESS)
                balance_change = final_balance - initial_balance
                safe_balance_change = ensure_valid_balance(balance_change)

                if safe_balance_change > 0:
                    readable_balance_change = round(web3.from_wei(balance_change, 'ether'), 2)
                    todays_earning += readable_balance_change  # Today's Earning 누적
                    save_todays_earning()  # 누적 후 저장
                    message_text = (f"Contract interaction completed! Transaction Hash: {tx_hash}\n"
                                    f"Balance change: {readable_balance_change} DAI\n"
                                    f"Total Earning: {round(todays_earning, 2)} DAI\n"
                                    f"Your Account Balance")
                    
                    # BERA (네이티브 토큰) 잔액 조회
                    bera_balance = get_native_token_balance(YOUR_WALLET_ADDRESS)
                    message_text += f"\nBERA : {web3.from_wei(bera_balance, 'ether')}"

                    for token in TOKEN_ADDRESSES:
                      token_balance = get_token_balance(token, YOUR_WALLET_ADDRESS)
                      formatted_balance = web3.from_wei(token_balance, 'ether')
                      message_text += f"\n{token} : {formatted_balance}"
                    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message_text)
                else:
                    message_text = (f"Contract interaction completed! Transaction Hash: {tx_hash}\n"
                                    f"Balance change: 유효한 잔액 변경 없음\n"
                                    f"Total Earning: {round(todays_earning, 2)} DAI\n"
                                    f"Your Account Balance")
                    
                    # BERA (네이티브 토큰) 잔액 조회
                    bera_balance = get_native_token_balance(YOUR_WALLET_ADDRESS)
                    message_text += f"\nBERA : {web3.from_wei(bera_balance, 'ether')}"

                    for token in TOKEN_ADDRESSES:
                      token_balance = get_token_balance(token, YOUR_WALLET_ADDRESS)
                      formatted_balance = web3.from_wei(token_balance, 'ether')
                      message_text += f"\n{token} : {formatted_balance}"
                    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message_text)

            elif receipt and receipt.status == 0:
                await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Transaction failed! Transaction Hash: {tx_hash}")
            else:
                await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="Failed to perform swap transaction or transaction timed out.")        
 
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
    load_todays_earning()
    application = ApplicationBuilder().token(API_TOKEN).build()
    job_queue = application.job_queue
    job_queue.run_repeating(callback=repeat_message, interval=2, first=1)

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
