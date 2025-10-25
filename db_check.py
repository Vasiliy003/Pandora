import sqlite3

db_path = "db/temp/test.db"

# Подключаемся к базе
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Получаем список всех таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

if not tables:
    print("В базе данных нет таблиц.")
else:
    for table_name, in tables:
        print(f"\n=== Таблица: {table_name} ===")

        # Получаем названия столбцов
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]
        print("Столбцы:", ", ".join(columns))

        # Получаем все строки таблицы
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("(Таблица пуста)")

# Закрываем соединение
conn.close()