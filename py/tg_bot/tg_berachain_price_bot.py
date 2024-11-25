import nest_asyncio
import asyncio
import logging
import os
from telegram.ext import ApplicationBuilder, ContextTypes
from web3 import Web3
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
from collections import defaultdict
import time
import aiohttp

load_dotenv()
nest_asyncio.apply()

# 로깅 설정
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot API token과 그룹 Chat ID
API_TOKEN = os.getenv('UKSANG_BOT_API_TOKEN')
GROUP_CHAT_ID = os.getenv('UKSANG_PRICE_BOT_CHAT_ID')
OOGA_BOOGA_API_TOKEN = os.getenv('OOGA_BOOGA_API_TOKEN')

# Web3 설정
WEB3_PROVIDER_URI = 'https://bera-testnet.nodeinfra.com'
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

# 가격 히스토리를 저장할 전역 딕셔너리
PRICE_HISTORY_FILE = 'price_history.json'
price_history = defaultdict(list)  # {token: [(timestamp, price), ...]}

def get_token_prices():
    url = "https://bartio.api.oogabooga.io/v1/prices"
    querystring = {"currency": "USD"}
    headers = {
        "Authorization": f"Bearer {OOGA_BOOGA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params=querystring,
            timeout=(5, 10) # connect timeout 3s, read timeout 10s
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")
        return {}
    
async def get_token_prices_async():
    url = "https://bartio.api.oogabooga.io/v1/prices"
    querystring = {"currency": "USD"}
    headers = {
        "Authorization": f"Bearer {OOGA_BOOGA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=querystring, timeout=30) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            print(f"API 요청 중 오류 발생: {e}")
            return {}    

def get_token_list():
    url = "https://bartio.api.oogabooga.io/v1/tokens"
    headers = {
        "Authorization": f"Bearer {OOGA_BOOGA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # JSON 파일로 저장
        with open('token_list.json', 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)
            
        # address_symbol_pairs 업데이트
        global address_symbol_pairs
        token_list = response.json()
        address_symbol_pairs = lowercase_keys({token['address']: token['symbol'] for token in token_list})
        
        print(f"token_list.json이 업데이트되었습니다. {len(token_list)}개의 토큰 정보가 저장되었습니다.")
        return True
    except Exception as e:
        print(f"토큰 리스트 업데이트 중 오류 발생: {e}")
        return False

async def update_token_list(context: ContextTypes.DEFAULT_TYPE):
    """토큰 리스트를 주기적으로 업데이트하는 함수"""
    get_token_list()

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

def load_token_list_from_file():
    """token_list.json 파일에서 토큰 목록을 읽어오는 함수"""
    try:
        with open('token_list.json', 'r') as file:
            token_list = json.load(file)
        print(f"token_list.json에서 {len(token_list)}개의 토큰 정보를 읽었습니다.")
        return lowercase_keys({token['address']: token['symbol'] for token in token_list})
    except FileNotFoundError:
        print("오류: token_list.json 파일을 찾을 수 없습니다.")
        return {}
    except json.JSONDecodeError:
        print("오류: token_list.json 파일의 형식이 올바르지 않습니다.")
        return {}

def categorize_and_sort_prices(matched_prices):
    """가격을 카테고리별로 분류하고 정렬"""
    # 제외할 토큰 리스트
    excluded_tokens = {'BHOT', 'BHYT', 'aWBTC', 'aWETH', 'stDYDX', 'CRACK', 'SPELL', 'fBERA', 'LORE', 'JNKY', 'BEARTIC', 'JANITOOR', 'SHMOKEY', 'wifsock'}
    
    # 카테고리별 토큰 정의
    categories = {
        'Berachain Native': {'WBERA', 'WBTC', 'WETH'},
        'Stablecoin': {'HONEY', 'DAI', 'aHONEY', 'bHONEY', 'USDC', 'USDT', 'NECT', 'MEAD', 'MIM'},
        'OogaBooga': {'OOGA', 'KEVIN'}
    }
    
    # 결과를 저장할 딕셔너리
    categorized_prices = {
        'Berachain Native': {},
        'Stablecoin': {},
        'OogaBooga': {},
        'Rest': {}
    }
    
    # 가격 데이터 분류
    for token, price in matched_prices.items():
        if token in excluded_tokens:
            continue
            
        price_float = float(price)
        categorized = False
        for category, tokens in categories.items():
            if token in tokens:
                categorized_prices[category][token] = price_float
                categorized = True
                break
        
        if not categorized:
            categorized_prices['Rest'][token] = price_float
    
    # 각 카테고리 내에서 가격 기준 내림차순 정렬
    for category in categorized_prices:
        categorized_prices[category] = dict(sorted(
            categorized_prices[category].items(),
            key=lambda x: float(x[1]),
            reverse=True
        ))
    
    return categorized_prices

def load_price_history():
    """저장된 가격 히스토리 파일 불러오기"""
    global price_history
    try:
        if os.path.exists(PRICE_HISTORY_FILE):
            with open(PRICE_HISTORY_FILE, 'r') as f:
                loaded_data = json.load(f)
                # defaultdict로 변환
                price_history = defaultdict(list, {k: v for k, v in loaded_data.items()})
                print(f"가격 히스토리 데이터를 불러왔습니다. ({len(price_history)} 토큰)")
    except Exception as e:
        print(f"가격 히스토리 파일 로딩 중 오류 발생: {e}")
        price_history = defaultdict(list)

def save_price_history():
    """가격 히스토리를 파일로 저장"""
    try:
        with open(PRICE_HISTORY_FILE, 'w') as f:
            json.dump(dict(price_history), f)
    except Exception as e:
        print(f"가격 히스토리 저장 중 오류 발생: {e}")

def store_price_history(matched_prices):
    """가격 히스토리 저장 및 오래된 데이터 정리"""
    current_time = time.time()
    for token, price in matched_prices.items():
        price_history[token].append((current_time, float(price)))
        # 24시간 이상 된 데이터는 삭제
        price_history[token] = [(t, p) for t, p in price_history[token] 
                              if current_time - t <= 24*60*60]
    # 변경된 데이터를 파일로 저장
    save_price_history()

def clean_old_price_history():
    """24시간이 지난 가격 데이터 삭제"""
    current_time = time.time()
    for token in price_history:
        price_history[token] = [
            (t, p) for t, p in price_history[token] 
            if current_time - t <= 24*60*60
        ]

def get_price_change(token, current_price, minutes):
    """특정 시간 전과의 가격 변화율 계산"""
    if token not in price_history:
        return None
    
    current_time = time.time()
    target_time = current_time - (minutes * 60)
    
    # 지정된 시간에 가장 가까운 과거 가격 찾기
    historical_prices = price_history[token]
    closest_price = None
    min_time_diff = float('inf')
    
    for timestamp, price in historical_prices:
        if timestamp <= target_time:
            time_diff = abs(timestamp - target_time)
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_price = price
    
    if closest_price is None:
        return None
    
    change = ((float(current_price) - closest_price) / closest_price) * 100
    return change

def format_price_changes(changes):
    """가격 변화 문자열 포맷팅"""
    result = []
    for period, change in changes.items():
        if change is not None:
            emoji = "📈" if change > 0 else "📉" if change < 0 else "➖"
            result.append(f"{period}: {emoji} {change:+.2f}%")
    return " | ".join(result) if result else "No historical data"

def get_24h_high_low(token):
    """24시간 동안의 최고가와 최저가 계산"""
    current_time = time.time()
    if token not in price_history:
        return None, None
    
    # 24시간 이내의 가격 데이터만 필터링
    prices_24h = [price for timestamp, price in price_history[token] 
                 if current_time - timestamp <= 24*60*60]
    
    if not prices_24h:
        return None, None
        
    return max(prices_24h), min(prices_24h)

def format_high_low(current_price, high, low):
    """최고가/최저가 문자열 포맷팅"""
    if high is None or low is None:
        return "24h H/L: No data"
    
    # 현재가가 최고가 대비 얼마나 하락했는지
    down_from_high = ((current_price - high) / high) * 100
    # 현재가가 최저가 대비 얼마나 상승했는지
    up_from_low = ((current_price - low) / low) * 100
    
    return f"24h H/L: ${high:.5f} ({down_from_high:.2f}%) / ${low:.5f} ({up_from_low:+.2f}%)"

async def repeat_message(context: ContextTypes.DEFAULT_TYPE):
    """API에서 받은 status 값을 그룹에 반복해서 보내는 함수"""
    prices = await get_token_prices_async()
    
    if prices:
        matched_prices = match_prices_with_symbols(prices, address_symbol_pairs)
        
        if matched_prices:
            # 현재 가격 저장
            store_price_history(matched_prices)
            clean_old_price_history()
            categorized_prices = categorize_and_sort_prices(matched_prices)
            
            message = f"Token Prices (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n\n"
            
            for category, prices in categorized_prices.items():
                if prices:
                    message += f"📌 {category}\n"
                    for token, price in prices.items():
                        # 각 시간대별 변화율 계산
                        changes = {
                            "5m": get_price_change(token, price, 5),
                            "1h": get_price_change(token, price, 60),
                            "4h": get_price_change(token, price, 240),
                            "24h": get_price_change(token, price, 1440)
                        }
                        
                        # 24시간 최고가/최저가 계산
                        high, low = get_24h_high_low(token)
                        price_changes = format_price_changes(changes)
                        high_low = format_high_low(price, high, low)
    
                        message += f"{token}: ${price:.5f}\n{price_changes}\n{high_low}\n\n"
                    message += "\n"
        else:
            message = "매칭된 가격 정보가 없습니다."
    else:
        message = "API에서 가격 정보를 가져오지 못했습니다."

    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)

async def main():
    """메인 함수에서 봇 설정 및 실행"""
    # 초기 데이터 로드
    load_price_history()
    
    # token_list.json 파일 존재 여부 확인
    if not os.path.exists('token_list.json'):
        print("token_list.json 파일이 존재하지 않습니다. 새로 불러옵니다.")
        success = get_token_list()
        if not success:
            print("토큰 리스트를 불러오는데 실패했습니다. 기본 빈 딕셔너리로 시작합니다.")
            global address_symbol_pairs
            address_symbol_pairs = {}
    
    application = ApplicationBuilder().token(API_TOKEN).build()

    # JobQueue 사용하여 작업 등록
    job_queue = application.job_queue
    job_queue.run_repeating(callback=repeat_message, interval=30, first=1)
    job_queue.run_repeating(callback=update_token_list, interval=3600, first=10)

    try:
        # 봇 실행
        await application.run_polling()
    finally:
        # 프로그램 종료 시 데이터 저장
        save_price_history()

if __name__ == '__main__':
    # Jupyter 환경에서의 실행
    asyncio.run(main())