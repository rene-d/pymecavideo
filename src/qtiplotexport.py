#-*- coding: utf-8 -*-

"""
    qtiplotexport.py, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>

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

from string import Template
import time

qtiFileTemplate=Template("""\
QtiPlot 0.9.0 project file
<scripting-lang>	muParser
<windows>	1
$table
<open>1</open>
""")

tableTemplate=Template("""\
<table>
Table1	$ligs	$cols	$date
geometry	0	0	664	258	active
header$headers
ColWidth$colWidths
<com>
</com>
ColType$colTypes
ReadOnlyColumn$colRo
HiddenColumn$colHidden
Comments$comments
WindowLabel		2
<data>
$data
</data>
</table>
""")

class Qtiplot:
    """
    Une classe pour exporter des fichiers de type Qtiplot
    """
    def __init__(self, app):
        """
        Crée l'objet
        @param app l'application de pymecavideo
        """
        self.app=app
        dic={}
        dic['date']=time.strftime("%d/%m/%y %H:%M")
        n=len(app.points.keys())
        if n <30: n=30
        dic['ligs']=str(n)
        dic['cols']=str(1+2*app.nb_de_points)
        dic['headers']='\tt-s[X]'
        dic['colWidths']='\t100'
        dic['colTypes']='\t0;0/13'
        dic['colRo']='\t0'
        dic['colHidden']='\t0'
        dic['comments']='\t'
        for i in range(app.nb_de_points):
            dic['headers']+='\tX%s-m[Y]\tY%s-m[Y]' %(i+1,i+1)
            dic['colWidths']+="\t100\t100"
            dic['colTypes']+="\t0;0/13\t0;0/13"
            dic['colRo']+='\t0\t0'
            dic['colHidden']+='\t0\t0'
            dic['comments']+='\t\t'
        # deux bizarreries : tabulations supplémentaires
        dic['colWidths']+='\t';  dic['comments']+='\t'
        dic['data']=''
        ligne=0
        dt=app.deltaT
        for k in app.points.keys():
            data=app.points[k]
            dic['data']+='%i\t%f' %(ligne, dt*ligne)
            for vect in data[1:]:
                vect=app.pointEnMetre(vect)
                dic['data']+='\t%f\t%f' %(vect.x(), vect.y())
            dic['data']+='\n'
            ligne +=1
        dic['data']= dic['data'][:-1] # suppression du dernier retour à la ligne
        self.table=tableTemplate.substitute(dic)
        self.qtifile=qtiFileTemplate.substitute({'table': self.table})

    def saveToFile(self,f):
        """
        Enregistre les données dans un fichier
        @param f le fichier ouver déjà en écriture
        """
        f.write(self.qtifile)
        
