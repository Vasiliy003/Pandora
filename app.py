from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, exc
import uuid, random, time, os, threading, string
import sqlite3
from sql_create import create_social_template, create_bank_template, create_shop_template
from stored_create import create_stored_template

from sessions_database import engine, SessionBase

app = Flask(__name__)
app.secret_key = "thhj;uirtjk;nfgdhb;jlknfgshkjn  mc xnfj ,klak  m"

TaskSession = sessionmaker(engine)
tasksession = TaskSession()

inactivity_timeout = 600

def is_inactivity():
    while True:
        time.sleep(10)
        current_time = datetime.now()
        rows = tasksession.query(SessionBase).all()
        for row in rows:
            create_time = datetime.strptime(row.last_activity, "%d.%m.%Y %H:%M:%S")
            delta = current_time - create_time
            if int(delta.total_seconds()) > inactivity_timeout:
                
                tasksession.delete(row)
                os.remove(f'db/temp/{row.session_id}.db')
                tasksession.commit()

def create_session(session_id, task, flag):
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user = SessionBase(session_id=session_id, task=task, flag=flag, last_activity=now)
    tasksession.add(user)

def get_by_sessionid(session_id):
    try:
        statement = select(SessionBase).where(SessionBase.session_id == session_id)
        db_object = tasksession.scalars(statement).one()
    except exc.NoResultFound:
        return None
    else:
        return db_object

def getRandFlag():
    length = random.randint(5, 10)
    return "".join(chr(random.randint(35, 125)) for i in range(length)) + chr(random.randint(65, 90)) + "".join(chr(random.randint(35, 125)) for i in range(length))

def closeSession(session_id):
    # убрать ключ из flask-session (если установлен)
    session.pop("session_id", None)

    db_path = f'db/temp/{session_id}.db'

    # Попытаться удалить файл с несколькими попытками — Windows не разрешает удалять
    # файл, пока на него есть открытые дескрипторы. Повторяем с небольшими паузами.
    for attempt in range(6):
        try:
            # принудительный сборщик мусора на случай, если где-то остались ссылки
            import gc
            gc.collect()
            if os.path.exists(db_path):
                os.remove(db_path)
            break
        except PermissionError as e:
            if attempt == 5:
                # не удалось удалить — логируем и продолжаем удаление записи из БД
                print(f"closeSession: не удалось удалить {db_path}: {e}")
            time.sleep(0.15)
        except FileNotFoundError:
            break
        except Exception as e:
            print(f"closeSession: unexpected error removing {db_path}: {e}")
            break

    object_to_delete = get_by_sessionid(session_id)
    if object_to_delete:
        tasksession.delete(object_to_delete)
        tasksession.commit()
    print("Закрыли сессию")



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/csqltask")
def create_sql_task():
    session_id = str(uuid.uuid4()).replace('-', '')
    print(session_id)
    template_type = random.choice(["bank", "social", "shop"])
    if template_type == "bank":
        template = create_bank_template(session_id=session_id)
    elif template_type == "social":
        template = create_social_template(session_id=session_id)
    elif template_type == "shop":
        template = create_shop_template(session_id=session_id)
    task = template["task_descr"]
    rflag = template["flag"]
    print(rflag)

    try:
        create_session(session_id=session_id, task=task, flag=rflag)
    except:
        print('ошибка в создании сессии')
        tasksession.rollback()
        raise
    else:
        tasksession.commit()

    session["template_type"] = template_type
    session["userstable"] = template["userstable"]
    session["session_id"] = session_id

    return redirect(url_for("sql_task"))

