import sqlite3
from BackendAPIStaticList import singleton

@singleton
class RecomendationDBManager:
    def __init__(self):

        """
            Here we start all the points necessary to start this class
            We need to connect to the database
            and get the last id!
        """
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
        self.controller = self.connection.cursor()

    def add_recommendation(self, user_id, event_id, score):

        """
            This function is used
        """

        sql_command = """
                    INSERT INTO UserRecommendation(user_id, event_id, score)
                    VALUES ( ? , ? , ?);
                """

        values = (user_id, event_id, score)
        self.controller.execute(sql_command, values)
        self.connection.commit()

    def remove_recommendation(self, user_id, event_id):

        """
            This function removes a event rating made by the user to the database
        """

        sql_command = """
                       DELETE FROM UserRating 
                       WHERE UserRecommendation.user_id = '{0}'
                       AND UserRecommendation.event_id = '{1}'
                    """.format(user_id, event_id)

        self.controller.execute(sql_command)
        self.connection.commit()

    def get_recommendations_for_user(self, user_id):

        """
            This function returns all event ratings from a specific user
            It returns it in the format [(event_id, rating), (event_id, rating) ..... ]
            This allows us to compute the recommendations
        """

        sql_command = """
                        SELECT event_id, score
                        FROM UserRecommendation
                        WHERE user_id = '{0}'
                        ORDER BY score
                    """.format(user_id)
        self.controller.execute(sql_command)

        return self.controller.fetchall()

    def check_database(self):

        """
            Just checking the database!
            Returns everything in it
        """

        sql_command = """
                    SELECT *
                    FROM UserRecommendations
                """
        self.controller.execute(sql_command)

        for col in self.controller.fetchall():
            print(col)


    def delete_ratings_table(self):
        """
            Created for debuging
            Deletes the data in the user ratings!
        """

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

if __name__ == "__main__":
    rmanager = RecomendationDBManager()
    rmanager.add_recommendation(0, 2270,5)

