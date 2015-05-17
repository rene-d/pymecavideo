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
    def __init__(self, parent, x, y, xlabel="", ylabel="", titre="", style=None, item=None):
        print "traceur2d", titre, item
        self.parent = parent
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.plotWidget=None
        self.update(x, y, xlabel, ylabel, titre, style, item)

    def update(self, x, y, xlabel="", ylabel="", titre="", style=None, item=None):
        if self.plotWidget:
            self.plotWidget.hide()
            del self.plotWidget
        self.plotWidget=pg.plot(title=titre)
        self.plotWidget.plot(x,y)
        self.plotWidget.setLabel('bottom', xlabel)
        self.plotWidget.setLabel('left', ylabel)
        self.plotWidget.show()





if __name__ == "__main__":
    from PyQt5 import QtGui  # (the example applies equally well to PySide)
    app = QtGui.QApplication([])
    ## Define a top-level widget to hold everything
    w = QtGui.QWidget()

    ## Create some widgets to be placed inside
    btn = QtGui.QPushButton('press me')
    text = QtGui.QLineEdit('enter text')
    listw = QtGui.QListWidget()

    x = np.arange(1000)
    y = np.random.normal(size=(3, 1000))
    plotWidget = pg.plot(title="Three plot curves")
    for i in range(3):
        plotWidget.plot(x, y[i], pen=(i,3))  ## setting pen=(i,3) automaticaly creates three different-colored pens
    
    ## Create a grid layout to manage the widgets size and position
    layout = QtGui.QGridLayout()
    w.setLayout(layout)
    ## Add widgets to the layout in their proper positions
    layout.addWidget(btn, 0, 0)   # button goes in upper-left
    layout.addWidget(text, 1, 0)   # text edit goes in middle-left
    layout.addWidget(listw, 2, 0)  # list widget goes in bottom-left
    layout.addWidget(plotWidget, 0, 1, 3, 1)  # plot goes on right side, spanning 3 rows

    ## Display the widget as a new window
    w.show()

    ## Start the Qt event loop
    app.exec_()
