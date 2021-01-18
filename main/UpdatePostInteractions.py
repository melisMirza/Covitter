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
from pathlib import Path
from datetime import datetime
from datetime import timedelta

API_Key = os.environ['TWIITER_API_KEY']
API_Secret_Key = os.environ['TWIITER_API_SECRET_KEY']
Access_Token = os.environ['TWIITER_ACCESS_TOKEN']
Access_Token_Secret = os.environ['TWIITER_ACCESS_TOKEN_SECRET']
tagme.GCUBE_TOKEN = os.environ['TAGME_TOKEN']

now = datetime.now()
lastmonth = now - timedelta(days=30)
today = now.strftime("%Y-%m-%d")
lastmonth_date = lastmonth.strftime("%Y-%m-%d")



#Authenticate
auth = tweepy.OAuthHandler(API_Key, API_Secret_Key)
auth.set_access_token(Access_Token, Access_Token_Secret)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

dbconn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
curget = dbconn.cursor()
query = 'SELECT post_id FROM twitter WHERE post_date >= \'%s\' AND post_date < \'%s\' ' %(lastmonth_date,today)
curget.execute(query)  
output = curget.fetchall()
dbconn.commit() 
curget.close()
ids=[]
for i in output:
    (p_id,) = i
    ids.append(p_id)
print(len(ids))

end = False
startIndex = 0
batch = 30
endIndex = startIndex + batch
while not end:
    if endIndex > len(ids):
        endIndex = len(ids)
        end = True
    conn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
    cur = conn.cursor()
    tweetContents = api.statuses_lookup(id_=ids[startIndex:endIndex],tweet_mode="extended")
    for tw in tweetContents:
        print(tw)
        post_id=tw.id_str
        retweet_count = tw.retweet_count
        favorite_count = tw.favorite_count

        query = 'UPDATE twitter SET favourite_count=%d,retweet_count=%d WHERE post_id=\'%s\' RETURNING id' %(favorite_count,retweet_count,post_id)
        print("QUERY:",query)
        cur.execute(query)  
        output = cur.fetchone()
        print("OUTPUT:",output)
        conn.commit() 
        print("\n")
    startIndex += batch
    endIndex = startIndex + batch
    cur.close()






   
