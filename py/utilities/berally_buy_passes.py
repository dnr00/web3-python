import asyncio
import aiohttp
import logging
from web3 import Web3
import time
import random

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RPC_URL = 'https://bera-testnet.nodeinfra.com'

# Web3 프로바이더 설정
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# 프록시 컨트랙트 주소
proxy_address = '0x4536f5e298b650134c6444d8d9Ed9f75f7e15aEe'

# Implementation 컨트랙트의 ABI (첨부된 파일의 내용)
implementation_abi = [
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "uint8",
        "name": "version",
        "type": "uint8"
      }
    ],
    "name": "Initialized",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "feePercentage",
        "type": "uint256"
      }
    ],
    "name": "ManagerFeePercentageChanged",
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
        "internalType": "uint256",
        "name": "feePercentage",
        "type": "uint256"
      }
    ],
    "name": "ProtocolFeePercentageChanged",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "address",
        "name": "trader",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "address",
        "name": "manager",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "bool",
        "name": "isBuy",
        "type": "bool"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "passAmount",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "beraAmount",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "protocolBeraAmount",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "managerBeraAmount",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "supply",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "factor",
        "type": "uint256"
      }
    ],
    "name": "Trade",
    "type": "event"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "holder",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "manager",
        "type": "address"
      }
    ],
    "name": "balanceOf",
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
        "name": "manager",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "factor",
        "type": "uint256"
      }
    ],
    "name": "buyPasses",
    "outputs": [],
    "stateMutability": "payable",
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
    "name": "defaultFactors",
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
    "name": "factors",
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
        "name": "manager",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "getBuyPrice",
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
        "name": "manager",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "getBuyPriceAfterFee",
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
        "internalType": "uint256",
        "name": "supply",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "factor",
        "type": "uint256"
      }
    ],
    "name": "getPrice",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "pure",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "manager",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "getSellPrice",
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
        "name": "manager",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "getSellPriceAfterFee",
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
    "name": "initialize",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "managerFeePercentage",
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
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "passesBalance",
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
        "name": "",
        "type": "address"
      }
    ],
    "name": "passesSupply",
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
    "name": "protocolFeePercentage",
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
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "manager",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "minPrice",
        "type": "uint256"
      }
    ],
    "name": "sellPasses",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "factor",
        "type": "uint256"
      },
      {
        "internalType": "bool",
        "name": "status",
        "type": "bool"
      }
    ],
    "name": "setDefaultFactor",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "_feePercentage",
        "type": "uint256"
      }
    ],
    "name": "setManagerFeePercentage",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "_feePercentage",
        "type": "uint256"
      }
    ],
    "name": "setProtocolFeePercentage",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_treasury",
        "type": "address"
      }
    ],
    "name": "setTreasury",
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
    "name": "treasury",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]

# 프록시 주소로 컨트랙트 인스턴스 생성, 하지만 implementation ABI 사용
contract = w3.eth.contract(address=proxy_address, abi=implementation_abi)

# 계정 설정
private_key = '0'
account = w3.eth.account.from_key(private_key)

async def get_logs_for_block(session, block_number, semaphore):
    async with semaphore:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                event_signature_hash = Web3.keccak(text="Trade(address,address,bool,uint256,uint256,uint256,uint256,uint256,uint256)").hex()
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_getLogs",
                    "params": [{
                        "fromBlock": w3.to_hex(block_number),
                        "toBlock": w3.to_hex(block_number),
                        "address": proxy_address,
                        "topics": ["0x"+event_signature_hash]
                    }],
                    "id": 1
                }
                async with session.post(RPC_URL, json=payload) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result.get('result', [])
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    logging.warning(f"Rate limit exceeded. Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                logging.error(f"Error fetching logs for block {block_number}: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)
    return []

async def process_logs(logs):
    unique_accounts = set()
    for log in logs:
        try:
            event = contract.events.Trade().process_log(log)
            if event['args']['isBuy']:
                unique_accounts.add(event['args']['trader'])
        except Exception as e:
            logging.error(f"Error processing log: {e}")
    return unique_accounts

async def get_unique_accounts():
    latest_block = w3.eth.get_block('latest')['number']
    start_block = max(0, latest_block - 10000)  # 최근 1000 블록만 확인
    end_block = latest_block
    unique_accounts = set()

    logging.info(f"Starting block scan from {start_block} to {end_block}")

    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(50)  # 동시에 최대 5개의 요청만 처리
        tasks = [asyncio.create_task(get_logs_for_block(session, block, semaphore)) for block in range(start_block, end_block + 1)]
        
        for i, completed in enumerate(asyncio.as_completed(tasks), 1):
            try:
                logs = await completed
                accounts = await process_logs(logs)
                unique_accounts.update(accounts)
                current_block = start_block + i - 1
                if len(unique_accounts) % 100 == 0 or i % 100 == 0:
                    logging.info(f"Processed Block {current_block}/{end_block} ({i}/{len(tasks)}). "
                                 f"Found {len(unique_accounts)} unique accounts so far.")
            except Exception as e:
                logging.error(f"Error processing block: {e}")

    logging.info(f"Completed block scan from {start_block} to {end_block}. "
                 f"Total unique accounts found: {len(unique_accounts)}")

    return list(unique_accounts)

def buy_passes_for_accounts(accounts):
    logging.info(f"Processing {len(accounts)} unique accounts")
    for i, manager in enumerate(accounts, 1):
        try:
            buy_price = contract.functions.getBuyPrice(manager, 10).call()
            price_in_bera = w3.from_wei(buy_price, 'ether')
            
            logging.info(f"Account {i}/{len(accounts)}: {manager}")
            logging.info(f"Buy Price: {price_in_bera} BERA")
            
            if price_in_bera < 10:
                buy_passes(manager, 10, 500)
            else:
                logging.info(f"Skipping account {manager} as price is 10 BERA or more")
        except Exception as e:
            logging.error(f"Error processing account {manager}: {e}")

def buy_passes(manager, amount, factor):
    try:
        buy_price = contract.functions.getBuyPrice(manager, amount).call()
        
        logging.info(f"Buying passes for {manager}")
        logging.info(f"Calculated buy price: {buy_price} wei")

        gas_price = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price, 'gwei')
        logging.info(f"Current gas price: {gas_price_gwei} Gwei")

        transaction = contract.functions.buyPasses(
            manager,
            amount,
            factor
        ).build_transaction({
            'from': account.address,
            'value': int(buy_price * 1.1),  # 10% 여유 추가
            'gas': 200000,
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': 80084
        })

        signed_txn = account.sign_transaction(transaction)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        logging.info(f"Transaction sent. Hash: 0x{tx_hash.hex()}")
        
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if tx_receipt['status'] == 1:
            logging.info("Transaction Status: Success")
        else:
            logging.warning("Transaction Status: Fail")
        
        logging.info(f"Block Number: {tx_receipt['blockNumber']}")
        logging.info(f"Gas Used: {tx_receipt['gasUsed']}")
        logging.info(f"Transaction Hash: 0x{tx_receipt['transactionHash'].hex()}")
    except Exception as e:
        logging.error(f"Error buying passes for {manager}: {e}")

async def main():
    logging.info("Starting the script...")
    unique_accounts = await get_unique_accounts()
    logging.info(f"Found {len(unique_accounts)} unique accounts interacting with the contract")
    buy_passes_for_accounts(unique_accounts)
    logging.info("Script execution completed.")

if __name__ == "__main__":
    asyncio.run(main())