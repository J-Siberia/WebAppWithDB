from datetime import datetime
import secrets
from hashlib import sha256
from flask import Flask, render_template, request, session, redirect, url_for
from bson.objectid import ObjectId
import redis
import pymongo
import re
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

def get_race(mongo_db, race_id):
    query = {'_id' : ObjectId(race_id)}
    return mongo_db.races.find_one(query)

def get_bookmark(mongo_db, user_id):
    query = {'user_id' : user_id}
    return mongo_db.bookmark.find(query)

def create_mongodb_connection():
    user = 'put_your_name'
    pwd = 'put_your_password'
    client = pymongo.MongoClient('put_MongoClient')
    db = client['db_number']
    return db

def create_redis_connection():
    conn = redis.Redis(host='localhost', port=-1, db=-1, password='put_your_password', charset="utf-8", decode_responses=True)
    return conn

def add_user(username, password):
    try:
        connection = mysql.connector.connect(
            host='host_ip_address',
            user='user_name',
            password='user_password',
            database='db_name'
        )
        cursor = connection.cursor()

        hashed_password = sha256(password.encode('utf-8')).hexdigest()

        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))

        connection.commit()
        return None
    except Error as e:
        error_message = "そのユーザ名は既に使用されています"
        return error_message
    finally:
        if connection.is_connected():
            connection.close()

def check_user(username, password):
    connection = mysql.connector.connect(
        host='host_ip_address',
        user='user_name',
        password='user_password',
        database='db_name'
    )
    cursor = connection.cursor()
    hashed_password = sha256(password.encode('utf-8')).hexdigest()
    cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, hashed_password))
    user = cursor.fetchone()
    connection.close()

    return user is not None

@app.route("/")
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = create_redis_connection()
    zset_data_desc = conn.zrevrange('race:votes', 0, 4, withscores=True)
    ranking_races=[]
    db = create_mongodb_connection()
    for member, score in zset_data_desc:
        append_data = get_race(db, member)
        append_data['score'] = int(score)
        ranking_races.append(append_data)
    return render_template('index.html', races=list(ranking_races), user=session['user'])

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('user', None)
    return render_template('login.html')

@app.route("/register", methods=["POST"])
def register():
    user_name = request.form["user_name"]
    password = request.form["password"]
    if check_user(user_name, password):
        session['user'] = user_name
        return redirect(url_for('index'))
    else:
        return render_template('login.html', mes='ユーザ名，もしくはパスワードが誤っています')
    
@app.route("/register_new", methods=["POST"])
def register_new():
    user_name = request.form["user_name"]
    password = request.form["password"]
    result = add_user(user_name, password)
    if result is None:
        if check_user(user_name, password):
            session['user'] = user_name
            return redirect(url_for('index'))
    else:
        return render_template('login.html', mes=result)
    
@app.route("/show_all_race", methods=["POST"])
def show_all_race():
    db = create_mongodb_connection()
    year = request.form['year']
    re_year = '^' + year + '.*'
    pattern = re.compile(re_year)
    query = {'race_date': {'$regex': pattern}} 
    result = db.races.find(query)
    return render_template('result.html', races=list(result))

@app.route("/show_race", methods=["POST"])
def show_race():
    db = create_mongodb_connection()
    query = {}
    if request.form['race_date']:
        date = request.form['race_date']
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y/%m/%d")
        query["race_date"] = formatted_date
    if request.form['course']:
        query["race_course"] = request.form['course']
    if request.form['place']:
        query["race_place"] = request.form['place']
    if request.form['race_distance']:
        query["race_distance"] = request.form['race_distance']
    if request.form['place_num']:
        query["place_num"] = request.form['place_num']
    if request.form['race_weather']:
        query["race_weather"] = request.form['race_weather']
    if request.form['race_condition']:
        query["race_condition"] = request.form['race_condition']
    if request.form['race_name']:
        re_name = '.*' + request.form['race_name'] +'.*'
        pattern = re.compile(re_name)
        query["race_name"] = {'$regex': pattern}
    result = db.races.find(query)
    return render_template('result.html', races=list(result.sort("race_date", pymongo.ASCENDING)))

@app.route("/race/<race_id>")
def detail(race_id):
    db = create_mongodb_connection()
    race = get_race(db, race_id)
    return render_template('detail.html', race = race)

@app.route("/vote", methods=["POST"])
def vote():
    race_id = request.form["race_id"]
    conn = create_redis_connection()
    if conn.sadd('race:votes:' + race_id, session['user']) == 1:
        conn.zincrby('race:votes', 1, race_id)
        mes = '投票が完了しました！'
    else:
        mes = '既に投票済みです。'
    db = create_mongodb_connection()
    race = get_race(db, race_id)
    return render_template('detail.html', race = race, mes = mes)

@app.route("/add_to_bookmark", methods=["POST"])
def add_to_bookmark():
    race_id = request.form["race_id"]
    db = create_mongodb_connection()
    new_document = {}
    new_document['race_id'] = race_id
    new_document['user_id'] = session['user']
    insert_result = db.bookmark.insert_one(new_document)
    if insert_result:
        race = get_race(db, race_id)
        return render_template('detail.html', race = race, mes = "お気に入り登録が完了しました！")
    else:
        return render_template('index.html', mes = "不明なエラーが発生しました。(add_to_bookmark)")

@app.route("/show_bookmark")
def show_bookmark():
    db = create_mongodb_connection()
    race_bookmark = get_bookmark(db, session['user'])
    race_id_bookmark = [doc['race_id'] for doc in race_bookmark]
    result = []
    for race_id in race_id_bookmark:
        match_race = db.races.find_one({'_id': ObjectId(race_id)})
        if match_race and (match_race not in result):
            result.append(match_race)
    sorted_result = sorted(result, key=lambda x: x['race_date'])
    return render_template('bookmark.html', races=sorted_result)

@app.route("/remove_from_bookmark", methods=["POST"])
def remove_bookmark():
    db = create_mongodb_connection()
    remove_id = request.form["remove_id"]
    del_result = db.bookmark.delete_one({"race_id": remove_id, "user_id": session['user']})
    if del_result:
        mes = "ブックマークから選択したレースを削除しました。"
    else:
        mes = "レースの削除に失敗しました。"
    race_bookmark = get_bookmark(db, session['user'])
    race_id_bookmark = [doc['race_id'] for doc in race_bookmark]
    result = []
    for race_id in race_id_bookmark:
        match_race = db.races.find_one({'_id': ObjectId(race_id)})
        if match_race and (match_race not in result):
            result.append(match_race)
    sorted_result = sorted(result, key=lambda x: x['race_date'])
    return render_template('bookmark.html', races=sorted_result, mes = mes)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=11021)
