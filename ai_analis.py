# Анализ чата между пациентом и врачом при помощи AI Qwen
import os
import json
import requests
import sqlite3

def connect_db():
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()
    return conn, cursor

# ...existing code...

def get_chat_messages_by_id(chat_id):
    """
    Получает сообщения чата по chat_id из таблицы chats.
    Возвращает список сообщений [{'role': 'doctor'/'patient', 'text': '...'}]
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT messages FROM chats WHERE id = ?", (chat_id,))
    row = cursor.fetchone()
    if not row:
        return []
    try:
        messages = json.loads(row[0])
    except Exception:
        messages = []
    return messages

def analyze_chat_by_id(chat_id):
    chat_messages = get_chat_messages_by_id(chat_id)
    if not chat_messages:
        return {"error": "Чат не найден или сообщений нет."}

    prompt = (
        "Проанализируй следующий диалог между пациентом и врачом. "
        "Оцени профессионализм и вежливость врача по шкале от 1 до 5 и дай краткий комментарий.\n\n"
        "Диалог:\n"
    )
    for msg in chat_messages:
        role = "Врач" if msg.get('sender') == 'doctor' else "Пациент"
        prompt += f"{role}: {msg.get('text', '')}\n"
    prompt += "\nОтвет в формате: Оценка: X. Комментарий: ..."

    url = "https://chat.qwenlm.ai/api/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjdlYTkwMTliLWI0OTgtNGZjMy1iZGEyLTk0OTVkOWY5NWQ2NSIsImV4cCI6MTc0ODk2NTM1Nn0._mbtE_49QgSO5JTVduj7WQcfhZPeIkEhesGyTHaNP70'}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-max-longcontext",  # или "qwen-turbo", "qwen-max", "qwen-max-longcontext"
        "input": {
            "prompt": prompt
        },
        "parameters": {
            "result_format": "text",
            "max_tokens": 200,
            "temperature": 0.7
        }
    }
    response = requests.post(url, headers=headers, json=data)
    print("HTTP status:", response.status_code)
    print("Raw response:", response.text)
    try:
        result = response.json()
    except Exception as e:
        return f"Ошибка разбора JSON: {e}, ответ: {response.text}"
    print("Ответ от Qwen API:", result)
    if "output" in result and "text" in result["output"]:
        return result["output"]["text"]
    else:
        return f"Ошибка: неожиданный ответ от API: {result}"
result = analyze_chat_by_id(chat_id=1)
print(result)