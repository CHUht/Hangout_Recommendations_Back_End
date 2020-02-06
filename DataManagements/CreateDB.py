import sqlite3

class CreatDataBase:
    def __init__(self, table_name):
        self.table_name = table_name
        self._connection = sqlite3.connect('./Database.db')

        # cursor
        self._cursor = self._connection.cursor()

    def create_table(self, attributs):
        # SQL command to create a table in the database
        attri_string = ''
        if type(attributs) == dict:
            for name, attritype in attributs.items():
                attri_string += name + ' ' + attritype + ','
            attri_string = attri_string[:-1]
        else:
            print('attributs should be organized in dict')
            return 0
        try:
            sql_command = "CREATE TABLE " + self.table_name + " (" + attri_string + ');'
            # execute the statement
            self._cursor.execute(sql_command)
            print(self.table_name + ' created')
        except sqlite3.OperationalError:
            print('trying to creat table',self.table_name,'which already exists')


        self._connection.close()

def create_databases():
    databases = []
    att1 = {'event_id': 'INTEGER PRIMARY KEY',
                'title': 'VARCHAR(50)',
                'category': 'VARCHAR(50)',
                'price': 'VARCHAR(50)',
                'description': 'VARCHAR(300)',
                'link': 'VARCHAR(50)',
                'telephone': 'VARCHAR(50)',
                'tags': 'VARCHAR(50)',
                'address_street': 'VARCHAR(50)',
                'address_city': 'VARCHAR(50)',
                'address_zipcode': 'VARCHAR(50)',
                'date': 'VARCHAR(50)',
                'date_end': 'VARCHAR(50)',
                'contact_mail': 'VARCHAR(50)',
                'facebook': 'VARCHAR(50)',
                'website': 'VARCHAR(50)',
                'cover_url':'VARCHAR(50)',
                'latitude': 'FLOAT(8)',
                'longitude': 'FLOAT(8)',
                'occurrences':'VARCHAR(1000)',
                'large_category':'VARCHAR(50)',
                'small_category':'VARCHAR(50)',
            }
    databases.append(('Events',att1))

    att2 = {'user_id':'INTEGER PRIMARY KEY',
                'uname': 'VARCHAR(50)',
                'pword': 'VARCHAR(50)',
                'email': 'VARCHAR(50)',
                'address': 'VARCHAR(50)',
                'city': 'VARCHAR(50)'}
    databases.append(('Users',att2))

    att3 = {'user_id': 'INTEGER',
                'event_id': 'INTEGER',
                'rating': 'INTEGER'}
    databases.append(('UserRating',att3))

    att4 = {'user_id': 'INTEGER',
                'event_id': 'INTEGER',
                'score': 'FLOAT(8)'}
    databases.append(('UserRecommendations',att4))

    att5 = {'user_id': 'INTEGER',
                'event_id': 'INTEGER'}
    databases.append(('UserLike',att5))

    att6 = {'user_id': 'INTEGER',
                'cate_type': 'INTEGER'}
    databases.append(('UserCates',att6))
    # print(databases)
    for i in range(len(databases)):
        cdb = CreatDataBase(databases[i][0])
        cdb.create_table(databases[i][1])

if __name__ == "__main__":
    create_databases()
