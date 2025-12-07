#Тут нужно кароче делать чтобы создавалась бд наша
import sqlite3
import random, os, string
from datetime import datetime, timedelta
import json

#tablesname хранит имена для таблиц
with open('tablesname.json', 'r') as json_data:
    tablesname = json.load(json_data)
    json_data.close

#Рандомная строка
def rnd_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

#Имя пользователя (имя)_(4 рандомных символа)
def rnd_username():
    prefixes = ['alex', 'vasily', 'kate', 'sasha', 'ivan', 'anna', 'oleg', 'lena', 'max']
    return random.choice(prefixes) + '_' + rnd_string(4)

#Либо простой пароль либо рандом из 6 символов
def rnd_password():
    return random.choice(['12345', 'qwerty', 'password', 'admin', 'root', 'eazypswrd']) if random.random() < 0.5 else rnd_string(6)

#кол-во
def rnd_amount():
    return round(random.uniform(5, 5000), 2)

#Рандомное месево из слов (био)
def rnd_sentence(words=6):
    samples = ["secure", "fast", "hello", "profile", "order", "message", "private", "test"]
    return " ".join(random.choice(samples) for i in range(words))

#Случайная дата от start_year года до end_year года (не включительно) (2024-04-20)
def rnd_date(start_year=2020, end_year=2021):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 1, 1)
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    return random_date.strftime("%Y-%m-%d")

