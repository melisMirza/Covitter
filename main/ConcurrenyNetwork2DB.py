import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd 
import Analyzer, RetrieveTweets_schedule
import psycopg2, os

####
# THE SCHEDULED JOB THAT FILLS "CONCURRENCY_ADJACENCY" AND "CONCURRENCY_INDICES" TABLES ON DATABASE 
# USES WEEKLY DATA TO CREATE CO-OCCURENCE GRAPH
# REPLACES NEW VALUES WITH THE OLD
# FOR: ENTITIES, HASHTAGS, USER MENTIONS
#####

def formatDate(origDate):
    date = origDate
    if origDate.strip() != "":
        dl = origDate.split('/')
        day = [lambda:str(dl[1]),lambda:'0'+str(dl[1])][len(str(dl[1])) == 1]()
        month = [lambda:str(dl[0]),lambda:'0'+str(dl[0])][len(str(dl[0])) == 1]()
        date = str(dl[2]) + month + day
    return date

#creates undirected, weighted graph
def createUDWnetork(tweets,graph_content):
    G = nx.Graph()
    #tweetDF = tweets[['mentions','entities','hashtags']]
    tweetDF = tweets[[graph_content]]
    print(tweetDF)
    tweetDict = tweetDF.to_dict('index')
    entityDict = {}
    allEntities = []
    #Convert mentions to entities
    for t in tweetDict.keys():
        entities = []
        if "str" in str(type(tweetDict[t][graph_content])):
            entities = tweetDict[t][graph_content].split('||')
            tweetDict[t][graph_content] = entities
            allEntities += tweetDict[t][graph_content]
            for ent in tweetDict[t][graph_content]:
                if ent != "":
                    if ent.strip() not in entityDict.keys():
                        entityDict[ent.strip()] = [t]
                    else:
                        entityDict[ent.strip()].append(t)
    allEntities = list(set(allEntities))
    print("node length:", len(allEntities))
    try:
        allEntities.remove("")
    except:
        pass
    for e in allEntities:
        #print("Node:",e)
        G.add_node(e.strip())
    print("all nodes added")
    for i in allEntities:
        i = i.strip()
        e1 = entityDict[i] #tweet indeces including this entity
        #print("e1:",e1)
        for j in allEntities:
            j=j.strip()
            if i != j:
                e2 = entityDict[j] #compare against other entities
                #print("e2:",e2)
                intersection_list = list(set(e1).intersection(e2))
                #print("intersection:",intersection_list)
                if len(intersection_list) > 0:
                    G.add_edge(i,j,weight=len(intersection_list))
    print("all edges added")
    return G
    
#DEGREE CENTRALITY
def degreeCentrality(G):
    und_degree = nx.degree_centrality(G)
    return und_degree

#CLOSENESS CENTRALITY
def closenessCentrality(G):
    und_close = nx.closeness_centrality(G)
    return und_close

#BETWEENNESS CENTRALITY
def betweennesCentrality(G):
    und_between = nx.betweenness_centrality(G)
    return und_between

#EIGENVECTOR CENTRALITY
def eigenvectorCentrality(G):
    und_eigen = nx.eigenvector_centrality(G)
    return und_eigen

def clusteringCoefficient(G):
    return nx.clustering(G)

graph_types = ["entities","mentions","tags"]

for t in graph_types:

    print("type:",t)
    tweets = RetrieveTweets_schedule.getTweetDF(option="thisweek")
    conc = createUDWnetork(tweets,graph_content=t)
    conc_edges,conc_weights = zip(*nx.get_edge_attributes(conc,'weight').items())
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
    
    del_query = 'DELETE FROM concurrency_adjacency where type=\'%s\''%(t)
    print(del_query)
    cur = conn.cursor()
    cur.execute(del_query)  
    conn.commit()
    
    # Adjacency Matrix
    values = []
    for i in range(len(conc_edges)):
        (source,destination) = conc_edges[i]
        value = '(\'%s\',\'%s\',%d,\'%s\')' %(source.replace('\'','\'\''),destination.replace('\'','\'\''), conc_weights[i],t)
        values.append(value)
    values_str = ','.join(values)
    query_adj = 'INSERT INTO concurrency_adjacency (source , destination, weight,type) VALUES %s RETURNING source' %(values_str)
    print(query_adj)
    cur = conn.cursor()
    cur.execute(query_adj)  
    output = cur.fetchone()    
    conn.commit() 
    cur.close()
    
    print("graph ok")
    
    degree_cent = degreeCentrality(conc)
    print("degree ok")
    closeness_cent = closenessCentrality(conc)
    print("close ok")
    betweenness_cent = betweennesCentrality(conc)
    print("between ok")
    
    try:
        eigenvector_cent = eigenvectorCentrality(conc)
        print("eigen ok")
    except:
        print("eigen error")
        eigenvector_cent = []
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
    del_query = 'DELETE FROM concurrency_indices where type=\'%s\''%(t)
    print(del_query)
    cur = conn.cursor()
    cur.execute(del_query)  
    conn.commit()

    # Degree Centrality
    values = []
    for node in degree_cent.keys():
        degree = degree_cent[node]
        value = '(\'%s\',%f,\'%s\')' %(node.replace('\'','\'\''), degree,t)
        values.append(value)
    values_str = ','.join(values)
    query_degree = 'INSERT INTO concurrency_indices (node , degree_centrality,type) VALUES %s RETURNING node' %(values_str)
    print(query_degree)
    cur = conn.cursor()
    cur.execute(query_degree)  
    output = cur.fetchone()    
    conn.commit() 
    cur.close()

    # Betweenness Centrality
    conn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
    values = [] 
    for node in betweenness_cent.keys():
        between = betweenness_cent[node]
        value = '(\'%s\',%f,\'%s\')' %(node.replace('\'','\'\''), between,t)
        values.append(value)
    values_str = ','.join(values)
    query_between = 'INSERT INTO concurrency_indices (node , betweenness_centrality,type) VALUES %s RETURNING node' %(values_str)
    print(query_between)
    cur = conn.cursor()
    cur.execute(query_between)  
    output = cur.fetchone()    
    conn.commit() 
    cur.close()

    #Closeness Centrality
    conn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
    values = []
    for node in closeness_cent.keys():
        close = closeness_cent[node]
        value = '(\'%s\',%f,\'%s\')' %(node.replace('\'','\'\''), close,t)
        values.append(value)
    values_str = ','.join(values)
    query_closeness = 'INSERT INTO concurrency_indices (node , closeness_centrality,type) VALUES %s RETURNING node' %(values_str)
    print(query_closeness)
    cur = conn.cursor()
    cur.execute(query_closeness)  
    output = cur.fetchone()    
    conn.commit() 
    cur.close()

    #Eigenvector Centrality
    conn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
    values = []
    if eigenvector_cent != []:
        for node in eigenvector_cent.keys():
            eigen = eigenvector_cent[node]
            value = '(\'%s\',%f,\'%s\')' %(node.replace('\'','\'\''), eigen,t)
            values.append(value)
        values_str = ','.join(values)
        query_eigen = 'INSERT INTO concurrency_indices (node , eigenvector_centrality,type) VALUES %s RETURNING node' %(values_str)
        print(query_eigen)
        cur = conn.cursor()
        cur.execute(query_eigen)  
        output = cur.fetchone()    
        conn.commit()
    cur.close()
    
