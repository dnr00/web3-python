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
GROUP_CHAT_ID = "YOUR_CHAT_ID"  # 실제로 사용 중인 그룹의 채팅 ID로 대체

# Web3 설정
WEB3_PROVIDER_URI = 'https://bartio.rpc.berachain.com'  
YOUR_WALLET_ADDRESS = 'WALLET_ADDRESS' # 실제 주소로 대체(체크섬 주소 사용하거나 web3.to_checksum_address(address) 사용할 것)
YOUR_PRIVATE_KEY = 'PRIVATE_KEY' #실제 프라이빗 키로 대체. 보안에 유의

# Web3 초기화
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

# 스마트 컨트랙트 정보(예: ERC20 토큰 전송)
CONTRACT_ADDRESS = '0xAd1782b2a7020631249031618fB1Bd09CD926b31'
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

# ERC20 토큰 설정 - 토큰 컨트랙트 주소
TOKEN_ADDRESSES = {
    'DAI': '0x806Ef538b228844c73E8E692ADCFa8Eb2fCF729c',
    'HONEY': '0x0E4aaF1351de4c0264C5c7056Ef3777b41BD8e03'
}

# DAI Vault Contract 주소
DAI_VAULT_CONTRACT_ADDRESS = '0xe8c4e92530F1A9d407891Edd00B335bC6676C68F'

# Honey Redeem Contract
REDEEM_CONTRACT_ADDRESS = '0xAd1782b2a7020631249031618fB1Bd09CD926b31'

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

def interact_with_contract(redeem_contract_balance):
    """스마트 계약의 redeem 함수와 상호작용하는 함수"""
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
    # redeem 함수의 파라미터 설정
    asset_address = '0x806Ef538b228844c73E8E692ADCFa8Eb2fCF729c' #DAI
    amount = int(int(redeem_contract_balance)-int(10000000000000000))   # 예시 값, 실제 파라미터 값으로 교체
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
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    return web3.to_hex(tx_hash)  # 트랜잭션 해시 반환

async def repeat_message(context: ContextTypes.DEFAULT_TYPE):
    """API에서 받은 status 값을 그룹에 반복해서 보내는 함수"""

    dai_vault_contract = web3.eth.contract(address=DAI_VAULT_CONTRACT_ADDRESS, abi=ERC20_ABI)
    redeem_contract_balance = dai_vault_contract.functions.balanceOf(REDEEM_CONTRACT_ADDRESS).call()

    status = web3.from_wei(redeem_contract_balance, 'ether')

    if status is not None:
        message = f"Current DAI Vault Balance: {status}"  # 전송할 메시지
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
        
        # 특정 조건을 만족할 경우 트랜잭션 전송
        if status >= 1:  # 여기에 실제 트리거 조건을 설정하세요
            tx_hash = interact_with_contract(redeem_contract_balance)
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
    job_queue.run_repeating(callback=repeat_message, interval=6, first=1)
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
