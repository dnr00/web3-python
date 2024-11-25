import nest_asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from handlers.command_handlers import start, price, update_tokens
from handlers.callback_handlers import button_callback
from handlers.price_handlers import price_chart, compare_tokens
from handlers.alert_handlers import set_price_alert
from handlers.watchlist_handlers import manage_watchlist
from utils.config import API_TOKEN
from managers.price_alert import price_alert_manager
from managers.watchlist import watchlist_manager

nest_asyncio.apply()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def create_application():
    application = Application.builder().token(API_TOKEN).build()
    
    # 기본 핸들러
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("price", price))
    application.add_handler(CommandHandler("update_tokens", update_tokens))
    
    # 새로운 핸들러
    application.add_handler(CommandHandler("chart", price_chart))
    application.add_handler(CommandHandler("compare", compare_tokens))
    application.add_handler(CommandHandler("alert", set_price_alert))
    application.add_handler(CommandHandler("watchlist", manage_watchlist))
    
    # 콜백 쿼리 핸들러
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # 주기적인 가격 알림 체크
    application.job_queue.run_repeating(price_alert_manager.check_alerts, interval=30)
    
    return application