from newsapi import NewsApiClient
import environ,os
''' % LOCAL TEST 
env = environ.Env()
environ.Env.read_env()
'''
def getHeadlines(source,fromDate='2021-01-11',toDate='2021-01-31'):
    #newsapi = NewsApiClient(api_key=env("NEWS_API_KEY"))
    newsapi = NewsApiClient(api_key=os.environ['NEWS_API_KEY'])

    #"Al Jazeera English,Associated Press,Bloomberg,Business Insider,CBS News,CNN,Fortune,Fox News,Google News,IGN,NBC News,Newsweek,Politico,Recode,Reuters,The American Conservative,The Huffington Post,The Verge,The Wall Street Journal,The Washington Post,The Washington Times,Time,USA Today,Vice News"
    all_articles = newsapi.get_everything(q='covid',
                                        sources=source,
                                        from_param=fromDate,
                                        to=toDate,
                                        language='en',
                                        sort_by='popularity')

    return all_articles["articles"]
