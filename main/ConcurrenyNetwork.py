import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd 
#from . import Analyzer, RetrieveTweets
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


def collectIndices(graph_type):
    indices = {"eigenvector":[],"degree":[],"betweenness":[],"closeness":[],"clustering":[]}
    nodes = []
    dbconn = psycopg2.connect(os.environ['DATABASE_URL'],sslmode='require')
    cur = dbconn.cursor()
    query = 'SELECT node,eigenvector_centrality FROM concurrency_indices WHERE eigenvector_centrality is not null AND type = \'%s\' ORDER BY eigenvector_centrality DESC LIMIT 10'%(graph_type)
    cur.execute(query)  
    eigen = cur.fetchall()
    for r in eigen:
        nodes.append(r[0])
        indices["eigenvector"].append(list(r))
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
    query = 'SELECT node,clustering_coefficient FROM concurrency_indices WHERE clustering_coefficient is not null AND type = \'%s\' ORDER BY clustering_coefficient DESC LIMIT 10'%(graph_type)
    cur.execute(query)  
    clustering = cur.fetchall()
    for r in clustering:
        nodes.append(r[0])
        indices["clustering"].append(list(r))
    dbconn.commit() 

    nodes = list(set(nodes))
    neighbourhood = {}
    print("total", len(nodes), "nodes")
    for n in nodes:
        combined = []
        query = 'SELECT destination,weight FROM concurrency_adjacency WHERE source = \'%s\' AND type = \'%s\' ORDER BY weight DESC LIMIT 5' %(n,graph_type)
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
    print(query)
    cur.execute(query)  
    adj = cur.fetchall()
    indices["adjacency"]=[]
    for r in adj:
        indices["adjacency"].append(list(r))
    print("************************************")
    print(indices["adjacency"])
    print("************************************")

    dbconn.commit()    
    cur.close() 
    return indices
        




