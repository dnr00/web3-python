from telegram import Update
from telegram.ext import ContextTypes
from managers.watchlist import watchlist_manager

async def manage_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        user_watchlist = await watchlist_manager.get_watchlist(update.effective_user.id)
        if user_watchlist:
            await update.message.reply_text(f"현재 워치리스트: {', '.join(user_watchlist)}")
        else:
            await update.message.reply_text("워치리스트가 비어있습니다.")
        return

    action = context.args[0]
    if len(context.args) < 2:
        await update.message.reply_text("토큰 심볼을 입력해주세요.")
        return

    token = context.args[1]
    if action == "add":
        if await watchlist_manager.add_token(update.effective_user.id, token):
            await update.message.reply_text(f"{token}이 워치리스트에 추가되었습니다.")
        else:
            await update.message.reply_text("이미 워치리스트에 있는 토큰입니다.")
    elif action == "remove":
        if await watchlist_manager.remove_token(update.effective_user.id, token):
            await update.message.reply_text(f"{token}이 워치리스트에서 제거되었습니다.")
        else:
            await update.message.reply_text("워치리스트에 없는 토큰입니다.")