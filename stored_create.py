import os
import sqlite3
import random
from sql_create import rnd_username, rnd_password, rnd_sentence, rnd_date

def create_stored_template(session_id):
    connection = sqlite3.connect(f'db/temp/{session_id}.db')
    cursor = connection.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        bio TEXT,
        joined TEXT
    );
    CREATE TABLE IF NOT EXISTS rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT
    );
    ''')
    connection.commit()

    number_users = random.randint(4,8)
    users = []
    for i in range(number_users):
        username = rnd_username()
        password = rnd_password()
        bio = rnd_sentence(8)
        joined = rnd_date(2019, 2023)
        users.append((username, password, bio, joined))
    cursor.executemany(f"INSERT INTO users (username, password, bio, joined) VALUES (?, ?, ?, ?);", users)
    connection.commit()

    number_rates = random.randint(4, 8)
    for i in range(number_rates):
        cursor.execute(
            "INSERT INTO rates (content) VALUES (?);",
            (rnd_sentence(10),)
        )
    connection.commit()

if __name__ == "__main__":
    temp_path = 'db/temp'
    for db_name in os.listdir(temp_path):
        db_path = os.path.join(temp_path, db_name)
        os.remove(db_path)
    create_stored_template(session_id='test')