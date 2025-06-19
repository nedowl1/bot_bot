import telebot
import sqlite3
#import qrcode
#import cloudpayments
from telebot import types
import random
import json
import os
import base64
import requests
import datetime
from datetime import datetime, timedelta
import time

TOKEN = "8156778620:AAFHqnTDYef3-qTlvOm9HY95bHFBiYAB4HQ"
#CLOUDPAYMENTS_PUBLIC_ID = "YOUR_PUBLIC_ID"
#CLOUDPAYMENTS_SECRET = "YOUR_SECRET_KEY"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = (2146048678, 935727305, 2107643694)  # Замените на ваш ID администратора
#ADMIN_ID = (935727305, 2107643694)
def connect_db():
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()
    return conn, cursor

       

@bot.message_handler(commands=['policy'])
def policy(message):
    bot.send_message(message.chat.id, text= "1️⃣ <a href='https://telegra.ph/Polzovatelskoe-soglashenie-06-18-14'>Пользовательским соглашением</a>\n\n"
        "2️⃣ <a href='https://telegra.ph/POLITIKA-KONFIDENCIALNOSTI-06-18-8'>Политикой конфиденциальности</a>\n\n"
        "3️⃣ <a href='https://telegra.ph/SOGLASIE-NA-OBRABOTKU-PERSONALNYH-DANNYH-06-18'>Согласие на обработку персональных данных</a>\n\n"
        "4️⃣ <a href='https://telegra.ph/OGRANICHENIE-OTVETSTVENNOSTI-DISKLEJMER-06-18'>Дисклеймер об ответственности.</a>\n\n"
        "5⃣ <a href='https://telegra.ph/OBYAZATELSTVO-O-SOHRANENII-VRACHEBNOJ-TAJNY-06-18'>ОБЯЗАТЕЛЬСТВО О СОХРАНЕНИИ ВРАЧЕБНОЙ ТАЙНЫ</a>\n\n"
        "6⃣ <a href='https://telegra.ph/SOGLASIE-NA-POLUCHENIE-REKLAMNOJ-I-INFORMACIONNOJ-RASSYLKI-06-18'>СОГЛАСИЕ НА ПОЛУЧЕНИЕ РЕКЛАМНОЙ И ИНФОРМАЦИОННОЙ РАССЫЛКИ</a>\n\n"
        "7⃣ <a href='https://telegra.ph/SOGLASHENIE-PRI-REGISTRACII-SPECIALISTA-06-18'>СОГЛАШЕНИЕ ПРИ РЕГИСТРАЦИИ СПЕЦИАЛИСТА</a>\n\n"
        "8⃣ <a href='https://telegra.ph/PUBLICHNAYA-OFERTA-O-ZAKLYUCHENII-DOGOVORA-S-PLATFORMOJ-06-18'>ПУБЛИЧНАЯ ОФЕРТА О ЗАКЛЮЧЕНИИ ДОГОВОРА С ПЛАТФОРМОЙ для специалистов (врачей, консультантов)</a>\n\n"
        "Индивидуальный предприниматель Колесников Александр Дмитриевич\n"
        "ИНН: 773701767759\n"
        "ОГРНИП: 325774600336521\n"
        "Email: sasha123011@gmail.com\n"
        "Telegram: @J_Milka",
            parse_mode="HTML")

@bot.message_handler(commands=['start'])
def start(message):
    if len(message.text.split()) > 1:
        # Если есть параметр после /start, например /start doc_123
        param = message.text.split()[1]
        if param.startswith("doc_"):
            user_id = int(param.split("_")[1])
            conn, cursor = connect_db()
            cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (user_id,))
            doctor = cursor.fetchone()
            if doctor:
                doc_card_1(message=message, call=2, doctor=doctor)
            else:
                bot.send_message(message.chat.id, "Доктор не найден.")
        else:
            bot.send_message(message.chat.id, "Неверный параметр.")
        return
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
    doctor = cursor.fetchone()
    cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
    patient = cursor.fetchone()
    print('doc',doctor)
    print('pat',patient)
    print(message.from_user.id)
    if doctor:
        profile_doc(message, call=message)
    elif patient:
        profile_pat(message, call=message)
    else:
        fl = 1
        polt_sogl(message, fl)

def polt_sogl(message, fl):    
    markup = types.InlineKeyboardMarkup()
    agree_button = types.InlineKeyboardButton(text='✅ Согласен', callback_data='agree_1' if fl==1 else 'agree_0')
    disagree_button = types.InlineKeyboardButton(text='❌ Не согласен', callback_data='disagree')
    rassilka_button = types.InlineKeyboardButton(text='✅Рассылки' if fl==1 else '❌Рассылки', callback_data='rassilka_on' if fl==1 else 'rassilka_off')
    markup.add(agree_button, disagree_button, rassilka_button)
    try:
        bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=(
            "Перед использованием бота, пожалуйста, ознакомьтесь с:\n\n"
            "1️⃣ [Пользовательским соглашением](https://telegra.ph/Polzovatelskoe-soglashenie-06-18-14)\n"
            "2️⃣ [Политикой конфиденциальности](https://telegra.ph/POLITIKA-KONFIDENCIALNOSTI-06-18-8)\n"
            "3️⃣ [Согласие на обработку персональных данных](https://telegra.ph/SOGLASIE-NA-OBRABOTKU-PERSONALNYH-DANNYH-06-18)\n"
            "4️⃣ [СОГЛАСИЕ НА ПОЛУЧЕНИЕ РЕКЛАМНОЙ И ИНФОРМАЦИОННОЙ РАССЫЛКИ](https://telegra.ph/SOGLASIE-NA-POLUCHENIE-REKLAMNOJ-I-INFORMACIONNOJ-RASSYLKI-06-18)"
            "5⃣ [Дисклеймер об ответственности](https://telegra.ph/OGRANICHENIE-OTVETSTVENNOSTI-DISKLEJMER-06-18).\n\n"
            "Нажимая \"Согласен\", вы подтверждаете, что ознакомились и принимаете условия."
        ),
        reply_markup=markup,
        parse_mode="Markdown"
    )
    except telebot.apihelper.ApiTelegramException as e:
        bot.send_message(message.chat.id,text=(
            "Перед использованием бота, пожалуйста, ознакомьтесь с:\n\n"
            "1️⃣ [Пользовательским соглашением](https://telegra.ph/Polzovatelskoe-soglashenie-06-18-14)\n"
            "2️⃣ [Политикой конфиденциальности](https://telegra.ph/POLITIKA-KONFIDENCIALNOSTI-06-18-8)\n"
            "3️⃣ [Согласие на обработку персональных данных](https://telegra.ph/SOGLASIE-NA-OBRABOTKU-PERSONALNYH-DANNYH-06-18)\n"
            "4️⃣ [Дисклеймер об ответственности](https://telegra.ph/OGRANICHENIE-OTVETSTVENNOSTI-DISKLEJMER-06-18).\n\n"
            "Нажимая \"Согласен\", вы подтверждаете, что ознакомились и принимаете условия."
        ),
        reply_markup=markup,
        parse_mode="Markdown"
    )

def start1(message,fl): 
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
    doctor = cursor.fetchone()
    cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
    patient = cursor.fetchone()
    print('doc',doctor)
    print('pat',patient)
    print(message.from_user.id)       
    marcup = types.InlineKeyboardMarkup(row_width=2)
    doc = types.InlineKeyboardButton(text="👨‍⚕️ Я доктор", callback_data=f"doctor_{fl}")
    pat = types.InlineKeyboardButton(text="🧑‍💼 Я пациент", callback_data=f"patient_{fl}")
    marcup.add(doc, pat)
    bot.send_message(message.chat.id, "👋 Добро пожаловать в сервис онлайн-консультаций!\n\n"
        "Здесь вы можете:\n"
        "— Найти врача по специальности\n"
        "— Получить консультацию\n"
        "— Общаться в чате и обмениваться файлами\n\n"
        "Пожалуйста, выберите вашу роль:", reply_markup=marcup)
    cursor.execute('''SELECT * FROM patients''')
    patients = cursor.fetchall()
    print('patients', patients)

def reg_doc_sogl(call, fl):
    markup = types.InlineKeyboardMarkup()
    agree_button = types.InlineKeyboardButton(text='✅ Согласен', callback_data=f'dagree_{fl}')
    disagree_button = types.InlineKeyboardButton(text='❌ Не согласен', callback_data='disagree')
    markup.add(agree_button, disagree_button)
    bot.send_message(call.message.chat.id, text="Перед регистрацией, ознакомтись пожалуйста с условиями для врачей\n\n"
                    '1⃣ [ОБЯЗАТЕЛЬСТВО О СОХРАНЕНИИ ВРАЧЕБНОЙ ТАЙНЫ](https://telegra.ph/OBYAZATELSTVO-O-SOHRANENII-VRACHEBNOJ-TAJNY-06-18)\n'
                    '2⃣ [СОГЛАШЕНИЕ ПРИ РЕГИСТРАЦИИ СПЕЦИАЛИСТА](https://telegra.ph/SOGLASHENIE-PRI-REGISTRACII-SPECIALISTA-06-18)\n'
                    '3⃣ [ПУБЛИЧНАЯ ОФЕРТА О ЗАКЛЮЧЕНИИ ДОГОВОРА С ПЛАТФОРМОЙ для специалистов (врачей, консультантов)](https://telegra.ph/PUBLICHNAYA-OFERTA-O-ZAKLYUCHENII-DOGOVORA-S-PLATFORMOJ-06-18)\n\n'
                    "Нажимая \"Согласен\", вы подтверждаете, что ознакомились и принимаете условия."
        ,
        reply_markup=markup,
        parse_mode="Markdown"
                     )

user_data = {}
def doc_reg(message, user_id, fl):
    user_data[user_id] = {}
    user_data[user_id]['rassilka'] = fl
    bot.send_message(message.chat.id, "Пожалуйста, введите ваше имя. Это поможет пациентам узнать вас.")
    bot.register_next_step_handler(message, get_doc_name)

def get_doc_name(message):
    user_data[message.from_user.id]['name'] = message.text
    bot.send_message(message.chat.id, "📞 Теперь введите ваш номер телефона:")
    bot.register_next_step_handler(message, get_doc_phone)
def get_doc_phone(message):
    user_data[message.from_user.id]['phone'] = message.text
    bot.send_message(message.chat.id, "✉️ Пожалуйста, введите ваш email.")
    bot.register_next_step_handler(message, get_doc_email)
def get_doc_email(message):
    user_data[message.from_user.id]['email'] = message.text
    bot.send_message(message.chat.id, f"🎉 Доктор успешно зарегистрирован!\n\n"
        f"👤 Имя: {user_data[message.from_user.id]['name']}\n"
        f"📞 Телефон: {user_data[message.from_user.id]['phone']}\n"
        f"✉️ Email: {user_data[message.from_user.id]['email']}\n\n"
        "✅ Следующий шаг — подтвердите документы для работы на платформе."
    )
    conn, cursor = connect_db()
    cursor.execute('''INSERT INTO doctors (user_id, name, phone, email, rassilka) VALUES (?, ?, ?, ?, ?)''', (
        message.from_user.id,
        user_data[message.from_user.id]['name'],
        user_data[message.from_user.id]['phone'],
        user_data[message.from_user.id]['email'],
        user_data[message.from_user.id]['rassilka']
    ))
    conn.commit()
    bot.send_message(message.chat.id, 
"📂 Для работы на платформе необходимо подтвердить документы.\n"
"Пожалуйста, прикрепите фото документов (например, диплома или сертификата).\n"
"👨‍⚕️ После успешной проверки вы получите бейдж «✅ Подтверждён» и сможете принимать пациентов."  
)
    print(user_data)
    print(cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,)).fetchall())
    profile_doc(message, call=message)

def pat_reg(message, call, fl):
    bot.send_message(message.chat.id, "🧑‍💼 Давайте зарегистрируем вас как пациента!\n\n"
        "Пожалуйста, введите ваше имя. Это поможет врачу обращаться к вам лично.")
    bot.register_next_step_handler(message, get_pat_name, fl)
def get_pat_name(message, fl):
    user_data[message.from_user.id] = {}
    user_data[message.from_user.id]['rassilka'] = fl
    user_data[message.from_user.id]['name'] = message.text
    bot.send_message(message.chat.id, "📞 Теперь введите ваш номер телефона.\n\n"
        "❗️ Мы не будем показывать его другим пользователям без вашего согласия.")
    bot.register_next_step_handler(message, get_pat_phone)
