import sqlite3


class UserRatings:

    management_instances_created = 0

    def __init__(self):

        self.check_number_of_instances()

        """
            Here we start all the points necessary to start this class
            We need to connect to the database
            and get the last id!
        """
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
        self.controller = self.connection.cursor()

    def check_number_of_instances(self):

        """
            To avoid conflicts we only generate a single instance of each db manager
        """

        if UserRatings.management_instances_created != 0:
            raise ValueError("There can only be one database manager")
        else:
            UserRatings.management_instances_created = UserRatings.management_instances_created + 1

    def add_rating(self, user_id, event_id, rating):

        """
            This function adds a event rating made by the user to the database
        """

        if type(user_id) != int or type(event_id) != int or type(rating) != int:
            raise TypeError("Values must be integers")
        # to verify if this event for this user has already been rated. if yes, override it. else, insert it into database
        sql_command = """
                        SELECT user_id, event_id, rating
                        FROM UserRating
                        WHERE user_id = '{0}'
                        AND event_id = '{1}'
                    """.format(user_id,event_id)

        self.controller.execute(sql_command)
        existing_rating = self.controller.fetchall()
        print('existing_rating')
        print(existing_rating)
        if len(existing_rating) == 0:
            sql_command = """
                        INSERT INTO UserRating(user_id, event_id, rating)
                        VALUES ( ? , ? , ?);
                    """

            values = (user_id, event_id, rating)
            self.controller.execute(sql_command, values)
            self.connection.commit()
        else:
            sql_command = """
                        UPDATE UserRating SET rating = {0}
                        WHERE user_id = '{1}'
                        AND event_id = '{2}'
                    """.format(rating,user_id,event_id)
            self.controller.execute(sql_command)
            self.connection.commit()

    def remove_rating(self, user_id, event_id):

        """
            This function removes a event rating made by the user to the database
        """

        if type(user_id) != int or type(event_id) != int:
            raise TypeError("Values must be integers")

        sql_command = """
                       DELETE FROM UserRating 
                       WHERE UserRating.user_id = '{0}'
                       AND UserRating.event_id = '{1}'
                    """.format(user_id, event_id)

        self.controller.execute(sql_command)
        self.connection.commit()

    def get_ratings_from_user(self, user_id):

        """
            This function returns all event ratings from a specific user
            It returns it in the format [(event_id, rating), (event_id, rating) ..... ]
            This allows us to compute the recommendations
        """

        if type(user_id) != int:
            raise TypeError("User id must be an int")

        sql_command = """
                        SELECT event_id, rating
                        FROM UserRating
                        WHERE user_id = '{0}'
                    """.format(user_id)
        self.controller.execute(sql_command)

        ratings = self.controller.fetchall()
        return ratings

    def get_unrated_events(self, user_id):

        """
            This function returns a list of all unrated events
            This is done to create the rating events page
            So the user can rate events he has yet not rated!
        """

        sql_command = """
                        SELECT event_id
                        FROM Events
                        WHERE event_id NOT IN(
                        SELECT event_id FROM UserRating
                        )
                    """.format(user_id)

        self.controller.execute(sql_command)

        ids = [x[0] for x in self.controller.fetchall()]
        return ids


    def check_database(self):

        """
            Just checking the database!
            Returns everything in it
        """

        sql_command = """
                    SELECT *
                    FROM UserRating
                """
        self.controller.execute(sql_command)
        print('check_database')
        for col in self.controller.fetchall():
            print(col)


    def delete_ratings_table(self):
        """
            Created for debuging
            Deletes the data in the user ratings!
        """

        sql_command = """
                        DELETE FROM UserRating;
                    """
        self.controller.execute(sql_command)
        self.connection.commit()

if __name__ == "__main__":

    userRatings = UserRatings()
    userRatings.check_database()
    userRatings.add_rating(0,0,1)
    userRatings.add_rating(0,1,2)
    userRatings.add_rating(0,2,5)
    print('get_rating_from_user for user 0 ')
    print(userRatings.get_ratings_from_user(0))
