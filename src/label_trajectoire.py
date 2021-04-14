# -*- coding: utf-8 -*-
"""
    Label_Video, a module for pymecavideo:
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
from math import sqrt, atan2, degrees

from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QRect, QPoint, QPointF
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPicture, QPainter, QColor, QFont, QPainterPath, QPen
from PyQt5.QtWidgets import QLabel, QApplication, QMainWindow, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from vecteur import vecteur


class Label_Trajectoire(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)

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

    def reDraw(self):
        """call when somthing change as repere, origine ..."""
        self.giveCoordonatesToPaint()
        # self.maj()
        self.repaint()

    def maj(self):
        #self.setGeometry(QRect(120, 100, self.label_video.width(), self.label_video.height()))
        self.origine_mvt = self.label_video.origine

    def giveCoordonatesToPaint(self):
        self.speedToDraw = []
        if self.label_video.app.ui.checkBoxVectorSpeed.isChecked():
            for key in self.label_video.app.points.keys():
                points = self.label_video.app.points[key]
                for i in range(len(points)):
                    wroteSpeed = False

                    point = points[i]
                    try:
                        if self.referentiel != 0:
                            ptreferentiel = points[int(self.referentiel)]

                            try:
                                ptreferentielAfter = self.label_video.app.points[key + 1][int(
                                    self.referentiel)]
                                ptreferentielBefore = self.label_video.app.points[key - 1][int(
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
                        if self.label_video.app.ui.radioButtonNearMouse.isChecked() and self.pos_souris != None:
                            near = 20
                            pos = self.pos_souris
                            distance = QPoint(point.x() + self.origine.x() - ptreferentiel.x(),
                                              point.y() + self.origine.y() - ptreferentiel.y()) - pos
                            if distance.manhattanLength() < near:
                                self.label_video.app.dbg.p(
                                    2, "mouse near a point")
                                wroteSpeed = True

                        elif self.label_video.app.ui.radioButtonSpeedEveryWhere.isChecked():
                            wroteSpeed = True

                        if wroteSpeed:
                            keyMax = len(self.label_video.app.points.keys())
                            # first and last point can't have speed.
                            if key != 0 and key != keyMax - 1:
                                # coordonnates of n-1 and n+1 point
                                try:
                                    tempsAfter = float(
                                        self.label_video.app.points[key + 1][0])/self.label_video.app.deltaT  # en "delta_T"
                                    tempsBefore = float(
                                        self.label_video.app.points[key-1][0])/self.label_video.app.deltaT  # en "delta_T"
                                    pointBefore = QPoint(
                                        (self.label_video.app.points[key - 1][i].x() + self.origine.x(
                                        ) - ptreferentielBefore.x())/(tempsAfter-tempsBefore),
                                        (self.label_video.app.points[key - 1][i].y() + self.origine.y() - ptreferentielBefore.y())/(tempsAfter-tempsBefore))

                                    pointAfter = QPoint(
                                        (self.label_video.app.points[key + 1][i].x() + self.origine.x(
                                        ) - ptreferentielAfter.x())/(tempsAfter-tempsBefore),
                                        (self.label_video.app.points[key + 1][i].y() + self.origine.y() - ptreferentielAfter.y())/(tempsAfter-tempsBefore))

                                    vector_speed = pointAfter - pointBefore

                                    self.speedToDraw.append((QPoint(point.x() + self.origine.x() - ptreferentiel.x(),
                                                                    point.y() + self.origine.y() - ptreferentiel.y()),
                                                             vector_speed, i))
                                except KeyError:  # last point -> can't compute speed
                                    pass
                                except IndexError:  # si pas le bon nb de points
                                    pass

    def mouseMoveEvent(self, event):
        # Look if mouse is near a point
        self.pos_souris = event.pos()
        if self.label_video.app.ui.radioButtonNearMouse.isChecked():
            self.reDraw()

    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)
       # self.painter.save()
        self.painter.fillRect(
            QRect(0, 0, self.label_video.width(), self.label_video.height()), QColor("grey"))
        self.painter.setRenderHint(QPainter.Antialiasing)

        ############################################################
        # paint the origin
        self.painter.setPen(Qt.green)
        self.painter.drawLine(self.origine_mvt.x() - 5, self.origine_mvt.y(), self.origine_mvt.x() + 5,
                              self.origine_mvt.y())
        self.painter.drawLine(self.origine_mvt.x(), self.origine_mvt.y() - 5, self.origine_mvt.x(),
                              self.origine_mvt.y() + 5)
        self.painter.drawText(self.origine_mvt.x(),
                              self.origine_mvt.y() + 15, "O")
        self.painter.end()

        # peint les informations pour le mode chronophotographie
        if self.chrono:  # ceci est géré dans pymecavideo.py, chercher : self.label_trajectoire.chrono

            self.painter = QPainter()
            self.painter.begin(self)
            self.painter.drawPixmap(0, 0, self.pixmap())
            font = QFont()
            font.setPointSize(15)
            self.painter.setFont(font)
            self.painter.setRenderHint(QPainter.TextAntialiasing)
            self.painter.setRenderHint(QPainter.Antialiasing)

            if self.chrono == 1:  # rends plus lisible si le fond est foncé
                self.painter.setPen(Qt.white)
                self.painter.setBrush(Qt.lightGray)
                self.painter.drawRect(self.width()-210, 30, 120, 30)
            self.painter.setPen(Qt.blue)
            try:
                self.painter.drawText(self.width(
                )-200, 50, unicode("{0}t = {1:.3f} s").format(unichr(916), self.label_video.app.deltaT))
            except NameError:
                self.painter.drawText(self.width(
                )-200, 50, "{0}t = {1:.3f} s".format(chr(916), self.label_video.app.deltaT))
            # dessine l'échelle
            if self.chrono == 2:  # chronophotogramme
                try:
                    longueur = sqrt((self.label_video.echelle_image.p1.x()-self.label_video.echelle_image.p2.x(
                    ))**2 + (self.label_video.echelle_image.p1.y()-self.label_video.echelle_image.p2.y())**2)
                    self.painter.drawLine(100, 60, 100, 80)
                    self.painter.drawLine(100, 70, longueur+100, 70)
                    self.painter.drawLine(longueur+100, 60, longueur+100, 80)
                    self.painter.drawText((longueur)/2, 120, unicode("d = {0:.2f} m").format(
                        self.label_video.echelle_image.longueur_reelle_etalon))
                except AttributeError:
                    pass  # échelle non faite
                except NameError:
                    longueur = sqrt((self.label_video.echelle_image.p1.x()-self.label_video.echelle_image.p2.x(
                    ))**2 + (self.label_video.echelle_image.p1.y()-self.label_video.echelle_image.p2.y())**2)
                    self.painter.drawLine(100, 60, 100, 80)
                    self.painter.drawLine(100, 70, longueur+100, 70)
                    self.painter.drawLine(longueur+100, 60, longueur+100, 80)
                    self.painter.drawText((longueur)/2, 120, "d = {0:.2f} m".format(
                        self.label_video.echelle_image.longueur_reelle_etalon))
            self.painter.end()

            ############################################################
            # Peindre l'échelle si chronophotographie
            if self.chrono == 1:  # chronophotographie
                self.painter = QPainter()
                self.painter.begin(self)
                self.painter.setFont(QFont("Times", 16, QFont.Bold))
                self.painter.setRenderHint(QPainter.Antialiasing)
                pen = QPen(Qt.darkBlue)
                pen.setWidth(5)
                self.painter.setPen(pen)
                self.painter.drawLine(self.label_video.app.label_echelle_trace.p1.x(), self.label_video.app.label_echelle_trace.p1.y(
                ), self.label_video.app.label_echelle_trace.p2.x(), self.label_video.app.label_echelle_trace.p2.y())

                echelle = str(
                    self.label_video.echelle_image.longueur_reelle_etalon)

                echelle += ' (m)'
                self.painter.drawText(self.label_video.app.label_echelle_trace.p1.x(
                )-30, int((self.label_video.app.label_echelle_trace.p1.y()+self.label_video.app.label_echelle_trace.p2.y())/2), echelle)
                self.painter.end()

        ############################################################

        ############################################################
        # Paint points
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.Antialiasing)

        listePoints = []
        listeParImage = []

        for point in self.label_video.app.listePoints:
            #    #TODO :si quelqu'un veut implémenter un slicing de l'objet listePointee...
            listeParImage.append(point[2])
            if len(listeParImage) % self.label_video.app.nb_de_points == 0:
                listePoints.append(listeParImage)
                listeParImage = []

        for points in listePoints:
            color = 0
            for point in points:
                if self.referentiel != 0:
                    ptreferentiel = points[int(self.referentiel)-1]

                else:
                    ptreferentiel = vecteur(0, 0)
                if type(point) != type(""):
                    self.painter.setPen(QColor(self.couleurs[color]))
                    self.painter.setFont(QFont("", 10))
                    self.painter.translate(point.x() + self.origine.x() - ptreferentiel.x(),
                                           point.y() + self.origine.y() - ptreferentiel.y())

                    self.painter.drawLine(-2, 0, 2, 0)
                    self.painter.drawLine(0, -2, 0, 2)
                    self.painter.translate(-10, +10)
                    self.painter.drawText(0, 0, str(color + 1))
                    self.painter.translate(-point.x() - self.origine.x() + ptreferentiel.x() + 10,
                                           -point.y() - 10 - self.origine.y() + ptreferentiel.y())
                    color += 1
        self.painter.end()
        ############################################################
        # paint repere
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.Antialiasing)
        self.painter.setPen(Qt.green)
        # self.painter.translate(0,0)
        self.painter.translate(self.origine_mvt.x(), self.origine_mvt.y())
        p1 = QPoint(self.label_video.app.sens_X * (-40), 0)
        p2 = QPoint(self.label_video.app.sens_X * (40), 0)
        p3 = QPoint(self.label_video.app.sens_X * (36), 2)
        p4 = QPoint(self.label_video.app.sens_X * (36), -2)
        self.painter.scale(1, 1)
        self.painter.drawPolyline(p1, p2, p3, p4, p2)
        self.painter.rotate(self.label_video.app.sens_X *
                            self.label_video.app.sens_Y * (-90))
        self.painter.drawPolyline(p1, p2, p3, p4, p2)
        self.painter.rotate(self.label_video.app.sens_X *
                            self.label_video.app.sens_Y * (90))
        self.painter.translate(-self.origine_mvt.x(), -self.origine_mvt.y())
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
                        speed = sqrt(vector_speed.x() ** 2 + vector_speed.y() ** 2) * float(self.label_video.echelle_image.mParPx()) \
                            / (2 * self.label_video.app.deltaT) * float(self.label_video.app.ui.checkBoxScale.currentText())
                        self.label_video.app.ui.checkBoxScale.setStyleSheet(
                            "background-color:none")
                        path = QPainterPath()
                        path.moveTo(0, 0)
                        path.lineTo(speed, 0)
                        path.lineTo(QPointF(speed - 10, 0) + QPointF(0, 10))
                        path.lineTo(speed - 8, 0)
                        path.lineTo(QPointF(speed - 10, 0) + QPointF(0, -10))
                        path.lineTo(speed, 0)

                        angle = atan2(float(vector_speed.y()),
                                      float(vector_speed.x()))
                        self.painter.translate(p.x(), p.y())
                        self.painter.rotate(degrees(angle))
                        self.painter.drawPath(path)
                        # VERIFIER COORDONÉES ICI
                        self.painter.fillPath(
                            path, QColor(self.couleurs[i - 1]))

                        path.moveTo(0, 0)
                    except ValueError:
                        self.label_video.app.checkBoxScale.setStyleSheet(
                            "background-color: red")
                    self.painter.end()
                else:
                    pass  # null speed
