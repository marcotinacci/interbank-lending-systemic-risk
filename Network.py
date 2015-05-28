
import networkx as nx
import numpy as np
import random

import Statistics

def WeightedEdges(dg):
    """
    Gives weights to edges as described in the paper
        dg: digraph
        returns: updated digraph
    """
    # interbank loans on edges
    for i, nbrs in dg.adjacency_iter():
        # normalization factor
        norm = 0
        for j in nbrs.keys():
            norm = norm + InterbankBorrowing(dg.node[j]) * dg.node[j]['ASSET']
        # assign weights to edges
        for j in nbrs.keys():
            dg[i][j]['weight'] = InterbankBorrowing(dg.node[j]) * InterbankLoans(dg.node[i]) * dg.node[i]['ASSET'] * dg.node[j]['ASSET'] / norm
    return dg

def UpdateAssets(dg):
    """
    Use weighted edges to flow interbanking loans between banks
        dg: digraph
        returns: updated digraph
    """
    # update assets O(n^2)
    for i,nbrs in dg.adjacency_iter():
        oL = InterbankBorrowing(dg.node[i]) # old interbank borrowing
        oB = InterbankLoans(dg.node[i]) # old interbank loans
        nL = 0 # new interbank borrowing
        nB = 0 # new interbank loans
        for j,jnbrs in dg.adjacency_iter():
            # lent amount
            if j in nbrs.keys():
                nL = nL + dg[i][j]['weight']
            # borrowed amount
            if i in jnbrs.keys():
                nB = nB + dg[j][i]['weight']
        # new node information
        oA = dg.node[i]['ASSET'] # old asset
        dg.node[i]['ASSET'] = max( 
            nB + dg.node[i]['CASH']*dg.node[i]['ASSET'] + dg.node[i]['LOANS']*dg.node[i]['ASSET'],
            nL + dg.node[i]['EQUITY']*dg.node[i]['ASSET'] + dg.node[i]['DEPOSITS']*dg.node[i]['ASSET'])
        nA = dg.node[i]['ASSET'] # new asset
        #print oA,'>',nA
        dg.node[i]['CASH'] = dg.node[i]['CASH'] * (nA - nB) / (oA - oB)
        dg.node[i]['LOANS'] = dg.node[i]['LOANS'] * (nA - nB) / (oA - oB)
        dg.node[i]['DEPOSITS'] = dg.node[i]['DEPOSITS'] * (nA - nL) / (oA - oL)
        dg.node[i]['EQUITY'] = dg.node[i]['EQUITY'] * (nA - nL) / (oA - oL)
    return dg

def InterbankBorrowing(node):
    return 1 - node['EQUITY'] - node['DEPOSITS']

def InterbankLoans(node):
    return 1 - node['CASH'] - node['LOANS']    

def Graph2DiGraph(g):
    """
    Convert a graph to a directed graph chosing a direction at random
        g: graph
        returns: a directed graph
    """
    # directed graph
    dg = nx.DiGraph()
    # copy of nodes
    dg.add_nodes_from(zip(g.node.keys(),g.node.values()))
    # copy and random orientation of edges
    for i,j in g.edges():
        if random.random() < 0.5:
            dg.add_edge(i,j)
        else:
            dg.add_edge(j,i)
    return dg

def initNodes(N,alpha=None):
    """
    Init nodes information, assets are drawn from a power law distribution, 
    other information are chosen at random in ranged specified in the paper
        N: number of nodes
        alpha: power law exponent, if None is drawn at random in [1.5,5.0]
        returns: list of nodes information sorted by decreasing assets
    """
    print ('# INIT NODES')
    nodes = {}
    if alpha == None:
        alpha = np.random.uniform(1.5,5)
    print ('alpha:',alpha)
    sample = Statistics.powerlaw_sample(100, 10**10, alpha,N)
    for i in range(N):
        equity = np.random.uniform(0, 0.25)
        cash = np.random.uniform(0, 0.25)
        # node information
        nodes[i] = {
            'ASSET': sample[i],
            'EQUITY': equity,
            'DEPOSITS': np.random.uniform(0,1 - equity),
            'CASH': cash,
            'LOANS': np.random.uniform(0, 1-cash),
            'BANKRUPT': False
        }
    # sorting
    sort = sorted(nodes.values(), key=lambda n: n['ASSET'], reverse=True)
    return {i: sort[i] for i in range(len(sort))}
