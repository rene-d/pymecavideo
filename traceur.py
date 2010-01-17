#-*- coding: utf-8 -*-

"""
    traceur, a module for pymecavideo:
      a program to launch gnuplot consistently
      
    Copyright (C) 2010 Georges Khaznadar <georgesk@ofset.org

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

import tempfile, os

def traceur2d(x,y,xlabel="", ylabel="", titre=""):
    """
    lancement de gnuplot puis d'autres programmes ensuite éventuellement
    """
    tmpdir=tempfile.mkdtemp("_pymeca_plot")
    datafilename="%s/data" %tmpdir
    data=open(datafilename,"w")
    for i in range(len(x)):
        data.write("%s %s\n" %(x[i],y[i]))
    data.close()
    gptFileName="%s/script.gpt" %tmpdir
    gnuplotfile=open(gptFileName,"w")
    script="""
set encoding iso_8859_1 
set xlabel "%s"
set ylabel "%s"
set grid xtics ytics x2tics y2tics
set terminal postscript portrait enhanced mono dashed lw 1 "Helvetica" 14
set output "%s/plot.ps"
plot "%s/data" title "%s"
""" %(xlabel,ylabel,tmpdir,tmpdir,titre)
    script=script.decode("utf-8").encode("iso-8859-15")
    gnuplotfile.write(script)
    gnuplotfile.close()
    os.system("gnuplot %s" %gptFileName)
    os.system("evince %s/plot.ps; rm -rf %s" %(tmpdir,tmpdir))
    if (os.path.exists(gptFileName)):
        os.system("rm -rf %s" %(tmpdir))
    
    def __call__(x,y,xlabel="", ylabel="", titre=""):
        """
        traceur2d doit se présenter comme une fonction pour pouvoir
        être appelé par threading.Thread(), d'où l'implémentation de
        __call__
        """
        return traceur2d(x,y,xlabel, ylabel, titre)
    
