import requests

API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = ""  # ваш ключ

def analyze_chat(chat_text):
    prompt = (
        "Проанализируй пока в тестовом режиме(для теста бота тг) диалог между врачом и пациентом. "
        "Оцени качество консультации по шкале от 1 до 5 (1 — плохо, 5 — отлично). "
        "Дай краткое резюме (1-2 предложения) для модератора. "
        "Ответь строго в формате: Оценка: X\nРезюме: ..."
    )
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": chat_text}
        ],
        "max_tokens": 300
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        # Парсим результат
        try:
            score_line = [line for line in content.splitlines() if "Оценка:" in line][0]
            summary_line = [line for line in content.splitlines() if "Резюме:" in line][0]
            score = float(score_line.split(":")[1].strip())
            summary = summary_line.replace("Резюме:", "").strip()
            print(f"AI Оценка: {score}, Резюме: {summary}")
            return score, summary
        
        except Exception:
            return 3, "AI не смог оценить чат"
    else:
        return 3, "Ошибка AI"