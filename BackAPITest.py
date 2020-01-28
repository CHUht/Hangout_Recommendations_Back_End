from flask import Flask, render_template, jsonify, abort, redirect
from flask import request, url_for
from flask_cors import CORS, cross_origin
from EventDBManagement import *
from UserDBManagement import *
from RecomendationDBManagement import *
from UserCatesDBManagement import *
from geopy.geocoders import Nominatim
# from vali_mail import validate_email
from BackendAPIStaticList import *
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import re
from validate_email import validate_email

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources=url_rsc, support_credentials=True,
            methods=['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE'])

user_manager = UserDBManager()
event_manager = EventsDBManager()
rcmd_manager = RecomendationDBManager()
user_cates_Manager = UserCatesManager()
geolocator = Nominatim(user_agent="Hangout Recommendation")


@app.errorhandler(IndexError)
def index_error_exception_handler(e):
    print('index error')
    return jsonify({'message': 'Back end Error raised'})


@app.errorhandler(TypeError)
def type_error_exception_handler(e):
    print('type error')
    return jsonify({'message': 'Back end Error raised'})


@app.errorhandler(404)
def all_exception_handler(e):
    return jsonify({'message': '404 not found'})

@app.errorhandler(204)
def all_exception_handler(e):
    return jsonify({'message': 'request recieved, but nothing to reply'})

@app.errorhandler(403)
def all_exception_handler(e):
    return jsonify({'message': '403 access refused'})


def verify_headers(head):
    if head['Authorization'] != 'Made-in-China#!@$%?':
        abort(403)


def read_user_header(head):
    try:
        return int(head['User-Id'])
    except TypeError:
        print('user_id header of wrong variable type')


@app.route('/')
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def index():
    """
    root url, no use
    :return:
    """
    verify_headers(request.headers)
    return jsonify({'Welcome': 'Keep Calm & Visit Paris'})


@app.route('/api/v1.0/Events/<event_id>', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_event(event_id):
    """
    Frontend gets event by its id, call 404 error if not found
    :param event_id:
    :return:
    """
    # event = list(filter(lambda t: t['event_id'] == event_id, event_manager.check_database()))
    verify_headers(request.headers)
    single_event = [event_manager.get_event_with_nearest(int(event_id))]
    if len(single_event) == 0:
        abort(204)
    return jsonify({'event': single_event[0]})


@app.route('/api/v1.0/Events', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_random_event():
    """
    Frontend gets a list of events for homepage, call 404 error if not found
    :return:
    """
    verify_headers(request.headers)
    if read_user_header(request.headers) == -1:
        rdm_event = event_manager.return_several_diff_events(number_of_events=20)
        print("warning: random events")
        if not rdm_event:
            abort(404)
    else:
        rcmd_event_id = rcmd_manager.get_recommendations_for_user(read_user_header(request.headers))
        rdm_event = []
        for event in rcmd_event_id:
            if event[0] in event_manager.retrieve_event_ids():
                rdm_event.append(event_manager.get_event_with_nearest(event[0]))
        if len(rdm_event) > 20:
            rdm_event = rdm_event[:20]
        elif len(rdm_event) == 0:
            print("no recommended event found")
            abort(204)
    return jsonify({'event': rdm_event})


@app.route('/api/v1.0/Events/Categories/<int:category>', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_event_by_category(category):
    """
    Frontend gets a list of events by selected category
    :return:
    """
    verify_headers(request.headers)
    if not isinstance(category, int):
        raise TypeError('query should be integer category index')
    if category <= 5:
        cate_event = event_manager.return_several_events_of_a_cate(category, number_of_events=20)
    else:
        cate_event = event_manager.all_events_of_cates(category)
    if len(cate_event) == 0 or not category:
        abort(204)
    return jsonify({'event': cate_event})


@app.route('/api/v1.0/Users/login', methods=['GET', 'POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_login():
    """
    get the user login form and check login authentication
    :return:
    """
    verify_headers(request.headers)
    if request.method == 'GET':
        return render_template('log_in.html')
    elif request.method == 'POST':
        # print(verify_headers(request.headers))
        # print(check_user_header(request.headers))
        if not request.json or 'unique_key' not in request.json:
            abort(400)
        user_info = {
                'unique_key': request.json['unique_key'],
                'pword': request.json['pword']}
        # code for debugging #
        # user_info = {
        #     'unique_key': request.form.get('unique_key'),
        #     'pword': request.form.get('pword')
        # }
        # print(request.json['unique_key'].type())

        if not user_info['unique_key']:
            return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                            'description': 'user name or email should not be empty'}), 201
        if not user_info['pword']:
            return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                            'description': 'password should not be empty'}), 201

        if re.match(r'.*@\w*\..*', user_info['unique_key']) != None:
            if not user_manager.return_user_data_by_email(user_info['unique_key']):
                return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                                'description': 'email not found'}), 201
            if user_manager.email_authentication(user_info['unique_key'], user_info['pword']):
                online_id = user_manager.return_user_data_by_email(user_info['unique_key'])[0][0]
                online_user = user_manager.return_user_data_by_email(user_info['unique_key'])[0][1]
                return jsonify({'user_online': online_id, 'uname': online_user, 'login_state': True,
                                'description': 'successfully log in'}), 201
            else:
                return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                                'description': 'wrong password, try again'}), 201
        else:
            if not user_manager.return_user_data(user_info['unique_key']):
                return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                                'description': 'user not found'}), 201
            if user_manager.user_authentication(user_info['unique_key'], user_info['pword']):
                return jsonify(
                    {'user_online': user_manager.return_user_id(user_info['unique_key']),
                     'uname': user_info['unique_key'], 'login_state': True,
                     'description': 'successfully log in'}), 201
            else:
                return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                                'description': 'wrong password, try again'}), 201


