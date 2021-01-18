from django.shortcuts import render
from . import RetrieveTweets, Cleaner, ConcurrenyNetwork, NewsHeadlines, Analyzer
import pandas as pd 
from main.forms import WordSearchForm
from django.shortcuts import redirect
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import json
# Create your views here.
def weekly(request):
    return render(request, "main/Weekly.html",{})


def search(request):
    if request.method == "POST":
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        words = request.POST.get("search_words")
        url ="/analytics/search/results?search=%s&from=%s&to=%s" %(words,from_date,to_date)
        return redirect(url)

    return render(request, "main/Search.html",{})

def searchResults(request):
    from_date = str(request.GET['from'])
    to_date = str(request.GET['to'])
    search_words = request.GET['search']
    news_from = from_date ; news_to = to_date
    if from_date == "" and to_date == "" and search_words == "":
        return render(request, "main/Search.html",{})
    else:   
        if from_date == "" and to_date == "":
            tweets = RetrieveTweets.getTweetDF(option="search",searchwords=search_words.lower())
        elif search_words == "":
            tweets = RetrieveTweets.getTweetDF(option="custom",fromDate=from_date,toDate=to_date)
    
    print("tweets:")
    print(tweets)
    totalPosts = len(tweets['orig_content'])

    ## Entities
    entities = json.dumps(Analyzer.getTopEntities(tweets['entities']))
    print(entities)
    '''
    ##network
    print("getting graph")
    conc_graph = ConcurrenyNetwork.createUDUWnetork(tweets)
    pos = nx.fruchterman_reingold_layout(conc_graph)
    nx.draw(conc_graph,pos)
    plt.show()
    '''
    #Hashtag table
    hashDF = RetrieveTweets.getTopHashtags(tweets,count=10)
    hashtag_data = hashDF.to_dict('split')
    hashtag_data["combined"] = []
    for i in range(len(hashtag_data["index"])):
        hashtag_data["combined"].append([i+1, hashtag_data["index"][i], hashtag_data["data"][i][0]])
    hashtag_data["totalCount"] = str(len(hashtag_data["index"]))

    #Sentiments
    sentiments = json.dumps(RetrieveTweets.getSentimentResults(tweets))
    print(sentiments)
    ## Mentions
    mentions = json.dumps(Analyzer.getTopMentions(tweets['mentions']))
    print(mentions)

    #News
    headlines = {"cnn":[],"breitbart":[],"washington":[]}   
    if len(tweets['date']) > 0:
        dates = list(set(tweets['date']))
        dates.sort()    
        news_from = [lambda:dates[0],lambda:from_date][from_date != ""]()
        news_to = [lambda:dates[-1],lambda:to_date][to_date != ""]()  
        cnn_data = NewsHeadlines.getHeadlines(source="CNN",fromDate = news_from,toDate = news_to)
        breitbart_data = NewsHeadlines.getHeadlines(source="breitbart-news",fromDate = news_from,toDate = news_to)
        washington_data = NewsHeadlines.getHeadlines(source="the-washington-post",fromDate = news_from,toDate = news_to)
        if len(cnn_data) > 0:
            for i in range(10):
                headlines["cnn"].append(Cleaner.cleanForView(cnn_data[i]["title"]))
                headlines["breitbart"].append(Cleaner.cleanForView(breitbart_data[i]["title"]))
                headlines["washington"].append(Cleaner.cleanForView(washington_data[i]["title"]))

    #Tweet Content Table
    post_data_df = tweets[['date','orig_content','favourite_count','retweet_count','sentiment']]
    post_data = post_data_df.to_dict('split')
    for d in range(0,len(post_data["data"])):
        post_data["data"][d][1] = Cleaner.cleanForView(post_data["data"][d][1])
    post_data["combined"] = []
    for i in post_data["index"]:
        combined = [i+1] + post_data["data"][i]
        post_data["combined"].append(combined)
    #print(post_data)
    post_data["count"] = totalPosts
    return render(request, "main/SearchResults.html",{"post_data":post_data,"hashtag_data":hashtag_data, "headlines":headlines,"sentiments":sentiments,"entities":entities,"mentions":mentions})

    #return render(request, "main/DateSearchResults.html",{"post_data":post_data})



def dateSearch(request):
    if request.method == "POST":
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        url ="/analytics/datesearch/results?from=%s&to=%s" %(from_date,to_date)
        return redirect(url)

    return render(request, "main/DateSearch.html",{})

