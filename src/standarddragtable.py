# -*- coding: utf-8 -*-
"""
    table, a module for pymecavideo:
      a subclass of QTableWidget able to send its data by drag & drop
      or to the clipboard.
      
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

import locale

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class standardDragTable(QTableWidget):
    """Implémente une table qui exporte du drag'n drop avec un contenu
    compatible, de type text/html
    """

    def __init__(self, parent):
        QTableWidget.__init__(self, parent)
        self.itemSelectionChanged.connect(self.selection)
        self.sep_decimal = "."
        try:
            if locale.getdefaultlocale()[0][0:2] == 'fr':
                # en France, le séparateur décimal est la virgule
                self.sep_decimal = ","
        except TypeError:
            pass

    def htmlSelected(self):
        t = "<table>"
        lig_debut = "<tr>"
        for c in range(self.columnCount()):
            lig_debut += "<td>"
            i = self.horizontalHeaderItem(c)
            lig_debut += str(i.text())
            lig_debut += "</td>"
        t += lig_debut + "</tr>"
        for l in range(self.rowCount()):
            lig = "<tr>"
            ok = False  # a priori la ligne pourrait être vide
            for c in range(self.columnCount()):
                lig += "<td>"
                i = self.item(l, c)
                if i and i.isSelected():  # seulement les cases de la sélection
                    lig += str(i.text()).replace(".", self.sep_decimal)
                    ok = True  # la ligne est non vide
                lig += "</td>"
            lig += "</tr>"
            if ok:  # on n'envoie que les lignes non vides
                t += lig
        t += "</table>"
        return t

    def textSelected(self):
        t = ""
        lig_debut = ""
        for c in range(self.columnCount()):
            i = self.horizontalHeaderItem(c)
            lig_debut += str(i.text()) + "\t"
        t += lig_debut[:-1] + "\n"
        for l in range(self.rowCount()):
            lig = ""
            ok = False  # a priori la ligne pourrait être vide
            for c in range(self.columnCount()):
                lig += ""
                i = self.item(l, c)
                if i and i.isSelected():  # seulement les cases de la sélection
                    lig += str(i.text()).replace(".", self.sep_decimal)
                    ok = True  # la ligne est non vide
                lig += "\t"
            if ok:  # on n'envoie que les lignes non vides
                t += lig[:-1] + "\n"
        t += ""
        return t

    def mimeSelected(self):
        mime = QMimeData()
        t = self.htmlSelected()
        mime.setData("text/html", t)
        t = self.textSelected()
        mime.setData("text/plain", t)
        return mime

    def startDrag(self, dropactions):
        drag = QDrag(self)
        mime = self.mimeSelected()
        drag.setMimeData(mime)
        drag.start(Qt.CopyAction)

    def selection(self):
        clip = QApplication.clipboard()
        mime = self.mimeSelected()
        clip.setMimeData(mime)
        # clip.setMimeData(mime, clip.Selection) # ça devrait mettre aussi les données dans le presse papier de la souris pour X11.


if __name__ == "__main__":
    import sys

    app = QApplication([])
    t = standardDragTable(None)
    t.setRowCount(4)
    t.setColumnCount(2)
    t.setGeometry(QRect(0, 0, 400, 300))
    t.setDragEnabled(True)
    for i in range(4):
        for j in range(2):
            t.setItem(i, j, QTableWidgetItem(str(i + j)))
    t.show()
    sys.exit(app.exec_())

