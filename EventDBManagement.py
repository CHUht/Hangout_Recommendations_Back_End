import sqlite3
import re
from random import choice
from time import *
import datetime
from BackendAPIStaticList import *
from threading import Lock

@singleton
class EventsDBManager:

    def dbconnect(self):
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
        self.controller = self.connection.cursor()

    def dbdeconnect(self):
        self.connection.close()

    def __init__(self):
        """
            Here we start all the points necessary to start this class
            We need to connect to the database
            and get the last id!
        """
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

        self.dbconnect()
        values = (event_id, title, category, price, description,
                  link, telephone, tags, address_street, address_city,
                  address_zipcode, date, date_end, contact_mail, facebook, website,
                  cover_url, latitude, longitude, occurrences,large_category,small_category)

        self.controller.execute(sql_command, values)
        self.connection.commit()
        self.dbdeconnect()

    def remove_event(self, event_id):

        """
            This function removes an event rating made by the user to the database
        """

        sql_command = """
                       DELETE FROM Events
                       WHERE Events.event_id = '{0}'
                    """.format(event_id)

        self.dbconnect()
        self.controller.execute(sql_command)
        self.connection.commit()
        self.dbdeconnect()

    def retrieve_event_ids(self):
        """
        this function returns a list of all ids sorted by increase
        """
        sql_command = """
                        SELECT DISTINCT event_id
                        FROM Events;
                    """

        self.dbconnect()
        self.controller.execute(sql_command)
        all_ids = self.controller.fetchall().copy()
        all_ids = sorted(all_ids)
        for i in range(len(all_ids)):
            all_ids[i] = all_ids[i][0]
        self.dbdeconnect()
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

        self.dbconnect()
        self.controller.execute(sql_command)
        query_result = self.controller.fetchall().copy()
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
        self.dbdeconnect()

        return event

    def return_several_diff_events(self,number_of_events = 10):
        """
            This function returns several different events, at least 2 events for each large category

        """
        self.dbconnect()
        if number_of_events < 10 or type(number_of_events) != int or number_of_events > 100:
            raise IndexError('number of events should >= 10, and  number of event should be small')
        events_id = []
        cates = self.get_catagories_statistics() # dict. key: large categories, value: number of it

        sql_command = """
                        SELECT event_id, large_category
                        FROM Events
                    """

        self.controller.execute(sql_command)
        query_result = self.controller.fetchall().copy()
        # print(query_result)
        self.dbdeconnect()
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
        if  type(cate_type) != int or cate_type <= 0 or number_of_events > 30:
            raise IndexError('number of events should be a positive integer,and  number of event should be small')
        cates = self.get_catagories_statistics() # dict. key: large categories, value: number of it

        self.dbconnect()
        sql_command = """
                        SELECT event_id
                        FROM Events
                        WHERE large_category = '{0}';
                    """.format(cate_map[cate_type])

        self.controller.execute(sql_command)
        ids_of_this_cate = self.controller.fetchall().copy()
        for i in range(len(ids_of_this_cate)):
            ids_of_this_cate[i] = ids_of_this_cate[i][0]
        # print(query_result)
        self.dbdeconnect()
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

        self.dbconnect()
        self.controller.execute(sql_command)
        query_result = self.controller.fetchall().copy()
        if len(query_result) == 0:
            raise ValueError('illegal input id')
        query_result = query_result[0]
        self.dbdeconnect()
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
                if int(hour) < 0:
                    if int(date_start[-2:]) == 0:
                        date_start = date_start[:-5] + str(int(date_start[-5:-3])-1).zfill(2) + date_start[-3:-2] + \
                                     str(int(date_start[-2:])-1).zfill(2)
                    hour = str(int(hour) + 24)
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
            whatday= datetime.datetime.strptime(nearest,'%Y-%m-%d %H:%M:%S').strftime("%w")
            whatday =jour_semaine[whatday]
            nearest = nearest[:-3]
            nearest += (' '+ whatday)
        else:
            nearest = "ce n'est pas no plus accesible"
        # print(nearest)
        event_to_return = self.return_event_no_nearest(query_result[0])
        event_to_return['nearest'] = nearest
        # print(event_to_return['nearest'])

        occu_dict = {}
        for start_time,end_time in occurrences_cleaned:
            date_occurrence = start_time[:10]
            occu_dict.setdefault(date_occurrence, []).append((start_time,end_time))
        event_to_return['occurrences'] = occu_dict
        return event_to_return

    def search_key_words(self,keywords):
        """
        this function returns a list of events of given keywords
        :param keywords: str
        :return: dict
        """
        keywords = str(keywords)
        keywords = re.split(r'\s*(?:;|,|\s)\s*',keywords)
        all_events = self.check_database()
        return_list_id = []
        return_list = []
        for event in all_events:
            whole = ''
            flag = True
            for value in event:
                whole += (str(value) + ' ')
            for keyword in keywords:
                matc = re.search(str(keyword),str(whole))
                if matc == None:
                    flag = False
                    break
            if flag:
                return_list_id.append(event[0])

        return_list = []
        # print(events_id)
        for i in return_list_id:
            event_raw = self.get_event_with_nearest(i)
            event = {}
            attr_list = ['event_id', 'title', 'address_street', 'address_city',
                  'cover_url','large_category','nearest']
            for key,value in event_raw.items():
                if key in attr_list:
                    event[key] = value
            return_list.append(event)
        return return_list

    def number_of_events(self):
        """
            This function returns the total number of events
        """
        all_ids = self.retrieve_event_ids()
        return len(all_ids)

    def all_events_of_cates(self,cate_type):
        """
            This function returns all events of a specified larde category
        """
        if cate_type not in range(1,50):
            raise IndexError('input should be integer from 1 to 49')
        return self.search_key_words(cate_map[cate_type])

    def get_no_label_statistics(self):
        all = self.check_database()
        label_list = ['event_id', 'title', 'category', 'price', 'description',
                          'link', 'telephone', 'tags', 'address_street', 'address_city',
                          'address_zipcode', 'date', 'date_end', 'contact_mail', 'facebook', 'website',
                          'cover_url', 'latitude', 'longitude','occurrences','large_category','small_category']
        dict = {}
        for event in all:
            for i in range(len(event)):
                if event[i] == "NULL":
                    dict[label_list[i]] = dict.get(label_list[i],0) + 1
        return dict


    def get_catagories_statistics(self):
        """
            This function returns a large category statistics in tuple and print
        """
        sql_command = """
                        SELECT large_category,small_category
                        FROM Events
                    """

        self.dbconnect()
        self.controller.execute(sql_command)
        query_result = self.controller.fetchall().copy()
        category_labels_large = {}
        category_labels_small = {}
        for i in query_result:
            category_labels_large[i[0]] = category_labels_large.get(i[0],0) + 1
            category_labels_small[i[1]] = category_labels_small.get(i[1],0) + 1
        self.dbdeconnect()

        # print('large categories:---------------------')
        # for key,value in category_labels_large.items():
        #     print(key,value)
        #
        # number_of_small_cates = 0
        # print('small categories:---------------------')
        # for key,value in category_labels_small.items():
        #     print(key,value)
        # print(number_of_small_cates)
        return category_labels_large

    def get_tags_statistics(self):
        """
            This function returns tags statistics in dict and print
        """

        sql_command = """
                        SELECT tags
                        FROM Events
                    """

        self.dbconnect()
        self.controller.execute(sql_command)
        query_result = self.controller.fetchall().copy()
        labels_list = []
        for i in query_result:
            list_each = re.split(';',i[0])
            labels_list += list_each
        number_labels = {}
        for i in labels_list:
            number_labels[i] = number_labels.get(i,0) + 1
        # for key,value in number_labels.items():
        #     print(key,value)
        number_labels.pop('NULL')
        number_labels.pop('English')
        self.dbdeconnect()
        return list(number_labels.keys())

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

        self.dbconnect()
        self.controller.execute(sql_command)
        large_category = self.controller.fetchall().copy()[0][0]
        self.dbdeconnect()
        return large_category

    def return_several_events_by_ids(self,list_of_ids:str):
        for single_id in list_of_ids:
            if type(single_id) != int:
                raise ValueError('illegal input, not integer')
        events = []
        for single_id in list_of_ids:
            events.append(self.get_event_with_nearest(single_id))
        return events

    def delete_Event_table(self):
        """
            Created for debuging
            Deletes the data in the user table!
        """

        self.dbconnect()
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
        self.dbdeconnect()

    def drop_table(self):
        """
            Created for debuging
            Drops the table!
        """

        self.dbconnect()
        sql_command = """
                    DROP TABLE Events;
                """
        self.connection.execute(sql_command)
        self.dbdeconnect()

    def return_all_events(self):
        """
            Returns the whole database
            This is done to get the recommendations from the user
        """
        self.dbconnect()
        sql_command = """
                        SELECT *
                        FROM Events
                    """
        self.controller.execute(sql_command)
        events = self.controller.fetchall().copy()
        self.dbdeconnect()

        return events

    def return_all_events_date_location(self):

        """
            Returns all the events location and stored date
            This is done for the filtering in the recommendation setting
        """
        sql_command = """
                        SELECT event_id, date_end, latitude, longitude
                        FROM Events
                    """

        self.dbconnect()
        self.controller.execute(sql_command)
        events = self.controller.fetchall().copy()
        self.dbdeconnect()

        return events

    def check_database(self):

        """
            Just checking the database!
            Returns everything in it
        """

        sql_command = """
                    SELECT *
                    FROM Events
                """
        self.dbconnect()
        self.controller.execute(sql_command)

        # for col in self.controller.fetchall():
        #     print("This row")
        #     for e in col:
        #         print(e)
        #     print()
        toreturn = self.controller.fetchall().copy()
        self.dbdeconnect()
        return toreturn

if __name__ == "__main__":

    eventsDBManager = EventsDBManager()
    # event = eventsDBManager.return_event_no_nearest(2270)# event is in type of dict of an event.
    # print(event)
    # print(eventsDBManager.check_database()[:2])
    # print(eventsDBManager.get_tags_statistics())
    cata = eventsDBManager.get_catagories_statistics()
    print(cata)
    # eventsDBManager.delete_Event_table()
    # eventsDBManager.drop_table()
    # print(eventsDBManager.check_database())
    # print(eventsDBManager.number_of_events())
    # print(eventsDBManager.get_large_categoty(2270))
    diff_events = eventsDBManager.return_several_events_of_a_cate(1)
    print(len(diff_events))
    # print(eventsDBManager.get_event_with_nearest(99746))
    # print(eventsDBManager.return_several_events_of_a_cate(2))
    # result = eventsDBManager.search_key_words('Mange')
    # print(len(result),result)
    # print(len(eventsDBManager.all_events_of_lagrg_cates(1)))
    # dict = eventsDBManager.get_no_label_statistics()
    # for key,value in dict.items():
    #     print(key,value)
