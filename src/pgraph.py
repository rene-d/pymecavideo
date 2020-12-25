# -*- coding: utf-8 -*-

"""
    pgraph, a module for pymecavideo:
      a program to launch a handy plotter
      
    Copyright (C) 2007-2018 Georges Khaznadar <georgesk.debian.org>

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

from PyQt5 import QtWidgets
import sys
import pyqtgraph as pg
import numpy as np

class traceur2d:
    def __init__(self, parent, x, y, xlabel="", ylabel="", titre="", style=None, item=None):
        self.parent = parent
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.plotWidget=pg.plot()
        self.update(x, y, xlabel, ylabel, titre, style, item)

    def update(self, x, y, xlabel="", ylabel="", titre="", style=None, item=None):
        self.plotWidget.clear()
        self.plotWidget.setTitle(titre)
        self.plotWidget.setWindowTitle(titre)

        self.plotWidget.plot(x,y)
        self.plotWidget.setLabel('bottom', xlabel)
        self.plotWidget.setLabel('left', ylabel)
        self.plotWidget.show()

if __name__ == "__main__":
    #lecture des données x,y depuis l'entrée standard
    xy=[list(map(float, ln.split())) for ln in sys.stdin if ln.strip()]
    x=[coord[0] for coord in xy]
    y=[coord[1] for coord in xy]
    app = QtWidgets.QApplication(sys.argv)
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    
    #Si python2
    try : 
        plotWidget = pg.plot(title=unicode(sys.argv[1],"UTF-8"))
        plotWidget.setLabel('bottom', unicode(sys.argv[2],"UTF-8"))
        plotWidget.setLabel('left', unicode(sys.argv[3],"UTF-8"))
        plotWidget.plot(x, y)
    #Si python3
    except NameError :
        plotWidget = pg.plot(title=sys.argv[1])
        plotWidget.setLabel('bottom', sys.argv[2])
        plotWidget.setLabel('left', sys.argv[3])
        plotWidget.plot(x, y)        
    
    
    plotWidget.show()

    ## Start the Qt event loop
    app.exec_()
