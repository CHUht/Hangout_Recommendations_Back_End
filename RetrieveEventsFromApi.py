from urllib import request
from geopy.geocoders import Nominatim
import json
from EventDBManagement import EventsDBManager
import re


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def get_data_from_API(url):
    with request.urlopen(url) as f:
        data = f.read()
        print('Status:', f.status, f.reason)
        # for k, v in f.getheaders():
        #     print('%s: %s' % (k, v))
        data_decoded = data.decode('utf-8')
        print('Data:',data_decoded)
    return data_decoded


def get_data_from_API_with_head(url):
    req = request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0')
    with request.urlopen(req) as f:
        #print('Status:', f.status, f.reason)
        # for k, v in f.getheaders():
        #     print('%s: %s' % (k, v))
        data_decode = f.read().decode('utf-8')
        data_decode = json.loads(data_decode)
        #print(type(data_decode), data_decode)
    print('data_gained')
    return data_decode


def data_clean(raw_data):
    events = raw_data['records']

    for event in events:

        cleaned_event = {}
        label_list = [('event_id','id'),('title','title'),('category','category'),('price','price_detail'),
                      ('description','description'),('link','access_link'),('telephone','contact_phone'),
                      ('tags', 'tags'), ('address_street','address_street'), ('address_city','address_city'),
                      ('address_zipcode','address_zipcode'),('date','date_description'),('date_end','date_end'),
                      ('contact_mail','contact_mail'),('facebook','contact_facebook'),('website','contact_url')]

        for a,b in label_list:
            try:
                cleaned_event[a] = cleanhtml(event['fields'][b])
            except KeyError:
                cleaned_event[a] = "NULL"

        try:
            location = geolocator.geocode(cleaned_event['address_street'] + "," + cleaned_event['address_city'])
        except:
            location = None

        if location is not None:
            cleaned_event['latitude'] = location.latitude
            cleaned_event['longitude'] = location.longitude
        else:
            cleaned_event['latitude'] = "NULL"
            cleaned_event['longitude'] = "NULL"


        if (cleaned_event['event_id'] not in str(Events.events_ids)) \
                and (cleaned_event['date'] != "NULL") and (cleaned_event['date_end'] != "NULL"):

            Events.add_event(cleaned_event['event_id'], cleaned_event['title'], cleaned_event['category'],
                             cleaned_event['price'], cleaned_event['description'], cleaned_event['link'],
                             cleaned_event['telephone'], cleaned_event['tags'], cleaned_event['address_street'],
                             cleaned_event['address_city'], cleaned_event['address_zipcode'], cleaned_event['date'],
                             cleaned_event['date_end'], cleaned_event['contact_mail'], cleaned_event['facebook'],
                             cleaned_event['website'], cleaned_event['latitude'], cleaned_event['longitude'])
        print('cleaning')



if __name__ == "__main__":

    geolocator = Nominatim(user_agent="Hangout Recommendation")
    Events = EventsDBManager()


    url = 'https://opendata.paris.fr/api/records/1.0/search/?dataset=que-faire-a-paris-&rows=10000&facet=category&facet=tags&facet=address_zipcode&facet=address_city&facet=pmr&facet=blind&facet=deaf&facet=access_type&facet=price_type'
    data = get_data_from_API_with_head(url)
    data_clean(data)

    Events.check_database()
