import nest_asyncio
import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
import telegram
from telegram.ext import Application, ApplicationBuilder, ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from web3 import Web3
import json
from dotenv import load_dotenv
import os

load_dotenv()
nest_asyncio.apply()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv('UKSANG_PRICE_CHECKER_BOT_API_TOKEN')
GROUP_CHAT_ID = os.getenv('UKSANG_PRICE_CHECKER_BOT_CHAT_ID')
OOGA_BOOGA_API_TOKEN = os.getenv('OOGA_BOOGA_API_TOKEN')

# 토큰 목록 가져오기 및 저장 함수
def fetch_and_save_token_list():
    url = "https://bartio.api.oogabooga.io/v1/tokens"
    headers = {"Authorization": f"Bearer {OOGA_BOOGA_API_TOKEN}",
               "Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        token_list = response.json()
        
        with open('token_list.json', 'w', encoding='utf-8') as f:
            json.dump(token_list, f, ensure_ascii=False, indent=4)
        
        print(f"성공적으로 {len(token_list)}개의 토큰 정보를 저장했습니다.")
        return True
    except Exception as e:
        print(f"토큰 목록 가져오기 중 오류 발생: {e}")
        return False

# 토큰 가격 조회 함수
async def get_token_prices():
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

# 토큰 목록 로드 함수
def load_token_list():
    try:
        with open('token_list.json', 'r') as file:
            token_list = json.load(file)
            return {token['address'].lower(): token['symbol'] for token in token_list}
    except FileNotFoundError:
        print("token_list.json 파일이 없습니다. 새로 생성합니다.")
        if fetch_and_save_token_list():
            return load_token_list()
        return {}
    except json.JSONDecodeError:
        print("token_list.json 파일의 형식이 올바르지 않습니다.")
        return {}

# 가격 매칭 함수
def match_prices_with_symbols(all_prices, address_symbol_pairs):
    matched_prices = {}
    for price_data in all_prices:
        address = price_data['address'].lower()
        if address in address_symbol_pairs:
            symbol = address_symbol_pairs[address]
            matched_prices[symbol] = price_data['price']
    return matched_prices

# 봇 커맨드: 가격 조회
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False) -> None:
    # 콜백 쿼리인 경우와 일반 메시지인 경우를 구분
    if is_callback:
        message = update.callback_query.message
    else:
        message = update.message

    await message.reply_text("가격 정보를 가져오는 중...")

    address_symbol_pairs = load_token_list()
    if not address_symbol_pairs:
        await message.reply_text("토큰 목록을 불러오는데 실패했습니다.")
        return

    all_prices = await get_token_prices()
    if all_prices:
        matched_prices = match_prices_with_symbols(all_prices, address_symbol_pairs)
        
        if matched_prices:
            # 가격순으로 정렬
            sorted_prices = dict(sorted(matched_prices.items(), key=lambda x: x[1], reverse=True))
            
            price_message = "현재 토큰 가격:\n\n"
            for symbol, price in sorted_prices.items():
                price_message += f"{symbol}: ${price:.5f}\n"
            
            # 메시지가 너무 길 경우 나눠서 보내기
            if len(price_message) > 4096:
                for i in range(0, len(price_message), 4096):
                    await message.reply_text(price_message[i:i+4096])
            else:
                if is_callback:
                    await update.callback_query.edit_message_text(price_message)
                else:
                    await message.reply_text(price_message)
        else:
            await message.reply_text("매칭된 가격 정보가 없습니다.")
    else:
        await message.reply_text("가격 정보를 가져오지 못했습니다.")
        
# 봇 커맨드: 토큰 목록 업데이트
async def update_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("토큰 목록을 업데이트하는 중...")
    if fetch_and_save_token_list():
        await update.message.reply_text("토큰 목록이 성공적으로 업데이트되었습니다.")
    else:
        await update.message.reply_text("토큰 목록 업데이트 중 오류가 발생했습니다.")

