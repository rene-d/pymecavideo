# -*- coding: utf-8 -*-
"""
    table, a module for pymecavideo:
      a subclass of QTableWidget able to send its data by drag & drop
      or to the clipboard.
      
    Copyright (C) 2008 Georges Khaznadar <georgesk@ofset.org>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class standardDragTable(QTableWidget):
    """Implémente une table qui exporte du drag'n drop avec un contenu
    compatible, de type text/html
    """
    def __init__(self,parent):
        QTableWidget.__init__(self,parent)
        QObject.connect(self,SIGNAL("itemSelectionChanged()"), self.selection)
    def htmlSelected(self):
        t="<table>"
        for l in range(self.rowCount()):
            lig="<tr>"
            ok=False # a priori la ligne pourrait être vide
            for c in range(self.columnCount()):
                lig+="<td>"
                i=self.item(l,c)
                if i and i.isSelected(): # seulement les cases de la sélection
                    lig += str(i.text())
                    ok=True # la ligne est non vide
                lig+="</td>"
            lig += "</tr>"
            if ok: # on n'envoie que les lignes non vides
                t+=lig
        t+="</table>"
        return t
    def textSelected(self):
        t=""
        for l in range(self.rowCount()):
            lig=""
            ok=False # a priori la ligne pourrait être vide
            for c in range(self.columnCount()):
                lig+=""
                i=self.item(l,c)
                if i and i.isSelected(): # seulement les cases de la sélection
                    lig += str(i.text())
                    ok=True # la ligne est non vide
                lig+="\t"
            if ok: # on n'envoie que les lignes non vides
                t+=lig[:-1]+"\n"
        t+=""
        return t
    def mimeSelected(self):
        mime=QMimeData()
        t=self.htmlSelected()
        mime.setData("text/html",t)
        t=self.textSelected()
        mime.setData("text/plain",t)
        return mime
    def startDrag(self,dropactions):
        drag=QDrag(self)
        mime=self.mimeSelected()
        drag.setMimeData(mime)
        drag.start(Qt.CopyAction)
    def  selection(self):
        clip=QApplication.clipboard()
        mime=self.mimeSelected()
        clip.setMimeData(mime)
        #clip.setMimeData(mime, clip.Selection) # ça devrait mettre aussi les données dans le presse papier de la souris pour X11.

if __name__ == "__main__":
    import sys
    app=QApplication([])
    t=standardDragTable(None)
    t.setRowCount(4)
    t.setColumnCount(2)
    t.setGeometry(QRect(0,0,400,300))
    t.setDragEnabled(True)
    for i in range(4):
        for j in range (2):
            t.setItem(i,j,QTableWidgetItem(str(i+j)))
    t.show()
    sys.exit(app.exec_())

