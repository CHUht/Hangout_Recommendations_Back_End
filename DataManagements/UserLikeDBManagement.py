import sqlite3
from DataManagements.UserRatingDBManagement import UserRatingManager
from DataManagements.BackendAPIStaticList import singleton

@singleton
class UserLikeManager:
    def __init__(self):
        pass

    def dbconnect(self):
        """
        connection to the db
        :return: None
        """
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
        self.controller = self.connection.cursor()

    def dbdeconnect(self):
        """
        deconnection from the db
        :return: None
        """
        self.connection.close()

    def add_like(self, user_id, event_id):
        """
        This function adds an event like made by the user to the database
        :param user_id: user id
        :param event_id: event id
        :return: None
        """
        if type(user_id) != int or type(event_id) != int:
            raise TypeError("Values must be integers")
        # to verify if this event for this user has already been rated. if yes, override it. else, insert it into database
        self.dbconnect()
        sql_command = """
                        SELECT user_id, event_id
                        FROM UserLike
                        WHERE user_id = '{0}'
                        AND event_id = '{1}'
                    """.format(user_id,event_id)
        self.controller.execute(sql_command)
        existing_event_like = self.controller.fetchall()
        if len(existing_event_like) == 0:
            sql_command = """
                        INSERT INTO UserLike(user_id, event_id)
                        VALUES ( ? , ?);
                    """

            values = (user_id, event_id)
            self.controller.execute(sql_command, values)
            self.connection.commit()
        self.dbdeconnect()
        # if user likes one event, should rate it 5 points automatically
        userRatingManager = UserRatingManager()
        userRatingManager.add_rating(user_id,event_id,5)


    def remove_like(self, user_id, event_id):
        """
        This function removes an event like made by the user to the database
        :param user_id: user id
        :param event_id: event id
        :return: None
        """
        if type(user_id) != int or type(event_id) != int:
            raise TypeError("Values must be integers")
        self.dbconnect()
        sql_command = """
                       DELETE FROM UserLike
                       WHERE UserLike.user_id = '{0}'
                       AND UserLike.event_id = '{1}'
                    """.format(user_id, event_id)
        self.controller.execute(sql_command)
        self.connection.commit()
        self.dbdeconnect()

    def get_likes_id_from_user(self, user_id):
        """
        This function returns all event likes from a specific user
        It returns it in the format [(event_id), (event_id) ..... ]
        This allows us to compute the recommendations
        :param user_id: user id
        :return: a list of user liked event ids
        """
        if type(user_id) != int:
            raise TypeError("User id must be an int")
        self.dbconnect()
        sql_command = """
                        SELECT event_id
                        FROM UserLike
                        WHERE user_id = '{0}'
                    """.format(user_id)
        self.controller.execute(sql_command)
        likes = self.controller.fetchall()
        self.dbdeconnect()
        for i in range(len(likes)):
            likes[i] = likes[i][0]
        return likes

    def return_like_events_from_user(self,user_id):
        """
        see get_likes_id_from_user
        :param user_id: user if
        :return: all likes of the user
        """
        self.get_likes_id_from_user()

    def check_database(self):
        """
        Just checking the database!
        Returns everything in it
        :return: a list of all things in this table
        """
        self.dbconnect()
        sql_command = """
                    SELECT *
                    FROM UserLike
                """
        self.controller.execute(sql_command)
        print('check_database')
        result = self.controller.fetchall()
        self.dbdeconnect()
        return result

    def delete_userlike_table(self):
        """
        Created for debuging
        Deletes the data in the user ratings!
        :return: None
        """
        self.dbconnect()
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
        self.dbdeconnect()

    def drop_table(self):
        """
        Created for debuging
        Drops the table!
        :return: None
        """
        self.dbconnect()
        sql_command = """
                    DROP TABLE UserLike;
                """
        self.connection.execute(sql_command)
        self.dbdeconnect()

if __name__ == "__main__":

    userLikeManager = UserLikeManager()
    # print(userLikeManager.check_database())
    # userLikeManager.drop_table()
    userLikeManager.add_like(1,2)
    userLikeManager.add_like(2,3)
    userLikeManager.get_likes_id_from_user(1)