def get_pat_phone(message):
    user_data[message.from_user.id]['phone'] = message.text
    bot.send_message(message.chat.id, "✉️ Пожалуйста, введите ваш email.")
    bot.register_next_step_handler(message, get_pat_email)
def get_pat_email(message):
    user_data[message.from_user.id]['email'] = message.text
    bot.send_message(message.chat.id,  f"🎉 Регистрация завершена!\n\n"
        f"👤 Имя: {user_data[message.from_user.id]['name']}\n"
        f"📞 Телефон: {user_data[message.from_user.id]['phone']}\n"
        f"✉️ Email: {user_data[message.from_user.id]['email']}\n\n"
        "✅ Теперь вы можете выбрать врача и начать консультацию!"
    )
    con, cursor = connect_db()
    cursor.execute('''INSERT INTO patients (user_id, name, phone, email, rassilka) VALUES (?, ?, ?, ?, ?)''', (
        message.from_user.id,
        user_data[message.from_user.id]['name'],
        user_data[message.from_user.id]['phone'],
        user_data[message.from_user.id]['email'],
        user_data[message.from_user.id]['rassilka']
    ))
    con.commit()
    profile_pat(message, call=message)

def profile_doc(message, call):
    try:
        id = call.from_user.id
    except AttributeError:
        id = message.from_user.id
    conn, cursor = connect_db()
    cursor.execute('''SELECT verification_status, balance FROM doctors WHERE user_id = ?''', (id,))
    status_balance = cursor.fetchone()
    if not status_balance:
        bot.send_message(id, "Профиль не найден.")
        return
    status, balance = status_balance
    cursor.execute("""SELECT rassilka FROM doctors WHERE user_id = ?""", (id,))
    fl = cursor.fetchone()
    print('fl =', fl)
    # Кнопки профиля
    marcup = types.InlineKeyboardMarkup(row_width=2)
    doc = types.InlineKeyboardButton(text="📑 Пройти верификацию", callback_data="doc_verification")
    specif = types.InlineKeyboardButton(text="🩺 Выбрать специальность", callback_data="doc_spec")
    chats = types.InlineKeyboardButton(text="💬 Чаты", callback_data="doc_chats")
    edit = types.InlineKeyboardButton(text="✏️ Редактировать профиль", callback_data="edit_profile")
    link = types.InlineKeyboardButton(text="🔗 Ссылка на профиль", callback_data="doc_link")
    rass = types.InlineKeyboardButton(text= "❌Отказаться от рассылки" if fl[0]==1 else "✅Согл. на рассылку", callback_data="doc_off_rass" if fl[0]==1 else "doc_on_rass")
    

    if status == 'pending':
        marcup.add(doc, specif, edit, rass)
    elif status == 'verified':
        marcup.add(specif, chats, edit, link, rass)
    elif status == 'rejected':
        marcup.add(doc, edit, rass)

    cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (id,))
    doctor = cursor.fetchone()
    cursor.execute('''SELECT name_ru FROM specialisation WHERE user_id = ?''', (id,))
    specialization = cursor.fetchall()
    specialization = [spec[0] for spec in specialization]
    specialization_str = ', '.join(specialization) if specialization else "Не выбраны"

    # Статус верификации
    if doctor[8] == 'pending':
        verif_text = "⏳ На данный момент вы находитесь в процессе верификации. Пожалуйста, дождитесь подтверждения."
    elif doctor[8] == 'verified':
        verif_text = "✅ Ваш профиль подтверждён. Вы можете принимать пациентов!"
    elif doctor[8] == 'rejected':
        verif_text = "❌ Верификация не пройдена. Пожалуйста, проверьте документы и попробуйте снова."
    else:
        verif_text = "Статус верификации неизвестен."
    profile_text = (
        "👨‍⚕️ *Ваш профиль врача*\n\n"
        f"👤 Имя: {doctor[2]}\n"
        f"📞 Телефон: {doctor[4]}\n"
        f"✉️ Email: {doctor[5]}\n"
        f"💼 Статус: {verif_text}\n"
        f"💰 Баланс: {doctor[10]} руб.\n"
        f"🩺 Специализации: {specialization_str}\n"
    )
    if doctor[15]:
        profile_text = f"❌ВАШ ПРОФИЛЬ ЗАМОРОЖЕН❌\n\n Пожалуйста, обратитесь в поддержку для получения дополнительной информации.\nВаш id:{doctor[1]}\n Чат с поддержкой: @J_Milka"
    # Если есть аватар, отправляем с фото, иначе просто текст
    if doctor[3]:
        try:
            with open(doctor[3], 'rb') as photo:
                bot.send_photo(id, photo, caption=profile_text, reply_markup=marcup, parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка открытия фото: {e}")
            bot.send_message(id, text=profile_text, reply_markup=marcup, parse_mode="Markdown")
    else:
        bot.send_message(id, text=profile_text, reply_markup=marcup, parse_mode="Markdown")

def get_doc_link(call):
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (call.from_user.id,))
    doctor = cursor.fetchone()
    if not doctor:
        bot.send_message(call.message.chat.id, "Профиль не найден.")
        return
    # Генерируем ссылку на профиль
    profile_link = f"https://t.me/{bot.get_me().username}?start=doc_{doctor[1]}"
    bot.send_message(
        call.message.chat.id,
        f"🔗 Ваша ссылка на профиль: {profile_link}\n\n"
        "Вы можете делиться этой ссылкой с пациентами, чтобы они могли легко найти вас."
    )

@bot.message_handler(commands=['unfreeze'])
def unfreeze_doctor(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❗️ Только администратор может разблокировать аккаунты.")
        return
    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, "❗️ Пожалуйста, укажите ID доктора для разблокировки.")
        return
    try:
        doc_id = int(message.text.split()[1])
    except ValueError:
        bot.send_message(message.chat.id, "❗️ Неверный формат ID. Пожалуйста, укажите числовой ID доктора.")
        return
    conn, cursor = connect_db()
    cursor.execute('''UPDATE doctors SET is_frozen = 0, ignore_count = 0 WHERE user_id = ?''', (doc_id,))
    conn.commit()
    bot.send_message(doc_id, "✅ Ваш аккаунт разблокирован администрацией. Вы снова можете принимать пациентов.")
    bot.send_message(message.chat.id, "Доктор разблокирован.")

def doc_consultations(call):
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM consultations WHERE doctor_id = ? AND status = ?''', (call.from_user.id, 'pending'))
    consultations = cursor.fetchall()
    if not consultations:
        bot.send_message(
            call.message.chat.id,
            "📋 У вас нет новых запросов на консультации."
        )
        return
    marcup = types.InlineKeyboardMarkup(row_width=1)
    for consultation in consultations:
        patient_name = consultation[2]
        consult_id = consultation[0]
        button_text = f"Запрос от {patient_name} (ID: {consult_id})"
        marcup.add(types.InlineKeyboardButton(text=button_text, callback_data=f"consultat_{consult_id}"))
    bot.send_message(
        call.message.chat.id,
        "📋 *Новые запросы на консультации:*\n\n"
        "Выберите запрос, чтобы просмотреть детали и ответить.",
        reply_markup=marcup,
        parse_mode="Markdown"
    )
    
#верификация

def doc_verification(message, call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(
            "📂 Для подтверждения профиля, пожалуйста, отправьте фото ваших документов (например, диплома или сертификата).\n\n"
            "❗️ Документы нужны для проверки вашей квалификации. Мы не передаём их третьим лицам.\n"
            "После успешной проверки вы получите бейдж «✅ Подтверждён» и сможете принимать пациентов."
        )
    )
    bot.register_next_step_handler(message, get_doc_verification)

def get_doc_verification(message):
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'verification_docs/{message.from_user.id}.jpg'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        conn, cursor = connect_db()
        cursor.execute(
            '''UPDATE doctors SET verification_status = ?, verification_docs = ? WHERE user_id = ?''',
            ('pending', src, message.from_user.id)
        )
        conn.commit()
        bot.send_message(
            message.chat.id,
            "✅ Документы успешно отправлены на проверку!\n\n"
            "⏳ Обычно проверка занимает не более 24 часов. "
            "Мы уведомим вас, когда профиль будет подтверждён или если потребуется повторная загрузка документов."
        )
        bot.send_message(
            ADMIN_ID,
            f"🆕 Новый запрос на верификацию от пользователя {message.from_user.id}."
        )
    else:
        bot.send_message(
            message.chat.id,
            "❗️ Пожалуйста, отправьте именно фото документов. Попробуйте ещё раз."
        )
        bot.register_next_step_handler(message, get_doc_verification)

def get_doc_spec(message, call):
    conn, cursor = connect_db()
    cursor.execute('''SELECT name FROM specialisation WHERE user_id = ?''', (call.from_user.id,))
    specialization = cursor.fetchall()
    specialization = [spec[0] for spec in specialization]

    marcup = types.InlineKeyboardMarkup(row_width=3)  # <-- row_width=3 для трёх столбцов
    spec_buttons = [
        ("therapist", "Терапевт"),
        ("family", "Семейный врач"),
        ("pediatrician", "Педиатр"),
        ("cardiologist", "Кардиолог"),
        ("gastroenterologist", "Гастроэнтеролог"),
        ("endocrinologist", "Эндокринолог"),
        ("neurologist", "Невролог"),
        ("allergist_immunologist", "Аллерголог-иммунолог"),
        ("dermatologist", "Дерматолог"),
        ("psychotherapist", "Психотерапевт"),
        ("gynecologist", "Гинеколог"),
        ("ophthalmologist", "Офтальмолог"),
        ("dentist", "Стоматолог"),
        ("psychiatrist", "Психиатр"),
    ]
    # Группируем кнопки по 3 в ряд
    row = []
    for code, label in spec_buttons:
        text = f"✅ {label}" if code in specialization else label
        row.append(types.InlineKeyboardButton(text=text, callback_data=code))
        if len(row) == 3:
            marcup.add(*row)
            row = []
    if row:
        marcup.add(*row)
    done = types.InlineKeyboardButton(text="Готово", callback_data="done")
    marcup.add(done)

    help_text = (
        "🩺 *Выберите ваши специализации*\n\n"
        "Выберите одну или несколько специализаций, по которым вы готовы консультировать пациентов. "
        "Нажмите на нужные направления — выбранные будут отмечены галочкой.\n\n"
        "Когда закончите, нажмите «Готово»."
    )

    try:
        bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=help_text,
        reply_markup=marcup,
        parse_mode="Markdown"
    )
    except telebot.apihelper.ApiTelegramException as e:
    # Если не получилось отредактировать (например, сообщение было фото) — просто отправляем новое сообщение
        if "there is no text in the message to edit" in str(e):
            bot.send_message(
            call.message.chat.id,
            help_text,
            reply_markup=marcup,
            parse_mode="Markdown"
        )
        else:
            raise

def get_price(message, call):
    conn, cursor = connect_db()
    cursor.execute('''SELECT name FROM specialisation WHERE user_id = ?''', (call.from_user.id,))
    specialization = cursor.fetchall()
    specialization = [spec[0] for spec in specialization]
    special = []
    for spec in specialization:
        if spec == 'therapist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Терапевт', call.from_user.id, spec))
        elif spec == 'family':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Семейный врач', call.from_user.id, spec))
        elif spec == 'pediatrician':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Педиатр', call.from_user.id, spec))
        elif spec == 'cardiologist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Кардиолог', call.from_user.id, spec))
        elif spec == 'gastroenterologist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Гастроэнтеролог', call.from_user.id, spec))
        elif spec == 'endocrinologist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Эндокринолог', call.from_user.id, spec))
        elif spec == 'neurologist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Невролог', call.from_user.id, spec))
        elif spec == 'allergist_immunologist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Аллерголог-иммунолог', call.from_user.id, spec))
        elif spec == 'dermatologist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Дерматолог', call.from_user.id, spec))
        elif spec == 'psychotherapist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Психотерапевт', call.from_user.id, spec))
        elif spec == 'gynecologist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Гинеколог', call.from_user.id, spec))
        elif spec == 'ophthalmologist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Офтальмолог', call.from_user.id, spec))
        elif spec == 'dentist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Стоматолог', call.from_user.id, spec))
        elif spec == 'psychiatrist':
            cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ? AND name = ?''', ('Психиатр', call.from_user.id, spec))
        conn.commit()
    cursor.execute('''SELECT name_ru FROM specialisation WHERE user_id = ?''', (call.from_user.id,))
    specialization = cursor.fetchall()
    print(specialization)
    # Преобразуем список кортежей в список строк
    specialization = [spec[0] for spec in specialization]
    # Преобразуем список строк в строку с разделителем
    specialization = ', '.join(specialization)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Вы выбрали {specialization}", reply_markup=None)
    get_price_value(message=message)