@app.route('/api/v1.0/Users/<uname>', methods=['GET', 'POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_profile(uname=None):
    """
    get user's profile or modify user profile
    :param uname:
    :return:
    """
    verify_headers(request.headers)
    if request.method == 'GET':
        user = user_manager.return_user_data(uname)
        if len(user) == 0:
            abort(404)
        preferred_events_id = rcmd_manager.get_recommendations_for_user(user_manager.return_user_id(uname))
        preferred_events = []
        for pair in preferred_events_id:
            preferred_events.append({'activity': event_manager.get_event_with_nearest(pair[0]),
                                    'score': pair[1]})
        return jsonify({'user': user, 'event': preferred_events})
    elif request.method == 'POST':
        if not request.json:
            abort(400)
        # to do


@app.route('/api/v1.0/Users/signup', methods=['GET', 'POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_signup():
    """
    create account for user while check if all info are legal
    :return:
    """
    verify_headers(request.headers)
    if request.method == 'GET':
        return render_template('sign_up_page.html')
    elif request.method == 'POST':
        if read_user_header(request.headers) != -1:
            abort(403)
        # code for debugging #
        # rj = {
        #     'uname': request.form.get('new_uname'),
        #     'pword': request.form.get('new_psw'),
        #     'email': request.form.get('email'),
        #     'address': request.form.get('adrs'),
        #     'city': request.form.get('city')
        # }
        # print(rj)
        rj = request.json
        print(rj)
        if not rj or 'uname' not in rj:
            print('empty file')
            abort(400)
        if not rj['uname'] or not rj['pword'] or not rj['email']:
            return jsonify({'user_info': {}, 'signup_state': False,
                            'description': 'obligatory field(s) missed'}), 201
        if not validate_email(str(rj['email']), verify=False):
            return jsonify({'user_info': {}, 'signup_state': False,
                            'description': 'email not validated'}), 201
        if rj['uname'] in user_manager.return_usernames():
            return jsonify({'user_info': {}, 'signup_state': False,
                            'description': 'user name already existed'}), 201
        for u in user_manager.check_database():
            if rj['email'] == u[5]:
                return jsonify({'user_info': {}, 'signup_state': False,
                                'description': 'email already occupied by another account'}), 201

        if rj['address'] != 'null' and rj['city'] != 'null':
            user_manager.create_new_user(
                rj['uname'], rj['pword'], rj['email'], rj['address'], rj['city']
            )
        elif rj['address'] != 'null' and rj['city'] == 'null':
            user_manager.create_new_user(
                rj['uname'], rj['pword'], rj['email'], address=rj['address'])
        elif rj['address'] == 'null' and rj['city'] != 'null':
            user_manager.create_new_user(
                rj['uname'], rj['pword'], rj['email'], city=rj['city'])
        else:
            user_manager.create_new_user(
                rj['uname'], rj['pword'], rj['email'])
        send_email(rj['email'],'Thank you for your subscription')
        user = {
            'uname': rj['uname']
        }
        return jsonify({'user_info': user, 'signup_state': True,
                        'description': 'successfully signed up. Start Visit Paris now!'}), 201


@app.route('/api/v1.0/Users/choose_tags', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_choose_tags():
    """
    user chooses the tags he prefers
    :return:
    """
    verify_headers(request.headers)
    if request.method == 'POST':
        if not request.json or 'user_id' not in request.json:
            abort(400)
        user_id = request.json['user_id']
        tags_chosen = set(request.json['tags'])

        for tag in tags_chosen:
            if tag not in cate_map.keys():
                tags_chosen.remove(tag)

        user_cates_Manager.insert_user_cates(user_id, tags_chosen)
        return jsonify({'user_info': user_id, 'tags': tags_chosen, 'state': True})
    # to do


@app.route('/api/v1.0/Users/send_link_by_email', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_post_email():
    verify_headers(request.headers)
    if read_user_header(request.headers) == -1:
        abort(403)
    if not request.json or 'email' not in request.json:
        abort(400)
    email = request.json['email']
    if not email or not validate_email(email, verify=True):
        return jsonify({'sending state': False, 'description': 'email not valid'})
    link = request.json['link']
    send_email(email, link)
    return jsonify({'sending state': True, 'description': 'email sent'})


def send_email(email, link):
    sender = 'parishangout@gmail.com'
    receivers = [email]

    message = MIMEText('EMAIL SENDING TEST: ' + link, 'plain', 'utf-8')
    message['From'] = Header("ParisHangOut", 'utf-8')
    message['To'] = Header(email, 'utf-8')
    message['Subject'] = Header('Email from Paris Hang Out Website', 'utf-8')

    try:
        smtpObj = smtplib.SMTP_SSL()
        smtpObj.connect('smtp.gmail.com', 465)
        smtpObj.login('lujiahao8146@gmail.com', 'GOOGLE274@')
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("successfully sent the email")
    except smtplib.SMTPException:
        print("Error: email not sent")
        abort(404)
    # to do


@app.route('/api/v1.0/Users/reset_password', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_reset_password():
    verify_headers(request.headers)
    if request.method == 'POST':
        if not request.json or 'uname' not in request.json:
            abort(400)
        if request.json['uname'] in user_manager.return_usernames():
            return jsonify({'reset state': False, 'description': 'user not found'})
        if request.json['new_pword'] != request.json['rep_pword']:
            return jsonify({'reset state': False, 'description': 'These two passwords entered do not match'})
        user_manager.modify_password(request.json['uname'], request.json['new_pword'])
        return jsonify({'reset state': False})
    # to do


@app.route('/api/v1.0/Events/search', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def event_search():
    verify_headers(request.headers)
    if request.method == 'POST':
        if not request.json:
            abort(400)
        search = request.json['keywords']
        if isinstance(search, tuple) or isinstance(search, list) or isinstance(search, dict):
            abort(404)
        search_result = event_manager.search_key_words(search)
        if not search_result:
            abort(404)
        return jsonify({'events': search_result})
    else:
        abort(404)


@app.route('/api/v1.0/Rating', methods=['GET', 'POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_rating():
    """
    get user's rating and put it into DB
    :param event_id:
    :return:
    """
    print(request.headers)
    verify_headers(request.headers)
    if request.method == 'GET':
        return '111'
    elif request.method == 'POST':
        if not request.json:
            abort(400)
        user_header = read_user_header(request.headers)
        if user_header == -1:
            abort(404)
        print(request.json)
        rate_info = {
            'event_id': request.json['event_id'],
            'rate': request.json['rate']
        }
        if not isinstance(rate_info['event_id'], int) or not isinstance(rate_info['rate'], int):
            raise TypeError
        rcmd_manager.add_recommendation(user_header, rate_info['event_id'], rate_info['rate'])
        return jsonify({'rating state': True})
        # to do


if __name__ == '__main__':

    print(host)
    app.run(debug=True, host=host, port=8080)
    # send_email('jiahao.lu@student-cs.fr','www.testlink.com')
    # print(isinstance(validate_email('zhuofanyu666@gmail.com'),bool))
