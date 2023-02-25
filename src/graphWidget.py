# -*- coding: utf-8 -*-

"""
    graphWidget, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>
    Copyright (C) 2023 Georges Khaznadar <georgesk@debian.org>

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

from PyQt6.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, \
    QSize, QTimer, QObject, QRect, QPoint, QPointF, QEvent
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, \
    QCursor, QPen, QColor, QFont, QResizeEvent, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, \
    QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, \
    QTableWidgetSelectionRange, QPushButton, QVBoxLayout

import os, time, re, sys
import locale
import pyqtgraph as pg
import pyqtgraph.exporters
import math

from version import Version
from vecteur import vecteur
from image_widget import ImageWidget
from globdef import cible_icon, DOCUMENT_PATH, inhibe, pattern_float
from toQimage import toQImage
from suivi_auto import SelRectWidget
from detect import filter_picture
from cadreur import Cadreur, openCvReader
from export import Export, EXPORT_FORMATS
from grandeurs import grandeurs
from dbg import Dbg

import interfaces.icon_rc

from interfaces.Ui_graphWidget import Ui_graphWidget
from etatsGraph import Etats

class GraphWidget(QWidget, Ui_graphWidget, Etats):
    """
    Widget principal de l'onglet grapheur

    paramètres du constructeur :
    @param parent l'onglet des graphiques
    """
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        Ui_graphWidget.__init__(self)
        Etats.__init__(self)
        self.setupUi(self)
        self.connecte_ui()
        self.locals = {} # dictionnaire de variables locales, pour eval
        self.graphe_deja_choisi = None
        self.graphW = None
        return

    def setApp(self, app):
        """
        Crée des liens avec la fenêtre principale, le débogueur,
        le wigdet de pointage
        @param app la fenêtre principale
        """
        self.app = app
        self.dbg = app.dbg
        self.pointage = app.pointage
        return
        
    def connecte_ui(self):
        """
        Connecte les signaux des sous-widgets
        """
        self.comboBox_X.currentIndexChanged.connect(self.dessine_graphe_avant)
        self.comboBox_Y.currentIndexChanged.connect(self.dessine_graphe_avant)
        self.lineEdit_m.textChanged.connect(self.verifie_m_grapheur)
        self.lineEdit_g.textChanged.connect(self.verifie_g_grapheur)
        self.comboBox_style.currentIndexChanged.connect(self.dessine_graphe)
        self.pushButton_save_plot.clicked.connect(self.enregistre_graphe)
        return
    
    def dessine_graphe_avant(self):
        if self.graphe_deja_choisi is not None :
            self.graphe_deja_choisi = None #si changement ds les combobox, on réinitilaise le choix.
        self.dessine_graphe()
        return

    def dessine_graphe(self):
        """dessine les graphes avec pyqtgraph au moment où les combobox sont choisies"""
        self.dbg.p(2, "rentre dans 'dessine_graphe'")
        X, Y = [], []
        styles = {0: {'pen': None, 'symbol': '+'}, 1: {'pen': (0, 0, 0), 'symbol': '+'}, 2: {'pen': (
            0, 0, 0), 'symbol': None}}  # Dictionnaire contenant les différents styles de graphes
        # Index du comboxBox styles, inspirés de Libreoffice
        style = self.comboBox_style.currentIndex()

        if self.graphe_deja_choisi is not None :
            abscisse = self.graphe_deja_choisi[1].strip('|')
            ordonnee = self.graphe_deja_choisi[0].strip('|')
        else :
            abscisse = self.comboBox_X.currentText().strip('|')
            ordonnee = self.comboBox_Y.currentText().strip('|')
        # Définition des paramètres 'pen' et 'symbol' pour pyqtgraph
        pen, symbol = styles[style]['pen'], styles[style]['symbol']
        grandeurX = abscisse
        grandeurY = ordonnee
        # rien à faire si le choix des axes est indéfini
        if grandeurX == "Choisir ..." or grandeurY == "Choisir ...": return

        if grandeurX == 't':
            X = self.pointage.dates
        elif grandeurX in self.locals :
            X = self.locals[grandeurX]
        if grandeurY == 't':
            Y = self.pointage.dates
        elif grandeurY in  self.locals :
            Y = self.locals[grandeurY]
        # on retire toutes les parties non définies
        # zip (*[liste de tuples]) permet de "dézipper"
        X, Y = zip(*[(x, y) for x,y in zip(X, Y) if x is not None and y is not None])
        X = list(X)
        Y = list(Y)
        
        if X != [] and Y != []:
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', 'k')
            titre = "%s en fonction de %s" % (ordonnee, abscisse)
            # gestion des unités
            if 't' in abscisse:
                unite_x = "t(s)"
            elif 'V' in abscisse:
                unite_x = abscisse+'(m/s)'
            elif 'E' in abscisse:
                unite_x = abscisse+'(J)'
            elif 'A' in abscisse:
                unite_x = abscisse+'(m/s²)'
            else:
                unite_x = abscisse+'(m)'

            if 't' in ordonnee:
                unite_y = "t(s)"
            elif 'V' in ordonnee:
                unite_y = ordonnee+'(m/s)'
            elif 'E' in ordonnee:
                unite_y = ordonnee+'(J)'
            elif 'A' in ordonnee:
                unite_y = ordonnee+'(m/s²)'
            else:
                unite_y = ordonnee+'(m)'

            if not self.graphW:  # premier tour
                self.graphW = pg.PlotWidget(
                    title=titre, parent=self.widget_graph)
                self.graphW.setMenuEnabled(False)
                self.graphW.setLabel('bottom', unite_x)
                self.graphW.setLabel('left', unite_y)
                self.vLayout = QVBoxLayout(self.widget_graph)
                self.vLayout.setContentsMargins(0, 0, 0, 0)
                self.vLayout.setObjectName(
                    "verticalLayout_graph")
                self.vLayout.addWidget(self.graphW)
                self.graphW.plot(X, Y, pen=pen, symbol=symbol)
                self.graphW.autoRange()
                self.graphW.show()
                self.pg_exporter = pg.exporters.ImageExporter(self.graphW.plotItem)
            else:
                plotItem = self.graphW.getPlotItem()
                plotItem.setTitle(titre)
                self.graphW.setLabel('bottom', unite_x)
                self.graphW.setLabel('left', unite_y)
                self.graphW.clear()
                self.graphW.plot(X, Y, pen=pen, symbol=symbol)
                self.graphW.autoRange()
                self.graphW.show()
            self.graphe_deja_choisi = (ordonnee, abscisse)
        return
    
    def enregistre_graphe(self):
        if hasattr (self, 'pg_exporter'):
            base_name = os.path.splitext(os.path.basename(self.pointage.filename))[0]
            defaultName = os.path.join(DOCUMENT_PATH, base_name+'.png')
            fichier = QFileDialog.getSaveFileName(
                self,
                self.tr("Enregistrer le graphique"),
                defaultName, self.tr("fichiers images(*.png)"))
            self.pg_exporter.export(fichier[0])
        return
    
    def verifie_m_grapheur(self):
        m = self.lineEdit_m.text().replace(',', '.')
        if m != "":
            if not pattern_float.match(m):
                QMessageBox.critical(
                    self,
                    self.tr("MAUVAISE VALEUR !"),
                    self.tr("La valeur rentrée (m = {}) n'est pas compatible avec le calcul").format(m))
            else:
                self.affiche_grapheur()
                self.dessine_graphe()
        return

    def verifie_g_grapheur(self):
        g = self.lineEdit_g.text().replace(',', '.')
        if g != "":
            if not pattern_float.match(g):
                QMessageBox.critical(
                    self,
                    self.tr("MAUVAISE VALEUR !"),
                    self.tr("La valeur rentrée (g = {}) n'est pas compatible avec le calcul").format(g))
            else:
                self.affiche_grapheur()
                self.dessine_graphe()
        return

    def affiche_grapheur(self, MAJ=True):
        self.dbg.p(2, "rentre dans 'affiche_grapheur'")
        m = self.lineEdit_m.text().replace(',', '.')
        g = self.lineEdit_g.text().replace(',', '.')
        if not pattern_float.match(m) or not pattern_float.match(g): return 
        deltaT = self.pointage.deltaT
        m = float(m)
        g = float(g)

        # initialisation de self.locals avec des listes vides
        for obj in self.pointage.suivis:
            for gr in grandeurs:
                self.locals[gr+str(obj)] = []

        # remplissage des self.locals pour les positions,
        # les vitesses, Ec et Epp
        for i, t, iter_OPV in self.pointage.gen_iter_TOPV():
            for j, obj, p, v in iter_OPV:
                p = self.pointage.pointEnMetre(p)
                v = self.pointage.pointEnMetre(v)
                self.locals["X"+str(obj)].append(p.x if p else None)
                self.locals["Y"+str(obj)].append(p.y if p else None)
                self.locals["Vx"+str(obj)].append(v.x if v else None)
                self.locals["Vy"+str(obj)].append(v.y if v else None)
                self.locals["V"+str(obj)].append(v.norme if v else None)
                self.locals["Ec"+str(obj)].append(
                    0.5 * m * v.norme ** 2 if v else None)
                self.locals["Epp"+str(obj)].append(
                    self.pointage.sens_Y * m * g * p.y if p else None)
        # on complète le remplissage de self.locals
        for obj in self.pointage.suivis:
            # énergie mécanique
            self.locals["Em"+str(obj)] = \
                [ec + epp if ec is not None and epp is not None else None
                 for ec, epp in zip (
                    self.locals["Ec"+str(obj)],
                    self.locals["Epp"+str(obj)])]
            # accélération Ax
            liste0 = self.locals["Vx"+str(obj)][1:-1] # commence à l'index 1
            liste1 = self.locals["Vx"+str(obj)][2:]   # commence à l'index 2
            self.locals["Ax"+str(obj)] = [None, None] + \
                [(v1 - v0) / deltaT if v1 is not None and v0 is not None else None
                 for v1, v0 in zip(liste1, liste0)]
            # accélération Ay
            liste0 = self.locals["Vy"+str(obj)][1:-1] # commence à l'index 1
            liste1 = self.locals["Vy"+str(obj)][2:]   # commence à l'index 2
            self.locals["Ay"+str(obj)] = [None, None] + \
                [(v1 - v0) / deltaT  if v1 is not None and v0 is not None else None
                 for v1, v0 in zip(liste1, liste0)]
            # module de l'accélération A
            self.locals["A"+str(obj)] = \
                [vecteur(ax, ay).norme if ax is not None else None
                 for ax, ay in zip(
                    self.locals["Ax"+str(obj)],
                    self.locals["Ay"+str(obj)]
                )]
        # mise à jour des éléments graphiques
        if self.graphe_deja_choisi is None :
            # tout premier choix de graphe
            self.comboBox_X.clear()
            self.comboBox_Y.clear()
            self.comboBox_X.insertItem(-1,
                                        self.tr("Choisir ..."))
            self.comboBox_Y.insertItem(-1,
                                        self.tr("Choisir ..."))
            self.comboBox_X.addItem('t')
            self.comboBox_Y.addItem('t')
            for grandeur in self.locals.keys():
                if self.locals[grandeur] != []:
                    numero = ''.join(
                        [grandeur[-2] if grandeur[-2].isdigit() else "", grandeur[-1]])
                    if 'prime' in grandeur :
                        if 'x' in grandeur :
                            grandeur_a_afficher = 'Vx'+numero
                        elif 'y' in grandeur :
                            grandeur_a_afficher = 'Vy'+numero
                        elif 'abs' in grandeur :
                            grandeur_a_afficher = 'Ax'+numero
                        elif 'ord' in grandeur :
                            grandeur_a_afficher = 'Ay'+numero
                    elif 'A' in grandeur or 'V' in grandeur:
                        grandeur_a_afficher = '|'+grandeur+'|'

                    else :
                        grandeur_a_afficher = grandeur
                    self.comboBox_X.addItem(grandeur_a_afficher)
                    self.comboBox_Y.addItem(grandeur_a_afficher)
        #else : #il y a déjà eu un choix de graphe
            #self.comboBox_X.setItem(self.graphe_deja_choisi[1])
            #self.comboBox_Y.setItem(self.graphe_deja_choisi[0])
        return
    

