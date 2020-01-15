import sqlite3
import re

class EventsDBManager:

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
        self.events_ids = self.retrieve_event_ids()
        self.tags = None
        self.categories = None

    def check_number_of_instances(self):

        """
            To avoid conflicts we only generate a single instance of each db manager
        """

        if EventsDBManager.management_instances_created != 0:
            raise ValueError("There can only be one database manager")
        else:
            EventsDBManager.management_instances_created = EventsDBManager.management_instances_created + 1

    def add_event(self, event_id, title, category, price, description,
                  link, telephone, tags, address_street, address_city,
                  address_zipcode, date, date_end, contact_mail, facebook, website,
                  cover_url, latitude, longitude):

        """
            This function adds a event to the event database
        """

        sql_command = """
                    INSERT INTO Events (event_id, title, category, price, description, 
                  link, telephone, tags, address_street, address_city, 
                  address_zipcode, date, date_end, contact_mail, facebook, website,
                  cover_url, latitude, longitude)
                    VALUES( ? , ?, ?, ?, ?, 
                  ? , ?, ?, ?, ?, 
                  ?, ?, ?, ?, ?, ?,
                  ?, ?, ?);
                """
        values = (event_id, title, category, price, description,
                  link, telephone, tags, address_street, address_city,
                  address_zipcode, date, date_end, contact_mail, facebook, website,
                  cover_url, latitude, longitude)

        self.controller.execute(sql_command, values)
        self.connection.commit()

    def remove_event(self, event_id):

        """
            This function removes a event rating made by the user to the database
        """

        sql_command = """
                       DELETE FROM Events
                       WHERE Events.event_id = '{0}'
                    """.format(event_id)

        self.controller.execute(sql_command)
        self.connection.commit()

    def retrieve_event_ids(self):

        """
            This function retrieves all event ids
            and creates a list to make sure they are unique!
        """

        sql_command = """
                        SELECT event_id
                        FROM Events
                    """
        self.controller.execute(sql_command)

        events_ids = []
        for event in self.controller.fetchall():
            events_ids.append(event[0])
        return events_ids

    def return_event(self, event_id):

        """
            This function returns in json format the event information based on the event id!
        """

        sql_command = """
                        SELECT *
                        FROM Events
                        WHERE event_id = '{0}'
                    """.format(event_id)

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()
        if len(query_result) == 0:
            return []
        event = {'event_id': query_result[0][0], 'title': query_result[0][1], 'category': query_result[0][2],
                 'price': query_result[0][3], 'description': query_result[0][4], 'link': query_result[0][5],
                 'telephone': query_result[0][6], 'tags': query_result[0][7], 'address_street': query_result[0][8],
                 'address_city': query_result[0][9], 'address_zipcode': query_result[0][10],
                 'date': query_result[0][11], 'date_end': query_result[0][12], 'contact_mail': query_result[0][13],
                 'facebook': query_result[0][14], 'website': query_result[0][15], 'cover_url': query_result[0][16],
                 'latitude': query_result[0][17], 'longitude': query_result[0][18]}

        return [event]


    def get_catagories(self):
        """
            This function returns a catagory statistics
        """
        sql_command = """
                        SELECT category
                        FROM Events
                    """

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()
        labels_list_large = []
        labels_list_small = []
        for i in query_result:
            match = re.match(r'(.*) -> (.*)',i[0])
            list_each_large = match.group(1)
            list_each_small = match.group(2)
            labels_list_large.append(list_each_large)
            labels_list_small.append(list_each_small)
        category_labels_large = {}
        category_labels_small = {}
        for i in labels_list_large:
            category_labels_large[i] = category_labels_large.get(i,0) + 1
        for i in labels_list_small:
            category_labels_small[i] = category_labels_small.get(i,0) + 1

        self.categoties_large = category_labels_large
        self.categoties_small = category_labels_small
        print('large categories:---------------------')
        for key,value in category_labels_large.items():
            print(key,value)

        print('small categories:---------------------')
        for key,value in category_labels_small.items():
            print(key,value)

    def get_tags(self):
        """
            This function returns a random event according totags
        """

        sql_command = """
                        SELECT tags
                        FROM Events
                    """

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()
        labels_list = []
        for i in query_result:
            list_each = re.split(';',i[0])
            labels_list += list_each
        number_labels = {}
        for i in labels_list:
            number_labels[i] = number_labels.get(i,0) + 1
        self.tags = number_labels
        for key,value in self.tags.items():
            print(key,value)
        return number_labels

        # event = {'event_id': query_result[0][0], 'title': query_result[0][1], 'category': query_result[0][2],
        #          'price': query_result[0][3], 'description': query_result[0][4], 'link': query_result[0][5],
        #          'telephone': query_result[0][6], 'tags': query_result[0][7], 'address_street': query_result[0][8],
        #          'address_city': query_result[0][9], 'address_zipcode': query_result[0][10],
        #          'date': query_result[0][11], 'date_end': query_result[0][12], 'contact_mail': query_result[0][13],
        #          'facebook': query_result[0][14], 'website': query_result[0][15], 'latitude': query_result[0][16],
        #          'longitude': query_result[0][17]}
        #
        # return event

    def return_several_events(self,number_of_events):
        events = []
        for i in range(number_of_events):
            events.append(self.return_event())

    def delete_Event_table(self):
        """
            Created for debuging
            Deletes the data in the user table!
        """

        sql_command = """
                        DELETE FROM Events;
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
                    DROP TABLE Events;
                """
        self.connection.execute(sql_command)

    def check_database(self):

        """
            Just checking the database!
            Returns everything in it
        """

        sql_command = """
                    SELECT *
                    FROM Events
                """
        self.controller.execute(sql_command)

        # for col in self.controller.fetchall():
        #     print("This row")
        #     for e in col:
        #         print(e)
        #     print()
        return self.controller.fetchall()

    def return_diff_cate_events(self):
        return

    def return_ten_diff_events(self):
        return self.check_database()[:10]


if __name__ == "__main__":

    Events = EventsDBManager()
    event = Events.return_event(1)# event is in type of dict of an event.

    # for key in event:
    #     print(key, event[key])
    # print(Events.check_database()[:2])
    # Events.return_random_events()
    # tags = Events.get_tags()
    cata = Events.get_catagories()
    # Events.delete_Event_table()
    # Events.drop_table()
    print(Events.return_event(2270))
