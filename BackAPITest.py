from flask import Flask, render_template, jsonify,abort
from flask import request
from flask_cors import CORS,cross_origin
from EventDBManagement import *
from UserdbManagement import *
from RecomendationDBManagement import *
from geopy.geocoders import Nominatim

import socket
import sqlite3
import json
host = socket.gethostbyname(socket.gethostname())
url_root = r'http://' + host + ':8080'
url_api = r'/api/v1.0'
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
url_rsc = {r"/": {"origins": url_root},
           url_api + r'/Events/<int:event_id>': {"origins": url_root + url_api + '/Events/<int:event_id>'},
           url_api + r'/Events': {"origins": url_root + url_api + "/Events"},
           url_api + r'/Users/login': {"origins": url_root + url_api + "/Users/login"},
           url_api + r'/Users/<int:user_id>': {"origins": url_root + url_api + "/Users/<int:user_id>"},
           url_api + r'/Users/signup': {'origins': url_root + url_api + '/Users/signup'},
           url_api + r'/Users/choose_tags': {'origins': url_root + url_api + '/Users/choose_tags'},
           url_api + r'/Users/send_link_by_email': {'origins': url_root + url_api + '/Users/send_link_by_email'},
           url_api + r'/Users/reset_password': {'origins': url_root + url_api + '/Users/reset_password'},
           url_api + r'/Events/search': {'origins': url_root + url_api + '//Events/search'}
           }
cors = CORS(app, resources=url_rsc)

user_manager = UserdbManagement()
event_manager = EventsDBManager()
rcmd_manager = RecomendationDBManagement()
geolocator = Nominatim(user_agent="Hangout Recommendation")


@app.route('/')
@cross_origin(origin=host, headers=['Content-Type','Authorization'])
def index():
    """
    root url, no use
    :return:
    """
    return render_template('home_page.html')


@app.route('/api/v1.0/Events/<int:event_id>', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_event(event_id=0):
    """
    Frontend gets event by its id, call 404 error if not found
    :param event_id:
    :return:
    """
    # event = list(filter(lambda t: t['event_id'] == event_id, event_manager.check_database()))
    event = event_manager.return_event(event_id)
    # 有的话，就返回列表形式包裹的这个元素，没有的话就报错404
    if len(event) == 0:
        abort(404)
    return jsonify({'event': event[0]})


@app.route('/api/v1.0/Events', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_random_event():
    """
    Frontend gets a list of events for homepage, call 404 error if not found
    :return:
    """
    event = event_manager.check_database()[:10] # to do
    if len(event) == 0:
        abort(404)
    return jsonify({'event': event})


@app.route('/api/v1.0/Users/login', methods=['GET', 'POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_login():
    user_info = {}
    if request.method == 'POST':
        if not request.json or 'user_id' not in request.json:
            abort(400)
        user_info = {
                'user_id': request.json['user_id'],
                'pword': request.json['pword']
        }
        if user_manager.user_authentication(user_info['user_id'], user_info['pword']):
            return jsonify({'user_online': user_info, 'state': True}), 201
        else:
            return jsonify({'user_online': user_info, 'state': False}), 201
    return jsonify({'user_online': user_info})


@app.route('/api/v1.0/Users/<int:user_id>', methods=['GET', 'PUT'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_profile(user_id=0):
    if request.method == 'GET':
        user = user_manager.return_user_data(user_id)
        if len(user) == 0:
            abort(404)
        preferred_events_id = rcmd_manager.get_recommendations_for_user()
        preferred_events = []
        for pair in preferred_events_id:
            preferred_events.append({'activity': event_manager.return_event(pair[0]),
                                    'score': pair[1]})
        return jsonify({'user': user[0], 'event': preferred_events})
    elif request.method == 'PUT':
        if not request.json:
            abort(400)
        # to do


@app.route('/api/v1.0/Users/signup', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_signup():
    user = {}
    return jsonify({'user_info': user, 'state': False})
    # to do


@app.route('/api/v1.0/Users/choose_tags', methods=['PUT'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_choose_tags():
    tags_chosen = []
    user = {}
    return jsonify({'user_info': user, 'tags': tags_chosen})
    # to do


@app.route('/api/v1.0/Users/send_link_by_email', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_post_email():
    email = ''
    return jsonify({'email': email, 'sending state': False})
    # to do


@app.route('/api/v1.0/Users/reset_password', methods=['PUT'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_reset_password():
    return jsonify({'reset state': False})
    # to do


@app.route('/api/v1.0/Events/search', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def event_search():
    if request.method == 'POST':
        if not request.json:
            abort(400)
        # to do
        events = []
        return jsonify({'events': events})
    else:
        abort(404)

# @app.route('/api/v1.0/tasks', methods=['POST'])
# @cross_origin(origin=host, headers=['Content-Type','Authorization'])
# def create_task():
# #如果请求里面没有json数据，或者json数据里面title的内容为空
#     if not request.json or not 'title' in request.json:
#         abort(400) #返回404错误
#     task = {
#         'id': tasks[-1]['id'] + 1, #取末尾tasks的id号+1
#         'title': request.json['title'], #title必须设置，不能为空。
#         'description': request.json.get('description', ""),
#         'done': False
#     }
#     tasks.append(task) #完了之后，添加这个task进tasks列表
#     return jsonify({'task': task}), 201
#
#
# @app.route('/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
# def update_task(task_id):
#     #检查是否有这个id数据
#     task = filter(lambda t: t['id'] == task_id, tasks)
#     if len(task) == 0:
#         abort(404)
#     #如果请求中没有附带json数据，则报错400
#     if not request.json:
#         abort(400)
#     #如果title对应的值，不是字符串类型，则报错400
#     if 'title' in request.json and type(request.json['title']) != 'str':
#         abort(400)
#     if 'description' in request.json and type(request.json['description']) is not 'str':
#         abort(400)
#     #检查done对应的值是否是布尔值
#     if 'done' in request.json and type(request.json['done']) is not bool:
#         abort(400)
#     #如果上述条件全部通过的话，更新title的值，同时设置默认值
#     task[0]['title'] = request.json.get('title', task[0]['title'])
#     task[0]['description'] = request.json.get('description', task[0]['description'])
#     task[0]['done'] = request.json.get('done', task[0]['done'])
#     #返回修改后的数据
#     return jsonify({'task': task[0]})
#
#
# @app.route('/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
# def delete_task(task_id):
#     #检查是否有这个数据
#     task = filter(lambda t: t['id'] == task_id, tasks)
#     if len(task) == 0:
#         abort(404)
#     #从tasks列表中删除这个值
#     tasks.remove(task[0])
#     #返回结果状态，自定义的result
#     return jsonify({'result': True})

if __name__ == '__main__':

    print(host)
    app.run(debug=True, host=host, port=8080)


