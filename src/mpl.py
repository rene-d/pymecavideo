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
import os

import matplotlib

# if sys.platform == "win32":
#    matplotlib.use('Qt4Agg')
#import matplotlib.pyplot as plt

#
#fig = plt.figure(1)
#ax = fig.add_subplot(111)
#
#plots = {}
#
#def traceur2d(x,y,xlabel="", ylabel="", titre="", style=None, item = None):
#    print "traceur2d", titre, item
#    global fig, ax, plots
#    ax.set_xlabel(xlabel)
#    ax.set_ylabel(ylabel)
#    if item in plots:
#        for p in plots[item]:
#            p.remove()
#    plots[item] = ax.plot(x, y, label = str(titre))
#    
#    l = ax.legend()
#    d1 = l.draggable()
#
#    plt.draw()
#    
#plt.show()
#plt.hide()
#    
#    

#figNo=0
#fig=None
#
#def traceur2d(x,y,xlabel="", ylabel="", titre="", style=None, item = None):
#    
#    if sys.platform == "win32":
#        #
#        # Pas de problème sous windows car on n'ouvre pas de thread séparé
#        #
#        fig = plt.figure(1)
#    else:
#        global fig, figNo
#        # conserve la même fenêtre de matplotlib quand elle a été créée
#        # pour la réutiliser. Il faut éviter de la fermer, ou alors, faire
#        # un peu de magie quand cette fenêtre est fermée, pour autoriser
#        # à la re-créer (ce n'est pas le cas dans la révision du 25 octobre 2010)
#        if figNo==0:
#            figNo=1
#            fig = plt.figure(1)
#        else:
#            fig.clear()
#            
#    ax = fig.add_subplot(111)
#    ax.set_xlabel(xlabel)
#    ax.set_ylabel(ylabel)
#    ax.plot(x, y, label = str(titre))
#    ax.legend()
#    
#    plt.show()
#    
#    
#    def __call__(x,y,xlabel="", ylabel="", titre=""):
#        """
#        traceur2d doit se présenter comme une fonction pour pouvoir
#        être appelé par threading.Thread(), d'où l'implémentation de
#        __call__. Cependant l'implémentation de mathplotlib est peu
#        efficace quand on utilise des threads.
#        """
#        return traceur2d(x,y,xlabel, ylabel, titre)
#    
#
#    
#
# Ce qui suit pourrait servir à intégrer les "plots" dans la fenêtre principale de pymecavideo
# ce n'est pas fini !!! ce ne sont que les bases !!!
#
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
from matplotlib.artist import setp

#
# Taille de caractère unique pour tous les textes affichés par Matplotlib
#
FONT_SIZE = 8

#
# Fonction pour recoder tous les textes à afficher en ISO (pb mpl)
#
def coderISO(text):
    return unicode(text, 'ISO-8859-1')


#
# 
#
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.fig = fig

        # ça, ça ne marche pas !!
        self.set_window_title("Courbes")

        # on crée les "axes"
        self.axes_xy = fig.add_subplot(211)
        self.axes_v = fig.add_subplot(212)

        # on  sauvegarde les positions
        self.pos_haut = self.axes_xy.get_position()
        self.pos_bas = self.axes_v.get_position()
        self.pos_tot = [self.pos_haut.xmin, self.pos_bas.ymin,
                        self.pos_haut.width, self.pos_haut.ymax - self.pos_bas.ymin]

        # on affecte des labels (vide) et une taille de police (fait une fois pour toute)
        for ax in [self.axes_xy, self.axes_v]:
            ax.set_xlabel("t (s)", size=FONT_SIZE)
            ax.set_ylabel("", size=FONT_SIZE)

        for ax in [self.axes_xy, self.axes_v]:
            setp(ax.get_xaxis().get_ticklabels(), fontsize=FONT_SIZE)
            setp(ax.get_yaxis().get_ticklabels(), fontsize=FONT_SIZE)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.updateGeometry(self)

        self.toolbar = VMToolbar(self, self)
        self.toolbar.show()

        self.plots = {}

    def effacerPlot(self, item):
        for p in self.plots[item]:
            p.remove()
            del self.plots[item]

    def effacerTousLesPlots(self):
        for item in self.plots.keys():
            self.effacerPlot(item)

    def gererAxes(self):
        xy, v = self.getTypeCourbe()
        if xy == 0:
            self.axes_xy.set_visible(False)
            self.axes_v.set_visible(True)
            self.axes_v.set_position(self.pos_tot)
        elif v == 0:
            self.axes_v.set_visible(False)
            self.axes_xy.set_visible(True)
            self.axes_xy.set_position(self.pos_tot)
        else:
            self.axes_v.set_visible(True)
            self.axes_xy.set_visible(True)
            self.axes_xy.set_position(self.pos_haut)
            self.axes_v.set_position(self.pos_bas)

    def getTypeCourbe(self):
        v, xy = 0, 0
        for t in self.plots.keys():
            typeDeCourbe = ("x", "y", "v")[(t - 1) % 3]
            if typeDeCourbe == "v":
                v += 1
            else:
                xy += 1
        return xy, v


class mplWindow(QDialog):
    def __init__(self, parent, widget1, widget2):
        QDialog.__init__(self, parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.update_widgets(widget1, widget2)

    def update_widgets(self, widget1, widget2):
        self.layout.addWidget(widget1)
        self.layout.addWidget(widget2)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        self.parent.emit(SIGNAL('mplWindowClosed()'))


class traceur2d(QObject):
    def __init__(self, parent, x, y, xlabel="", ylabel="", titre="", style=None, item=None):
        print "traceur2d", titre, item
        self.parent = parent
        self.canvas = self.parent.canvas
        self.update_canvas(x, y, xlabel, ylabel, titre, style, item)

    def update(self):
        self.mpl_window.update_widgets(self.canvas, self.canvas.toolbar)
        self.mpl_window.show()

    def update_canvas(self, x, y, xlabel="", ylabel="", titre="", style=None, item=None):
        if hasattr(self, 'mpl_window'):
            self.mpl_window.hide()
            del self.mpl_window
        self.change_canvas(x, y, xlabel, ylabel, titre, style, item)
        self.mpl_window = mplWindow(self.parent, self.canvas, self.canvas.toolbar)
        self.mpl_window.show()

    def change_canvas(self, x, y, xlabel="", ylabel="", titre="", style=None, item=None):
        typeDeCourbe = ("x", "y", "v")[(item - 1) % 3]
        if typeDeCourbe == "v":
            ax = self.canvas.axes_v
        else:
            ax = self.canvas.axes_xy
        #        ax.set_xlabel(coderISO(xlabel), size = FONT_SIZE)
        ax.set_ylabel(coderISO(ylabel))
        if item in self.canvas.plots:
            for p in self.canvas.plots[item]:
                p.remove()
        self.canvas.plots[item] = ax.plot(x, y, label=coderISO(str(titre)))
        self.canvas.gererAxes()

        leg = ax.legend(shadow=True)
        if hasattr(leg, "draggable"):
            d1 = leg.draggable()

        frame = leg.get_frame()
        frame.set_facecolor('0.80')

        for t in leg.get_texts():
            t.set_fontsize(FONT_SIZE)


class VMToolbar(NavigationToolbar2QTAgg):
    def __init__(self, plotCanvas, parent):
        NavigationToolbar2QTAgg.__init__(self, plotCanvas, parent)

    def _icon(self, name):
        #dirty hack to use exclusively .png and thus avoid .svg usage
        #because .exe generation is problematic with .svg
        name = name.replace('.svg', '.png')
        return QIcon(os.path.join(self.basedir, name)) 
