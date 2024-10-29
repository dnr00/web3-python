import nest_asyncio
import asyncio
import logging
from telegram import Bot
from telegram.ext import ApplicationBuilder, ContextTypes
from web3 import Web3
from telegram.error import BadRequest

nest_asyncio.apply()

web3 = Web3(Web3.HTTPProvider('https://bera-testnet.nodeinfra.com'))

# 로깅 설정
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot API 토큰과 그룹 채팅 ID
API_TOKEN = 'TG_API_TOKEN'
GROUP_CHAT_ID = 'GROUP_CHAT_ID'

TOKEN_ADDRESSES = {
 'tHPOT':'0xfc5e3743E9FAC8BB60408797607352E24Db7d65E',
 'JNKY':'0xa0525273423537BC76825B4389F3bAeC1968f83F'
}

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

MY_ADDRESS = '0xe844CC2790Fcff25befabFaE587CbA31aAC2AC4d'

def get_token_balance(token_name, address):
    """ERC20 토큰의 잔고를 조회"""
    token_contract = web3.eth.contract(address=TOKEN_ADDRESSES[token_name], abi=ERC20_ABI)
    balance = token_contract.functions.balanceOf(address).call()
    return balance

async def update_message(context: ContextTypes.DEFAULT_TYPE):
    """API에서 받은 status 값으로 메시지를 업데이트하는 함수"""
    max_retries = 3
    retry_delay = 5  # 재시도 간 대기 시간 (초)

    for attempt in range(max_retries):
        try:
            status1 = get_token_balance("tHPOT", MY_ADDRESS)
            status2 = get_token_balance("JNKY", MY_ADDRESS)
            
            if status1 is not None and status2 is not None:
                new_message = (f"Current thPOT Balance: {web3.from_wei(status1, 'ether')} thPOT\n"
                               f"Current JNKY Balance: {web3.from_wei(status2, 'ether')} JNKY")

                if not hasattr(context.job, 'data') or context.job.data is None:
                    context.job.data = {}
                
                if 'message_id' not in context.job.data:
                    sent_message = await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=new_message)
                    context.job.data['message_id'] = sent_message.message_id
                    context.job.data['last_message'] = new_message
                else:
                    if context.job.data.get('last_message') != new_message:
                        try:
                            await context.bot.edit_message_text(
                                chat_id=GROUP_CHAT_ID, 
                                message_id=context.job.data['message_id'], 
                                text=new_message
                            )
                            context.job.data['last_message'] = new_message
                        except BadRequest as e:
                            if str(e) == "Message is not modified":
                                print("Message content is the same, no update needed.")
                            else:
                                raise
                    else:
                        print("Message content is the same, skipping update.")
                return  # 성공적으로 처리되면 함수 종료
            else:
                raise ValueError("Failed to retrieve the status.")
        except Exception as e:
            if attempt < max_retries - 1:
                await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Failed to retrieve the status. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Failed to retrieve the status after {max_retries} attempts. Error: {str(e)}")
                
async def main():
    """메인 함수에서 봇 설정 및 실행"""
    application = ApplicationBuilder().token(API_TOKEN).build()

    # JobQueue 사용하여 메시지 업데이트 작업 등록
    job_queue = application.job_queue
    job_queue.run_repeating(callback=update_message, interval=30, first=1, data={})  # data 초기화

    # 봇 실행
    await application.run_polling()

if __name__ == '__main__':
    # Jupyter 환경에서의 실행
    asyncio.run(main())