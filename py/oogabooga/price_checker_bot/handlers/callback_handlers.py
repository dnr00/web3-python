from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.api import get_main_prices
from handlers.command_handlers import price, update_tokens
from managers.watchlist import watchlist_manager

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    home_button = [[InlineKeyboardButton("🏠 홈으로 돌아가기", callback_data='home')]]
    home_markup = InlineKeyboardMarkup(home_button)

    if query.data == 'home':
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
                InlineKeyboardButton("📊 차트", callback_data='chart'),
                InlineKeyboardButton("🔔 알림 설정", callback_data='alert')
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
        await query.message.reply_text(
            "다른 기능을 사용하시려면 아래 버튼을 눌러주세요.",
            reply_markup=home_markup
        )

    elif query.data == 'watchlist':
        user_id = update.effective_user.id
        watchlist = await watchlist_manager.get_watchlist(user_id)
        
        if watchlist:
            await query.message.reply_text(f"현재 워치리스트: {', '.join(watchlist)}")
        else:
            await query.message.reply_text("워치리스트가 비어있습니다.")
            
        await query.message.reply_text(
            "워치리스트를 관리하려면 다음 명령어를 사용하세요:\n"
            "/watchlist add <토큰심볼> - 워치리스트에 토큰 추가\n"
            "/watchlist remove <토큰심볼> - 워치리스트에서 토큰 제거\n"
            "/watchlist - 현재 워치리스트 확인",
            reply_markup=home_markup
        )

    elif query.data == 'chart':
        await query.edit_message_text(
            "차트를 보려면 다음 명령어를 사용하세요:\n"
            "/chart <토큰심볼> [시간단위]\n"
            "예시: /chart WBERA 24h\n"
            "시간단위: 24h (기본값), 7d",
            reply_markup=home_markup
        )

    elif query.data == 'alert':
        await query.edit_message_text(
            "가격 알림을 설정하려면 다음 명령어를 사용하세요:\n"
            "/alert <토큰심볼> <가격> <above/below>\n"
            "예시: /alert WBERA 1.5 above\n"
            "위 예시는 WBERA 가격이 $1.5 이상이 되면 알림을 보냅니다.",
            reply_markup=home_markup
        )

    elif query.data == 'settings':
        keyboard = [
            [
                InlineKeyboardButton("🔄 토큰 목록 업데이트", callback_data='update_tokens'),
                InlineKeyboardButton("🏠 홈으로", callback_data='home')
            ]
        ]
        settings_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "설정 메뉴입니다. 원하는 기능을 선택하세요.",
            reply_markup=settings_markup
        )

    elif query.data == 'update_tokens':
        await update_tokens(update, context, is_callback=True)
        await query.message.reply_text(
            "다른 기능을 사용하시려면 아래 버튼을 눌러주세요.",
            reply_markup=home_markup
        )

    elif query.data == 'help':
        help_text = (
            "🤖 사용 가능한 명령어 목록:\n\n"
            "/start - 봇 시작 및 메인 메뉴\n"
            "/price - 모든 토큰의 현재 가격 확인\n"
            "/chart <토큰> [24h/7d] - 토큰의 가격 차트 보기\n"
            "/alert <토큰> <가격> <above/below> - 가격 알림 설정\n"
            "/watchlist - 워치리스트 관리\n"
            "/update_tokens - 토큰 목록 업데이트\n\n"
            "자세한 사용법은 각 기능의 도움말을 참고하세요."
        )
        await query.edit_message_text(help_text, reply_markup=home_markup)