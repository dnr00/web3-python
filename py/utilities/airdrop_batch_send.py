from web3 import Web3
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

RPC_URL = 'https://bera-testnet.nodeinfra.com'

# Web3 설정
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# 컨트랙트 주소와 ABI 설정
contract_address = '0xB68ddDb97384C3775748C72192cA509A0C20e542'
contract_abi = [
  {
    "inputs": [],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "addOwner",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address payable[]",
        "name": "recipients",
        "type": "address[]"
      },
      {
        "internalType": "uint256[]",
        "name": "amounts",
        "type": "uint256[]"
      }
    ],
    "name": "batchTransfer",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract IERC20",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "address[]",
        "name": "recipients",
        "type": "address[]"
      },
      {
        "internalType": "uint256[]",
        "name": "amounts",
        "type": "uint256[]"
      }
    ],
    "name": "batchTransferERC20",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract IERC20",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "depositERC20",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "isOwner",
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
        "name": "",
        "type": "address"
      }
    ],
    "name": "owners",
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
        "name": "ownerToRemove",
        "type": "address"
      }
    ],
    "name": "removeOwner",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "withdraw",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract IERC20",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "withdrawERC20",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
] # 위에서 제공한 ABI

# 컨트랙트 인스턴스 생성
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# ERC20 토큰 주소와 금액 설정
token_address = '0xE6E772E87B65b43cc0820593fA7B61ed308DC094'
erc20_abi = [
  {
    "constant": True,
    "inputs": [],
    "name": "name",
    "outputs": [{"name": "", "type": "string"}],
    "type": "function"
  },
  {
    "constant": True,
    "inputs": [],
    "name": "symbol",
    "outputs": [{"name": "", "type": "string"}],
    "type": "function"
  },
  {
    "constant": True,
    "inputs": [],
    "name": "decimals",
    "outputs": [{"name": "", "type": "uint8"}],
    "type": "function"
  },
  {
    "constant": True,
    "inputs": [],
    "name": "totalSupply",
    "outputs": [{"name": "", "type": "uint256"}],
    "type": "function"
  },
  {
    "constant": True,
    "inputs": [{"name": "_owner", "type": "address"}],
    "name": "balanceOf",
    "outputs": [{"name": "balance", "type": "uint256"}],
    "type": "function"
  },
  {
    "constant": False,
    "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
    "name": "transfer",
    "outputs": [{"name": "success", "type": "bool"}],
    "type": "function"
  },
  {
    "constant": False,
    "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}],
    "name": "approve",
    "outputs": [{"name": "success", "type": "bool"}],
    "type": "function"
  },
  {
    "constant": True,
    "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}],
    "name": "allowance",
    "outputs": [{"name": "remaining", "type": "uint256"}],
    "type": "function"
  },
  {
    "constant": False,
    "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
    "name": "transferFrom",
    "outputs": [{"name": "success", "type": "bool"}],
    "type": "function"
  },
  {
    "inputs": [{"name": "_initialAmount", "type": "uint256"}, {"name": "_tokenName", "type": "string"}, {"name": "_decimalUnits", "type": "uint8"}, {"name": "_tokenSymbol", "type": "string"}],
    "type": "constructor"
  },
  {
    "anonymous": False,
    "inputs": [{"indexed": True, "name": "_from", "type": "address"}, {"indexed": True, "name": "_to", "type": "address"}, {"indexed": False, "name": "_value", "type": "uint256"}],
    "name": "Transfer",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [{"indexed": True, "name": "_owner", "type": "address"}, {"indexed": True, "name": "_spender", "type": "address"}, {"indexed": False, "name": "_value", "type": "uint256"}],
    "name": "Approval",
    "type": "event"
  }
] 
token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)

# 사용자 주소와 개인키
MY_PRIVATE_KEY = os.getenv('MAIN_ACCOUNT')
account = w3.eth.account.from_key(MY_PRIVATE_KEY)
MY_WALLET_ADDRESS = account.address

# apply_accounts.json 파일에서 주소 읽기
def load_addresses():
    with open('apply_accounts.json', 'r') as f:
        data = json.load(f)
    return [account['account'] for account in data]

def batch_transfer_erc20(recipients, amounts):
    nonce = w3.eth.get_transaction_count(MY_WALLET_ADDRESS)
    
    txn = contract.functions.batchTransferERC20(
        token_address,
        recipients,
        amounts
    ).build_transaction({
        'from': MY_WALLET_ADDRESS,
        'nonce': nonce,
        'gas': 20000000,  # 가스 한도 조정 필요할 수 있음
        'gasPrice': int(1.4*w3.eth.gas_price)
    })
    
    signed_txn = w3.eth.account.sign_transaction(txn, MY_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def main():
    all_recipients = load_addresses()
    amount_per_recipient = w3.to_wei(2500, 'ether')  # 500 토큰, 소수점 18자리 가정
    
    batch_size = 500
    wait_time = 1

    for i in range(0, len(all_recipients), batch_size):
        batch_recipients = all_recipients[i:i+batch_size]
        
        # 첫 다섯 계정의 토큰 잔고 확인
        check_accounts = batch_recipients[:5]
        token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)  # ERC20 토큰의 ABI 필요
        should_skip_batch = all(token_contract.functions.balanceOf(account).call() > w3.to_wei(100, 'ether') for account in check_accounts)
        
        if should_skip_batch:
            print(f"Skipping batch {i//batch_size + 1} as the first five accounts have non-zero token balance")
            continue
        
        
        batch_amounts = [amount_per_recipient] * len(batch_recipients)
        
        print(f"Sending batch {i//batch_size + 1} of {(len(all_recipients)-1)//batch_size + 1}")
        try:
            tx_hash = batch_transfer_erc20(batch_recipients, batch_amounts)
            print(f"Batch transaction successful. Hash: {tx_hash}")
        except Exception as e:
            print(f"Error sending batch: {e}")
            # 여기에 추가적인 오류 처리 로직을 넣을 수 있습니다.
        
        if i + batch_size < len(all_recipients):
            print(f"Waiting for {wait_time} seconds before next batch...")
            time.sleep(wait_time)

    print("All batches sent successfully.")

if __name__ == "__main__":
    main()