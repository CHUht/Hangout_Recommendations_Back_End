from flask import Flask, render_template, jsonify, abort
from flask import request
from flask_cors import CORS, cross_origin
from EventDBManagement import *
from UserDBManagement import *
from RecomendationDBManagement import *
from UserRatingDBManagement import *
from UserCatesDBManagement import *
from RecommendEvents import generate_user_recommendations
from BackendAPIStaticList import *
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import re
from validate_email import validate_email
import time
from threading import Thread, Lock
import requests


# Initialisation of Flask with CORS (Cross-Origin Resource Sharing)
# CORS allows to share the restrained resource of web pages to another domain
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources=url_rsc, support_credentials=True,
            methods=['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE'])

# Initialisation of database managers
user_manager = UserDBManager()
event_manager = EventsDBManager()
rcmd_manager = RecomendationDBManager()
user_cates_Manager = UserCatesManager()
rating_manager = UserRatingManager()

# Initialisation of AES encipher
aes_cipher = AesCrypto("WuHan,GoodLuck!!", "+wx:lzh295256908")


@app.errorhandler(IndexError)
def index_error_exception_handler(e):
    """
    Handle the index error when it occurs.
    For example, call list[3] when len(list) == 3.
    :param e: the error event
    :return: json containing error info
    """
    print('index error ')
    return jsonify({'message': "Index Error"})


@app.errorhandler(TypeError)
def type_error_exception_handler(e):
    """
    Handle the type error when it occurs.
    For example, mistake an integer for a string.
    :param e: the error event
    :return: json containing error info
    """
    print('type error: ', e)
    return jsonify({'message': "Type Error"})


@app.errorhandler(UnicodeDecodeError)
def unicode_decode_error_exception_handler(e):
    """
    Handle the utf-8 decode error when it occurs.
    For example, utf-8 codec can't decode invalid start byte.
    :param e: the error event
    :return: json containing error info
    """
    print('unicode decode error: ', e)
    return jsonify({'message': " Decode Error "})


@app.errorhandler(404)
def all_exception_handler(e):
    """
    Handle the 404 not found client error.
    404:
    The requested resource could not be found but may be available in the future.
    Subsequent requests by the client are permissible.
    :param e: the error event
    :return: json containing error info
    """
    print('404 not found: ', e.description)
    return jsonify({'message': e.description})


@app.errorhandler(403)
def all_exception_handler(e):
    """
    Handle the 403 forbidden client error.
    403:
    The request contained valid data and was understood by the server, but the server is refusing action.
    This may be due to the user not having the necessary permissions for a resource
    or needing an account of some sort, or attempting a prohibited action
    (e.g. creating a duplicate record where only one is allowed).
    This code is also typically used if the request provided authentication via the WWW-Authenticate header field,
    but the server did not accept that authentication. The request should not be repeated.
    :param e: the error event
    :return: json containing error info
    """
    print('403 forbidden: ', e.description)
    return jsonify({'message': e.description})


def verify_headers(head):
    """
    The 'Authorization' header is put into the requests here to avoid illegal access to backend URLs.
    Only the frontend knows the header content as a password.
    :param head: the request's header
    :return: Check if the password is correct, abort 403 forbidden if not.
    """
    if head['Authorization'] != 'Made-in-China#!@$%?':
        abort(403)


def read_user_header(head):
    """
    The 'User-Id' header contains the current online user's id, which is an integer
    -1 if no user online
    :param head: the request's header
    :return: online user's id, abort type error if the header is not an integer.
    """
    try:
        return int(head['User-Id'])
    except TypeError:
        print('user_id header of wrong variable type')


@app.route('/')
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def index():
    """
    root url for testing, no real use
    :return: a testing json
    """
    verify_headers(request.headers)
    return jsonify({'Welcome': 'Keep Calm & Visit Paris'})