def get_price_value(message):
    bot.send_message(
        message.chat.id,
        "💰 Введите стоимость консультации для каждого выбранного направления через запятую.\n\n"
        "Например: 1000,2000,3000\n"
        "Порядок цен должен соответствовать порядку выбранных специализаций."
    )
    bot.register_next_step_handler(message, get_price_value_2)

def get_price_value_2(message):
    prices = message.text.split(',')
    conn, cursor = connect_db()
    cursor.execute('''SELECT name FROM specialisation WHERE user_id = ?''', (message.from_user.id,))
    specialization = cursor.fetchall()
    specialization = [spec[0] for spec in specialization]
    try:
        for i in range(len(specialization)):
            cursor.execute(
                '''UPDATE specialisation SET price = ? WHERE user_id = ? AND name = ?''',
                (prices[i], message.from_user.id, specialization[i])
            )
            conn.commit()
        bot.send_message(
            message.chat.id,
            "✅ Стоимость успешно обновлена для всех направлений!\n\n"
            "Теперь ваш профиль полностью готов к приёму пациентов."
        )
        pr = cursor.execute('''SELECT name, price FROM specialisation WHERE user_id = ?''', (message.from_user.id,)).fetchall()
        print(pr)
        profile_doc(message, call=message)
    except IndexError:
        bot.send_message(
            message.chat.id,
            "❗️ Ошибка: количество цен не соответствует количеству выбранных направлений.\n"
            "Пожалуйста, попробуйте снова и убедитесь, что ввели цену для каждого направления."
        )
        get_price_value(message)
    

def edit_profile(message, call):
    marcup = types.InlineKeyboardMarkup(row_width=2)
    name = types.InlineKeyboardButton(text="📝 Изменить имя", callback_data="name")
    phone = types.InlineKeyboardButton(text="📞 Изменить номер телефона", callback_data="phone")
    email = types.InlineKeyboardButton(text="✉️ Изменить email", callback_data="email")
    discription = types.InlineKeyboardButton(text="ℹ️ Изм./добавить описание", callback_data="description")
    avatar = types.InlineKeyboardButton(text="🖼️ Изменить аватар", callback_data="avatar")
    marcup.add(name, phone)
    marcup.add(email, discription, avatar)
    bot.send_message(
        chat_id=call.message.chat.id,
        text=(
            "🔧 *Редактирование профиля*\n\n"
            "Выберите, что вы хотите изменить. После внесения изменений вы сразу увидите обновлённый профиль."
        ),
        reply_markup=marcup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data in ["name", "phone", "email", "description", "avatar"])
def edit_profile1(call):
    bot.answer_callback_query(call.id)
    if call.data == "name":
        bot.send_message(
            call.message.chat.id,
            "✏️ Введите новое имя.\n\n"
            "Пожалуйста, укажите, как вы хотите, чтобы вас видели пациенты."
        )
        bot.register_next_step_handler(call.message, get_new_name)
    elif call.data == "phone":
        bot.send_message(
            call.message.chat.id,
            "📞 Введите новый номер телефона.\n\n"
            "Убедитесь, что номер актуален — на него могут приходить важные уведомления."
        )
        bot.register_next_step_handler(call.message, get_new_phone)
    elif call.data == "email":
        bot.send_message(
            call.message.chat.id,
            "✉️ Введите новый email.\n\n"
            "Проверьте правильность адреса."
        )
        bot.register_next_step_handler(call.message, get_new_email)
    elif call.data == "description":
        bot.send_message(
            call.message.chat.id,
            "ℹ️ Введите новое описание.\n\n"
            "Расскажите о себе, опыте и подходе к работе — это поможет пациентам выбрать именно вас."
        )
        bot.register_next_step_handler(call.message, get_new_description)
    elif call.data == "avatar":
        bot.send_message(
            call.message.chat.id,
            "🖼️ Отправьте новое фото профиля.\n\n"
            "Это поможет пациентам лучше узнать вас."
        )
        bot.register_next_step_handler(call.message, get_new_avatar)
    

