import asyncio
import json
import time
from web3 import AsyncWeb3

# AsyncWeb3 설정
web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider('https://bera-testnet.nodeinfra.com'))
token_contract_address = '0xfc5e3743E9FAC8BB60408797607352E24Db7d65E'
token_contract_abi = [
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
    "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
    "name": "transferFrom",
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

token_contract = web3.eth.contract(address=token_contract_address, abi=token_contract_abi)

# 전역 변수로 진행 상황을 추적
processed_accounts = 0
total_accounts = 0
start_time = 0

def read_accounts_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

async def call_approve(address, private_key, amount):
    nonce = await web3.eth.get_transaction_count(address)
    
    txn = await token_contract.functions.approve(address, amount).build_transaction({
        'chainId': 80084, 
        'gas': 200000,
        'gasPrice': await web3.eth.gas_price,
        'nonce': nonce,
    })
    
    signed_txn = web3.eth.account.sign_transaction(txn, private_key)
    tx_hash = await web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    tx_receipt = await web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Approve successful for {address}. Transaction hash: {tx_receipt.transactionHash.hex()}")

async def check_allowance(owner_address):
    allowance = await token_contract.functions.allowance(owner_address, owner_address).call()
    return allowance

async def process_account(semaphore, account, approve_amount):
    global processed_accounts
    async with semaphore:
        address = account['address']
        private_key = account['private_key']
        
        current_allowance = await check_allowance(address)
        if current_allowance >= approve_amount:
            print(f"Skipping {address} - Already has sufficient allowance: {web3.from_wei(current_allowance, 'ether')} tokens")
            processed_accounts += 1
            return
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await call_approve(address, private_key, approve_amount)
                print(f"Approve completed for {address}")
                processed_accounts += 1
                break
            except Exception as e:
                print(f"Error approving for {address} (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(3)
                else:
                    print(f"Max retries reached for {address}. Moving to next account.")
                    processed_accounts += 1

async def print_progress():
    while True:
        elapsed_time = time.time() - start_time
        progress = (processed_accounts / total_accounts) * 100
        print(f"Progress: {progress:.2f}% ({processed_accounts}/{total_accounts}) - Elapsed time: {elapsed_time:.2f} seconds")
        if processed_accounts >= total_accounts:
            break
        await asyncio.sleep(3)  # 10초마다 진행 상황 출력

async def main():
    global total_accounts, start_time
    accounts = read_accounts_from_json('accounts.json')
    total_accounts = len(accounts)
    approve_amount = web3.to_wei(1000, 'ether')  # approve 할 금액
    
    semaphore = asyncio.Semaphore(500)  # 동시에 200개의 작업만 실행되도록 제한
    
    start_time = time.time()
    
    progress_task = asyncio.create_task(print_progress())
    
    tasks = [process_account(semaphore, account, approve_amount) for account in accounts]
    await asyncio.gather(*tasks)
    
    await progress_task  # 진행 상황 출력 태스크가 완료될 때까지 기다림

    print("All approve requests completed.")
    print(f"Total time elapsed: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())