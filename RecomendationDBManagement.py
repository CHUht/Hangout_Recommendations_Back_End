import sqlite3
from BackendAPIStaticList import singleton
from threading import Lock

@singleton
class RecomendationDBManager:
    def __init__(self):

        """
            Here we start all the points necessary to start this class
            We need to connect to the database
            and get the last id!
        """
        self.lock = Lock()
    def dbconnect(self):
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
        self.controller = self.connection.cursor()


    def dbdeconnect(self):
        self.connection.close()

    def add_recommendation(self, user_id, event_id, score):

        """
            This function is used
        """

        with self.lock:
            self.dbconnect()
            sql_command = """
                        INSERT INTO UserRecommendations(user_id, event_id, score)
                        VALUES ( ? , ? , ?);
                    """

            values = (user_id, event_id, score)
            self.controller.execute(sql_command, values)
            self.connection.commit()
            self.dbdeconnect()

    def remove_recommendation(self, user_id, event_id):

        """
            This function removes a event rating made by the user to the database
        """

        with self.lock:
            self.dbconnect()
            sql_command = """
                           DELETE FROM UserRating 
                           WHERE UserRecommendations.user_id = '{0}'
                           AND UserRecommendations.event_id = '{1}'
                        """.format(user_id, event_id)

            self.controller.execute(sql_command)
            self.connection.commit()
            self.dbdeconnect()

    def get_recommendations_for_user(self, user_id):

        """
            This function returns all event ratings from a specific user
            It returns it in the format [(event_id, rating), (event_id, rating) ..... ]
            This allows us to compute the recommendations
        """

        with self.lock:
            self.dbconnect()
            sql_command = """
                            SELECT event_id, score
                            FROM UserRecommendations
                            WHERE user_id = '{0}'
                            ORDER BY score
                        """.format(user_id)
            self.controller.execute(sql_command)
            recommendations = self.controller.fetchall()
            recommendations = list(recommendations)

            self.dbdeconnect()

        return recommendations

    def check_database(self):

        """
            Just checking the database!
            Returns everything in it
        """

        with self.lock:
            self.dbconnect()
            sql_command = """
                        SELECT *
                        FROM UserRecommendations
                    """
            self.controller.execute(sql_command)

            request = self.controller.fetchall()
            for col in request:
                print(col)
            self.dbdeconnect()

    def delete_recommendations_from_user(self, user_id):
        """
            This function deletes all recommendations from a specific user
            This is done to update the recommendations!
        """

        with self.lock:
            self.dbconnect()
            sql_command = """
                            DELETE FROM UserRecommendations
                            WHERE user_id = '{0}'
                        """.format(user_id)

            self.controller.execute(sql_command)
            self.connection.commit()
            self.dbdeconnect()

    def delete_recommendations_table(self):
        """
            Created for debuging
            Deletes the data in the user recommendations!
        """

        with self.lock:
            self.dbconnect()
            sql_command = """
                            DELETE FROM UserRecommendations;
                        """
            self.controller.execute(sql_command)
            self.connection.commit()

            sql_command = """
                            VACUUM;
                        """
            self.controller.execute(sql_command)
            self.connection.commit()
            self.dbdeconnect()

    def drop_table(self):
        """
            Created for debuging
            Drops the table!
        """

        with self.lock:
            self.dbconnect()
            sql_command = """
                        DROP TABLE UserRecommendations;
                    """
            self.connection.execute(sql_command)
            self.dbdeconnect()

if __name__ == "__main__":

    rmanager = RecomendationDBManager()
    # rmanager.delete_recommendations_table()
    print(rmanager.check_database())