def get_new_name(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE doctors SET name = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(
        message.chat.id,
        "✅ Имя успешно изменено!\n\n"
        "Ваш профиль обновлён."
    )
    profile_doc(message, call=message)

def get_new_phone(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE doctors SET phone = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(
        message.chat.id,
        "✅ Номер телефона успешно изменён!\n\n"
        "Ваш профиль обновлён."
    )
    profile_doc(message, call=message)

def get_new_email(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE doctors SET email = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(
        message.chat.id,
        "✅ Email успешно изменён!\n\n"
        "Ваш профиль обновлён."
    )
    profile_doc(message, call=message)

def get_new_description(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE doctors SET description = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(
        message.chat.id,
        "✅ Описание успешно изменено!\n\n"
        "Ваш профиль обновлён."
    )
    profile_doc(message, call=message)

def get_new_avatar(message):
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'avatars/{message.from_user.id}.jpg'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        conn, cursor = connect_db()
        cursor.execute('''UPDATE doctors SET avatar = ? WHERE user_id = ?''', (src, message.from_user.id))
        conn.commit()
        bot.send_message(
            message.chat.id,
            "✅ Аватар успешно изменён!\n\n"
            "Ваш профиль обновлён."
        )
        profile_doc(message, call=message)
    else:
        bot.send_message(
            message.chat.id,
            "❗️ Пожалуйста, отправьте именно фото аватара. Попробуйте ещё раз."
        )
        bot.register_next_step_handler(message, get_new_avatar)

def profile_pat(message, call):
    conn, cursor = connect_db()
    
    try:
        id = call.from_user.id
    except AttributeError:
        id = message.from_user.id
    cursor.execute("""SELECT rassilka FROM patients WHERE user_id = ?""", (id,))
    fl = cursor.fetchone()
    marcup = types.InlineKeyboardMarkup(row_width=2)
    doc = types.InlineKeyboardButton(text="👨‍⚕️ Записаться к врачу", callback_data="doc_reg")
    chats = types.InlineKeyboardButton(text="💬 Чаты", callback_data="pat_chats")
    edit_profile = types.InlineKeyboardButton(text="✏️ Редактировать профиль", callback_data="edit_profile_pat")
    rass = types.InlineKeyboardButton(text= "❌Отказаться от рассылки" if fl[0]==1 else "✅Согл. на рассылку", callback_data="pat_off_rass" if fl[0]==1 else "pat_on_rass")
    marcup.add(doc, chats, edit_profile)
    
    cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (id,))
    patient = cursor.fetchone()
    # Проверяем, есть ли аватар

    if patient:
        profile_text = (
            "🧑‍💼 *Ваш профиль пациента*\n\n"
            f"👤 Имя: {patient[2]}\n"
            f"📞 Телефон: {patient[4]}\n"
            f"✉️ Email: {patient[5]}\n\n"
            "Выберите действие:"
        )
        # Если есть аватар, отправляем с фото, иначе просто текст
        if patient[3]:
            try:
                with open(patient[3], 'rb') as photo:
                    bot.send_photo(id, photo, caption=profile_text, reply_markup=marcup, parse_mode="Markdown")
            except Exception as e:
                print(f"Ошибка открытия фото: {e}")
                bot.send_message(id, text=profile_text, reply_markup=marcup, parse_mode="Markdown")
        else:
            bot.send_message(id, text=profile_text, reply_markup=marcup, parse_mode="Markdown")

def edit_profile_pat(call):
    marcup = types.InlineKeyboardMarkup(row_width=2)
    name = types.InlineKeyboardButton(text="📝 Изменить имя", callback_data="pat_name")
    phone = types.InlineKeyboardButton(text="📞 Изменить номер телефона", callback_data="pat_phone")
    email = types.InlineKeyboardButton(text="✉️ Изменить email", callback_data="pat_email")
    avatar = types.InlineKeyboardButton(text="🖼️ Изменить аватар", callback_data="pat_avatar")
    marcup.add(name, phone, email, avatar)
    bot.send_message(
        call.message.chat.id,
        text=(
            "🔧 *Редактирование профиля*\n\n"
            "Выберите, что вы хотите изменить. После внесения изменений вы сразу увидите обновлённый профиль."
        ),
        reply_markup=marcup,
        parse_mode="Markdown"
    )
@bot.callback_query_handler(func=lambda call: call.data in ["pat_name", "pat_phone", "pat_email", "pat_avatar"])
def edit_profile_pat1(call):
    bot.answer_callback_query(call.id)
    if call.data == "pat_name":
        bot.send_message(
            call.message.chat.id,
            "✏️ Введите новое имя.\n\n"
            "Пожалуйста, укажите, как вы хотите, чтобы вас видели врачи."
        )
        bot.register_next_step_handler(call.message, get_new_pat_name)
    elif call.data == "pat_phone":
        bot.send_message(
            call.message.chat.id,
            "📞 Введите новый номер телефона.\n\n"
            "Убедитесь, что номер актуален — на него могут приходить важные уведомления."
        )
        bot.register_next_step_handler(call.message, get_new_pat_phone)
    elif call.data == "pat_email":
        bot.send_message(
            call.message.chat.id,
            "✉️ Введите новый email.\n\n"
            "Проверьте правильность адреса."
        )
        bot.register_next_step_handler(call.message, get_new_pat_email)
    elif call.data == "pat_avatar":
        bot.send_message(
            call.message.chat.id,
            "🖼️ Отправьте новое фото профиля.\n\n"
            "Это поможет врачам лучше узнать вас."
        )
        bot.register_next_step_handler(call.message, get_new_pat_avatar)

def get_new_pat_name(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE patients SET name = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(
        message.chat.id,
        "✅ Имя успешно изменено!\n\n"
        "Ваш профиль обновлён."
    )
    profile_pat(message, call=message)
def get_new_pat_phone(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE patients SET phone = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(
        message.chat.id,
        "✅ Номер телефона успешно изменён!\n\n"
        "Ваш профиль обновлён."
    )
    profile_pat(message, call=message)
def get_new_pat_email(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE patients SET email = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(
        message.chat.id,
        "✅ Email успешно изменён!\n\n"
        "Ваш профиль обновлён."
    )
    profile_pat(message, call=message)
def get_new_pat_avatar(message):
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'avatars/{message.from_user.id}.jpg'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        conn, cursor = connect_db()
        cursor.execute('''UPDATE patients SET avatar = ? WHERE user_id = ?''', (src, message.from_user.id))
        conn.commit()
        bot.send_message(
            message.chat.id,
            "✅ Аватар успешно изменён!\n\n"
            "Ваш профиль обновлён."
        )
        profile_pat(message, call=message)
    else:
        bot.send_message(
            message.chat.id,
            "❗️ Пожалуйста, отправьте именно фото аватара. Попробуйте ещё раз."
        )
        bot.register_next_step_handler(message, get_new_pat_avatar)

def doc_list(message, call):
    marcup = types.InlineKeyboardMarkup(row_width=3)
    spec1 = types.InlineKeyboardButton(text="Терапевт", callback_data="therapist_doc")
    spec2 = types.InlineKeyboardButton(text="Семейный врач", callback_data="family_doc")
    spec3 = types.InlineKeyboardButton(text="Педиатр", callback_data="pediatrician_doc")
    spec4 = types.InlineKeyboardButton(text="Кардиолог", callback_data="cardiologist_doc")
    spec5 = types.InlineKeyboardButton(text="Гастроэнтеролог", callback_data="gastroenterologist_doc")
    spec6 = types.InlineKeyboardButton(text="Эндокринолог", callback_data="endocrinologist_doc")
    spec7 = types.InlineKeyboardButton(text="Невролог", callback_data="neurologist_doc")
    spec8 = types.InlineKeyboardButton(text="Аллерголог-иммунолог", callback_data="allergist_immunologist_doc")
    spec9 = types.InlineKeyboardButton(text="Дерматолог", callback_data="dermatologist_doc")
    spec10 = types.InlineKeyboardButton(text="Психотерапевт", callback_data="psychotherapist_doc")
    spec11 = types.InlineKeyboardButton(text="Гинеколог", callback_data="gynecologist_doc")
    spec12 = types.InlineKeyboardButton(text="Офтальмолог", callback_data="ophthalmologist_doc")
    spec13 = types.InlineKeyboardButton(text="Стоматолог", callback_data="dentist_doc")
    spec14 = types.InlineKeyboardButton(text="Психиатр", callback_data="psychiatrist_doc")
    marcup.add(spec1, spec2, spec3, spec4, spec5, spec6, spec7, spec8, spec9, spec10, spec11, spec12, spec13, spec14)
    bot.send_message(
    chat_id=call.message.chat.id,
    text=(
        "🩺 *Выберите направление*\n\n"
        "Пожалуйста, выберите специальность врача, к которому хотите записаться. "
        "Вы можете посмотреть подробную информацию о каждом специалисте после выбора.\n\n"
        "Нажмите на нужное направление:"
    ),
    reply_markup=marcup,
    parse_mode="Markdown"
)

def get_doc(message, call, filters, flag, msg, id):
    doctor = []
    conn, cursor = connect_db()
    spec = cursor.execute('''SELECT spec FROM patients WHERE user_id = ?''', (call.from_user.id,)).fetchone()
    print(spec)
    cursor.execute('''SELECT user_id FROM specialisation WHERE name = ?''', (spec))
    doctors_ids = cursor.fetchall()
    
    print(spec)
    print(doctors_ids)
    doctors_ids = [doctor[0] for doctor in doctors_ids]
    print(doctors_ids)
    cursor.execute('''SELECT filter FROM patients WHERE user_id = ?''', (id,))
    filters = cursor.fetchone()
    filters= int(filters[0])
    print('filters', filters)
    if doctors_ids:
        for doctor_id in doctors_ids:
            print(doctor_id)
            cursor.execute('''SELECT * FROM doctors WHERE verification_status = 'verified' AND (is_frozen IS NULL OR is_frozen = 0)''')
            doctor += cursor.fetchall()
        print(doctor)
        doctor = sorted(doctor, key=lambda x: x[filters], reverse=True)
        print(doctor)
        print(len(doctor))
    if flag:
        doc_card(message, call, doctor, msg)
        flag = False
    else:
        doctors(message, call, doctor)

def doctors(message, call, doctor):
    conn, cursor = connect_db()
    if len(doctor) == 0:
        bot.send_message(message.chat.id, "❗️ Врачи по выбранному направлению не найдены.\n\nПопробуйте выбрать другую специальность или вернитесь в меню.")
    else:
        marcup = types.InlineKeyboardMarkup(row_width=3)
        sort1 = types.InlineKeyboardButton(text="⭐️ По рейтингу", callback_data="sort1")
        sort2 = types.InlineKeyboardButton(text="💰 По цене", callback_data="sort2")
        sort3 = types.InlineKeyboardButton(text="🎓 По опыту", callback_data="sort3")
        back = types.InlineKeyboardButton(text="⬅️ Назад", callback_data="doc_reg")
        marcup.add(sort1, sort2, sort3)
        marcup.add(back)
        # Создаем красивый текст для отправки
        text = "👨‍⚕️ *Список врачей*\n\n"
        for idx, doc in enumerate(doctor, 1):
            text += (
                f"*{idx}. {doc[2]}*\n"
                f"— 🏅 Рейтинг: {doc[10]}\n"
                f"— 🎓 Стаж: {doc[11]} лет\n"
                f"— 💬 Подробнее: выберите врача для просмотра профиля\n\n"
            )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=marcup,
            parse_mode="Markdown"
        )


def doc_card(message, call, doctor, msg):
    msg = int(msg) - 1
    conn, cursor = connect_db()
    try:
        msg = int(msg) - 1
        doc_info = doctor[msg]
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "❗️ Ошибка: некорректный номер врача. Пожалуйста, попробуйте снова.")
        return
    except TypeError:
        doc_info = doctor
    cursor.execute('''SELECT * FROM specialisation WHERE user_id = ?''', (doc_info[1],))
    specializations = cursor.fetchall()
    marcup = types.InlineKeyboardMarkup(row_width=2)
    back = types.InlineKeyboardButton(text="⬅️ Назад", callback_data="doc_reg")
    consult = types.InlineKeyboardButton(text="📝 Записаться на консультацию", callback_data=f"consult_{doc_info[1]}")
    marcup.add(consult, back)

    # Формируем красивую карточку
    spec_text = ""
    for spec in specializations:
        spec_text += f"🩺 {spec[3]}\n💰 Цена: {spec[4]} руб.\n\n"

    card_text = (
        f"👨‍⚕️ *Профиль врача*\n\n"
        f"👤 Имя: {doc_info[2]}\n"
        f"🎓 Стаж: {doc_info[11]} лет\n"
        f"🏅 Рейтинг: {doc_info[10]}\n"
        f"{spec_text}"
        f"ℹ️ Подробнее: выберите «Записаться на консультацию», чтобы отправить заявку врачу."
    )

    # Если есть фото — отправляем с фото, иначе просто текст
    if doc_info[3]:
        try:
            with open(doc_info[3], 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=card_text, reply_markup=marcup, parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка открытия фото: {e}")
            bot.send_message(message.chat.id, text=card_text, reply_markup=marcup, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, text=card_text, reply_markup=marcup, parse_mode="Markdown")
    
# Функция для создания карточки врача с кнопкой записи на консультацию по его специализациям
def doc_card_1(message, call, doctor):
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM specialisation WHERE user_id = ?''', (doctor[1],))
    specializations = cursor.fetchall()
    marcup = types.InlineKeyboardMarkup(row_width=2)
    # Кнопка теперь вызывает выбор специализации
    consult = types.InlineKeyboardButton(text="📝 Записаться на консультацию", callback_data=f"choose_spec_{doctor[1]}")
    back = types.InlineKeyboardButton(text="⬅️ Назад", callback_data="doc_reg")
    marcup.add(consult, back)

    spec_text = ""
    for spec in specializations:
        spec_text += f"🩺 {spec[3]}\n💰 Цена: {spec[4]} руб.\n\n"

    card_text = (
        f"👨‍⚕️ *Профиль врача*\n\n"
        f"👤 Имя: {doctor[2]}\n"
        f"🎓 Стаж: {doctor[11]} лет\n"
        f"🏅 Рейтинг: {doctor[10]}\n"
        f"{spec_text}"
        f"ℹ️ Нажмите «Записаться на консультацию», чтобы выбрать специализацию."
    )

    if doctor[3]:
        try:
            with open(doctor[3], 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=card_text, reply_markup=marcup, parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка открытия фото: {e}")
            bot.send_message(message.chat.id, text=card_text, reply_markup=marcup, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, text=card_text, reply_markup=marcup, parse_mode="Markdown")




def get_consultation_date(message):
    id_consult = random.randint(100000, 999999)
    marcup = types.InlineKeyboardMarkup(row_width=2)
    approve = types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve{id_consult}")
    cancel = types.InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel{id_consult}")
    marcup.add(approve, cancel)
    conn, cursor = connect_db()
    cursor.execute('''SELECT data FROM temporary_data WHERE user_id = ?''', (message.from_user.id,))
    doctor_id = cursor.fetchone()
    cursor.execute('''SELECT name FROM patients WHERE user_id = ?''', (message.from_user.id,))
    name = cursor.fetchone()
    name = name[0] if name else "Пациент"
    if doctor_id:
        doctor_id = doctor_id[0]
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (doctor_id,))
        doctor = cursor.fetchone()
        if doctor:
            bot.send_message(
                message.chat.id,
                f"📝 Вы записаны на консультацию к врачу *{doctor[2]}*.\n"
                f"Ваше сообщение: {message.text}\n\n"
                "Пожалуйста, дождитесь подтверждения от врача. "
                
            )
            bot.send_message(
                doctor_id,
                f"👨‍⚕️ Новый запрос на консультацию!\n"
                f"Пациент: {message.from_user.id}\n"
                f"Имя пациента: {name}\n"
                f"Сообщение: {message.text}\n\n"
                "Пожалуйста, подтвердите или отклоните заявку.",
                reply_markup=marcup
            )
            total_price = cursor.execute('''SELECT price FROM specialisation WHERE user_id = ?''', (doctor_id,)).fetchone()
            total_price = total_price[0]
            cursor.execute(
                '''INSERT INTO consultations (identifier, doctor_id, patient_id, description, total_price, created_at) VALUES (?, ?, ?, ?, ?, ?)''',
                (id_consult, doctor_id, message.from_user.id, message.text, total_price, datetime.now())
            )
            conn.commit()
            cursor.execute('''DELETE FROM temporary_data WHERE user_id = ?''', (message.from_user.id,))
            conn.commit()
        else:
            bot.send_message(message.chat.id, "❗️ Врач не найден.")
    else:
        bot.send_message(message.chat.id, "❗️ Ошибка получения данных врача.")

def finish_consultation(message):
    conn, cursor = connect_db()
    cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
    active_chat_id = cursor.fetchone()
    if not active_chat_id:
        bot.send_message(message.chat.id, "Нет активной консультации.")
        return
    active_chat_id = active_chat_id[0]
    cursor.execute('''UPDATE consultations SET status = ?, finished_at = ? WHERE identifier = ?''',
                   ('completed', datetime.now(), active_chat_id))
    conn.commit()
    bot.send_message(message.chat.id, "Приём завершён. В течение 14 дней вы можете получить обратную связь от врача.")

def show_followup_button(call, consultation):
    finished_at = consultation[9]  # finished_at
    followup_ping = consultation[10]  # followup_ping
    if finished_at and followup_ping == 0:
        if datetime.now() - datetime.fromisoformat(finished_at) < timedelta(days=14):
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("Запросить обратную связь", callback_data=f"followup_{consultation[1]}")
            markup.add(btn)
            bot.send_message(call.message.chat.id, "Вы можете запросить обратную связь у пациента.", reply_markup=markup)

from chat_ai import chat_with_ai

@bot.message_handler(commands=['ai'])
def ai_chat_handler(message):
    user_text = message.text.replace('/ai', '').strip()
    if not user_text:
         bot.send_message(message.chat.id, "Напишите вопрос после /ai")
         return
    messages = [
        {"role": "system", "content": "Ты медицинский ассистент."},
        {"role": "user", "content": user_text}
    ]
    bot.send_chat_action(message.chat.id, 'typing')
    answer = chat_with_ai(messages)
    bot.send_message(message.chat.id, answer)

import requests
import base64

CLOUDPAYMENTS_PUBLIC_ID = "ВАШ_PUBLIC_ID"
CLOUDPAYMENTS_SECRET = "ВАШ_SECRET_KEY"
CLOUDPAYMENTS_API_URL = "https://api.cloudpayments.ru/"

def calculate_commission(price, has_subscription=False):
    # Комиссия делится пополам между врачом и пациентом
    if has_subscription:
        percent = 0.05
        limit = 150
    else:
        percent = 0.10
        limit = 500
    commission = min(price * percent, limit)
    return commission

def create_cloudpayments_invoice(consultation_id):
    conn, cursor = connect_db()
    # Получаем данные консультации
    cursor.execute('''SELECT patient_id, doctor_id, total_price FROM consultations WHERE identifier = ?''', (consultation_id,))
    row = cursor.fetchone()
    print('row', row)
    if not row:
        return None
    patient_id, doctor_id, price = row
    print('id', patient_id)
    # Получаем email пациента
    cursor.execute('''SELECT email FROM patients WHERE user_id = ?''', (patient_id,))
    patient_email = cursor.fetchone()
    print('patient_email', patient_email)

    # Получаем email врача (если нужно)
    # cursor.execute('''SELECT email FROM doctors WHERE id = ?''', (doctor_id,))
    # doctor_email = cursor.fetchone()[0]

    # Проверяем подписку (пример, если есть поле subscription)
    # cursor.execute('''SELECT subscription FROM patients WHERE id = ?''', (patient_id,))
    # has_subscription = cursor.fetchone()[0] == 1
    has_subscription = False  # пока всегда False

    commission = calculate_commission(price, has_subscription)
    total_for_patient = price + commission / 2  # Пациент платит половину комиссии сверху

    # Формируем запрос к CloudPayments
    url = CLOUDPAYMENTS_API_URL + "payments/charge"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLOUDPAYMENTS_PUBLIC_ID}:{CLOUDPAYMENTS_SECRET}".encode()).decode()
    }
    data = {
        "Amount": total_for_patient,
        "Currency": "RUB",
        "Description": f"Консультация #{consultation_id}",
        "InvoiceId": consultation_id,
        "AccountId": patient_email,
        "Email": patient_email
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def send_invoice_to_patient(consultation_id, chat_id):
    invoice = create_cloudpayments_invoice(consultation_id)
    if invoice and invoice.get("Success"):
        payment_url = invoice["Model"].get("Url", "https://pay.cloudpayments.ru/")
        bot.send_message(chat_id, f"Оплатите консультацию по ссылке: {payment_url}")
        # В базе: payment_status = 'pending_payment'
        conn, cursor = connect_db()
        cursor.execute('''UPDATE consultations SET payment_status = ? WHERE identifier = ?''', ('pending_payment', consultation_id))
        conn.commit()
    else:
        bot.send_message(chat_id, "Ошибка создания платежа. Попробуйте позже.")

def create_chat(message, call):
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (call.data.replace("approve", ""),))
    consultation = cursor.fetchone()
    if consultation:
        cursor.execute('''INSERT INTO chats (consultation_id, doctor_id, patient_id) VALUES (?, ?, ?)''', (consultation[1], consultation[3], consultation[2]))
        conn.commit()
        bot.send_message(consultation[2], "Чат создан.")
        bot.send_message(consultation[3], "Чат создан.")
        # Здесь можно добавить логику для создания чата
    else:
        bot.send_message(call.message.id, "❗️ Произошла ошибка. Пожалуйста, попробуйте ещё раз или обратитесь в поддержку.")

def chats(message, call):
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM chats WHERE doctor_id = ? OR patient_id = ?''', (call.from_user.id, call.from_user.id))
    chats = cursor.fetchall()
    marcup = types.InlineKeyboardMarkup(row_width=2)
    for chat in chats:
        chat_id = chat[0]
        consultation_id = chat[1]
        cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (consultation_id,))
        consultation = cursor.fetchone()
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (consultation[3],))
        doctor = cursor.fetchone()
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (consultation[2],))
        patient = cursor.fetchone()
        print('chat', chat)
        print('consultation', consultation)
        print('doctor', doctor)
        print('patient', patient)
        if consultation:
            chat_button = types.InlineKeyboardButton(text=f"Чат с {patient[2] if call.data == 'doc_chats' else doctor[2]}", callback_data=f"chat_{chat[1]}_1" if call.data == 'doc_chats' else f"chat_{chat[1]}_2")
            marcup.add(chat_button)
    back = types.InlineKeyboardButton(text="Назад", callback_data=f"{'back_doc'if call.data == 'doc_chats' else 'back_pat'}")
    marcup.add(back)
    print('chats', chats)
    #выводим список чатов
    if len(chats) == 0:
        bot.send_message(message.chat.id, "💬 Чаты не найдены.\n\nВы пока не участвовали в консультациях. После записи к врачу здесь появится ваш чат.")
    else:
        text = "💬 *Ваши чаты*\n\n"
    for chat in chats:
        cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (chat[1],))
        consultation = cursor.fetchone()
        if consultation:
            text += f"🗂 Консультация: {consultation[1]}\n"
            text += f"🧑‍💼 Пациент: {patient[2]}\n"
            text += f"👨‍⚕️ Врач: {doctor[2]}\n\n"
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=marcup,
            parse_mode="Markdown"
        )
    except Exception as e:
        pass