#рандомная соц.сеть
def create_social_template(session_id):
    connection = sqlite3.connect(f'db/temp/{session_id}.db')
    cursor = connection.cursor()
    
    userstable = random.choice(tablesname["userstable"])
    poststable = random.choice(tablesname["poststable"])
    messagestable = random.choice(tablesname["messagestable"])
    
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS ''' + userstable + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        bio TEXT,
        joined TEXT
    );
    CREATE TABLE IF NOT EXISTS ''' + poststable + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        created TEXT
    );
    CREATE TABLE IF NOT EXISTS ''' + messagestable + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user INTEGER,
        to_user INTEGER,
        body TEXT,
        created TEXT
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
    cursor.executemany(f"INSERT INTO {userstable} (username, password, bio, joined) VALUES (?, ?, ?, ?);", users)
    connection.commit()

    number_posts = random.randint(8, 20)
    for i in range(number_posts):
        cursor.execute(
            f"INSERT INTO {poststable} (user_id, content, created) VALUES (?, ?, ?);",
            (random.randint(1, number_users), rnd_sentence(10), rnd_date(2024, 2025))
        )

    number_messages = random.randint(7, 16)
    for i in range(number_messages):
        cursor.execute(
            f"INSERT INTO {messagestable} (from_user, to_user, body, created) VALUES (?, ?, ?, ?);",
            (random.randint(1, number_users), random.randint(1, number_users), rnd_sentence(10), rnd_date(2024, 2025))
        )

    connection.commit()

    #Создание задания и вывод result
    task_types = [
        "find_password_of_user",
        "find_bio_of_user",
        "find_post_content",
        "find_message_body"
    ]
    task_type = random.choice(task_types)

    cursor.execute(f"SELECT id, username FROM {userstable};")
    users_list = cursor.fetchall()

    cursor.execute(f"SELECT id FROM {poststable};")
    posts_list = [r[0] for r in cursor.fetchall()]

    cursor.execute(f"SELECT id FROM {messagestable};")
    msgs_list = [r[0] for r in cursor.fetchall()]

    result = {
        "task_type": task_type,
        "task_descr": None,
        "flag": None, #сам флаг
        "flag_location": None, #чота типа подсказки, мб вообще не понадобится
        "userstable": userstable
    }

    if task_type == "find_password_of_user":
        target_row = random.choice(users_list)
        target_id, target_username = target_row
        cursor.execute(f"SELECT password FROM {userstable} WHERE id = ?;", (target_id,))
        target_password = cursor.fetchone()[0]

        result["task_descr"] = f"Узнать пароль пользователя {target_username}."
        result["flag"] = target_password
        result["flag_location"] = f"{userstable}.password (user_id={target_id})"
    elif task_type == "find_bio_of_user":
        target_row = random.choice(users_list)
        target_id, target_username = target_row

        secret =  f"secret_phrase_{rnd_string(6)}"
        cursor.execute(f"UPDATE {userstable} SET bio = bio || ? WHERE id = ?;", (f" [SECRET:{secret}]", target_id))
        connection.commit()
        
        result["task_descr"] = f"В био пользователя {target_username} спрятана секретная фраза - найдите её."
        result["flag"] = secret
        result["flag_location"] = f"{userstable}.bio (user_id={target_id})"
    elif task_type == "find_post_content":
        target_post = random.choice(posts_list)

        secret = f"post_secret_{rnd_string(6)}"
        cursor.execute(f"UPDATE {poststable} SET content = content || ? WHERE id = ?;", (f" [FLAG:{secret}]", target_post))
        connection.commit()

        result["task_descr"] = f"Найдите скрытый флаг в содержимом поста с id = {target_post}."
        result["flag"] = secret
        result["flag_location"] = f"posts.content (post_id={target_post})"
    elif task_type == "find_message_body":
        target_msg = random.choice(msgs_list)

        secret = f"msg_secret_{rnd_string(6)}"
        cursor.execute(f"UPDATE {messagestable} SET body = body || ? WHERE id = ?;", (f" [FLAG:{secret}]", target_msg))
        connection.commit()

        result["task_descr"] = f"В приватном сообщении с id = {target_msg} спрятан код, получите его."
        result["flag"] = secret
        result["flag_location"] = f"messages.body (message_id = {target_msg})"

    cursor.close()
    connection.close()
    return result

#рандомный банк
def create_bank_template(session_id):
    connection = sqlite3.connect(f'db/temp/{session_id}.db')
    cursor = connection.cursor()
    
    userstable = random.choice(tablesname["userstable"])
    accountstable = random.choice(tablesname["accountstable"])
    transactionstable = random.choice(tablesname["transactionstable"])
    admin_notes_table = random.choice(tablesname["admin_notes_table"])

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS ''' + userstable + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        login TEXT,
        password TEXT
    );
    CREATE TABLE IF NOT EXISTS ''' + accountstable + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        balance REAL,
        account_number TEXT,
        created TEXT
    );
    CREATE TABLE IF NOT EXISTS ''' + transactionstable + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        amount REAL,
        timestamp TEXT,
        description TEXT
    );
    CREATE TABLE IF NOT EXISTS ''' + admin_notes_table + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note TEXT
    );
    ''')
    connection.commit()

    number_users = random.randint(4,8)
    users = []
    for i in range(number_users):
        name = rnd_username()
        login = f"user{rnd_string(4)}"
        password = rnd_password()
        users.append((name, login, password))
    cursor.executemany(f"INSERT INTO {userstable} (username, login, password) VALUES (?, ?, ?);", users)
    connection.commit()

    #accounts
    for user_id in range(1, number_users+1):
        account_number = "AC" + rnd_string(10)
        balance = rnd_amount()
        cursor.execute(f"INSERT INTO {accountstable} (customer_id, balance, account_number, created) VALUES (?, ?, ?, ?);",
                       (user_id, account_number, balance, rnd_date(2000, 2010)))
    connection.commit()

    #transactions
    for i in range(random.randint(8, 20)):
        cursor.execute(f"INSERT INTO {transactionstable} (account_id, amount, timestamp, description) VALUES (?, ?, ?, ?);",
                       (random.randint(1, number_users), rnd_amount()*random.choice([1, -1]), rnd_date(2009, 2020), rnd_sentence(6)))
    connection.commit()

    #admin_notes
    cursor.execute(f"INSERT INTO {admin_notes_table} (note) VALUES (?);", (rnd_sentence(8),))
    connection.commit()

    task_types = ["get_customer_password", "get_account_number", "get_admin_note"]
    task_type = random.choice(task_types)

    cursor.execute(f"SELECT id, username FROM {userstable};")
    users_list = cursor.fetchall()

    cursor.execute(f"SELECT id FROM {accountstable};")
    accounts_list = [r[0] for r in cursor.fetchall()]

    cursor.execute(f"SELECT id FROM {transactionstable};")
    transactions_list = [r[0] for r in cursor.fetchall()]

    cursor.execute(f"SELECT id FROM {admin_notes_table};")
    admin_notes_list = [r[0] for r in cursor.fetchall()]

    result = {
        "task_type": task_type,
        "task_descr": None,
        "flag": None, #сам флаг
        "flag_location": None, #чота типа подсказки, мб вообще не понадобится
        "userstable": userstable
    }

    if task_type == "get_customer_password":
        target_row = random.choice(users_list)
        target_id, target_username = target_row
        cursor.execute(f"SELECT password FROM {userstable} WHERE id = ?;", (target_id,))
        target_password = cursor.fetchone()[0]
        result["task_descr"] = f"Узнать пароль пользователя {target_username}."
        result["flag"] = target_password
        result["flag_location"] = f"{userstable}.password (user_id={target_id})"
    elif task_type == "get_account_number":
        target_row = random.choice(accounts_list)
        target_id = target_row
        cursor.execute(f"SELECT customer_id FROM {accountstable} WHERE id = ?;", (target_id,))
        customer_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT account_number FROM {accountstable} WHERE customer_id = ?;", (customer_id,))
        accnumber = cursor.fetchone()[0]
        cursor.execute(f"SELECT username FROM {userstable} WHERE id = ?;", (customer_id,))
        customer_name = cursor.fetchone()[0]

        result["task_descr"] = f"Узнать номер счёта клиента {customer_name}."
        result["flag"] = accnumber
        result["flag_location"] = f"accounts.account_number (customer_id={customer_id})"
    elif task_type == "get_admin_note":
        target_note = random.choice(admin_notes_list)
        secret_text = f"admin_secret_{rnd_string(6)}"
        cursor.execute(f"UPDATE {admin_notes_table} SET note = note || ? WHERE id = ?;", (f" [FLAG:{secret_text}]", target_note))
        connection.commit()

        result["task_descr"] = f"Внутри записки админа с id={target_note} спрятан код - получите его."
        result["flag"] = secret_text
        result["flag_location"] = f"admin_notes.note (id={target_note})"

    cursor.close()
    connection.close()
    return result

