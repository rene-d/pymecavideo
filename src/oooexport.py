# -*- coding: utf-8 -*-

"""
    oooexport.py, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>
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

import os, sys
import time
import subprocess
import threading

## pour exporter des fichier ODS
from odf.opendocument import OpenDocumentSpreadsheet
from odf.text import P
from odf.table import Table, TableColumn, TableRow, TableCell

## pour les fichiers temporaires
import tempfile
## pour étiqueter avec la date
import time

# nom de la commande qui lance LibreOffice Calc
tableur="libreoffice --calc"

class CalcThread(threading.Thread):
    """
    lance une instance de LibreOffice Calc dans un thread indépendant
    """
    def __init__(self, calcFile):
        """
        Le constructeur
        @param calcFile le fichier à ouvrir
        """
        threading.Thread.__init__(self)
        self.calcFile=calcFile

    def run(self):
        """
        activité principale du thread
        """

        ## on invoque un sous-shell et on le place en tâche de fond
        cmd="({0} {1})&".format(tableur, self.calcFile)
        subprocess.call(cmd, shell=True)
        return


class Calc():
    """
    Objet capable d'écrire des données textes et numériques dans
    un fichier au fomat ODS
    """

    def __init__(self, fichier_ods):
        """
        Crée un fichier temporaire pour y faire l'export et
        un document
        """
        self.outfile = tempfile.NamedTemporaryFile(
            mode='wb', 
            suffix='.ods',
            prefix='pymeca-',
            delete=False)
        self.outfile = open(fichier_ods, 'wb')
        self.doc=OpenDocumentSpreadsheet()
        self.table = Table(name="Pymecavideo {0}".format(time.strftime("%Y-%m-%d %Hh%Mm%Ss")))
        return

    def titres (self, lesTitres=[]):
        """
        Ajoute une ligne de titres
        @param les Titres une liste de chaînes
        """
        if not lesTitres:
            return
        tr = TableRow()
        self.table.addElement(tr)
        for t in lesTitres:
            tc = TableCell()
            tr.addElement(tc)
            p = P(text=t)
            tc.addElement(p)
        return

    def ligneValeurs(self, val=[]):
        """
        Ajoute une ligne de valeurs
        @param val une liste de flottants
        """
        if not val:
            return
        tr = TableRow()
        self.table.addElement(tr)
        for v in val:
            tc = TableCell(valuetype="float", value=str(v))
            tr.addElement(tc)
        return

    def importPymeca(self, app):
        """
        importe les données de pymecavideo
        @param app pointeur vers l'application
        """
        ## fait une ligne de titres
        titles=["t (s)"]
        for i in range(app.nb_de_points):
            x = "X%d (m)" % (1 + i)
            y = "Y%d (m)" % (1 + i)
            titles.append(x)
            titles.append(y)
        self.titres(titles)
        ## fait les lignes de données
        t=0
        dt = app.deltaT
        for k in app.points.keys():
            val=[t]
            t += app.deltaT
            data = app.points[k]
            for vect in data[1:]:
                vect = app.pointEnMetre(vect)
                val.append(vect.x())
                val.append(vect.y())
            self.ligneValeurs(val)
        ## accroche la feuille au document tableur
        self.doc.spreadsheet.addElement(self.table)
        ## écrit dans le fichier de sortie
        self.doc.save(self.outfile)
        self.outfile.close()
        return self.outfile.name


#if __name__ == "__main__":
    #calc = Calc()
    #calc.titres([u"date",
                 #u"heure",
                 #u"durée", 
                 #u"salle",
                 #u"conférenciers",
                 #u"titre",
                 #u"lien"])
    ### accroche la feuille au document tableur
    #calc.doc.spreadsheet.addElement(calc.table)
    ### écrit dans le fichier de sortie
    #calc.doc.save(calc.outfile)
    #calc.outfile.close()
    #thread=CalcThread(calc.outfile.name)
    #thread.start()

    