@app.route(url_api + '/Events/<event_id>', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_event(event_id):
    """
    Frontend gets full detail information of an event by its id,
    containing the nearest occurrence date.
    Call 404 error if event not found.
    :param event_id: integer from 4 to 6 digits,
                     run EventDBManagement.retrieve_event_ids() to check all IDs
    :return: json of structure {'event': {'event_id': 1234, 'title': '...', ...}}
    """
    verify_headers(request.headers)
    single_event = [event_manager.get_event_with_nearest(int(event_id))]
    if len(single_event) == 0:
        abort(404)
    return jsonify({'event': single_event[0]})


@app.route(url_api + '/Events', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_random_event():
    """
    Frontend gets a list of events of brief information.
    Call 404 error if no event found.
    :return: json of brief events, which means only 'event_id', 'title', 'address_street', 'address_city',
            'cover_url','large_category','nearest' will be retrieved
            Structured as {'event': [{'event_id': 1234, 'title': '...', ...},{'event_id': 2345, ...}, ...]}
    """
    verify_headers(request.headers)
    num_e = 80
    # If no user online, random events will be returned,
    if read_user_header(request.headers) == -1:
        rdm_event = event_manager.return_several_diff_events(number_of_events=num_e)
        print("no user login: random events")
        if not rdm_event:
            abort(404)
    # else, recommendations will be made for the online user.
    else:
        rcmd_event_id = rcmd_manager.get_recommendations_for_user(read_user_header(request.headers))
        rdm_event = []
        for event in rcmd_event_id:
            if event[0] in event_manager.retrieve_event_ids():
                rdm_event.append(event_manager.get_event_with_nearest(event[0]))
        # The number of events will be adjusted to num_e = 80 with random events.
        if len(rdm_event) >= num_e:
            rdm_event = rdm_event[:num_e]
        elif len(rdm_event) == 0:
            rdm_event = event_manager.return_several_diff_events(number_of_events=num_e)
            print("no recommended event found")
            if not rdm_event:
                abort(404)
        else:
            rdm_event = rdm_event + event_manager.return_several_diff_events(number_of_events=num_e - len(rdm_event))

    return jsonify({'event': rdm_event})


@app.route(url_api + '/Events/Categories/<int:category>', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_event_by_category(category):
    """
    Frontend gets a list of events by selected category.
    The number of events will be adjusted to num_e = 80.
    Call 404 error if no event found.
    :return: json of brief events, which means only 'event_id', 'title', 'address_street', 'address_city',
             'cover_url','large_category','nearest' will be retrieved
             Structured as {'event': [{'event_id': 1234, 'title': '...', ...},{'event_id': 2345, ...}, ...]}
    """
    verify_headers(request.headers)
    num_e = 80
    # Each category is represented by an integer, see BackendStaticList.cate_map for detail.
    if not isinstance(category, int):
        raise TypeError('query should be integer category index')
    # if category <= 5, it is a large category.
    if category <= 5:
        cate_event = event_manager.return_several_events_of_a_cate(category, number_of_events=num_e)
    else:
        cate_event = event_manager.all_events_of_cates(category)
        # The number of events will be adjusted to num_e = 80.
        if len(cate_event) > num_e:
            cate_event = cate_event[:num_e]
    if len(cate_event) == 0 or not category:
        abort(404)
    return jsonify({'event': cate_event})


@app.route(url_api + '/Users/login', methods=['GET', 'POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_login():
    """
    Frontend posts user's unique key (name / email) and password,
    and gets the user login state and login description (reason for login failure if not succeeded).
    All user's info enciphered by AES.
    Unique key should be a registered one.
    Once login succeeds, the recommendations for the user will be updated.
    :return: json of login state.
             structured as {'user_online': 'null'/online_id, 'uname': 'null', 'login_state': False/True,
                            'description': 'reason for failure/success here'}
    """
    verify_headers(request.headers)
    if request.method == 'GET':
        return render_template('log_in.html')
    elif request.method == 'POST':
        if not request.json or 'unique_key' not in request.json:
            abort(400)
        user_info = {}
        # All user's info enciphered by AES.
        try:
            user_info = {
                    'unique_key': aes_cipher.decrypt(request.json['unique_key']),
                    'pword': aes_cipher.decrypt(request.json['pword'])}
        except UnicodeDecodeError:
            print("utf-8 codec can't decode byte 0xfa in position 0: invalid start byte")
        # code for debugging #
        # user_info = {
        #     'unique_key': request.form.get('unique_key'),
        #     'pword': request.form.get('pword')
        # }
        # print(request.json['unique_key'].type())

        # Unique key and password should not be empty.
        if not user_info['unique_key']:
            return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                            'description': 'user name or email should not be empty'}), 201
        if not user_info['pword']:
            return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                            'description': 'password should not be empty'}), 201
        # If login by email
        if validate_email(user_info['unique_key']):
            print(user_info)

            # Email should be a registered one.
            if not user_manager.return_user_data_by_email(user_info['unique_key']):
                return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                                'description': 'email not found'}), 201
            # Password should be correct
            if user_manager.email_authentication(user_info['unique_key'], user_info['pword']):
                online_id = user_manager.return_user_data_by_email(user_info['unique_key'])[0][0]
                online_user = user_manager.return_user_data_by_email(user_info['unique_key'])[0][1]

                # Compute recommendations when user log in
                requests.get(url_root + url_api + '/ComputeRecommendations?passkey=fafa&user_id=' + str(online_id))

                return jsonify({'user_online': online_id, 'uname': online_user, 'login_state': True,
                                'description': 'successfully log in'}), 201
            else:
                return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                                'description': 'wrong password, try again'}), 201
        # If login by user name
        else:
            # User name should be a registered one
            if not user_manager.return_user_data(user_info['unique_key']):
                print(user_info,'sss')
                return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                                'description': 'user not found'}), 201
            # Password should be valid
            if user_manager.user_authentication(user_info['unique_key'], user_info['pword']):
                online_id = user_manager.return_user_id(user_info['unique_key'])

                # Compute recommendations when user log in
                requests.get(url_root + url_api + '/ComputeRecommendations?passkey=fafa&user_id=' + str(online_id))

                return jsonify(
                    {'user_online': online_id,
                     'uname': user_info['unique_key'], 'login_state': True,
                     'description': 'successfully log in'}), 201
            else:
                return jsonify({'user_online': 'null', 'uname': 'null', 'login_state': False,
                                'description': 'wrong password, try again'}), 201


