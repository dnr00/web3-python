from web3 import Web3

# Web3 설정
web3 = Web3(Web3.HTTPProvider('https://bera-testnet.nodeinfra.com')) #예시(베라체인 노드인프라 RPC URL)

# 토큰 컨트랙트 주소와 ABI 설정
token_contract_address = '0xfc5e3743E9FAC8BB60408797607352E24Db7d65E' #예시 컨트랙트 주소
token_contract_abi = [ # 예시 컨트랙트 ABI
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

def check_allowance(owner_address, spender_address):
    allowance = token_contract.functions.allowance(owner_address, spender_address).call()
    return web3.from_wei(allowance, 'ether')

# 사용 예시
owner = 'owner_address' # 토큰 소유자 주소
spender = 'spender_address' # 토큰 사용 권한을 요청하는 주소 (주로 Contract)

allowed_amount = check_allowance(owner, spender)
print(f"The spender {spender} is allowed to spend {allowed_amount} tokens on behalf of {owner}")