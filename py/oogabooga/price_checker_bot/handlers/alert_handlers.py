from telegram import Update
from telegram.ext import ContextTypes
from managers.price_alert import price_alert_manager

async def set_price_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3:
        await update.message.reply_text("사용법: /alert <토큰> <가격> <above/below>")
        return
    
    token, price, condition = context.args
    try:
        price = float(price)
        await price_alert_manager.add_alert(update.effective_user.id, token, price, condition)
        await update.message.reply_text(f"알림이 설정되었습니다: {token} ${price} {condition}")
    except ValueError:
        await update.message.reply_text("올바른 가격을 입력해주세요.")