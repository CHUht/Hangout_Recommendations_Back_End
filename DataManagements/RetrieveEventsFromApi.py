from urllib import request
from geopy.geocoders import Nominatim
import json
from EventDBManagement import EventsDBManager
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from gensim import corpora, models, similarities
import gensim
import re
import numpy as np
import pickle as pkl


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


def data_clean(raw_data,Events,geolocator):
    events = raw_data['records']
    no_label_numbers = {}
    tag_numbers = {}
    i =0
    for event in events:

        cleaned_event = {}
        label_list = [('event_id','id'),('title','title'),('category','category'),('price','price_detail'),
                      ('description','description'),('link','access_link'),('telephone','contact_phone'),
                      ('tags', 'tags'), ('address_street','address_street'), ('address_city','address_city'),
                      ('address_zipcode','address_zipcode'),('date','date_description'),('date_end','date_end'),
                      ('contact_mail','contact_mail'),('facebook','contact_facebook'),('website','contact_url'),
                      ('cover_url','cover_url'),('occurrences','occurrences')]

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

        # occurrence clean
        cleaned_event['occurrences'] += ';'

        #category clean
        match = re.match(r'(.*) -> (.*)',cleaned_event['category'])
        cleaned_event['large_category'] = match.group(1)
        cleaned_event['small_category'] = match.group(2)


        if (cleaned_event['event_id'] not in str(Events.events_ids)) \
                and (cleaned_event['date'] != "NULL") and (cleaned_event['date_end'] != "NULL"):

            Events.add_event(cleaned_event['event_id'], cleaned_event['title'], cleaned_event['category'],
                             cleaned_event['price'], cleaned_event['description'], cleaned_event['link'],
                             cleaned_event['telephone'], cleaned_event['tags'], cleaned_event['address_street'],
                             cleaned_event['address_city'], cleaned_event['address_zipcode'], cleaned_event['date'],
                             cleaned_event['date_end'], cleaned_event['contact_mail'], cleaned_event['facebook'],
                             cleaned_event['website'], cleaned_event['cover_url'], cleaned_event['latitude'],
                             cleaned_event['longitude'],cleaned_event['occurrences'],cleaned_event['large_category'],
                             cleaned_event['small_category'])
            # print('cleaning ' + cleaned_event['event_id'] + ' not exists')
        i += 1
        print(i)


def generate_similarity_matrix(Events):

    """
        Start by retrieving all events from the database
    """
    events = Events.return_all_events()
    events = [(event[0], event[4]) for event in events]

    """
        The event id is different from the position of the event on the similarity matrix
        So we must create a hash relation to translate between indices
    """
    id_to_index = {}
    index_to_id = {}
    for i,event in enumerate(events):
        id_to_index[event[0]] = i
        index_to_id[i] = event[0]



    """
        Declare the events as a pandas dataframe
    """

    def get_human_names(text):
        """
        :param text: receives a text
        :return: get's human names from that text so we can remove them
        """
        tokens = nltk.tokenize.word_tokenize(text)
        pos = nltk.pos_tag(tokens)
        sentt = nltk.ne_chunk(pos, binary=False)
        for word in sentt:
            try:
                if word.label() == "PERSON" and word[0][0].lower() not in stop_words:
                    stop_words.append(word[0][0].lower())
            except AttributeError:
                pass

    """
        List of stop words in french
        they must be removed for the NLP 
        and the tokenizer to keep only the useful letters and numbers 
    """
    stop_words = list(stopwords.words('french'))
    tokenizer = RegexpTokenizer(r'\w+')

    """
        Here we tokenize the events remove the names and create the texts structure
        The texts will be used to process the similarities between the rated events and all events!
    """
    texts = []
    for i,event in enumerate(events):
        get_human_names(event[1])
        event_des = event[1]
        event_des = tokenizer.tokenize(event_des)
        event_des = [x.lower() for x in event_des]
        event_des = [x for x in event_des if not x in stop_words]
        texts.append(event_des)
    """
        Create the dictionary with all the words on the events
        And the corpus (number of features of each document!)
    """
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    """
        Apply the tfidf model to the corpus
        And them apply it to the feature map
    """
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    # Use feature reduction by applying the lsi model
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=50)
    index = similarities.MatrixSimilarity(lsi[corpus_tfidf])

    """
        Here we finally process the similarities between the events
        The similarity is a measurement of how close the description of the events are!
        If they are exactly equal the similarity is one
    """
    total_sims = []  # storage of all similarity vectors to analysis
    for i, doc in enumerate(corpus_tfidf):
        vec_lsi = lsi[doc]  # convert the vector to LSI space
        sims = index[vec_lsi]  # perform a similarity vector against the corpus

        total_sims.append(sims)
    total_sims = np.asarray(total_sims)

    similarity_matrix = {}
    similarity_matrix["index_to_id"] = index_to_id
    similarity_matrix["id_to_index"] = id_to_index
    similarity_matrix["similarities"] = total_sims

    pkl.dump(similarity_matrix, open("similarities.pkl", "wb"))

    exit()

def download_and_clean():

    geolocator = Nominatim(user_agent="Hangout Recommendation")
    Events = EventsDBManager()

    url = 'https://opendata.paris.fr/api/records/1.0/search/?dataset=que-faire-a-paris-&rows=10000&facet=category&facet=tags&facet=address_zipcode&facet=address_city&facet=pmr&facet=blind&facet=deaf&facet=access_type&facet=price_type'
    data = get_data_from_API_with_head(url)
    data_clean(data,Events,geolocator)
    # print(Events.get_tags_statistics())

    # Events.check_database()
    generate_similarity_matrix(Events)

if __name__ == "__main__":
    # download_and_clean()
    Events = EventsDBManager()
    download_and_clean()