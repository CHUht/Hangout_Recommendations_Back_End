import pickle as pkl
import numpy as np
import datetime as dt
from UserRatingDBManagement import UserRatingManager
from EventDBManagement import EventsDBManager
from RecomendationDBManagement import RecomendationDBManager
import time
import math


def generate_user_recommendations(Events, user_ratings, user_id, Recommendations, time_decay = -8.23e-7):


    """
        :param events: description of all events in the database send in the same order as returned from the sql file
        :param user_ratings: user ratings of the events on the format (user_id, event_id, rating)
        :param user_id: the user identification number
        :param Recommendations: the recommendation database manager
        :return: nothing, sets the recommendations on the recommendation database
    """


    """
        Firstly we retrieve all events from the Event database with their location and date
        Them we create a hash to quickly check if the event due date has already passed
        This is done to base recommendations in location and date!!!!!
    """
    events = Events.return_all_events_date_location()
    hash_event_id = {}
    for event in events:
        date = event[1][:10]
        date = date.split("-")
        date = dt.datetime(int(date[0]), int(date[1]), int(date[2]))
        hash_event_id[event[0]] = [date, event[2], event[3]]



    # We start by retrieving the similarity matrix from the disk with pickle
    similarities_matrix = pkl.load(open("similarities.pkl", "rb"))

    # Retrieve the attributes from the matrix
    index_to_id = similarities_matrix["index_to_id"]
    id_to_index = similarities_matrix["id_to_index"]
    similarities_matrix = similarities_matrix["similarities"]

    """
       Now we must compute the recommendation score for every event in the database!
       We start by retrieving the ratings from the user!
       Them we must get the corresponding index from the matching event id
       We do this to figure out the position of every event in the recommendation text
       Afterwards we compute the recommendations based on the formula
       sum (rating - 3)*similarity*time_decay_factor
       sort the list by score and return the top 20 recommendations!
   """
    # Here is the part we get the corresponding index on the text from the event id!
    # ratings_with_events_list is the variable that stores those indexes
    # REMINDER INDEX IN SIMILARITY MATRIX != EVENT ID
    ratings_with_events_list = []
    for rating in user_ratings:
        ratings_with_events_list.append((id_to_index[rating[0]], rating[1], rating[2]))


    """
        Finally construct the recommendations
        And store them in the form (user_id, event_id, score)!
        Also sort them according to the similarities score
    """
    recommendations = []
    now = time.time()
    for i in range(len(similarities_matrix)):
        score = 0
        for j, rating, timestamp in ratings_with_events_list:
            score = score + (rating - 3) * similarities_matrix[i, j] * math.exp(time_decay*(now - timestamp))

        recommendations.append((user_id, events[i][0], score))
    recommendations = sorted(recommendations, key=lambda x: x[2])
    recommendations.reverse()

    """
        Finally we need to filter the recommendations
        We only want to recommend events that haven't happened yet!!
    """
    today_time = dt.datetime.now()
    final_recommendations = []
    for recommendation in recommendations:
        if today_time > hash_event_id[recommendation[1]][0]:
            continue
        else:
            final_recommendations.append(recommendation)

        if len(final_recommendations) == 50:
            break

    """
        Delete old recommendations and add the new ones!!!!
        
    """
    Recommendations.delete_recommendations_from_user(int(user_id))
    for recommendation in final_recommendations:
        Recommendations.add_recommendation(int(recommendation[0]), int(recommendation[1]), recommendation[2])



if __name__ == "__main__":

    Recommendations = RecomendationDBManager()
    Events = EventsDBManager()
    Ratings = UserRatingManager()
    ratings = Ratings.get_ratings_from_user(1)
    generate_user_recommendations(Events, ratings, 1, Recommendations)