#!/usr/bin/env python

# file imports
import Network as net
import Plot
import Contagion
import Measures

# imports
import random as rnd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    
#%% GLOBAL PARAMS SIMULATION
    # random seed
    # SEED = int(time.time())
    SEED = None
    rnd.seed(SEED)
    np.random.seed(SEED)
    # node scale factor
    node_scale = 0.1
    # number of nodes
    N=200
    # power law exponent
    alpha=4
    avg = []
    niter = 20
    nrep = 20
    for i in range(0,niter):
#%% GRAPH INSTANCE
        ff = []
        for it in range(nrep):
            # graph
            g = net.initGraphMod(N,i,niter,alpha=alpha)
            copy = nx.DiGraph(g)
            # convert to digraph
            g = net.Graph2DiGraph(g)
            # weight edges
            g = net.WeightedEdges(g)
            # update assets
            g = net.UpdateAssets(g)
       
            Contagion.contagion(0,g)
        
    #%% PLOTS
            ff.append(Measures.fractionFailing(g))
            #print 'FF:', ff[len(ff)-1],
    #        print 'degree:',nx.degree_centrality(copy)
    #        print 'closeness:',nx.closeness_centrality(copy)
    #        print 'betweeness:',nx.betweenness_centrality(copy)
#            pos = nx.circular_layout(g)
#            Plot.plotGraph(g,alpha,node_scale=node_scale,seed=SEED,pos=pos)
        avg.append(sum(ff) / len(ff))
        print avg[len(avg)-1],',',

    plt.plot(avg,'g-o')
