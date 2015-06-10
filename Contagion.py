import Network

# CONTAGION PARAMS
RECOVERY_RATE = 0.5

def contagion(init,dg):
    dg.node[init]['BANKRUPT'] = 3
    # exogenous failure of initial node
    old_asset = dg.node[init]['ASSET']
    # exogenous loss equal to its equity
    equityLoss = old_asset * dg.node[init]['EQUITY'] #+ dg.node[init]['DEPOSITS'])
    # loss from wind up recovery
    recoveryLoss = old_asset * (1 - RECOVERY_RATE) * dg.node[init]['LOANS']

    loss = equityLoss + recoveryLoss
    windup(init,dg,exLoss=loss)
    repay(init,dg)
    

def windup(b,dg,exLoss=None):
    ''' convert asset to cash and return the loss to apply'''
    # 1. loss from recovery loans
    loss = (1 - RECOVERY_RATE) * dg.node[b]['LOANS'] * dg.node[b]['ASSET']
    if not exLoss == None:
        loss = loss + exLoss
    old_asset = dg.node[b]['ASSET']
    dg.node[b]['ASSET'] = old_asset - loss
    dg.node[b]['CASH'] = (dg.node[b]['CASH'] + RECOVERY_RATE * dg.node[b]['LOANS']) / dg.node[b]['ASSET']
    dg.node[b]['LOANS'] = 0
    if loss <= dg.node[b]['EQUITY'] * old_asset:
        dg.node[b]['DEPOSITS'] = dg.node[b]['DEPOSITS']*old_asset / dg.node[b]['ASSET']
        dg.node[b]['EQUITY'] = (dg.node[b]['EQUITY']*old_asset - loss) / dg.node[b]['ASSET']
    elif loss <= (1 - dg.node[b]['DEPOSITS']) * old_asset:
        dg.node[b]['DEPOSITS'] = dg.node[b]['DEPOSITS'] * old_asset / dg.node[b]['ASSET']
        dg.node[b]['EQUITY'] = 0
    else:
        dg.node[b]['DEPOSITS'] = 1
        dg.node[b]['EQUITY'] = 0

    # 2. call in interbank loans
    creditors = dg.adjacency_list()[b]
    for c in filter(lambda x: not checkBankrupt(x,dg),creditors):
        callInLoan(b,c,dg)

def callInLoan(frm,to,dg):
    ''' call in a loan and return the loss to apply to the debtor d '''
    loan = dg[frm][to]['weight']
    old_asset = dg.node[to]['ASSET']
    if checkBankrupt(to,dg):
        #print 'call in loop',frm,to
        # a loan from a failing bank is completely loss
        loss = loan
        old_asset = dg.node[frm]['ASSET']
        dg.node[frm]['ASSET'] = old_asset - loss
        dg.node[frm]['CASH'] = (dg.node[frm]['CASH']*old_asset-loss) / dg.node[frm]['ASSET']
        if loss <= dg.node[frm]['EQUITY'] * old_asset:
            dg.node[frm]['DEPOSITS'] = dg.node[frm]['DEPOSITS']*old_asset / dg.node[frm]['ASSET']
            dg.node[frm]['EQUITY'] = (dg.node[frm]['EQUITY']*old_asset - loss) / dg.node[frm]['ASSET']
        elif loss <= (1 - dg.node[frm]['DEPOSITS']) * old_asset:
            dg.node[frm]['DEPOSITS'] = dg.node[frm]['DEPOSITS'] * old_asset / dg.node[frm]['ASSET']
            dg.node[frm]['EQUITY'] = 0
        else:
            dg.node[frm]['DEPOSITS'] = 1
            dg.node[frm]['EQUITY'] = 0
        # remove loan edge
#        dg[frm][to]['weight'] = 0
    elif dg.node[to]['CASH'] * old_asset < loan:
        # bankrupt by failure mechanism
        failure(to,2,dg)
    else:
        # from: move loan to cash
        dg.node[frm]['CASH'] = dg.node[frm]['CASH'] + loan / dg.node[frm]['ASSET']
        # to: resane the debt
        dg.node[to]['ASSET'] = old_asset - loan
        dg.node[to]['CASH'] = (dg.node[to]['CASH'] * old_asset - loan) / dg.node[to]['ASSET']
        dg.node[to]['LOANS'] = (dg.node[to]['LOANS'] * old_asset) / dg.node[to]['ASSET']
        dg.node[to]['DEPOSITS'] = (dg.node[to]['DEPOSITS'] * old_asset) / dg.node[to]['ASSET']
        dg.node[to]['EQUITY'] = (dg.node[to]['EQUITY'] * old_asset) / dg.node[to]['ASSET']
        # remove loan edge
        #dg.remove_edge(frm,to)
