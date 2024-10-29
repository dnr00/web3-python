import nest_asyncio
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
import telegram
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from datetime import datetime, timedelta, time
from web3 import Web3
import pytz
import json
from dotenv import load_dotenv
import os

load_dotenv()
nest_asyncio.apply()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram Bot API 토큰과 그룹 채팅 ID
API_TOKEN = os.getenv('UKSANG_FAUCET_BOT_API_TOKEN')
BOT_CHAT_ID = os.getenv('UKSANG_FAUCET_BOT_CHAT_ID')

WEB3_PROVIDER_URI = 'https://bera-testnet.nodeinfra.com'

# Web3 초기화
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

# Web3 설정

MY_PRIVATE_KEY = os.getenv('MAIN_ACCOUNT')
account = web3.eth.account.from_key(MY_PRIVATE_KEY)
MY_WALLET_ADDRESS = account.address

# 컨트랙트 관련 설정
CONTRACT_ADDRESS = '0x4175E85b953EBe069401b8aA8a20178b8B0A2dcD'
CONTRACT_ABI = [{"type":"constructor","inputs":[],"stateMutability":"nonpayable"},{"type":"receive","stateMutability":"payable"},{"type":"function","name":"getBalance","inputs":[],"outputs":[{"name":"","type":"uint256","internalType":"uint256"}],"stateMutability":"view"},{"type":"function","name":"owner","inputs":[],"outputs":[{"name":"","type":"address","internalType":"address"}],"stateMutability":"view"},{"type":"function","name":"requestFunds","inputs":[{"name":"user","type":"address","internalType":"address"}],"outputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"withdrawAll","inputs":[],"outputs":[],"stateMutability":"nonpayable"}]

# 컨트랙트 인스턴스
faucet_contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

SEOUL_TZ = pytz.timezone('Asia/Seoul')
AUTO_TRANSFER_AMOUNT = 150 # 매일 9시에 토큰 자동으로 채움
MAX_TRANSACTIONS_PER_DAY = 30

# 각 요청 정보 저장
FILE_NAME = 'data.json'

# 데이터 로드 함수
def load_data():
    try:
        with open(FILE_NAME, 'r') as f:
            data = json.load(f)
            # datetime 문자열을 다시 datetime 객체로 변환
            if 'user_requests' in data:
                for user_id, timestamp in data['user_requests'].items():
                    data['user_requests'][user_id] = datetime.fromisoformat(timestamp)
            if 'wallet_requests' in data:
                for address, timestamp in data['wallet_requests'].items():
                    data['wallet_requests'][address] = datetime.fromisoformat(timestamp)
            current_transaction_count = data.get('current_transaction_count', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
        current_transaction_count = 0
    return data, current_transaction_count

data, current_transaction_count = load_data()
user_requests = data.get('user_requests', {})
wallet_requests = data.get('wallet_requests', {})
user_states = {}  # 사용자의 상태를 저장

# 데이터 저장 함수
def save_data():
    global current_transaction_count  # current_transaction_count는 글로벌 변수입니다.
    data = {
        'user_requests': {user_id: timestamp.isoformat() for user_id, timestamp in user_requests.items()},
        'wallet_requests': {address: timestamp.isoformat() for address, timestamp in wallet_requests.items() if isinstance(timestamp, datetime)},
        'current_transaction_count': current_transaction_count,
    }
    with open(FILE_NAME, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def can_request_telegram_user(user_id):
    now = datetime.now(SEOUL_TZ)
    if user_id in user_requests:
        last_request_datetime = user_requests[user_id]
        # 오늘 오전 9시 시각 생성
        today_9am = now.replace(hour=9, minute=0, second=0, microsecond=0)
        # 만약 현재 시각이 오늘 9시 이전이면, 어제 9시를 기준 시각으로 설정
        if now < today_9am:
            today_9am = today_9am - timedelta(days=1)
        # 마지막 요청 시각이 기준 시각 이전이라면 다시 요청 가능
        if last_request_datetime < today_9am:
            user_requests[user_id] = now
            save_data()
            return True
        else:
            return False
    else:
        # 요청 기록이 없다면 요청 가능
        user_requests[user_id] = now
        save_data()
        return True
    
def is_wallet_duplicate(wallet_address):
    now = datetime.now(SEOUL_TZ)
    if wallet_address in wallet_requests:
        last_request_datetime = wallet_requests[wallet_address]

        # 올바른 값인지 체크
        if not isinstance(last_request_datetime, datetime):
            # 잘못된 데이터가 존재하므로 출력
            print(f"올바르지 않은 값 발견: {wallet_address}에 대한 데이터가 없거나 손상됨.")
            return False
        
        # 오늘 오전 9시 시각 생성
        today_9am = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # 만약 현재 시각이 오늘 9시 이전이면, 어제 9시를 기준 시각으로 설정
        if now < today_9am:
            today_9am -= timedelta(days=1)

        # 지갑 주소의 마지막 요청 시각이 기준 시각 이전이라면 다시 요청 가능
        if last_request_datetime < today_9am:
            wallet_requests[wallet_address] = now
            save_data()
            return False
        else:
            return True
    else:
        # 요청 기록이 없다면 새로 기록하고 False 리턴
        wallet_requests[wallet_address] = now
        save_data()
        return False

async def request_tokens_via_contract(user_wallet_address, user_id):
    global current_transaction_count
    
    # 일일 전송 횟수 체크
    if current_transaction_count >= MAX_TRANSACTIONS_PER_DAY:
        return "오늘의 최대 전송 횟수를 초과했습니다."

    nonce = web3.eth.get_transaction_count(MY_WALLET_ADDRESS)
    gas_price = web3.eth.gas_price

    try:
        txn = faucet_contract.functions.requestFunds(user_wallet_address).build_transaction({
            'chainId': 80084,
            'gas': 200000,
            'gasPrice': gas_price,
            'nonce': nonce,
            'from': MY_WALLET_ADDRESS
        })

        signed_txn = web3.eth.account.sign_transaction(txn, private_key=MY_PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction) # 로컬 환경에서는(아마 라이브러리 버전 문제) rawTransaction으로 수정
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        if receipt.status == 1:
            current_transaction_count += 1
            save_data()

            user_balance = web3.from_wei(web3.eth.get_balance(user_wallet_address), 'ether')
            success_message = (f"성공적으로 전송했다곰! 트랜잭션 해시: {web3.to_hex(tx_hash)}\n"
                               f"수령 후 잔액: {round(user_balance, 2)} BERA")
            return success_message
        else:
            if user_wallet_address in wallet_requests:
                del wallet_requests[user_wallet_address], user_requests[user_id]
            save_data()
            return "트랜잭션이 실패했다곰..."
    except Exception as e:
        if user_wallet_address in wallet_requests:
            del wallet_requests[user_wallet_address], user_requests[user_id]
        save_data()
        return f"트랜잭션 에러: {str(e)}"
    
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE, modify_message=False):
    if update.message:
        user_id = update.message.chat_id
    elif update.callback_query:
        user_id = update.callback_query.message.chat_id

    user_states[user_id] = 'START'
    
    # 이미지 URL 또는 로컬 파일 경로
    image_url = "https://assets-global.website-files.com/636e894daa9e99940a604aef/65a1f003b90bcfd48ce6e42d_What%20is%20Berachain_%20(1).webp"  # URL 사용 시
    # image_path = "/path/to/local/image.png"  # 로컬 이미지 사용 시

    keyboard = [
        [InlineKeyboardButton("베라 달라곰!", callback_data='request_token')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Faucet balance 및 today 사용 횟수 출력
    faucet_balance = web3.from_wei(web3.eth.get_balance(CONTRACT_ADDRESS), 'ether')
    message_text = (f"안녕하곰🐻 Uksang의 BERA Faucet에 온 걸 환영한다곰!\n"
                    f"하루에 한 번, 5 BERA를 {MAX_TRANSACTIONS_PER_DAY}명까지 받아갈 수 있다곰!\n"
                    f"현재 Faucet 잔고: {round(faucet_balance, 2)} BERA\n"
                    f"받아간 사람: {current_transaction_count}/{MAX_TRANSACTIONS_PER_DAY}")
    
    if modify_message and update.callback_query:
        # 캡션 수정 시도
        try:
            await update.callback_query.message.edit_caption(caption=message_text, reply_markup=reply_markup)
        except telegram.error.BadRequest:
            # 만약 초기 메시지에 캡션이 없다면 InputMediaPhoto를 사용해서 수정
            await update.callback_query.message.edit_media(
                media=InputFile(media=image_url, caption=message_text),
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_photo(photo=image_url, caption=message_text, reply_markup=reply_markup)

async def handle_request_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.message.chat_id
    await query.answer()

    if current_transaction_count >= MAX_TRANSACTIONS_PER_DAY:
        keyboard = [[InlineKeyboardButton("처음으로", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(caption="오늘은 다 떨어졌다곰😢", reply_markup=reply_markup)
        return
    
    user_states[user_id] = 'WAITING_FOR_WALLET'
    keyboard = [[InlineKeyboardButton("처음으로", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_caption(caption="지갑주소를 입력하라곰!", reply_markup=reply_markup)

async def edit_message_safely(query, caption, reply_markup):
    try:
        if query.message.caption != caption or query.message.reply_markup != reply_markup:
            await query.edit_message_caption(caption=caption, reply_markup=reply_markup)
    except telegram.error.BadRequest as e:
        if str(e) != 'Message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message':
            raise

async def handle_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    query = context.user_data.get("query")
    keyboard = [[InlineKeyboardButton("처음으로", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 메시지 자동 삭제
    message_id = update.message.message_id
    chat_id = update.message.chat_id
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    # 사용자의 상태를 확인
    if user_states.get(user_id) != 'WAITING_FOR_WALLET':
        await edit_message_safely(query, "꼼수 부려도 안 통한다곰!", reply_markup)
        return

    user_wallet_address = update.message.text.strip()

    if not web3.is_address(user_wallet_address):
        await edit_message_safely(query, "올바른 지갑 주소를 입력하라곰!.", reply_markup)
        await asyncio.sleep(3)
        await edit_message_safely(query, "지갑 주소를 입력하라곰!.", reply_markup)
        return

    user_wallet_address = web3.to_checksum_address(user_wallet_address)

    if not can_request_telegram_user(user_id):
        await edit_message_safely(query, "하루에 한 번만 받을 수 있다곰.", reply_markup)
        return

    if is_wallet_duplicate(user_wallet_address):
        await edit_message_safely(query, "이 주소는 이미 BERA를 받았다곰.", reply_markup)
        return

    result_message = await request_tokens_via_contract(user_wallet_address, user_id)
    
    await edit_message_safely(query, result_message, reply_markup)

    user_states[user_id] = 'START'

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data["query"] = query
    data = query.data
    user_id = query.message.chat_id

    if data == 'request_token':
        await handle_request_token(update, context)
    elif data == 'start':
        user_states[user_id] = 'START'
        await handle_start(update, context, modify_message=True)

async def reset_transaction_count(context: ContextTypes.DEFAULT_TYPE):
    global current_transaction_count
    current_transaction_count = 0
    user_requests.clear()
    wallet_requests.clear()
    save_data()
    print("트랜잭션 카운트 및 요청 데이터가 초기화되었습니다.")

async def auto_transfer(context: ContextTypes.DEFAULT_TYPE):
    """자동으로 잔고를 채움"""
    max_retries = 3
    retry_delay = 5  # 재시도 간 대기 시간(초)

    for attempt in range(max_retries):
        if web3.eth.get_balance(MY_WALLET_ADDRESS) < web3.to_wei(AUTO_TRANSFER_AMOUNT, 'ether'):
            print("출발 계정의 잔고가 부족합니다.")
            return
        
        try:
            nonce = web3.eth.get_transaction_count(MY_WALLET_ADDRESS)
            gas_price = web3.eth.gas_price

            transaction = {
                'to': CONTRACT_ADDRESS,
                'chainId': 80084,
                'gas': 200000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'value': web3.to_wei(AUTO_TRANSFER_AMOUNT, 'ether')
            }

            signed_txn = web3.eth.account.sign_transaction(transaction, private_key=MY_PRIVATE_KEY)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
            if receipt.status == 1:
                print(f"자동 송금 성공. 트랜잭션 해시: {web3.to_hex(tx_hash)}")
                return  # 성공 시 함수 종료
            else:
                raise Exception("트랜잭션 실패")
        
        except Exception as e:
            print(f"자동 송금 트랜잭션 실패. 시도 {attempt + 1}/{max_retries}. 오류: {str(e)}")
            if attempt < max_retries - 1:
                print(f"{retry_delay}초 후 재시도합니다...")
                time.sleep(retry_delay)
            else:
                print("최대 재시도 횟수에 도달했습니다. 자동 송금을 중단합니다.") 
        

async def main() -> None:
    application = ApplicationBuilder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet_address))

    job_queue = application.job_queue
    job_queue.run_daily(
        reset_transaction_count, 
        time=time(hour=9, minute=0, second=0, tzinfo=SEOUL_TZ),
        job_kwargs={'coalesce': True, 'misfire_grace_time': 30}
    )

    # auto_transfer 작업 예약 추가
    job_queue.run_daily(
        auto_transfer, 
        time=time(hour=9, minute=0, second=0, tzinfo=SEOUL_TZ),
        job_kwargs={'coalesce': True, 'misfire_grace_time': 30}
    )

    
    await application.run_polling()
    

if __name__ == '__main__':
    asyncio.run(main())