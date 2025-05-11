import telebot
import sqlite3
#import qrcode
#import cloudpayments
from telebot import types

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
        profile_doc(message)
    elif patient:
        profile_pat(message)
    else:
        marcup = types.InlineKeyboardMarkup(row_width=2)
        doc = types.InlineKeyboardButton(text="Доктор", callback_data="doctor")
        pat = types.InlineKeyboardButton(text="Пациент", callback_data="patient")
        marcup.add(doc, pat)
        bot.send_message(message.chat.id, "Выберите роль:", reply_markup=marcup)


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
    profile_doc(message)

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

def profile_doc(message):
    conn, cursor = connect_db()
    cursor.execute('''SELECT verification_status, balance FROM doctors WHERE user_id = ?''', (message.from_user.id,))
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
    
    cursor.execute('''SELECT * FROM doctors WHERE user_id = ?''', (message.from_user.id,))
    doctor = cursor.fetchone()
    cursor.execute('''SELECT name_ru FROM specialisation WHERE user_id = ?''', (message.from_user.id,))
    specialization = cursor.fetchone()
    
    if specialization:
        special_str = ','.join(specialization)
        specialization = special_str
    else:
        specialization = "Не выбрана"
    if doctor:
        bot.send_message(message.chat.id, text="Ваш профиль:\n"
                         "Имя: {}\n"
                         "Телефон: {}\n"
                         "Email: {}\n"
                         "Статус: {}\n"
                         "Баланс: {}\n"
                         "Специализации {}".format(
            doctor[2], doctor[4], doctor[5], '✅Подтверждён' if doctor[6] == 'verified' else '❌ Не подтверждён', doctor[10], specialization),
                          reply_markup=marcup)
    else:
        bot.send_message(message.chat.id, "Профиль не найден.")

#верификация

def doc_verification(message, call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Отправьте фото документов для верификации.")
    bot.register_next_step_handler(message, get_doc_verification)
def get_doc_verification(message):
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
        bot.send_message(ADMIN_ID, f"Новый запрос на верификацию {message.from_user.id}.")
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
    spec2 = types.InlineKeyboardButton(text="✅ Семейный врач" if "family_doctor" in specialization else "Семейный врач", callback_data="family_doctor")
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
            special += [' Терапевт']
        elif spec == 'family_doctor':
            special += [' Семейный врач']
        elif spec == 'pediatrician':
            special += [' Педиатр']
        elif spec == 'cardiologist':
            special += [' Кардиолог']
        elif spec == 'gastroenterologist':
            special += [' Гастроэнтеролог']
        elif spec == 'endocrinologist':
            special += [' Эндокринолог']
        elif spec == 'neurologist':
            special += [' Невролог']
        elif spec == 'allergist_immunologist':
            special += [' Аллерголог-иммунолог']
        elif spec == 'dermatologist':
            special += [' Дерматолог']
        elif spec == 'psychotherapist':
            special += [' Психотерапевт']
        elif spec == 'gynecologist':
            special += [' Гинеколог']
        elif spec == 'ophthalmologist':
            special += [' Офтальмолог']
        elif spec == 'dentist':
            special += [' Стоматолог']
        elif spec == 'psychiatrist':
            special += [' Психиатр']
    print(special)
    special = list(set(special))  # Убираем дубликаты
    special_str = ','.join(special)  # Преобразуем список в строку
    cursor.execute('''UPDATE specialisation SET name_ru = ? WHERE user_id = ?''', (special_str, call.from_user.id))
    conn.commit()
    cursor.execute('''SELECT name_ru FROM specialisation WHERE user_id = ?''', (call.from_user.id,))
    specialization = cursor.fetchone()
    if specialization:
        specialization = specialization[0].split(',')  # Преобразуем строку обратно в список
    print(specialization)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Вы выбрали {special_str}", reply_markup=None)
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
    for i in range(len(specialization)):
        cursor.execute('''UPDATE specialisation SET price = ? WHERE user_id = ? AND name = ?''', (prices[i], message.from_user.id, specialization[i]))
        conn.commit()
    bot.send_message(message.chat.id, "Стоимость успешно обновлена.")
    pr = cursor.execute('''SELECT name, price FROM specialisation WHERE user_id = ?''', (message.from_user.id,)).fetchall()
    print(pr)
    profile_doc(message)

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

def profile_pat(message):
    marcup = types.InlineKeyboardMarkup(row_width=2)
    doc = types.InlineKeyboardButton(text="Записаться к врачу", callback_data="doc_reg")
    chats = types.InlineKeyboardButton(text="Чаты", callback_data="pat_chats")
    marcup.add(doc, chats)
    conn, cursor = connect_db()
    cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (message.from_user.id,))
    patient = cursor.fetchone()
    if patient:
        bot.send_message(message.chat.id, text="Ваш профиль:\n"
                         "Имя: {}\n"
                         "Телефон: {}\n"
                         "Email: {}".format(
            patient[2], patient[4], patient[5]),
        reply_markup=marcup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
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
    elif call.data in ["therapist", "family_doctor", "pediatrician", "cardiologist", "gastroenterologist",
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
    elif call.data == "doc_chats":
        pass
    elif call.data == "edit_profile":
        edit_profile(message=call.message, call=call)





bot.polling(none_stop=True)