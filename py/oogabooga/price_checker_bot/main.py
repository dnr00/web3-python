import asyncio
from telegram import Update
from bot import create_application
from utils.config import load_token_list

async def main() -> None:
    if not load_token_list():
        print("초기 토큰 목록을 생성하지 못했습니다.")
    
    application = await create_application()
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())