# -*- coding: utf-8 -*-
"""
    trajWidget, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>
    Copyright (C) 2022 Georges Khaznadar <georgesk@debian.org>

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
from math import sqrt, atan2, degrees

from PyQt6.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QRect, QPoint, QPointF
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPicture, QPainter, QColor, QFont, QPainterPath, QPen, QFontMetrics, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from image_widget import ImageWidget
from vecteur import vecteur
from globdef import pattern_float

class trajWidget(ImageWidget):
    """
    Classe pour l'élément qui remplit l'essentiel de l'onglet trajectoire
    paramètres du constructeur :

    @param parent un des layouts de l'onglet
    """
    def __init__(self, parent):
        ImageWidget.__init__(self, parent)
        self.chrono = False

        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setAutoFillBackground(True)
        self.couleurs = ["red", "blue", "cyan", "magenta", "yellow", "gray", "green", "red", "blue", "cyan", "magenta",
                         "yellow", "gray", "green"]
        self.setMouseTracking(True)
        self.speedToDraw = []
        self.speedtest = []
        self.pos_souris = None
        # self.update()
        self.picture = QPicture()
        self.origine_mvt = vecteur(0,0)
        self.origine = vecteur(0,0)
        self.referentiel = 0
        return

    def maj(self):
        self.origine_mvt = self.pointage.origine

    def prepare_vecteurs_pour_paint(self):
        if self.trajectoire.checkBoxVectorSpeed.isChecked():
            echelle = self.trajectoire.checkBoxScale.currentText().replace(
                ",",".")
            if not pattern_float.match(echelle): return
            self.speedToDraw = self.pointage.vecteursVitesse(float(echelle))
        return

    def mouseMoveEvent(self, event):
        # Look if mouse is near a point
        self.pos_souris = event.pos()
        if self.trajectoire.radioButtonNearMouse.isChecked():
            self.update()
        return

    def paintText(self, x, y, text,
                  color = QColor("white"), bgcolor = QColor("lightGray"),
                  fontsize = 12,
                  fontfamily = None,
                  center=False):
        """
        Trace un texte (self.painter doit être actif !)
        @param x abscisse
        @param y ordonnée
        @param text le teste à tracer
        @param color couleur de texte (defaut : Qt.white)
        @param bgcolor couleur de fond (par défaut : Qt.lightGray) ; 
          peut être None pour pas de fond
        @param fontsize taille de police (par défaut : 12)
        @param fontfamily famille de police (par défaut: None)
        @param center (faux par défaut) centrage horizontal demandé
        """
        if fontfamily:
            font = QFont(fontfamily, fontsize, weight = 700) # bold
        else:
            font = QFont()
        font.setPointSize(fontsize)
        self.painter.setFont(font)
        font_metrics = QFontMetrics(font)
        r = font_metrics.boundingRect(text)
        text_width = r.width()
        text_height = r.height()
        self.painter.setPen(color)
        offset_x = 0 if center == False else text_width // 2
        if bgcolor:
            self.painter.setBrush(bgcolor)
            self.painter.drawRect(
                x-5-offset_x, y-text_height-5,
                text_width+10, text_height+10)
        self.painter.drawText(x-offset_x, y, text)
        return
    
    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # self.painter.save()
        if self.chrono == 2 :
            couleur_de_fond = QColor("white")
        else :
            couleur_de_fond = QColor("grey")
        if not self.chrono == 1 :
            self.painter.fillRect(
                QRect(0, 0, self.video.image_w, self.video.image_h), couleur_de_fond)
        
        ############################################################
        # paint the origin
        if not self.chrono == 2:
            self.painter.setPen(QColor("green"))
            self.painter.drawLine(
                round(self.origine_mvt.x) - 5, round(self.origine_mvt.y),
                round(self.origine_mvt.x) + 5, round(self.origine_mvt.y))
            self.painter.drawLine(
                round(self.origine_mvt.x), round(self.origine_mvt.y) - 5,
                round(self.origine_mvt.x), round(self.origine_mvt.y) + 5)
            self.painter.drawText(
                round(self.origine_mvt.x), round(self.origine_mvt.y) + 15, "O")
            self.painter.end()

        # peint les informations pour le mode chronophotographie
        if self.chrono:  # ceci est géré dans pymecavideo.py, chercher : self.label_trajectoire.chrono
            self.painter = QPainter()
            self.painter.begin(self)
            if self.chrono==1:
                self.painter.drawPixmap(0, 0, self.image)
            self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            x1 = 50 # marge en largeur
            y1 = 50 # marge en hauteur
            # Ecrit l'intervalle de temps
            if self.chrono == 1:  # rends plus lisible si le fond est foncé
                text = f"Δt = {self.pointage.deltaT:.3f} s"
                self.paintText(self.width() - x1 - 100, y1, text)
                text = f"t = {self.pointage.deltaT*(self.trajectoire.spinBox_chrono.value()-1):.3f} s"
                self.paintText(self.width() - x1 - 100, 2 * y1, text)
            # dessine l'échelle
            if self.chrono == 2:  # chronogramme
                self.painter.setPen(QColor("black"))
                if self.pointage.echelle_image : #dessine une échelle en haut, horizontalement
                    longueur = round((self.pointage.echelle_image.p1 - self.pointage.echelle_image.p2).norme)
                    self.painter.drawLine(x1, y1-10, x1, y1+10)
                    self.painter.drawLine(x1, y1, longueur+x1, y1)
                    self.painter.drawLine(longueur+x1, y1-10, longueur+x1, y1+10)
                    text = "d = {0:.2e} m".format(self.pointage.echelle_image.longueur_reelle_etalon)
                    self.paintText(
                        max(x1+round(longueur/2), 0), y1+30,
                        text,
                        color = QColor("black"),
                        bgcolor = None,
                        center = True
                    )
                else : #échelle non faite
                    self.paintText(
                        x1, y1+20,
                        "échelle non précisée",
                         color = QColor("black"),
                         bgcolor = None)
                self.painter.end()

            ############################################################
            # Peindre l'échelle si chronophotographie
            if self.chrono == 1:  # chronophotographie
                self.painter = QPainter()
                self.painter.begin(self)
                self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                pen = QPen(QColor("blue"))
                pen.setWidth(3)
                self.painter.setPen(pen)
                if self.pointage.echelle: 
                    self.painter.drawLine(
                        round(self.pointage.echelle_trace.p1.x),
                        round(self.pointage.echelle_trace.p1.y),
                        round(self.pointage.echelle_trace.p2.x),
                        round(self.pointage.echelle_trace.p2.y))

                    echelle = "d = {0:.2e} m".format(
                            self.pointage.echelle_image.longueur_reelle_etalon)

                    self.paintText(
                        round(self.pointage.echelle_trace.p1.x),
                        round((self.pointage.echelle_trace.p1.y + self.pointage.echelle_trace.p2.y)/2)+20,
                        echelle,
                        color = Qt.blue,
                        bgcolor = None,
                        fontfamily = "Times",
                        fontsize = 15,
                    )
                else : #pas d'échelle 
                    self.paintText(x1, y1+20, "échelle non précisée",
                                   color = QColor("blue"),
                                   bgcolor = None,
                                   fontfamily = "Times",
                                   fontsize = 15,)
                    
                self.painter.end()

        ############################################################

        ############################################################
        # Paint points
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # préparation de la fonction de rappel
        for i, t, iter_OP in self.pointage.gen_iter_TOP():
            if self.referentiel != 0:
                obj_reference = self.pointage.data[t][self.referentiel]
            else:
                obj_reference = vecteur(0, 0)
            for j, obj, p in iter_OP:
                if p:
                    self.painter.setFont(QFont("", 10))
                    self.painter.translate(
                        round(p.x + self.origine.x - obj_reference.x),
                        round(p.y + self.origine.y - obj_reference.y))
                    if self.chrono == 2:
                        self.painter.setPen(QColor("black"))
                        self.painter.drawLine(-4, 0, 4, 0)
                        self.painter.drawLine(0, -4, 0, 4)
                        self.painter.translate(-10, +10)
                        decal = -25
                        if p.x + decal < 0 : 
                            decal = 5 
                        self.painter.drawText(decal, 5, "M"+"'"*j+str(i))
                    else :
                        self.painter.setPen(QColor(self.couleurs[j]))
                        self.painter.drawLine(-2, 0, 2, 0)
                        self.painter.drawLine(0, -2, 0, 2)
                        self.painter.translate(-10, +10)
                        self.painter.drawText(0, 0, str(j + 1))
                    self.painter.translate(
                        round(-p.x - self.origine.x + obj_reference.x) + 10,
                        round(-p.y - self.origine.y + obj_reference.y) - 10)
        self.painter.end()
        ############################################################
        # paint repere
        if not self.chrono == 2 :
            self.painter = QPainter()
            self.painter.begin(self)
            self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.painter.setPen(QColor("green"))
            # self.painter.translate(0,0)
            self.painter.translate(
                round(self.origine_mvt.x), round(self.origine_mvt.y))
            p1 = QPoint(round(self.pointage.sens_X * (-40)), 0)
            p2 = QPoint(round(self.pointage.sens_X * (40)), 0)
            p3 = QPoint(round(self.pointage.sens_X * (36)), 2)
            p4 = QPoint(round(self.pointage.sens_X * (36)), -2)
            self.painter.scale(1, 1)
            self.painter.drawPolyline(p1, p2, p3, p4, p2)
            self.painter.rotate(self.pointage.sens_X *
                                self.pointage.sens_Y * (-90))
            self.painter.drawPolyline(p1, p2, p3, p4, p2)
            self.painter.rotate(self.pointage.sens_X *
                                self.pointage.sens_Y * (90))
            self.painter.translate(
                round(-self.origine_mvt.x), round(-self.origine_mvt.y))
            self.painter.end()

        # paint speed vectors if asked

        if self.speedToDraw != [] and \
           self.trajectoire.checkBoxVectorSpeed.isChecked():
            for obj in self.speedToDraw:
                for (org, ext) in self.speedToDraw[obj]:
                    if org == ext:  continue # si la vitesse est nulle
                    # on prend en considération éventuellement la distance
                    # du pointeur de souris;
                    # s'il est à plus de 20 pixels de l'origine du vecteur
                    # on ne trace rien
                    if self.trajectoire.radioButtonNearMouse.isChecked():
                        ecart = vecteur(qPoint = self.pos_souris) - org
                        if ecart.manhattanLength() > 20: continue
                    self.painter = QPainter()
                    self.painter.begin(self)
                    self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    self.painter.setPen(QColor(self.video.couleurs[int(obj) - 1]))
                    vec = ext - org                # le vecteur de la flèche 
                    ortho = vecteur(-vec.y, vec.x) # idem tourné de 90°
                    p1 = ext - vec * 0.1 + ortho * 0.05
                    p2 = p1 - ortho * 0.1
                    self.painter.drawPolyline(
                        org.toQPointF(),
                        ext.toQPointF(),
                        p1.toQPointF(),
                        p2.toQPointF(),
                        ext.toQPointF()
                    )
                    self.painter.end()
                else:
                    pass  # null speed
