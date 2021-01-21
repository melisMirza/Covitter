import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd 
import Analyzer, RetrieveTweets
import psycopg2, os


def formatDate(origDate):
    date = origDate
    if origDate.strip() != "":
        dl = origDate.split('/')
        day = [lambda:str(dl[1]),lambda:'0'+str(dl[1])][len(str(dl[1])) == 1]()
        month = [lambda:str(dl[0]),lambda:'0'+str(dl[0])][len(str(dl[0])) == 1]()
        date = str(dl[2]) + month + day
    return date


#creates undirected, unweighted graph
def createUDWnetork(tweets):
    G = nx.Graph()
    tweetDF = tweets[['mentions','entities']]
    tweetDict = tweetDF.to_dict('index')
    entityDict = {}
    allEntities = []
    #Convert mentions to entities
    for t in tweetDict.keys():
        entities = []
        if "str" in str(type(tweetDict[t]["entities"])):
            entities = tweetDict[t]["entities"].split('||')
            tweetDict[t]["entities"] = entities
        allEntities += tweetDict[t]["entities"]
        for ent in tweetDict[t]["entities"]:
            if ent != "":
                if ent.strip() not in entityDict.keys():
                    entityDict[ent] = [t]
                else:
                    entityDict[ent].append(t)
    allEntities = list(set(allEntities))
    allEntities.remove("")
    for e in allEntities:
        #print("Node:",e)
        G.add_node(e.strip())
    
    for i in allEntities:
        e1 = entityDict[i] #tweet indeces including this entity
        #print("e1:",e1)
        for j in allEntities:
            if i != j:
                e2 = entityDict[j] #compare against other entities
                #print("e2:",e2)
                intersection_list = list(set(e1).intersection(e2))
                print(i,"-",j,":",len(intersection_list))
                #print("intersection:",intersection_list)
                if len(intersection_list) > 0:
                    G.add_edge(i,j,weight=len(intersection_list))
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

tweets = RetrieveTweets.getTweetDF(option="thisweek_all")
conc = createUDWnetork(tweets)
conc_edges,conc_weights = zip(*nx.get_edge_attributes(conc,'weight').items())

conn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
'''
for i in range(len(conc_edges)):
    (source,destination) = conc_edges[i]
    query_adj = 'INSERT INTO concurrency_adjacency (source , destination, weight) VALUES (\'%s\',\'%s\',%d) RETURNING source' %(source,destination, conc_weights[i])
    print(query_adj)
    cur = conn.cursor()
    cur.execute(query_adj)  
    output = cur.fetchone()    
    conn.commit() 
cur.close()
'''
'''
degree_cent = degreeCentrality(conc)
closeness_cent = closenessCentrality(conc)
betweenness_cent = betweennesCentrality(conc)
eigenvector_cent = eigenvectorCentrality(conc)
clustring_coef = clusteringCoefficient(conc)

for node in degree_cent.keys():
    degree = degree_cent[node]
    query_degree = 'INSERT INTO concurrency_indices (node , degree_centrality) VALUES (\'%s\',%f) RETURNING node' %(node, degree)
    print(query_degree)
    cur = conn.cursor()
    cur.execute(query_degree)  
    output = cur.fetchone()    
    conn.commit() 
cur.close()

for node in betweenness_cent.keys():
    between = betweenness_cent[node]
    query_between = 'INSERT INTO concurrency_indices (node , betweenness_centrality) VALUES (\'%s\',%f) RETURNING node' %(node, between)
    print(query_between)
    cur = conn.cursor()
    cur.execute(query_between)  
    output = cur.fetchone()    
    conn.commit() 
cur.close()

for node in closeness_cent.keys():
    close = closeness_cent[node]
    query_closeness = 'INSERT INTO concurrency_indices (node , closeness_centrality) VALUES (\'%s\',%f) RETURNING node' %(node, close)
    print(query_closeness)
    cur = conn.cursor()
    cur.execute(query_closeness)  
    output = cur.fetchone()    
    conn.commit() 
cur.close()

for node in eigenvector_cent.keys():
    eigen = eigenvector_cent[node]
    query_eigen = 'INSERT INTO concurrency_indices (node , eigenvector_centrality) VALUES (\'%s\',%f) RETURNING node' %(node, eigen)
    print(query_eigen)
    cur = conn.cursor()
    cur.execute(query_eigen)  
    output = cur.fetchone()    
    conn.commit() 
cur.close()
'''
clustring_coef = clusteringCoefficient(conc)

for node in clustring_coef.keys():
    coef = clustring_coef[node]
    query_coef = 'INSERT INTO concurrency_indices (node , clustering_coefficient) VALUES (\'%s\',%f) RETURNING node' %(node, coef)
    print(query_coef)
    cur = conn.cursor()
    cur.execute(query_coef)  
    output = cur.fetchone()    
    conn.commit() 
cur.close()
