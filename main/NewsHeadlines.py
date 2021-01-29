from newsapi import NewsApiClient
import environ,os
from datetime import datetime
from datetime import timedelta
''' % LOCAL TEST 
env = environ.Env()
environ.Env.read_env()
'''
def getHeadlines(source,fromDate,toDate):
    #newsapi = NewsApiClient(api_key=env("NEWS_API_KEY"))
    newsapi = NewsApiClient(api_key=os.environ['NEWS_API_KEY'])
    if toDate == "":
        toDate = str(datetime.now()).split(' ')[0]
    if fromDate == "":
        fromDate = str(datetime.now()- timedelta(days=1)).split(' ')[0]
    #print("from:",fromDate)
    #print("toDate:",toDate)
    available = str(datetime.now() - timedelta(days=30)).split(' ')[0]
    if str(toDate) <= available:
        print("returning empty")
        return []
    else:
        if str(fromDate) <= available:
            fromDate = datetime.strptime(available, '%Y-%m-%d')
    print("final from:",fromDate,"  final to:",toDate)

    #"Al Jazeera English,Associated Press,Bloomberg,Business Insider,CBS News,CNN,Fortune,Fox News,Google News,IGN,NBC News,Newsweek,Politico,Recode,Reuters,The American Conservative,The Huffington Post,The Verge,The Wall Street Journal,The Washington Post,The Washington Times,Time,USA Today,Vice News"
    all_articles = newsapi.get_everything(q='covid',
                                        sources=source,
                                        from_param=fromDate,
                                        to=toDate,
                                        language='en',
                                        sort_by='popularity')
    return all_articles["articles"]