def start_chat(call, chat_id_end):
    print('chat_id_end', chat_id_end)
    marcup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    text = types.KeyboardButton(text="💬 Отправить сообщение")
    img = types.KeyboardButton(text="🖼 Отправить фото")
    video = types.KeyboardButton(text="🎥 Отправить видео")
    audio = types.KeyboardButton(text="🎤 Отправить аудио-сообщение")
    end_consult = types.KeyboardButton(text="✅ Завершить консультацию")
    spor = types.KeyboardButton(text="⚠️ Оспорить консультацию")
    back = types.KeyboardButton(text="⬅️ Назад")
    if chat_id_end:
        conn, cursor = connect_db()
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (call.from_user.id,))
        active_chat_id = cursor.fetchone()
        cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (active_chat_id[0],))
        consultation = cursor.fetchone()
        if consultation and consultation[5] == 'completed':
            show_followup_button(call, consultation)
            return
        marcup.add(text, img, video, audio, end_consult, spor, back)
    else:
        
        marcup.add(text, img, video, audio, end_consult, spor, back)
    bot.send_message(
        call.message.chat.id,
        "👇 *Выберите действие для общения в чате:*\n\n"
        "— 💬 Отправить текстовое сообщение\n"
        "— 🖼 Отправить фото\n"
        "— 🎥 Отправить видео\n"
        "— 🎤 Отправить аудио-сообщение\n"
        "— ✅ Завершить консультацию\n"
        "— ⚠️ Оспорить консультацию (если есть спорная ситуация)\n"
        "— ⬅️ Назад — вернуться в главное меню",
        reply_markup=marcup,
        parse_mode="Markdown"
    )
#оценка врача после консультации
def ret_pac(message, call):
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (call.from_user.id,))
    patient = cursor.fetchone()
    bot.send_message(
        message.chat.id,
        "⭐️ *Оцените врача*\n\n"
        "Пожалуйста, оцените врача по шкале от 1 до 5. "
        "Это поможет нам улучшить качество обслуживания и выбрать лучших специалистов для вас.\n\n"
        "Введите вашу оценку (от 1 до 5):"
    )
    bot.register_next_step_handler(message, get_rating, patient=patient)
def get_rating(message, patient):
    try:
        rating = int(message.text)
        if rating < 1 or rating > 5:
            raise ValueError("Оценка должна быть от 1 до 5.")
    except ValueError as e:
        bot.send_message(message.chat.id, f"❗️ Ошибка: {e}\n\nПожалуйста, введите корректную оценку.")
        bot.register_next_step_handler(message, get_rating, patient=patient)
        return
    
    conn, cursor = connect_db()
    cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
    active_chat_id = cursor.fetchone()
    cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (active_chat_id[0],))
    consultation = cursor.fetchone()
    cursor.execute('''SELECT rating FROM doctors WHERE user_id = ?''', (consultation[3],))
    current_rating = cursor.fetchone()
    rating = current_rating[0] if current_rating else 0
    if rating == 0:
        rating = 0
    else:
        rating = (rating + int(message.text)) / 2
    cursor.execute('''UPDATE doctors SET rating = ? WHERE user_id ''', (rating, consultation[3]))
    conn.commit()
    bot.send_message(
        message.chat.id,
        "✅ Спасибо за вашу оценку! "
        "Ваш отзыв поможет нам улучшить качество обслуживания и выбрать лучших специалистов для вас."
    )



@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id in ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=2)
        veri = types.InlineKeyboardButton(text="Заявки на верификацию", callback_data="doc_ver_admin")
        spor = types.InlineKeyboardButton(text="Заявки на оспаривание", callback_data="dispute_consultation")
        rassilka = types.InlineKeyboardButton(text="Рассылки", callback_data="rassilka")
        markup.add(veri, spor, rassilka)
        bot.send_message(message.chat.id, "Добро пожаловать в админ-панель!", reply_markup=markup)

def rassilka(call):
    marcup = types.InlineKeyboardMarkup(row_width=1)
    rass1 = types.InlineKeyboardButton(text='Получить сп. email', callback_data='rass_list')
    rass2 = types.InlineKeyboardButton(text='Создать расс. в тг', callback_data='rass_new')
    marcup.add(rass1, rass2)
    bot.send_message(call.message.chat.id, text='Выберете действие', reply_markup=marcup)

import pandas as pd
def rass_list(call):
    cunn, cursor = connect_db()
    email_doc = cursor.execute("""SELECT email FROM doctors WHERE rassilka = 1""").fetchall()
    print(email_doc)
    email_pac = cursor.execute("""SELECT email FROM patients WHERE rassilka = 1""").fetchall()
    data = []
    data_pac = []
    for i in email_doc:
        data += i
    for i in email_pac:
        data_pac += i
    data = [{item} for item in data]
    data_pac = [{it} for it in data_pac]
    print(data)
    df = pd.DataFrame(data)
    df.to_excel("media/email_doc.xlsx", index=False)
    
    with open('media/email_doc.xlsx', 'rb') as file:
        bot.send_document(call.message.chat.id, file)
    try:
        df = pd.DataFrame(data_pac)
        df.to_excel("media/email_pac.xlsx", index=False)
        with open('media/email_pac.xlsx', 'rb') as file:
            bot.send_document(call.message.chat.id, file)
    except ValueError:
        pass

def rass_new(call):
    bot.send_message(call.message.chat.id, text="Введите текст для рассылки")
    bot.register_next_step_handler(call.message, rass_new1)
def rass_new1(message):
    conn, cursor = connect_db()
    id_doc = cursor.execute("""SELECT user_id FROM doctors WHERE rassilka = 1""").fetchall()
    id_pac = cursor.execute("""SELECT user_id FROM patients WHERE rassilka = 1""").fetchall()
    ids = id_doc + id_pac
    id_s = []
    for i in ids:
        id_s += i
    print(id_s)
    for _ in id_s:
        bot.send_message(_, text=message.text)
    bot.send_message(message.chat.id, text=f"Рассылка успешно отправлена.\n\nВсего отправленно сообщений {len(id_s)}")


@bot.message_handler(content_types=['text', 'photo', 'video', 'audio'])
def handle_message(message):
    if message.text == "💬 Отправить сообщение":
        bot.send_message(message.chat.id, "Введите ваше сообщение:")
        bot.register_next_step_handler(message, send_text_message)
    elif message.text == "🖼 Отправить фото":
        bot.send_message(message.chat.id, "Отправьте фото:")
        bot.register_next_step_handler(message, send_photo_message)
    elif message.text == "🎥 Отправить видео":
        bot.send_message(message.chat.id, "Отправьте видео:")
        bot.register_next_step_handler(message, send_video_message)
    elif message.text == "🎤 Отправить аудио-сообщение":
        bot.send_message(message.chat.id, "Отправьте голосовое-собщение:")
        bot.register_next_step_handler(message, send_vocie_message)
    
    elif message.text == "⬅️ Назад":
        bot.send_message(message.chat.id, "Вы вернулись в главное меню.", reply_markup=types.ReplyKeyboardRemove())
        conn, cursor = connect_db()
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
        patient = cursor.fetchone()
        if patient:
            cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
            active_chat_id = cursor.fetchone()
        else:
            cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
            active_chat_id = cursor.fetchone()
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id[0],))
        chats = cursor.fetchall()
        chats = chats[0]
        print('chats', chats)
        
        if chats[2] == message.from_user.id:
            cursor.execute('''UPDATE patients SET active_chat_id = NULL WHERE user_id = ?''', (message.from_user.id,))
            conn.commit()
            print('patients', chats[2])
        elif chats[3] == message.from_user.id:
            cursor.execute('''UPDATE doctors SET active_chat_id = NULL WHERE user_id = ?''', (message.from_user.id,))
            conn.commit()
            print('doctors', chats[3])
        start(message)
    elif message.text == "⚠️ Оспорить консультацию":
        bot.send_message(message.chat.id, "Введите причину спора:")
        bot.register_next_step_handler(message, dispute_consultation)
    elif message.text == "✅ Завершить консультацию":
        conn, cursor = connect_db()
        cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
        doc = 0
        if not active_chat_id:
            cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
            active_chat_id = cursor.fetchone()
            doc = 1
        if not active_chat_id:
            bot.send_message(message.chat.id, "Нет активной консультации.")
            return
        active_chat_id = active_chat_id[0]
        cursor.execute('''UPDATE consultations SET status = ?, finished_at = ? WHERE identifier = ?''',
                        ('completed', datetime.now(), active_chat_id))
        conn.commit()
        if doc:
            bot.send_message(message.chat.id, "Приём завершён. В течение 14 дней вы можете спросить у пациента о его состоянии.")
        else:
            bot.send_message(message.chat.id, "Приём завершён. В течение 14 дней вы можете получить обратную связь от врача.")
            ai_audit_and_review(consultation_id=active_chat_id)
            ret_pac(message, call=message)
    if message.text.startswith('/view_chat_'):
        chat_id = message.text.replace("/view_chat_", "")
        print('view_chat_id', chat_id)
        conn, cursor = connect_db()
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (chat_id,))
        chats = cursor.fetchone()
        print('chat', chats)
        if chats:
            cursor.execute('''SELECT messages FROM chats WHERE consultation_id = ?''', (chat_id,))
            row = cursor.fetchone()
            if row:
                messages = json.loads(row[0])
                print('messages', messages)
                count_messages = 0
                for messagea in messages:
                    # Отправляем по 10 сообщений в секунду
                    if count_messages >= 10:
                        time.sleep(1)
                        count_messages = 0
                    count_messages += 1
                    if messagea['sender'] == 'patient':
                        if 'photo' in messagea:
                            with open(messagea['photo'], 'rb') as photo_file:
                                bot.send_photo(message.chat.id, photo=photo_file, caption=f"Пациент: {messagea['text']}")
                        elif 'video' in messagea:
                            with open(messagea['video'], 'rb') as video_file:
                                bot.send_video(message.chat.id, video=video_file, caption=f"Пациент: {messagea['text']}")
                        elif 'voice' in messagea:
                            with open(messagea['voice'], 'rb') as voice_file:
                                bot.send_voice(message.chat.id, voice=voice_file, caption=f"Пациент: {messagea['text']}")
                        else:   
                            bot.send_message(message.chat.id, f"Пациент: {messagea['text']}")
                    elif messagea['sender'] == 'doctor':
                        if 'photo' in messagea:
                            with open(messagea['photo'], 'rb') as photo_file:
                                bot.send_photo(message.chat.id, photo=photo_file, caption=f"Врач: {messagea['text']}")
                        elif 'video' in messagea:
                            with open(messagea['video'], 'rb') as video_file:
                                bot.send_video(message.chat.id, video=video_file, caption=f"Врач: {messagea['text']}")
                        elif 'voice' in messagea:
                            with open(messagea['voice'], 'rb') as voice_file:
                                bot.send_voice(message.chat.id, voice=voice_file, caption=f"Врач: {messagea['text']}")
                        else:   
                            bot.send_message(message.chat.id, f"Врач: {messagea['text']}")
            else:
                bot.send_message(message.chat.id, "Сообщения не найдены.")
        else:
            bot.send_message(message.chat.id, "Чат не найден.")
    else:
        try:
            msg = message.text
            flag= True
            conn, cursor = connect_db()
            cursor.execute('''SELECT filter FROM patients WHERE user_id = ?''', (message.from_user.id,))
            filters = cursor.fetchone()
            get_doc(message, message, filters=filters, flag=flag, msg=msg, id=message.from_user.id)
        except Exception as e:
            print(f"Ошибка при обработке сообщения: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")
    
