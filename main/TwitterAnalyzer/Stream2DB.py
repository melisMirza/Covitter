import psycopg2
from configparser import ConfigParser
import json, tweepy, requests, sys, subprocess, os
import pandas as pd 
from tweepy import StreamListener
from tweepy import Stream
import string, nltk,re, emot,tagme
from nltk.corpus import stopwords as ntStop
from wordcloud import STOPWORDS as wcStop
from spellchecker import SpellChecker
from textblob import TextBlob
from emot.emo_unicode import UNICODE_EMO, EMOTICONS
import Cleaner, Analyzer
from Tweet import Tweet

def config(section,filename='database.ini'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


class Listener(StreamListener):

    def on_status(self, status):
        
        if hasattr(status, "retweeted_status"): 
            rt = "true"
            try:
                text = status.retweeted_status.extended_tweet["full_text"]
                
            except AttributeError:
                text = status.retweeted_status.text
        else:
            rt = "false"
            try:
                text = status.extended_tweet["full_text"]
            except AttributeError:
                text = status.text

        mentions = status.entities["user_mentions"]
        hashtags = status.entities["hashtags"]
        pm = []; ht = []
        for m in mentions:
            if m["name"].isascii():
                pm.append(m["name"])
        for h in hashtags:
            if h["text"].isascii():
                ht.append(h["text"])

        tweet = Tweet(text,status.id_str,status.user.screen_name,status.created_at,ht,pm,status.favorite_count,status.retweet_count,rt)   
        tweets.append(tweet)
        if len(tweets) == 300:
             return False
                  
    def on_error(self, status_code):
        print(status_code)
        return False

def listToDbString(inputList):
    if len(inputList) == 0:
        dbString = "null"
    else:
        inputList = list(set(inputList))
        dbString = "|| ".join(inputList)
        dbString = Cleaner.standardize(dbString)
        dbString = dbString.replace("\'","\'\'")
        dbString = "\'" + dbString + "\'"
    return dbString

API_Key = "WNmf8Sn7lxTnv8DXXETH2rMt3"
API_Secret_Key = "si9nsqctwXlrkCISATa9Tb4Rz8n50WneRIlrpvz710d9SPhI2p"
Bearer_Token = "AAAAAAAAAAAAAAAAAAAAAEvlJgEAAAAATlgz0sdbprRgHkkU%2B0hVrF1jAKE%3DhX8F3CD6SxXBITywP9TbAYMjABQMLOnZfb7HUlWoa1jNVG5gBq"
Access_Token = "251584559-knqwY4QZn8G6qmVUba2P9yJJ0aOhRPPMQj5yjjra"
Access_Token_Secret = "lS2FkFXPLdmKMToCDY2BrLHOh6d3cJJVk0OUYjkgBxLjS"
tagme.GCUBE_TOKEN = "24d4b5ec-ce55-4be2-a530-75f1d03fbc76-843339462"
#Authenticate
auth = tweepy.OAuthHandler(API_Key, API_Secret_Key)
auth.set_access_token(Access_Token, Access_Token_Secret)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

#Stream
tweets = []

listener = Listener()#output_file=output)
stream = Stream(auth=api.auth, listener=listener,tweet_mode='extended',)
stream.filter(track=['corona','covid','coronavirus','covid19','covid-19'],encoding='ascii',languages=['en'])#,locations=[42.091493, -124.080958, 25.288416, -80.516587])
try:
    print('Start streaming.')
except KeyboardInterrupt:
    print("Stopped.")
finally:
    stream.disconnect()


##DB CONNECTIONS
params = config('posts')
conn = psycopg2.connect(**params)
cur = conn.cursor()
stopwords = Cleaner.getCustomStopwords(reference="custom", filename="CustomStopwords.txt")
for post in tweets:
    p_text_orig = post.text
    p_text_orig = p_text_orig.replace('\'','\'\'')
    p_date = post.post_date
    p_mentions = listToDbString(post.mentions)
    p_hashtags = listToDbString(post.hashtags)

    #Clean Tweet
    p_text_clean = Cleaner.standardize(post.text)
    p_text_clean = Cleaner.removeHastags(p_text_clean)
    p_text_clean = Cleaner.removeMentions(p_text_clean)
    p_text_clean = Cleaner.cleanURL(p_text_clean)
    p_text_clean = Cleaner.convertAbbreviations(p_text_clean)
    p_fortag = p_text_clean
    p_text_clean = Cleaner.removePunctuation(p_text_clean)
    (p_text_clean, p_text_clean_wo_emojis, p_emojis) = Cleaner.convertEmojis(p_text_clean)
    p_emojis = listToDbString(p_emojis)
    p_text_clean = Cleaner.removeStopwords(p_text_clean,stopwords)

    #Analyze
    p_text_lemmatized = Analyzer.lemmatization(p_text_clean)
    sentiment_score = Analyzer.analyzeSentiment(p_text_lemmatized,tool="vader")
    sentiment_result = Analyzer.getSentimentResult(sentiment_score)

    #ENTITIES
    entities = []
    tags = tagme.annotate(p_fortag)
    for t in tags.get_annotations(0.125):
        t = str(t).split('>')[1].split('(')[0].strip()
        t = t.replace("\'","\'\'")
        entities.append(t)
    p_entities = "||".join(list(set(entities)))
    
    #Insert to DB
    query = 'INSERT INTO \"STREAMED_DATA\".\"TWITTER\" (\"POST_CONTENT\" , \"POST_DATE\", \"HASHTAGS\",\"MENTIONS_SCREEN_NAME\",\"POST_CLEANED\",\"EMOJIS\",\"POST_LEMMATIZED\",\"SENTIMENT_RESULT\",\"SENTIMENT_SCORE\",\"POST_ID\",\"USER_NAME\",\"FAVOURITE_COUNT\",\"RETWEET_COUNT\",\"IS_RETWEET\",\"ENTITIES\") VALUES (\'%s\', TO_DATE(\'%s\',\'YYYY-MM-DD HH24:MI:SS\'),%s,%s,\'%s\',%s,\'%s\',\'%s\',%f,\'%s\',\'%s\',%d,%d,\'%s\',\'%s\') RETURNING \"ID\"' %(p_text_orig,post.post_date, p_hashtags,p_mentions,p_text_clean,p_emojis,p_text_lemmatized,sentiment_result,sentiment_score,post.post_id,post.user_name,post.favourite_count,post.retweet_count,post.is_retweet,p_entities)    
    #print("QUERY:",query)
    
    cur.execute(query)  
    output = cur.fetchone()
    print("OUTPUT:",output)
    
    conn.commit() 
    print("\n")
    
cur.close()
