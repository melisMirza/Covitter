import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd 
#from . import Analyzer, RetrieveTweets
import psycopg2, os

#####
# CO-OCCURANCE GRAPH INDICES and ADJACENCY MATRIX
#####

def formatDate(origDate):
    date = origDate
    if origDate.strip() != "":
        dl = origDate.split('/')
        day = [lambda:str(dl[1]),lambda:'0'+str(dl[1])][len(str(dl[1])) == 1]()
        month = [lambda:str(dl[0]),lambda:'0'+str(dl[0])][len(str(dl[0])) == 1]()
        date = str(dl[2]) + month + day
    return date

#creates undirected, unweighted graph
def createUDUWnetork(tweets):
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
    '''
    print("Nodes")
    print(G.nodes())
    print("Edges")
    print(G.edges())
    '''
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

#collects centrality indices of the graph from database, returns dictionary
def collectIndices(graph_type):
    indices = {"eigenvector":[],"degree":[],"betweenness":[],"closeness":[],"clustering":[]}
    nodes = []
    dbconn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
    cur = dbconn.cursor()
    
    try:
        query = 'SELECT node,eigenvector_centrality FROM concurrency_indices WHERE eigenvector_centrality is not null AND type = \'%s\' ORDER BY eigenvector_centrality DESC LIMIT 10'%(graph_type)
        cur.execute(query)  
        eigen = cur.fetchall()
        for r in eigen:
            nodes.append(r[0])
            indices["eigenvector"].append(list(r))
    except:
        indices["eigenvector"].append([])
    
    query = 'SELECT node,degree_centrality FROM concurrency_indices WHERE degree_centrality is not null AND type = \'%s\' ORDER BY degree_centrality DESC LIMIT 10'%(graph_type)
    cur.execute(query)  
    degree = cur.fetchall()
    for r in degree:
        nodes.append(r[0])
        indices["degree"].append(list(r))
    
    query = 'SELECT node,betweenness_centrality FROM concurrency_indices WHERE betweenness_centrality is not null AND type = \'%s\' ORDER BY betweenness_centrality DESC LIMIT 10'%(graph_type)
    cur.execute(query)  
    betweenness = cur.fetchall()
    for r in betweenness:
        nodes.append(r[0])
        indices["betweenness"].append(list(r))
    
    query = 'SELECT node,closeness_centrality FROM concurrency_indices WHERE closeness_centrality is not null AND type = \'%s\' ORDER BY closeness_centrality DESC LIMIT 10'%(graph_type)
    cur.execute(query)  
    closeness = cur.fetchall()
    for r in closeness:
        nodes.append(r[0])
        indices["closeness"].append(list(r))

    #find strongest edges of the node
    nodes = list(set(nodes))
    neighbourhood = {}
    print("total", len(nodes), "nodes")
    for n in nodes:
        combined = []
        n_q = n.replace('\'','\'\'')
        query = 'SELECT destination,weight FROM concurrency_adjacency WHERE source = \'%s\' AND type = \'%s\' ORDER BY weight DESC LIMIT 5' %(n_q,graph_type)
        cur.execute(query)  
        neighbours = cur.fetchall()
        for dest in neighbours:
            strng = dest[0] + " (" + str(dest[1]) + ")"
            combined.append(strng)
        combined = ' | '.join(combined)
        print(combined)
        neighbourhood[n] = combined
    dbconn.commit()    
    
    for index in indices.keys():
        for j in range(len(indices[index])):
            indices[index][j] += [neighbourhood[indices[index][j][0]]]
    
    cur = dbconn.cursor()
    query = 'SELECT source,destination,weight FROM concurrency_adjacency WHERE weight is not null AND type = \'%s\' ORDER BY weight DESC LIMIT 10'%(graph_type)
    cur.execute(query)  
    adj = cur.fetchall()
    indices["adjacency"]=[]
    for r in adj:
        indices["adjacency"].append(list(r))

    dbconn.commit()    
    cur.close() 
    return indices
        
