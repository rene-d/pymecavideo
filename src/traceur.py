# -*- coding: utf-8 -*-

"""
    traceur, a module for pymecavideo:
      a program to launch gnuplot consistently
      
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

import tempfile
import os


def traceur2d(x, y, xlabel="", ylabel="", titre="", style=None):
    """
    lancement de gnuplot puis d'un visionneur de postscript.
    
    Bug connu : si le visionneur met plus de 1 seconde pour démarrer,
    le fichier à ouvrir est déjà effacé. En général la deuxième fois
    le bug disparaît.
    
    @param x liste d'abscisses de points
    @param y liste d'ordonnées de points
    @param xlabel label de l'axe des abscisses
    @param ylabel label de l'axe des ordonnées
    @param titre le titre du graphique
    @param style phrase de style. On peut y mettre des choses comme :
      * [x1,y1,x2,y2] : une liste de 4 réels donne les dimensions de la fenêtre
      * "zero" : le point (0,0) doit être visible dans le graphique
    """
    autozoom = True  # par défaut, gnuplot zoomera tout seul pour cadrer au mieux
    if type(style) == type([]):  # les dimensions de la fenêtre sont explicites
        autozoom = False
        xmin, ymin, xmax, ymax = style
        if xmin > xmax:
            xmin, xmax = (xmax, xmin)
        if ymin > ymax:
            ymin, ymax = (ymax, ymin)
    if style == "zero":  # on doit s'assurer que la fenêtre contient (0,0)
        autozoom = False
        xmin = x[0];
        xmax = xmin;
        ymin = y[0];
        ymax = ymin
        for xtemp in x[1:] + [0]:
            if xtemp < xmin:
                xmin = xtemp
            if xtemp > xmax:
                xmax = xtemp
        for ytemp in y[1:] + [0]:
            if ytemp < ymin:
                ymin = ytemp
            if ytemp > ymax:
                ymax = ytemp
    if autozoom:
        xyranges = "# automatic zoom"
    else:
        # cas où un point est vraiment immobile, on élargit la fenêtre
        if xmax == xmin:
            xmin = xmin - 0.1; xmax = xmax + 0.1
        if ymax == ymin:
            ymin = ymin - 0.1; ymax = ymax + 0.1
        # on élargit la fenêtre de 10 % ensuite
        xspan = xmax - xmin;
        yspan = ymax - ymin
        xmin -= 0.05 * xspan;
        xmax += 0.05 * xspan
        ymin -= 0.05 * yspan;
        ymax += 0.05 * yspan
        # on peut enfin fixer les paramètres définitifs de la fenêtre
        xyranges = """set xrange [%s:%s]
set yrange [%s:%s]""" % (xmin, xmax, ymin, ymax)
    tmpdir = tempfile.mkdtemp(prefix="pymeca_plot_")
    datafilename = "%s/data" % tmpdir
    data = open(datafilename, "w")
    for i in range(len(x)):
        data.write("%s %s\n" % (x[i], y[i]))
    data.close()
    gptFileName = "%s/script.gpt" % tmpdir
    gnuplotfile = open(gptFileName, "w")
    # pour les styles de gnuplot, voir http://gnuplot.info/docs/node62.html
    script = """
set encoding iso_8859_1 
set xlabel "%s"
set ylabel "%s"
%s
set grid xtics ytics x2tics y2tics
set terminal postscript portrait enhanced mono dashed lw 1 "Helvetica" 14
set output "%s/plot.ps"
set style line 5 lt rgb "red" lw 1 pt 1
plot "%s/data" title "%s" with linespoints ls 5
""" % (xlabel, ylabel, xyranges, tmpdir, tmpdir, titre)
    script = script.decode("utf-8").encode("iso-8859-15")
    gnuplotfile.write(script)
    gnuplotfile.close()
    os.system("gnuplot %s" % gptFileName)
    # xdg-open a tendance à rendre la main aussitôt
    # donc on attend une seconde pour être sûr que les fichiers
    # temporaires sont encore là quand l'application de lecture
    # postscript est réellement lancée ! d'où la sleep 5. ce temps est grand pour les ordinateurs un peu lents.
    #il serait préférable d'avoir un test sur l'ouverture effective du lecteur pour effacer les fichiers temporaires.
    os.system("xdg-open %s/plot.ps; sleep 5" % (tmpdir))
    # ensuite on fait le ménage dans les fichiers temporaires.
    #if (os.path.exists(gptFileName)):
    #os.system("rm -rf %s" %(tmpdir))

    def __call__(x, y, xlabel="", ylabel="", titre=""):
        """
        traceur2d doit se présenter comme une fonction pour pouvoir
        être appelé par threading.Thread(), d'où l'implémentation de
        __call__
        """
        return traceur2d(x, y, xlabel, ylabel, titre)
    
