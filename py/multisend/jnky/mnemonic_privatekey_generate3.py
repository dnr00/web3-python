from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from web3 import Web3
import random
import json
from mnemonic import Mnemonic
import secrets

def mnemonic_to_private_key(mnemonic, account_index=0, address_index=0):
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    bip44_acc = bip44_mst_ctx.Purpose().Coin().Account(account_index)
    bip44_chg = bip44_acc.Change(Bip44Changes.CHAIN_EXT)
    bip44_addr = bip44_chg.AddressIndex(address_index)
    
    private_key = bip44_addr.PrivateKey().Raw().ToHex()
    
    return private_key

def generate_mnemonic(num_words=12, language="english"):
    mnemo = Mnemonic(language)
    
    # 엔트로피 계산: 12단어는 128비트, 24단어는 256비트
    if num_words == 24:
        entropy = secrets.token_bytes(32)  # 256 비트
    else:
        entropy = secrets.token_bytes(16)  # 128 비트 (기본값)
    
    # 니모닉 생성
    mnemonic = mnemo.to_mnemonic(entropy)
    return mnemonic

# 니모닉을 직접 코드에 입력
mnemonic = generate_mnemonic()

# 생성할 계정 수를 직접 지정
num_accounts = 1000

accounts = []

for i in range(num_accounts):
    # 랜덤한 address_index 생성 (0부터 1,000,000 사이의 정수)
    address_index = random.randint(0, 1000000)

    # 프라이빗 키 생성
    private_key = mnemonic_to_private_key(mnemonic, account_index=0, address_index=address_index)

    # Web3.py로 계정 생성
    web3 = Web3()
    account = web3.eth.account.from_key(private_key)

    accounts.append({
        "address": account.address,
        "private_key": private_key
    })

    print(f"\nAccount {i+1}:")
    print(f"Ethereum Address: {account.address}")
    print(f"Private Key: {private_key}")
    print(f"Used address index: {address_index}")

# JSON 파일로 저장
with open('accounts.json', 'w') as f:
    json.dump(accounts, f, indent=4)

print("\nAccounts have been saved to accounts.json")


