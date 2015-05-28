# -*- coding: utf-8 -*-

#!/usr/bin/env python
"""
Experiments from "Interbank Lending and the Spread of 
Bank Failures: A Network Model of Systemic Risk"
"""

__author__="""Marco Tinacci (marco.tinacci@gmail.com)"""

# file imports
import Network as net
import Test
import Plot
import Contagion

# imports
import random as rnd
import networkx as nx
import numpy as np

## TODO
# contagio
#   campo BANKRUPT con valori None default o failure per distinguerli nel plot
# hist size frequenza
# hist degree frequenza
# classi
# togliere sovrapposizione nodi    

if __name__ == '__main__':
    
#%% GLOBAL PARAMS SIMULATION
    # random seed
    # SEED = int(time.time())
    SEED = 1
    rnd.seed(SEED)
    np.random.seed(SEED)
    # node scale factor
    node_scale = 0.1
    # number of nodes
    N=100
    # power law exponent
    alpha=5

#%% GRAPH INSTANCE    
    # nodes
    nodes = net.initNodes(N,alpha=alpha)
    # undirected edges
    exp_degree = map(lambda x:nodes[x]['ASSET'],nodes.keys())
    exp_degree = exp_degree / max(exp_degree)
    exp_degree = exp_degree * N
    g = nx.expected_degree_graph(exp_degree,selfloops=False)
    for i in g.nodes():
        g.node[i] = nodes[i]
    # convert to digraph
    g = net.Graph2DiGraph(g)
    # weight edges
    g = net.WeightedEdges(g)
    # NOTE: correlations must be checked before the loans update
    Test.correlation(g)
    # update assets
    g = net.UpdateAssets(g)
    g1 = nx.DiGraph(g)
   
   #g1.remove_nodes_from(nx.isolates(g1))

#%% CONTAGION SIMULATION
    g = Contagion.failure(0,g)
    g.remove_nodes_from(nx.isolates(g))
    
#%% PLOTS
    pos = nx.random_layout(g1)
#    pos = nx.circular_layout(g1)

    Plot.plotGraph(g1,alpha,node_scale=node_scale,seed=SEED,pos=pos)
    Plot.plotGraph(g,alpha,node_scale=node_scale,seed=SEED,pos=pos)

    Plot.scatterDegreeSize(g1)





