from telegram import Update, InputFile
from telegram.ext import ContextTypes
from utils.api import get_token_prices
from utils.config import load_token_list
from utils.api import match_prices_with_symbols
from utils.helpers import generate_price_chart

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

async def price_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.args[0] if context.args else 'WBERA'
    time_period = context.args[1] if len(context.args) > 1 else '24h'
    
    chart_buf = await generate_price_chart(token, time_period)
    await update.message.reply_photo(photo=InputFile(chart_buf))

async def compare_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("비교할 토큰 심볼을 2개 이상 입력해주세요.")
        return
    
    tokens = context.args
    prices = await get_token_prices()
    
    comparison_text = "토큰 비교 결과:\n\n"
    for token in tokens:
        price = prices.get(token, 0)
        comparison_text += f"{token}:\n"
        comparison_text += f"현재 가격: ${price:.4f}\n\n"
    
    await update.message.reply_text(comparison_text)