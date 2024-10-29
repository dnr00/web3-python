import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
OOGA_BOOGA_API_TOKEN = os.getenv('OOGA_BOOGA_API_TOKEN')

url = "https://bartio.api.oogabooga.io/v1/tokens"
headers = {"Authorization": f"Bearer {OOGA_BOOGA_API_TOKEN}",
               "Content-Type": "application/json"}
response = requests.get(url, headers=headers)

# JSON 파일로 저장
with open('token_list.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=4)