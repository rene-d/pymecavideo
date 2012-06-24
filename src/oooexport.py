#-*- coding: utf-8 -*-

"""
    oooexport.py, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>

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

import os, time, subprocess
import oootools

class Calc:
    """
    Crée une instance d'Ooo Calc en mode serveur pour permettre d'y inscrire
    des données, et fournit des méthodes pour y envoyer des données.
    """
    def __init__(self,Hidden=False, HOST = 'localhost', PORT = 11111):
        #find which is the soffice excutable on system. Depends on System.
        for exe_ooo in ["soffice","ooffice3.2"]:
            if  any(os.access(os.path.join(p,exe_ooo), os.X_OK) for p in os.environ['PATH'].split(os.pathsep)):
                self.exe_ooo = exe_ooo
        cmd='(%s --nodefault --accept="socket,host=%s,port=%d;urp;StarOffice.ServiceManager" &)' %(self.exe_ooo, HOST, PORT)
        subprocess.call(cmd, shell=True)
        maxduration=10
        delay=2
        ok=False
        t=0
        while not ok and t < maxduration:
            time.sleep(delay)
            t+=delay
            self.ooo = oootools.OOoTools(HOST, PORT)
            self.ctx = self.ooo.ctx
            self.desktop = self.ooo.desktop
            ok = self.desktop != None
        if not ok:
            raise IOError, "Pas possible de communiquer avec {libre|open}office."
        if Hidden:
            props=PropertyValue()
            props.Name="Hidden"
            props.Value=True
            self.calc = self.desktop.loadComponentFromURL("private:factory/scalc",'_blank',0,(props,))
        else:
             self.calc = self.desktop.loadComponentFromURL("private:factory/scalc",'_blank',0,())
        self.sheet=self.calc.getSheets().getByIndex(0)

    def setFormula(self,x,y,value):
        """
        Écrit le contenu d'une cellule dans la feuille courante
        @param x la colonne
        @param y le numéro de ligne
        @param value la formule à placer
        """
        self.sheet.getCellByPosition(x,y).setFormula(value)

    def importPymeca(self, app):
        """
        importe les données de pymecavideo
        @param app pointeur vers l'application
        """
        self.setFormula(0,0,"t (s)")
        for i in range(app.nb_de_points):
            x="X%d (m)" %(1+i)
            y="Y%d (m)" %(1+i)
            self.setFormula(2*i+1,0,x)
            self.setFormula(2*i+2,0,y)
        ligne=1
        dt=app.deltaT
        for k in app.points.keys():
            data=app.points[k]
            i=0
            self.setFormula(0,ligne,"%s" %(dt*(ligne-1)))
            for vect in data[1:]:
                vect=app.pointEnMetre(vect)
                self.setFormula(2*i+1,ligne, "%s" %vect.x())
                self.setFormula(2*i+2,ligne, "%s" %vect.y())
                i+=1
            ligne +=1
            
if __name__=="__main__":
    calc=Calc()
    calc.setFormula(0,0,"date")
    calc.setFormula(1,0,"heure")
    calc.setFormula(2,0,"durée")
    calc.setFormula(3,0,"salle")
    calc.setFormula(4,0,"conférenciers")
    calc.setFormula(5,0,"titre")
    calc.setFormula(6,0,"lien")
