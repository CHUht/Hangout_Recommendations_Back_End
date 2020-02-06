import pandas as pd
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import nltk
from gensim import corpora, models, similarities
import gensim
import numpy as np
import matplotlib.pyplot as plt

movies = pd.read_csv("wiki_movie_plots_deduped.csv")


"""
# Lopping through the features
for feature in movies:
    print(feature)
"""

# Removing names from plot data
def get_human_names(text):
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
# Lopping through the rows 
for row in movies.iterrows():
    print(row)
"""

"""
# Dataset!
print(movies)
"""

stop_words = list(stopwords.words('english'))

tokenizer = RegexpTokenizer(r'\w+')
texts = []
for i in range(len(movies)):

    if i >= 100 :
        break

    get_human_names(movies.loc[i,'Plot'])

    moviePlot = movies.loc[i,'Plot']
    moviePlot = tokenizer.tokenize(moviePlot)
    moviePlot = [x.lower() for x in moviePlot]
    moviePlot = [x for x in moviePlot if not x in stop_words]
    texts.append(moviePlot)

dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=30)
index = similarities.MatrixSimilarity(lsi[corpus_tfidf])

total_sims = [] # storage of all similarity vectors to analysis
for i, doc in enumerate(corpus_tfidf):
    vec_lsi = lsi[doc] # convert the vector to LSI space
    sims = index[vec_lsi] # perform a similarity vector against the corpus

    total_sims.append(sims)


total_sims = np.asarray(total_sims)
print(total_sims.shape)




