# -*- coding: utf-8 -*-
"""
Created on Thu May 21 12:12:21 2015

@author: Marco Tinacci
"""

import numpy as np
import Network as net
import networkx as nx

def correlation(dg):
    '''
    Tests the correlation between total assets and degrees (in, out and sum of 
    both)
        dg: digraph with node assets
        prints: correlations between (assets,degrees), (assets,in degrees) and
            (assets,out degrees)
    '''

    assets = []
    degrees = []
    out_degrees = []
    in_degrees = []
    for i in dg.nodes():
        assets.append(dg.node[i]['ASSET'])
        degrees.append(dg.degree(i)) 
        out_degrees.append(dg.out_degree(i)) 
        in_degrees.append(dg.in_degree(i)) 

    print '-> TEST: correlation'
    print 'corr(assets,degree) =',np.corrcoef(assets,degrees)[0,1]
    print 'corr(assets,out degree) =',np.corrcoef(assets,out_degrees)[0,1]
    print 'corr(assets,in degree) =',np.corrcoef(assets,in_degrees)[0,1]
    print '-> END TEST: correlation'

def globalAsset(g):
    print '-> TEST: global asset'
    dg = nx.DiGraph(g) # copy
    net.UpdateAssets(dg)
    print 'global asset before update:',reduce(lambda x,y:x+y, map(lambda z:z['ASSET'],g.node.values()))
    print 'global asset after update:',reduce(lambda x,y:x+y, map(lambda z:z['ASSET'],dg.node.values()))
    print '-> END TEST: global asset'    

def interbanking(g):
    print '-> TEST: interbanking'
    r = nx.DiGraph.reverse(g)
    for i in g.nodes():
        if g[i]:
            print i,'edges:',reduce(lambda x,y:x+y, map(lambda z:z['weight'],g[i].values())),' IBL:',g.node[i]['ASSET'] * net.InterbankLoans(g.node[i])
        else:
            print i, 'has no neighbors'
        if r[i]:
            print i,'coedges',reduce(lambda x,y:x+y, map(lambda z:z['weight'],r[i].values())),' IBB:',g.node[i]['ASSET'] * net.InterbankBorrowing(g.node[i])
        else:
            print i, 'is not a neighbor'
    print '-> END TEST: interbanking'

def failedBankIsolated(g):
    r = nx.DiGraph.reverse(g)
    print '-> TEST: failed bank isolated'
    print 'Failed and still connected banks:',filter(lambda x: g.node[x]['BANKRUPT'] > 0 and (g.neighbors(x) or
 r.neighbors(x)), g.nodes())
    print '-> END TEST: failed bank isolated'