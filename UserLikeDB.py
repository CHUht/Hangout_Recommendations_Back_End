import sqlite3
from UserRatingDb import UserRatings


class UserLike:

    management_instances_created = 0

    def __init__(self):

        self.check_number_of_instances()

        """
            Here we start all the points necessary to start this class
            We need to connect to the database
            and get the last id!
        """
        self.connection = sqlite3.connect("UserLike.db", check_same_thread=False)
        self.controller = self.connection.cursor()

    def check_number_of_instances(self):

        """
            To avoid conflicts we only generate a single instance of each db manager
        """

        if UserLike.management_instances_created != 0:
            raise ValueError("There can only be one database manager")
        else:

            UserLike.management_instances_created = UserLike.management_instances_created + 1

    def add_like(self, user_id, event_id):

        """
            This function adds an event like made by the user to the database
        """

        if type(user_id) != int or type(event_id) != int:
            raise TypeError("Values must be integers")
        # to verify if this event for this user has already been rated. if yes, override it. else, insert it into database
        sql_command = """
                        SELECT user_id, event_id
                        FROM UserLike
                        WHERE user_id = '{0}'
                        AND event_id = '{1}'
                    """.format(user_id,event_id)

        self.controller.execute(sql_command)
        existing_event_like = self.controller.fetchall()
        print('existing_event_like')
        print(existing_event_like)
        if len(existing_event_like) == 0:
            sql_command = """
                        INSERT INTO UserLike(user_id, event_id)
                        VALUES ( ? , ?);
                    """

            values = (user_id, event_id)
            self.controller.execute(sql_command, values)
            self.connection.commit()
        # if user likes one event, should rate it 5 points automatically
        userRatings = UserRatings()
        userRatings.add_rating(user_id,event_id,5)


    def remove_like(self, user_id, event_id):

        """
            This function removes an event like made by the user to the database
        """

        if type(user_id) != int or type(event_id) != int:
            raise TypeError("Values must be integers")

        sql_command = """
                       DELETE FROM UserLike 
                       WHERE UserLike.user_id = '{0}'
                       AND UserLike.event_id = '{1}'
                    """.format(user_id, event_id)

        self.controller.execute(sql_command)
        self.connection.commit()

    def get_likes_from_user(self, user_id):

        """
            This function returns all event likes from a specific user
            It returns it in the format [(event_id), (event_id) ..... ]
            This allows us to compute the recommendations
        """

        if type(user_id) != int:
            raise TypeError("User id must be an int")

        sql_command = """
                        SELECT event_id
                        FROM UserLike
                        WHERE user_id = '{0}'
                    """.format(user_id)
        self.controller.execute(sql_command)

        likes = self.controller.fetchall()
        return likes


    def check_database(self):

        """
            Just checking the database!
            Returns everything in it
        """

        sql_command = """
                    SELECT *
                    FROM UserLike
                """
        self.controller.execute(sql_command)
        print('check_database')
        for col in self.controller.fetchall():
            print(col)


if __name__ == "__main__":

    UserLike = UserLike()
    UserLike.check_database()
    UserLike.add_like(0, 0)
    UserLike.add_like(0, 1)
    UserLike.add_like(0, 2)
    print('get_likes_from_user')
    print(UserLike.get_likes_from_user(0))
