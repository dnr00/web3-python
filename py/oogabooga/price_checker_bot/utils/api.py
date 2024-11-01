import requests
from utils.config import OOGA_BOOGA_API_TOKEN

async def get_token_prices():
    """모든 토큰의 가격 정보를 가져오는 함수"""
    url = "https://bartio.api.oogabooga.io/v1/prices"
    querystring = {"currency": "USD"}
    headers = {
        "Authorization": f"Bearer {OOGA_BOOGA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")
        return {}

async def get_main_prices():
    """주요 토큰의 가격을 가져오는 함수"""
    from utils.config import load_token_list  # 순환 참조 방지를 위해 함수 내에서 import

    all_prices = await get_token_prices()
    address_symbol_pairs = load_token_list()
    
    if all_prices and address_symbol_pairs:
        # address_symbol_pairs의 키-값을 반전시켜 symbol:address 매핑 생성
        symbol_address_pairs = {v: k for k, v in address_symbol_pairs.items()}
        
        main_tokens = {'WBERA': 0, 'HONEY': 0, 'WBTC': 0}  # 기본값 설정
        
        for price_data in all_prices:
            address = price_data['address'].lower()
            if address in address_symbol_pairs:
                symbol = address_symbol_pairs[address]
                if symbol in main_tokens:
                    main_tokens[symbol] = price_data['price']
        
        return main_tokens
    return None

def match_prices_with_symbols(all_prices, address_symbol_pairs):
    """가격 정보와 토큰 심볼을 매칭하는 함수"""
    matched_prices = {}
    for price_data in all_prices:
        address = price_data['address'].lower()
        if address in address_symbol_pairs:
            symbol = address_symbol_pairs[address]
            matched_prices[symbol] = price_data['price']
    return matched_prices