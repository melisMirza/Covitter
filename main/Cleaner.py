import json, tweepy, requests, sys, subprocess, os
import pandas as pd 
from tweepy import StreamListener
from tweepy import Stream
import string, nltk,re, emot
from nltk.corpus import stopwords as ntStop
from wordcloud import STOPWORDS as wcStop
#from spellchecker import SpellChecker
from textblob import TextBlob
from emot.emo_unicode import UNICODE_EMO, EMOTICONS

#####
#CLEANING AND PRE-PROCESSING ACTIVITIES
#####

# Retrieves chosen stop words, returns list
def getCustomStopwords(reference,filename=""):
    stopwords = []
    if reference == "custom":
        with open(filename, 'r+') as cs:
            customWords = cs.readlines()
        cs.close()
        for w in customWords:
            stopwords.append(w.replace("\n",""))

    elif reference == "nltk":
        nltk.download('stopwords')
        stopwords = ntStop.words('english')

    elif reference == "wordcloud":
        stopwords = list(set(wcStop))
    else:
        pass
    return stopwords

# Retrieves chosen abbreviations, returns list
def getAbbreviations(filename):
    abbDict = {}

    with open(filename, 'r+') as ab:
        content = ab.readlines()
    ab.close()
    content = list(set(content))
    for abb in content:
        abr = abb.split('=')[0].lower()
        meaning = abb.split('=')[1].replace("\n","").lower()
        abbDict[abr] = meaning
    
    return abbDict

# removes new lines and quotations, return string
def standardize(text):
    text = text.lower()
    text = text.replace('\n',' ')
    text = text.replace('’','\'')
    text = text.replace('‘','\'')
    text = text.replace('“','\'')
    text = text.replace('”','\'')
    return text

#cleans the given list of stop words from text, returns string
def removeStopwords(text,wordlist):
    text = " ".join([word for word in str(text).split() if word not in wordlist])
    return text

#cleans URLs from a given text, returns string
def cleanURL(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    text = url_pattern.sub(r'', text)
    return text

#cleans non utf-8 characters, returns string
def removeNonUtf8(text):
    text = bytes(text, 'utf-8').decode('utf-8', 'ignore')
    return text

#cleans punctuations from text, returns string
def removePunctuation(text):
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    text = text.translate(translator)
    return text

#cleans user mentions in a post(ones that start with '@'), returns string
def removeMentions(text):
    text = " ".join([word for word in str(text).split() if not word.startswith('@')])
    return text

#cleans hashtags in a post(ones that start with '#'), returns string
def removeHastags(text):
    text = " ".join([word for word in str(text).split() if not word.startswith('#')])
    return text

#coverts emoijs to their descriptions, returns string
def convertEmojis(text):
    #Get emojis and emoticons in the tweet
    if "list" in str(type(emot.emoji(text))):
        emojis = emot.emoji(text)[0]
    else:
        emojis = emot.emoji(text)
    
    if "list" in str(type(emot.emoticons(text))):
        emoticons = emot.emoticons(text)[0]
    else:
        emoticons = emot.emoticons(text)
    
    emotList = []
    if emojis["flag"]:
        emotList += list(emojis["mean"])
    if emoticons["flag"]:
        emotList += list(emoticons["mean"])
    
    text_wo_emotion = text
    for emotion in UNICODE_EMO:
        text = text.replace(emotion," "+" ".join(UNICODE_EMO[emotion].replace(",","").replace(":","").replace("_"," ").split()))
        text_wo_emotion = text.replace(emotion," ")
    return (text, text_wo_emotion,emotList)

#converts abbreviations to original meaning, returns string
def convertAbbreviations(text,filename="main\Abbreviations.txt"):
    abbDict = getAbbreviations(filename)
    text_converted = []
    for word in str(text).split():
        if word in abbDict.keys():
            text_converted.append(abbDict[word])
        else:
            text_converted.append(word)
    return " ".join(text_converted)

#cleans the post for viewing on front-end, return string    
def cleanForView(text):
    text = text.replace('\n',' ')
    text = text.replace('&amp;','&')
    text = text.replace('&gt;','>')
    text = text.replace('&lt;','<')
    text = text.replace('&le;','<=')
    text = text.replace('&ge;','>=')

    return text