# -*- coding: utf-8 -*-

#!/usr/bin/env python
"""
Experiments from "Interbank Lending and the Spread of 
Bank Failures: A Network Model of Systemic Risk"
"""

import SystemGraph as sg
import random as rnd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import time
import Tests

__author__="""Marco Tinacci (marco.tinacci@gmail.com)"""

if __name__ == '__main__':
    
#%% GLOBAL PARAMS SIMULATION
    # random seed
    SEED = int(time.time())
    rnd.seed(SEED)
    np.random.seed(SEED)
    # node scale factor
    node_scale = 0.05

#%% GRAPH INSTANCE    
    # nodes
    N = 500
    nodes = sg.initNodes(N,alpha=2.5)
    # undirected edges
    exp_degree = map(lambda x:nodes[x]['ASSET'],nodes.keys())
    exp_degree = exp_degree / max(exp_degree)
    exp_degree = exp_degree * N
    g = nx.expected_degree_graph(exp_degree)
    for i in g.nodes():
        g.node[i] = nodes[i]
    # convert to digraph
    g = sg.Graph2DiGraph(g)
    # weight edges
    g = sg.WeightedEdges(g)
    # note: correlations must be checked before the loans update
    Tests.correlation(g)
    # update assets
    g = sg.UpdateAssets(g)

    Tests.correlation(g)
#%% DRAW GRAPH
    # layout
    #pos = nx.circular_layout(g)
    pos = nx.random_layout(g)
    # draw nodes
    nx.draw_networkx_nodes(g,pos,
        nodelist = g.nodes(),
        node_size = [node_scale*g.node[k]['ASSET'] for k in g.nodes()],
        node_color = [node_scale*g.node[k]['ASSET'] for k in g.nodes()],
        cmap = plt.cm.Blues)
    # draw edges
    edges,weights = zip(*nx.get_edge_attributes(g,'weight').items())
    nx.draw_networkx_edges(g, pos,
        edge_color = weights,
        width=0.5,
        edge_cmap = plt.cm.Blues,
        arrows=False)
    # plot graph
    nx.write_gml(g,'output_graphs/graph'+str(SEED)+'.gml')
    plt.savefig('output_graphs/graph'+str(SEED)+'.png')
    plt.show()

#%% PLOT DEGREE/SIZE
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    ax2.scatter(map(lambda x:g.degree(x),g.nodes()),map(lambda y:y['ASSET'],g.node.values()))

# contagio
# hist size frequenza
# hist degree frequenza
# classi: 
# togliere sovrapposizione nodi