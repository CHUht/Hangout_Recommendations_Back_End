import sqlite3
from BackendAPIStaticList import singleton

@singleton
class UserDBManager:
    def __init__(self):
        """
            Here we start all the points necessary to start this class
            We need to connect to the database
            and get the last id!
        """
        self.set_last_id()

    def dbconnect(self):
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
        self.controller = self.connection.cursor()

    def dbdeconnect(self):
        self.connection.close()

    def set_last_id(self):

        """
            In this function we find the last id on the database
            this is done since we need to assign a new
        """
        self.dbconnect()
        sql_command = """
                    SELECT user_id
                    FROM Users
                """
        self.controller.execute(sql_command)
        all_ids = self.controller.fetchall()
        self.dbdeconnect()
        # print('all_ids')
        # print(all_ids)
        if len(all_ids) == 0:
            self.last_id = -1
        else:
            self.last_id = all_ids[-1][0]


    def create_new_user(self, uname, psw, email ,address = None, city = 'Paris'):

        """
            This function adds a new user to the user db table!
            It takes the given username and password to create it
            We assume the check for unique usernames is done at the front end level
        """
        self.dbconnect()
        self.last_id = self.last_id + 1
        sql_command = """
            INSERT INTO Users(user_id, uname, pword, email, address, city)
            VALUES ( ?, ?, ?, ?, ?, ? );
        """

        values = (self.last_id, uname, psw, address, city, email)
        self.controller.execute(sql_command, values)
        self.connection.commit()
        self.dbdeconnect()

    def modify_password(self,uname:str,new_password:str):
        """
            This function must return the user profile based on the username
            It needs other database classes to work with it!
            For now just return the basic stuff
        """
        self.dbconnect()
        sql_command = """
            UPDATE Users SET pword = {0}
            WHERE uname = '{1}';
            """.format(new_password,uname)
        self.controller.execute(sql_command)
        self.dbdeconnect()

    def return_user_data(self, uname):

        """
            This function must return the user profile based on the username
            It needs other database classes to work with it!
            For now just return the basic stuff
        """
        self.dbconnect()
        sql_command = """
                    SELECT *
                    FROM Users
                    WHERE uname='{0}'
                """.format(uname)
        self.controller.execute(sql_command)
        if len(self.controller.fetchall()) != 0:
            result = self.controller.fetchall()[0]
        else:
            result = []
        self.dbdeconnect()
        return result

    def return_user_data_by_email(self, email):

        """
            This function must return the user profile based on the email
            It needs other database classes to work with it!
            For now just return the basic stuff
        """
        self.dbconnect()
        sql_command = """
                       SELECT *
                       FROM Users
                       WHERE email='{0}'
                   """.format(email)
        self.controller.execute(sql_command)
        result = self.controller.fetchall()[0]
        self.dbdeconnect()
        return result

    def return_user_id(self, uname):

        """
            This function takes in a username and returns a user id!
            The user names must all be unique
            We check the creation of usernames to avoid duplicates
        """
        self.dbconnect()
        sql_command = """
                            SELECT user_id
                            FROM Users
                            WHERE uname='{0}'
                        """.format(uname)
        self.controller.execute(sql_command)
        user_id = self.controller.fetchall()
        self.dbdeconnect()

        if(len(user_id) != 1):
            raise Exception("Fatal error occurred two ids for one username")

        return user_id[0][0]

    def return_usernames(self):

        """
            This function returns a list with all usernames
            This is done in the server level to check if there are any matching usernames
        """
        self.dbconnect()
        sql_command = """
                    SELECT uname
                    FROM Users
                """
        self.controller.execute(sql_command)
        unames = []
        for value in self.controller.fetchall():
            unames.append(value[0])
        self.dbdeconnect()
        return unames


    def user_authentication(self, uname, password):
        """
            This function returns true if the username matches the password
            False otherwise
        """
        self.dbconnect()
        sql_command = """
                    SELECT uname, pword 
                    FROM Users
                    WHERE uname = '{0}'
                """.format(uname)
        self.controller.execute(sql_command)
        compare = self.controller.fetchall()
        self.dbdeconnect()
        if password == compare[0][1]:
            return True
        else:
            return False

    def email_authentication(self, email, password):
        """
            This function returns true if the username matches the password
            False otherwise
        """
        self.dbconnect()
        sql_command = """
                    SELECT email, pword
                    FROM Users
                    WHERE email = '{0}'
                """.format(email)
        self.controller.execute(sql_command)
        compare = self.controller.fetchall()
        self.dbdeconnect()
        if password == compare[0][1]:
            return True
        else:
            return False


    def check_database(self):
        # Returns everything in it
        self.dbconnect()
        sql_command = """
                    SELECT *
                    FROM Users
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
                        DELETE FROM Users;
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
                    DROP TABLE Users;
                """
        self.connection.execute(sql_command)
        self.dbdeconnect()

if __name__ == "__main__":
    userDBManager = UserDBManager()
    print(userDBManager.check_database()[0][0])
    # userDBManager.create_new_user('Li', 'nopw', 'lizhihaozyz@gmail.com')
    # userDBManager.create_new_user('Lu','withpw','jiaohao.li@student-cs.fr')
    # userDBManager.delete_user_table()
    # userDBManager.drop_table()
    # print(userDBManager.return_usernames())
    # print(userDBManager.check_database())
