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

TOKEN = "8156778620:AAGDqv6M3xzOH75owFRtTGU59EPaz_Mz0II"
#CLOUDPAYMENTS_PUBLIC_ID = "YOUR_PUBLIC_ID"
#CLOUDPAYMENTS_SECRET = "YOUR_SECRET_KEY"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 2146048678  # Замените на ваш ID администратора
#ADMIN_ID = (935727305, 2107643694)
def connect_db():
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()
    return conn, cursor


@bot.message_handler(commands=['start'])
def start(message):
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
    doctor = cursor.fetchone()
    cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
    patient = cursor.fetchone()
    print(doctor)
    print(message.from_user.id)
    if doctor:
        profile_doc(message, call=message)
    elif patient:
        profile_pat(message, call=message)
    else:
        marcup = types.InlineKeyboardMarkup(row_width=2)
        doc = types.InlineKeyboardButton(text="Доктор", callback_data="doctor")
        pat = types.InlineKeyboardButton(text="Пациент", callback_data="patient")
        marcup.add(doc, pat)
        bot.send_message(message.chat.id, "Выберите роль:", reply_markup=marcup)
    cursor.execute('''SELECT * FROM patients''')
    patients = cursor.fetchall()
    print('patients', patients)


user_data = {}
def doc_reg(message, user_id):
    user_data[user_id] = {}
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, get_doc_name)

def get_doc_name(message):
    user_data[message.from_user.id]['name'] = message.text
    bot.send_message(message.chat.id, "Введите номер телефона:")
    bot.register_next_step_handler(message, get_doc_phone)
def get_doc_phone(message):
    user_data[message.from_user.id]['phone'] = message.text
    bot.send_message(message.chat.id, "Введите email:")
    bot.register_next_step_handler(message, get_doc_email)
def get_doc_email(message):
    user_data[message.from_user.id]['email'] = message.text
    bot.send_message(message.chat.id, "Доктор успешно зарегистрирован!\n"
                     "Имя: {}\n"
                     "Телефон: {}\n"
                     "Email: {}".format(
        user_data[message.from_user.id]['name'],
        user_data[message.from_user.id]['phone'],
        user_data[message.from_user.id]['email']
    ))
    conn, cursor = connect_db()
    cursor.execute('''INSERT INTO doctors (user_id, name, phone, email) VALUES (?, ?, ?, ?)''', (
        message.from_user.id,
        user_data[message.from_user.id]['name'],
        user_data[message.from_user.id]['phone'],
        user_data[message.from_user.id]['email']
    ))
    conn.commit()
    bot.send_message(message.chat.id, """
📂 Для работы на платформе необходимо подтвердить документы.  
📷 Прикрепите фото документов, чтобы пройти проверку.  
👨‍⚕️ После успешной проверки вы получите бейдж «✅ Подтверждён».  
""")
    print(user_data)
    print(cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,)).fetchall())
    profile_doc(message, call=message)

def pat_reg(message, call):
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, get_pat_name)
def get_pat_name(message):
    user_data[message.from_user.id] = {}
    user_data[message.from_user.id]['name'] = message.text
    bot.send_message(message.chat.id, "Введите номер телефона:")
    bot.register_next_step_handler(message, get_pat_phone)
def get_pat_phone(message):
    user_data[message.from_user.id]['phone'] = message.text
    bot.send_message(message.chat.id, "Введите email:")
    bot.register_next_step_handler(message, get_pat_email)
