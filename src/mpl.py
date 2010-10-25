# -*- coding: utf-8 -*-

'''
Created on 22 oct. 2010

@author: Cedrick
'''

#import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.lines as lines
#import matplotlib.transforms as mtransforms
#import matplotlib.text as mtext

def traceur2d(x,y,xlabel="", ylabel="", titre="", style=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.plot(x, y, label = str(titre))
    ax.legend()
#    line = MyLine(x, y, mfc='red', ms=12, label='line label')
    #line.text.set_text('line label')
#    line.text.set_color('red')
#    line.text.set_fontsize(16)
    
    
#    ax.add_line(line)
    
    
    plt.show()
    
    
    def __call__(x,y,xlabel="", ylabel="", titre=""):
        """
        traceur2d doit se présenter comme une fonction pour pouvoir
        être appelé par threading.Thread(), d'où l'implémentation de
        __call__
        """
        return traceur2d(x,y,xlabel, ylabel, titre)
    
