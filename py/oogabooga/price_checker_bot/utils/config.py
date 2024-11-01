import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('UKSANG_PRICE_CHECKER_BOT_API_TOKEN')
GROUP_CHAT_ID = os.getenv('UKSANG_PRICE_CHECKER_BOT_CHAT_ID')
OOGA_BOOGA_API_TOKEN = os.getenv('OOGA_BOOGA_API_TOKEN')

def fetch_and_save_token_list():
    url = "https://bartio.api.oogabooga.io/v1/tokens"
    headers = {
        "Authorization": f"Bearer {OOGA_BOOGA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        token_list = response.json()
        with open('token_list.json', 'w', encoding='utf-8') as f:
            json.dump(token_list, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"토큰 목록 가져오기 중 오류 발생: {e}")
        return False

def load_token_list():
    try:
        with open('token_list.json', 'r') as file:
            token_list = json.load(file)
        return {token['address'].lower(): token['symbol'] for token in token_list}
    except FileNotFoundError:
        if fetch_and_save_token_list():
            return load_token_list()
        return {}