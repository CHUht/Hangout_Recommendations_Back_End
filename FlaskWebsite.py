from flask import *
import random as rd
from HTMLGenerator import HTMLGenerator
import os
from UserDBManagement import UserDBManager
from EventDBManagement import EventsDBManager
from UserRatingDBManagement import UserRatingManager
from geopy.geocoders import Nominatim

class Server:

    """
    This Class function is handling the http requests
    It must also handle the data coming from the user in the forms
    The authentication based on this information is also a method of this class
    """

    # Testing user and password routine

    def __init__(self, host, port):
        app = Flask(__name__)
        app.secret_key = '"\n*\x96sc\x17I\xd2\xf2-\x01\xe8\xac5'

        """
            Declaration of the database managing classes
            One class manage user database
            One manages events
            The final manages the ratings from users and events
        """
        UserDB = UserDBManager()
        Events = EventsDBManager()
        Ratings = UserRatingManager()
        geolocator = Nominatim(user_agent="Hangout Recommendation")

        """
            We start by serving the homepage
        """
        @app.route('/', methods=['GET'])
        def index():
            return HTMLGenerator.generate_home_page(events=Events)

        """
            This is the log in page, it can either come with nothing
            Or come in POST method with a form
            If it comes with the form we retrieve the username and the password 
            Using this username and password we verify the authentication 
        """

        @app.route("/log_in", methods=['GET', 'POST'])
        def log_in_page():
            if request.method == 'GET':
                return render_template("log_in.html")
            elif request.method == 'POST':
                username = request.form.get("uname")
                password = request.form.get("psw")

                # Authentication part!!!!!
                if UserDB.user_authentication(username,password):
                    session['user_id'] = UserDB.return_user_id(username)
                    return redirect('/user_ratings_page')
                else:
                    return HTMLGenerator.generate_aut_fail_page()



        """
            This is the sign up method
            Here we must retrieve the original data from the user!
            We start by checking if the username is unique
            If it is we create a new sql table with the aquired data
        """
        @app.route("/sign_up" , methods=['GET', 'POST'])
        def return_sign_up_page():
            if request.method == 'GET':
                return HTMLGenerator.generate_sing_up_page(UserDB)
            elif request.method == 'POST':
                new_username = request.form.get("new_uname")
                new_password = request.form.get("new_psw")
                address = request.form.get("address")
                city = request.form.get("city")

                # We must check if the username is unique! If not return the same template
                # With a warning!
                if new_username in UserDB.return_usernames():
                    return HTMLGenerator.generate_sing_up_page(UserDB, alert_username=1)


                #location = geolocator.geocode(address + "," + city)
                location = None
                if location is None:
                    latitude = "NULL"
                    longitude = "NULL"
                else:
                    latitude = location.latitude
                    longitude = location.longitude

                UserDB.create_new_user(new_username, new_password, address, city
                                       , latitude, longitude)
                session['user_id'] = UserDB.return_user_id(new_username)
                return redirect('/user_ratings_page')


        """
            This is what we show when a user clicked in an event in the home page!
            Every event will be stored with an id, the user sends the id in the http request
            We retrieve the id to show the information about the event!
        """
        @app.route("/events", methods=['GET'])
        def return_event_page():
            number = request.args.get("number")
            return HTMLGenerator.generate_event_page(events=Events,event_id=number)

        """
            This part generates the user page
            The user page consists of two parts
            A part to rate events based on how likely a user wishes to go on them
            And a part consisting on the recommended events for this user!
        """
        @app.route("/user_ratings_page", methods=['GET','POST'])
        def return_user_rating_page():
            if request.method == 'GET':
                return HTMLGenerator.generate_ratings_page(session['user_id'], UserDB, Events, Ratings)
            if request.method == 'POST':

                for review in request.form:
                    review = review.split()

                    if( len(review) == 2):
                        number_of_starts = review[0][-1]
                        event_id = review[1]
                        Ratings.add_rating(str(session['user_id']), str(event_id), str(number_of_starts))

            return HTMLGenerator.generate_ratings_page(session['user_id'], UserDB, Events, Ratings)

        @app.route("/user_page", methods=['GET'])
        def return_user_page():
            if request.method == 'GET':
                pass

        app.run(debug=True, port=port, host=host)


"""
@app.route('/action_page.php', methods = ["GET",'POST'])
def after_password():
    if request.method == 'POST':
        names = request.get_json()
    return render_template("begin.html")
"""

if __name__ == '__main__':

    Server('127.0.0.1', 8080)
