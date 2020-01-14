import socket

Cate_map = {
        1: 'Expositions',
        2: 'Animations',
        3: 'Spectacles',
        4: 'Événements',
        5: 'Concerts'
    }

host = socket.gethostbyname(socket.gethostname())
url_root = r'http://' + host + ':8080'
url_api = r'/api/v1.0'
url_rsc = {r"/": {"origins": url_root},
           url_api + r'/Events/<int:event_id>': {"origins": url_root + url_api + '/Events/<int:event_id>'},
           url_api + r'/Events': {"origins": url_root + url_api + "/Events"},
           url_api + r'/Events/Categories/<int:cate_id>': {"origins": url_root + url_api + "/Events/Categories/<int:cate_id>"},
           url_api + r'/Users/login': {"origins": url_root + url_api + "/Users/login"},
           url_api + r'/Users/<int:user_id>': {"origins": url_root + url_api + "/Users/<int:user_id>"},
           url_api + r'/Users/signup': {'origins': url_root + url_api + '/Users/signup'},
           url_api + r'/Users/choose_tags': {'origins': url_root + url_api + '/Users/choose_tags'},
           url_api + r'/Users/send_link_by_email': {'origins': url_root + url_api + '/Users/send_link_by_email'},
           url_api + r'/Users/reset_password': {'origins': url_root + url_api + '/Users/reset_password'},
           url_api + r'/Events/search': {'origins': url_root + url_api + '//Events/search'}
           }
"""
r"/": useless 
r'/Events/<int:event_id>'[GET]: 根据event_id返回event，找不到则抛出404
r'/Events'[GET]: 随机返回10个不同events概览， 找不到则抛出404
r'/Events/Categories/<int:cate_id>'[GET]: 根据category返回events概览 ，  找不到则抛出404
r'/Users/login'[POST]: 收取{user_id, pword}, 返回 {'user_online': user_info, 'state': True/False,
                            'description': 'wrong password'/'successfully log in'}
r'/Users/<int:user_id>'[GET,PUT]: GET根据user_id返回user及recommendation for user，找不到则抛出404
                                PUT修改user信息  # to do
r'/Users/signup'[POST]: 收取{uname, pword, pword_r, email, ...}, 根据request返回{user_info, signup state: T/F, description} 
r'/Users/choose_tags'[PUT]: 根据user_id，修改其preferred tags，返回{'user_info': user, 'tags': tags_chosen, 'description':''}  # to do
r'/Users/send_link_by_email'[POST]: user重置密码时使用， （待议）
r'/Users/reset_password'[PUT]: 重置user密码，（待议） 
r'/Events/search'[POST]: 收取搜索词key-value pairs { 'title': '...', 'address_city': '...', ...}, 返回找到的events概览，找不到则抛出404
"""