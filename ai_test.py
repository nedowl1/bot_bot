import sqlite3
import json
import importlib
def connect_db():
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()
    return conn, cursor

def ai_audit_and_review(consultation_id):
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (consultation_id,))
    chat = cursor.fetchone()
    if not chat or not chat[4]:
        print("Нет сообщений для аудита")
        return
    messages = json.loads(chat[4])
    chat_text = ""
    for msg in messages:
        sender = "Врач" if msg.get("sender") == "doctor" else "Пациент"
        chat_text += f"{sender}: {msg.get('text','')}\n"
    ai_analis = importlib.import_module("ai_analis")
    ai_score, ai_summary = ai_analis.analyze_chat(chat_text)
    print(f"AI Оценка: {ai_score}, Резюме: {ai_summary}")

ai_audit_and_review(321350)  # Замените 1 на нужный ID консультации для теста