import psycopg2
from configparser import ConfigParser
import json, tweepy, requests, sys, subprocess, os
import pandas as pd 
from tweepy import StreamListener
from tweepy import Stream
import string, nltk,re, emot,tagme
from nltk.corpus import stopwords as ntStop
from wordcloud import STOPWORDS as wcStop
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
            print("m[name]:",m["name"],":",type(m["name"]))
            if m["name"].strip() == ascii(m["name"]):
                pm.append(m["name"])
        for h in hashtags:
            print("h[text]:",h["text"],":",type(h["text"]))
            if h["text"].strip() == ascii(h["text"]):
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

API_Key = os.environ['TWIITER_API_KEY']
API_Secret_Key = os.environ['TWIITER_API_SECRET_KEY']
Access_Token = os.environ['TWIITER_ACCESS_TOKEN']
Access_Token_Secret = os.environ['TWIITER_ACCESS_TOKEN_SECRET']
tagme.GCUBE_TOKEN = os.environ['TAGME_TOKEN']
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
#params = config('posts')
#conn = psycopg2.connect(**params)
conn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
cur = conn.cursor()
stopwords = Cleaner.getCustomStopwords(reference="custom", filename="CustomStopwords.txt")
for post in tweets:
    p_text_orig = post.text
    print(post.text)
    p_text_orig = p_text_orig.replace('\'','\'\'')
    p_date = post.post_date
    p_mentions = listToDbString(post.mentions)
    p_hashtags = listToDbString(post.hashtags)

    #Clean Tweet
    print("cleaning")
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
    print("analyzing")
    p_text_lemmatized = Analyzer.lemmatization(p_text_clean)
    sentiment_score = Analyzer.analyzeSentiment(p_text_lemmatized,tool="vader")
    sentiment_result = Analyzer.getSentimentResult(sentiment_score)

    #ENTITIES
    print("entities")
    entities = []
    tags = tagme.annotate(p_fortag)
    for t in tags.get_annotations(0.125):
        t = str(t).split('>')[1].split('(')[0].strip()
        t = t.replace("\'","\'\'")
        entities.append(t)
    p_entities = "||".join(list(set(entities)))
    
    #Insert to DB
    #query = 'INSERT INTO \"STREAMED_DATA\".\"TWITTER\" (\"POST_CONTENT\" , \"POST_DATE\", \"HASHTAGS\",\"MENTIONS_SCREEN_NAME\",\"POST_CLEANED\",\"EMOJIS\",\"POST_LEMMATIZED\",\"SENTIMENT_RESULT\",\"SENTIMENT_SCORE\",\"POST_ID\",\"USER_NAME\",\"FAVOURITE_COUNT\",\"RETWEET_COUNT\",\"IS_RETWEET\",\"ENTITIES\") VALUES (\'%s\', TO_DATE(\'%s\',\'YYYY-MM-DD HH24:MI:SS\'),%s,%s,\'%s\',%s,\'%s\',\'%s\',%f,\'%s\',\'%s\',%d,%d,\'%s\',\'%s\') RETURNING \"ID\"' %(p_text_orig,post.post_date, p_hashtags,p_mentions,p_text_clean,p_emojis,p_text_lemmatized,sentiment_result,sentiment_score,post.post_id,post.user_name,post.favourite_count,post.retweet_count,post.is_retweet,p_entities)    
    query = 'INSERT INTO twitter (post_content , post_date, hashtags,mentions_screen_name,post_cleaned,emojis,post_lemmatized,sentiment_result,sentiment_score,post_id,user_name,favourite_count,retweet_count,is_retweet,entities) VALUES (\'%s\', TO_DATE(\'%s\',\'YYYY-MM-DD HH24:MI:SS\'),%s,%s,\'%s\',%s,\'%s\',\'%s\',%f,\'%s\',\'%s\',%d,%d,\'%s\',\'%s\') RETURNING id' %(p_text_orig,post.post_date, p_hashtags,p_mentions,p_text_clean,p_emojis,p_text_lemmatized,sentiment_result,sentiment_score,post.post_id,post.user_name,post.favourite_count,post.retweet_count,post.is_retweet,p_entities)    
    #print("QUERY:",query)
    
    cur.execute(query)  
    output = cur.fetchone()
    print("OUTPUT:",output)
    
    conn.commit() 
    print("\n")
    
cur.close()
