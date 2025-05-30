import requests
import json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjdlYTkwMTliLWI0OTgtNGZjMy1iZGEyLTk0OTVkOWY5NWQ2NSIsImV4cCI6MTc0ODk2NTM1Nn0._mbtE_49QgSO5JTVduj7WQcfhZPeIkEhesGyTHaNP70"

QWEN_URL = "https://chat.qwenlm.ai/api/chat/completions"
QWEN_HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.84.2.178 Safari/537.36"
}

# Пример сообщений для отправки
messages = [
    {"role": "user", "content": "Привет!", "extra": {}, "chat_type": "t2t"},
] # chat_type указываю на t2t для обмена сообщениями (В самом ИИ можно ещё видео и картинки генерировать)

payload = {
    "chat_type": "t2t",
    "messages": messages,
    "model": "qwen-max-latest",
    "stream": False
}

# Отправка POST-запроса
response = requests.post(QWEN_URL, headers=QWEN_HEADERS, json=payload)

# Обработка ответа
if response.status_code == 200:
    result = response.json()
    print("Ответ от нейросети:", result["choices"][0]["message"]["content"])
else:
    print(f"Ошибка при отправке запроса: {response.status_code}")
    print("Тело ответа:", response.text)