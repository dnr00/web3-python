from mnemonic import Mnemonic
import secrets

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

# 12개의 단어로 구성된 니모닉 코드 생성
mnemonic_code = generate_mnemonic()
print("12-word mnemonic:", mnemonic_code)

# 24개의 단어로 구성된 니모닉 코드 생성
# mnemonic_code_24 = generate_mnemonic(24)
# print("24-word mnemonic:", mnemonic_code_24)