'''
#creates directed, weighted graph
def createWDnetork(bloggers,posts,alpha=0.01):
        
    weights = {}
    #pi = []
    blgrs = bloggers.keys()
    for b in blgrs:
        weights[b] = {}
        weights[b]["dests"] = {}
        weights[b]["cumulative"] = 0.0
        for i in blgrs:
            weights[b]["dests"][i] = {"indices":[]}#, "sum" :0}
    
    for p in posts.keys():
        dest = posts[p].blogger
        sources = posts[p].links
        comments = posts[p].comments
        postindex = 1 + alpha*int(comments)
        #print("post index", postindex)

        for s in sources:
            weights[s]["dests"][dest]["indices"].append(postindex)
    for u in weights.keys():
        cum = 0
        for v in weights[u]["dests"].keys():
            weights[u]["dests"][v]["sum"] = sum(weights[u]["dests"][v]["indices"])
        for v2 in weights[u]["dests"].keys():
            weights[u]["cumulative"] += weights[u]["dests"][v2]["sum"]

    G = nx.DiGraph()
    for bg in bloggers.keys():
        G.add_node(bg)
    for b in bloggers.keys():
        for p in bloggers[b].posts:
            for l in p.links:
                if b != l:
                    edgeWeight = weights[l]["dests"][b]["sum"] / weights[l]["cumulative"]
                    #print(l,"-->",b,"weight:",edgeWeight)
                    #pi.append(str(edgeWeight))
                    G.add_edge(l,b,weight=edgeWeight)

    return G


(b,p) = processData()
print(len(p.keys()))
Gd = createDUWnetork(b, p)
#print(Gd.edges())
#print("nodesD:",len(Gd.nodes()))
#print("edgesD:",len(Gd.edges()))

Gu = createUDUWnetork(b, p)
#print(G.edges())
#print("nodes:",len(Gu.nodes()))
#print("edges:",len(Gu.edges()))

Gw = createWDnetork(b, p)


#DEGREE CENTRALITY
und_degree = nx.degree_centrality(Gu)
d_degree = nx.in_degree_centrality(Gd)
dw_degree = nx.in_degree_centrality(Gw)
print("Blog ID|Blogger Name|Undirected|Directed|Weighted")
for blg in und_degree.keys():
    print(blg,"|",b[blg].name,"|",und_degree[blg],"|",d_degree[blg],"|",dw_degree[blg])


#EIGENVECTOR CENTRALITY
und_eigen = nx.eigenvector_centrality(Gu)
d_eigen = nx.eigenvector_centrality(Gd)
dw_eigen = nx.eigenvector_centrality(Gw)
print("Blog ID|Blogger Name|Undirected|Directed|Weighted")
for blg in und_eigen.keys():
    print(blg,"|",b[blg].name,"|",und_eigen[blg],"|",d_eigen[blg],"|",dw_eigen[blg])


#KATZ CENTRALITY -- doesnt converge
#und_katz = nx.katz_centrality(Gu)
d_katz = nx.katz_centrality(Gd, alpha=0.1, beta=1.0,max_iter=100000)
print("Blog|Undirected|Directed")
for blg in und_katz.keys():
    print(blg,"|",b[blg].name,"|","X","|",d_katz[blg])


#PAGERANK
und_page = nx.pagerank(Gu,0.85,weight=None),
d_page = nx.pagerank(Gd,0.85,weight=None)#, alpha=0.1, beta=1.0,max_iter=100000)
dw_page = nx.pagerank(Gw,0.85,weight="weight")#, alpha=0.1, beta=1.0,max_iter=100000)
print("Blog ID|Blogger Name|Undirected|Directed|Weighted")
(und_page_dict,) = und_page 
for blg in und_page_dict.keys():
    print(blg,"|",b[blg].name,"|",und_page_dict[blg],"|",d_page[blg],"|",dw_page[blg])


#CLOSENESS CENTRALITY
und_close = nx.closeness_centrality(Gu)
d_close = nx.closeness_centrality(Gd)
dw_close = nx.closeness_centrality(Gw)
print("Blog ID|Blogger Name|Undirected|Directed|Weighted")
for blg in und_close.keys():
    print(blg,"|",b[blg].name,"|",und_close[blg],"|",d_close[blg],"|",dw_close[blg])



#BETWEENNESS CENTRALITY
und_btw = nx.betweenness_centrality(Gu)
d_btw = nx.betweenness_centrality(Gd)
dw_btw = nx.betweenness_centrality(Gw)
print("Blog ID|Blogger Name|Undirected|Directed|Weighted")
for blg in und_btw.keys():
    print(blg,"|",b[blg].name,"|",und_btw[blg],"|",d_btw[blg],"|",dw_btw[blg])


#HUBS AND AUTHORITIES
(hubs, authorities) = nx.hits(Gw, normalized = True)
print(hubs)
print(authorities)
print("Blog ID|Blogger Name|Hubs|Authorities")
for blg in hubs.keys():
    print(blg,"|",b[blg].name,"|",hubs[blg],"|",authorities[blg])


##K-SHELL DECOMP
dw_kshell = nx.core_number(Gw)
kmax = 0
print(len(list(set(list(dw_kshell.values())))))
for k in dw_kshell.keys():
    kmax = [lambda:kmax, lambda:dw_kshell[k]][dw_kshell[k] > kmax]()
    if dw_kshell[k] == 17:
        print(k)
print("kmax:",kmax)

##K-shell plot
k_vals = list(sorted(list(dw_kshell.values())))
ic = []
for i in k_vals:
    ic.append(k_vals.count(i))
plt.plot(k_vals,ic,'ro-') # in-degree
plt.xlabel('k-shell')
plt.ylabel('Number of vertices')
plt.show()


##PLOTS
pos = nx.layout.spring_layout(Gw)
print(Gw.edges())
node_sizes = []
for i in dw_degree.keys():
    node_sizes.append(dw_degree[i]*3000 + 30)
#M = Gw.number_of_edges()
#edge_colors = range(2, M + 2)
edges,weights = zip(*nx.get_edge_attributes(Gw,'weight').items())

nColor = []
top5 = ["1","3","5","4","6"]
for n in Gw.nodes():
    if n in top5:
        nColor.append("#891428")
    else:
        nColor.append("#1A6164")


nodes = nx.draw_networkx_nodes(Gw, pos, nodes = Gw.nodes(), node_color="#1A6164" ,node_size=400,alpha=0.9)
edges = nx.draw_networkx_edges(Gw, pos, arrowstyle='->', edgelist = edges,
                               arrowsize=10, edge_color='#171E66',
                               edge_cmap=plt.cm.Blues, width=2,alpha=0.4)
plt.show()


nodes = nx.draw_networkx_nodes(Gw, pos, nodes = Gw.nodes(), node_color="#1A6164" ,node_size=node_sizes,alpha=0.9)
edges = nx.draw_networkx_edges(Gw, pos, arrowstyle='->', edgelist = edges,
                               arrowsize=10, edge_color='#171E66',
                               edge_cmap=plt.cm.Blues, width=2,alpha=0.4)
plt.show()


nodes = nx.draw_networkx_nodes(Gw, pos, nodes = Gw.nodes(), node_color=nColor ,node_size=node_sizes,alpha=0.9)
edges = nx.draw_networkx_edges(Gw, pos, arrowstyle='->', edgelist = edges,
                               arrowsize=10, edge_color='#171E66',
                               edge_cmap=plt.cm.Blues, width=2,alpha=0.4)
plt.show() 



###IN vs OUT
ins = {}
outs = {}

for n in Gw.nodes():
    ins[n] = Gw.in_degree(n)
    outs[n] = Gw.out_degree(n)
i_vals = list(sorted(list(ins.values())))
o_vals = list(sorted(list(outs.values())))

ic = []
oc = []

for i in i_vals:
    ic.append(i_vals.count(i))

for j in o_vals:
    oc.append(o_vals.count(j))

plt.plot(i_vals,ic,'ro-') # in-degree
plt.plot(o_vals,oc,'bv-') # out-degree
plt.legend(['In-degree','Out-degree'])
plt.xlabel('Degree')
plt.ylabel('Number of vertices')
plt.show()

'''
