from flask import Flask, render_template, jsonify, abort
from flask import request
from flask_cors import CORS, cross_origin
from EventDBManagement import *
from UserdbManagement import *
from RecomendationDBManagement import *
from geopy.geocoders import Nominatim
from validate_email import validate_email
from BackendAPIStaticList import *

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources=url_rsc)

user_manager = UserdbManagement()
event_manager = EventsDBManager()
rcmd_manager = RecomendationDBManagement()
geolocator = Nominatim(user_agent="Hangout Recommendation")


@app.route('/')
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
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
    single_event = event_manager.return_event(event_id)
    # 有的话，就返回列表形式包裹的这个元素，没有的话就报错404
    if len(single_event) == 0:
        abort(404)
    return jsonify({'event': single_event[0]})


@app.route('/api/v1.0/Events', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_random_event():
    """
    Frontend gets a list of events for homepage, call 404 error if not found
    :return:
    """
    rdm_event = event_manager.return_ten_diff_events()  # to do
    if len(rdm_event) == 0:
        abort(404)
    return jsonify({'event': rdm_event})


@app.route('/api/v1.0/Events/Categories/<category>', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_event_by_category(category):
    """
    Frontend gets a list of events by selected category
    :return:
    """
    cate_event = event_manager.return_events_by_category(category)  # to do
    if len(cate_event) == 0 or category == '':
        abort(404)
    return jsonify({'event': cate_event})


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
            return jsonify({'user_online': user_info, 'login state': True,
                            'description': 'successfully log in'}), 201
        else:
            return jsonify({'user_online': user_info, 'state': False,
                            'description': 'wrong password'}), 201
    return jsonify({'user_online': user_info})


@app.route('/api/v1.0/Users/<uname>', methods=['GET', 'PUT'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_profile(uname=None):
    if request.method == 'GET':
        user = user_manager.return_user_data(uname)
        if len(user) == 0:
            abort(404)
        preferred_events_id = rcmd_manager.get_recommendations_for_user(user_manager.return_user_id(uname))
        preferred_events = []
        for pair in preferred_events_id:
            preferred_events.append({'activity': event_manager.return_event(pair[0]),
                                    'score': pair[1]})
        return jsonify({'user': user, 'event': preferred_events})
    elif request.method == 'PUT':
        if not request.json:
            abort(400)
        # to do


@app.route('/api/v1.0/Users/signup', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_signup():
    rj = request.json
    if not rj or 'uname' not in rj:
        abort(400)
    if rj['uname'] == '' or rj['pword'] == '' or rj['pword_r'] == '' or rj['email'] == '':
        return jsonify({'user_info': {}, 'signup state': False,
                        'description': 'obligatory field(s) missed'}), 201
    if rj['pword'] != rj['pword_r']:
        return jsonify({'user_info': {}, 'signup state': False,
                        'description': 'password verification failed'}), 201
    if not validate_email(rj['email'], verify=True):
        return jsonify({'user_info': {}, 'signup state': False,
                        'description': 'email not valid'}), 201
    if request.json['uname'] in user_manager.return_usernames():
        return jsonify({'user_info': {}, 'signup state': False,
                        'description': 'user name already existed'}), 201
    for u in user_manager.check_database():
        if request.json['email'] == u['email']:
            return jsonify({'user_info': {}, 'signup state': False,
                            'description': 'email already occupied by another account'}), 201
    user = {
        'uname': rj['uname'],
        'email': rj['email'],
        'city': rj['city']
    }
    user_manager.create_new_user(
        rj['uname'], rj['pword'], rj['email'], rj['address'], rj['city'], rj['latitude'], rj['longitude']
    )

    return jsonify({'user_info': user, 'state': True,
                    'description': 'successfully signed up. Start Visit Paris now!'})


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
    if not request.json or 'email' not in request.json:
        abort(400)
    email = request.json['email']
    if not email or not validate_email(email, verify=True):
        return jsonify({'sending state': False, 'description': 'email not valid'})
    link = request.json['link']
    send_email(email, link)
    return jsonify({'sending state': True, 'description': 'email sent'})


def send_email(email, link):
    return
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
        search = request.json
        # to do
        events = []
        return jsonify({'events': events})
    else:
        abort(404)




if __name__ == '__main__':

    print(host)
    app.run(debug=True, host=host, port=8080)
