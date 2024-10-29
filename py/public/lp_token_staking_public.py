from web3 import Web3
import time

# Ethereum 노드에 연결 (예: Infura)
w3 = Web3(Web3.HTTPProvider('https://bera-testnet.nodeinfra.com'))

# 트랜잭션 보내는 계정
ACCOUNT_ADDRESS = 'your_account_address'
PRIVATE_KEY = 'your_private_key'

# 컨트랙트 주소와 ABI 설정
CONTRACT_ADDRESS = '0xe3b9B72ba027FD6c514C0e5BA075Ac9c77C23Afa'
CONTRACT_ABI = [
    {"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"stake","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}
]

TOKEN_ADDRESSES = {
    'HONEY-USDC-LP': '0xD69ADb6FB5fD6D06E6ceEc5405D95A37F96E3b96'
}
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

# 컨트랙트 인스턴스 생성
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def get_balance():
    """사용자의 스테이킹된 LP 토큰 잔액을 조회합니다."""
    balance = contract.functions.balanceOf(ACCOUNT_ADDRESS).call()
    return balance

def get_token_balance(address):
    """ERC20 토큰의 잔고를 조회"""
    token_contract = w3.eth.contract(address=TOKEN_ADDRESSES["HONEY-USDC-LP"], abi=ERC20_ABI)
    token_balance = token_contract.functions.balanceOf(address).call()
    return token_balance

def send_transaction(func, value=0):
    """트랜잭션을 생성하고 전송합니다."""
    nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    txn = func.build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': nonce,
        'value': value,
        'gas': 2000000,  # 가스 한도 설정
        'gasPrice': w3.eth.gas_price,
    })
    
    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"Transaction sent. Hash: 0x{tx_hash.hex()}")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction confirmed in block {tx_receipt['blockNumber']}")
    return tx_receipt

def stake(amount):
    """지정된 양의 LP 토큰을 스테이킹합니다."""
    print(f"Staking {w3.from_wei(amount, 'ether')} LP tokens...")
    func = contract.functions.stake(amount)
    return send_transaction(func)

def withdraw(amount):
    """지정된 양의 LP 토큰을 출금합니다."""
    print(f"Withdrawing {w3.from_wei(amount, 'ether')} LP tokens...")
    func = contract.functions.withdraw(amount)
    return send_transaction(func)

def main():
    while True:
        print("\n1. Check Balance")
        print("2. Stake LP Tokens")
        print("3. Withdraw LP Tokens")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            balance = get_balance()
            print(f"Your current staked LP token balance: {w3.from_wei(balance, 'ether')}")
        
        elif choice == '2':
            token_balance = get_token_balance(ACCOUNT_ADDRESS)
            print(f"Your current LP token balance in your account: {w3.from_wei(token_balance, 'ether')}")
            amount = float(input("Enter the amount of LP tokens to stake: "))
            stake(w3.to_wei(amount, 'ether'))
        
        elif choice == '3':
            balance = get_balance()
            print(f"Your current staked LP token balance: {w3.from_wei(balance, 'ether')}")
            amount = float(input("Enter the amount of LP tokens to withdraw: "))
            if amount > balance:
                print("Error: Withdrawal amount exceeds balance")
            else:
                withdraw(w3.to_wei(amount, 'ether'))
        
        elif choice == '4':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")
        
        time.sleep(1)  # 잠시 대기

if __name__ == "__main__":
    main()