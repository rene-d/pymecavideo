# -*- coding: utf-8 -*-

"""
    mpl, a module for pymecavideo:
      a program to launch a handy plotter
      
    Copyright (C) 2010 Cédrick FAURY <cedrick.faury@laposte.net>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
import matplotlib
if sys.platform == "win32":
    matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt


figNo=0
fig=None

def traceur2d(x,y,xlabel="", ylabel="", titre="", style=None):
    if sys.platform == "win32":
        #
        # Pas de problème sous windows car on n'ouvre pas de thread séparé
        #
        fig = plt.figure(1)
    else:
        global fig, figNo
        # conserve la même fenêtre de matplotlib quand elle a été créée
        # pour la réutiliser. Il faut éviter de la fermer, ou alors, faire
        # un peu de magie quand cette fenêtre est fermée, pour autoriser
        # à la re-créer (ce n'est pas le cas dans la révision du 25 octobre 2010)
        if figNo==0:
            figNo=1
            fig = plt.figure(1)
        else:
            fig.clear()
            
    ax = fig.add_subplot(111)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.plot(x, y, label = str(titre))
    ax.legend()
    
    plt.show()
    
    
    def __call__(x,y,xlabel="", ylabel="", titre=""):
        """
        traceur2d doit se présenter comme une fonction pour pouvoir
        être appelé par threading.Thread(), d'où l'implémentation de
        __call__. Cependant l'implémentation de mathplotlib est peu
        efficace quand on utilise des threads.
        """
        return traceur2d(x,y,xlabel, ylabel, titre)
    
    
    
#
# Ce qui suit pourrait servir à intégrer les "plots" dans la fenêtre principale de pymecavideo
# ce n'est pas fini !!! ce ne sont que les bases !!!
#
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