def get_pat_email(message):
    user_data[message.from_user.id]['email'] = message.text
    bot.send_message(message.chat.id, "Пациент успешно зарегистрирован!\n"
                     "Имя: {}\n"
                     "Телефон: {}\n"
                     "Email: {}".format(
        user_data[message.from_user.id]['name'],
        user_data[message.from_user.id]['phone'],
        user_data[message.from_user.id]['email']
    ))
    con, cursor = connect_db()
    cursor.execute('''INSERT INTO patients (user_id, name, phone, email) VALUES (?, ?, ?, ?)''', (
        message.from_user.id,
        user_data[message.from_user.id]['name'],
        user_data[message.from_user.id]['phone'],
        user_data[message.from_user.id]['email']
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
    marcup = types.InlineKeyboardMarkup(row_width=2)
    doc = types.InlineKeyboardButton(text="Пройти вертификацию", callback_data="doc_verification")
    specif = types.InlineKeyboardButton(text="Выбрать специальность", callback_data="doc_spec")
    chats = types.InlineKeyboardButton(text="Чаты", callback_data="doc_chats")
    edit = types.InlineKeyboardButton(text="Редактировать профиль", callback_data="edit_profile")
    status = cursor.fetchone()[0]
    print(status)
    if status == 'pending':
        marcup.add(doc, specif, edit)
    elif status == 'verified':
        marcup.add(specif, chats, edit)
    
    cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (id,))
    doctor = cursor.fetchone()
    cursor.execute('''SELECT name_ru FROM specialisation WHERE user_id = ?''', (id,))
    specialization = cursor.fetchall()
    # Преобразуем список кортежей в список строк
    specialization = [spec[0] for spec in specialization]
    print(specialization)
    
    # Преобразуем список строк в строку с разделителем
    specialization = ', '.join(specialization)
    if doctor:
        bot.send_message(id, text="Ваш профиль:\n"
                         "Имя: {}\n"
                         "Телефон: {}\n"
                         "Email: {}\n"
                         "Статус: {}\n"
                         "Баланс: {}\n"
                         "Специализации {}".format(
            doctor[2], doctor[4], doctor[5], '✅Подтверждён' if doctor[8] == 'verified' else '❌ Не подтверждён', doctor[10], specialization),
                          reply_markup=marcup)
    else:
        bot.send_message(id, "Профиль не найден.")

#верификация

def doc_verification(message, call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Отправьте фото документов для верификации.")
    bot.register_next_step_handler(message, get_doc_verification)
def get_doc_verification(message):
    marcup = types.InlineKeyboardMarkup(row_width=2)
    ver_accept = types.InlineKeyboardButton(text="Принять", callback_data="accept_{}".format(message.from_user.id))
    ver_decline = types.InlineKeyboardButton(text="Отклонить", callback_data="decline")
    marcup.add(ver_accept, ver_decline)
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'verification_docs/' + str(message.from_user.id) + '.jpg'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        conn, cursor = connect_db()
        cursor.execute('''UPDATE doctors SET verification_status = ? WHERE user_id = ?''', ('pending', message.from_user.id))
        cursor.execute('''UPDATE doctors SET verification_docs = ? WHERE user_id = ?''', (src, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, text="Документы отправлены на проверку.")
        bot.send_message(ADMIN_ID, f"Новый запрос на верификацию {message.from_user.id}.", reply_markup=marcup)
    #else:
       # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пожалуйста, отправьте фото документов.")


def get_doc_spec(message, call):
    conn, cursor = connect_db()
    cursor.execute('''SELECT name FROM specialisation WHERE user_id = ?''', (call.from_user.id,))
    specialization = cursor.fetchall()
    print(specialization)
    specialization = [spec[0] for spec in specialization]
    print(specialization)
    marcup = types.InlineKeyboardMarkup(row_width=3)
    spec1 = types.InlineKeyboardButton(text="✅ Терапевт" if "therapist" in specialization else "Терапевт", callback_data="therapist")
    spec2 = types.InlineKeyboardButton(text="✅ Семейный врач" if "family" in specialization else "Семейный врач", callback_data="family")
    spec3 = types.InlineKeyboardButton(text="✅ Педиатр" if "pediatrician" in specialization else "Педиатр", callback_data="pediatrician")
    spec4 = types.InlineKeyboardButton(text="✅ Кардиолог" if "cardiologist" in specialization else "Кардиолог", callback_data="cardiologist")
    spec5 = types.InlineKeyboardButton(text="✅ Гастроэнтеролог" if "gastroenterologist" in specialization else "Гастроэнтеролог", callback_data="gastroenterologist")
    spec6 = types.InlineKeyboardButton(text="✅ Эндокринолог" if "endocrinologist" in specialization else "Эндокринолог", callback_data="endocrinologist")
    spec7 = types.InlineKeyboardButton(text="✅ Невролог" if "neurologist" in specialization else "Невролог", callback_data="neurologist")
    spec8 = types.InlineKeyboardButton(text="✅ Аллерголог-иммунолог" if "allergist_immunologist" in specialization else "Аллерголог-иммунолог", callback_data="allergist_immunologist")
    spec9 = types.InlineKeyboardButton(text="✅ Дерматолог" if "dermatologist" in specialization else "Дерматолог", callback_data="dermatologist")
    spec10 = types.InlineKeyboardButton(text="✅ Психотерапевт" if "psychotherapist" in specialization else "Психотерапевт", callback_data="psychotherapist")
    spec11 = types.InlineKeyboardButton(text="✅ Гинеколог" if "gynecologist" in specialization else "Гинеколог", callback_data="gynecologist")
    spec12 = types.InlineKeyboardButton(text="✅ Офтальмолог" if "ophthalmologist" in specialization else "Офтальмолог", callback_data="ophthalmologist")
    spec13 = types.InlineKeyboardButton(text="✅ Стоматолог" if "dentist" in specialization else "Стоматолог", callback_data="dentist")
    spec14 = types.InlineKeyboardButton(text="✅ Психиатр" if "psychiatrist" in specialization else "Психиатр", callback_data="psychiatrist")
    done = types.InlineKeyboardButton(text="Готово", callback_data="done")
    marcup.add(spec1, spec2, spec3, spec4, spec5, spec6, spec7, spec8, spec9, spec10, spec11, spec12, spec13, spec14, done)
    
    # Проверяем, изменилось ли сообщение
    current_text = "Выберите специальность:"
    current_markup = call.message.reply_markup

    # Преобразуем разметку в строку для сравнения
    if current_text != call.message.text or str(current_markup) != str(marcup.to_dict()):
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=current_text, reply_markup=marcup)


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
    bot.send_message(message.chat.id, "Введите стоимость консультации для каждого направления через запятую (например: 1000,2000,3000):")
    bot.register_next_step_handler(message, get_price_value_2)
def get_price_value_2(message):
    prices = message.text.split(',')
    conn, cursor = connect_db()
    cursor.execute('''SELECT name FROM specialisation WHERE user_id = ?''', (message.from_user.id,))
    specialization = cursor.fetchall()
    specialization = [spec[0] for spec in specialization]
    print(specialization)
    try:
        for i in range(len(specialization)):
            cursor.execute('''UPDATE specialisation SET price = ? WHERE user_id = ? AND name = ?''', (prices[i], message.from_user.id, specialization[i]))
            conn.commit()
        bot.send_message(message.chat.id, "Стоимость успешно обновлена.")
        pr = cursor.execute('''SELECT name, price FROM specialisation WHERE user_id = ?''', (message.from_user.id,)).fetchall()
        print(pr)
        profile_doc(message, call=message)
    except IndexError:
        bot.send_message(message.chat.id, "Ошибка: количество цен не соответствует количеству направлений. Пожалуйста, попробуйте снова.")
        get_price_value(message)
    

def edit_profile(message, call):
    marcup = types.InlineKeyboardMarkup(row_width=2)
    name = types.InlineKeyboardButton(text="Изменить имя", callback_data="name")
    phone = types.InlineKeyboardButton(text="Изменить номер телефона", callback_data="phone")
    email = types.InlineKeyboardButton(text="Изменить email", callback_data="email")
    discription = types.InlineKeyboardButton(text="Изм.\доб. описание", callback_data="description")
    marcup.add(name, phone, email, discription)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите действие:", reply_markup=marcup)

@bot.callback_query_handler(func=lambda call: call.data in ["name", "phone", "email", "description"])
def edit_profile1(call):
    bot.answer_callback_query(call.id)
    if call.data == "name":
        bot.send_message(call.message.chat.id, "Введите новое имя:")
        bot.register_next_step_handler(call.message, get_new_name)
    elif call.data == "phone":
        bot.send_message(call.message.chat.id, "Введите новый номер телефона:")
        bot.register_next_step_handler(call.message, get_new_phone)
    elif call.data == "email":
        bot.send_message(call.message.chat.id, "Введите новый email:")
        bot.register_next_step_handler(call.message, get_new_email)
    elif call.data == "description":
        bot.send_message(call.message.chat.id, "Введите новое описание:")
        bot.register_next_step_handler(call.message, get_new_description)
def get_new_name(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE doctors SET name = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(message.chat.id, "Имя успешно изменено.")
    profile_doc(message)
def get_new_phone(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE doctors SET phone = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(message.chat.id, "Номер телефона успешно изменён.")
    profile_doc(message)
def get_new_email(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE doctors SET email = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(message.chat.id, "Email успешно изменён.")
    profile_doc(message)
def get_new_description(message):
    conn, cursor = connect_db()
    cursor.execute('''UPDATE doctors SET description = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(message.chat.id, "Описание успешно изменено.")
    profile_doc(message)

def profile_pat(message, call):
    try:
        id = call.from_user.id
    except AttributeError:
        id = message.from_user.id
    marcup = types.InlineKeyboardMarkup(row_width=2)
    doc = types.InlineKeyboardButton(text="Записаться к врачу", callback_data="doc_reg")
    chats = types.InlineKeyboardButton(text="Чаты", callback_data="pat_chats")
    marcup.add(doc, chats)
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (id,))
    patient = cursor.fetchone()
    if patient:
        bot.send_message(id, text="Ваш профиль:\n"
                         "Имя: {}\n"
                         "Телефон: {}\n"
                         "Email: {}".format(
            patient[2], patient[4], patient[5]),
        reply_markup=marcup)

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
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите напровление:", reply_markup=marcup)

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
            cursor.execute('''SELECT * FROM doctors WHERE user_id = ? AND verification_status = ?''', (doctor_id, 'verified'))
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
        bot.send_message(message.chat.id, "Врачи не найдены.")
    else:
        marcup = types.InlineKeyboardMarkup(row_width=3)
        sort1 = types.InlineKeyboardButton(text="По рейтингу", callback_data="sort1")
        sort2 = types.InlineKeyboardButton(text="По цене", callback_data="sort2")
        sort3 = types.InlineKeyboardButton(text="По опыту", callback_data="sort3")
        back = types.InlineKeyboardButton(text="Назад", callback_data="doc_reg")
        marcup.add(sort1, sort2, sort3, back)
        #создаем текст для отправки
        text = "Врачи:\n"
        t = 1
        for doc in doctor:
            text += f"{t}. Имя: {doc[2]}\nСтаж: {doc[11]}\nРейтинг: {doc[10]}\n\n"
            t += 1
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=marcup)
            


def doc_card(message, call, doctor, msg):
    msg = int(msg) - 1
    print(doctor[msg])
    doctors = doctor[msg][3]
    print('doc', doctors)  
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM specialisation WHERE user_id = ?''', (doctor[msg][1],))
    specialization = cursor.fetchall()
    print('spec', specialization)
    specialization_coun = int(len(specialization))
    print('spec1', specialization_coun)
    marcup = types.InlineKeyboardMarkup(row_width=2)
    back = types.InlineKeyboardButton(text="Назад", callback_data="doc_reg")
    consult = types.InlineKeyboardButton(text="Записаться на консультацию", callback_data="consult_{}".format(doctor[msg][1]))
    marcup.add(consult, back)
    if doctors != None:
        print(doctor[msg][3])
        with open(doctor[msg][3], 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=f"Имя: {doctor[msg][2]}\n"
                                                           f"Специальность: {doctor[msg][7]}\n"
                                                           f"Стаж: {doctor[msg][11]}\n"
                                                           f"Рейтинг: {doctor[msg][10]}\n"
                                                           f"Цена: {specialization[0][4]}\n")
    else:
        text=f"Имя: {doctor[msg][2]}\n"f"Стаж: {doctor[msg][11]}\n"f"Рейтинг: {doctor[msg][10]}\n"
        for specialization in specialization:
            text += f"Специальность: {specialization[3]}\n"
            text += f"Цена: {specialization[4]}\n\n"
            
        bot.send_message(message.chat.id, text=text, reply_markup=marcup)
    

def get_consultation_date(message):
    id_consult = random.randint(100000, 999999)
    marcup = types.InlineKeyboardMarkup(row_width=2)
    approve = types.InlineKeyboardButton(text="Подтвердить", callback_data=f"approve{id_consult}")
    cancel = types.InlineKeyboardButton(text="Отменить", callback_data=f"cancel{id_consult}")
    marcup.add(approve, cancel)
    conn, cursor = connect_db()
    cursor.execute('''SELECT data FROM temporary_data WHERE user_id = ?''', (message.from_user.id,))
    doctor_id = cursor.fetchone()
    print(doctor_id)
    if doctor_id:
        doctor_id = doctor_id[0]
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (doctor_id,))
        doctor = cursor.fetchone()
        print(doctor)
        if doctor:
            
            bot.send_message(message.chat.id, f"Вы записаны на консультацию к врачу {doctor[2]}.\n"
                                               f"Ваше сообщение: {message.text}")
            bot.send_message(doctor_id, f"Пациент {message.from_user.id} записался на консультацию.\n"
                                         f"Сообщение: {message.text}", reply_markup=marcup)
            # Здесь можно добавить логику для записи на консультацию
            total_price = cursor.execute('''SELECT price FROM specialisation WHERE user_id = ?''', (doctor_id,)).fetchone()
            total_price = total_price[0]
            print('price', total_price)
            print('id', message.from_user.id)
                                                                                                                                       ### не забыть поменять \/\/\/\/\/ ###
            cursor.execute('''INSERT INTO consultations (identifier, doctor_id, patient_id, description, total_price) VALUES (?, ?, ?, ?, ?)''', (id_consult, doctor_id, message.from_user.id, message.text, total_price))
            conn.commit()
            cursor.execute('''DELETE FROM temporary_data WHERE user_id = ?''', (message.from_user.id,))
            conn.commit()
        else:
            bot.send_message(message.chat.id, "Врач не найден.")
    else:
        bot.send_message(message.chat.id, "Ошибка получения данных врача.")


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
        cursor.execute('''INSERT INTO chats (consultation_id, doctor_id, patient_id) VALUES (?, ?, ?)''', (consultation[1], consultation[2], consultation[3]))
        conn.commit()
        bot.send_message(consultation[2], "Чат создан.")
        bot.send_message(consultation[3], "Чат создан.")
        # Здесь можно добавить логику для создания чата
    else:
        bot.send_message(call.message.chat.id, "Ошибка создания чата.")

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
            chat_button = types.InlineKeyboardButton(text=f"Чат с {patient[2] if call.data == "doc_chats" else doctor[2]}", callback_data=f"chat_{chat[1]}_1" if call.data == "doc_chats" else f"chat_{chat[1]}_2")
            marcup.add(chat_button)
    back = types.InlineKeyboardButton(text="Назад", callback_data=f"{'back_doc'if call.data == "doc_chats" else "back_pat"}")
    marcup.add(back)
    print('chats', chats)
    #выводим список чатов
    if len(chats) == 0:
        bot.send_message(message.chat.id, "Чаты не найдены.")
    else:
        text = "Чаты:\n"
        for chat in chats:
            cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (chat[1],))
            consultation = cursor.fetchone()
            if consultation:
                text += f"Консультация: {consultation[1]}\n"
                text += f"Пациент: {patient[2]}\n"
                text += f"Врач: {doctor[2]}\n\n"
        bot.send_message(message.chat.id, text=text, reply_markup=marcup)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Чаты", reply_markup=None)

def start_chat(call):
    marcup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    text = types.KeyboardButton(text="Отправить сообщение")
    img = types.KeyboardButton(text="Отправить фото")
    video = types.KeyboardButton(text="Отправить видео")
    audio = types.KeyboardButton(text="Отправить аудио-сообщение")
    end_consult = types.KeyboardButton(text="Завершить консультацию")
    back = types.KeyboardButton(text="Назад")
    marcup.add(text, img, video, audio, end_consult, back)
    bot.send_message(call.message.chat.id, "Выберите действие:", reply_markup=marcup)

@bot.message_handler(content_types=['text', 'photo', 'video', 'audio'])
def handle_message(message):
    if message.text == "Отправить сообщение":
        bot.send_message(message.chat.id, "Введите ваше сообщение:")
        bot.register_next_step_handler(message, send_text_message)
    elif message.text == "Отправить фото":
        bot.send_message(message.chat.id, "Отправьте фото:")
        bot.register_next_step_handler(message, send_photo_message)
    elif message.text == "Отправить видео":
        bot.send_message(message.chat.id, "Отправьте видео:")
        bot.register_next_step_handler(message, send_video_message)
    elif message.text == "Отправить аудио-сообщение":
        bot.send_message(message.chat.id, "Отправьте голосовое-собщение:")
        bot.register_next_step_handler(message, send_vocie_message)
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

def send_text_message(message):
    conn, cursor = connect_db()
    pac_dont_chat = 1
    doc_dont_chat = 1
    print('message', message.from_user.id)
    try:
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
        data_pac = cursor.fetchone()
        print('data', data_pac)
        active_chat_id = data_pac[8]
        name = data_pac[2]
    except TypeError:
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        data_doc = cursor.fetchone()
        print('data', data_doc)
        active_chat_id = data_doc[12]
        name = data_doc[2]
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
    cursor.execute('''SELECT messages FROM chats WHERE id = ?''', (active_chat_id,))
    row = cursor.fetchone()
    if row:
        messages = json.loads(row[0])
    else:
        messages = []
    
    if chat:
        if chat[2] == message.from_user.id and doc_dont_chat:
            bot.send_message(chat[3], text = f'Сообщение от пациента {name}\n {message.text}')  # Отправляем сообщение врачу
            print('Сообщение от пациента', message.text)
            messages.append({
                "sender": "patient",
                "text": message.text,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id and pac_dont_chat:
            bot.send_message(chat[2], text = f'Сообщение от врача {name}\n {message.text}')
            messages.append({
                "sender": "doctor",
                "text": message.text,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id:
            bot.send_message(chat[3], text = f'Сообщение от пациента {name}')
            messages.append({
                "sender": "patient",
                "text": message.text,
                "timestamp": datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id:
            bot.send_message(chat[2], text = f'Сообщение от врача {name}')
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

    else:
        bot.send_message(message.chat.id, "Чат не найден.")

def send_photo_message(message):
    conn, cursor = connect_db()
    pac_dont_chat = 1
    doc_dont_chat = 1
    try:
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
        data_pac = cursor.fetchone()
        active_chat_id = data_pac[8]
        name = data_pac[2]
    except TypeError:
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        data_doc = cursor.fetchone()
        active_chat_id = data_doc[12]
        name = data_doc[2]
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
        pac_dont_chat = 0
        if active_chat_id == None:
            doc_dont_chat = 0
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    #active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
    active_chat_id = cursor.fetchone()
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    chat = cursor.fetchone()
    print('chat', chat)
    cursor.execute('''SELECT messages FROM chats WHERE id = ?''', (active_chat_id,))
    row = cursor.fetchone()
    if row:
        messages = json.loads(row[0])
    else:
        messages = []
    
    if chat:
        if chat[2] == message.from_user.id and doc_dont_chat:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/photos/{message.photo[-1].file_id}.jpg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_photo(chat[3], photo=open(local_path, 'rb'), caption=f'Сообщение от пациента {name}')
            messages.append({
            "sender": "patient",
            "text": f'Сообщение от пациента {name}',
            "photo": local_path,
            "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id and pac_dont_chat:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/photos/{message.photo[-1].file_id}.jpg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_photo(chat[2], photo=open(local_path, 'rb'), caption=f'Сообщение от врача {name}')
            messages.append({
                "sender": "doctor",
                "text": f'Сообщение от врача {name}',
                "photo": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/photos/{message.photo[-1].file_id}.jpg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_photo(chat[3], photo=open(local_path, 'rb'), caption=f'Сообщение от пациента {name}')
            messages.append({
                "sender": "patient",
                "text": f'Сообщение от пациента {name}',
                "photo": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)
            local_path = f"media/photos/{message.photo[-1].file_id}.jpg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_photo(chat[2], photo=open(local_path, 'rb'), caption=f'Сообщение от врача {name}')
            messages.append({
                "sender": "doctor",
                "text": f'Сообщение от врача {name}',
                "photo": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        # сохраняем сообщение в json в базе данных
        messages_json = json.dumps(messages, ensure_ascii=False)
        cursor.execute('''UPDATE chats SET messages = ? WHERE consultation_id = ?''', (messages_json, active_chat_id))
        conn.commit()
        print('Сообщение сохранено в базе данных', messages_json)
    else:
        bot.send_message(message.chat.id, "Чат не найден.")

def send_video_message(message):
    conn, cursor = connect_db()
    pac_dont_chat = 1
    doc_dont_chat = 1
    try:
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
        data_pac = cursor.fetchone()
        active_chat_id = data_pac[8]
        name = data_pac[2]
    except TypeError:
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        data_doc = cursor.fetchone()
        active_chat_id = data_doc[12]
        name = data_doc[2]
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
        pac_dont_chat = 0
        if active_chat_id == None:
            doc_dont_chat = 0
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    #active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
    active_chat_id = cursor.fetchone()
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    chat = cursor.fetchone()
    print('chat', chat)
    cursor.execute('''SELECT messages FROM chats WHERE id = ?''', (active_chat_id,))
    row = cursor.fetchone()
    if row:
        messages = json.loads(row[0])
    else:
        messages = []
    
    if chat:
        if chat[2] == message.from_user.id and doc_dont_chat:
            file_info = bot.get_file(message.video.file_id)
            file_path = file_info.file_path
            downloaded_file= bot.download_file(file_path)
            local_path = f"media/videos/{message.video.file_id}.mp4"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_video(chat[3], video=open(local_path, 'rb'), caption=f'Сообщение от пациента {name}')
            messages.append({
                "sender": "patient",
                "text": f'Сообщение от пациента {name}',
                "video": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id and pac_dont_chat:
            file_info = bot.get_file(message.video.file_id)
            file_path = file_info.file_path
            downloaded_file= bot.download_file(file_path)
            local_path = f"media/videos/{message.video.file_id}.mp4"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_video(chat[2], video=open(local_path, 'rb'), caption=f'Сообщение от врача {name}')
            messages.append({
                "sender": "doctor",
                "text": f'Сообщение от врача {name}',
                "video": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id:
            file_info = bot.get_file(message.video.file_id)
            file_path = file_info.file_path
            downloaded_file= bot.download_file(file_path)
            local_path = f"media/videos/{message.video.file_id}.mp4"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_video(chat[3], video=open(local_path, 'rb'), caption=f'Сообщение от пациента {name}')
            messages.append({
                "sender": "patient",
                "text": f'Сообщение от пациента {name}',
                "video": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id:
            file_info = bot.get_file(message.video.file_id)
            file_path = file_info.file_path
            downloaded_file= bot.download_file(file_path)
            local_path = f"media/videos/{message.video.file_id}.mp4"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_video(chat[2], video=open(local_path, 'rb'), caption=f'Сообщение от врача {name}')
            messages.append({
                "sender": "doctor",
                "text": f'Сообщение от врача {name}',
                "video": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        # сохраняем сообщение в json в базе данных
        messages_json = json.dumps(messages, ensure_ascii=False)
        cursor.execute('''UPDATE chats SET messages = ? WHERE consultation_id = ?''', (messages_json, active_chat_id))
        conn.commit()
        print('Сообщение сохранено в базе данных', messages_json)

def send_vocie_message(message):
    conn, cursor = connect_db()
    pac_dont_chat = 1
    doc_dont_chat = 1
    try:
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
        data_pac = cursor.fetchone()
        active_chat_id = data_pac[8]
        name = data_pac[2]
    except TypeError:
        cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        data_doc = cursor.fetchone()
        active_chat_id = data_doc[12]
        name = data_doc[2]
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
        pac_dont_chat = 0
        if active_chat_id == None:
            doc_dont_chat = 0
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    #active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT active_chat_id FROM patients WHERE user_id = ?''', (message.from_user.id,))
    active_chat_id = cursor.fetchone()
    if active_chat_id == None:
        cursor.execute('''SELECT active_chat_id FROM doctors WHERE user_id = ?''', (message.from_user.id,))
        active_chat_id = cursor.fetchone()
    if active_chat_id == None:
        bot.send_message(message.chat.id, "У вас нет активного чата. Пожалуйста, выберите врача и начните консультацию.")
        return
    active_chat_id = active_chat_id[0]
    cursor.execute('''SELECT * FROM chats WHERE consultation_id = ?''', (active_chat_id,))
    chat = cursor.fetchone()
    print('chat', chat)
    cursor.execute('''SELECT messages FROM chats WHERE id = ?''', (active_chat_id,))
    row = cursor.fetchone()
    if row:
        messages = json.loads(row[0])
    else:
        messages = []
    
    if chat:
        if chat[2] == message.from_user.id and doc_dont_chat:
            file_info = bot.get_file(message.voice.file_id)
            file_path = file_info.file_path
            downloaded_file= bot.download_file(file_path)        
            local_path = f"media/voice/{message.voice.file_id}.ogg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_voice(chat[3], voice=open(local_path, 'rb'), caption=f'Сообщение от пациента {name}')
            messages.append({
                "sender": "patient",
                "text": f'Сообщение от пациента {name}',
                "voice": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id and pac_dont_chat:
            file_info = bot.get_file(message.voice.file_id)
            file_path = file_info.file_path
            downloaded_file= bot.download_file(file_path)        
            local_path = f"media/voice/{message.voice.file_id}.ogg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_voice(chat[2], voice=open(local_path, 'rb'), caption=f'Сообщение от врача {name}')
            messages.append({
                "sender": "doctor",
                "text": f'Сообщение от врача {name}',
                "voice": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[2] == message.from_user.id:
            file_info = bot.get_file(message.voice.file_id)
            file_path = file_info.file_path
            downloaded_file= bot.download_file(file_path)        
            local_path = f"media/voice/{message.voice.file_id}.ogg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_voice(chat[3], voice=open(local_path, 'rb'), caption=f'Сообщение от пациента {name}')
            messages.append({
                "sender": "patient",
                "text": f'Сообщение от пациента {name}',
                "voice": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        elif chat[3] == message.from_user.id:
            file_info = bot.get_file(message.voice.file_id)
            file_path = file_info.file_path
            downloaded_file= bot.download_file(file_path)        
            local_path = f"media/voice/{message.voice.file_id}.ogg"
            with open(local_path, 'wb') as f:
                f.write(downloaded_file)
            bot.send_voice(chat[2], voice=open(local_path, 'rb'), caption=f'Сообщение от врача {name}')
            messages.append({
                "sender": "doctor",
                "text": f'Сообщение от врача {name}',
                "voice": local_path,
                "timestamp": datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            })
        # сохраняем сообщение в json в базе данных
        messages_json = json.dumps(messages, ensure_ascii=False)
        cursor.execute('''UPDATE chats SET messages = ? WHERE consultation_id = ?''', (messages_json, active_chat_id))
        conn.commit()


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    conn, cursor = connect_db()
    id_consult = cursor.execute('''SELECT identifier FROM consultations WHERE doctor_id = ?''', (call.from_user.id,)).fetchall()
    print('id', id_consult)
    print(call.from_user.id)
    bot.answer_callback_query(call.id)
    if call.data == "doctor":
        doc_reg(message=call.message, user_id=call.from_user.id)
    elif call.data == "patient":
        pat_reg(message=call.message, call=call)
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
        id = call.data.replace("consult_", "")
        conn, cursor = connect_db()
        cursor.execute('''INSERT INTO temporary_data (user_id, data) VALUES (?, ?)''', (call.from_user.id, id))
        conn.commit()
        bot.send_message(call.message.chat.id, "Опишите свою проблему:")
        bot.register_next_step_handler(call.message, get_consultation_date)
    elif call.data.startswith("approve"):
        id_consult = call.data.replace("approve", "")
        conn, cursor = connect_db()
        cursor.execute('''SELECT * FROM consultations WHERE identifier = ?''', (id_consult,))
        consultation = cursor.fetchone()
        if consultation:
            #нужна проверка, логика оплаты.
            bot.send_message(consultation[3], "Ваша консультация подтверждена.")
            bot.send_message(consultation[2], "Консультация подтверждена.")
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
            bot.send_message(consultation[3], "Ваша консультация отменена.")
            bot.send_message(consultation[2], "Консультация отменена.")
        else:
            bot.send_message(call.message.chat.id, "Консультация не найдена.")
    elif call.data.startswith("accept"):
        id = call.data.replace("accept_", "")
        print('id=', id)
        conn, cursor = connect_db()
        cursor.execute('''UPDATE doctors SET verification_status = ? WHERE user_id = ?''', ('verified', id))
        conn.commit()
        bot.send_message(id, "Ваша верификация прошла успешно.")
        bot.send_message(call.message.chat.id, "Верификация принята.")
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
                start_chat(call)
            else:
                bot.send_message(call.message.chat.id, "Консультация не найдена.")
        else:
            bot.send_message(call.message.chat.id, "Чат не найден.")




bot.polling(none_stop=True)