async def get_main_prices():
    """주요 토큰의 가격을 가져오는 함수"""
    all_prices = await get_token_prices()
    address_symbol_pairs = load_token_list()
    
    if all_prices and address_symbol_pairs:
        matched_prices = match_prices_with_symbols(all_prices, address_symbol_pairs)
        main_tokens = {'WBERA': 0, 'HONEY': 0, 'WBTC': 0}  # 기본값 설정
        
        for symbol, price in matched_prices.items():
            if symbol in main_tokens:
                main_tokens[symbol] = price
        
        return main_tokens
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # 주요 토큰 가격 가져오기
    main_prices = await get_main_prices()
    
    # 메인 메시지 구성
    welcome_message = (
        "안녕하세요! 베라체인 가격 확인 봇입니다. 이 봇은 Ooga Booga API를 기반으로 구동됩니다.\n"
        "Account: ❌\n\n"
        "현재 주요 토큰의 가격"
    )
    
    if main_prices:
        price_message = (
            f"WBERA : ${main_prices.get('WBERA', 0):.2f}\n"
            f"HONEY : ${main_prices.get('HONEY', 0):.2f}\n"
            f"WBTC : ${main_prices.get('WBTC', 0):.2f}"
        )
    else:
        price_message = "가격 정보를 불러올 수 없습니다."

    # 인라인 키보드 버튼 생성
    keyboard = [
        [
            InlineKeyboardButton("💰 가격 확인", callback_data='price'),
            InlineKeyboardButton("⭐ 워치리스트", callback_data='watchlist')
        ],
        [
            InlineKeyboardButton("⚙️ 설정", callback_data='settings'),
            InlineKeyboardButton("❓ 도움말", callback_data='help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 메시지 전송
    message = f"{welcome_message}\n```\n{price_message}\n```\n\n원하는 기능을 선택해 주세요."
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
# 콜백 쿼리 핸들러
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    # 홈으로 돌아가기 버튼 생성
    home_button = [[InlineKeyboardButton("🏠 홈으로 돌아가기", callback_data='home')]]
    home_markup = InlineKeyboardMarkup(home_button)
    
    if query.data == 'home':
        # 홈 화면으로 돌아가기
        main_prices = await get_main_prices()
        welcome_message = (
            "안녕하세요! 베라체인 가격 확인 봇입니다.\n"
            "이 봇은 Ooga Booga API를 기반으로 구동됩니다.\n"
            "Account: ❌\n"
            "아직 주소를 설정하지 않았습니다.\n\n"
            "현재 주요 토큰의 가격"
        )
        
        if main_prices:
            price_message = (
                f"WBERA : ${main_prices.get('WBERA', 0):.2f}\n"
                f"HONEY : ${main_prices.get('HONEY', 0):.2f}\n"
                f"WBTC : ${main_prices.get('WBTC', 0):.2f}"
            )
        else:
            price_message = "가격 정보를 불러올 수 없습니다."

        keyboard = [
            [
                InlineKeyboardButton("💰 가격 확인", callback_data='price'),
                InlineKeyboardButton("⭐ 워치리스트", callback_data='watchlist')
            ],
            [
                InlineKeyboardButton("⚙️ 설정", callback_data='settings'),
                InlineKeyboardButton("❓ 도움말", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"{welcome_message}\n```\n{price_message}\n```\n\n원하는 기능을 선택해 주세요."
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'price':
        await price(update, context, is_callback=True)
        # 가격 정보 메시지 끝에 홈으로 돌아가기 버튼 추가
        await query.message.reply_text("다른 기능을 사용하시려면 아래 버튼을 눌러주세요.", reply_markup=home_markup)
    
    elif query.data == 'watchlist':
        await query.edit_message_text(
            "워치리스트 기능은 준비 중입니다.",
            reply_markup=home_markup
        )
    
    elif query.data == 'settings':
        await query.edit_message_text(
            "설정 기능은 준비 중입니다.",
            reply_markup=home_markup
        )
    
    elif query.data == 'help':
        await query.edit_message_text(
            "도움말 기능은 준비 중입니다.",
            reply_markup=home_markup
        )

async def main() -> None:
    # 시작 시 토큰 목록 생성
    if not load_token_list():
        print("초기 토큰 목록을 생성하지 못했습니다.")
    
    # 봇 생성 및 실행
    application = Application.builder().token(API_TOKEN).build()

    # 커맨드 핸들러 등록
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("price", price))
    application.add_handler(CommandHandler("update_tokens", update_tokens))
    
    # 콜백 쿼리 핸들러 등록
    application.add_handler(CallbackQueryHandler(button_callback))

    # 봇 실행
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())