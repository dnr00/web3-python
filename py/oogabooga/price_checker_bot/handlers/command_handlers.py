from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.api import get_main_prices, get_token_prices
from utils.config import fetch_and_save_token_list, load_token_list
from utils.helpers import match_prices_with_symbols

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    main_prices = await get_main_prices()
    
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
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False) -> None:
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
            sorted_prices = dict(sorted(matched_prices.items(), key=lambda x: x[1], reverse=True))
            price_message = "현재 토큰 가격:\n\n"
            
            for symbol, price in sorted_prices.items():
                price_message += f"{symbol}: ${price:.5f}\n"

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

async def update_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("토큰 목록을 업데이트하는 중...")
    if fetch_and_save_token_list():
        await update.message.reply_text("토큰 목록이 성공적으로 업데이트되었습니다.")
    else:
        await update.message.reply_text("토큰 목록 업데이트 중 오류가 발생했습니다.")