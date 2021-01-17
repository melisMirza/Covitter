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
'''
API_Key = os.environ['TWIITER_API_KEY']
API_Secret_Key = os.environ['TWIITER_API_SECRET_KEY']
Access_Token = os.environ['TWIITER_ACCESS_TOKEN']
Access_Token_Secret = os.environ['TWIITER_ACCESS_TOKEN_SECRET']
tagme.GCUBE_TOKEN = os.environ['TAGME_TOKEN']
'''


'''
##DB CONNECTIONS
#params = config('posts')
#conn = psycopg2.connect(**params)
conn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
cur = conn.cursor()
BASE_DIR = Path(__file__).resolve().parent.parent
base = os.path.join(BASE_DIR, 'main')
print(base)
filename = base+"/CustomStopwords.txt"
stopwords = Cleaner.getCustomStopwords(reference="custom", filename=filename)
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
    abbr_file = base + "/Abbreviations.txt"
    p_text_clean = Cleaner.convertAbbreviations(p_text_clean,filename=abbr_file)
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

'''
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

dbconn = psycopg2.connect("postgres://xyaoonlajxbtxz:abf03651d79b90a5f194b86303a93037dedcb01544f920ff1635d7c1638d0e3c@ec2-18-208-49-190.compute-1.amazonaws.com:5432/d43c41soe9v55l",sslmode='require')
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
print(ids)

end = False
startIndex = 0
batch = 30
endIndex = startIndex + batch
while not end:
    if endIndex > len(ids):
        endIndex = len(ids)
        end = True
    conn = psycopg2.connect("postgres://xyaoonlajxbtxz:abf03651d79b90a5f194b86303a93037dedcb01544f920ff1635d7c1638d0e3c@ec2-18-208-49-190.compute-1.amazonaws.com:5432/d43c41soe9v55l",sslmode='require')
    cur = conn.cursor()
    tweetContents = api.statuses_lookup(id_=ids[startIndex:endIndex],tweet_mode="extended")
    for tw in tweetContents:
        print(tw)
        post_id=tw.id_str
        retweet_count = tw.retweet_count
        favorite_count = tw.favorite_count

        query = 'UPDATE twitter SET favourite_count=%d,retweet_count=%d WHERE post_id=\'%s\'' %(favorite_count,retweet_count,post_id)
        print("QUERY:",query)
        cur.execute(query)  
        output = cur.fetchone()
        print("OUTPUT:",output)
        conn.commit() 
        print("\n")
    startIndex += batch
    endIndex = startIndex + batch
    cur.close()






   
