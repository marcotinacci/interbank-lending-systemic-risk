# -*- coding: utf-8 -*-
"""
Created on Thu May 21 12:12:21 2015

@author: Marco Tinacci
"""

import numpy as np

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

    print 'corr(assets,degree) =',np.corrcoef(assets,degrees)[0,1]
    print 'corr(assets,out degree) =',np.corrcoef(assets,out_degrees)[0,1]
    print 'corr(assets,in degree) =',np.corrcoef(assets,in_degrees)[0,1]