import sqlite3
import re
from random import choice

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

    def return_ten_diff_events(self): # return 10 different events, 2 events for each large category
        events_id = []
        cates = self.get_catagories() # dict. key: large categories, value: number of it

        sql_command = """
                        SELECT event_id, category
                        FROM Events
                    """

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()
        # print(query_result)
        cleaned_result = []
        for id,cate in query_result:
            match = re.match(r'(.*) -> (.*)',cate)
            large_cate = match.group(1)
            cleaned_result.append((id,large_cate))
        # print(cleaned_result)
        need = {}
        for cate in cates.keys():
            need[cate] = 2# to generate list of number of needed events
        # print(self.get_catagories())
        all_ids = self.all_id_of_events()
        while(len(events_id) < 10):
            rand_id = choice(all_ids)
            rand_id_cate = self.get_categoty(rand_id)
            if need[rand_id_cate] > 0:
                need[rand_id_cate] -= 1
                # events_id.append((rand_id,rand_id_cate)r)
                events_id.append(rand_id)
        events = []
        for i in events_id:
            events += self.return_event(i)
        return events

    def number_of_events(self):
        sql_command = """
                        SELECT COUNT(DISTINCT event_id)
                        FROM Events;
                    """

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()[0][0]
        # print('number of events:')
        # print(query_result)
        return query_result

    def all_id_of_events(self): # return a list of sorted ids by increase
        sql_command = """
                        SELECT DISTINCT event_id
                        FROM Events;
                    """

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()
        query_result = sorted(query_result)
        for i in range(len(query_result)):
            query_result[i] = query_result[i][0]
        # print('all ids:')
        # print(query_result)
        return query_result


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

        # print('large categories:---------------------')
        # for key,value in category_labels_large.items():
        #     print(key,value)
        #
        # print('small categories:---------------------')
        # for key,value in category_labels_small.items():
        #     print(key,value)

        return category_labels_large

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
        # for key,value in number_labels.items():
        #     print(key,value)
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

    def get_categoty(self,id):
        sql_command = """
                        SELECT category
                        FROM Events
                        WHERE event_id = {0}
                    """.format(id)

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()
        match = re.match(r'(.*) -> (.*)',query_result[0][0])
        large_category = match.group(1)
        return large_category

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


if __name__ == "__main__":

    Events = EventsDBManager()
    event = Events.return_event(1)# event is in type of dict of an event.

    # for key in event:
    #     print(key, event[key])
    # print(Events.check_database()[:2])
    # Events.return_random_events()
    # tags = Events.get_tags()
    # cata = Events.get_catagories()
    # Events.delete_Event_table()
    # Events.drop_table()
    # print(Events.check_database())
    # Events.return_ten_diff_events()
    # Events.number_of_events()
    # Events.all_id_of_events()
    # print(Events.get_categoty(2270))
    print(Events.return_ten_diff_events())