#рандомный шаблон магазина
def create_shop_template(session_id):
    connection = sqlite3.connect(f'db/temp/{session_id}.db')
    cursor = connection.cursor()
    
    userstable = random.choice(tablesname["userstable"])
    productstable = random.choice(tablesname["productstable"])
    orderstable = random.choice(tablesname["orderstable"])
    reviewstable = random.choice(tablesname["reviewstable"])

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS ''' + userstable + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT NOT NULL,
        bio TEXT
    );
    CREATE TABLE IF NOT EXISTS ''' + productstable + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL
    );
    CREATE TABLE IF NOT EXISTS ''' + orderstable + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        order_notes TEXT
    );
    CREATE TABLE IF NOT EXISTS ''' + reviewstable + ''' (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        customer_id INTEGER,
        content TEXT
    );
    ''')
    connection.commit()

    n_users = random.randint(3, 7)
    for i in range(n_users):
        cursor.execute(f"INSERT INTO {userstable} (username, password, bio) VALUES (?, ?, ?);",
                       (f"{rnd_string(6)}@yandex.ru", rnd_password(), rnd_sentence(8)))
    connection.commit()

    n_prod = random.randint(5, 12)
    for i in range(n_prod):
        cursor.execute(f"INSERT INTO {productstable} (name, description, price) VALUES (?, ?, ?);",
                       (f"Product {rnd_string(4)}", rnd_sentence(10), rnd_amount()))
    connection.commit()

    #orders
    for i in range(random.randint(6, 18)):
        cursor.execute(f"INSERT INTO {orderstable} (customer_id, product_id, order_notes) VALUES (?, ?, ?);",
                       (random.randint(1, n_users), random.randint(1, n_prod), rnd_sentence(8)))
    connection.commit()

    #reviews
    for i in range(random.randint(4, 12)):
        cursor.execute(f"INSERT INTO {reviewstable} (product_id, customer_id, content) VALUES (?, ?, ?);",
                       (random.randint(1, n_prod), random.randint(1, n_users), rnd_sentence(12)))
    connection.commit()

    task_types = ["find_customer_password", "find_order_note", "find_product_price"]
    task_type = random.choice(task_types)

    cursor.execute(f"SELECT id, username FROM {userstable};")
    users_list = cursor.fetchall()
    cursor.execute(f"SELECT id FROM {productstable};")
    products_list = [r[0] for r in cursor.fetchall()]
    cursor.execute(f"SELECT id FROM {orderstable};")
    orders_list = [r[0] for r in cursor.fetchall()]
    cursor.execute(f"SELECT id FROM {reviewstable};")
    reviews_list = [r[0] for r in cursor.fetchall()]

    result = {
        "task_type": task_type,
        "task_descr": None,
        "flag": None, #сам флаг
        "flag_location": None, #чота типа подсказки, мб вообще не понадобится
        "userstable": userstable
    }

    if task_type == "find_customer_password":
        target_row = random.choice(users_list)
        target_id, target_email = target_row
        cursor.execute(f"SELECT password FROM {userstable} WHERE id = ?;", (target_id,))
        target_password = cursor.fetchone()[0]

        result["task_descr"] = f"Узнать пароль пользователя с почтой {target_email}"
        result["flag"] = target_password
        result["flag_location"] = f"customers.password (email={target_email})"
    elif task_type == "find_order_note":
        target_order = random.choice(orders_list)
        secret_text = f"order_secret_{rnd_string(6)}"
        cursor.execute(f"UPDATE {orderstable} SET order_notes = order_notes || ? WHERE id = ?;", (f" [FLAG:{secret_text}]", target_order))
        connection.commit()
        
        result["task_descr"] = f"Найти секретную метку в заметке заказа id = {target_order}."
        result["flag"] = secret_text
        result["flag_location"] = f"orders.order_notes (order_id={target_order})"
    elif task_type == "find_product_price":
        target_product = random.choice(products_list)
        cursor.execute(f"SELECT price FROM {productstable} WHERE id = ?;", (target_product,))
        target_price = cursor.fetchone()[0]

        result["task_descr"] = f"Узнать цену товара id = {target_product}."
        result["flag"] = target_price
        result["flag_location"] = f"products.price (product_id={target_product})"
    
    cursor.close()
    connection.close()
    return result

if __name__ == '__main__':
    temp_path = 'db/temp'
    for db_name in os.listdir(temp_path):
        db_path = os.path.join(temp_path, db_name)
        os.remove(db_path)
    print(create_shop_template(session_id='test'))