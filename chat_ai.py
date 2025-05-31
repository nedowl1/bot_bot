import requests

API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "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"  # ваш ключ

def chat_with_ai(messages, model="gpt-4o", max_tokens=500):
    """
    messages: список сообщений [{"role": "user"/"assistant"/"system", "content": "текст"}]
    model: модель OpenAI (по умолчанию gpt-4o)
    max_tokens: максимальное количество токенов в ответе
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Ошибка: {response.status_code} — {response.text}"
