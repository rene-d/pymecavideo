# -*- coding: utf-8 -*-

"""
    videoWidget, a module for pymecavideo:
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

from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QObject, QRect, QPoint, QPointF
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, QCursor, QPen, QColor, QFont, QResizeEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

import os, time

from vecteur import vecteur
from echelle import echelle
from image_widget import ImageWidget
from pointage import Pointage
from globdef import _translate
from cadreur import openCvReader
from toQimage import toQImage

import icon_rc

class VideoWidget(ImageWidget):
    def __init__(self, parent):
        ImageWidget.__init__(self, parent)
        self.app = None        # pointeur vers la fenêtre principale
        self.zoom = None       # pointeur vers le widget de zoom
        self.hotspot = None    # vecteur (position de la souris)
        self.points_ecran = {} # dictionnaire des pointages
        self.cible_icon = ":/data/icones/curseur_cible.svg"        
        pix = QPixmap(self.cible_icon).scaledToHeight(32, 32)
        self.cursor = QCursor(pix)
        self.setCursor(self.cursor)
        self.pos_zoom = vecteur(50, 50)
        self.image_w = self.width()  # deux valeurs par défaut
        self.image_h = self.height() # pas forcément pertinentes
        self.setMouseTracking(True)
        self.origine = vecteur(self.width()//2, self.height()//2)
        self.echelle_image = echelle()  # objet gérant l'échelle
        # TODO
        self.decal = vecteur(0, 0)  # if video is not 4:3, center video

        self.couleurs = ["red", "blue", "cyan", "magenta", "yellow", "gray", "green", "red", "blue", "cyan", "magenta",
                         "yellow", "gray", "green"]
        self.tourne = False
        self.premier_resize = True
        return

    def setApp(self, app):
        """
        Connecte le videoWidget à sa fenêtre principale, et connecte
        aussi les sous-widgets nécessaires, ceux que le videoWidget doit
        pouvoir contrôler
        """
        self.app = app
        self.dbg = app.dbg
        self.horizontalSlider = app.horizontalSlider
        self.spinBox_image = app.spinBox_image
        return
    
    def setZoom(self, zoom):
        self.zoom = zoom
        return
    
    def clear(self):
        self.image = None
        return

    def updateZoom(self, position = None):
        """
        place dans le widget de zoom une image agrandie pertinente
        @param position l'endroit où prendre l'image à agrandir ; si
          position == None (par défaut) ça signifie vecteur(50,50)
        """
        if position is None :
            position = vecteur(50,50)
        self.zoom.fait_crop(self.image, position)
        return
    
    def reinit(self):
        """
        méthode appelée par reinitialise_capture de la fenêtre principale
        """
        self.update()
        self.setCursor(Qt.ArrowCursor)
        self.setEnabled(1)
        self.reinit_origine()
        
    def resizeEvent(self, e):
        if self.premier_resize:  # Au premier resize, la taille est changée mais pas l'origine.
            self.premier_resize = False
            self.reinit_origine()

        if e.oldSize() != QSize(-1, -1):
            if not self.app.tourne:
                ratiow = self.width()/e.oldSize().width()
                ratioh = self.height()/e.oldSize().height()
            else:
                ratiow = self.width()/e.oldSize().height()
                ratioh = self.height()/e.oldSize().width()
            x = self.origine.x*ratiow
            y = self.origine.y*ratioh
            if not self.app.premier_chargement_fichier_mecavideo:
                self.origine = vecteur(x, y)


            if self.echelle_faite:
                x = self.echelle_image.p1.x*ratiow
                y = self.echelle_image.p1.y*ratioh
                if not self.app.premier_chargement_fichier_mecavideo:
                    self.echelle_image.p1 = vecteur(x, y)

                x = self.echelle_image.p2.x*ratiow
                y = self.echelle_image.p2.y*ratioh
                if not self.app.premier_chargement_fichier_mecavideo:
                    self.echelle_image.p2 = vecteur(x, y)
                self.app.feedbackEchelle(
                    self.echelle_image.p1, self.echelle_image.p2)
            #self.app.premier_chargement_fichier_mecavideo = False

    def reinit(self):
        self.updateZoom()
        self.setMouseTracking(True)

    def reinit_origine(self):
        """
        Replace l'origine au centre de l'image
        """
        self.origine = vecteur(self.image_w//2, self.image_h//2)

    def storePoint(self, point):
        if self.app.lance_capture == True:
            self.app.enregistre_dans_listePoints(point)
            self.pos_avant = self.hotspot
            self.app.clic_sur_video_signal.emit()
            self.updateZoom(self.hotspot)
            self.update()

    def mouseReleaseEvent(self, event):
        self.storePoint(vecteur(event.x(), event.y()))

    def enterEvent(self, event):
        if self.app.lance_capture == True and self.app.auto == False:  # ne se lance que si la capture est lancée
            pix = QPixmap(self.cible_icon).scaledToHeight(32, 32)
            self.cursor = QCursor(pix)
            self.setCursor(self.cursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def maj(self, tourne=False):
        self.dbg.p(1, "rentre dans 'label_video.maj'")
        
        if tourne:
            self.tourne = True


    def mouseMoveEvent(self, event):
        if self.app.lance_capture == True and self.app.auto == False:  # ne se lance que si la capture est lancée
            self.hotspot = vecteur(event.x(), event.y())
            self.updateZoom(self.hotspot)

    def cache_zoom(self):
        pass

    def placeImage(self, im, ratio):
        """
        place une image dans le widget, en conservant le ratio de cette image
        @param im une image
        @param ratio le ratio à respecter
        @return l'image, redimensionnée selon le ratio
        """
        self.image_w = min(self.width(), round(self.height() * ratio))
        self.image_h = round(self.image_w / ratio)
        self.setMouseTracking(True)
        image = im.scaled(self.image_w, self.image_h)
        self.app.imageAffichee = image # verrue nécessaire avant met_a_jour_crop
        self.setImage(image)
        self.updateZoom()
        self.reinit_origine()
        return image
    
class VideoPointeeWidget(VideoWidget, Pointage):
    """
    Cette classe permet de gérer une séquence d'images extraites d'une vidéo
    et les pointages qu'on peut réaliser à la souris ou automatiquement,
    pour suivre les mouvements d'un ou plusieurs objets.
    """

    def __init__(self, parent):
        VideoWidget.__init__(self, parent)
        Pointage.__init__(self)
        self.rotation = False  # permet de retourner une vidéo mal prise
        self.image_max = None  # numéro de la dernière image de la vidéo
        self.framerate = None  # nombre d'images par seconde
        # dimensions natives des images de la vidéo
        self.largeurFilm, self.hauteurFilm = None, None
        self.index = None      # index de l'image courante
        self.a_une_image = False # indication quant à une image disponible
        self.imageExtraite = None # référence de l'image courante
        self.origine = None      # position de l'origine sur les images
        self.lance_capture = False # un pointage est en cours
        self.decal = vecteur(0,0)  # décalage des images
        self.echelle_faite = False # vrai quand l'échelle est définie
        return
    
    def paintEvent(self, event):
        if self.a_une_image:
            if self.echelle_faite and self.lance_capture:
                self.updateZoom(self.hotspot)

            self.painter = QPainter()
            self.painter.begin(self)
            if self.image != None:
                self.painter.drawPixmap(
                    round(self.decal.x), round(self.decal.y), self.image)
            ############################################################
            # dessin de l'origine
            longueur_origine = 5
            self.painter.setPen(Qt.green)
            try:
                self.painter.drawLine(
                    round(self.origine.x) - longueur_origine, round(self.origine.y),
                    round(self.origine.x) + longueur_origine, round(self.origine.y))
                self.painter.drawLine(
                    round(self.origine.x), round(self.origine.y) - longueur_origine,
                    round(self.origine.x), round(self.origine.y) + longueur_origine)
                self.painter.drawText(
                    round(self.origine.x), round(self.origine.y) + 15, "O")
            except:
                pass

            ############################################################
            # draw points
            self.dbg.p(
                5, "In videoWidget, paintEvent, self.data :%s" % self.data)
            for date in self.data:
                for obj in self.data[date]:
                    color = int(obj)
                    point = self.data[date][obj]
                    if point:
                        self.painter.setPen(QColor(self.couleurs[color]))
                        self.painter.setFont(QFont("", 10))
                        self.painter.translate(point.x, point.y)
                        self.painter.drawLine(-2, 0, 2, 0)
                        self.painter.drawLine(0, -2, 0, 2)
                        self.painter.translate(-10, +10)
                        self.painter.drawText(0, 0, str(color+1))
                        self.painter.translate(-point.x + 10, -point.y - 10)
            print("YESSSS")
            ############################################################
            # paint repere
            self.painter.setPen(Qt.green)
            self.painter.translate(0, 0)
            try:
                self.painter.translate(
                    round(self.origine.x), round(self.origine.y))
            except AttributeError:
                pass
            p1 = QPoint(round(self.app.sens_X * (-40)), 0)
            p2 = QPoint(round(self.app.sens_X * (40)), 0)
            p3 = QPoint(round(self.app.sens_X * (36)), 2)
            p4 = QPoint(round(self.app.sens_X * (36)), -2)
            self.painter.scale(1, 1)
            self.painter.drawPolyline(p1, p2, p3, p4, p2)
            self.painter.rotate(self.app.sens_X * self.app.sens_Y * (-90))
            self.painter.drawPolyline(p1, p2, p3, p4, p2)
            ############################################################

            self.painter.end()
        return

    def extract_image(self, index):
        """
        extrait une image de la video à l'aide d'OpenCV et l'enregistre
        @param video le nom du fichier video
        @param index le numéro de l'image
        @param force permet de forcer l'écriture d'une image
        """
        self.dbg.p(1, "rentre dans 'extract_image' " + 'index : ' + str(index))
        ok, image_opencv = self.cvReader.getImage(index, self.rotation)
        if not ok:
            self.mets_a_jour_widget_infos(
                _translate("pymecavideo", "Pymecavideo n'arrive pas à lire l'image", None))
            return False, None
        self.a_une_image = ok
        return ok, image_opencv

    def calcul_deltaT(self, ips_from_line_edit=False, rouvre=False):
        """
        Détermination de l'intervalle de temps entre deux images.
        Cela modifie self.deltaT

        @param ips_from_line_edit (faux par défaut) indique qu'on lit 
         deltaT depuis un champ de saisie
        @param rouvre (faux par défaut) indique qu'on lit les données depuis
         un fichier pymecavidéo
        """
        self.dbg.p(1, "rentre dans 'calcul_deltaT'")
        if rouvre:
            # se produit quand on lit un deltaT depuis un fichier mecavideo
            IPS = round(1/self.deltaT)
            self.app.lineEdit_IPS.setText(str(IPS))
        else:
            if not ips_from_line_edit:
                self.deltaT = 1 / self.framerate
                # mets à jour le widget contenant les IPS
                self.app.lineEdit_IPS.setText(str(self.framerate))
            else:
                IPS = int(self.app.lineEdit_IPS.text())
                self.framerate = IPS
                self.deltaT = 1 / IPS
        return
    
    def active_controle_image(self, state=True):
        """
        Gère les deux widgets horizontalSlider et spinBox_image
        @param state (vrai par défaut) ; si state == True, les deux
          widgets sont activés et leurs signaux valueChanged sont pris
          en compte ; sinon ils sont désactivés ainsi que les signaux
        """
        if state:
            self.horizontalSlider.setMinimum(1)
            self.spinBox_image.setMinimum(1)
            if self.image_max:
                self.horizontalSlider.setMaximum(int(self.image_max))
                self.spinBox_image.setMaximum(int(self.image_max))
            self.horizontalSlider.valueChanged.connect(
                self.app.affiche_image_slider_move)
            self.spinBox_image.valueChanged.connect(self.app.affiche_image_spinbox)
        else:
            if self.horizontalSlider.receivers(self.horizontalSlider.valueChanged):
                self.horizontalSlider.valueChanged.disconnect()
            if self.spinBox_image.receivers(self.spinBox_image.valueChanged):
                self.spinBox_image.valueChanged.disconnect()
        self.horizontalSlider.setEnabled(state)
        self.spinBox_image.setEnabled(state)
        return
        
    def affiche_echelle(self):
        """
        affiche l'échelle courante pour les distances sur l'image
        """
        self.dbg.p(1, "rentre dans 'affiche_echelle'")
        if self.echelle_image.isUndef():
            self.app.echelleEdit.setText(
                _translate("pymecavideo", "indéf.", None))
            self.app.Bouton_Echelle.setEnabled(True)
        else:
            epxParM = self.echelle_image.pxParM()
            if epxParM > 20:
                self.app.echelleEdit.setText("%.1f" % epxParM)
            else:
                self.app.echelleEdit.setText("%8e" % epxParM)
        self.app.echelleEdit.show()
        self.app.Bouton_Echelle.show()
        return

    def init_image(self):
        """intialise certaines variables lors le la mise en place d'une nouvelle image"""
        self.dbg.p(1, "rentre dans 'init_image'")
        self.index = 1
        ok, self.image_opencv = self.extract_image(self.index)
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = \
            self.cvReader.recupere_avi_infos(self.rotation)
        # openCV renvoir quelques flottants, qu'il faut convertir en entiers
        self.framerate = round(self.framerate)
        self.image_max = round(self.image_max)
        self.ratio = self.largeurFilm / self.hauteurFilm
        self.app.init_interface()
        self.trajectoire = {}
        self.calcul_deltaT()
        # on dimensionne les données pour les pointages
        self.dimensionne(1, self.deltaT, self.image_max)
        self.active_controle_image()
        self.extract_image(1)
        self.echelle_image = echelle()
        self.affiche_echelle()
        self.affiche_image()
        return

    def affiche_image(self):
        self.dbg.p(1, "rentre dans 'affiche_image'" + ' ' +
                   str(self.index) + ' ' + str(self.image_max))
        if self.index <= self.image_max:
            self.dbg.p(1, "affiche_image " +
                       "self.index <= self.image_max")
            ok, self.image_opencv = self.extract_image(
                self.index)  # 2ms
            self.imageExtraite = toQImage(self.image_opencv)
            self.dbg.p(2, "Image extraite : largeur : %s, hauteur %s: " % (
                self.imageExtraite.width(), self.imageExtraite.height()))
            self.afficheJusteImage()  # 4 ms
            if self.horizontalSlider.value() != self.index:
                self.dbg.p(1, "affiche_image " + "horizontal")
                i = int(self.index)
                self.horizontalSlider.setValue(i)
                self.spinBox_image.setValue(i)  # 0.01 ms
        elif self.index > self.image_max:
            self.index = self.image_max
            self.lance_capture = False
        return
    
    def afficheJusteImage(self):
        if self.a_une_image:
            self.placeImage(self.imageExtraite, self.ratio)
        return
    
    def init_cvReader(self):
        """
        Initialise le lecteur de flux vidéo pour OpenCV
        et recode la vidéo si nécessaire.
        """
        self.dbg.p(1, "rentre dans 'init_cvReader', ouverture de %s" %
                   (self.filename))
        self.cvReader = openCvReader(self.filename)
        time.sleep(0.1)
        if not self.cvReader.ok:
            QMessageBox.warning(None, "Format vidéo non pris en charge",
                                _translate("pymecavideo", """\le format de cette vidéo n'est pas pris en charge par pymecavideo""",
                                           None),
                                QMessageBox.Ok, QMessageBox.Ok)
        else:
            return True

    def openTheFile(self, filename):
        """
        Ouvre le fichier de nom filename, enregistre les préférences de
        fichier vidéo.
        @param filename nom du fichier
        """
        self.dbg.p(1, "rentre dans 'openTheFile'")
        if not filename :
            return
        self.filename = filename
        goOn = self.init_cvReader()
        if goOn:  # le fichier vidéo est OK, et son format est reconnu
            self.init_image()
            self.app.init_capture(filename)
            self.change_axe_ou_origine()
        else:
            QMessageBox.warning(
                None,
                _translate("pymecavideo", "Erreur lors de la lecture du fichier", None),
                _translate("pymecavideo", "Le fichier<b>{0}</b> ...\nn'est peut-être pas dans un format vidéo supporté.", None).format(
                    filename),
                QMessageBox.Ok, QMessageBox.Ok)
        return
    
    def change_axe_ou_origine(self, origine=None):
        """mets à jour le tableau de données"""
        self.dbg.p(1, "rentre dans 'change_axe_ou_origine'")
        self.dbg.p(3, "valeur de l'origine en argument %s"%(origine))
        # repaint axes and define origine
        if origine is not None:
            self.origine = origine
        self.app.trajectoire_widget.origine_mvt = self.origine
        self.app.trajectoire_widget.update()
        self.update()
        return
    
    def clic_sur_la_video(self, liste_points=None, interactif=True):
        self.dbg.p(1, "rentre dans 'clic_sur_video'")
        self.lance_capture = True
        # on fait des marques pour les points déjà visités
        self.point_attendu = len(self.listePoints) % self.nb_de_points
        self.dbg.p(2, "self.point_attendu %s" % self.point_attendu)
        self.affiche_point_attendu(self.point_attendu)
        if self.index_de_l_image <= self.image_max:  # si on n'atteint pas encore la fin de la vidéo
            self.lance_capture = True
            self.stock_coordonnees_image(
                ligne=int((len(self.listePoints)-1)/self.nb_de_points))
            if interactif:
                self.modifie = True
            self.clic_sur_video_ajuste_ui(self.point_attendu)
        if self.index_de_l_image > self.image_max:
            self.lance_capture = False
            self.mets_a_jour_widget_infos(_translate(
                "pymecavideo", "Vous avez atteint la fin de la vidéo", None))
            self.index_de_l_image = self.image_max
        self.nb_clics += 1
        if self.nb_clics == self.nb_de_points:
            self.nb_clics = 0
            self.index_de_l_image += 1
            self.affiche_image()

            if self.refait_point : #quandon refait 1 seul point faux.
                self.fin_refait_point_depuis_tableau()
        return
    
