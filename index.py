import os
from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from hashlib import md5
from scripts.data import load_trie, load_pickle, get_path_above, json_load
from scripts.database import DataBase
from scripts.log import Logger
from scripts.key import search
from scripts.statistics import time_length, iteration_time, iteration_length

app = Flask(__name__)
auth = HTTPBasicAuth()


FULL_DICT = load_pickle(get_path_above('resources/full_dict.pickle'))
SYNONYMIZER = load_pickle(get_path_above('resources/synonymizer.pickle'))
TRIE = load_trie(get_path_above('resources/corpus.trie'))
TRIE_SLANG = load_trie(get_path_above('resources/slang.trie'))
LOGGER = Logger('logs')


def get_hash(input_str):
    return md5(input_str.encode()).hexdigest()


@auth.hash_password
def hash_password(password):
    return get_hash(password)


@auth.get_password
def get_password(username):
    database = DataBase()
    password = database.get_user(username)[1]
    return password


@app.route('/stat')
@auth.login_required
def get_statistic():
    files = []

    file_name = 'time_length.png'
    file_path = os.path.abspath('static\\'+file_name)
    time_length(LOGGER.log, file_path)
    files.append('/static/' + file_name)

    file_name = 'iteration_time.png'
    file_path = os.path.abspath('static\\'+file_name)
    iteration_time(LOGGER.log, file_path)
    files.append('/static/' + file_name)

    file_name = 'iteration_length.png'
    file_path = os.path.abspath('static\\'+file_name)
    iteration_length(LOGGER.log, file_path)
    # files.append('/static/' + file_name)

    return render_template('stat.html', stat_image=files, stat_table=LOGGER.log)


@app.route('/login/{}:{}'.format(b'<username>'.decode('utf-8'), b'<password>'.decode('utf-8')), methods=['GET'])
@auth.login_required
def login(username, password):
    database = DataBase()
    database.create_user(username, get_hash(password))
    return "Пользователь {} успешно создан".format(username)


@app.route('/load', defaults={'path': None})
@app.route('/load:<path>')
@auth.login_required
def logger_load(path=None):
    LOGGER.load_log(path)
    return "Лог загружен"


@app.route('/clear')
@auth.login_required
def logger_clear():
    LOGGER.clear_log()
    return "Лог очищен"


@app.route('/save')
@auth.login_required
def logger_save():
    return "Лог сохранен: %s" % LOGGER.save_log()


def get_result(el):
    res, info = search(el, FULL_DICT, SYNONYMIZER, TRIE, TRIE_SLANG)
    LOGGER.add_info(info)
    return res


@app.route('/test:<path>')
@auth.login_required
def test_search(path):
    test_list = json_load(path)
    for el in test_list:
        get_result(el)
    return "Тестирование завершено"


@app.route('/', methods=['GET', 'POST'])
def init():
    res = []
    input_value = request.form.get('hashtag', "")
    if input_value:
        res = get_result(input_value)
    return render_template('index.html', res=res, input_value=input_value)


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
    # app.run(host='192.168.1.71', port='50623')
    # app.debug = True
    # app.run(host='192.168.1.71')
    # app.run()
    # LOGGER.save_log()