@app.route("/sql", methods=['GET', 'POST'])
def sql_task():
    session_id = session.get("session_id")
    if not session_id:
        return redirect(url_for("create_sql_task"))
    session_object = get_by_sessionid(session_id=session_id)
    if not session_object:
        closeSession(session_id)
        return redirect(url_for("lose"))
    
    task = session_object.task
    iflag = request.args.get('flag')
    print(task) 
    print(session_object.flag)
    if iflag == session_object.flag:
        closeSession(session_id)
        return redirect(url_for("win"))
    
    template_type = session.get("template_type")
    
    message = None
    userstable = session.get("userstable")
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if username or password:
        raw_sql = f"SELECT id, username FROM {userstable} WHERE username = '{username}' AND password = '{password}';"
        try:
            connection = sqlite3.connect(f'db/temp/{session_id}.db')
            cursor = connection.cursor()
            cursor.execute(raw_sql)
            rows = cursor.fetchall()
            if rows:
                message = "<br>".join([str(r) for r in rows])
            else:
                message = "Ничего не найдено."
            cursor.close()
            connection.close()
        except Exception as e:
            return render_template(
                f'sql_{template_type}.html', task=task, start_time=session_object.last_activity, message=f"SQL error: {e}"
            )
    return render_template(f"sql_{template_type}.html", task=task, start_time=session_object.last_activity, message=message)

@app.route("/cxsstask")
def create_xss_task():
    session_id = str(uuid.uuid4()).replace('-', '')
    print(session_id)
    rflag = "FLAG{" + ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + "}"
    task_type = random.choice(["reflected", "stored", "dom"])
    if task_type == "stored":
        task_descr = "Добавьте отзыв так, чтобы при просмотре сообщения у вас отобразился код."
        create_stored_template(session_id)
    elif task_type == "reflected":
        task_descr = "Вставьте payload в незащищенное поле ввода, чтобы страница отобразила код."
    else:
        task_descr = "Используйте fragment/hash в URL (после #) для выполнения payload и получения кода."

    try:
        create_session(session_id=session_id, task=task_descr, flag=rflag)
    except:
        print('ошибка в создании сессии')
        tasksession.rollback()
        raise
    else:
        tasksession.commit()

    session["session_id"] = session_id
    session["task_type"] = task_type

    return redirect(url_for("xss_task"))

@app.route("/xss", methods=['GET', 'POST'])
def xss_task():
    session_id = session.get("session_id")
    if not session_id:
        return redirect(url_for("create_xss_task"))
    session_object = get_by_sessionid(session_id=session_id)
    if not session_object:
        closeSession(session_id)
        return redirect(url_for("lose"))
    
    task = session_object.task
    iflag = request.form.get("flag")
    print(task)
    print(session_object.flag)
    if iflag == session_object.flag:
        closeSession(session_id)
        return redirect(url_for("win"))
    
    task_type = session["task_type"]

    if task_type == "stored":
        rate = request.form.get("rate")
        connection = sqlite3.connect(f'db/temp/{session_id}.db')
        cursor = connection.cursor()
        if rate:
            cursor.execute("INSERT INTO rates (content) VALUES (?);", (rate,))
            connection.commit()
        
        cursor.execute("SELECT content FROM rates")
        rows = cursor.fetchall()
        rates = [row[0] for row in rows]

        cursor.close()
        connection.close()

        return render_template("xss_stored.html", task=task, start_time=session_object.last_activity, xss_flag = session_object.flag, rates = rates)
    elif task_type == "reflected":
        query = request.args.get("query", "")
        connection = sqlite3.connect(f'db/temp/{session_id}.db')
        connection.close()

        return render_template("xss_reflected.html", task=task, start_time=session_object.last_activity, query=query, xss_flag = session_object.flag)

    elif task_type == "dom":
        connection = sqlite3.connect(f'db/temp/{session_id}.db')
        connection.close()

        return render_template("xss_dom.html", task=task, start_time=session_object.last_activity, xss_flag = session_object.flag)

@app.route("/win")
def win():
    return render_template("win.html")

@app.route("/lose")
def lose():
    return render_template("lose.html")

if __name__ == "__main__":
    #Очищаем все сессии и временные бд
    rows = tasksession.query(SessionBase).all()
    for row in rows:
        tasksession.delete(row)
    tasksession.commit()
    temp_path = 'db/temp'
    for db_name in os.listdir(temp_path):
        db_path = os.path.join(temp_path, db_name)
        os.remove(db_path)
    
    #Запускаем ветку с очисткой просроченных сессий
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        inactivity_thread = threading.Thread(target=is_inactivity, daemon=True)
        inactivity_thread.start()

    app.run(debug=True)