#!/usr/bin/env python
# coding: utf-8

import json, collections
from http.client import HTTPSConnection
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import psycopg2
from configparser import ConfigParser
import json, tweepy, requests, sys, subprocess, os
import pandas as pd 
import environ
env = environ.Env()
environ.Env.read_env()


wordlist = []; hashlist = [];mentionlist=[];sentimentlist=[];entlist=[]

##Get tweets from DB
params = {"host":env("POSTGRES_HOST"), "database":env("POSTGRES_DATABASE"),"user": env("POSTGRES_USER"),"password":env("POSTGRES_PASSWORD")}
dbconn = psycopg2.connect(**params)
cur = dbconn.cursor()

query = 'SELECT \"TWITTER\".\"POST_LEMMATIZED\",\"TWITTER\".\"HASHTAGS\",\"TWITTER\".\"SENTIMENT_RESULT\",\"TWITTER\".\"MENTIONS_SCREEN_NAME\",\"TWITTER\".\"ENTITIES\" FROM \"STREAMED_DATA\".\"TWITTER\"'
print(query)
cur.execute(query)  
output = cur.fetchall()
dbconn.commit() 
cur.close()

for tweet in output:
    (lemma,tags,sentiment,mentions,entities) = tweet
    #tweetTexts.append(text)
    sentimentlist.append(sentiment)
    tl = lemma.split(' ')
    for w in tl: 
        if w not in ["not","can"]:
            wordlist.append(w.strip())
    
    try:
        t = tags.split('||')
        for i in t:
            hashlist.append(i.strip())
    except AttributeError:
        pass

    try:
        t = entities.split('||')
        for i in t:
            entlist.append(i.strip())
    except AttributeError:
        pass
    try:
        m = mentions.split('||')
        for j in m:
            mentionlist.append(j.strip())
    except AttributeError:
        pass

wrdCnt = dict(collections.Counter(wordlist))
sentCnt = dict(collections.Counter(sentimentlist))
mentCnt = dict(collections.Counter(mentionlist))
hashCnt = dict(collections.Counter(hashlist))
entCnt = dict(collections.Counter(entlist))


##PLOT
print("**********WORDS**********")
dfDict = {"topics":[],"count":[]}
for w in wrdCnt.keys():
    dfDict["topics"].append(w)
    dfDict["count"].append(wrdCnt[w])
wordDF = pd.DataFrame({"count":dfDict["count"]},index=dfDict["topics"])
wordDF.sort_values(by=["count"],ascending=False,inplace=True)
wordDF = wordDF.head(50)
print(wordDF.head(25))

wordDF.plot(kind="bar")
plt.xticks(rotation=70)
plt.xlabel("Words")
plt.ylabel("Occurances")

#SENTIMENTS
print("**********SENTIMENTS**********")
dfDict = {"topics":[],"count":[]}
for w in sentCnt.keys():
    dfDict["topics"].append(w)
    dfDict["count"].append(sentCnt[w])
sentDF = pd.DataFrame({"count":dfDict["count"]},index=dfDict["topics"])
sentDF.sort_values(by=["count"],ascending=False,inplace=True)
sentDF = sentDF.head(50)
print(sentDF.head(25))

sentDF.plot(kind="bar")
plt.xticks(rotation=70)
plt.xlabel("Sentiments")
plt.ylabel("Tweet Count")

#MENTIONS
print("**********MENTIONS**********")
##PLOT
dfDict = {"topics":[],"count":[]}
for w in mentCnt.keys():
    dfDict["topics"].append(w)
    dfDict["count"].append(mentCnt[w])
mentDF = pd.DataFrame({"count":dfDict["count"]},index=dfDict["topics"])
mentDF.sort_values(by=["count"],ascending=False,inplace=True)
mentDF = mentDF.head(50)
print(mentDF.head(25))

mentDF.plot(kind="bar")
plt.xticks(rotation=70)
plt.xlabel("Mentions")
plt.ylabel("Tweet Count")

#ENTITIES
print("**********ENTITIES**********")
dfDict = {"topics":[],"count":[]}
for w in entCnt.keys():
    dfDict["topics"].append(w)
    dfDict["count"].append(entCnt[w])
entDF = pd.DataFrame({"count":dfDict["count"]},index=dfDict["topics"])
entDF.sort_values(by=["count"],ascending=False,inplace=True)
entDF = entDF.head(50)
print(entDF.head(20))

entDF.plot(kind="bar")
plt.xticks(rotation=70)
plt.xlabel("Entities")
plt.ylabel("Occurances")

#HASTAGS
print("**********HASHTAGS**********")
dfDict = {"topics":[],"count":[]}
for w in hashCnt.keys():
    dfDict["topics"].append(w)
    dfDict["count"].append(hashCnt[w])
hashDF = pd.DataFrame({"count":dfDict["count"]},index=dfDict["topics"])
hashDF.sort_values(by=["count"],ascending=False,inplace=True)
hashDF = hashDF.head(50)
print(hashDF.head(20))

hashDF.plot(kind="bar")
plt.xticks(rotation=70)
plt.xlabel("Hashtags")
plt.ylabel("Occurances")
plt.show()