import importlib
import json



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
    cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (consultation_id,))
    consult = cursor.fetchone()
    doctor_id = consult[3]
    patient_id = consult[2]
    # Сохраняем оценку в reviews (создайте таблицу reviews, если нет)
    cursor.execute('''INSERT INTO reviews (doctor_id, patient_id, ai_rating, comments, consultation_id) VALUES (?, ?, ?, ?, ?)''',
                   (doctor_id, patient_id, ai_score, ai_summary, consultation_id))
    conn.commit()
    if ai_score < 3:
        bot.send_message(
            ADMIN_ID,
            f"⚠️ AI-аудит: низкая оценка ({ai_score}) по консультации {consultation_id}.\n"
            f"Резюме: {ai_summary}\n"
            f"Открыть чат: /view_chat_{consultation_id}"
        )

def dispute_consultation(message):
    message_text = message.text
    conn, cursor = connect_db()
    cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
    active_chat_id = cursor.fetchone()
    cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id))
    chat = cursor.fetchone()
    marcup = types.InlineKeyboardMarkup(row_width=2)
    view_chat = types.InlineKeyboardButton(text="Посмотреть чат", callback_data=f"view_chat_{chat[1]}")
    marcup.add(view_chat)
    bot.send_message(ADMIN_ID, f"Пациент {message.from_user.id} оспорил консультацию.\nПричина: {message_text}\nЧат: {chat[1]}", reply_markup=marcup)

