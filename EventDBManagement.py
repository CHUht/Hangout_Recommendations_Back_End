import sqlite3
import re
from random import choice
from time import *
import datetime
from BackendAPIStaticList import *

@singleton
class EventsDBManager:
    def __init__(self):
        """
            Here we start all the points necessary to start this class
            We need to connect to the database
            and get the last id!
        """
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
        self.controller = self.connection.cursor()
        self.events_ids = self.retrieve_event_ids()

    def add_event(self, event_id, title, category, price, description,
                  link, telephone, tags, address_street, address_city,
                  address_zipcode, date, date_end, contact_mail, facebook, website,
                  cover_url, latitude, longitude,occurrences,large_category,small_category):

        """
            This function adds a event to the event database
        """

        sql_command = """
                    INSERT INTO Events (event_id, title, category, price, description, 
                  link, telephone, tags, address_street, address_city, 
                  address_zipcode, date, date_end, contact_mail, facebook, website,
                  cover_url, latitude, longitude,occurrences,large_category,small_category)
                    VALUES( ? , ?, ?, ?, ?, 
                  ? , ?, ?, ?, ?, 
                  ?, ?, ?, ?, ?, ?,
                  ?, ?, ?, ?, ?, ?);
                """
        values = (event_id, title, category, price, description,
                  link, telephone, tags, address_street, address_city,
                  address_zipcode, date, date_end, contact_mail, facebook, website,
                  cover_url, latitude, longitude, occurrences,large_category,small_category)

        self.controller.execute(sql_command, values)
        self.connection.commit()

    def remove_event(self, event_id):

        """
            This function removes an event rating made by the user to the database
        """

        sql_command = """
                       DELETE FROM Events
                       WHERE Events.event_id = '{0}'
                    """.format(event_id)

        self.controller.execute(sql_command)
        self.connection.commit()

    def retrieve_event_ids(self):
        """
        this function returns a list of all ids sorted by increase
        """
        sql_command = """
                        SELECT DISTINCT event_id
                        FROM Events;
                    """

        self.controller.execute(sql_command)
        all_ids = self.controller.fetchall()
        all_ids = sorted(all_ids)
        for i in range(len(all_ids)):
            all_ids[i] = all_ids[i][0]
        return all_ids

    def return_event_no_nearest(self, event_id):

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
                 'latitude': query_result[0][17], 'longitude': query_result[0][18], 'occurrences':query_result[0][19],
                 'large_category':query_result[0][20],'small_category':query_result[0][21]}

        return event

    def return_several_diff_events(self,number_of_events = 10):
        """
            This function returns several different events, at least 2 events for each large category

        """
        if number_of_events < 10 or type(number_of_events) != int:
            raise IndexError('number of events should >= 10')
        events_id = []
        cates = self.get_catagories_statistics() # dict. key: large categories, value: number of it

        sql_command = """
                        SELECT event_id, large_category
                        FROM Events
                    """

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()
        # print(query_result)
        cleaned_result = []
        for id,large_cate in query_result:
            cleaned_result.append((id,large_cate))
        # print(cleaned_result)
        need = {}
        for cate in cates.keys():
            need[cate] = 2 # to generate list of number of needed events
        # print(self.get_catagories_statistics())
        all_ids = self.retrieve_event_ids()
        while(len(events_id) < 10):
            rand_id = choice(all_ids)
            rand_id_cate = self.get_large_categoty(rand_id)
            if need[rand_id_cate] > 0 and (rand_id not in events_id):
                need[rand_id_cate] -= 1
                # events_id.append((rand_id,rand_id_cate)r)
                events_id.append(rand_id)
        while(len(events_id) < number_of_events):
            rand_id = choice(all_ids)
            if rand_id not in events_id:
                # events_id.append((rand_id,rand_id_cate)r)
                events_id.append(rand_id)

        events = []
        # print(events_id)
        for i in events_id:
            event_raw = self.get_event_with_nearest(i)
            event = {}
            attr_list = ['event_id', 'title', 'address_street', 'address_city',
                  'cover_url','large_category','nearest']
            for key,value in event_raw.items():
                if key in attr_list:
                    event[key] = value
            events.append(event)
        return events

    def return_several_events_of_a_cate(self, cate_type, number_of_events = 10):
        """
            This function returns several different events, at least 2 events for each large category

        """
        if  type(cate_type) != int or cate_type <= 0:
            raise IndexError('number of events should be a positive integer')
        cates = self.get_catagories_statistics() # dict. key: large categories, value: number of it

        sql_command = """
                        SELECT event_id
                        FROM Events
                        WHERE large_category = '{0}';
                    """.format(cate_map[cate_type])

        self.controller.execute(sql_command)
        ids_of_this_cate = self.controller.fetchall()
        for i in range(len(ids_of_this_cate)):
            ids_of_this_cate[i] = ids_of_this_cate[i][0]
        # print(query_result)
        events_id = []
        while(len(events_id) < number_of_events):
            rand_id = choice(ids_of_this_cate)
            if rand_id not in events_id:
                events_id.append(rand_id)

        events = []
        # print(events_id)
        for i in events_id:
            event_raw = self.get_event_with_nearest(i)
            event = {}
            attr_list = ['event_id', 'title', 'address_street', 'address_city',
                  'cover_url','large_category','nearest']
            for key,value in event_raw.items():
                if key in attr_list:
                    event[key] = value
            events.append(event)
        return events

    def get_event_with_nearest(self, id):
        """
        this function returns an event dict with the nearest occurence
        :param id: int
        :return: dict
        """
        sql_command = """
                        SELECT event_id, occurrences
                        FROM Events
                        WHERE event_id = {0};
                    """.format(id)

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()[0]
        now = strftime("%Y-%m-%dT%H:%M:%S", localtime())
        # print(query_result)
        pattern = re.compile('(20.*?)_(20.*?);')
        occurrences = re.findall(pattern, query_result[1])
        occurrences_cleaned = []
        for i in range(len(occurrences)):
            period = []
            for j in range(2):
                splited = re.match('(.*?)T(.*?):(.*?):(.*?)\+(.*):00',occurrences[i][j])
                date_start = splited.group(1)
                hour = splited.group(2)
                minute = splited.group(3)
                second = splited.group(4)
                diff = splited.group(5)
                hour = str(int(hour) - int(diff))
                time = (date_start+' '+hour+':'+ minute+':'+second)
                period.append(time)
            occurrences_cleaned.append(period)
        # print(occurrences_cleaned)
        # print(now)
        nearest = None
        for period in occurrences_cleaned:
            if period[0] > now:
                nearest = period[0]
                break

        if nearest != None:
            # print(nearest,query_result[0])
            if nearest[11] == '-':
                nearest = nearest[:11]+nearest[12:]
            whatday= datetime.datetime.strptime(nearest,'%Y-%m-%d %H:%M:%S').strftime("%w")
            whatday =jour_semaine[whatday]
            nearest += (' '+ whatday)
        else:
            nearest = "ce n'est pas no plus accesible"
        # print(nearest)
        event_to_return = self.return_event_no_nearest(query_result[0])
        event_to_return['nearest'] = nearest
        # print(event_to_return['nearest'])
        return event_to_return

    def number_of_events(self):
        """
        this function retuens the total number of events
        """
        all_ids = self.retrieve_event_ids()
        return len(all_ids)


    def return_events_by_category(self,number:int):
        """
            This function returns in json format the event information based on the event id!
        """

        if number not in [1,2,3,4,5]:
            raise IndexError('input should be 1,2,3,4,5')
        all_ids = self.retrieve_event_ids()
        while True:
            id_random = choice(all_ids)
            event = self.return_event_no_nearest(id_random)
            if event['large_category'] == cate_map[number]:
                return event


    def get_catagories_statistics(self):
        """
            This function returns a large category statistics in tuple and print
        """
        sql_command = """
                        SELECT large_category,small_category
                        FROM Events
                    """

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall()
        print(query_result)
        category_labels_large = {}
        category_labels_small = {}
        for i in query_result:
            category_labels_large[i[0]] = category_labels_large.get(i[0],0) + 1
            category_labels_small[i[1]] = category_labels_small.get(i[1],0) + 1

        # print('large categories:---------------------')
        # for key,value in category_labels_large.items():
        #     print(key,value)
        #
        # print('small categories:---------------------')
        # for key,value in category_labels_small.items():
        #     print(key,value)

        return category_labels_large

    def get_tags_statistics(self):
        """
            This function returns tags statistics in dict and print
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

    def get_large_categoty(self, id):
        """
        this funciton returns the large category of a given id
        :param id:
        :return:
        """
        sql_command = """
                        SELECT large_category
                        FROM Events
                        WHERE event_id = {0}
                    """.format(id)

        self.controller.execute(sql_command)
        large_category = self.controller.fetchall()[0][0]
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

    eventsDBManager = EventsDBManager()
    # event = eventsDBManager.return_event_no_nearest(1)# event is in type of dict of an event.
    # print(event)
    # print(eventsDBManager.check_database()[:2])
    # eventsDBManager.return_random_events()
    # print(eventsDBManager.get_tags_statistics())
    # cata = eventsDBManager.get_catagories_statistics()
    # eventsDBManager.delete_Event_table()
    # eventsDBManager.drop_table()
    # print(eventsDBManager.check_database())
    # eventsDBManager.return_ten_diff_events()
    # print(eventsDBManager.number_of_events())
    # eventsDBManager.all_ids_of_events()
    # print(eventsDBManager.get_large_categoty(2270))
    diff_events = eventsDBManager.return_several_events_of_a_cate(1)
    print(len(diff_events))
    for i in diff_events:
        print(i)
    # print(eventsDBManager.get_event_with_nearest(99812))
    # print(eventsDBManager.return_events_by_category(2))