#        dg[frm][to]['weight'] = 0
    # remove loan edge
    dg[frm][to]['weight'] = 0

def failure(b,failType,dg):
    dg.node[b]['BANKRUPT'] = failType
    windup(b,dg)
    repay(b,dg)

def checkBankrupt(x,dg):
    return dg.node[x]['BANKRUPT'] > 0

def repay(b,dg):
#    print 'repay',b
    debtors = filter(lambda x: (b in dg.adjacency_list()[x]) and not dg[x][b]['weight'] == 0 and not checkBankrupt(x,dg), dg.nodes())
    if not debtors:
        return
    # total debit
    total_debit = reduce(lambda x,y:x+y, map(lambda z:dg[z][b]['weight'],debtors))
    if total_debit <= Network.InterbankBorrowing(dg.node[b])*dg.node[b]['ASSET']:
        # the debit can be completely repaid, no loss for creditors
        dg.node[b]['ASSET'] = dg.node[b]['ASSET'] - total_debit
        # TODO adjust ratio
        # adjust balance of every creditor
        for i in debtors:
            dg.node[i]['CASH'] = dg.node[i]['CASH'] + dg[i][b]['weight'] / dg.node[i]['ASSET']
            # remove loan edge
            dg[i][b]['weight'] = 0
            #dg.remove_edge(i,b)
    else:
        # the debit cannot be completely repaid
        # pay the debts that are below the equal fraction
        debtorsUpdated = True
        while debtorsUpdated:
            debtorsUpdated = False
            # equal fraction of the asset            
            fraction = dg.node[b]['ASSET'] / len(debtors)
            # adjust balance of every creditor
            for i in debtors:
                debt = dg[i][b]['weight']
                if  debt <= fraction:
                    # pay the entire debt if the amount is below the fraction
                    dg.node[b]['ASSET'] = dg.node[b]['ASSET'] - debt
                    # TODO adjust ratio
                    dg.node[i]['CASH'] = dg.node[i]['CASH'] + dg[i][b]['weight'] / dg.node[i]['ASSET']
                    # remove loan edge
                    dg[i][b]['weight'] = 0
                    debtors.remove(i)
                    debtorsUpdated = True
        # pay equally the remaining debts
        for i in debtors:
            # pay the fraction
            dg.node[b]['ASSET'] = dg.node[b]['ASSET'] - fraction
            # loss for the debtor
            loss = dg[i][b]['weight'] - fraction
            old_asset = dg.node[i]['ASSET']
            dg.node[i]['ASSET'] = dg.node[i]['ASSET'] - loss
            dg.node[i]['CASH'] = dg.node[i]['CASH'] * old_asset / (old_asset - loss)
            dg.node[i]['LOANS'] = dg.node[i]['LOANS'] * old_asset / (old_asset - loss)

            if dg.node[i]['EQUITY'] * old_asset >= loss:
                dg.node[i]['DEPOSITS'] = (dg.node[i]['DEPOSITS'] * old_asset) / (old_asset - loss)
                dg.node[i]['EQUITY'] = (dg.node[i]['EQUITY'] * old_asset - loss) / (old_asset - loss)
                # remove loan edge
                dg[i][b]['weight'] = 0
            else:
                # bankrupt by default mechanism
                dg.node[i]['EQUITY'] = 0
                if 1 - dg.node[i]['DEPOSITS'] >= loss:
                    dg.node[i]['DEPOSITS'] = dg.node[b]['DEPOSITS'] / (1-loss)
                else:
                    dg.node[i]['DEPOSITS'] = 1
                # remove loan edge
                dg[i][b]['weight'] = 0
                #dg.remove_edge(i,b)
                failure(i,1,dg)
                
def cleanZeroEdges(dg):
    '''Clear zero edges of DiGraph dg'''
    for n,nbrdict in dg.adjacency_iter():
        for m in nbrdict.keys():
            if nbrdict[m]['weight'] == 0:
                dg.remove_edge(n,m)