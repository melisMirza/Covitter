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
import snscrape.modules.twitter

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

BASE_DIR = Path(__file__).resolve().parent.parent
base = os.path.join(BASE_DIR, 'main')
print(base)
filename = base+"/CustomStopwords.txt"
stopwords = Cleaner.getCustomStopwords(reference="custom", filename=filename)

API_Key = os.environ['TWIITER_API_KEY']
API_Secret_Key = os.environ['TWIITER_API_SECRET_KEY']
Access_Token = os.environ['TWIITER_ACCESS_TOKEN']
Access_Token_Secret = os.environ['TWIITER_ACCESS_TOKEN_SECRET']
tagme.GCUBE_TOKEN = os.environ['TAGME_TOKEN']

#Authenticate
auth = tweepy.OAuthHandler(API_Key, API_Secret_Key)
auth.set_access_token(Access_Token, Access_Token_Secret)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

now = datetime.now()
p_d = now.strftime("%Y-%m-%d")
while p_d != "2020-01-01":
    day_before = datetime.strptime(p_d,"%Y-%m-%d")
    day_before = day_before - timedelta(days=1)
    day_before_str = day_before.strftime("%Y-%m-%d")

    dbconn = psycopg2.connect("postgres://xyaoonlajxbtxz:abf03651d79b90a5f194b86303a93037dedcb01544f920ff1635d7c1638d0e3c@ec2-18-208-49-190.compute-1.amazonaws.com:5432/d43c41soe9v55l",sslmode='require')
    curs = dbconn.cursor()
    query = 'SELECT COUNT(post_id) FROM twitter WHERE post_date = \'%s\'' %(p_d)
    curs.execute(query)  
    output = curs.fetchall()
    dbconn.commit() 
    (dailyCount,) = output[0]
    missing = 2000 - dailyCount
    
    if missing > 0:
        print("will retreive ",missing, " tweets")
        
        ids = []
        query = "covid since:%s until:%s lang:en" %(str(day_before_str).split(' ')[0],str(p_d).split(' ')[0])
        print(query)
        for tweet in snscrape.modules.twitter.TwitterSearchScraper(query).get_items():
            tl = str(tweet).split('/')[-1]
            #print(tl)
            #print(tweet.content)
            ids.append(tl)
            if len(ids) >= missing:
                break

        end = False
        startIndex = 0
        batch = 30
        endIndex = startIndex + batch
        while not end:
            if endIndex > len(ids):
                endIndex = len(ids)
                end = True
            #conn = psycopg2.connect("postgres://xyaoonlajxbtxz:abf03651d79b90a5f194b86303a93037dedcb01544f920ff1635d7c1638d0e3c@ec2-18-208-49-190.compute-1.amazonaws.com:5432/d43c41soe9v55l",sslmode='require')
            #cur = conn.cursor()
            tweetContents = api.statuses_lookup(id_=ids[startIndex:endIndex],tweet_mode="extended")
            for tw in tweetContents:
                print(tw)
                if hasattr(tw,"retweeted_status"): 
                #if tw.retweeted:
                    is_retweet = "true"
                    try:
                        text = tw.retweeted_status.extended_tweet["full_text"]
                        
                    except AttributeError:
                        #text = tw.retweeted_status.text
                        text = tw.retweeted_status.full_text

                else:
                    is_retweet = "false"
                    try:
                        text = tw.full_text
                    except AttributeError:
                        text = tw.text
                mentions = tw.entities["user_mentions"]
                hashtags = tw.entities["hashtags"]
                pm = []; ht = []
                for m in mentions:
                    if m["name"].isascii():
                        pm.append(m["name"])
                for h in hashtags:
                    if h["text"].isascii():
                        ht.append(h["text"])
                post_id = tw.id_str
                retweet_count = tw.retweet_count
                favorite_count = tw.favorite_count
                user_name = tw.user.screen_name
                post_date = tw.created_at

                p_text_orig = text
                p_text_orig = p_text_orig.replace('\'','\'\'')
                p_mentions = listToDbString(pm)
                p_hashtags = listToDbString(ht)

                #Clean Tweet
                p_text_clean = Cleaner.standardize(text)
                p_text_clean = Cleaner.removeHastags(p_text_clean)
                p_text_clean = Cleaner.removeMentions(p_text_clean)
                p_text_clean = Cleaner.cleanURL(p_text_clean)
                p_text_clean = Cleaner.convertAbbreviations(p_text_clean,filename=base+"/Abbreviations.txt")
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
                try:
                    tags = tagme.annotate(p_fortag)
                    for t in tags.get_annotations(0.125):
                        t = str(t).split('>')[1].split('(')[0].strip()
                        t = t.replace("\'","\'\'")
                        entities.append(t)
                except:
                    pass
                p_entities = '\'' + "||".join(list(set(entities))) + '\''


                query = 'INSERT INTO twitter (post_content , post_date, hashtags,mentions_screen_name,post_cleaned,emojis,post_lemmatized,sentiment_result,sentiment_score,post_id,user_name,favourite_count,retweet_count,is_retweet,entities) VALUES (\'%s\', TO_DATE(\'%s\',\'YYYY-MM-DD HH24:MI:SS\'),%s,%s,\'%s\',%s,\'%s\',\'%s\',%f,\'%s\',\'%s\',%d,%d,\'%s\',%s) RETURNING id' %(p_text_orig,post_date,p_hashtags,p_mentions,p_text_clean,p_emojis,p_text_lemmatized,sentiment_result,sentiment_score,post_id,user_name,favorite_count,retweet_count,is_retweet,p_entities)
                print("QUERY:",query)
                
                curs.execute(query)  
                output = curs.fetchone()
                print("OUTPUT:",output)
                dbconn.commit() 
                print("\n")
            startIndex += batch
            endIndex = startIndex + batch
            curs.close()
        
    p_d = day_before_str







   
