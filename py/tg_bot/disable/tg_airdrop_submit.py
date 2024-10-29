import nest_asyncio
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from datetime import datetime
from web3 import Web3
import json

nest_asyncio.apply()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram Bot API 토큰
API_TOKEN = 'TG_API_TOKEN'

# 데이터 파일 이름
FILE_NAME = 'apply_accounts.json'

# 최대 등록 가능 인원
MAX_REGISTRATIONS = 200

# Web3 설정
web3 = Web3(Web3.HTTPProvider('https://bera-testnet.nodeinfra.com'))

# 데이터 로드 함수
def load_data():
    try:
        with open(FILE_NAME, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {'users': {}}
    return data

# 데이터 저장 함수
def save_data(data):
    with open(FILE_NAME, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 사용자 상태 저장
user_states = {}

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_states[user_id] = 'START'
    
    data = load_data()
    registered_count = len(data['users'])
    
    keyboard = [
        [InlineKeyboardButton("에어드랍 등록하기", callback_data='register')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (f"안녕하세요! UKSANG2 에어드랍 등록 봇입니다.\n"
                    f"현재 등록된 사용자: {registered_count}/{MAX_REGISTRATIONS}")
    
    await update.message.reply_text(message_text, reply_markup=reply_markup)

async def handle_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    data = load_data()
    if str(user_id) in data['users']:
        await query.edit_message_text("이미 등록하셨습니다.")
        return
    
    if len(data['users']) >= MAX_REGISTRATIONS:
        await query.edit_message_text("죄송합니다. 최대 등록 인원에 도달했습니다.")
        return
    
    user_states[user_id] = 'WAITING_FOR_WALLET'
    await query.edit_message_text("지갑 주소를 입력해주세요.")

async def handle_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if user_states.get(user_id) != 'WAITING_FOR_WALLET':
        await update.message.reply_text("잘못된 접근입니다. /start 명령어로 다시 시작해주세요.")
        return
    
    wallet_address = update.message.text.strip()
    if not web3.is_address(wallet_address):
        await update.message.reply_text("올바른 지갑 주소를 입력해주세요.")
        return
    
    wallet_address = web3.to_checksum_address(wallet_address)
    
    data = load_data()
    if any(user['wallet'] == wallet_address for user in data['users'].values()):
        await update.message.reply_text("이 지갑 주소는 이미 등록되었습니다.")
        return
    
    data['users'][str(user_id)] = {
        'wallet': wallet_address,
        'timestamp': datetime.now().isoformat()
    }
    save_data(data)
    
    user_states[user_id] = 'START'
    await update.message.reply_text("성공적으로 등록되었습니다!")

async def main() -> None:
    application = ApplicationBuilder().token(API_TOKEN).build()
    
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CallbackQueryHandler(handle_register, pattern='^register$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet_address))
    
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())