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
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
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
            this is done since we need to assign a new
        """

        sql_command = """
                    SELECT user_id
                    FROM Users
                """
        self.controller.execute(sql_command)
        all_ids = self.controller.fetchall()
        print('all_ids')
        print(all_ids)
        if len(all_ids) == 0:
            self.last_id = -1
        else:
            self.last_id = all_ids[-1][0]


    def create_new_user(self, uname, psw, address, city, latitute, longitude):

        """
            This function adds a new user to the user db table!
            It takes the given username and password to create it
            We assume the check for unique usernames is done at the front end level
        """

        self.last_id = self.last_id + 1
        sql_command = """
            INSERT INTO Users(user_id, uname, pword, address, city, latitude, longitude)
            VALUES ( ?, ?, ?, ?, ?, ?, ? );
        """

        values = (self.last_id, uname, psw, address, city, latitute, longitude)
        self.controller.execute(sql_command, values)
        self.connection.commit()


    def return_user_data(self, uname):

        """
            This function must return the user profile based on the username
            It needs other database classes to work with it!
            For now just return the basic stuff
        """
        sql_command = """
                    SELECT *
                    FROM Users
                    WHERE uname='{0}'
                """.format(uname)
        self.controller.execute(sql_command)
        return self.controller.fetchall()[0]


    def return_user_id(self, uname):

        """
            This function takes in a username and returns a user id!
            The user names must all be unique
            We check the creation of usernames to avoid duplicates
        """
        sql_command = """
                            SELECT user_id
                            FROM Users
                            WHERE uname='{0}'
                        """.format(uname)
        self.controller.execute(sql_command)
        user_id = self.controller.fetchall()

        if(len(user_id) != 1):
            raise Exception("Fatal error occurred two ids for one username")

        return user_id[0][0]

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


    def user_authentication(self, uname, password):
        """
            This function returns true if the username matches the password
            False otherwise
        """
        sql_command = """
                    SELECT uname, pword
                    FROM Users
                    WHERE uname = '{0}'
                """.format(uname)
        self.controller.execute(sql_command)
        compare = self.controller.fetchall()
        if password == compare[0][1]:
            return True
        else:
            return False


    def check_database(self):
        # Returns everything in it
        sql_command = """
                    SELECT *
                    FROM Users
                """
        self.controller.execute(sql_command)

        print('checke_database')

        for col in self.controller.fetchall():
            print(col)

    def delete_user_table(self):
        """
            Created for debuging
            Deletes the data in the user table!
        """

        sql_command = """
                        DELETE FROM Users;
                    """
        self.controller.execute(sql_command)
        self.connection.commit()

    def drop_table(self):
        """
            Created for debuging
            Drops the table!
        """

        sql_command = """
                    DROP TABLE Users;
                """
        self.connection.execute(sql_command)


if __name__ == "__main__":

    UserDB = UserdbManagement()
    UserDB.check_database()
    UserDB.create_new_user('Li', 'nopw', 123, 12)
    UserDB.create_new_user('Fafa', '123', 11, 22)
    print('usernames')
    print(UserDB.return_usernames())
    print('fafa_re')
    print(UserDB.return_user_data("Fafa"))
    print('fafa_123_re')
    print(UserDB.user_authentication("Fafa","123"))
    print('all_list')
    print(UserDB.check_database())
