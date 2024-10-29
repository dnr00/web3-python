import asyncio
import aiohttp
import json
from web3 import AsyncWeb3
import time

# Web3 설정
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

async def check_token_balance(address):
    balance = await token_contract.functions.balanceOf(address).call()
    return balance

async def transfer_tokens(session, from_address, private_key, to_address, amount):
    nonce = await web3.eth.get_transaction_count(from_address)
    
    txn = await token_contract.functions.transfer(to_address, amount).build_transaction({
        'chainId': 80084, 
        'gas': 200000,
        'gasPrice': await web3.eth.gas_price,
        'nonce': nonce,
    })
    
    signed_txn = web3.eth.account.sign_transaction(txn, private_key)
    tx_hash = await web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    tx_receipt = await web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transfer successful from {from_address} to {to_address}. Transaction hash: {tx_receipt.transactionHash.hex()}")

async def process_account(semaphore, session, account, min_token_balance, transfer_amount, recipient_address):
    global processed_accounts
    async with semaphore:
        address = account['address']
        private_key = account['private_key']
        
        current_balance = await check_token_balance(address)
        if current_balance < min_token_balance:
            print(f"Skipping {address} - Insufficient token balance: {web3.from_wei(current_balance, 'ether')} tokens")
            processed_accounts += 1
            return
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await transfer_tokens(session, address, private_key, recipient_address, transfer_amount)
                print(f"Transfer completed for {address}")
                processed_accounts += 1
                break
            except Exception as e:
                print(f"Error transferring from {address} (Attempt {attempt+1}/{max_retries}): {e}")
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
    global total_accounts, start_time, processed_accounts
    accounts = read_accounts_from_json('accounts.json')
    total_accounts = len(accounts)
    processed_accounts = 0
    min_token_balance = web3.to_wei(10, 'ether')
    transfer_amount = web3.to_wei(300, 'ether')
    recipient_address = '0xe844CC2790Fcff25befabFaE587CbA31aAC2AC4d'
    
    semaphore = asyncio.Semaphore(500)  # 동시에 500개의 작업만 실행되도록 제한
    
    start_time = time.time()
    
    progress_task = asyncio.create_task(print_progress())
    
    async with aiohttp.ClientSession() as session:
        tasks = [process_account(semaphore, session, account, min_token_balance, transfer_amount, recipient_address) for account in accounts]
        await asyncio.gather(*tasks)

    await progress_task  # 진행 상황 출력 태스크가 완료될 때까지 기다림

    print("All transfer requests completed.")
    print(f"Total time elapsed: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())