@app.route(url_api + '/Users/<uname>', methods=['GET', 'POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_profile(uname=None):
    """
    Frontend gets user's profile by user name or modify user profile (to do).
    Return user's complete profile and the recommendations for him (brief events).
    :param uname: user's name, a string
    :return: a json structured as {'user': [(0, 'who', 'password', 'email@student.ecp.fr', 'address', 'Limoges')],
                                    'event': [{'event_id': 1234, 'title': '...', ...},{'event_id': 2345, ...}, ...]}
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
        # to do for user profile modification


@app.route(url_api + '/Users/signup', methods=['GET', 'POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_signup():
    """
    Create account for user while check if all info are legal.
    All user's input are enciphered.
    Compulsory fields: uname, pword, email.
    Email should be a valid one.
    Email and uname cannot be the one already used by other users.
    Once account created, an email will be sent to user, indicating the success of sign up.
    :return: a json implying the sign-up state.
             structured as {'user_info': {} / {'uname': 'who'}, 'signup_state': False / True,
                                'description': 'reason for failure/ success'}
    """
    verify_headers(request.headers)
    if request.method == 'GET':
        return render_template('sign_up_page.html')
    elif request.method == 'POST':
        # Check no user already login
        if read_user_header(request.headers) != -1:
            abort(403)

        rj = {}
        try:
            rj = {
                'uname': aes_cipher.decrypt(request.json['uname']),
                'pword': aes_cipher.decrypt(request.json['pword']),
                'email': aes_cipher.decrypt(request.json['email']),
                'address': aes_cipher.decrypt(request.json['address']),
                'city': aes_cipher.decrypt(request.json['city'])
            }
        except UnicodeDecodeError:
            print("utf-8 codec can't decode byte 0xfa in position 0: invalid start byte")
        print(rj)
        if not rj or 'uname' not in rj:
            print('empty file')
            abort(400)
        # Obligatory fields must not be empty
        if not rj['uname'] or not rj['pword'] or not rj['email']:
            return jsonify({'user_info': {}, 'signup_state': False,
                            'description': 'obligatory field(s) missed'}), 201

        # Email should be valid
        if not validate_email(str(rj['email']), verify=False):
            return jsonify({'user_info': {}, 'signup_state': False,
                            'description': 'email not validated'}), 201

        # Email and uname cannot be the one already used by other users.
        if rj['uname'] in user_manager.return_usernames():
            return jsonify({'user_info': {}, 'signup_state': False,
                            'description': 'user name already existed'}), 201
        if rj['email'] in user_manager.return_emails():
            return jsonify({'user_info': {}, 'signup_state': False,
                            'description': 'email already occupied by another account'}), 201

        # Sign up with Obligatory fields and optional fields
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
        send_email(rj['email'], 'Thank you for your subscription')
        user = {
            'uname': rj['uname']
        }
        return jsonify({'user_info': user, 'signup_state': True,
                        'description': 'successfully signed up. Start Visit Paris now!'}), 201


@app.route(url_api + '/Users/choose_tags', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_choose_tags():
    """
    Frontend posts the request containing preferred categories of the user.
    Categories are represented by integer indexes, see BackendAPIStaticList.cate_map.
    Non-existing category labels will be removed.
    These preferred categories will be stored into user-category database.
    :return: a json implying the registering state.
             structured as {'user_info': {'user_id': 0}, 'tags': [] / [1, 3, 5, ...], 'state': False / True}
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
        if not tags_chosen:
            return jsonify({'user_info': user_id, 'tages': [], 'state': False}), 201
        user_cates_Manager.insert_user_cates(user_id, tags_chosen)
        return jsonify({'user_info': user_id, 'tags': list(tags_chosen), 'state': True}), 201
    # to do


@app.route(url_api + '/Users/send_link_by_email', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_post_email():
    """
    This URL is used for sending a password-reset email.
    All info are enciphered during the communication.
    Frontend posts the email typed in by user and the captcha generated randomly.
    Email address should be valid and at least one user in database uses this email.
    The captcha will be sent to user's email, and then user can type it into verification web page.
    :return: a json implying the sending state
             structured as {'sending_state': False/True, 'description': 'reason for failure / success'}
    """
    verify_headers(request.headers)
    if not request.json or 'email' not in request.json:
        abort(400)
    email = aes_cipher.decrypt(request.json['email'])
    if not email or not validate_email(email, verify=False):
        print("error: email not valid")
        return jsonify({'sending_state': False, 'description': 'email not valid'}), 201
    if not user_manager.return_user_data_by_email(email):
        print('error: email not existing in db')
        return jsonify({'sending_state': False,
                        'description': 'no current user uses this email'}), 201
    captcha = aes_cipher.decrypt(request.json['captcha'])
    send_email(email, captcha)
    return jsonify({'sending_state': True, 'description': 'email sent'}), 201


def send_email(email, mail_content):
    """
    Send the corresponding content to the assigned email.
    :param email: user's email
    :param mail_content: email content
    :return: void
    """
    sender = 'parishangout@gmail.com'
    receivers = [email]

    # Set the sender, receiver, text, title of the mail
    message = MIMEText('EMAIL SENDING TEST: ' + mail_content, 'plain', 'utf-8')
    message['From'] = Header("ParisHangOut", 'utf-8')
    message['To'] = Header(email, 'utf-8')
    message['Subject'] = Header('Email from Paris Hang Out Website', 'utf-8')

    # Send the mail
    try:
        smtp_obj = smtplib.SMTP_SSL('smtp.gmail.com')
        smtp_obj.connect('smtp.gmail.com', 465)
        smtp_obj.login('lujiahao8146@gmail.com', 'GOOGLE274@')
        smtp_obj.sendmail(sender, receivers, message.as_string())
        print("successfully sent the email")
    except smtplib.SMTPException:
        print("Error: email not sent")
        abort(404)


@app.route(url_api + '/Users/reset_password', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_reset_password():
    """
    Frontend posts the new password of one user.
    Change the password registered in the user database.
    All info are enciphered.
    :return: a json implying reset state
             structured as {'reset_state': True / False, 'description': 'password updated'/'reason for failure'}
    """
    verify_headers(request.headers)
    if request.method == 'POST':
        if not request.json or 'pword' not in request.json:
            abort(400)
        email = aes_cipher.decrypt(request.json['email'])
        pword = aes_cipher.decrypt(request.json['pword'])

        # User's email should be valid
        if not user_manager.return_user_data_by_email(email):
            return jsonify({'reset_state': False, 'description': 'user not found'}), 201

        # User cannot replace the old password by the same one.
        if pword == user_manager.return_user_data_by_email(email)[0][2]:
            return jsonify({'reset_state': False, 'description': 'should not repeat the old password'}), 201

        # Update password
        user_manager.modify_password(user_manager.return_user_data_by_email(email)[0][3], pword)
        return jsonify({'reset_state': True, 'description': 'password updated'}), 201


@app.route(url_api + '/Events/search', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def event_search():
    """
    Frontend posts the keywords, with which events are searched and returned to user.
    Keywords can be split by ',' or ';' or space and is a string
    :return: Events found, {'event': [result1, result2, ...]}
    """
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
        return jsonify({'event': search_result})
    else:
        abort(404)


@app.route(url_api + '/Rating', methods=['POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_rating():
    """
    Frontend posts an user and his/her rating to an event.
    Rate is an integer from 1 to 5.
    :return: {'rating state': True / False, 'description': 'rate success'/ 'failure reason'}
    """
    verify_headers(request.headers)
    if request.method == 'POST':
        if not request.json:
            abort(400)
        user_header = read_user_header(request.headers)
        # Check online user's id
        if user_header == -1:
            return jsonify({'rating state': False, 'description': 'no user online'})
        print(request.json)
        rate_info = {
            'event_id': int(request.json['event_id']),
            'rate': int(request.json['rate']),
            'timestamp': int(time.time())
        }

        print(rate_info)

        rating_manager.add_rating(user_header, rate_info['event_id'], rate_info['rate'], rate_info['timestamp'])
        return jsonify({'rating state': True, 'description': 'rate success'})
        # to do


@app.route(url_api + '/ComputeRecommendations', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def compute_recommendations():
    """
    URL for generate recommendations for user.
    Normally not called directly by frontend, but by other API URLs.
    :return: {"OK" / 'Fail': "Computations recommended" / 'Failure reason'}
    """
    passkey = request.args.get('passkey')
    user_id = int(request.args.get('user_id'))

    if not(passkey and user_id is not None):
        return jsonify({"Fail": "Arguments Missing"})
    # Check authorization key
    if passkey == "fafa":
        ratings = rating_manager.get_ratings_from_user(user_id)

        if not ratings:
            return jsonify({"Fail": "Cannot compute recommendations with no ratings"})

        # Start recommendation generating thread
        recommend_thread = Thread(target=generate_user_recommendations,
                                  args=(event_manager, ratings, user_id, rcmd_manager))
        recommend_thread.start()
    else:
        return jsonify({"Fail": "Wrong passkey"})

    return jsonify({"OK": "Computations recommended"})


if __name__ == '__main__':

    # print(host)
    app.run(debug=True, host=host, port=8080)
    # send_email('jiahao.lu@student-cs.fr', 'www.testlink.com')
    # print(isinstance(validate_email('zhuofanyu666@gmail.com'),bool))
