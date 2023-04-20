# -*- coding: utf-8 -*-

"""
    trajectoireWidget, a module for pymecavideo:
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
    QTableWidgetSelectionRange

import os, time, re, sys
import locale

from version import Version
from vecteur import vecteur
from image_widget import ImageWidget
from globdef import cible_icon, DOCUMENT_PATH, inhibe, pattern_float
from toQimage import toQImage
from suivi_auto import SelRectWidget
from detect import filter_picture
from cadreur import Cadreur, openCvReader
from dbg import Dbg

import interfaces.icon_rc

from interfaces.Ui_trajectoire import Ui_trajectoire
from etatsTraj import Etats

class TrajectoireWidget(QWidget, Ui_trajectoire, Etats):
    """
    Le widget principal de l'onglet des trajectoires

    Paramètres du constructeur :
    @param parent l'onglet des trajectoires
    """
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        Ui_trajectoire.__init__(self)
        Etats.__init__(self)
        self.setupUi(self)
        self.connecte_ui()
        self.trace.connect(self.traceTrajectoires)
        self.redessine_pixmap.connect(self.defini_pixmap)
        return
    
    ############ les signaux spéciaux #####################
    trace = pyqtSignal(str)
    redessine_pixmap = pyqtSignal()

    def setApp(self, app):
        """
        Crée des pointeurs locaux vers les widgets importants, le débogueur
        et les préférences ; connecte aussi les widgets importants dans
        le sous-widget self.trajW
        """
        self.app = app
        self.dbg = app.dbg
        self.prefs = app.prefs
        self.pointage = app.pointage
        self.video = app.pointage.video
        ###
        self.trajW.pointage = self.pointage
        self.trajW.video = self.video
        self.trajW.trajectoire = self
        return

    def connecte_ui(self):
        """
        Connecte les signaux des sous-widgets
        """
        self.pushButton_save.clicked.connect(self.enregistreChrono)
        self.spinBox_chrono.valueChanged.connect(self.changeChronoImg)
        self.comboBox_referentiel.currentIndexChanged.connect(
            self.traceTrajectoires)
        self.checkBoxScale.currentIndexChanged.connect(self.enableSpeed)
        self.checkBoxScale.currentTextChanged.connect(self.enableSpeed)
        self.checkBoxVectorSpeed.stateChanged.connect(self.enableSpeed)
        self.radioButtonSpeedEveryWhere.clicked.connect(self.enableSpeed)
        self.radioButtonNearMouse.clicked.connect(self.enableSpeed)
        self.button_video.clicked.connect(self.montre_video)
        self.comboBoxChrono.currentIndexChanged.connect(self.chronoPhoto)
        return
    
    def apply_preferences(self):
        """
        Récupère les préférences sauvegardées, et en applique les données
        ici on s'occupe de ce qui se gère facilement au niveau de la
        fenêtre principale
        """
        self.dbg.p(2, "rentre dans 'trajectoireWidget.apply_preferences'")
        d = self.prefs.config["DEFAULT"]
        self.radioButtonNearMouse.setChecked(d["proximite"] == "True")
        return

    def enregistreChrono(self):
        self.pixmapChrono = QPixmap(self.trajW.size())
        self.trajW.render(self.pixmapChrono)
        base_name = os.path.splitext(os.path.basename(self.pointage.filename))[0]
        defaultName = os.path.join(DOCUMENT_PATH, base_name)+".jpg"
        fichier = QFileDialog.getSaveFileName(self,
                                              self.tr("Enregistrer comme image"),
                                              defaultName, self.tr("fichiers images(*.png *.jpg)"))
        try :
            self.pixmapChrono.save(fichier[0])
        except Exception as err:
            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
            QMessageBox.critical(None, self.tr("Erreur lors de l'enregistrement"), self.tr("Echec de l'enregistrement du fichier:<b>\n{0}</b>").format(
                    fichier[0]))

    def defini_pixmap(self):
        """appelé par le signal redessine_pixmap, a chaque changement de type de trajectoire à afficher autre que celui par défaut"""

        #self.trajW.setImage(QPixmap())
        self.trajW.update()

    def chronoPhoto(self):
        """lance la sauvegarde du trajW.
        Si chronophotographie, on ajoute l'image et la trace de l'échelle comme pointée.
        Si chronophotogramme, on ne met pas l'image et la trace est en haut.
        """
        self.dbg.p(2, "rentre dans 'chronoPhoto'")

        # Configure l'UI en fonction du mode
        if self.comboBoxChrono.currentIndex() == 0 :
            self.widget_chronophoto.setEnabled(False)
            self.trajW.setEnabled(True)
            self.widget_speed.setEnabled(True)
        elif self.comboBoxChrono.currentIndex() == 1 :
            self.widget_chronophoto.setEnabled(True)
            self.trajW.setEnabled(False)
            self.widget_speed.setEnabled(False)
            self.checkBoxVectorSpeed.setChecked(False)
            self.spinBox_chrono.setMaximum(int(self.pointage.image_max))
            self.spinBox_chrono.setMinimum(1)


        elif self.comboBoxChrono.currentIndex() == 2 :
            self.widget_chronophoto.setEnabled(False)
            self.trajW.setEnabled(False)
            self.widget_speed.setEnabled(False)
            self.checkBoxVectorSpeed.setChecked(False)
        # ajoute la première image utilisée pour le pointage sur le fond du vidget
        liste_types_photos = ['chronophotographie', 'chronophotogramme']

        self.widget_speed.update() #nécessaire pour la prise en compte du setEnabled

        if self.comboBoxChrono.currentIndex() != 0:
            photo_chrono = liste_types_photos[self.comboBoxChrono.currentIndex(
            )-1]
            self.dbg.p(2, "dans 'chronoPhoto, on a choisi le type %s'" %
                       (photo_chrono))
            if photo_chrono == 'chronophotographie':  # on extrait le première image que l'on rajoute au widget
                self.trajW.chrono = 1  # 1 pour chronophotographie
                ok, img = self.pointage.cvReader.getImage(
                    self.chronoImg, self.pointage.video.rotation)
                self.imageChrono = toQImage(img).scaled(
                    self.pointage.video.image_w, self.pointage.video.image_h) #, Qt.KeepAspectRatio)
                self.trajW.setImage(
                    QPixmap.fromImage(self.imageChrono))
            else:
                self.trajW.chrono = 2  # 2 pour chronophotogramme
                self.trajW.setImage(QPixmap())

            #self.enregistreChrono()
        else:
            self.trajW.chrono = 0
            #self.redessine_pixmap.emit()
            self.trajW.setImage(QPixmap())
        self.redessine_pixmap.emit()
        self.update()
        self.app.redimensionneFenetre()
        return

    def changeChronoImg(self,img):
        self.dbg.p(2, "rentre dans 'changeChronoImg'")

        self.chronoImg = img
        self.chronoPhoto()

    def enableSpeed(self, secondParam=None):
        """
        Quand on veut afficher le vecteur vitesse,
        on active le spinbox qui permet de choisir une échelle.
        Quand on ne veut plus, on peut cacher le spinbox.
        @param secondParam peu utile mais nécessaire : certains modes
          de rappel de cette fonction ont un paramètre supplémentaire
        """
        self.dbg.p(2, "rentre dans 'enableSpeed'")
        if self.checkBoxVectorSpeed.isChecked():
            self.dbg.p(2, "In enableSpeed")
            self.checkBoxScale.setEnabled(1)
            if self.checkBoxScale.count() < 1:
                self.checkBoxScale.insertItem(0, "1")
            self.radioButtonNearMouse.show()
            self.radioButtonSpeedEveryWhere.show()
            self.trajW.prepare_vecteurs_pour_paint()
            self.trajW.update()
        else:
            self.checkBoxScale.setEnabled(0)
            self.radioButtonNearMouse.hide()
            self.radioButtonSpeedEveryWhere.hide()
            self.trajW.update()
        return

    def montre_video(self):
        self.dbg.p(2, "rentre dans 'montre_video'")
        ref = self.comboBox_referentiel.currentText().split(" ")[-1]
        if len(ref) == 0 or ref == "camera":
            return
        c = Cadreur(int(ref), self)
        c.montrefilm()
        return

    def traceTrajectoires(self, laquelle):
        """
        fonction de rappel du signal "trace"
        Cette fonction est appelée par un changement de référentiel.
        On peut aussi appeler cette fonction directement, auquel cas on
        donne la valeur "absolu" à newValue pour reconnaître ce cas.
        efface les trajectoires anciennes, puis
        trace les trajectoires en fonction du référentiel choisi.
        
        @param laquelle désignation de la trajectoire ("absolu" = réf. camera)
        """
        self.dbg.p(2, "rentre dans 'traceTrajectoire'")
        self.trajW.origine_mvt = self.pointage.origine
        if laquelle == "absolu":
            ref = 0 # la caméra
            # mets à jour le comboBox referentiel :
            self.comboBox_referentiel.setCurrentIndex(
                self.comboBox_referentiel.count()-1)
            self.comboBox_referentiel.update()
        else:
            choix_ref = self.comboBox_referentiel.currentText()
            # on évite le cas où le combobox a été vidé, entre deux sessions 
            if choix_ref == "":
                return
            elif choix_ref == "camera":
                ref = 0
            else:
                ref = int(choix_ref.split(" ")[-1])
        if ref != 0:
            self.button_video.setEnabled(1)
            self.trajW.chrono = False
            origine = vecteur(self.pointage.width() // 2, self.pointage.height() // 2)
            self.trajW.origine = origine
            self.trajW.origine_mvt = origine
            self.trajW.referentiel = ref
        else:  # si le référentiel est la caméra, aucune translation !
            self.trajW.referentiel = 0
            self.trajW.origine = vecteur(0, 0)
        self.dbg.p(3, "origine %s, ref %s" %
                   (str(self.trajW.origine), str(ref)))
        self.trajW.prepare_vecteurs_pour_paint()
        self.trajW.update()
        return
    
