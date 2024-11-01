from utils.api import get_token_prices

class PriceAlert:
    def __init__(self):
        self.alerts = {}

    async def add_alert(self, user_id: int, token: str, target_price: float, condition: str):
        if user_id not in self.alerts:
            self.alerts[user_id] = []
        
        self.alerts[user_id].append({
            'token': token,
            'target_price': target_price,
            'condition': condition
        })
        
    async def check_alerts(self, context):
        current_prices = await get_token_prices()
        for user_id, user_alerts in self.alerts.items():
            for alert in user_alerts[:]:
                current_price = current_prices.get(alert['token'])
                if current_price:
                    if (alert['condition'] == 'above' and current_price >= alert['target_price']) or \
                       (alert['condition'] == 'below' and current_price <= alert['target_price']):
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"🔔 알림: {alert['token']}의 가격이 ${current_price:.2f}가 되었습니다!"
                        )
                        self.alerts[user_id].remove(alert)

price_alert_manager = PriceAlert()