import socket
from Crypto.Cipher import AES
import base64

# this document contains statistic useful common tools imported by other documents.
# Mapping of category index to category name
cate_map = {
    1: 'Animations',
    2: 'Concerts',
    3: 'Événements',
    4: 'Expositions',
    5: 'Spectacles',
    6: 'Atelier/Cours',
    7: 'Autre animation',
    8: 'Balade',
    9: 'Conférence / Débat',
    10: 'Lecture / Rencontre',
    11: 'Loisirs / Jeux',
    12: 'Stage',
    13: 'Visite guidée',
    14: 'Autre concert',
    15: 'Chanson française',
    16: "Classique",
    17:  "Folk",
    18: "Hip-Hop",
    19: "Jazz",
    20: "Musiques du Monde",
    21: "Pop / Variété",
    22: "Reggae",
    23: "Rock",
    24: "Soul/Funk",
    25: "Électronique",
    26: "Autre événement",
    27: "Brocante / Marché",
    28: "Festival / Cycle",
    29: "Fête / Parade",
    30: "Salon",
    31: "Soirée / Bal",
    32: "Événement sportif",
    33: "Art Contemporain",
    34: "Autre expo",
    35: "Beaux-Arts",
    36: "Design / Mode",
    37: "Histoire / Civilisations",
    38: "Illustration / BD",
    39: "Photographie",
    40: "Sciences / Techniques",
    41: "Street-art",
    42: "Autre spectacle",
    43: "Cirque / Art de la Rue",
    44: "Danse",
    45: "Humour",
    46: "Jeune public",
    47: "Opéra / Musical",
    48: "Projection",
    49: "Théâtre",
}

# Backend server IP address and URLs
host = socket.gethostbyname(socket.gethostname())
url_root = r'http://' + host + ':8080'
url_api = r'/api/v1.0'
url_rsc = {r"/": {"origins": url_root},
           url_api + r'/Events/<int:event_id>': {"origins": url_root + url_api + '/Events/<int:event_id>'},
           url_api + r'/Events': {"origins": url_root + url_api + "/Events"},
           url_api + r'/Events/Categories/<int:cate_id>':
               {"origins": url_root + url_api + "/Events/Categories/<int:cate_id>"},
           url_api + r'/Users/login': {"origins": url_root + url_api + "/Users/login"},
           url_api + r'/Users/<int:user_id>': {"origins": url_root + url_api + "/Users/<int:user_id>"},
           url_api + r'/Users/signup': {'origins': url_root + url_api + '/Users/signup'},
           url_api + r'/Users/choose_tags': {'origins': url_root + url_api + '/Users/choose_tags'},
           url_api + r'/Users/send_link_by_email': {'origins': url_root + url_api + '/Users/send_link_by_email'},
           url_api + r'/Users/reset_password': {'origins': url_root + url_api + '/Users/reset_password'},
           url_api + r'/Events/search': {'origins': url_root + url_api + '/Events/search'},
           url_api + r'/Rating': {'origins': url_root + url_api + '/Rating'},
           url_api + r'/ComputeRecommendations': {'origins': url_root + url_api + '/ComputeRecommendations'}
           }
"""
r"/": root url for testing, no real use

r'/Events/<int:event_id>'[GET]: Frontend gets full detail information of an event by its id,
                                containing the nearest occurrence date.
                                Call 404 error if event not found.
                                
r'/Events'[GET]: Frontend gets a list of events of brief information.
                 Call 404 error if no event found.
                 If no user online, random events will be returned,
                 else, recommendations will be made for the online user.
                 
r'/Events/Categories/<category>'[GET]: Frontend gets a list of events by selected category.
                                       The number of events will be adjusted to num_e = 80.
                                       Call 404 error if no event found.
                                       
r'/Users/login'[POST]: Frontend posts user's unique key (name / email) and password,
                       and gets the user login state and login description (reason for login failure if not succeeded).
                       post{user_id, pword}, return {'user_online': user_info, 'state': True/False,
                            'description': 'wrong password'/'successfully log in'}
                            
r'/Users/<uname>'[GET,POST]: Frontend gets user's profile by user name or modify user profile (to do).
                            Return user's complete profile and the recommendations for him (brief events).

r'/Users/signup'[POST]: Create account for user while check if all info are legal.
                        post{uname, pword, pword_r, email, ...},return{user_info, signup state: T/F, description} 

r'/Users/choose_tags'[POST]:  Frontend posts the request containing preferred categories of the user.
                             post user_id，update preferred tags，return {'user_info': user, 'tags': tags_chosen, 'description':''}

r'/Users/send_link_by_email'[POST]: This URL is used for sending a password-reset email.
                                    return {'sending_state': False/True, 'description': 'reason for failure / success'}

r'/Users/reset_password'[POST]: Frontend posts the new password of one user.
                               Change the password registered in the user database. 

r'/Events/search'[POST]: Frontend posts the keywords, with which events are searched and returned to user.
                         Keywords can be split by ',' or ';' or space and is a string

r'/Rating'[POST]: Frontend posts an user and his/her rating to an event.

r'/ComputeRecomendations'[GET] : Generate recommendations for user
"""

# Singleton instance mode
def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner


jour_semaine = {'0': 'dimanche',
                '1': 'lundi',
                '2': 'mardi',
                '3': 'mercredi',
                '4': 'jeudi',
                '5': 'vendredi',
                '6': 'samedi'}

# AES Cipher Class
class AesCrypto:
    def __init__(self, password,iv):
        self.key = password.encode()  # must be 16 bytes boundary
        self.iv = iv.encode()  # must be 16 bytes
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        bs = AES.block_size
        cipher = AES.new(self.key, self.mode, self.iv)
        pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs).encode("utf-8")
        data = pad(text.encode('utf-8'))
        encrypt_data = cipher.encrypt(data)
        return base64.b64encode(encrypt_data).decode()

    def decrypt(self, ciphertext):
            cipher = AES.new(self.key, self.mode, self.iv)
            encrypt_data = base64.b64decode(ciphertext)
            # print(encrypt_data)
            decrypt_data = cipher.decrypt(encrypt_data)
            upad = lambda s: s[0:-(s[-1])]
            decrypt_data = upad(decrypt_data)
            return decrypt_data.decode()


if __name__ == '__main__':
    myKey = "WuHan,GoodLuck!!"
    myIV = "+wx:lzh295256908"
    pc = AesCrypto(myKey, myIV)
    code = pc.encrypt('@@@')
    # code = 'U2FsdGVkX18wF8F8K85745zwEtxsulXaoVYlxOvQIZBJYayIQL5+vf69vQmG81mI'
    #code = 'RpS/sdWm1xFU8ZVfuBVrKg=='
    d = pc.decrypt(code)
    print(code)
    print(d)
    # print(Random.new().read(3))


