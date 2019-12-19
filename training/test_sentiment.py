## test.python: try to figure out what the hell the
# "nlp_sentiment.py" does...

import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup
import requests
import os
import pickle
import statistics
import re
import numpy as np
import time
import schedule
from nltk.corpus import stopwords
import random
import wrds
from textblob import TextBlob
import pandas_datareader.data as web
from collections import Counter
import asyncio, concurrent.futures
from sklearn import svm, neighbors #cross_validation (didn't find)
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
#import matplotlib.pyplot as plt
from nltk.tokenize import sent_tokenize, word_tokenize
from matplotlib import style

import pickle as pkl


'''
    1. get an rss feed associated with each stock name.
    2. all the links we find in the rss feed are articles. Get the articles?
'''

#### rss_feed(ticker)
ticker = 'aramco'
ticker = ticker.lower()

#--------------------------------------------------------#
# Part A: Run the below code just once, store results.
#--------------------------------------------------------#

def collect_rss_data():
    #1. collect all the rss feeds.
    resp = requests.get("https://www.cnbc.com/rss-feeds/")
    soup = BeautifulSoup(resp.content, "lxml")
    div = soup.find("div", attrs={"class" :  "wildcard"})
    links = []
    total_items = []
    i = div.find_all("a")
    #print (i[0].attrs["href"])
    for k in i:
        links.append(k.attrs["href"])

    #2. Crawl each rss feed and collect all articles.
    for link in links:
        print ("https:"+link) #prints the rss feed link.

        test = requests.get("https:"+link)
        test_soup = BeautifulSoup(test.content,"lxml")
        #item is for each RSS link.
        items = test_soup.findAll("item")
        total_items.append(items)
    #print(total_items[:5])

### {MAYBE I SHOULD USE THIS FOR THE PICKLE ("total_items")}

    #3. Create a list of all titles & descriptions. (this is all that's used for sentiment analysis.)
    dictionaries = []

    for i in range(0,len(total_items)):
        #print (total_items[i])
        for j in range(0, len(total_items[i])):
            #print (total_items[i][j].title.text)
            dictionary = {}
            try:
                dictionary["title"] = total_items[i][j].title.text.lower()
                dictionary["description"] = total_items[i][j].description.text.lower()
            except Exception as e:
                print(type(e))
                print(e)

            #print (dictionary)
            dictionaries.append(dictionary)


    #3.5: save the variable "dictionaries" as a pickle.
    rsfile = './rss_feed_articles.pickle'
    with open('./rss_feed_articles.pickle','wb') as f:
        pkl.dump(dictionaries, f)

    #test:
    '''
    print("test: printing out part of the picke stored data...")
    with open('./rss_feed_articles.pickle', 'rb') as f:
        data = pkl.load(f)
        print(data[:4])
    '''

    return rsfile


#--------------------------------------------------------#
# End part A.
#--------------------------------------------------------#
# Part B: actually do the sentiment analysis.
#--------------------------------------------------------#

'''here, we take the "dictionaries" and actually do the sentiment analysis.'''
def sentiment_analysis(dict_pk_file):
    value = 0
    negative = 0
    positive = 0
    negative_list = []
    positive_list = []
    #print (dictionaries[0]["title"])
    for dic in dictionaries:
        #print (dic["title"])
        if ticker in dic["title"]:


            result = sentiment(dic["title"])
            #print (sentiment(dic["title"]))
            #print (asyncio.async(sentiment(dic["title"])))
            #print ("h",reult)
            negative += result[0]
            positive += result[1]

            negative_list.append(result[2])
            positive_list.append(result[3])
            #time.sleep(8)


    if positive > negative:
        #print (positive)
        value = 1
    elif positive == negative:
        value = 0
    else:
        #print (negative)
        value =-1
    #print (negative_list)
    #print (positive_list)
    return value


#main:

#1. recollect all data if need be:
rsfilename = collect_rss_data()
#classication = sentiment_analysis(rsfilename)






#I wonder if looking at the actual article will improve the sentiment analysis results?

'''
    next steps:
        1. measure the performance of the current code somehow.
            ~ Does the code take into account the date of the article at all?
            ~ is there any way I can crawl historical data for testing purposes?
            - may need to crawl stock price movements
                (or track them every day...)

            #building a dataset - ideas:
                - track stocks & articles every day for a few months.
                - try to get data for as many tickers as possible and train / test on that.
                - waybackpack: https://github.com/jsvine/waybackpack/blob/master/README.md
                    ~ might allow you to get archived data from the rss feed.
                -

        2. try to add some more NLP and see what methods improve the performance.
            ~ Shouldn't we crawl more sources of data? Maybe it's better once you aggregate all
                the data sources.



    building out the dataset:
        - keep refining the dataset process:
            - one way is to query the "wayback machine" directly:
            resp = requests.get("https://web.archive.org/web/20190513203949/https://www.cnbc.com/id/100003114/device/rss/rss.html")
            == this think has a lot more data!
            == maybe I should just "manually" crawl these links rather than relying on the library...

        - use "waybackpack" library to crawl a bunch of the historical rss feed links.
        ~ see: https://github.com/jsvine/waybackpack/blob/master/README.md
        - store the results as a "database" of rss feeds.

        - use a bunch of stock tickers, and crawl all the links and descriptions
            present within that database to create a "data point"
            ~ one data point per day per ticker.
        -
'''
