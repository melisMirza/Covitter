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

def getAbbreviations(filename = "Abbreviations.txt"):
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

def standardize(text):
    text = text.lower()
    text = text.replace('\n',' ')
    text = text.replace('’','\'')
    text = text.replace('‘','\'')
    text = text.replace('“','\'')
    text = text.replace('”','\'')
    return text

def removeStopwords(text,wordlist):
    text = " ".join([word for word in str(text).split() if word not in wordlist])
    return text

def cleanURL(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    text = url_pattern.sub(r'', text)
    return text

def removeNonUtf8(text):
    text = bytes(text, 'utf-8').decode('utf-8', 'ignore')
    return text
'''
def correctSpellings(text):
    spell = SpellChecker()  
    corrected_text = []
    misspelled_words = spell.unknown(text.split())
    for word in text.split():
        if word in misspelled_words:
            corrected_text.append(spell.correction(word))
        else:
            corrected_text.append(word)
    return " ".join(corrected_text)
'''
def removePunctuation(text):
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    text = text.translate(translator)
    return text

def removeMentions(text):
    text = " ".join([word for word in str(text).split() if not word.startswith('@')])
    return text

def removeHastags(text):
    text = " ".join([word for word in str(text).split() if not word.startswith('#')])
    return text

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

def convertAbbreviations(text):
    abbDict = getAbbreviations()
    text_converted = []
    for word in str(text).split():
        if word in abbDict.keys():
            text_converted.append(abbDict[word])
        else:
            text_converted.append(word)
    return " ".join(text_converted)
    

