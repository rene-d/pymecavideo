# -*- coding: utf-8 -*-

"""
    pgraph, a module for pymecavideo:
      a program to launch a handy plotter
      
    Copyright (C) 2015 Georges Khaznadar <georgesk@debian.org>

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

import pyqtgraph as pg
import numpy as np

class traceur2d:
    def __init__(self, parent, x, y, xlabel="", ylabel="", titre=""):
        print "traceur2d", titre
        self.parent = parent
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.plotWidget=None
        self.update(x, y, xlabel, ylabel, titre, style, item)

    def update(self, x, y, xlabel="", ylabel="", titre=""):
        if self.plotWidget:
            self.plotWidget.hide()
            del self.plotWidget
        self.plotWidget=pg.plot(title=titre)
        self.plotWidget.plot(x,y)
        self.plotWidget.setLabel('bottom', xlabel)
        self.plotWidget.setLabel('left', ylabel)
        self.plotWidget.show()





if __name__ == "__main__":
    from PyQt4 import QtGui
    import sys
    
    
    #lecture des données x,y depuis l'entrée standard
    xy=[map(float, ln.split()) for ln in sys.stdin if ln.strip()]
    x=[coord[0] for coord in xy]
    y=[coord[1] for coord in xy]
    
    app = QtGui.QApplication(sys.argv)
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    plotWidget = pg.plot(title=unicode(sys.argv[1],"UTF-8"))
    plotWidget.setLabel('bottom', unicode(sys.argv[2],"UTF-8"))
    plotWidget.setLabel('left', unicode(sys.argv[3],"UTF-8"))
    plotWidget.plot(x, y)
    
    plotWidget.show()

    ## Start the Qt event loop
    app.exec_()
