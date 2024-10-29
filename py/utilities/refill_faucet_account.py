from web3 import Web3
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
  }
]

# 컨트랙트 인스턴스 생성
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# 서명할 지갑 주소와 개인키
YOUR_PRIVATE_KEY = os.getenv('MAIN_ACCOUNT')
account = w3.eth.account.from_key(YOUR_PRIVATE_KEY)
YOUR_WALLET_ADDRESS = account.address


# 받는 사람들의 주소 (직접 입력)
recipients = [
    '0x7ADD9dC0Ccf5A1866F0C39cD9A0Ce7190768b48c',
    '0xBbAb188865BF9825F00A3D050DfA0Ed27f54C43A',
    '0x981Fe9c81dB490CC953B7e185096FCFfF24585F8',
    '0x0D619e76A71EBFa69596dC02EAbcB78D858e929F'
]

AMOUNT_PER_ADDRESS = w3.to_wei(200, 'ether')  # 각 주소로 보낼 금액 (ETH)

def get_balance(address):
    balance_wei = w3.eth.get_balance(address)
    return w3.from_wei(balance_wei, 'ether')

def print_balances():
    for idx, address in enumerate(recipients, 1):
        balance = get_balance(address)
        print(f"계정 {idx}: {address}, 잔액: {balance:.4f} ETH")

def get_selected_recipients():
    while True:
        selection = input("토큰을 송금할 계정 번호를 입력하세요 (1-4, 콤마로 구분, 또는 'all'): ").strip().lower()
        if selection == 'all':
            return recipients
        try:
            selected = [recipients[int(num)-1] for num in selection.split(',') if 1 <= int(num) <= 4]
            if selected:
                return selected
        except ValueError:
            pass
        print("잘못된 입력입니다. 다시 시도해주세요.")

def send_batch_transaction(w3, contract, sender_address, private_key, recipients, amounts):
    total_amount = sum(amounts)
    txn = contract.functions.batchTransfer(recipients, amounts).build_transaction({
        'from': sender_address,
        'value': total_amount,
        'gas': 2000000,
        'gasPrice': int(w3.eth.gas_price * 1.4),
        'nonce': w3.eth.get_transaction_count(sender_address),
    })
    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def main():
    if not w3.is_connected():
        print("이더리움 네트워크에 연결할 수 없습니다.")
        return

    print("각 계정의 현재 잔액:")
    print_balances()
    
    selected_recipients = get_selected_recipients()
    amounts = [AMOUNT_PER_ADDRESS] * len(selected_recipients)
    
    print("\n토큰 전송 시작:")
    try:
        tx_hash = send_batch_transaction(w3, contract, YOUR_WALLET_ADDRESS, YOUR_PRIVATE_KEY, selected_recipients, amounts)
        print(f"트랜잭션이 성공적으로 전송되었습니다. 해시: {tx_hash}")
    except Exception as e:
        print(f"트랜잭션 전송 중 오류 발생: {e}")

if __name__ == "__main__":
    main()