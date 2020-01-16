from flask import Flask, render_template, jsonify, abort, redirect
from flask import request, url_for
from flask_cors import CORS, cross_origin
from EventDBManagement import *
from UserDBManagement import *
from RecomendationDBManagement import *
from geopy.geocoders import Nominatim
from validate_email import validate_email
from BackendAPIStaticList import *
import smtplib
from email.mime.text import MIMEText
from email.header import Header

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources=url_rsc, support_credentials=True,
            methods=['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE'])

user_manager = UserDBManager()
event_manager = EventsDBManager()
rcmd_manager = RecomendationDBManager()
geolocator = Nominatim(user_agent="Hangout Recommendation")


# @app.errorhandler(IndexError)
# @app.errorhandler(TypeError)
# def all_exception_handler(e):
#     return jsonify({'message': 'Back end Error raised'})


@app.errorhandler(404)
def all_exception_handler(e):
    return jsonify({'message': '404 not found'})


@app.route('/')
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def index():
    """
    root url, no use
    :return:
    """
    return jsonify({'Welcome': 'Keep Calm & Visit Paris'})


@app.route('/api/v1.0/Events/<int:event_id>', methods=['GET'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def get_event(event_id=0):
    """
    Frontend gets event by its id, call 404 error if not found
    :param event_id:
    :return:
    """
    # event = list(filter(lambda t: t['event_id'] == event_id, event_manager.check_database()))
    single_event = [event_manager.get_event_with_nearest(event_id)]
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
    rdm_event = event_manager.return_several_diff_events(number_of_events=20)
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
    cate_type = cate_re_map[category]
    cate_event = event_manager.return_several_events_of_a_cate(cate_type, number_of_events=20)
    if len(cate_event) == 0 or category == '':
        abort(404)
    return jsonify({'event': cate_event})


@app.route('/api/v1.0/Users/login', methods=['GET', 'POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_login():
    if request.method == 'GET':
        return render_template('log_in.html')
    elif request.method == 'POST':
        if not request.json or 'uname' not in request.json:
            abort(400)
        user_info = {
                'uname': request.json['uname'],
                'pword': request.json['pword']
        }
        # code for debugging #
        # user_info = {
        #     'uname': request.form.get('uname'),
        #     'pword': request.form.get('pword')
        # }
        print(user_info)
        if user_info['uname'] == '':
            return jsonify({'user_online': user_info, 'login state': False,
                            'description': 'user name should not be vacant'}), 201
        if not user_manager.return_user_data(user_info['uname']):
            return jsonify({'user_online': user_info, 'login state': False,
                            'description': 'user not found'}), 201
        if user_manager.user_authentication(user_info['uname'], user_info['pword']):
            return jsonify({'user_online': user_info, 'login state': True,
                            'description': 'successfully log in'}), 201
        else:
            return jsonify({'user_online': user_info, 'state': False,
                            'description': 'wrong password, try again'}), 201


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
            preferred_events.append({'activity': event_manager.get_event_with_nearest(pair[0]),
                                    'score': pair[1]})
        return jsonify({'user': user, 'event': preferred_events})
    elif request.method == 'PUT':
        if not request.json:
            abort(400)
        # to do


@app.route('/api/v1.0/Users/signup', methods=['GET', 'POST'])
@cross_origin(origin=host, headers=['Content-Type', 'Authorization'])
def user_signup():
    if request.method == 'GET':
        return render_template('sign_up_page.html')
    elif request.method == 'POST':
        rj = {
            'uname': request.form.get('new_uname'),
            'pword': request.form.get('new_psw'),
            'pword_r': request.form.get('rep_psw'),
            'email': request.form.get('email'),
            'address': request.form.get('adrs'),
            'city': request.form.get('city')
        }
        # rj = request.form.get
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
            if request.json['email'] == u[5]:
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
    sender = 'keepcalmvisitparis@gmail.com'
    receivers = [email]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText('EMAIL SENDING TEST: ' + link, 'plain', 'utf-8')
    message['From'] = Header("KeepCalm&VisitParis", 'utf-8')  # 发送者
    message['To'] = Header(email, 'utf-8')  # 接收者
    message['Subject'] = Header('API email', 'utf-8')

    try:
        smtpObj = smtplib.SMTP_SSL()
        smtpObj.connect('smtp.gmail.com', 465)
        smtpObj.login('lujiahao8146@gmail.com', 'GOOGLE274@')
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("successfully sent the email")
    except smtplib.SMTPException:
        print("Error: email not sent")
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
    # send_email('jiahao.lu@student-cs.fr','www.testlink.com')