def send_text_message(message):
    conn, cursor = connect_db()
    pac_dont_chat = 1
    doc_dont_chat = 1
    print('message', message.from_user.id)
    try: 
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
        data_pac = cursor.fetchone()
        print('data_pac', data_pac)
        active_chat_id = data_pac[8]
        name = data_pac[2]
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
        chat = cursor.fetchone()
        print('chat', chat)
        doc_id = chat[2]
        print('doc_id', doc_id)
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (doc_id,))
        data_doc = cursor.fetchone()
        print('data_doc', data_doc)
        if data_doc[12] == None:
            doc_dont_chat = 0
    
    except TypeError:
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        data_doc = cursor.fetchone()
        print('data_doc', data_doc)
        active_chat_id = data_doc[12]
        print('active_chat_id', active_chat_id)
        name = data_doc[2]
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
        chat = cursor.fetchone()
        print('chat', chat)
        pac_id = chat[3]
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (pac_id,))
        data_pac = cursor.fetchone()
        print('data_pac', data_pac)
        if data_pac[8] == None:
            pac_dont_chat = 0
    print('name', name)
    
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
        pac_dont_chat = 0
        if active_chat_id == None:
            doc_dont_chat = 0
    print('active_chat_id', active_chat_id)
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    #active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
    active_chat_id = cursor.fetchone()
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
    print('active_chat_id', active_chat_id)
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    chat = cursor.fetchone()
    print('chat', chat)
    cursor.execute('''SELECT messages FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    row = cursor.fetchone()
    print('row', row)
    if row[0] != None:
        messages = json.loads(row[0])
    else:
        messages = []
    
    if chat:
        if chat[3] == message.from_user.id and pac_dont_chat:
            bot.send_message(chat[2], text = f'Сообщение от пациента {name}\n {message.text}')  # Отправляем сообщение врачу
            print('Сообщение от пациента', message.text)
            messages.append({
                "sender": "patient",
                "text": message.text,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id and doc_dont_chat:
            bot.send_message(chat[3], text = f'Сообщение от врача {name}\n {message.text}')
            messages.append({
                "sender": "doctor",
                "text": message.text,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id:
            bot.send_message(chat[2], text = f'Новое сообщение от пациента {name}\n {message.text}')
            messages.append({
                "sender": "patient",
                "text": message.text,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id:
            bot.send_message(chat[3], text = f'Новое сообщение от врача {name}\n {message.text}')
            messages.append({
                "sender": "doctor",
                "text": message.text,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        # сохраняем сообщение в json в базе данных
        messages_json = json.dumps(messages, ensure_ascii=False)
        cursor.execute('''UPDATE chats SET messages = ? WHERE consultation_id = ?''', (messages_json, active_chat_id))
        conn.commit()
        print('Сообщение сохранено в базе данных', messages_json)
        bot.send_message(message.chat.id, "✅ Сообщение отправлено!")

    else:
        bot.send_message(message.chat.id, "Чат не найден.")

def send_photo_message(message):
    conn, cursor = connect_db()
    pac_dont_chat = 1
    doc_dont_chat = 1
    try: 
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
        data_pac = cursor.fetchone()
        print('data_pac', data_pac)
        active_chat_id = data_pac[8]
        name = data_pac[2]
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
        chat = cursor.fetchone()
        print('chat', chat)
        doc_id = chat[2]
        print('doc_id', doc_id)
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (doc_id,))
        data_doc = cursor.fetchone()
        print('data_doc', data_doc)
        if data_doc[12] == None:
            doc_dont_chat = 0
    
    except TypeError:
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        data_doc = cursor.fetchone()
        print('data_doc', data_doc)
        active_chat_id = data_doc[12]
        print('active_chat_id', active_chat_id)
        name = data_doc[2]
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
        chat = cursor.fetchone()
        print('chat', chat)
        pac_id = chat[3]
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (pac_id,))
        data_pac = cursor.fetchone()
        print('data_pac', data_pac)
        if data_pac[8] == None:
            pac_dont_chat = 0
    print('name', name)
    
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
        pac_dont_chat = 0
        if active_chat_id == None:
            doc_dont_chat = 0
    print('active_chat_id', active_chat_id)
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    #active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
    active_chat_id = cursor.fetchone()
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
    print('active_chat_id', active_chat_id)
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    chat = cursor.fetchone()
    print('chat', chat)
    cursor.execute('''SELECT messages FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    row = cursor.fetchone()
    if row:
        messages = json.loads(row[0])
    else:
        messages = []
    if chat:
        if chat[3] == message.from_user.id and pac_dont_chat:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/photos/{message.photo[-1].file_id}.jpg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_photo(chat[2], photo=message.photo[-1].file_id, caption=f'Сообщение от пациента {name}\n {message.caption or ""}')
            print('Сообщение от пациента', message.photo[-1].file_id)
            messages.append({
                "sender": "patient",
                "text": message.caption or "",
                "photo": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id and doc_dont_chat:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/photos/{message.photo[-1].file_id}.jpg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_photo(chat[3], photo=message.photo[-1].file_id, caption=f'Сообщение от врача {name}\n {message.caption or ""}')
            messages.append({
                "sender": "doctor",
                "text": message.caption or "",
                "photo": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/photos/{message.photo[-1].file_id}.jpg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_photo(chat[2], photo=message.photo[-1].file_id, caption=f'Новое сообщение от пациента {name}\n {message.caption or ""}')
            messages.append({
                "sender": "patient",
                "text": message.caption or "",
                "photo": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/photos/{message.photo[-1].file_id}.jpg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_photo(chat[3], photo=message.photo[-1].file_id, caption=f'Новое сообщение от врача {name}\n {message.caption or ""}')
            messages.append({
                "sender": "doctor",
                "text": message.caption or "",
                "photo": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        # сохраняем сообщение в json в базе данных
        messages_json = json.dumps(messages, ensure_ascii=False)
        cursor.execute('''UPDATE chats SET messages = ? WHERE consultation_id = ?''', (messages_json, active_chat_id))
        conn.commit()
        print('Сообщение сохранено в базе данных', messages_json)
        bot.send_message(message.chat.id, "✅ Сообщение отправлено!")
    else:
        bot.send_message(message.chat.id, "Чат не найден.")

def send_video_message(message):
    conn, cursor = connect_db()
    pac_dont_chat = 1
    doc_dont_chat = 1
    try: 
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
        data_pac = cursor.fetchone()
        print('data_pac', data_pac)
        active_chat_id = data_pac[8]
        name = data_pac[2]
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
        chat = cursor.fetchone()
        print('chat', chat)
        doc_id = chat[2]
        print('doc_id', doc_id)
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (doc_id,))
        data_doc = cursor.fetchone()
        print('data_doc', data_doc)
        if data_doc[12] == None:
            doc_dont_chat = 0
    
    except TypeError:
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        data_doc = cursor.fetchone()
        print('data_doc', data_doc)
        active_chat_id = data_doc[12]
        print('active_chat_id', active_chat_id)
        name = data_doc[2]
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
        chat = cursor.fetchone()
        print('chat', chat)
        pac_id = chat[3]
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (pac_id,))
        data_pac = cursor.fetchone()
        print('data_pac', data_pac)
        if data_pac[8] == None:
            pac_dont_chat = 0
    print('name', name)
    
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
        pac_dont_chat = 0
        if active_chat_id == None:
            doc_dont_chat = 0
    print('active_chat_id', active_chat_id)
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    #active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
    active_chat_id = cursor.fetchone()
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
    print('active_chat_id', active_chat_id)
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    chat = cursor.fetchone()
    print('chat', chat)
    cursor.execute('''SELECT messages FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    row = cursor.fetchone()
    if row:
        messages = json.loads(row[0])
    else:
        messages = []
    if chat:
        if chat[3] == message.from_user.id and pac_dont_chat:
            file_info = bot.get_file(message.video.file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/videos/{message.video.file_id}.mp4"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_video(chat[2], video=message.video.file_id, caption=f'Сообщение от пациента {name}\n {message.caption or ""}')
            print('Сообщение от пациента', message.video.file_id)
            messages.append({
                "sender": "patient",
                "text": message.caption or "",
                "video": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id and doc_dont_chat:
            file_info = bot.get_file(message.video.file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/videos/{message.video.file_id}.mp4"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_video(chat[3], video=message.video.file_id, caption=f'Сообщение от врача {name}\n {message.caption or ""}')
            messages.append({
                "sender": "doctor",
                "text": message.caption or "",
                "video": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id:
            file_info = bot.get_file(message.video.file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/videos/{message.video.file_id}.mp4"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_video(chat[2], video=message.video.file_id, caption=f'Новое сообщение от пациента {name}\n {message.caption or ""}')
            messages.append({
                "sender": "patient",
                "text": message.caption or "",
                "video": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id:
            file_info = bot.get_file(message.video.file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/videos/{message.video.file_id}.mp4"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_video(chat[3], video=message.video.file_id, caption=f'Новое сообщение от врача {name}\n {message.caption or ""}')
            messages.append({
                "sender": "doctor",
                "text": message.caption or "",
                "video": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        # сохраняем сообщение в json в базе данных
        messages_json = json.dumps(messages, ensure_ascii=False)
        cursor.execute('''UPDATE chats SET messages = ? WHERE consultation_id = ?''', (messages_json, active_chat_id))
        conn.commit()
        print('Сообщение сохранено в базе данных', messages_json)
        bot.send_message(message.chat.id, "✅ Сообщение отправлено!")
    else:
        bot.send_message(message.chat.id, "Чат не найден.")

def send_vocie_message(message):
    conn, cursor = connect_db()
    pac_dont_chat = 1
    doc_dont_chat = 1
    try: 
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
        data_pac = cursor.fetchone()
        print('data_pac', data_pac)
        active_chat_id = data_pac[8]
        name = data_pac[2]
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
        chat = cursor.fetchone()
        print('chat', chat)
        doc_id = chat[2]
        print('doc_id', doc_id)
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (doc_id,))
        data_doc = cursor.fetchone()
        print('data_doc', data_doc)
        if data_doc[12] == None:
            doc_dont_chat = 0
    
    except TypeError:
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        data_doc = cursor.fetchone()
        print('data_doc', data_doc)
        active_chat_id = data_doc[12]
        print('active_chat_id', active_chat_id)
        name = data_doc[2]
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
        chat = cursor.fetchone()
        print('chat', chat)
        pac_id = chat[3]
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (pac_id,))
        data_pac = cursor.fetchone()
        print('data_pac', data_pac)
        if data_pac[8] == None:
            pac_dont_chat = 0
    print('name', name)
    
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
        pac_dont_chat = 0
        if active_chat_id == None:
            doc_dont_chat = 0
    print('active_chat_id', active_chat_id)
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    #active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
    active_chat_id = cursor.fetchone()
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
    print('active_chat_id', active_chat_id)
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    chat = cursor.fetchone()
    print('chat', chat)
    cursor.execute('''SELECT messages FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    row = cursor.fetchone()
    print('row', row)
    if row:
        messages = json.loads(row[0])
    else:
        messages = []
    if chat:
        if chat[3] == message.from_user.id and pac_dont_chat:
            file_info = bot.get_file(message.voice.file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/voices/{message.voice.file_id}.ogg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_voice(chat[2], voice=message.voice.file_id, caption=f'Сообщение от пациента {name}\n {message.caption or ""}')
            print('Сообщение от пациента', message.voice.file_id)
            messages.append({
                "sender": "patient",
                "text": message.caption or "",
                "voice": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id and doc_dont_chat:
            file_info = bot.get_file(message.voice.file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/voices/{message.voice.file_id}.ogg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_voice(chat[3], voice=message.voice.file_id, caption=f'Сообщение от врача {name}\n {message.caption or ""}')
            messages.append({
                "sender": "doctor",
                "text": message.caption or "",
                "voice": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id:
            file_info = bot.get_file(message.voice.file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/voices/{message.voice.file_id}.ogg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_voice(chat[2], voice=message.voice.file_id, caption=f'Новое сообщение от пациента {name}\n {message.caption or ""}')
            messages.append({
                "sender": "patient",
                "text": message.caption or "",
                "voice": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id:
            file_info = bot.get_file(message.voice.file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/voices/{message.voice.file_id}.ogg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_voice(chat[3], voice=message.voice.file_id, caption=f'Новое сообщение от врача {name}\n {message.caption or ""}')
            messages.append({
                "sender": "doctor",
                "text": message.caption or "",
                "voice": local_path,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        # сохраняем сообщение в json в базе данных
        messages_json = json.dumps(messages, ensure_ascii=False)
        cursor.execute('''UPDATE chats SET messages = ? WHERE consultation_id = ?''', (messages_json, active_chat_id))
        conn.commit()
        print('Сообщение сохранено в базе данных', messages_json)
        bot.send_message(message.chat.id, "✅ Сообщение отправлено!")
    else:
        bot.send_message(message.chat.id, "Чат не найден.")



def doc_ver_admin(call):
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM doctors WHERE verification_status = ?''', ('pending',))
    data = cursor.fetchall()
    if not data:
        bot.send_message(call.message.chat.id, "Нет заявок на верификацию.")
        return
    for row in data:
        print('row', row)
        markup = types.InlineKeyboardMarkup(row_width=2)
        check = types.InlineKeyboardButton(text=f"Проверить {row[2]}", callback_data=f"check_{row[1]}")
        markup.add(check)
        bot.send_message(call.message.chat.id, f"Заявка на верификацию", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check_doc(call):
    conn, cursor = connect_db()
    doc_id = call.data.split("_")[1]
    cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (doc_id,))
    data = cursor.fetchone()
    if not data:
        bot.send_message(call.message.chat.id, "Доктор не найден.")
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    approve = types.InlineKeyboardButton(text="Одобрить", callback_data=f"accept_{doc_id}")
    reject = types.InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{doc_id}")
    markup.add(approve, reject)
    with open(data[7], 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo=photo, caption=f"Доктор: {data[2]}", reply_markup=markup)
    
@bot.callback_query_handler(func=lambda call: call.data.startswith("followup_"))
def followup_request(call):
    consultation_id = call.data.replace("followup_", "")
    print('consultation_id', consultation_id)
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (consultation_id,))
    consultation = cursor.fetchone()
    if not consultation:
        bot.send_message(call.message.chat.id, "Консультация не найдена.")
        return
    # Проверяем, был ли уже пинг
    if consultation[10]:  # followup_ping
        bot.send_message(call.message.chat.id, "Вы уже отправляли запрос на обратную связь по этой консультации.")
        return
    # Ставим флаг
    cursor.execute('''UPDATE consultations SET followup_ping = 1 WHERE identifier = ?''', (consultation_id,))
    conn.commit()
    # Отправляем пациенту
    patient_id = consultation[2]
    doctor_id = consultation[3]
    cursor.execute('''SELECT name FROM doctors WHERE user_id = ?''', (doctor_id,))
    doc_name = cursor.fetchone()[0]
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🟢 Лучше", callback_data=f"1followup_status_{consultation_id}_good"),
        types.InlineKeyboardButton("🟡 Без изменений", callback_data=f"1followup_status_{consultation_id}_neutral"),
        types.InlineKeyboardButton("🔴 Хуже", callback_data=f"1followup_status_{consultation_id}_bad"),
    )
    bot.send_message(
        patient_id,
        f"Доктор {doc_name} интересуется, как вы себя чувствуете после консультации. Выберите вариант:",
        reply_markup=markup
    )
    bot.send_message(call.message.chat.id, "Запрос отправлен пациенту.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("1followup_status_"))
def followup_status(call):
    parts = call.data.split("_")
    consultation_id = parts[2]
    status = parts[3]
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (consultation_id,))
    consultation = cursor.fetchone()
    doctor_id = consultation[3]
    patient_id = consultation[2]
    # Можно добавить поле followup_status в consultations, если хотите хранить результат
    try:
        cursor.execute('''ALTER TABLE consultations ADD COLUMN followup_status TEXT''')
        conn.commit()
    except Exception:
        pass  # поле уже есть
    cursor.execute('''UPDATE consultations SET followup_status = ? WHERE identifier = ?''', (status, consultation_id))
    conn.commit()
    # Уведомляем врача
    status_text = {"good": "🟢 Лучше", "neutral": "🟡 Без изменений", "bad": "🔴 Хуже"}[status]
    bot.send_message(doctor_id, f"Пациент ответил на ваш запрос: {status_text}")
    # Если "хуже" — предложить пациенту оформить новую консультацию
    if status == "bad":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Оформить новую консультацию", callback_data="doc_reg"))
        bot.send_message(
            patient_id,
            "❗️ Если ваше самочувствие ухудшилось, вы можете оформить новую консультацию или обратиться в экстренную службу.",
            reply_markup=markup
        )
    else:
        bot.send_message(patient_id, "Спасибо за обратную связь! Если потребуется — вы всегда можете обратиться к врачу снова.")

import threading

def auto_refund_job():
    while True:
        conn, cursor = connect_db()
        now = datetime.now()
        cursor.execute('''SELECT * FROM consultations WHERE status = ?''', ('pending',))
        consultations = cursor.fetchall()
        for consult in consultations:
            created_at = datetime.fromisoformat(consult[8])  # consult[8] = created_at
            if (now - created_at) > timedelta(hours=24):
                # Возврат: меняем статус, уведомляем, возвращаем деньги (если реализовано)
                cursor.execute('''UPDATE consultations SET status = ? WHERE identifier = ?''', ('refunded', consult[1]))
                conn.commit()
                bot.send_message(consult[2], "⏳ Врач не ответил на ваш запрос в течение 24 часов. Средства возвращены, вы можете выбрать другого врача.")
                bot.send_message(consult[3], "❗️ Ваш аккаунт может быть ограничен за игнорирование заявок.")
                cursor.execute('''UPDATE doctors SET ignore_count = COALESCE(ignore_count, 0) + 1 WHERE user_id = ?''', (consult[3],))
                cursor.execute('''SELECT ignore_count FROM doctors WHERE user_id = ?''', (consult[3],))
                ignore_count = cursor.fetchone()[0]
                if ignore_count >= 4:
                    cursor.execute('''UPDATE doctors SET is_frozen = 1 WHERE user_id = ?''', (consult[3],))
                    bot.send_message(consult[3], "❌ Ваш аккаунт заморожен из-за неоднократного игнорирования заявок. Обратитесь в администрацию для разблокировки.")
                conn.commit()
        time.sleep(3600)  # Проверять раз в час


# Запускать в отдельном потоке:
threading.Thread(target=auto_refund_job, daemon=True).start()

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    conn, cursor = connect_db()
    id_consult = cursor.execute('''SELECT identifier FROM consultations WHERE doctor_id = ?''', (call.from_user.id,)).fetchall()
    print('id', id_consult)
    print(call.from_user.id)
    bot.answer_callback_query(call.id)
    if call.data.startswith("doctor_"):
        reg_doc_sogl(call, fl=int(call.data.replace("doctor_","")))
    elif call.data.startswith('dagree_'):
        doc_reg(message=call.message, user_id=call.from_user.id, fl=int(call.data.replace("dagree_","")))
    elif call.data.startswith("patient_"):
        pat_reg(message=call.message, call=call, fl=int(call.data.replace("patient_","")))
    elif call.data == "doc_verification":
        print(1)
        doc_verification(message=call.message, call=call)
    elif call.data == "doc_spec":
        print(2)
        get_doc_spec(message=call.message, call=call)
    elif call.data in ["therapist", "family", "pediatrician", "cardiologist", "gastroenterologist",
                     "endocrinologist", "neurologist", "allergist_immunologist", "dermatologist",
                     "psychotherapist", "gynecologist", "ophthalmologist", "dentist", "psychiatrist"]:
        conn, cursor = connect_db()
        cursor.execute('''SELECT name FROM specialisation WHERE user_id = ?''', (call.from_user.id,))
        specialization = cursor.fetchall()
        specialization = [spec[0] for spec in specialization]
        if call.data in specialization:
            cursor.execute('''DELETE FROM specialisation WHERE user_id = ? AND name = ?''', (call.from_user.id, call.data))
            conn.commit()
        else:
            cursor.execute('''INSERT INTO specialisation (user_id, name, price) VALUES (?, ?, ?)''', (call.from_user.id, call.data, 0))
            conn.commit()
        get_doc_spec(message=call.message, call=call)
    elif call.data == "done":
        get_price(message=call.message, call=call)
    elif call.data == "edit_profile":
        edit_profile(message=call.message, call=call)
    elif call.data == "doc_reg":
        doc_list(message=call.message, call=call)
    elif call.data in ["therapist_doc", "family_doc", "pediatrician_doc", "cardiologist_doc", "gastroenterologist_doc",
                     "endocrinologist_doc", "neurologist_doc", "allergist_immunologist_doc", "dermatologist_doc",
                     "psychotherapist_doc", "gynecologist_doc", "ophthalmologist_doc", "dentist_doc", "psychiatrist_doc"]:
        spec = call.data.replace("_doc", "")
        print(spec)
        conn, cursor = connect_db()
        cursor.execute('''SELECT spec FROM patients WHERE user_id = ?''', (call.from_user.id,))
        specialization = cursor.fetchone() 
        print('spec1',specialization)  
        conn.commit()
        cursor.execute('''UPDATE patients SET spec = ? WHERE user_id = ?''', (spec, call.from_user.id))
        conn.commit()
        filters = 10
        cursor.execute('''UPDATE patients SET filter = ? WHERE user_id = ?''', (filters, call.from_user.id))
        conn.commit()
        get_doc(message=call.message, call=call, filters=filters, flag=False, msg=None, id=call.from_user.id)
    elif call.data == "sort1":
        filters = 10
        conn, cursor = connect_db()
        cursor.execute('''UPDATE patients SET filter = ? WHERE user_id = ?''', (filters, call.from_user.id))
        conn.commit()
        get_doc(message=call.message, call=call, filters=filters, flag=False, msg=None, id=call.from_user.id)
    elif call.data == "sort2":
        filters = 11
        conn, cursor = connect_db()
        cursor.execute('''UPDATE patients SET filter = ? WHERE user_id = ?''', (filters, call.from_user.id))
        conn.commit()
        get_doc(message=call.message, call=call, filters=filters, flag=False, msg=None, id=call.from_user.id)
    elif call.data == "sort3":
        filters = 11
        conn, cursor = connect_db()
        cursor.execute('''UPDATE patients SET filter = ? WHERE user_id = ?''', (filters, call.from_user.id))
        conn.commit()
        get_doc(message=call.message, call=call, filters=filters, flag=False, msg=None, id=call.from_user.id)
    elif call.data.startswith("consult_"):
        parts = call.data.split("_")
        if len(parts) == 3:
            doctor_id = int(parts[1])
            spec_id = int(parts[2])
            # Сохраняем выбранную специализацию во временные данные, если нужно
            conn, cursor = connect_db()
            cursor.execute('''INSERT OR REPLACE INTO temporary_data (user_id, data, spec_id) VALUES (?, ?, ?)''', (call.from_user.id, doctor_id, spec_id))
            conn.commit()
            bot.send_message(
                call.message.chat.id,
                "📝 Пожалуйста, опишите вашу проблему максимально подробно.\n\n"
                "Это поможет врачу быстрее разобраться в ситуации и дать более точную консультацию.\n\n"
                "Например: «Беспокоит боль в горле и температура уже 3 дня...»"
            )
            bot.register_next_step_handler(call.message, get_consultation_date)
        else:
            id = call.data.replace("consult_", "")
            conn, cursor = connect_db()
            cursor.execute('''INSERT INTO temporary_data (user_id, data) VALUES (?, ?)''', (call.from_user.id, id))
            conn.commit()
            bot.send_message(
                call.message.chat.id,
                "📝 Пожалуйста, опишите вашу проблему максимально подробно.\n\n"
                "Это поможет врачу быстрее разобраться в ситуации и дать более точную консультацию.\n\n"
                "Например: «Беспокоит боль в горле и температура уже 3 дня...»"
            )
            bot.register_next_step_handler(call.message, get_consultation_date)
    elif call.data.startswith("approve"):
        id_consult = call.data.replace("approve", "")
        conn, cursor = connect_db()
        cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (id_consult,))
        consultation = cursor.fetchone()
        if consultation:
            #нужна проверка, логика оплаты.
            bot.send_message(
        consultation[3],
    "✅ Ваша консультация подтверждена!\n\n"
    "Вы можете перейти в чат с пациентом для начала общения."
)
            bot.send_message(
    consultation[2],
    "✅ Консультация подтверждена врачом!\n\n"
    "Вы можете перейти в чат для общения с врачом."
)
            #send_invoice_to_patient(id_consult, call.message.chat.id)
            create_chat(message=call.message, call=call)
        else:
            bot.send_message(call.message.chat.id, "Консультация не найдена.")
    elif call.data.startswith("cancel"):
        id_consult = call.data.replace("cancel", "")
        conn, cursor = connect_db()
        cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (id_consult,))
        consultation = cursor.fetchone()
        if consultation:
            bot.send_message(
                consultation[3],
                "❌ Ваша консультация была отменена.\n\n"
                "Если у вас остались вопросы — вы можете выбрать другого врача или попробовать записаться снова."
)
            bot.send_message(
                consultation[2],
                "❌ Консультация отменена.\n\n"
                "Если вы хотите, вы можете выбрать другого специалиста для консультации."
)
        else:
            bot.send_message(call.message.chat.id, "Консультация не найдена.")
    elif call.data.startswith("accept"):
        id = call.data.replace("accept_", "")
        print('id=', id)
        conn, cursor = connect_db()
        cursor.execute('''UPDATE doctors SET verification_status = ? WHERE user_id = ?''', ('verified', id))
        conn.commit()
        bot.send_message(
    id,
    "✅ Поздравляем! Ваша верификация прошла успешно.\n\n"
    "Теперь вы можете принимать пациентов на платформе и пользоваться всеми возможностями сервиса."
)
        bot.send_message(
    call.message.chat.id,
    "✅ Верификация одобрена.\n\n"
    "Доктор получил уведомление и теперь может работать на платформе."
)
        
    elif call.data.startswith("reject"):
        id = call.data.replace("reject_", "")
        print('id=', id)
        conn, cursor = connect_db()
        cursor.execute('''UPDATE doctors SET verification_status = ? WHERE user_id = ?''', ('rejected', id))
        conn.commit()
        bot.send_message(
    id,
    "❌ К сожалению, ваша верификация отклонена.\n\n"
    "Проверьте корректность загруженных документов и попробуйте пройти верификацию снова.\n"
    "Если возникли вопросы — обратитесь в поддержку."
)
        bot.send_message(
    call.message.chat.id,
    "❌ Верификация отклонена.\n\n"
    "Доктор получил уведомление и может повторно отправить документы."
)
    elif call.data == "doc_chats":
        print('doc_chats')
        chats(message=call.message, call=call)
    elif call.data == "pat_chats":
        chats(message=call.message, call=call)
    elif call.data == "back_doc" or call.data == "back_pat":
        if call.data == "back_doc":
            profile_doc(message=call.message, call=call)
        else:
            profile_pat(message=call.message, call=call)
    elif call.data.startswith("chat_"):
        chat_id = call.data.replace("chat_", "")
        print('chat_id', chat_id)
        chat_id_end = chat_id.endswith('_1')
        print('chat_id_end', chat_id_end)
        #убираем "_1" или "_2" в конце, если есть
        if chat_id.endswith("_1") or chat_id.endswith("_2"):
            chat_id = chat_id[:-2]
        print('chat_id', chat_id)
        conn, cursor = connect_db()
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (chat_id,))
        chat = cursor.fetchone()
        print('chat', chat)
        if chat:
            cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (chat[1],))
            consultation = cursor.fetchone()
            if consultation:
                cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (consultation[3],))
                doctor = cursor.fetchone()
                cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (consultation[2],))
                patient = cursor.fetchone()
                bot.send_message(call.message.chat.id, f"Чат с {doctor[2] if call.data == 'doc_chats' else patient[2]}")
                print('chat_id.end', chat_id.endswith('_1'))
                if chat_id_end:
                    cursor.execute('''UPDATE doctors SET active_chat_id = ? WHERE user_id = ?''', (chat_id, consultation[3]))
                    conn.commit()
                else:
                    cursor.execute('''UPDATE patients SET active_chat_id = ? WHERE user_id = ?''', (chat_id, consultation[2]))
                    conn.commit()
                bot.send_message(call.message.chat.id, "Вы можете начать общение в этом чате.")
                start_chat(call, chat_id_end)
            else:
                bot.send_message(call.message.chat.id, "Консультация не найдена.")
        else:
            bot.send_message(call.message.chat.id, "Чат не найден.")
    
    elif call.data.startswith("view_chat_"):
        # Получаем chat_id из call.data
        if call.data.startswith("view_chat_"):
            chat_id = call.data.replace("view_chat_", "")
            print('view_chat_id', chat_id)
        else:
            chat_id = message.text.replace("view_chat_", "")
            print('view_chat_id', chat_id)
        conn, cursor = connect_db()
        cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (chat_id,))
        chat = cursor.fetchone()
        print('chat', chat)
        if chat:
            cursor.execute('''SELECT messages FROM chats WHERE consultation_id = ?''', (chat_id,))
            row = cursor.fetchone()
            if row:
                messages = json.loads(row[0])
                print('messages', messages)
                count_messages = 0
                for message in messages:
                    # Отправляем по 10 сообщений в секунду
                    if count_messages >= 10:
                        time.sleep(1)
                        count_messages = 0
                    count_messages += 1
                    if message['sender'] == 'patient':
                        if 'photo' in message:
                            with open(message['photo'], 'rb') as photo_file:
                                bot.send_photo(call.message.chat.id, photo=photo_file, caption=f"Пациент: {message['text']}")
                        elif 'video' in message:
                            with open(message['video'], 'rb') as video_file:
                                bot.send_video(call.message.chat.id, video=video_file, caption=f"Пациент: {message['text']}")
                        elif 'voice' in message:
                            with open(message['voice'], 'rb') as voice_file:
                                bot.send_voice(call.message.chat.id, voice=voice_file, caption=f"Пациент: {message['text']}")
                        else:   
                            bot.send_message(call.message.chat.id, f"Пациент: {message['text']}")
                    elif message['sender'] == 'doctor':
                        if 'photo' in message:
                            with open(message['photo'], 'rb') as photo_file:
                                bot.send_photo(call.message.chat.id, photo=photo_file, caption=f"Врач: {message['text']}")
                        elif 'video' in message:
                            with open(message['video'], 'rb') as video_file:
                                bot.send_video(call.message.chat.id, video=video_file, caption=f"Врач: {message['text']}")
                        elif 'voice' in message:
                            with open(message['voice'], 'rb') as voice_file:
                                bot.send_voice(call.message.chat.id, voice=voice_file, caption=f"Врач: {message['text']}")
                        else:   
                            bot.send_message(call.message.chat.id, f"Врач: {message['text']}")
            else:
                bot.send_message(call.message.chat.id, "Сообщения не найдены.")
        else:
            bot.send_message(call.message.chat.id, "Чат не найден.")
    elif call.data == 'doc_ver_admin':
        doc_ver_admin(call)
    elif call.data == "edit_profile_pat":
        edit_profile_pat(call=call)
    elif call.data == "doc_consultations":
        doc_consultations(call=call)
    elif call.data == 'doc_link':
        get_doc_link(call=call)
    elif call.data.startswith("choose_spec_"):
        doctor_id = int(call.data.replace("choose_spec_", ""))
        conn, cursor = connect_db()
        cursor.execute('''SELECT * FROM specialisation WHERE user_id = ?''', (doctor_id,))
        specs = cursor.fetchall()
        if not specs:
            bot.send_message(call.message.chat.id, "У врача не указаны специализации.")
            return
        marcup = types.InlineKeyboardMarkup(row_width=1)
        for spec in specs:
            # spec[0] — id специализации, spec[3] — название
            marcup.add(types.InlineKeyboardButton(
                text=f"{spec[3]} — {spec[4]} руб.",
                callback_data=f"consult_{doctor_id}_{spec[0]}"
            ))
        marcup.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"doc_card_{doctor_id}"))
        bot.send_message(
            chat_id=call.message.chat.id,
            text="🩺 Выберите специализацию для консультации:",
            reply_markup=marcup
        )
    elif call.data == "rassilka_on":
        fl = 0
        polt_sogl(message=call.message, fl=fl)
    elif call.data == "rassilka_off":
        fl = 1
        polt_sogl(message=call.message, fl=fl)
    elif call.data.startswith('agree_'):
        start1(message=call.message, fl=int(call.data.replace("agree_","")))
    elif call.data == "disagree":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = "❌ Вы отказались от условий. Использование сервиса невозможно.")
    elif call.data == 'rassilka':
        rassilka(call)
    elif call.data == 'rass_list':
        rass_list(call)
    elif call.data == 'rass_new':
        rass_new(call)
    elif call.data == 'doc_off_rass':
        cursor.execute("""UPDATE doctors SET rassilka = ? WHERE user_id = ?""", (0, call.from_user.id))
        conn.commit()
        profile_doc(call.message, call)
    elif call.data == 'doc_on_rass':
        cursor.execute("""UPDATE doctors SET rassilka = ? WHERE user_id = ?""", (1, call.from_user.id))
        conn.commit()
        profile_doc(call.message, call)
    elif call.data == 'pat_off_rass':
        cursor.execute("""UPDATE patients SET rassilka = ? WHERE user_id = ?""", (0, call.from_user.id))
        conn.commit()
        profile_doc(call.message, call)
    elif call.data == 'pat_on_rass':
        cursor.execute("""UPDATE patients SET rassilka = ? WHERE user_id = ?""", (1, call.from_user.id))
        conn.commit()
        profile_doc(call.message, call)


bot.polling(none_stop=True)