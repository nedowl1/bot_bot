import sqlite3
import os


conn = sqlite3.connect("db.db", check_same_thread=False)
c = conn.cursor()
#1
c.execute('''INSERT INTO doctors (user_id, name, avatar, phone, email, description, verification_docs, verification_status, rating, balance, experience)
    VALUES (132, 'Иванов Иван', 'None', '+79999945999', 'hghffjds', 'Врач', 'None', 'verified', 0.0, 0.0, 3)''')
c.execute('''INSERT INTO specialisation (user_id, name, name_ru, price) VALUES (132, 'therapist', 'Терапевт', 999)''')
#2
c.execute('''INSERT INTO doctors (user_id, name, avatar, phone, email, description, verification_docs, verification_status, rating, balance, experience)
    VALUES (123, 'сергей сер', 'None', '+79999799999', 'hhghfjdd', 'Врач', 'None', 'verified', 0.0, 0.0, 4)''')
c.execute('''INSERT INTO specialisation (user_id, name, name_ru, price) VALUES (126, 'therapist', 'Терапевт', 999)''')
#3
c.execute('''INSERT INTO doctors (user_id, name, avatar, phone, email, description, verification_docs, verification_status, rating, balance, experience)
    VALUES (124, 'Петров Петр', 'None', '+79999899999', 'hghffjfds', 'Врач', 'None', 'verified', 0.0, 0.0, 5)''')
c.execute('''INSERT INTO specialisation (user_id, name, name_ru, price) VALUES (126, 'therapist', 'Терапевт', 999)''')
#4
c.execute('''INSERT INTO doctors (user_id, name, avatar, phone, email, description, verification_docs, verification_status, rating, balance, experience)
    VALUES (125, 'Сидоров Сидор', 'None', '+79999699999', 'hghfdfjds', 'Врач', 'None', 'verified', 0.0, 0.0, 6)''')
c.execute('''INSERT INTO specialisation (user_id, name, name_ru, price) VALUES (126, 'therapist', 'Терапевт', 999)''')
#5
c.execute('''INSERT INTO doctors (user_id, name, avatar, phone, email, description, verification_docs, verification_status, rating, balance, experience)
    VALUES (126, 'Сидоров Сидор', 'None', '+799996979999', 'hghffjdfs', 'Врач', 'None', 'verified', 0.0, 0.0, 6)''')
c.execute('''INSERT INTO specialisation (user_id, name, name_ru, price) VALUES (126, 'therapist', 'Терапевт', 999)''')

conn.commit()