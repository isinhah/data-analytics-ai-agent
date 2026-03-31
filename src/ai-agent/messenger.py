import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TelegramMessenger:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("CHAT_ID")
        self.url_base = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def enviar_mensagem(self, texto):
        payload = {
            "chat_id": self.chat_id,
            "text": texto,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(self.url_base, data=payload)
            return response.json()
        except Exception as e:
            print(f"❌ Erro ao enviar Telegram: {e}")