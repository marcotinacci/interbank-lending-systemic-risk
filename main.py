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
# hist size frequenza
# hist degree frequenza
# classi

if __name__ == '__main__':

#%% GLOBAL PARAMS SIMULATION
    # random seed
    # SEED = int(time.time())
    SEED = 3
    rnd.seed(SEED)
    np.random.seed(SEED)
    # node scale factor
    node_scale = 0.1
    # number of nodes
    N=100
    # power law exponent
    alpha=4
#%% GRAPH INSTANCE    
    # graph
    g = net.initGraph(N,alpha=alpha)
  #  g = net.initGraph(N,alpha=alpha)
    # convert to digraph
    g = net.Graph2DiGraph(g)
    # weight edges
    g = net.WeightedEdges(g)
    # update assets
    g = net.UpdateAssets(g)

    g1 = nx.DiGraph(g)
   
#%% CONTAGION SIMULATION
    Contagion.contagion(0,g)
    #g.remove_nodes_from(nx.isolates(g))
    
#%% PLOTS
#    pos = nx.random_layout(g1)
#    pos = nx.circular_layout(g1)

    pos = nx.graphviz_layout(g1,prog='twopi',root=0)
    Plot.plotGraph(g1,alpha,node_scale=node_scale,seed=SEED,pos=pos)
    Contagion.cleanZeroEdges(g)
    Plot.plotGraph(g,alpha,node_scale=node_scale,seed=SEED,pos=pos)



