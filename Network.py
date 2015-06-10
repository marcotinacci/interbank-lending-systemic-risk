
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
    for i in dg.nodes():
        oL = InterbankBorrowing(dg.node[i]) * dg.node[i]['ASSET'] # old interbank borrowing
        oB = InterbankLoans(dg.node[i]) * dg.node[i]['ASSET'] # old interbank loans
        nL = 0 # new interbank borrowing
        nB = 0 # new interbank loans
        for j in dg.nodes():
            # new IB loans
            if j in dg.neighbors(i):
                nB = nB + dg[i][j]['weight']
            # new IB borrowing
            if i in dg.neighbors(j):
                nL = nL + dg[j][i]['weight']
        # new node information
        oA = dg.node[i]['ASSET'] # old asset
        dg.node[i]['ASSET'] = max( 
            nB + dg.node[i]['CASH']*dg.node[i]['ASSET'] + dg.node[i]['LOANS']*dg.node[i]['ASSET'],
            nL + dg.node[i]['EQUITY']*dg.node[i]['ASSET'] + dg.node[i]['DEPOSITS']*dg.node[i]['ASSET'])
        nA = dg.node[i]['ASSET'] # new asset
        #print 'oL:',oL,' nL:',nL
        dg.node[i]['CASH'] = dg.node[i]['CASH'] * (oA/nA) * (nA - nB) / (oA - oB)
        dg.node[i]['LOANS'] = dg.node[i]['LOANS'] * (oA/nA) * (nA - nB) / (oA - oB)
        dg.node[i]['DEPOSITS'] = dg.node[i]['DEPOSITS'] * (oA/nA) * (nA - nL) / (oA - oL)
        dg.node[i]['EQUITY'] = dg.node[i]['EQUITY'] * (oA/nA) * (nA - nL) / (oA - oL)
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

def initGraph(N,alpha=None):
    """
    Init graph, assets are drawn from a power law distribution, 
    other information are chosen at random in ranged specified in the paper
        N: number of nodes
        alpha: power law exponent, if None is drawn at random in [1.5,5.0]
        returns: list of nodes information sorted by decreasing assets
    """
#    print ('# INIT GRAPH')
    nodes = {}
    if alpha == None:
        alpha = np.random.uniform(1.5,5)
#    print ('alpha:',alpha)
    sample = Statistics.powerlaw_sample(100, 10**10, alpha,N)
    for i in range(N):
        equity = np.random.uniform(0, 0.25)
        cash = np.random.uniform(0, 0.25)
        # node information
        nodes[i] = {
            'ASSET': sample[i],
            'EQUITY': equity,
            'DEPOSITS': np.random.uniform(0,1-equity),
            'CASH': cash,
            'LOANS': np.random.uniform(0, 1-cash),
            # 0: False, 1: default, 2: failure, 3: exogenous
            'BANKRUPT': 0 
        }
    # sorting
    sort = sorted(nodes.values(), key=lambda n: n['ASSET'], reverse=True)
    # nodes as dictionary
    nodes = {i: sort[i] for i in range(len(sort))}
    
    # undirected edges
    exp_degree = map(lambda x:nodes[x]['ASSET'],nodes.keys())
    exp_degree = exp_degree / max(exp_degree)
    exp_degree = exp_degree * N
    g = nx.expected_degree_graph(exp_degree,selfloops=False)
    for i in g.nodes():
        g.node[i] = nodes[i]
    return g

def initGraphByClass(N,nc,alpha=None):
    """
    Init graph, assets are drawn from a power law distribution, 
    other information are chosen at random in ranged specified in the paper
        N: number of nodes
        alpha: power law exponent, if None is drawn at random in [1.5,5.0]
        returns: list of nodes information sorted by decreasing assets
    """
    nodes = {}
    if alpha == None:
        alpha = np.random.uniform(1.5,5)
    sample = Statistics.powerlaw_sample(100, 10**10, alpha,N)
    inf = 0.25
    sup = 1
    steps = (sup-inf)/nc
    points = drange(inf,sup,steps)
    for i in range(N):
        equity = np.random.uniform(0, 0.25)
        cash = np.random.uniform(points[i%nc]-steps, points[i%nc])
        # node information
        nodes[i] = {
            'ASSET': sample[i],
            'EQUITY': equity,
            'DEPOSITS': np.random.uniform(0,1-equity),
            'CASH': cash,
            'LOANS': np.random.uniform(0, 1-cash),
            # 0: False, 1: default, 2: failure, 3: exogenous
            'BANKRUPT': 0 
        }      
    # sorting
    sort = sorted(nodes.values(), key=lambda n: n['ASSET'], reverse=True)
    # nodes as dictionary
    nodes = {i: sort[i] for i in range(len(sort))}
    
    # undirected edges
    exp_degree = map(lambda x:nodes[x]['ASSET'],nodes.keys())
    exp_degree = exp_degree / max(exp_degree)
    exp_degree = exp_degree * N
    g = nx.expected_degree_graph(exp_degree,selfloops=False)
    # remove cycles
    #g = nx.bfs_tree(g,0)
    for i in g.nodes():
        g.node[i] = nodes[i]
    return g

def drange(start, stop, step):
    r = start
    l=[]
    while r < stop:
        l.append(r)
        r += step
    return l
