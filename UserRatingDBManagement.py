import sqlite3
from BackendAPIStaticList import singleton
from threading import Lock

@singleton
class UserRatingManager:
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

    def add_rating(self, user_id, event_id, rating, timestamp):
        """
            This function adds a event rating made by the user to the database
        """
        with self.lock:
            self.dbconnect()
            if type(user_id) != int or type(event_id) != int or type(timestamp) != int:
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
            # print('existing_rating')
            # print(existing_rating)
            if len(existing_rating) == 0:
                sql_command = """
                            INSERT INTO UserRating(user_id, event_id, rating, timestamp)
                            VALUES ( ? , ? , ?,  ?);
                        """

                values = (user_id, event_id, rating, timestamp)
                self.controller.execute(sql_command, values)
                self.connection.commit()
            else:
                sql_command = """
                            UPDATE UserRating SET rating = {0}
                            WHERE user_id = '{1}'
                            AND event_id = '{2}'
                            AND timestamp = '{3}'
                        """.format(rating,user_id,event_id, timestamp)
                self.controller.execute(sql_command)
                self.connection.commit()
            self.dbdeconnect()
        print("Rating added --- user:{0} --- event:{1}".format(user_id, event_id))

    def remove_rating(self, user_id, event_id):

        """
            This function removes a event rating made by the user to the database
        """

        if type(user_id) != int or type(event_id) != int:
            raise TypeError("Values must be integers")
        with self.lock:
            self.dbconnect()
            sql_command = """
                           DELETE FROM UserRating 
                           WHERE UserRating.user_id = '{0}'
                           AND UserRating.event_id = '{1}'
                        """.format(user_id, event_id)

            self.controller.execute(sql_command)
            self.connection.commit()
            self.dbdeconnect()

    def get_ratings_from_user(self, user_id):

        """
            This function returns all event ratings from a specific user
            It returns it in the format [(event_id, rating), (event_id, rating) ..... ]
            This allows us to compute the recommendations
        """
        if type(user_id) != int:
            raise TypeError("User id must be an int")

        with self.lock:
            self.dbconnect()
            sql_command = """
                            SELECT event_id, rating, timestamp
                            FROM UserRating
                            WHERE user_id = '{0}'
                        """.format(user_id)
            self.controller.execute(sql_command)

            ratings = self.controller.fetchall()
            self.dbdeconnect()
        return ratings

    def get_unrated_events(self, user_id):

        """
            This function returns a list of all unrated events
            This is done to create the rating events page
            So the user can rate events he has yet not rated!
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                            SELECT event_id
                            FROM Events
                            WHERE event_id NOT IN(
                            SELECT event_id FROM UserRating
                            )
                        """.format(user_id)

            self.controller.execute(sql_command)

            ids = [x[0] for x in self.controller.fetchall()]
            self.dbdeconnect()
        return ids


    def check_database(self):

        """
            Just checking the database!
            Returns everything in it
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                        SELECT *
                        FROM UserRating
                    """
            self.controller.execute(sql_command)
            print('check_database')
            result = self.controller.fetchall()
            # for col in result:
            #     print(col)
            self.dbdeconnect()
        return result

    def delete_ratings_table(self):
        """
            Created for debuging
            Deletes the data in the user ratings!
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                            DELETE FROM UserRating;
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
                        DROP TABLE UserRating;
                    """
            self.connection.execute(sql_command)
            self.dbdeconnect()

if __name__ == "__main__":
    userRatingManager = UserRatingManager()
    print(userRatingManager.check_database())
    # userRatingManager.add_rating(0,0,1)
    # userRatingManager.add_rating(0,1,2)
    # userRatingManager.add_rating(0,2,5)
    # print(userRatingManager.get_ratings_from_user(0))
    # userRatingManager.delete_ratings_table()
    # userRatingManager.drop_table()
