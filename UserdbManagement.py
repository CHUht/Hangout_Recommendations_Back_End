import sqlite3


class UserdbManagement:

    management_instances_created = 0

    def __init__(self):

        self.check_number_of_instances()

        """
            Here we start all the points necessary to start this class
            We need to connect to the database
            and get the last id!
        """
        self.connection = sqlite3.connect("UserTable.db", check_same_thread=False)
        self.controller = self.connection.cursor()

        self.set_last_id()

    def check_number_of_instances(self):

        if( UserdbManagement.management_instances_created != 0):
            raise ValueError("There can only be one database manager")
        else:
            UserdbManagement.management_instances_created = UserdbManagement.management_instances_created + 1


    def set_last_id(self):

        """
            In this function we find the last id on the database
            this is done since we need to assing a new
        """

        sql_command = """
                    SELECT user_id
                    FROM Users
                """
        self.controller.execute(sql_command)
        all_ids = self.controller.fetchall()
        self.last_id = all_ids[-1][0]


    def create_new_user(self, uname, psw, latitute, longitude):

        """
            This function adds a new user to the user db table!
            It takes the given username and password to create it
            We assume the check for unique usernames is done at the front end level
        """

        self.last_id = self.last_id + 1
        sql_command = """
            INSERT INTO Users(user_id, uname, pword, latitude, longitude)
            VALUES ( ? , ?, ?, ?, ? );
        """.format(self.last_id, uname, psw, latitute, longitude)

        values = (self.last_id, uname, psw, latitute, longitude)
        self.controller.execute(sql_command, values)
        self.connection.commit()


    def return_user_data(self, user_id):

        """
            This function must return the user profile based on the username
            It needs other database classes to work with it!
            For now just return the basic stuff
        """
        sql_command = """
                    SELECT *
                    FROM Users
                    WHERE user_id='{0}'
                """.format(user_id)
        self.controller.execute(sql_command)
        res = self.controller.fetchall()
        if len(res) == 0:
            return []
        user = {
            'user_id': res[0][0],
            'uname': res[0][1],
            'latitude': res[0][3],
            'longitude': res[0][4]
        }
        return [user]



    def return_usernames(self):

        """
            This function returns a list with all usernames
            This is done in the server level to check if there are any matching usernames
        """

        sql_command = """
                    SELECT uname
                    FROM Users
                """
        self.controller.execute(sql_command)
        unames = []
        for value in self.controller.fetchall():
            unames.append(value[0])
        return unames


    def user_authentication(self, user_id, password):
        """
            This function returns true if the username matches the password
            False otherwise
        """
        sql_command = """
                    SELECT user_id, pword
                    FROM Users
                    WHERE user_id = '{0}'
                """.format(user_id)
        self.controller.execute(sql_command)
        compare = self.controller.fetchall()
        if password == compare[0][1]:
            return True
        else:
            return False


    def check_database(self):

        sql_command = """
                    SELECT *
                    FROM Users
                """
        self.controller.execute(sql_command)

        for col in self.controller.fetchall():
            print(col)





if __name__ == "__main__":

    UserDB = UserdbManagement()
    UserDB.check_database()
    print(UserDB.return_usernames())
    print(UserDB.return_user_data("Fafa"))
    print(UserDB.user_authentication("Fafa","123"))