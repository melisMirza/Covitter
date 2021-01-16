import json, tweepy, requests, sys, subprocess, os
import pandas as pd 
from tweepy import StreamListener
from tweepy import Stream
import string, nltk,re, emot
from nltk.corpus import stopwords as ntStop
from wordcloud import STOPWORDS as wcStop
from textblob import TextBlob
from emot.emo_unicode import UNICODE_EMO, EMOTICONS
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import tagme
import environ
''' % LOCAL TEST %
env = environ.Env()
environ.Env.read_env()
'''
def lemmatization(text):
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')
    lemmatizer = WordNetLemmatizer()
    wordnet_map = {"N":wordnet.NOUN, "V":wordnet.VERB, "J":wordnet.ADJ, "R":wordnet.ADV}

    text_tagged = nltk.pos_tag(text.split())
    text_lemmatized = " ".join([lemmatizer.lemmatize(word, wordnet_map.get(pos[0], wordnet.NOUN)) for word, pos in text_tagged])

    return text_lemmatized

def analyzeSentiment(text,tool):
    sentimentScore = 0.0
    if tool == "textblob":
        sentimentScore = TextBlob(text).sentiment.polarity
    elif tool == "vader":
        nltk.download('vader_lexicon')
        sid = SentimentIntensityAnalyzer()
        polDict = sid.polarity_scores(text)
        sentimentScore = polDict["compound"]
    return sentimentScore

def getSentimentResult(sentiment_score):
    
    if sentiment_score >= 0.25 and sentiment_score < 0.75:
        sentiment = "Positive"
    elif sentiment_score >= 0.75:
        sentiment = "Very Positive"
    elif sentiment_score <= -0.25 and sentiment_score > -0.75:
        sentiment = "Negative"
    elif sentiment_score <= -0.75:
        sentiment = "Very Negative"
    else:
        sentiment = "Neutral"
    
    return sentiment

def getEntities(text,input_type="text"):
    #tagme.GCUBE_TOKEN = env("TAGME_TOKEN")
    tagme.GCUBE_TOKEN = os.environ['TAGME_TOKEN']

    entities = []
    limit = 0.125

    if input_type == "mentions":
        for m in text.split('||'):
            tags = tagme.annotate(m)
            for t in tags.get_annotations(limit):
                t = str(t).split('>')[1].split('(')[0].strip()
                t = t.replace("\'","\'\'")
                entities.append(t)
    else:
        tags = tagme.annotate(text)
        for t in tags.get_annotations(limit):
            t = str(t).split('>')[1].split('(')[0].strip()
            t = t.replace("\'","\'\'")
            entities.append(t)
            
    return entities