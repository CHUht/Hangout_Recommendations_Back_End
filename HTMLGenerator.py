from flask import *
import random as rd


class HTMLGenerator:
    """
        This class is responsible for generating the html documents that will be sent through flask
        It handles all the render templates methods
    """

    @classmethod
    def generate_home_page(cls, events):

        event_ids = events.retrieve_event_ids()
        data = []
        for i in range(10):
            event_id = rd.choice(event_ids)
            data.append(events.return_event_no_nearest(event_id))

        return render_template("home_page.html", data=data)

    @classmethod
    def generate_event_page(cls, events, event_id):
        event_data = events.return_event_no_nearest(event_id)
        return render_template("event_page.html", data=event_data)

    @classmethod
    def generate_log_in_page(cls):
        return render_template("log_in.html")

    @classmethod
    def generate_aut_fail_page(cls):
        return render_template("aut_fail.html")

    @classmethod
    def generate_sing_up_page(cls, UserDB, alert_address=0, alert_username=0):
        return render_template("sing_up_page.html", data=UserDB.return_usernames(), alert_address=alert_address
                               , alert_username=alert_username)

    @classmethod
    def generate_user_page(cls, user_name):
        return render_template("user_page.html", username=user_name)

    @classmethod
    def generate_ratings_page(cls, user_id, UserDB, Events, Ratings):

        event_ids = Ratings.get_unrated_events(user_id)

        # Here we select 10 distinct events from the list of possible events
        # We start by selecting their index at random
        # Them popping that random element from the selection list
        # If the list of possible events becomes empty we just stop selecting
        data = []
        for i in range(3):
            list_event_id = rd.randint(0,len(event_ids) - 1)
            event_id = event_ids.pop(list_event_id)
            data.append(Events.return_event_no_nearest(event_id))

            if len(event_ids) == 0:
                break

        return render_template("rating_events_page.html", data=data)









if __name__ == "__main__":

    pass




