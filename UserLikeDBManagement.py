import sqlite3
from UserRatingDBManagement import UserRatingManager
from BackendAPIStaticList import singleton

@singleton
class UserLikeManager:
    def __init__(self):

        """
            Here we start all the points necessary to start this class
            We need to connect to the database
            and get the last id!
        """
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
        self.controller = self.connection.cursor()

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
        userRatingManager = UserRatingManager()
        userRatingManager.add_rating(user_id,event_id,5)


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

    def delete_userlike_table(self):
        """
            Created for debuging
            Deletes the data in the user ratings!
        """

        sql_command = """
                        DELETE FROM UserLike;
                    """
        self.controller.execute(sql_command)
        self.connection.commit()

        sql_command = """
                        VACUUM;
                    """
        self.controller.execute(sql_command)
        self.connection.commit()

    def drop_table(self):
        """
            Created for debuging
            Drops the table!
        """

        sql_command = """
                    DROP TABLE UserLike;
                """
        self.connection.execute(sql_command)

if __name__ == "__main__":

    userLikeManager = UserLikeManager()
    userLikeManager2 = UserLikeManager()
    print(userLikeManager,userLikeManager2)
