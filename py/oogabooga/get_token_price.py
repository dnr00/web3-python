import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
OOGA_BOOGA_API_TOKEN = os.getenv('OOGA_BOOGA_API_TOKEN')

def get_token_prices():
    url = "https://bartio.api.oogabooga.io/v1/prices"
    querystring = {"currency": "USD"}
    headers = {"Authorization": f"Bearer {OOGA_BOOGA_API_TOKEN}",
               "Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")
        return {}

def load_token_list():
    try:
        with open('token_list.json', 'r') as file:
            token_list = json.load(file)
        return {token['address']: token['symbol'] for token in token_list}
    except FileNotFoundError:
        print("오류: token_list.json 파일을 찾을 수 없습니다.")
        return {}
    except json.JSONDecodeError:
        print("오류: token_list.json 파일의 형식이 올바르지 않습니다.")
        return {}
    
def match_prices_with_symbols(all_prices, address_symbol_pairs):
    matched_prices = {}
    for price_data in all_prices:
        address = price_data['address'].lower()  # 주소를 소문자로 변환
        if address in address_symbol_pairs:
            symbol = address_symbol_pairs[address]
            matched_prices[symbol] = price_data['price']
    return matched_prices

# 주소를 소문자로 변환하는 함수 추가
def lowercase_keys(d):
    return {k.lower(): v for k, v in d.items()}

# token_list.json 파일에서 토큰 목록 읽기
try:
    with open('token_list.json', 'r') as file:
        token_list = json.load(file)
    print(f"token_list.json에서 {len(token_list)}개의 토큰 정보를 읽었습니다.")
    address_symbol_pairs = lowercase_keys({token['address']: token['symbol'] for token in token_list})
except FileNotFoundError:
    print("오류: token_list.json 파일을 찾을 수 없습니다.")
    address_symbol_pairs = {}
except json.JSONDecodeError:
    print("오류: token_list.json 파일의 형식이 올바르지 않습니다.")
    address_symbol_pairs = {}

# 가격 정보를 가져오기
print("API에서 가격 정보를 가져오는 중...")
all_prices = get_token_prices()

if all_prices:
    print(f"API에서 {len(all_prices)}개의 가격 정보를 가져왔습니다.")
    
    # 가격과 기호 매칭
    print("가격 정보와 토큰 기호를 매칭하는 중...")
    matched_prices = match_prices_with_symbols(all_prices, address_symbol_pairs)
    
    # 결과 출력
    if matched_prices:
        print("\n가격 정보:")
        for symbol, price in matched_prices.items():
            print(f"{symbol}: ${price:.5f}")
        print(f"\n총 {len(matched_prices)}개의 토큰에 대한 가격 정보를 찾았습니다.")
    else:
        print("매칭된 가격 정보가 없습니다.")
else:
    print("API에서 가격 정보를 가져오지 못했습니다.")