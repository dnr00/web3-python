from web3 import Web3
import json, time
from dotenv import load_dotenv
import os

load_dotenv()
# Web3 설정
w3 = Web3(Web3.HTTPProvider('https://bera-testnet.nodeinfra.com'))

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
    "name": "withdraw",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]

# 컨트랙트 인스턴스 생성
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def read_addresses_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return [entry['address'] for entry in data]

json_file_path = '/mnt/c/workspace/web3-python/py/multisend/batch/accounts.json'    #'/home/dnr000129/bot/batch/accounts.json'
all_recipients = read_addresses_from_json(json_file_path)

# 받는 사람들의 주소와 금액
amount_per_address = Web3.to_wei(0.00001, 'ether')

# 트랜잭션 보내는 사람의 주소와 개인키
YOUR_PRIVATE_KEY = os.getenv('FOURTH_ACCOUNT')
account = w3.eth.account.from_key(YOUR_PRIVATE_KEY)
YOUR_WALLET_ADDRESS = account.address

def send_batch_transaction(w3, contract, sender_address, private_key, recipients, amounts):
    total_amount = sum(amounts)
    txn = contract.functions.batchTransfer(recipients, amounts).build_transaction({
        'from': sender_address,
        'value': total_amount,
        'gas': 25000000,
        'gasPrice': int(w3.eth.gas_price * 1.4),
        'nonce': w3.eth.get_transaction_count(sender_address),
    })
    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

batch_size = 500
wait_time = 1

# 배치 전송
for i in range(0, len(all_recipients), batch_size):
    batch_recipients = all_recipients[i:i+batch_size]
    
    # 첫 다섯 계정의 잔고 확인
    check_accounts = batch_recipients[:5]
    should_skip_batch = all(w3.eth.get_balance(account) > 0 for account in check_accounts)
    
    if should_skip_batch:
        print(f"Skipping batch {i//batch_size + 1} as the first five accounts have non-zero balance")
        continue
    
    batch_amounts = [amount_per_address] * len(batch_recipients)
    
    print(f"Sending batch {i//batch_size + 1} of {(len(all_recipients)-1)//batch_size + 1}")
    try:
        tx_hash = send_batch_transaction(w3, contract, YOUR_WALLET_ADDRESS, YOUR_PRIVATE_KEY, batch_recipients, batch_amounts)
        print(f"Batch transaction successful. Hash: {tx_hash}")
    except Exception as e:
        print(f"Error sending batch: {e}")
        # 여기에 오류 처리 로직을 추가할 수 있습니다.
    
    if i + batch_size < len(all_recipients):
        print(f"Waiting for {wait_time} seconds before next batch...")
        time.sleep(wait_time)

print("All batches sent successfully.")