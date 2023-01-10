# -*- coding: utf-8 -*-
"""
    trajectoire_widget, a module for pymecavideo:
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

from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QRect, QPoint, QPointF
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPicture, QPainter, QColor, QFont, QPainterPath, QPen, QFontMetrics
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from image_widget import ImageWidget

from vecteur import vecteur


class TrajectoireWidget(ImageWidget):
    def __init__(self, parent):
        ImageWidget.__init__(self, parent)
        self.app = None
        self.chrono = False

        self.setCursor(Qt.ArrowCursor)
        self.setAutoFillBackground(True)
        # self.setMouseTracking(1)
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

    def setApp(self, app):
        self.app = app
        return
    
    def reDraw(self):
        """call when somthing change as repere, origine ..."""
        self.giveCoordonatesToPaint()
        # self.maj()
        self.repaint()

    def maj(self):
        self.origine_mvt = self.video.origine

    def giveCoordonatesToPaint(self):
        self.speedToDraw = []
        if self.video.app.checkBoxVectorSpeed.isChecked():
            for key in self.video.app.points.keys():
                points = self.video.app.points[key]
                for i in range(len(points)):
                    wroteSpeed = False

                    point = points[i]
                    try:
                        if self.referentiel != 0:
                            ptreferentiel = points[int(self.referentiel)]

                            try:
                                ptreferentielAfter = self.video.app.points[key + 1][int(
                                    self.referentiel)]
                                ptreferentielBefore = self.video.app.points[key - 1][int(
                                    self.referentiel)]
                            except KeyError:  # last point -> can't compute speed
                                break

                        else:
                            ptreferentiel = vecteur(0, 0)
                            ptreferentielBefore = vecteur(0, 0)
                            ptreferentielAfter = vecteur(0, 0)
                    except IndexError:  # si pas le bon nb de points
                        pass

                    if type(point) != type(""):
                        if self.video.app.radioButtonNearMouse.isChecked() and self.pos_souris != None:
                            near = 20
                            pos = self.pos_souris
                            distance = QPoint(
                                round(point.x + self.origine.x - ptreferentiel.x),
                                round(point.y + self.origine.y - ptreferentiel.y)) - pos
                            if distance.manhattanLength() < near:
                                self.video.app.dbg.p(
                                    2, "mouse near a point")
                                wroteSpeed = True

                        elif self.video.app.radioButtonSpeedEveryWhere.isChecked():
                            wroteSpeed = True

                        if wroteSpeed:
                            keyMax = len(self.video.app.points.keys())
                            # first and last point can't have speed.
                            if key != 0 and key != keyMax - 1:
                                # coordonnates of n-1 and n+1 point
                                try:
                                    tempsAfter = float(
                                        self.video.app.points[key + 1][0])/self.video.app.deltaT  # en "delta_T"
                                    tempsBefore = float(
                                        self.video.app.points[key-1][0])/self.video.app.deltaT  # en "delta_T"
                                    pointBefore = vecteur(
                                        (self.video.app.points[key - 1][i].x + self.origine.x - ptreferentielBefore.x)/(tempsAfter-tempsBefore),
                                        (self.video.app.points[key - 1][i].y + self.origine.y - ptreferentielBefore.y)/(tempsAfter-tempsBefore))

                                    pointAfter = vecteur(
                                        (self.video.app.points[key + 1][i].x + self.origine.x - ptreferentielAfter.x)/(tempsAfter-tempsBefore),
                                        (self.video.app.points[key + 1][i].y + self.origine.y - ptreferentielAfter.y)/(tempsAfter-tempsBefore))

                                    vector_speed = pointAfter - pointBefore

                                    self.speedToDraw.append((vecteur(point.x + self.origine.x - ptreferentiel.x,
                                                                    point.y + self.origine.y - ptreferentiel.y),
                                                             vector_speed, i))
                                except KeyError:  # last point -> can't compute speed
                                    pass
                                except IndexError:  # si pas le bon nb de points
                                    pass

    def mouseMoveEvent(self, event):
        # Look if mouse is near a point
        self.pos_souris = event.pos()
        if self.video.app.radioButtonNearMouse.isChecked():
            self.reDraw()

        return

    def paintText(self, x, y, text,
                  color = Qt.white, bgcolor = Qt.lightGray,
                  fontsize = 12,
                  fontfamily = None):
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
        """
        if fontfamily:
            font = QFont(fontfamily, fontsize, QFont.Bold)
        else:
            font = QFont()
        font.setPointSize(fontsize)
        self.painter.setFont(font)
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.width(text)
        text_height = fontsize
        self.painter.setPen(color)
        if bgcolor:
            self.painter.setBrush(bgcolor)
            self.painter.drawRect(
                x-5, y-text_height-5,
                text_width+10, text_height+10)
        self.painter.drawText(x, y, text)
        return
    
    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.Antialiasing)
        # self.painter.save()
        if self.chrono == 2 :
            couleur_de_fond = QColor("white")
        else :
            couleur_de_fond = QColor("grey")
        if not self.chrono == 1 :
            self.painter.fillRect(
                QRect(0, 0, self.video.width(), self.video.height()), couleur_de_fond)
        
        ############################################################
        # paint the origin
        if not self.chrono == 2:
            self.painter.setPen(Qt.green)
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
            self.painter.setRenderHint(QPainter.TextAntialiasing)
            self.painter.setRenderHint(QPainter.Antialiasing)
            x1 = 50 # marge en largeur
            y1 = 50 # marge en hauteur
            # Ecrit l'intervalle de temps
            if self.chrono == 1:  # rends plus lisible si le fond est foncé
                text = f"Δt = {self.app.deltaT:.3f} s"
                self.paintText(self.width() - x1 - 100, y1, text)
                text = f"t = {self.app.deltaT*(self.app.spinBox_chrono.value()-1):.3f} s"
                self.paintText(self.width() - x1 - 100, 2 * y1, text)
            # dessine l'échelle
            if self.chrono == 2:  # chronogramme
                self.painter.setPen(Qt.black)
                if self.video.echelle_faite : #dessine une échelle en haut, horizontalement
                    longueur = round((self.video.echelle_image.p1 - self.video.echelle_image.p2).norme)
                    self.painter.drawLine(x1, y1-10, x1, y1+10)
                    self.painter.drawLine(x1, y1, longueur+x1, y1)
                    self.painter.drawLine(longueur+x1, y1-10, longueur+x1, y1+10)
                    text = "d = {0:.2e} m".format(self.video.echelle_image.longueur_reelle_etalon)
                    self.paintText(
                        max(x1+round((longueur/2)-(text_width/2)), 0), y1+30,
                        text,
                        color = Qt.black,
                        bgcolor = None
                    )
                else : #échelle non faite
                    self.paintText(
                        x1, y1+20,
                        "échelle non précisée",
                         color = Qt.black,
                         bgcolor = None)
                self.painter.end()

            ############################################################
            # Peindre l'échelle si chronophotographie
            if self.chrono == 1:  # chronophotographie
                self.painter = QPainter()
                self.painter.begin(self)
                self.painter.setRenderHint(QPainter.Antialiasing)
                pen = QPen(Qt.blue)
                pen.setWidth(3)
                self.painter.setPen(pen)
                if self.video.echelle_faite: 
                    self.painter.drawLine(
                        round(self.video.app.echelle_trace.p1.x),
                        round(self.video.app.echelle_trace.p1.y),
                        round(self.video.app.echelle_trace.p2.x),
                        round(self.video.app.echelle_trace.p2.y))

                    echelle = "d = {0:.2e} m".format(
                            self.video.echelle_image.longueur_reelle_etalon)

                    self.paintText(
                        round(self.video.app.echelle_trace.p1.x),
                        round((self.video.app.echelle_trace.p1.y + self.video.app.echelle_trace.p2.y)/2)+20,
                        echelle,
                        color = Qt.blue,
                        bgcolor = None,
                        fontfamily = "Times",
                        fontsize = 15,
                    )
                else : #pas d'échelle 
                    self.paintText(x1, y1+20, "échelle non précisée",
                                   color = Qt.blue,
                                   bgcolor = None,
                                   fontfamily = "Times",
                                   fontsize = 15,)
                    
                self.painter.end()

        ############################################################

        ############################################################
        # Paint points
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.Antialiasing)

        listePoints = [[self.video.data[t][obj] for obj in self.video.suivis] \
                       for t in self.video.data]
        for no,points in enumerate(listePoints):
            color = 0
            num_point=0
            for point in points:
                if self.referentiel != 0:
                    ptreferentiel = points[int(self.referentiel)-1]
                else:
                    ptreferentiel = vecteur(0, 0)
                    
                if point:
                    if self.chrono == 2:
                        self.painter.setPen(Qt.black)
                    else :
                        self.painter.setPen(QColor(self.couleurs[color]))
                    self.painter.setFont(QFont("", 10))
                    self.painter.translate(
                        round(point.x + self.origine.x - ptreferentiel.x),
                        round(point.y + self.origine.y - ptreferentiel.y))

                    if self.chrono == 2:
                        self.painter.drawLine(-4, 0, 4, 0)
                        self.painter.drawLine(0, -4, 0, 4)
                        self.painter.translate(-10, +10)
                        decal = -25
                        if point.x + decal < 0 : 
                            decal = 5 
                        self.painter.drawText(decal, 5, "M"+"'"*num_point+str(no))
                    else :
                        self.painter.drawLine(-2, 0, 2, 0)
                        self.painter.drawLine(0, -2, 0, 2)
                        self.painter.translate(-10, +10)
                        self.painter.drawText(0, 0, str(color + 1))
                        
                    self.painter.translate(
                        round(-point.x - self.origine.x + ptreferentiel.x) + 10,
                        round(-point.y - self.origine.y + ptreferentiel.y) - 10)
                    color += 1
                    num_point+=1
                    
        self.painter.end()
        ############################################################
        # paint repere
        if not self.chrono == 2 :
            self.painter = QPainter()
            self.painter.begin(self)
            self.painter.setRenderHint(QPainter.Antialiasing)
            self.painter.setPen(Qt.green)
            # self.painter.translate(0,0)
            self.painter.translate(
                round(self.origine_mvt.x), round(self.origine_mvt.y))
            p1 = QPoint(round(self.video.sens_X * (-40)), 0)
            p2 = QPoint(round(self.video.sens_X * (40)), 0)
            p3 = QPoint(round(self.video.sens_X * (36)), 2)
            p4 = QPoint(round(self.video.sens_X * (36)), -2)
            self.painter.scale(1, 1)
            self.painter.drawPolyline(p1, p2, p3, p4, p2)
            self.painter.rotate(self.video.sens_X *
                                self.video.sens_Y * (-90))
            self.painter.drawPolyline(p1, p2, p3, p4, p2)
            self.painter.rotate(self.video.sens_X *
                                self.video.sens_Y * (90))
            self.painter.translate(
                round(-self.origine_mvt.x), round(-self.origine_mvt.y))
            self.painter.end()

        # paint speed vectors if asked

        if self.speedToDraw != []:
            for vector in self.speedToDraw:
                p, vector_speed, i = vector
                if vector_speed != QPoint():  # if speed is not null.
                    self.painter = QPainter()
                    self.painter.begin(self)
                    self.painter.setRenderHint(QPainter.Antialiasing)
                    self.painter.setPen(QColor(self.couleurs[i - 1]))
                    try:
                        speed = vector_speed.norme * float(self.video.echelle_image.mParPx()) / (2 * self.video.deltaT) * float(self.video.checkBoxScale.currentText())
                        self.video.checkBoxScale.setStyleSheet(
                            "background-color:none")
                        path = QPainterPath()
                        path.moveTo(0, 0)
                        path.lineTo(speed, 0)
                        path.lineTo(QPointF(speed - 10, 0) + QPointF(0, 10))
                        path.lineTo(speed - 8, 0)
                        path.lineTo(QPointF(speed - 10, 0) + QPointF(0, -10))
                        path.lineTo(speed, 0)

                        angle = vector_speed.anglePolaire
                        self.painter.translate(round(p.x), round(p.y))
                        self.painter.rotate(degrees(angle))
                        self.painter.drawPath(path)
                        # VERIFIER COORDONÉES ICI
                        self.painter.fillPath(
                            path, QColor(self.couleurs[i - 1]))

                        path.moveTo(0, 0)
                    except ValueError:
                        self.video.checkBoxScale.setStyleSheet(
                            "background-color: red")
                    self.painter.end()
                else:
                    pass  # null speed
