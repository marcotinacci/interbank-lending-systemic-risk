#!/usr/bin/env python

def fractionFailing(dg):
    return len(filter(lambda x:dg.node[x]['BANKRUPT'] > 0,dg.nodes())) / float(len(dg))