def dateSearchResults(request):
    from_date = str(request.GET['from'])
    to_date = str(request.GET['to'])
    tweets = RetrieveTweets.getTweetDF(option="custom",fromDate=from_date,toDate=to_date)
    print("tweets:")
    print(tweets)
    totalPosts = len(tweets['orig_content'])

    ## Entities
    entities = json.dumps(Analyzer.getTopEntities(tweets['entities']))
    print(entities)
    '''
    ##network
    print("getting graph")
    conc_graph = ConcurrenyNetwork.createUDUWnetork(tweets)
    pos = nx.fruchterman_reingold_layout(conc_graph)
    nx.draw(conc_graph,pos)
    plt.show()
    '''
    #Hashtag table
    hashDF = RetrieveTweets.getTopHashtags(tweets,count=10)
    hashtag_data = hashDF.to_dict('split')
    hashtag_data["combined"] = []
    for i in range(len(hashtag_data["index"])):
        hashtag_data["combined"].append([i+1, hashtag_data["index"][i], hashtag_data["data"][i][0]])
    hashtag_data["totalCount"] = str(len(hashtag_data["index"]))

    #Sentiments
    sentiments = json.dumps(RetrieveTweets.getSentimentResults(tweets))
    print(sentiments)
    ## Mentions
    mentions = json.dumps(Analyzer.getTopMentions(tweets['mentions']))
    print(mentions)

    #News
    headlines = {"cnn":[],"breitbart":[],"washington":[]}   
    if len(tweets['date']) > 0:
        dates = list(set(tweets['date']))
        dates.sort()       
        cnn_data = NewsHeadlines.getHeadlines(source="CNN",fromDate = from_date,toDate = to_date)
        breitbart_data = NewsHeadlines.getHeadlines(source="breitbart-news",fromDate = from_date,toDate = to_date)
        washington_data = NewsHeadlines.getHeadlines(source="the-washington-post",fromDate = from_date,toDate = to_date)
        if len(cnn_data) > 0:
            for i in range(10):
                headlines["cnn"].append(Cleaner.cleanForView(cnn_data[i]["title"]))
                headlines["breitbart"].append(Cleaner.cleanForView(breitbart_data[i]["title"]))
                headlines["washington"].append(Cleaner.cleanForView(washington_data[i]["title"]))

    #Tweet Content Table
    post_data_df = tweets[['date','orig_content','favourite_count','retweet_count','sentiment']]
    post_data = post_data_df.to_dict('split')
    for d in range(0,len(post_data["data"])):
        post_data["data"][d][1] = Cleaner.cleanForView(post_data["data"][d][1])
    post_data["combined"] = []
    for i in post_data["index"]:
        combined = [i+1] + post_data["data"][i]
        post_data["combined"].append(combined)
    #print(post_data)
    post_data["count"] = totalPosts
    return render(request, "main/DateSearchResults.html",{"post_data":post_data,"hashtag_data":hashtag_data, "headlines":headlines,"sentiments":sentiments,"entities":entities,"mentions":mentions})

    #return render(request, "main/DateSearchResults.html",{"post_data":post_data})

def wordSearch(request):
    if request.method == "POST":
        words = request.POST.get("search_words")
        url ="/analytics/wordsearch/results?search=" + words
        print(url)
        return redirect(url)

    return render(request, "main/WordSearch.html",{})

def wordSearchResults(request):
    search_words = request.GET['search']
    tweets = RetrieveTweets.getTweetDF(option="search",searchwords=search_words.lower())
    totalPosts = len(tweets['orig_content'])
    #post_data_df = tweets[['orig_content','tags','sentiment']]
    '''
    ##network
    print("getting graph")
    conc_graph = ConcurrenyNetwork.createUDUWnetork(tweets)
    pos = nx.fruchterman_reingold_layout(conc_graph)
    nx.draw(conc_graph,pos)
    plt.show()
    '''

    ## Entities
    entities = json.dumps(Analyzer.getTopEntities(tweets['entities']))
    print(entities)
    
    ## Mentions
    mentions = json.dumps(Analyzer.getTopMentions(tweets['mentions']))
    print(mentions)

    #Hashtag table
    hashDF = RetrieveTweets.getTopHashtags(tweets,count=10)
    hashtag_data = hashDF.to_dict('split')
    hashtag_data["combined"] = []
    for i in range(len(hashtag_data["index"])):
        hashtag_data["combined"].append([i+1, hashtag_data["index"][i], hashtag_data["data"][i][0]])
    hashtag_data["totalCount"] = str(len(hashtag_data["index"]))

    #Sentiments
    sentiments = json.dumps(RetrieveTweets.getSentimentResults(tweets))
    print(sentiments)
    
    #News
    headlines = {"cnn":[],"breitbart":[],"washington":[]}   
    if len(tweets['date']) > 0:

        dates = list(set(tweets['date']))
        dates.sort()
        
        cnn_data = NewsHeadlines.getHeadlines(source="CNN",fromDate = dates[0],toDate = dates[-1])
        breitbart_data = NewsHeadlines.getHeadlines(source="breitbart-news",fromDate = dates[0],toDate = dates[-1])
        washington_data = NewsHeadlines.getHeadlines(source="the-washington-post",fromDate = dates[0],toDate = dates[-1])
        if len(cnn_data) > 0:
            for i in range(10):
                headlines["cnn"].append(Cleaner.cleanForView(cnn_data[i]["title"]))
                headlines["breitbart"].append(Cleaner.cleanForView(breitbart_data[i]["title"]))
                headlines["washington"].append(Cleaner.cleanForView(washington_data[i]["title"]))
    
    #Tweet Content Table
    post_data_df = tweets[['date','orig_content','favourite_count','retweet_count','sentiment']]
    post_data = post_data_df.to_dict('split')
    for d in range(0,len(post_data["data"])):
        post_data["data"][d][1] = Cleaner.cleanForView(post_data["data"][d][1])
    post_data["combined"] = []
    for i in post_data["index"]:
        combined = [i+1] + post_data["data"][i]
        post_data["combined"].append(combined)
    #print(post_data)
    post_data["count"] = totalPosts
    return render(request, "main/WordSearchResults.html",{"post_data":post_data,"hashtag_data":hashtag_data, "headlines":headlines,"sentiments":sentiments, "entities":entities, "mentions":mentions})

def userAccount(request):
    return render(request, "main/UserAccount.html",{})