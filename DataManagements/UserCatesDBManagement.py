import sqlite3
from DataManagements.BackendAPIStaticList import singleton
from DataManagements.BackendAPIStaticList import cate_map

@singleton
class UserCatesManager:
    def __init__(self):
        pass

    def dbconnect(self):
        """
        connect to the database
        :return: None
        """
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
        self.controller = self.connection.cursor()

    def dbdeconnect(self):
        """
        deconnecct from the database
        :return:None
        """
        self.connection.close()

    def get_all_cates(self):
        """
        this function returns a list of strings, all kinds of categories
        :return: list of all categories
        """
        to_return = list(cate_map.values())
        return to_return

    def insert_user_cates(self, user_id:int, cate_type_list:set):

        """
            This function adds a new user to the user db table!
            It takes the given username and password to create it
            We assume the check for unique usernames is done at the front end level
        """
        self.dbconnect()
        sql_command = """
                    SELECT cate_type
                    FROM UserCates
                    WHERE user_id = '{0}'
                """.format(user_id)
        self.controller.execute(sql_command)
        already_cates = self.controller.fetchall()
        for i in range(len(already_cates)):
            already_cates[i] = already_cates[i][0]
        already_cates = set(already_cates)
        to_insert = cate_type_list - already_cates

        for cate_type in to_insert:
            sql_command = """
                INSERT INTO UserCates(user_id, cate_type)
                VALUES ( ?, ?);
            """

            values = (user_id,cate_type)
            self.controller.execute(sql_command, values)
            self.connection.commit()
        self.dbdeconnect()

    def return_user_cates(self, user_id):

        """
            This function must return the user profile based on the username
            It needs other database classes to work with it!
            For now just return the basic stuff
        """
        self.dbconnect()
        sql_command = """
                    SELECT cate_type
                    FROM UserCates
                    WHERE user_id='{0}'
                """.format(user_id)
        self.controller.execute(sql_command)
        result = self.controller.fetchall()
        for i in range(len(result)):
            result[i] = result[i][0]
        self.dbdeconnect()
        return result

    def return_cate_user(self, cate_type:int):

        """
            This function takes in a username and returns a user id!
            The user names must all be unique
            We check the creation of usernames to avoid duplicates
        """
        self.dbconnect()
        sql_command = """
                            SELECT user_id
                            FROM UserCates
                            WHERE cate_type='{0}'
                        """.format(cate_type)
        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()
        for i in range(len(query_result)):
            query_result[i] = query_result[i][0]
        self.dbdeconnect()


        return query_result

    def check_database(self):
        # Returns everything in it
        self.dbconnect()
        sql_command = """
                    SELECT *
                    FROM UserCates
                """
        self.controller.execute(sql_command)

        # print('checke_database')

        # for col in self.controller.fetchall():
        #     print(col)
        result = self.controller.fetchall()
        self.dbdeconnect()
        return result

    def delete_user_table(self):
        """
            Created for debuging
            Deletes the data in the user table!
        """
        self.dbconnect()
        sql_command = """
                        DELETE FROM UserCates;
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
        self.dbconnect()
        sql_command = """
                    DROP TABLE UserCates;
                """
        self.connection.execute(sql_command)
        self.dbdeconnect()

if __name__ == "__main__":
    userCatesManager = UserCatesManager()
    # userCatesManager.insert_user_tags(0,[1,4,13])
    userCatesManager.insert_user_cates(0,{1,5,12})
    userCatesManager.insert_user_cates(1,{1,6,14})
    print(userCatesManager.return_user_cates(0))
    print(userCatesManager.return_cate_user(1))
    print(userCatesManager.check_database())
    print(userCatesManager.get_all_cates())
    # userCatesManager.delete_user_table()
    # UserCatesManager.drop_table()
