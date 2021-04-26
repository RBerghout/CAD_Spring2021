import networkx as nx
import random
import sys
size=int(sys.argv[-1])
name=str(sys.argv[-2])
G=nx.gnp_random_graph(size,0.5,directed=True, seed=random.seed())
DAG = nx.DiGraph([(u,v,{'weight':random.randint(1,10)}) for (u,v) in G.edges() if u<v])
print(list(DAG))
print(list(DAG.edges(data=True)))
leaf = ([x for x in DAG.nodes() if DAG.out_degree(x)==0 and DAG.in_degree(x)!=0])
print(len(leaf))
for ln in leaf:
    G.add_edge(ln, 10+1, weight=random.randint(1,10))
leaf = ([x for x in G.nodes() if G.out_degree(x)==0 and G.in_degree(x)!=0])
print(len(leaf))
nx.write_edgelist(DAG, name, data=["weight"])
import matplotlib.pyplot as plt
#pos = nx.spring_layout(G)
#nx.draw_networkx(G, node_color ='green', pos=nx.spectral_layout(G))
#plt.show()
