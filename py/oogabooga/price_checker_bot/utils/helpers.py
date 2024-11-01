from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
from telegram import InputFile

def match_prices_with_symbols(all_prices, address_symbol_pairs):
    matched_prices = {}
    for price_data in all_prices:
        address = price_data['address'].lower()
        if address in address_symbol_pairs:
            symbol = address_symbol_pairs[address]
            matched_prices[symbol] = price_data['price']
    return matched_prices

async def generate_price_chart(token_symbol: str, time_period: str = '24h'):
    # 임시 데이터 생성 (실제 구현 시에는 API에서 historical 데이터를 가져와야 함)
    now = datetime.now()
    timestamps = []
    values = []
    
    hours = 24 if time_period == '24h' else 168  # 24h 또는 7d
    
    for i in range(hours):
        timestamps.append(now - timedelta(hours=i))
        # 임시 데이터
        values.append(100 + (i % 10))
    
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, values)
    plt.title(f'{token_symbol} Price Chart ({time_period})')
    plt.xlabel('Time')
    plt.ylabel('Price (USD)')
    plt.xticks(rotation=45)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf