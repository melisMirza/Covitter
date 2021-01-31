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
import tagme, collections
import environ

######
#ANALYSIS METHODS
######

# Returns lemmatized version of a text
def lemmatization(text):
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')
    lemmatizer = WordNetLemmatizer()
    wordnet_map = {"N":wordnet.NOUN, "V":wordnet.VERB, "J":wordnet.ADJ, "R":wordnet.ADV}

    text_tagged = nltk.pos_tag(text.split())
    text_lemmatized = " ".join([lemmatizer.lemmatize(word, wordnet_map.get(pos[0], wordnet.NOUN)) for word, pos in text_tagged])

    return text_lemmatized

# Analyzes the sentiment of a text, using the chosen tool, returns a sentiment score between -1 and 1
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

# Categorizes the sentiment score to : Very Negative, Negative, Neutral, Positive, Very Positive
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

# Identifies the entities in a given text, using Tagme
def getEntities(text,input_type="text"):
    #tagme.GCUBE_TOKEN = env("TAGME_TOKEN")
    tagme.GCUBE_TOKEN = os.environ['TAGME_TOKEN']

    entities = []
    limit = 0.125
    try:
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
    except:
        pass        
    return entities

# Returns the most common {result_count} many entities of a given entity list, returns a dataframe
def getTopEntities(entities,result_count=15):
    allEntities = []
    
    #Convert mentions to entities
    for eg in entities:
        temp = []
        if "str" in str(type(eg)):
            #allEntities += eg.split('||')      
            temp = eg.split('||')
            for e in temp:
                if e != '':
                    allEntities.append(e)
    #allEntities.remove('')
    entDict = collections.Counter(allEntities)
    entDict_inv = {k: v for k, v in sorted(entDict.items(), key=lambda item: item[1],reverse=True)}
    output = [['Entity', 'Occurance']]
    e_keys = list(entDict_inv.keys())
    limit = [lambda:len(e_keys),lambda:result_count][len(e_keys) > result_count]()
    for r in range(limit):
        output.append([e_keys[r], entDict_inv[e_keys[r]]])
    return output

# Returns the most common {result_count} many mentioned users of a given mentions list, returns a dataframe
def getTopMentions(mentions,result_count=15):
    allMentions = []
    
    #Convert mentions to entities
    for eg in mentions:
        temp = []
        if "str" in str(type(eg)):
            temp = eg.split('||')
            for e in temp:
                if e != '':
                    allMentions.append(e.strip())
    mentDict = collections.Counter(allMentions)
    mentDict_inv = {k: v for k, v in sorted(mentDict.items(), key=lambda item: item[1],reverse=True)}
    output = [['Mention', 'Occurance']]
    me_keys = list(mentDict_inv.keys())
    limit = [lambda:len(me_keys),lambda:result_count][len(me_keys) > result_count]()
    for r in range(limit):
        output.append([me_keys[r], mentDict_inv[me_keys[r]]])
    return output