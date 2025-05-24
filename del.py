import sqlite3
import os


conn = sqlite3.connect("db.db", check_same_thread=False)
c = conn.cursor()

c.execute('''DELETE FROM temporary_data WHERE user_id = ?''', (2146048678))
conn.commit()