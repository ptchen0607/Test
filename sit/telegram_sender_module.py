

import requests

class TelegramSender:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_message(self, chat_ids, message):
        for chat_id in chat_ids:
            payload = {
                "chat_id": chat_id,
                "text": message
            }
            response = requests.post(self.url, json=payload, verify=False)
            if response.status_code == 200:
                print(f"Message sent successfully to chat_id: {chat_id}")
            else:
                print(f"Failed to send message to chat_id: {chat_id}. Status code: {response.status_code}")

