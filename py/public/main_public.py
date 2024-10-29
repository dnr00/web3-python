import nest_asyncio
import asyncio
import logging
from telegram import Bot
from telegram.ext import ApplicationBuilder, ContextTypes
import requests

nest_asyncio.apply()

# 로깅 설정
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot API token과 그룹 Chat ID
API_TOKEN = "YOUR_API_TOKEN"  # 실제로 사용 중인 Bot의 API token으로 대체
GROUP_CHAT_ID = "YOUR_CHAT_ID"  # 실제로 사용 중인 그룹의 채팅 ID로 대체

API_URL = 'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan/api?module=account&action=tokenbalance&contractaddress=0xe8c4e92530F1A9d407891Edd00B335bC6676C68F&address=0xAd1782b2a7020631249031618fB1Bd09CD926b31&tag=latest'

def fetch_result():
    """API에서 result 값을 가져오는 함수"""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # 요청 실패 시 예외 발생
        data = response.json()  # JSON 응답을 파이썬 객체로 변환
        return data['result']  # 'status' 필드의 값을 반환
    except requests.RequestException as e:
        logger.error(f"API 요청 중 에러 발생: {e}")
        return None

async def repeat_message(context: ContextTypes.DEFAULT_TYPE):
    """API에서 받은 status 값을 그룹에 반복해서 보내는 함수"""
    status = round(int(fetch_result())*(0.000000000000000001), 2)
    if status is not None:
        message = f"Current DAI Vault Balance: {status}"  # 전송할 메시지
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
    else:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="Failed to retrieve the status.")


async def main():
    """메인 함수에서 봇 설정 및 실행"""
    application = ApplicationBuilder().token(API_TOKEN).build()

    # JobQueue 사용하여 메시지 전송 반복 작업 등록
    job_queue = application.job_queue
    job_queue.run_repeating(callback=repeat_message, interval=3, first=1)  # 5초마다 실행

    # 봇 실행
    await application.run_polling()

if __name__ == '__main__':
    # Jupyter 환경에서의 실행
    asyncio.run(main())