from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, exc
import uuid, random, time, os, threading
import sqlite3
from sql_create import create_social_template, create_bank_template, create_shop_template

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
    session.pop(session_id, None)

    os.remove(f'db/temp/{session_id}.db')
    object_to_delete = get_by_sessionid(session_id)
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
            row = cursor.fetchone()
            connection.close()
            print(row)
        except Exception as e:
            return render_template(
                f'sql_{template_type}.html', task=task, start_time=session_object.last_activity, message=f"SQL error: {e}"
            )
        if row:
            message = row
    return render_template(f"sql_{template_type}.html", task=task, start_time=session_object.last_activity, message=message)

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