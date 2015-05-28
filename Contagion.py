# -*- coding: utf-8 -*-
"""
Created on Thu May 21 15:36:38 2015

@author: Marco Tinacci
"""
import Network
import networkx as nx

# CONTAGION PARAMS
RECOVERY_RATE = 1

def contagion(dg,init):
    '''
    Update the state of the network after an initial shock given by the 
    bankrupt of the 'init' node, the details are described inside the paper
        dg: digraph of banks
        init: initial bankrupt node
        returns: updated digraph after the shock
    '''
    dg = nx.DiGraph()
    failure(init,dg)        
    return dg

def failure(b,dg):
    '''
    Failure procedure
        b: liquidated bank
        dg: bank network
    '''
    #print 'failure:',b
    dg.node[b]['BANKRUPT'] = True
    windup(b,dg)
    #repay(b,dg)
    dg.node[b]['EQUITY'] = 0
    dg.node[b]['CASH'] = 0
    return dg

def windup(b,dg):
    #print 'windup:',b
    creditors = dg.adjacency_list()[b]
    # call in interbank loans
    for c in filter(lambda x: not checkBankrupt(x,dg),creditors):
        callInLoan(b,c,dg)
    # call in loans to customers
    loss = (1 - RECOVERY_RATE) * dg.node[b]['LOANS']
    if loss <= dg.node[b]['EQUITY']:
        dg.node[b]['DEPOSITS'] = dg.node[b]['DEPOSITS'] / (1-loss)
        dg.node[b]['EQUITY'] = (dg.node[b]['EQUITY'] - loss) / (1-loss)
    elif loss <= 1 - dg.node[b]['DEPOSITS']:
        dg.node[b]['DEPOSITS'] = dg.node[b]['DEPOSITS'] / (1-loss)
        dg.node[b]['EQUITY'] = 0
    else:
        dg.node[b]['DEPOSITS'] = 1
        dg.node[b]['EQUITY'] = 0

def checkBankrupt(x,dg):
    return dg.node[x]['BANKRUPT']
    #return dg.node[x]['EQUITY'] == 0 or dg.node[x]['CASH'] == 0

def repay(b,dg):
    debtors = []
    for i in dg.nodes():
        if b in dg.adjacency_list()[i]:
            debtors.append(i)
    # total debit
    total_debit = reduce(lambda x,y:x+y, map(lambda z:dg[z][b]['weight'],debtors))
    if total_debit <= Network.InterbankBorrowing(dg.node[b])*dg.node[b]['ASSET']:
        # the debit can be completely repaid
        # repay, no loss for creditors
        dg.node[b]['ASSET'] = dg.node[b]['ASSET'] - total_debit
        # adjust creditors' balance
        reduce(lambda x,y:x+y, map(lambda z: Network.InterbankLoans(dg.node[z]) 
            * dg[b][z]['weight'] * dg.node[z]['ASSET'], debtors))      
        
    else:
        # the debit cannot be completely repaid
        # number of debtors
        dg.in_degree(b)
        # 

def callInLoan(d,c,dg):
    '''
    Call in a loan from a bank:
        d: debtor
        c: creditor
        dg: bank network
    '''
    #print 'call in loan:',d,c
    loan = dg[d][c]['weight']
    old_asset = dg.node[c]['ASSET']
    if dg.node[c]['CASH'] * old_asset - loan < 0:
        # bankrupt by failure mechanism
        failure(c,dg)
    else:
        # debtor: move loan to cash
        dg.node[d]['CASH'] = dg.node[d]['CASH'] + loan / dg.node[d]['ASSET']
        # creditor: update balance
        dg.node[c]['ASSET'] = old_asset - loan
        dg.node[c]['CASH'] = (dg.node[c]['CASH'] * old_asset - loan) / (old_asset - loan)
        dg.node[c]['LOANS'] = (dg.node[c]['LOANS'] * old_asset) / (old_asset - loan)
        dg.node[c]['DEPOSITS'] = (dg.node[c]['DEPOSITS'] * old_asset) / (old_asset - loan)
        dg.node[c]['EQUITY'] = (dg.node[c]['EQUITY'] * old_asset) / (old_asset - loan)
        # remove loan edge
        dg.remove_edge(d,c)
    
    
    
    
    