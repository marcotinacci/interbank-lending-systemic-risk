# -*- coding: utf-8 -*-

import scipy.stats as st
import matplotlib.pyplot as plt

class powerlaw(st.rv_continuous):
    def _pdf(self,x,C,alpha,xmax):
        return C*x**(-alpha) - xmax**(-alpha)

def powerlaw_sample(a,b,alpha,N):
    C = (1-alpha) / (b**(1-alpha) - a**(1-alpha))
    distr = powerlaw(a=a,name='powerlaw',shapes='C, alpha, xmax')
    return distr.rvs(C=C,alpha=alpha,xmax=b,size=N)
    
if __name__ == '__main__':
    # TEST SAMPLING POWERLAW
    # init
    a = 100
    b = 10**10
    alpha = 1.5
    N = 100
    
    # sampling
    data = powerlaw_sample(a,b,alpha,N)
    
    # plot
    plt.plot(sorted(data))
