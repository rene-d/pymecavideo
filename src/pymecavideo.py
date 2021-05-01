# -*- coding: utf-8 -*-

import subprocess
import os.path
import os
from globdef import HOME_PATH, VIDEO_PATH, CONF_PATH, \
    ICON_PATH, LANG_PATH, \
    DATA_PATH, HELP_PATH, DOCUMENT_PATH
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QVBoxLayout, QTableWidgetSelectionRange, QDialog, QAction, QPushButton
import getopt
import locale
import traceback
import time
import sys
from aspectlayout import AspectLayout
import functools
from detect import filter_picture
import numpy as np
import math
import tempfile
import platform
import threading
from export import Export, EXPORT_FORMATS
import re
from echelle import Label_Echelle_Trace
from toQimage import toQImage
from dialogencode import QMessageBoxEncode
from label_auto import Label_Auto
from version import Version
from listes import listePointee
from dbg import Dbg
from preferences import Preferences
from cadreur import Cadreur, openCvReader
from label_origine import Label_Origine
from label_trajectoire import Label_Trajectoire
from label_video import Label_Video
from echelle import Label_Echelle, echelle
from glob import glob
import pyqtgraph as pg
import pyqtgraph.exporters
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer
from PyQt5 import uic
from vecteur import vecteur
import icon_rc
licence = {}
licence['en'] = """
    pymecavideo version %s:

    a program to track moving points in a video frameset
    
    Copyright (C) 2007-2016 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2018 Georges Khaznadar <georgesk@debian.org>

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

licence['fr'] = u"""
    pymecavideo version %s :

    un programme pour tracer les trajectoires des points dans une vidéo.
    
    Copyright (C) 2007-2016 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2018 Georges Khaznadar <georgesk@debian.org>
    
    Ce projet est un logiciel libre : vous pouvez le redistribuer, le modifier selon les terme de la GPL (GNU Public License) dans les termes de la Free Software Foundation concernant la version 3 ou plus de la dite licence.
    
    Ce programme est fait avec l'espoir qu'il sera utile mais SANS AUCUNE GARANTIE. Lisez la licence pour plus de détails.
    
    <http://www.gnu.org/licenses/>.
"""
#
# Le module de gestion des erreurs n'est chargé que si on execute le fichier .exe ou si on est sous Linux
#
# if sys.platform == "win32" or sys.argv[0].endswith(".exe"):
# import Error
thisDir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, thisDir)


#from export_python import ExportDialog
# création précoce de l'objet application, déjà nécessaire pour traiter les bugs
app = QApplication(sys.argv)


#import qtiplotexport


def time_it(func):
    """Timestamp decorator for dedicated functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        mlsec = repr(elapsed).split('.')[1][:3]
        readable = time.strftime(
            "%H:%M:%S.{}".format(mlsec), time.gmtime(elapsed))
        print('Function "{}": {} sec'.format(func.__name__, readable))
        return result
    return wrapper


def _translate(context, text, disambig):
    return QApplication.translate(context, text, disambig)


class MonThreadDeCalcul2(QThread):
    """Thread permettant le calcul des points automatiquement. Version Qt. 20/04/2015 : focntionne mal sous windows"""

    def __init__(self, parent, motif, image, tmpdir):
        QThread.__init__(self)
        self.parent = parent
        self.parent.dbg.p(1, "rentre dans 'monThreadDeCalcul'")
        self.motif = motif
        self.image = image
        self.tmpdir = tmpdir
        self.stopped = False

    def run(self):
        """
        lance le thread.
        stocke les coordonnées des points trouvés
        Envoi un signal quand terminé.
        """
        while not self.stopped:
            self.parent.picture_detect(self.tmpdir)
        self.terminate

    def stop(self):
        self.stopped = True


class MonThreadDeCalcul(QThread):
    """Thread permettant le calcul des points automatiquement. Version Qt. 20/04/2015 : focntionne mal sous windows"""

    def __init__(self, parent, motif, image, tmpdir):
        QThread.__init__(self)
        self.parent = parent
        self.parent.dbg.p(1, "rentre dans 'monThreadDeCalcul'")
        self.motif = motif
        self.image = image
        self.tmpdir = tmpdir
        self.stopped = False

    def run(self):
        """
        lance le thread.
        stocke les coordonnées des points trouvés
        Envoi un signal quand terminé.
        """
        while not self.stopped:
            self.parent.picture_detect(self.tmpdir)
        self.terminate

    def stop(self):
        self.stopped = True


class StartQt5(QMainWindow):
    def __init__(self, parent=None, opts=[], args=[]):
        """
        le constructeur reçoit les données principales du logiciel : 
        @param parent le widget parent, None pour une fenêtre principale
        @param opts les options de l'invocation bien rangées en tableau
        @param args les arguments restants après raitement des options
        """
        # QT
        QMainWindow.__init__(self)
        QWidget.__init__(self, parent)
        self.hauteur = 1
        self.largeur = 0
        self.ratio = 4/3
        self.decalh = 0
        self.decalw = 0
        self.rotation = 0  # permet de retourner une vidéo mal prise
        # points utilisés pour la détection automatique, définissent une zone où il est probable de trouver un objet suivi
        self.pointsProbables = [None]
        self.methode_thread = 3  # définit la methode de calcul à utiliser pour la détection auto. 1 : 1 thread de calcul  2 : découpage en plusieurs thread 3: 1 thread<-> 1 calcul
        
        # Mode plein écran
        self.plein_ecran = False
        QShortcut(QKeySequence(Qt.Key_F11), self, self.basculer_plein_ecran)

        self.height_screen, self.width_screen = QDesktopWidget(
        ).screenGeometry().height(), QDesktopWidget().screenGeometry().width()

        from Ui_pymecavideo_mini_layout import Ui_pymecavideo

        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowSystemMenuHint |
                            Qt.WindowMinMaxButtonsHint)

        self.ui = Ui_pymecavideo()
        self.ui.setupUi(self)

        # gestion des layout pour redimensionnement
        self.aspectlayout1 = AspectLayout(self.ratio)
        self.ui.containerWidget1.setLayout(self.aspectlayout1)

        self.aspectlayout2 = AspectLayout(self.ratio)
        self.ui.containerWidget2.setLayout(self.aspectlayout2)

        self.dbg = Dbg(0)
        for o in opts:
            if ('-d' in o[0]) or ('--debug' in o[0]):
                self.dbg = Dbg(o[1])
                self.dbg.p(1, "Niveau de débogage" + o[1])

        self.args = args

        self.cvReader = None

        self.platform = platform.system()
        self.prefs = Preferences(self)
        if len(self.args) > 0:
            # le premier argument éventuel est le nom d'une vidéo
            self.prefs.lastVideo = args[0]

        # intialise les répertoires
        self._dir()
        #defait_icon = os.path.join(self._dir("icones"), "undo.png")

        #self.ui.pushButton_defait.setIcon(QIcon(defait_icon))
        #refait_icon = os.path.join(self._dir("icones"), "redo.png")
        #self.ui.pushButton_refait.setIcon(QIcon(refait_icon))

        # variables à initialiser
        # disable UI at beginning
        self.ui.tabWidget.setEnabled(0)
        self.ui.actionDefaire.setEnabled(0)
        self.ui.actionRefaire.setEnabled(0)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(0)
        self.ui.menuE_xporter_vers.setEnabled(0)
        self.ui.actionSaveData.setEnabled(0)
        self.ui.actionExemples.setEnabled(0)
        self.ui.widget_chronophoto.setEnabled(False)

        # exportCombo
        self.ui.exportCombo.addItem('Exporter vers...')
        # Ajoute les différents formats d'exportation
        for key in sorted(EXPORT_FORMATS.keys()):
            self.ui.exportCombo.addItem(EXPORT_FORMATS[key]['nom'])

        #exportQactions
        for key in sorted(EXPORT_FORMATS.keys()):
            action = QAction(EXPORT_FORMATS[key]
                             ['nom'], self.ui.menuE_xporter_vers)
            action.triggered.connect(
                lambda checked, index=key: self.export(index))
            self.ui.menuE_xporter_vers.addAction(action)

        self.init_variables(opts)
        self.init_interface()
        # connections internes
        self.ui_connections()

        # chargement d'un éventuel premier fichier
        self.splashVideo()

        # prise en compte d'options de la ligne de commande
        self.traiteOptions()

    def hasHeightForWidth(self):
        # This tells the layout manager that the banner's height does depend on its width
        return True

    def sizeHint(self):
        return QSize(1024, 800)

    def showFullScreen_(self):
        #"""gère les dimensions en fonction de la largeur et la hauteur de l'écran"""
        #self.setFixedSize(QSize(self.width_screen,self.height_screen ))
        self.showFullScreen()

    def basculer_plein_ecran(self):
        """Basculer en mode plein écran / mode fenétré"""
        self.dbg.p(1, "rentre dans 'basculer_plein_ecran'")
        if not self.plein_ecran:
            self.showFullScreen()
        else:
            self.showNormal()
        self.plein_ecran = not (self.plein_ecran)

    def splashVideo(self):
        self.dbg.p(1, "rentre dans 'splashVideo'")
        if os.path.isfile(self.filename):
            self.openTheFile(self.filename)
        elif os.path.isfile(self.prefs.lastVideo):
            try:
                self.openTheFile(self.prefs.lastVideo)
            except:
                pass

    def init_variables(self, opts, filename=u""):
        self.dbg.p(1, "rentre dans 'init_variables'")
        self.logiciel_acquisition = False
        self.points_ecran = {}
        self.index_max = 1
        self.sens_X = 1
        self.sens_Y = 1
        self.repere = 0
        self.masse_objet = 0
        self.dictionnairePlotWidget = {}
        # contient les listes des abscisses, vitesses, énergies calculées par le grapheur.
        self.dictionnaire_grandeurs = {}
        self.rouvert = False  # positionné a vrai si on vien d'ouvrir un fichier mecavideo
        self.auto = False
        self.motif = []
        self.lance_capture = False
        # est Vraie si le fichier est odifié. permet de sauvegarder les changements
        self.modifie = False
        self.points = {}  # dictionnaire des points cliqués, par n d'image.
        self.trajectoire = {}  # dictionnaire des points des trajectoires
        self.pX = {}  # points apparaissant à l'écran, indexés par X
        self.pY = {}  # points apparaissant à l'écran, indexés par Y
        self.index_du_point = 0
        self.couleurs = ["red", "blue", "cyan", "magenta", "yellow", "gray",
                         "green"]  # correspond aux couleurs des points de la trajectoire
        self.nb_de_points = 0  # nombre de points suivis
        self.point_attendu = 0
        self.nb_clics = 0
        self.premiere_image = 1  # n° de la première image cliquée
        self.index_de_l_image = 1  # image à afficher
        self.chronoImg = 0
        self.filename = filename
        self.opts = opts
        self.stdout_file = os.path.join(CONF_PATH, "stdout")
        self.exitDecode = False
        self.echelle_faite = False
        self.layout().setSizeConstraint(QLayout.SetMaximumSize)  # TODO
        self.rotation = 0
        try:
            self.ratio = self.determineRatio()
        except:
            pass
        self.listePoints = listePointee()
        self.pileDeDetections = []
        self.premierResize = True  # arrive quand on ouvre la première fois la fenetre
        self.a_une_image = False
        self.resizing = False
        self.stopRedimensionne = False
        self.refait_point = False
        self.graphe_deja_choisi = None
        self.defixeLesDimensions()

    def init_interface(self, refait=0):
        self.dbg.p(1, "rentre dans 'init_interface'")

        self.ui.tabWidget.setEnabled(1)
        if len(self.points) == 0:
            self.ui.tabWidget.setTabEnabled(3, False)
            self.ui.tabWidget.setTabEnabled(2, False)
            self.ui.tabWidget.setTabEnabled(1, False)
        else:  # quando n ouvre un fichier via la ligne de commande
            self.ui.tabWidget.setTabEnabled(3, True)
            self.ui.tabWidget.setTabEnabled(2, True)
            self.ui.tabWidget.setTabEnabled(1, True)
        if not self.a_une_image:
            self.ui.tabWidget.setTabEnabled(0, False)
        self.ui.actionExemples.setEnabled(1)
        try:
            self.label_trajectoire.clear()
        except AttributeError:
            self.label_trajectoire = Label_Trajectoire(
                parent=self.ui.containerWidget2)
            self.aspectlayout2.addWidget(self.label_trajectoire)
            self.label_trajectoire.chrono = False
            self.label_trajectoire.show()

        self.update()
        self.ui.horizontalSlider.setEnabled(0)
        self.ui.echelleEdit.setEnabled(0)
        self.ui.echelleEdit.setText(_translate("pymecavideo", "indéf", None))
        self.ui.Bouton_Echelle.setText(_translate(
            "pymecavideo", "Définir l'échelle", None))
        self.ui.Bouton_Echelle.setStyleSheet("background-color:None;")

        try:
            self.affiche_echelle()
        except:
            pass
        self.ui.tab_traj.setEnabled(0)
        self.ui.actionSaveData.setEnabled(0)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(0)
        self.ui.spinBox_image.setEnabled(0)
        self.affiche_lance_capture(False)
        if not refait:
            self.ui.horizontalSlider.setValue(1)

        self.affiche_nb_points(False)
        self.ui.Bouton_Echelle.setEnabled(False)
        self.ui.checkBoxScale.setDuplicatesEnabled(False)
        self.ui.radioButtonNearMouse.hide()
        self.ui.radioButtonSpeedEveryWhere.hide()

        if not self.a_une_image:
            self.ui.pushButton_rot_droite.setEnabled(0)
            self.ui.pushButton_rot_gauche.setEnabled(0)
        else:
            self.ui.pushButton_rot_droite.setEnabled(1)
            self.ui.pushButton_rot_gauche.setEnabled(1)

        # création du label qui contiendra la vidéo.
        try:
            self.dbg.p(3, "In : init_interface, clear Label_Video")
            self.label_video.clear()
        except AttributeError:
            self.dbg.p(3, "In : init_interface, cree Label_Video")
            self.label_video = Label_Video(
                parent=self.ui.containerWidget1, app=self)
            self.aspectlayout1.addWidget(self.label_video)
            self.label_video.show()

        self.ui.tabWidget.setCurrentIndex(0)  # montre l'onglet video
        self.ui.pushButton_stopCalculs.setEnabled(0)
        self.ui.pushButton_stopCalculs.hide()
        self.ui.button_video.setEnabled(0)
        self.ui.checkBox_Ec.setChecked(0)
        self.ui.checkBox_Em.setChecked(0)
        self.ui.checkBox_Epp.setChecked(0)
        self.label_trajectoire.label_video = self.label_video
        
        #mets à jour le ratio
        try : 
            self.ratio=self.determineRatio()
        except: 
            pass #si lancé prématurément, la vidéo n'est pas chargée
        self.aspectlayout1.aspect = self.ratio
        self.aspectlayout2.aspect = self.ratio

    def affiche_lance_capture(self, active=False):
        """
        Met à jour l'affichage du bouton pour lancer la capture
        @param active vrai si le bouton doit être activé
        """
        self.dbg.p(1, "rentre dans 'affiche_lance_capture'")
        self.ui.Bouton_lance_capture.setEnabled(active)

    def affiche_nb_points(self, active=False):
        """
        Met à jour l'afficheur de nombre de points à saisir
        @param active vrai si on doit permettre la saisie du nombre de points
        """
        self.dbg.p(1, "rentre dans 'affiche_nb_points'")
        self.ui.spinBox_nb_de_points.setEnabled(active)
        self.ui.spinBox_nb_de_points.setValue(self.nb_de_points)

    def affiche_echelle(self):
        """
        affiche l'échelle courante pour les distances sur l'image
        """
        self.dbg.p(1, "rentre dans 'affiche_echelle'")
        if self.label_video.echelle_image.isUndef():
            self.ui.echelleEdit.setText(
                _translate("pymecavideo", "indéf.", None))
            self.ui.Bouton_Echelle.setEnabled(True)
        else:
            epxParM = self.label_video.echelle_image.pxParM()
            if epxParM > 20:
                self.ui.echelleEdit.setText("%.1f" % epxParM)
            else:
                self.ui.echelleEdit.setText("%8e" % epxParM)
        self.ui.echelleEdit.show()
        self.ui.Bouton_Echelle.show()

    def reinitialise_capture(self):
        """
        Efface toutes les données de la capture en cours et prépare une nouvelle
        session de capture.
        """
        self.dbg.p(1, "rentre dans 'reinitialise_capture'")
        self.montre_vitesses = False
        try:
            self.label_trajectoire.update()  # premier lancement sans fichier
        except AttributeError:
            pass

        # ferme les widget d'affichages des x, y, v du 2e onglets si elles existent
        for plotwidget in self.dictionnairePlotWidget.values():
            plotwidget.parentWidget().close()
            plotwidget.close()
            del plotwidget

        self.rotation = 0
        self.defixeLesDimensions()
        # remet le ratio à l'initialisation
        ratio = self.determineRatio()
        self.aspectlayout1.aspect = ratio
        self.aspectlayout2.aspect = ratio
        try:
            self.label_video.update()
            self.label_video.setCursor(Qt.ArrowCursor)
            self.label_video.setEnabled(1)
            self.label_video.reinit_origine()
        except AttributeError:
            pass
        try:
            self.label_echelle_trace.hide()
            del self.label_echelle_trace
        except AttributeError:
            # quand on demande un effacement tout au début. Comme par exemple, ouvrir les exmples.
            pass

        self.ui.Bouton_Echelle.setText(_translate(
            "pymecavideo", "Définir l'échelle", None))
        self.ui.Bouton_Echelle.setStyleSheet("background-color:None;")
        self.init_variables(None, filename=self.filename)
        try:
            self.affiche_image()
        except AttributeError:
            pass

        self.label_video.echelle_image = echelle()
        self.affiche_echelle()
        self.ui.horizontalSlider.setEnabled(1)
        self.ui.spinBox_image.setEnabled(1)
        self.ui.spinBox_image.setValue(1)
        self.enableDefaire(False)
        self.enableRefaire(False)
        self.affiche_nb_points(1)
        self.ui.Bouton_lance_capture.setEnabled(1)

        # désactive le bouton de calculs si existant :
        self.ui.pushButton_stopCalculs.setEnabled(0)
        self.ui.pushButton_stopCalculs.hide()

        # désactive grpahe si existant
        try:
            plotItem = self.graphWidget.getPlotItem()
            plotItem.clear()
            plotItem.setTitle('')
            plotItem.hideAxis('bottom')
            plotItem.hideAxis('left')
        except AttributeError:
            pass  # pas eu de graphes dessiné

        ### Réactiver checkBox_avancees après réinitialisation ###
        self.ui.pushButton_origine.setEnabled(1)
        self.ui.checkBox_abscisses.setEnabled(1)
        self.ui.checkBox_ordonnees.setEnabled(1)
        self.ui.checkBox_auto.setEnabled(1)
        self.ui.checkBox_abscisses.setCheckState(Qt.Unchecked)
        self.ui.checkBox_ordonnees.setCheckState(Qt.Unchecked)
        self.ui.checkBox_auto.setCheckState(Qt.Unchecked)
        if self.a_une_image:
            self.ui.pushButton_rot_droite.setEnabled(1)
            self.ui.pushButton_rot_gauche.setEnabled(1)
        else:
            self.ui.pushButton_rot_droite.setEnabled(0)
            self.ui.pushButton_rot_gauche.setEnabled(0)
        # remets le signal enlevé :
        self.ui.horizontalSlider.valueChanged.connect(
            self.affiche_image_slider_move)
        self.ui.spinBox_image.valueChanged.connect(self.affiche_image_spinbox)
        self.ui.tabWidget.setTabEnabled(3, False)
        self.ui.tabWidget.setTabEnabled(2, False)
        self.ui.tabWidget.setTabEnabled(1, False)
        self.ui.checkBox_Ec.setChecked(0)
        self.ui.checkBox_Em.setChecked(0)
        self.ui.checkBox_Epp.setChecked(0)
        if self.ui.tableWidget:
            self.ui.tableWidget.clear()

        # HACK : oblige le redimensionnement
        self.resize(self.size()+QSize(1, 0))

    ############ les signaux spéciaux #####################
    clic_sur_video = pyqtSignal()
    change_axe_origine = pyqtSignal()
    selection_done = pyqtSignal()
    selection_motif_done = pyqtSignal()
    stopRedimensionnement = pyqtSignal()
    OKRedimensionnement = pyqtSignal()
    redimensionneSignal = pyqtSignal(bool)
    stopCalculs = pyqtSignal()
    updateProgressBar = pyqtSignal()
    pythonsourceOK = pyqtSignal(list)
    #chrono_changed = pyqtSignal()

    def ui_connections(self):
        """connecte les signaux de Qt"""
        self.dbg.p(1, "rentre dans 'ui_connections'")
        self.ui.actionOuvrir_un_fichier.triggered.connect(self.openfile)
        self.ui.actionExemples.triggered.connect(self.openexample)
        self.ui.action_propos.triggered.connect(self.propos)
        self.ui.actionAide.triggered.connect(self.aide)
        self.ui.actionDefaire.triggered.connect(self.efface_point_precedent)
        self.ui.actionRefaire.triggered.connect(self.refait_point_suivant)
        self.ui.actionQuitter.triggered.connect(self.close)
        self.ui.actionSaveData.triggered.connect(self.enregistre_ui)
        self.ui.actionCopier_dans_le_presse_papier.triggered.connect(
            self.presse_papier)
        self.ui.actionRouvrirMecavideo.triggered.connect(self.rouvre_ui)
        self.ui.Bouton_Echelle.clicked.connect(self.demande_echelle)
        self.ui.horizontalSlider.sliderReleased.connect(
            self.affiche_image_slider)
        self.ui.horizontalSlider.valueChanged.connect(
            self.affiche_image_slider_move)
        self.ui.spinBox_image.valueChanged.connect(self.affiche_image_spinbox)
        self.ui.Bouton_lance_capture.clicked.connect(self.debut_capture)
        self.clic_sur_video.connect(self.clic_sur_label_video)
        self.ui.comboBox_referentiel.currentIndexChanged.connect(
            self.tracer_trajectoires)
        #self.ui.comboBox_mode_tracer.currentIndexChanged.connect(
            #self.tracer_courbe)
        self.ui.tabWidget.currentChanged.connect(self.choix_onglets)
        self.ui.checkBoxScale.currentIndexChanged.connect(self.enableSpeed)
        self.ui.checkBoxVectorSpeed.stateChanged.connect(self.enableSpeed)
        self.ui.radioButtonSpeedEveryWhere.clicked.connect(self.enableSpeed)
        self.ui.radioButtonNearMouse.clicked.connect(self.enableSpeed)
        self.ui.button_video.clicked.connect(self.video)
        self.ui.pushButton_select_all_table.clicked.connect(self.presse_papier)
        self.ui.comboBoxChrono.currentIndexChanged.connect(self.chronoPhoto)
        self.ui.pushButton_reinit.clicked.connect(self.reinitialise_capture)
        self.ui.pushButton_defait.clicked.connect(self.efface_point_precedent)
        self.ui.pushButton_refait.clicked.connect(self.refait_point_suivant)
        self.ui.pushButton_origine.clicked.connect(
            self.choisi_nouvelle_origine)
        self.ui.checkBox_abscisses.stateChanged.connect(self.change_sens_X)
        self.ui.checkBox_ordonnees.stateChanged.connect(self.change_sens_Y)
        self.ui.pushButton_rot_droite.clicked.connect(self.tourne_droite)
        self.ui.pushButton_rot_gauche.clicked.connect(self.tourne_gauche)
        self.change_axe_origine.connect(self.change_axe_ou_origine)
        self.selection_done.connect(self.picture_detect)
        self.selection_motif_done.connect(self.suiviDuMotif)
        self.stopRedimensionnement.connect(self.fixeLesDimensions)
        self.OKRedimensionnement.connect(self.defixeLesDimensions)
        self.redimensionneSignal.connect(self.redimensionneFenetre)
        self.stopCalculs.connect(self.stopComputing)
        self.ui.pushButton_stopCalculs.clicked.connect(self.stopCalculs)
        self.updateProgressBar.connect(self.updatePB)
        self.ui.exportCombo.currentIndexChanged.connect(self.export)
        self.ui.pushButton_nvl_echelle.clicked.connect(self.recommence_echelle)
        self.ui.checkBox_Ec.stateChanged.connect(self.affiche_tableau)
        self.ui.checkBox_Epp.stateChanged.connect(self.affiche_tableau)
        self.ui.checkBox_Em.stateChanged.connect(self.affiche_tableau)
        self.ui.comboBox_X.currentIndexChanged.connect(self.dessine_graphe_avant)
        self.ui.comboBox_Y.currentIndexChanged.connect(self.dessine_graphe_avant)
        self.ui.lineEdit_m.textChanged.connect(self.verifie_m_grapheur)
        self.ui.lineEdit_g.textChanged.connect(self.verifie_g_grapheur)
        self.ui.lineEdit_IPS.textChanged.connect(self.verifie_IPS)
        self.ui.comboBox_style.currentIndexChanged.connect(self.dessine_graphe)
        self.ui.pushButton_save.clicked.connect(self.enregistreChrono)
        self.ui.spinBox_chrono.valueChanged.connect(self.changeChronoImg)
        self.ui.pushButton_save_plot.clicked.connect(self.enregistre_graphe)
        
    def changeChronoImg(self,img):
        self.chronoImg = img
        self.chronoPhoto()

    def enregistreChrono(self):
        self.pixmapChrono = QPixmap(self.label_trajectoire.size())
        self.label_trajectoire.render(self.pixmapChrono)
        base_name = os.path.splitext(os.path.basename(self.filename))[0]
        defaultName = os.path.join(DOCUMENT_PATH[0], base_name)
        fichier = QFileDialog.getSaveFileName(self,
                                              _translate(
                                                  "pymecavideo", "Enregistrer comme image", None),
                                              defaultName, _translate("pymecavideo", "fichiers images(*.png *.jpg)", None))
        try :
            self.pixmapChrono.save(fichier[0])
        except :
            QMessageBox.critical(None, _translate("pymecavideo", "Erreur lors de l'enregistrement", None), _translate("pymecavideo", "Echec de l'enregistrement du fichier:<b>\n{0}</b>", None).format(
                    fichier[0]), QMessageBox.Ok, QMessageBox.Ok)

    def chronoPhoto(self):
        """lance la sauvegarde du label_trajectoire.
        Si chronophotographie, on ajoute l'image et la trace de l'échelle comme pointée.
        Si chronophotogramme, on ne met pas l'image et la trace est en haut.
        """
        # Configure l'UI en fonction du mode
        if self.ui.comboBoxChrono.currentIndex() == 0 :
            self.ui.widget_chronophoto.setEnabled(False)
            self.ui.topWidget2.setEnabled(True)
            self.ui.widget_speed.setEnabled(True)
        elif self.ui.comboBoxChrono.currentIndex() == 1 :
            self.ui.widget_chronophoto.setEnabled(True)
            self.ui.topWidget2.setEnabled(False)
            self.ui.widget_speed.setEnabled(False)
            self.ui.checkBoxVectorSpeed.setChecked(False)
        elif self.ui.comboBoxChrono.currentIndex() == 2 :
            self.ui.widget_chronophoto.setEnabled(False)
            self.ui.topWidget2.setEnabled(False)
            self.ui.widget_speed.setEnabled(False)
            self.ui.checkBoxVectorSpeed.setChecked(False)
        self.dbg.p(1, "rentre dans 'chronoPhoto'")
        # ajoute la première image utilisée pour le pointage sur le fond du label
        liste_types_photos = ['chronophotographie', 'chronophotogramme']

        if self.ui.comboBoxChrono.currentIndex() != 0:
            photo_chrono = liste_types_photos[self.ui.comboBoxChrono.currentIndex(
            )-1]
            self.dbg.p(2, "dans 'chronoPhoto, on a choisi le type %s'" %
                       (photo_chrono))
            if photo_chrono == 'chronophotographie':  # on extrait le première image que l'on rajoute au label
                self.label_trajectoire.chrono = 1  # 1 pour chronophotographie
                ok, img = self.cvReader.getImage(
                    self.chronoImg, self.rotation)
                self.imageChrono = toQImage(img).scaled(
                    self.label_video.width(), self.label_video.height(), Qt.KeepAspectRatio)
                self.label_trajectoire.setPixmap(
                    QPixmap.fromImage(self.imageChrono))
            else:
                self.label_trajectoire.chrono = 2  # 2 pour chronophotogramme
                self.label_trajectoire.setPixmap(QPixmap())
            #self.enregistreChrono()
        else:
            self.label_trajectoire.setPixmap(QPixmap())
            self.label_trajectoire.chrono = 0
        self.redimensionneFenetre()
        self.update()

    def fixeLesDimensions(self):
        self.setMinimumWidth(self.width())
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.setFixedSize(QSize(self.width(), self.height()))

    def defixeLesDimensions(self):
        self.setMinimumWidth(1000)
        self.setMaximumWidth(16000000)
        self.setMinimumHeight(800)
        self.setMaximumHeight(16000000)
        pass

    def updatePB(self):
        self.qmsgboxencode.updateProgressBar()

    def enableSpeed(self, secondParam=None):
        """
        Quand on veut afficher le vecteur vitesse,
        on active le spinbox qui permet de choisir une échelle.
        Quand on ne veut plus, on peut cacher le spinbox.
        @param secondParam peu utile mais nécessaire : certains modes
        de rappel de cette fonction ont un paramètre supplémentaire
        """
        self.dbg.p(1, "rentre dans 'enableSpeed'")
        if self.ui.checkBoxVectorSpeed.isChecked():
            self.dbg.p(2, "In enableSpeed")
            self.ui.checkBoxScale.setEnabled(1)
            if self.ui.checkBoxScale.count() < 1:
                self.ui.checkBoxScale.insertItem(0, "1")
            self.ui.radioButtonNearMouse.show()
            self.ui.radioButtonSpeedEveryWhere.show()
            self.label_trajectoire.reDraw()
        else:
            self.ui.checkBoxScale.setEnabled(0)
            self.ui.radioButtonNearMouse.hide()
            self.ui.radioButtonSpeedEveryWhere.hide()
            self.label_trajectoire.reDraw()

    def suiviDuMotif(self):
        self.dbg.p(1, "rentre dans 'suiviDuMotif'")
        if len(self.motif) == self.nb_de_points:
            self.dbg.p(3, "selection des motifs finie")
            self.label_auto.hide()
            self.label_auto.close()
            del self.label_auto
            self.indexMotif = 0
            self.ui.pushButton_stopCalculs.setText("STOP")
            self.ui.pushButton_stopCalculs.setEnabled(1)
            self.ui.pushButton_stopCalculs.show()
            self.label_video.setEnabled(0)
            self.pileDeDetections = []
            for i in range(self.index_de_l_image, int(self.image_max)+1):
                for j in range(self.nb_de_points):
                    self.pileDeDetections.append(i)
            # programme le suivi du point suivant après un délai de 50 ms,
            # pour laisser une chance aux évènement de l'interface graphique
            # d'être traités en priorité
            self.dbg.p(3, "self.pileDeDetections : %s" % self.pileDeDetections)
            timer = QTimer.singleShot(50, self.detecteUnPoint)

    # @time_it
    def detecteUnPoint(self):
        """
        méthode (re)lancée pour les détections automatiques de points
        traite une à une les données empilées dans self.pileDeDetections
        et relance un signal si la pile n'est pas vide après chacun
        des traitements.
        """
        self.dbg.p(1, "rentre dans 'detecteUnPoint'")
        if self.pileDeDetections:
            if len(self.pileDeDetections) % self.nb_de_points != 0:
                self.indexMotif += 1
            else:
                self.indexMotif = 0
            index_de_l_image = self.pileDeDetections.pop(0)
            texteDuBouton = "STOP (%d)" % index_de_l_image
            self.ui.pushButton_stopCalculs.setText(texteDuBouton)
            # TODO : principal point noir du calcul.
            self.dbg.p(2, "On lance la detection avec : self.motif %s, self.indexMotif %s" % (
                self.motif, self.indexMotif))
            point = filter_picture(
                self.motif, self.indexMotif, self.imageAffichee, self.pointsProbables)
            self.pointsProbables[0] = point
            self.label_video.storePoint(vecteur(point[0], point[1]))

            # programme le suivi du point suivant après un délai de 5 ms,
            # pour laisser une chance aux évènement de l'interface graphique
            # d'être traités en priorité
            timer = QTimer.singleShot(5, self.detecteUnPoint)
        else:
            self.stopCalculs.emit()

    def storeMotif(self):
        self.dbg.p(1, "rentre dans 'storeMotif'")
        if len(self.motif) == self.nb_de_points:
            self.dbg.p(3, "selection des motifs finie")
            self.label_auto.hide()
            self.label_auto.close()
            self.indexMotif = 0
            self.ui.pushButton_stopCalculs.setText("STOP")
            self.ui.pushButton_stopCalculs.setEnabled(1)
            self.ui.pushButton_stopCalculs.show()
            self.label_video.setEnabled(0)
            self.goCalcul = True
            # TODO : tests avec les différents mode de threading
            if self.methode_thread == 1:
                self.monThread = MonThreadDeCalcul(
                    self, self.motif[self.indexMotif], self.imageAffichee)
                self.monThread.start()
            elif self.methode_thread == 2:  # 1 thread par image
                for i in range((self.image_max-self.premiere_image)*self.nb_de_points):
                    self.liste_thread = [MonThreadDeCalcul2(
                        self, self.image, self.motif[self.indexMotif], self.imageAffichee)]
            elif self.methode_thread == 3:  # pour l'instant celle qui foncitonne le mieux
                timer = QTimer.singleShot(5, self.detecteUnPoint)

    def picture_detect(self):
        """
        Est lancée lors de la détection automatique des points. Gère l'ajout des thread de calcul.
        self.motifs : tableau des motifs
        """
        self.dbg.p(1, "rentre dans 'picture_detect'")
        self.dbg.p(3, "début 'picture_detect'" + str(self.indexMotif))
        if self.index_de_l_image <= self.image_max:
            self.pointsFound = []
            if self.indexMotif <= len(self.motif) - 1:
                self.dbg.p(1, "'picture_detect' : While")
                self.pointTrouve = filter_picture(
                    self.motif, self.indexMotif, self.imageAffichee, self.listePoints)
                self.dbg.p(3, "Point Trouve dans mon Thread : " +
                           str(self.pointTrouve))
                self.onePointFind()
                self.indexMotif += 1
            else:
                self.indexMotif = 0
        if self.index_de_l_image == self.image_max:
            if self.indexMotif == 0 and not self.goCalcul:  # dernier passage
                self.stopCalculs.emit()
            elif self.indexMotif == 0 and self.goCalcul:  # premier passage, premier calcul de la dernière image
                self.goCalcul = False

    def stopComputing(self):
        self.dbg.p(1, "rentre dans 'stopComputing'")
        self.pileDeDetections = []  # vide la liste des points à détecter encore
        try:
            if self.monThread:
                self.monThread.stopped = True
        except AttributeError:
            pass
        self.label_video.setEnabled(1)
        self.ui.pushButton_stopCalculs.setEnabled(0)
        self.ui.pushButton_stopCalculs.hide()

    def onePointFind(self):
        """est appelée quand un point a été trouvé lors de la détection automatique
        self.pointFound : liste des points trouvés
        """
        self.dbg.p(1, "rentre dans 'onePointFind'")
        self.pointsFound.append(self.pointTrouve)  # stock all points found
        for point in self.pointsFound:
            self.label_video.storePoint(vecteur(point[0], point[1]))

    def readStdout(self):
        self.dbg.p(1, "rentre dans 'readStdout'")
        try:
            if not self.time.isActive():
                self.timer = QTimer(self)
                self.timer.timeout.connect(self, SLOT(self.readStdout()))
                self.timer.start(100)
            else:
                while not self.exitDecode:
                    stdout_file = open(self.stdout_file, 'w+')
                    stdout = stdout_filepointsProbables.readlines()  # a gloabliser poru windows
                    if not self.exitDecode:
                        try:
                            pct = stdout[-1].split()[3].replace('%',
                                                                '').replace(')', '').replace('(', '')
                            assert (pct.isalnum())
                            exit = True
                        except IndexError:

                            exit = False
        except:
            pass

    def refait_echelle(self):
        # """Permet de retracer une échelle et de recalculer les points"""
        self.dbg.p(1, "rentre dans 'refait_echelle'")
        self.recalculLesCoordonnees()

    def choisi_nouvelle_origine(self):
        self.dbg.p(1, "rentre dans 'choisi_nouvelle_origine'")
        nvl_origine = QMessageBox.information(
            self,
            u"NOUVELLE ORIGINE",
            u"Choisissez, en cliquant sur la vidéo le point qui sera la nouvelle origine")
        label = Label_Origine(parent=self.label_video, app=self)
        label.show()

    def tourne_droite(self):
        self.dbg.p(1, "rentre dans 'tourne_droite'")
        self.tourne_image("droite")

    def tourne_gauche(self):
        self.dbg.p(1, "rentre dans 'tourne_droite'")
        self.tourne_image("gauche")

    def tourne_image(self, sens=None):
        self.dbg.p(1, "rentre dans 'tourne_image'")
        if sens == "droite":
            self.increment = 90
        elif sens == "gauche":
            self.increment = -90
        else:
            self.increment = 0
        self.rotation += self.increment
        if self.rotation > 180:
            self.rotation = self.rotation-360  # arrive pour 270° par exemple
        elif self.rotation <= -180:
            self.rotation = self.rotation+360
        self.dbg.p(2, "Dans 'tourne_image' self rotation vaut" +
                   str(self.rotation))

        # gestion de l'origine et de l'échelle :
        # DEBUG
        self.dbg.p(3, "Dans 'tourne_image' avant de tourner, self.origine %s, largeur label_video%s, hauteur label_video%s" % (
            self.label_video.origine, self.label_video.width(), self.label_video.height()))
        try:
            self.dbg.p(3, "Dans 'tourne_image' avant de tourner, self.echelle_image.p1 %s, self.echelle_image.p2 %s" % (
                self.label_video.echelle_image.p1, self.label_video.echelle_image.p2))
        except AttributeError:
            pass
        self.redimensionneSignal.emit(1)

    def change_axe_ou_origine(self, origine=None):
        """mets à jour le tableau de données"""
        self.dbg.p(1, "rentre dans 'change_axe_ou_origine'")
        # repaint axes and define origine
        if origine:
            self.label_video.origine = origine
        self.label_trajectoire.origine_mvt = self.label_video.origine
        self.label_trajectoire.update()
        self.label_video.update()

        # construit un dico plus simple à manier, dont la clef est point_ID et qui contient les coordoonées
        if self.points_ecran != {}:
            liste_clef = []
            donnees = {}
            for key in self.points_ecran:
                donnees[self.points_ecran[key][2]] = self.points_ecran[key][3]
                liste_clef.append(self.points_ecran[key][2])
            liste_clef.sort()
            for key in liste_clef:
                serie, position = self.couleur_et_numero(int(key))
                self.rempli_tableau(
                    serie, position, donnees[key], recalcul=True)
        try:
            del self.repere_camera
        except AttributeError:
            pass

    def change_sens_X(self):
        self.dbg.p(1, "rentre dans 'change_sens_X'")
        if self.ui.checkBox_abscisses.isChecked():
            self.sens_X = -1
        else:
            self.sens_X = 1
        self.change_axe_origine.emit()

    def change_sens_Y(self):
        self.dbg.p(1, "rentre dans 'change_sens_Y'")
        if self.ui.checkBox_ordonnees.isChecked():
            self.sens_Y = -1
        else:
            self.sens_Y = 1
        self.change_axe_origine.emit()

    def check_uncheck_direction_axes(self):
        if self.sens_X == -1:
            self.ui.checkBox_abscisses.setChecked(1)
        else:
            self.ui.checkBox_abscisses.setChecked(0)
        if self.sens_Y == -1:
            self.ui.checkBox_ordonnees.setChecked(1)
        else:
            self.ui.checkBox_ordonnees.setChecked(0)

    def pointEnMetre(self, p):
        """
        renvoie un point, dont les coordonnées sont en mètre, dans un
        référentiel "à l\'endroit"
        @param point un point en "coordonnées d\'écran"
        """
        self.dbg.p(1, "rentre dans 'pointEnMetre'")
        return vecteur(self.sens_X * (float(p.x() - self.label_video.origine.x()) * self.label_video.echelle_image.mParPx()), self.sens_Y * float(self.label_video.origine.y() - p.y()) * self.label_video.echelle_image.mParPx())

    def presse_papier(self):
        """Sélectionne la totalité du tableau de coordonnées
        et l'exporte dans le presse-papier (l'exportation est implicitement
        héritée de la classe utilisée pour faire le tableau). Les
        séparateurs décimaux sont automatiquement remplacés par des virgules
        si la locale est française.
        """
        self.dbg.p(1, "rentre dans 'presse_papier'")
        self.affiche_tableau()
        trange = QTableWidgetSelectionRange(0, 0,
                                            self.ui.tableWidget.rowCount() - 1,
                                            self.ui.tableWidget.columnCount() - 1)
        self.ui.tableWidget.setRangeSelected(trange, True)
        self.ui.tableWidget.selection()

    def export(self, choix_export=None):
        self.dbg.p(1, "rentre dans 'export'")
        """
        Traite le signal venu de exportCombo, puis remet l\'index de ce 
        combo à zéro.
        """
        # Si appel depuis les QActions, choix_export contient la clé du dico
        if not choix_export:
            # Si appel depuis le comboBox, on cherche l'index
            choix_export = self.ui.exportCombo.currentIndex()
        if choix_export > 0:
            # Les choix d'export du comboBox commencent à l'index 1. Le dico EXPORT_FORMATS commence à 1 et pas à zéro
            self.ui.exportCombo.setCurrentIndex(0)
            self.affiche_tableau()
            Export(self, choix_export)

    def _dir(lequel=None, install=None):
        """renvoie les répertoires utiles.
        paramètre lequel (chaîne) : peut prendre les valeurs utiles suivantes,
        "videos", "home", "conf", "images", "icones", "langues", "data", "help"
        quand le paramètre est absent, initialise les répertoires si nécessaire
        """
        if lequel == "home":
            return HOME_PATH
        elif lequel == "videos":
            return VIDEO_PATH
        elif lequel == "conf":
            return CONF_PATH
        elif lequel == "icones":
            return ICON_PATH
        elif lequel == "langues":
            return LANG_PATH
        elif lequel == "data":
            return DATA_PATH
        elif lequel == "help":
            return HELP_PATH
        elif type(lequel) == type(""):
            self.dbg.p(
                1, "erreur, appel de _dir() avec le paramètre inconnu %s" % lequel)
            self.close()
        else:
            # vérifie/crée les repertoires
            dd = StartQt5._dir("conf")
            if not os.path.exists(dd):
                os.makedirs(dd)
    _dir = staticmethod(_dir)

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

    def rouvre_ui(self):
        self.dbg.p(1, "rentre dans 'rouvre_ui'")
        
        dir_ = DOCUMENT_PATH[0]
        fichier, _ = QFileDialog.getOpenFileName(self, _translate("pymecavideo", "Ouvrir un projet Pymecavideo", None),
                                                 dir_,
                                                 _translate("pymecavideo", "Projet Pymecavideo (*.mecavideo)", None))
        if fichier != "":
            self.rouvre(fichier)

    def mets_en_orange_echelle(self):
        self.ui.Bouton_Echelle.setEnabled(1)
        self.ui.Bouton_Echelle.setText("refaire l'échelle")
        self.ui.Bouton_Echelle.setStyleSheet("background-color:orange;")

    def loads(self, s):
        """lis la chaine de caractère issue du fichier mecavideo et en extrait les données utiles"""
        self.dbg.p(1, "rentre dans 'loads'")
        s = s[1:-2].replace("\n#", "\n")
        echelle, point, self.deltaT, self.nb_de_points = s.splitlines()[
            1:-1][-4:]
        self.label_video.echelle_image.longueur_reelle_etalon = float(echelle.split()[
                                                                      1])
        x, y = float(point.split()[3][1:-1]), float(point.split()[4][:-1])
        self.label_video.echelle_image.p1 = vecteur(x, y)
        x, y = float(point.split()[5][1:-1]), float(point.split()[6][:-1])
        self.label_video.echelle_image.p2 = vecteur(x, y)
        donnees_fichier = s.splitlines()[1:-1]
        dico_donnee = {}
        for donnee in donnees_fichier:
            if len(donnee.split('=')) == 2:
                cle, valeur = donnee.split('=')
                dico_donnee[cle.strip()] = valeur.strip()
        self.filename = dico_donnee["video"]
        self.dbg.p(3, "rentre dans 'loads fichier : ' %s" % (self.filename))
        try:
            self.sens_X = int(dico_donnee['sens axe des X'])
        except KeyError:
            self.sens_X = 1
        self.dbg.p(3, "rentre dans 'loads' : sens_x' %s" % (self.sens_X))
        try:
            self.sens_Y = int(dico_donnee['sens axe des Y'])
        except KeyError:
            self.sens_Y = 1
        self.dbg.p(3, "rentre dans 'loads' sens_y %s" % (self.sens_Y))
        try:
            largeur = int(dico_donnee['largeur video'])
        except KeyError:
            largeur = 640
        self.dbg.p(3, "rentre dans 'loads' largeur :  %s" % (largeur))
        try:
            hauteur = int(dico_donnee['hauteur video'])
        except KeyError:
            largeur = 480
        self.dbg.p(3, "rentre dans 'loads' hauteur %s" % (hauteur))
        try:
            self.rotation = int(dico_donnee['rotation'])
        except KeyError:
            self.rotation = 0
        self.dbg.p(3, "rentre dans 'loads' rotation %s" % (self.rotation))
        try:
            self.label_video.origine = vecteur(dico_donnee['origine de pointage'].split(
            )[-2][1:-1], dico_donnee['origine de pointage'].split()[-1][:-1])
        except KeyError:
            self.label_video.origine = vecteur(largeur//2, hauteur//2)
        self.dbg.p(3, "rentre dans 'loads' origine %s" %
                   (self.label_video.origine))
        self.premiere_image = int(dico_donnee['index de depart'])
        self.dbg.p(3, "rentre dans 'loads' première image %s" %
                   (self.premiere_image))
        self.dbg.p(3, "rentre dans 'loads' longueur_reelle_etalon %s" %
                   (self.label_video.echelle_image.longueur_reelle_etalon))
        self.label_video.echelle_image.p1, self.label_video.echelle_image.p2 = vecteur(point.split(
        )[-4][1:-1], point.split()[-3][:-1]), vecteur(point.split()[-2][1:-1], point.split()[-1][:-1])
        self.dbg.p(3, "rentre dans 'loads' points de l'échelle %s" % (
            [self.label_video.echelle_image.p1, self.label_video.echelle_image.p2]))
        self.deltaT = float(self.deltaT.split()[-1])
        self.dbg.p(3, "rentre dans 'loads' delta_t %s" % (self.deltaT))
        self.nb_de_points = int(self.nb_de_points.split()[-2])
        self.dbg.p(3, "rentre dans 'loads' nb de points %s" %
                   (self.nb_de_points))
        self.dbg.p(3, "rentre dans 'loads, dico données' %s" % (dico_donnee))
        self.calcul_deltaT(rouvre=True)
        self.label_video.resize(QSize(largeur, hauteur))
        ########redimensionne l'application TODO : ATTENTION 
        geom = self.label_video.geometry()
        #print(geom.x(),geom.y(),geom.width(),geom.height())
        #print(self.ui.containerWidget1.geometry())
        self.ui.containerWidget1.setGeometry(0,0, geom.width(),geom.height())
        decalage_gauche = 220
        decalage_haut = 130
        self.setGeometry(0,0, self.label_video.width()+decalage_gauche, self.label_video.height()+decalage_haut)
        
        self.aspectlayout1.aspect = largeur/hauteur
        self.aspectlayout2.aspect = largeur/hauteur
        self.init_cvReader()
        return dico_donnee

    def rouvre(self, fichier):
        """Open a mecavideo file"""
        self.dbg.p(1, "rentre dans 'rouvre'")
        self.reinitialise_capture()
        lignes = open(fichier, "r").readlines()
        i = 0
        self.points = {}  # dictionnaire des données, simple. Les clefs sont les index de l'image. les données les
        self.listePoints = listePointee()
        dictionnaire_données_str = ""
        for l in lignes:
            if l[0] == "#":
                dictionnaire_données_str += l
        self.label_video.echelle_image = echelle()  # on réinitialise l'échelle
        try:
            # on récupère les données importantes
            dico_donnees = self.loads(dictionnaire_données_str)
            self.check_uncheck_direction_axes()  # check or uncheck axes Checkboxes
            self.init_interface()
            self.change_axe_ou_origine()

            # puis on trace le segment entre les points cliqués pour l'échelle
            # on réinitialise l'échelle.p1, self.echelle_image.p2)
            self.feedbackEchelle(
                self.label_video.echelle_image.p1, self.label_video.echelle_image.p2)
            framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos(
                self.rotation)
            self.rouvert = True
            self.premierResize = False
            # on régénère self.listePoints et self.points
            for l in lignes:
                if l[0] == "#":
                    pass
                else:
                    l = l.strip('\t\n')
                    d = l.split("\t")
                    t = "%4f" % (float(d[0].replace(",", ".")))
                    self.points[i] = [t]
                    for j in range(1, len(d), 2):
                        pos = vecteur(float(d[j].replace(",", ".")) * self.label_video.echelle_image.pxParM()
                                      + self.label_video.origine.x(), self.label_video.origine.y() - float(
                            d[j + 1].replace(",", ".")) * self.label_video.echelle_image.pxParM())
                        self.enregistre_dans_listePoints(
                            pos, index=int(float(t)*framerate) +
                            self.premiere_image
                        )
                        self.points[i].append(pos)
                    i += 1
            self.defini_barre_avancement()
            self.affiche_echelle()  # on met à jour le widget d'échelle
            derniere_image = self.listePoints[len(self.listePoints)-1][0]+1
            self.ui.horizontalSlider.setValue(derniere_image)
            self.ui.spinBox_image.setValue(derniere_image)
            self.ui.spinBox_chrono.setMaximum(derniere_image)
            self.affiche_nb_points(self.nb_de_points)
            self.enableDefaire(True)
            self.enableRefaire(False)
            self.affiche_image()  # on affiche l'image
            self.mets_en_orange_echelle()
            self.ui.tableWidget.show()
            self.recalculLesCoordonnees()
            self.debut_capture(rouvre=True)
        except:
            reponse = QMessageBox.warning(None, "Mauvais type de fichier",
                                          _translate("pymecavideo", """\
Le fichier choisi n'est pas compatible avec pymecavideo""",
                                                     None),
                                          QMessageBox.Ok, QMessageBox.Ok)
            self.a_une_image = False

    def determineRatio(self):
        self.dbg.p(1, "rentre dans 'determineRatio'")
        if self.premierResize:
            if self.cvReader is None:
                self.image_max, self.largeurFilm, self.hauteurFilm = 10, 320, 200
            else:
                framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos()
        framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos()
        ratioFilm = float(self.largeurFilm) / self.hauteurFilm
        self.dbg.p(3, "dans 'determineRatio', le ratio a été calculé à %s"%(ratioFilm))
        return ratioFilm

    def redimensionneFenetre(self, tourne=False, old=None):
        self.tourne = tourne  # n'est utilisée que ici et dans label_video
        if tourne:  # on vient de cliquer sur tourner. rien n'est changé.
            largeur = self.label_video.width()
            hauteur = self.label_video.height()
            self.label_video.origine = self.label_video.origine.rotate(
                self.increment, largeur, hauteur)
            self.label_video.echelle_image.p1 = self.label_video.echelle_image.p1.rotate(
                self.increment, largeur, hauteur)
            self.label_video.echelle_image.p2 = self.label_video.echelle_image.p2.rotate(
                self.increment, largeur, hauteur)
            self.label_video.setGeometry(0, 0, hauteur, largeur)
            self.ratio = 1/self.ratio
            self.aspectlayout1.aspect = self.ratio
            self.aspectlayout2.aspect = self.ratio
            self.tourne = False
            # HACK : oblige le redimensionnement
            self.resize(self.size()+QSize(1, 0))

        if self.lance_capture:
            self.dbg.p(2, "on fixe les hauteurs du label")
            self.ui.containerWidget1.setFixedHeight(
                self.ui.containerWidget1.height())
            self.ui.containerWidget1.setFixedWidth(
                self.ui.containerWidget1.width())
            self.dbg.p(2, "on fixe les hauteurs de la fenetre")

        if hasattr(self, 'label_video'):
            self.dbg.p(2, "on fixe les hauteurs de label_video")
            self.dbg.p(2, "label_vidéo situé en %s %s" %
                       (self.label_video.pos().x(), self.label_video.pos().y()))
            self.dbg.p(3, "label_vidéo largeur :  %s hauteur : %s" %
                       (self.label_video.width(), self.label_video.height()))
            self.dbg.p(2, "MAJ de label_video")
            self.label_video.maj()
            self.label_trajectoire.maj()
            self.affiche_image()

        self.dbg.p(2, "On fixe les tailles de centralwidget et tabWidget")

    def widthForHeight_label_video(self, h):
        # calcule self.largeur et self.hauteur si la hauteur est prédominante
        # si la hauteur est trop petite, ne permet plus de redimensionnement
        self.dbg.p(1, "retre dans 'widthForHeight'")
        self.dbg.p(2, "argument h : %s" % (str(h)))
        return int(h*self.ratio)

    def heightForWidth_label_video(self, w):
        # calcul self.largeur et self.hauteur
        # si la largeur est trop petite, ne permet plus de redimensionnement
        self.dbg.p(1, "retre dans 'heightForWidth'")
        self.dbg.p(2, "argument w : %s" % (str(w)))
        return int(w/self.ratio)

    def enterEvent(self, e):
        self.gardeLargeur()

    def leaveEvent(self, e):
        self.gardeLargeur()

    def gardeLargeur(self):
        self.largeurAvant = self.largeur

    def resizeEvent(self, event):
        self.dbg.p(1, "rentre dans 'resizeEvent'")
        self.redimensionneFenetre(tourne=False, old=event.oldSize())
        return super(StartQt5, self).resizeEvent(event)

    def showEvent(self, event):
        self.dbg.p(1, "rentre dans 'showEvent'")
        self.redimensionneSignal.emit(0)

    def entete_fichier(self, msg=""):
        self.dbg.p(1, "rentre dans 'entete_fichier'")
        result = u"""#pymecavideo
#video = %s
#sens axe des X = %d
#sens axe des Y = %d
#largeur video = %d
#hauteur video = %d
#rotation = %d
#origine de pointage = %s
#index de depart = %d
#echelle %5f m pour %5f pixel
#echelle pointee en %s %s
#intervalle de temps : %f
#suivi de %s point(s)
#%s
#""" % (self.filename, self.sens_X, self.sens_Y, self.label_video.width(), self.label_video.height(), self.rotation, self.label_video.origine, self.premiere_image, self.label_video.echelle_image.longueur_reelle_etalon, self.label_video.echelle_image.longueur_pixel_etalon(),
            self.label_video.echelle_image.p1, self.label_video.echelle_image.p2, self.deltaT, self.nb_de_points, msg)
        return result

    def enregistre(self, fichier):
        self.dbg.p(1, "rentre dans 'enregistre'")
        sep_decimal = "."
        try:
            if locale.getdefaultlocale()[0][0:2] == 'fr':
                # en France, le séparateur décimal est la virgule
                sep_decimal = ","
        except TypeError:
            pass
        if fichier != "":
            liste_des_cles = []
            for key in self.points:
                liste_des_cles.append(key)
            ################## fin du fichier mecavideo ################
            file = open(fichier, 'w')
            try:
                file.write(self.entete_fichier(_translate(
                    "pymecavideo", "temps en seconde, positions en mètre", None)))
                for cle in liste_des_cles:
                    donnee = self.points[cle]
                    t = float(donnee[0])
                    a = ("\n%.2f\t" % t).replace(".", sep_decimal)
                    for p in donnee[1:]:
                        pm = self.pointEnMetre(p)
                        a += ("%5f\t" % (pm.x())).replace(".", sep_decimal)
                        a += ("%5f\t" % (pm.y())).replace(".", sep_decimal)
                    file.write(a)
            finally:
                file.close()
            ################# fin du fichier physique ################
            self.modifie = False

    def enregistre_ui(self):
        self.dbg.p(1, "rentre dans 'enregistre_ui'")
        if self.points != {}:
            base_name = os.path.splitext(os.path.basename(self.filename))[0]
            defaultName = os.path.join(DOCUMENT_PATH[0], base_name+'.mecavideo')
            fichier = QFileDialog.getSaveFileName(self,
                                              _translate(
                                                  "pymecavideo", "Enregistrer le projet pymecavideo", None),
                                              defaultName, _translate("pymecavideo", "Projet pymecavideo (*.mecavideo)", None))
            try :
                self.enregistre(fichier[0])
            except :
                QMessageBox.critical(None, _translate("pymecavideo", "Erreur lors de l'enregistrement", None), _translate("pymecavideo", "Echec de l'enregistrement du fichier:<b>\n{0}</b>", None).format(
                        fichier[0]), QMessageBox.Ok, QMessageBox.Ok)
 
    def debut_capture(self, departManuel=True, rouvre=False):
        """
        permet de mettre en place le nombre de point à acquérir
        @param departManuel vrai si on a fixé à la main la première image.
        @param rouvre  : ne mets pas à jour self.prmeière_image à partir du slider.

        """
        self.dbg.p(1, "rentre dans 'debut_capture'")
        self.label_video.setFocus()
        self.label_video.show()
        self.label_video.activateWindow()
        self.label_video.setVisible(True)
        try:
            # nécessaire sinon, label_video n'est pas actif.
            self.label_echelle_trace.lower()
        except AttributeError:
            pass
        self.nb_de_points = self.ui.spinBox_nb_de_points.value()
        self.affiche_nb_points(False)
        self.affiche_lance_capture(False)
        self.ui.horizontalSlider.setEnabled(0)
        self.ui.spinBox_image.setEnabled(0)
        self.ui.tabWidget.setEnabled(1)
        self.ui.tabWidget.setTabEnabled(3, True)
        self.ui.tabWidget.setTabEnabled(2, True)
        self.ui.tabWidget.setTabEnabled(1, True)
        self.arretAuto = False
        if not rouvre : #si rouvre, self.premiere_imageest déjà définie
            self.premiere_image = self.ui.horizontalSlider.value()
        self.affiche_point_attendu(0)
        self.lance_capture = True
        self.fixeLesDimensions()
        self.label_video.setCursor(Qt.CrossCursor)
        self.ui.tab_traj.setEnabled(1)
        self.ui.actionSaveData.setEnabled(1)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(1)
        self.ui.comboBox_referentiel.setEnabled(1)
        self.ui.pushButton_select_all_table.setEnabled(1)

        self.ui.comboBox_referentiel.clear()
        self.ui.comboBox_referentiel.insertItem(-1, "camera")
        for i in range(self.nb_de_points):
            self.ui.comboBox_referentiel.insertItem(-1, _translate(
                "pymecavideo", "point N° {0}", None).format(i+1))

        self.ui.pushButton_origine.setEnabled(0)
        self.ui.checkBox_abscisses.setEnabled(0)
        self.ui.checkBox_ordonnees.setEnabled(0)
        self.ui.checkBox_auto.setEnabled(0)
        # self.ui.Bouton_Echelle.setEnabled(0)
        self.ui.Bouton_lance_capture.setEnabled(0)
        self.ui.pushButton_rot_droite.setEnabled(0)
        self.ui.pushButton_rot_gauche.setEnabled(0)

        # on empêche le redimensionnement
        self.fixeLesDimensions()

        # si aucune échelle n'a été définie, on place l'étalon à 1 px pou 1 m.
        if self.label_video.echelle_image.mParPx() == 1:
            self.label_video.echelle_image.longueur_reelle_etalon = 1
            self.label_video.echelle_image.p1 = vecteur(0, 0)
            self.label_video.echelle_image.p1 = vecteur(0, 1)

        # automatic capture
        if self.ui.checkBox_auto.isChecked():
            #self.auto = True
            self.mets_a_jour_label_infos(
                _translate("pymecavideo", "Pointage Automatique", None))
            reponse = QMessageBox.warning(None, "Capture Automatique",
                                          _translate("pymecavideo", """\
Veuillez sélectionner un cadre autour du ou des objets que vous voulez suivre.
Vous pouvez arrêter à tout moment la capture en appuyant sur le bouton STOP""",
                                                     None),
                                          QMessageBox.Ok, QMessageBox.Ok)
            try:
                self.label_auto.hide()
                del self.label_auto
            except:
                pass
            # in this label, motif(s) are defined.
            self.label_auto = Label_Auto(self.label_video, self)
            self.label_auto.show()
            # IMPORTANT : permet de gagner en fluidité de l'affichage lors du pointage autmatique. BUG lié au rafraichissment du slider.
            self.ui.horizontalSlider.valueChanged.disconnect()
            self.ui.spinBox_image.valueChanged.disconnect()

    def cree_tableau(self):
        """
        Crée un tableau de coordonnées neuf dans l'onglet idoine.
        """
        self.dbg.p(1, "rentre dans 'cree_tableau'")
        self.ui.tableWidget.clear()
        self.ui.tab_coord.setEnabled(1)
        self.ui.tableWidget.setRowCount(1)
        colonnes_sup = self.ui.checkBox_Ec.isChecked()+self.ui.checkBox_Epp.isChecked() + \
            self.ui.checkBox_Em.isChecked()
        
        self.ui.tableWidget.setColumnCount(
            self.nb_de_points * 2 + 2 + colonnes_sup*self.nb_de_points) #ajout d'une colonne bouton
        
        self.ui.tableWidget.setDragEnabled(True)
        # on met des titres aux colonnes.
        self.ui.tableWidget.setHorizontalHeaderItem(
            0, QTableWidgetItem('t (s)'))
        self.ui.tableWidget.setRowCount(len(self.points))
        for i in range(self.nb_de_points):
            if self.echelle_faite:
                x = "X%d (m)" % (1 + i)
                y = "Y%d (m)" % (1 + i)
            else:
                x = "X%d (px)" % (1 + i)
                y = "Y%d (px)" % (1 + i)

            self.ui.tableWidget.setHorizontalHeaderItem(
                1 + (2+colonnes_sup) * i, QTableWidgetItem(x))
            self.ui.tableWidget.setHorizontalHeaderItem(
                2 + (2+colonnes_sup) * i, QTableWidgetItem(y))
            for j in range(colonnes_sup):
                cptr = 0
                if self.ui.checkBox_Ec.isChecked():
                    self.ui.tableWidget.setHorizontalHeaderItem(
                        3+cptr + (2+colonnes_sup)*i, QTableWidgetItem("Ec%d (J)" % (1 + i)))
                    cptr += 1
                if self.ui.checkBox_Epp.isChecked():
                    self.ui.tableWidget.setHorizontalHeaderItem(
                        3+cptr + (2+colonnes_sup)*i, QTableWidgetItem("Epp%d (J)" % (1 + i)))
                    cptr += 1
                if self.ui.checkBox_Em.isChecked():
                    self.ui.tableWidget.setHorizontalHeaderItem(
                        3+cptr + (2+colonnes_sup)*i, QTableWidgetItem("Em%d (J)" % (1 + i)))
                    cptr += 1
        #dernier pour le bouton
        self.ui.tableWidget.setHorizontalHeaderItem(
                        self.nb_de_points * 2 + 1 + colonnes_sup*self.nb_de_points, QTableWidgetItem("Refaire le point"))
        
    def barycentre_trajectoires(self, referentiel):
        """
        calcule le barycentre de tous les points constituant les trajectoires
        rapportées à un référentiel.
        """
        self.dbg.p(1, "rentre dans 'barycentre_trajectoires'")
        bc = vecteur(0, 0)
        compte = 0
        for n in range(self.nb_de_points):
            if n == referentiel:
                pass
            for i in self.points.keys():
                bc += self.points[i][1 + n] - self.points[i][1 + referentiel]
                compte += 1
        bc *= 1.0 / compte
        return bc

    def mediane_trajectoires(self, referentiel):
        """
        calcule le barycentre de tous les points constituant les trajectoires
        rapportées à un référentiel.
        """
        self.dbg.p(1, "rentre dans 'mediane_trajectoires'")
        min_ = None
        max_ = None
        for n in range(self.nb_de_points):
            if n == referentiel:
                pass
            for i in self.points.keys():
                try:
                    p = self.points[i][1 + n] - self.points[i][1 + referentiel]
                    min_ = p.minXY(min_)
                    max_ = p.maxXY(max_)
                except:
                    pass  # si on s'arrête de cliquer avant d'avoir fini l'image
        if min_ != None and max_ != None:
            return (min_ + max_) * 0.5
        else:
            return vecteur(self.largeur / 2, self.hauteur / 2)

    def efface_point_precedent(self):
        """revient au point précédent
        """
        self.dbg.p(1, "rentre dans 'efface_point_precedent'")
        # efface la dernière entrée dans le tableau
        self.ui.tableWidget.removeRow(
            int((len(self.listePoints)-1)/self.nb_de_points))
        self.listePoints.decPtr()
        self.dbg.p(2, "self.listePoints" + str(self.listePoints) +
                   "self.points" + str(self.points))
        if len(self.listePoints) % self.nb_de_points != 0:
            try:
                self.points[len(self.listePoints)/self.nb_de_points].pop()
            except KeyError:
                # liée au passage de ptyhon2 à python3 et au changement de comportement de /
                self.dbg.p(1, "Erreur de clé : " +
                           str(len(self.listePoints)/self.nb_de_points))
        else:
            try:
                del self.points[len(self.listePoints)/self.nb_de_points]
            except KeyError:
                self.dbg.p(1, "Erreur de clé : " +
                           str(len(self.listePoints)/self.nb_de_points))
        # dernière image à afficher
        if self.nb_de_points != 1:
            if len(self.listePoints)-1 >= 0:
                if len(self.listePoints) % self.nb_de_points == self.nb_de_points-1:
                    self.index_de_l_image = self.listePoints[len(
                        self.listePoints)-1][0]
        else:
            if len(self.listePoints)-1 >= 0:
                if len(self.listePoints) % self.nb_de_points == self.nb_de_points-1:
                    self.index_de_l_image = self.listePoints[len(
                        self.listePoints)-1][0]+1
        self.affiche_image()
        self.clic_sur_label_video_ajuste_ui(self.index_de_l_image)

    def refait_point_suivant(self):
        """rétablit le point suivant après un effacement
        """
        self.dbg.p(1, "rentre dans 'refait_point_suivant'")
        self.listePoints.incPtr()
        # on stocke si la ligne est complète
        if len(self.listePoints) % self.nb_de_points == 0:
            self.stock_coordonnees_image(
                ligne=int((len(self.listePoints)-1)/self.nb_de_points))
            self.index_de_l_image = self.listePoints[len(
                self.listePoints)-1][0]+1
        self.affiche_image()
        self.clic_sur_label_video_ajuste_ui(self.index_de_l_image)

    def video(self):
        self.dbg.p(1, "rentre dans 'videos'")
        ref = self.ui.comboBox_referentiel.currentText().split(" ")[-1]
        if len(ref) == 0 or ref == "camera":
            return
        c = Cadreur(int(ref), self)
        c.montrefilm()

    def choix_onglets(self, newValue):
        """
        traite les signaux émis par le changement d'onglet, ou
        par le changement de référentiel dans l'onglet des trajectoires."""
        self.dbg.p(1, "rentre dans 'choix_onglets'")
        if self.ui.tabWidget.currentIndex() == 1:
            self.statusBar().clearMessage() # ClearMessage plutôt que hide, ne décale pas les widgets
            self.tracer_trajectoires("absolu")
        elif self.ui.tabWidget.currentIndex() == 2:
            self.statusBar().clearMessage() # ClearMessage plutôt que hide, ne décale pas les widgets
            self.affiche_tableau()
        elif self.ui.tabWidget.currentIndex() == 3:
            self.affiche_grapheur()
            self.MAJ_combox_box_grapheur()
            self.statusBar().clearMessage() # ClearMessage plutôt que hide, ne décale pas les widgets

    def affiche_grapheur(self, MAJ=True):
        self.dbg.p(1, "rentre dans 'affiche_grapheur'")
        # PARTIE OBSOLETE PERMETTANT DE RENVOYER DES ERREURS PYTHON D'UNE ÉVENTUELLE RENTRÉE MANUELLE DES EXPRESSIONS DES VITESSES ETC.
        # A GARDER
        # entete ="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
        # <html><head><meta name="qrichtext" content="1" /><style type="text/css">
        # p, li { white-space: pre-wrap; }
        # </style></head><body style=" font-family:'Ubuntu'; font-size:9pt; font-weight:400; font-style:normal;" bgcolor="#808080"> """

        #erreurs_python1 = """<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">"""
        #erreurs_python2 = """</p>"""
        #footer = """</body></html>"""
        erreur_indices = ""
        erreurs_python = []
        ##################

        # LE CODE SUIVANT PEUT ÊTRE REFACTORISÉ. IL UTILISE UN SYSTÈME DYNAMIQUE PERMETTANT DE PROPOSER DES EXPRESSIONS MANUELLES. JANVIER 2020
        for i in range(self.nb_de_points):
            self.dictionnaire_grandeurs["X"+str(i+1)] = []
            self.dictionnaire_grandeurs["Y"+str(i+1)] = []
            self.dictionnaire_grandeurs["V"+str(i+1)] = []
            # doit s'appeler xprime pour que ça soit orthonal à V pour les replaces.
            self.dictionnaire_grandeurs["xprime"+str(i+1)] = []
            # doit s'appeler yprime pour que ça soit orthonal à V pour les replaces.
            self.dictionnaire_grandeurs["yprime"+str(i+1)] = []
            self.dictionnaire_grandeurs["Ec"+str(i+1)] = []
            self.dictionnaire_grandeurs["Epp"+str(i+1)] = []
            self.dictionnaire_grandeurs["Em"+str(i+1)] = []
            self.dictionnaire_grandeurs["A"+str(i+1)] = []
            # doit s'appeler xprime pour que ça soit orthonal à V pour les replaces.
            self.dictionnaire_grandeurs["vabsprime"+str(i+1)] = []
            # doit s'appeler yprime pour que ça soit orthonal à V pour les replaces.
            self.dictionnaire_grandeurs["vordprime"+str(i+1)] = []
            
        deltaT = self.deltaT
        for ligne in self.points.keys():
            i = 0
            for point in self.points[ligne][1:]:
                pm = self.pointEnMetre(point)
                self.dictionnaire_grandeurs["X"+str(i+1)].append(pm.x())
                self.dictionnaire_grandeurs["Y"+str(i+1)].append(pm.y())
                i += 1
        for i in range(self.nb_de_points):
            for n in range(len(self.points.keys())):
                grandeurX = "self.dictionnaire_grandeurs['X"+str(i+1)+"']"
                grandeurY = "self.dictionnaire_grandeurs['Y"+str(i+1)+"']"
                grandeurVx = "self.dictionnaire_grandeurs['xprime"+str(
                    i+1)+"']"
                grandeurVy = "self.dictionnaire_grandeurs['yprime"+str(
                    i+1)+"']"
                grandeurV = "self.dictionnaire_grandeurs['V"+str(i+1)+"']"
                grandeurAx = "self.dictionnaire_grandeurs['vabsprime"+str(
                    i+1)+"']"
                grandeurAy = "self.dictionnaire_grandeurs['vordprime"+str(
                    i+1)+"']"
                grandeurA = "self.dictionnaire_grandeurs['A"+str(i+1)+"']"
                
                grandeurEc = "self.dictionnaire_grandeurs['Ec"+str(i+1)+"']"
                grandeurEpp = "self.dictionnaire_grandeurs['Epp"+str(i+1)+"']"
                grandeurEm = "self.dictionnaire_grandeurs['Em"+str(i+1)+"']"
                
                
                m = float(self.ui.lineEdit_m.text().replace(',', '.'))
                g = float(self.ui.lineEdit_g.text().replace(',', '.'))
                
                
                expression_Vx = '(X[n+1]-X[n-1])/(2*deltaT)'
                expression_Vy = '(Y[n+1]-Y[n-1])/(2*deltaT)'
                expression_V = 'math.sqrt(Vx[n]**2+Vy[n]**2)'
                expression_Ec = '0.5*m*V[n]**2'
                expression_Epp = 'm*g*Y[n]' if self.sens_Y == 1 else '-m*g*Y[n]'
                expression_Em = 'Epp[n]+Ec[n]'
                expression_Ax = '(Vx[n+1]-Vx[n-1])/(2*deltaT)'
                expression_Ay = '(Vy[n+1]-Vy[n-1])/(2*deltaT)'
                expression_A = 'math.sqrt(Ax[n]**2+Ay[n]**2)'
                
                expression_Vx = expression_Vx.replace('X', grandeurX)

                expression_Vy = expression_Vy.replace('Y', grandeurY)

                expression_V = expression_V.replace('Vx', grandeurVx).replace(
                    'Vy', grandeurVy)

                expression_Ax = expression_Ax.replace('Vx', grandeurVx)

                expression_Ay = expression_Ay.replace('Vy', grandeurVy)

                expression_A = expression_A.replace('Ax', grandeurAx).replace(
                    'Ay', grandeurAy)

                expression_Ec = expression_Ec.replace('V', grandeurV)

                expression_Epp = expression_Epp.replace('Y', grandeurY)

                expression_Em = expression_Em.replace('Ec', grandeurEc).replace('Epp', grandeurEpp)
                
                ###si un jour besoin : 
                #expression_Em = expression_Em.replace('X', grandeurX).replace('Y', grandeurY).replace('Vx', grandeurVx).replace(
                    ##'Vy', grandeurVy).replace('V', grandeurV).replace('Ec', grandeurEc).replace('Epp', grandeurEpp).replace('Em', grandeurEm)
                

                # CETTE PARTIE PERMET DE RENTRER MANUELLEMENT DES EXPRESSIONS.
                #expression_Vx = self.ui.lineEdit_vx.text().replace('X',grandeurX ).replace('Y',grandeurY ).replace('Vx',grandeurVx ).replace('Vy',grandeurVy ).replace('V',grandeurV ).replace('Ec',grandeurEc ).replace('Epp',grandeurEpp ).replace('Em',grandeurEm )
                #expression_Vy = self.ui.lineEdit_vy.text().replace('X',grandeurX ).replace('Y',grandeurY ).replace('Vx',grandeurVx ).replace('Vy',grandeurVy ).replace('V',grandeurV ).replace('Ec',grandeurEc ).replace('Epp',grandeurEpp ).replace('Em',grandeurEm )
                #expression_V = self.ui.lineEdit_v.text().replace('X',grandeurX ).replace('Y',grandeurY ).replace('Vx',grandeurVx ).replace('Vy',grandeurVy ).replace('V',grandeurV ).replace('Ec',grandeurEc ).replace('Epp',grandeurEpp ).replace('Em',grandeurEm )
                #expression_Ec = self.ui.lineEdit_Ec.text().replace('X',grandeurX ).replace('Y',grandeurY ).replace('Vx',grandeurVx ).replace('Vy',grandeurVy ).replace('V',grandeurV ).replace('Ec',grandeurEc ).replace('Epp',grandeurEpp ).replace('Em',grandeurEm )
                #expression_Epp = self.ui.lineEdit_Epp.text().replace('X',grandeurX ).replace('Y',grandeurY ).replace('Vx',grandeurVx ).replace('Vy',grandeurVy ).replace('V',grandeurV ).replace('Ec',grandeurEc ).replace('Epp',grandeurEpp ).replace('Em',grandeurEm )
                #expression_Em = self.ui.lineEdit_Em.text().replace('X',grandeurX ).replace('Y',grandeurY ).replace('Vx',grandeurVx ).replace('Vy',grandeurVy ).replace('V',grandeurV ).replace('Ec',grandeurEc ).replace('Epp',grandeurEpp ).replace('Em',grandeurEm )

                # il faut traiter le cas particulier des indices négatifs : par défaut, si python évalue 'n-1' avec n qui vaut 0, il renvoie un résultat tout de même... ce qui fausse les calculs de vitesse.
                expression_Vx, err1 = self.traite_indices(
                    expression_Vx, i, n, 'Vx')
                expression_Vy, err2 = self.traite_indices(
                    expression_Vy, i, n, 'Vy')
                expression_V, err3 = self.traite_indices(
                    expression_V, i, n, 'V')
                
                expression_Ec, err4 = self.traite_indices(
                    expression_Ec, i, n, 'Ec')
                expression_Epp, err5 = self.traite_indices(
                    expression_Epp, i, n, 'Epp')
                expression_Em, err6 = self.traite_indices(
                    expression_Em, i, n, 'Em')
                
                expression_Ax, err7 = self.traite_indices(
                    expression_Ax, i, n, 'Ax')
                expression_Ay, err8 = self.traite_indices(
                    expression_Ay, i, n, 'Ay')
                expression_A, err9 = self.traite_indices(
                    expression_A, i, n, 'A')
                                
                erreur_indices += err1+err2+err3+err4+err5+err6+err7+err8+err9
                if expression_Vx != '':
                    try:
                        self.dictionnaire_grandeurs["xprime" +
                                                    str(i+1)].append(eval(expression_Vx))
                    except IndexError:
                        erreur_indices += "la vitesse en X du point %s, n'a pas pu être calculée à la position %s<br>" % (
                            i+1, n)
                        self.dictionnaire_grandeurs["xprime" +
                                                    str(i+1)].append(float('NaN'))
                    except:
                        erreurs_python_ = """l'expression python '%s' ne peut pas être évaluée ! <br> """ % (str(expression_Vx.replace(
                            "self.dictionnaire_grandeurs['", "").replace("']", '').replace('xprime', 'Vx').replace('yprime', 'Vy')))
                        # erreurs_python_+=traceback.format_exc()
                        erreurs_python.append(erreurs_python_)
                if expression_Vy != '':
                    try:
                        self.dictionnaire_grandeurs["yprime" +
                                                    str(i+1)].append(eval(expression_Vy))
                    except IndexError:
                        erreur_indices += "la vitesse en Y du point %s, n'a pas pu être calculée à la position %s<br>" % (
                            i+1, n)
                        self.dictionnaire_grandeurs["yprime" +
                                                    str(i+1)].append(float('NaN'))
                    except:
                        erreurs_python_ = """l'expression python '%s' ne peut pas être évaluée !  <br> """ % (str(expression_Vy.replace(
                            "self.dictionnaire_grandeurs['", "").replace("']", '').replace('xprime', 'Vx').replace('yprime', 'Vy')))
                        # erreurs_python_+=traceback.format_exc()
                        erreurs_python.append(erreurs_python_)
                if expression_V != '':
                    try:
                        
                        self.dictionnaire_grandeurs["V" +
                                                    str(i+1)].append(eval(expression_V))
                    except IndexError:
                        erreur_indices += "la vitesse du point %s, n'a pas pu être calculée à la position %s<br>" % (
                            i+1, n)
                        self.dictionnaire_grandeurs["V"+str(i+1)].append(float('NaN'))
                    except:
                        erreurs_python_ = """l'expression python '%s' ne peut pas être évaluée !  <br>""" % (str(expression_V.replace(
                            "self.dictionnaire_grandeurs['", "").replace("']", '').replace('xprime', 'Vx').replace('yprime', 'Vy')))
                        #erreurs_python_ +=traceback.format_exc()
                        erreurs_python.append(erreurs_python_)


                        
                if expression_Ec != '':
                    try:
                        self.dictionnaire_grandeurs["Ec" +
                                                    str(i+1)].append(eval(expression_Ec))
                    except IndexError:
                        erreur_indices += "l'énergie Cinétique du point %s, n'a pas pu être calculée à la position %s<br>" % (
                            i+1, n)
                        self.dictionnaire_grandeurs["Ec" +
                                                    str(i+1)].append(float('NaN'))
                    except:
                        erreurs_python_ = """l'expression python '%s' ne peut pas être évaluée !<br> """ % (str(expression_Ec.replace(
                            "self.dictionnaire_grandeurs['", "").replace("']", '').replace('xprime', 'Vx').replace('yprime', 'Vy')))
                        # erreurs_python_+=traceback.format_exc()
                        erreurs_python.append(erreurs_python_)
                if expression_Epp != '':
                    try:
                        self.dictionnaire_grandeurs["Epp" +
                                                    str(i+1)].append(eval(expression_Epp))
                    except IndexError:
                        erreur_indices += "l'énergie cinétique du point %s, n'a pas pu être calculée à la position %s<br>" % (
                            i+1, n)
                        self.dictionnaire_grandeurs["Epp" +
                                                    str(i+1)].append(float('NaN'))
                    except:
                        erreurs_python_ = """l'expression python '%s' ne peut pas être évaluée !  <br> """ % (str(expression_Epp.replace(
                            "self.dictionnaire_grandeurs['", "").replace("']", '').replace('xprime', 'Vx').replace('yprime', 'Vy')))
                        #erreurs_python_ +=traceback.format_exc()
                        erreurs_python.append(erreurs_python_)                
                
                if expression_Em != '':
                    try:
                        self.dictionnaire_grandeurs["Em" +
                                                    str(i+1)].append(eval(expression_Em))
                    except IndexError:
                        erreur_indices += "l'énergie mécanique du point %s, n'a pas pu être calculée à la position %s<br>" % (
                            i+1, n)
                        self.dictionnaire_grandeurs["Em" +
                                                    str(i+1)].append(float('NaN'))
                    except SyntaxError:
                        erreurs_python_ = """l'expression python '%s' ne peut pas être évaluée !  <br> """ % (str(expression_Em.replace(
                            "self.dictionnaire_grandeurs['", "").replace("']", '').replace('xprime', 'Vx').replace('yprime', 'Vy')))
                        #erreurs_python_ +=traceback.format_exc()
                        erreurs_python.append(erreurs_python_)
                        
                
        #une fois que les vitesses ont été calculées : 
        for i in range(self.nb_de_points):
            for n in range(len(self.points.keys())):
            
                if expression_Ax != '':
                    try:
                        self.dictionnaire_grandeurs["vabsprime" +
                                                    str(i+1)].append(eval(expression_Ax))
                    except IndexError:
                        erreur_indices += "l'accélération en X du point %s, n'a pas pu être calculée à la position %s<br>" % (
                            i+1, n)
                        self.dictionnaire_grandeurs["vabsprime" +
                                                    str(i+1)].append(float('NaN'))
                    except:
                        erreurs_python_ = """l'expression python '%s' ne peut pas être évaluée ! <br> """ % (str(expression_Ax.replace(
                            "self.dictionnaire_grandeurs['", "").replace("']", '').replace('vabsprime', 'Ax').replace('vordprime', 'Ay')))
                        # erreurs_python_+=traceback.format_exc()
                        erreurs_python.append(erreurs_python_)
                if expression_Ay != '':
                    try:
                        self.dictionnaire_grandeurs["vordprime" +
                                                    str(i+1)].append(eval(expression_Ay))
                    except IndexError:
                        erreur_indices += "l'accélération en Y du point %s, n'a pas pu être calculée à la position %s<br>" % (
                            i+1, n)
                        self.dictionnaire_grandeurs["vordprime" +
                                                    str(i+1)].append(float('NaN'))
                    except:
                        erreurs_python_ = """l'expression python '%s' ne peut pas être évaluée !  <br> """ % (str(expression_Ay.replace(
                            "self.dictionnaire_grandeurs['", "").replace("']", '').replace('vabsprime', 'Ax').replace('vordprime', 'Ay')))
                        # erreurs_python_+=traceback.format_exc()
                        erreurs_python.append(erreurs_python_)
                if expression_A != '':
                    try:
                        self.dictionnaire_grandeurs["A" +
                                                    str(i+1)].append(eval(expression_A))
                    except IndexError:
                        erreur_indices += "l'accélération du point %s, n'a pas pu être calculée à la position %s<br>" % (
                            i+1, n)
                        self.dictionnaire_grandeurs["A"+str(i+1)].append(float('NaN'))
                    except:
                        erreurs_python_ = """l'expression python '%s' ne peut pas être évaluée !  <br>""" % (str(expression_V.replace(
                            "self.dictionnaire_grandeurs['", "").replace("']", '').replace('vabsprime', 'Ax').replace('vordprime', 'Ay')))
                        #erreurs_python_ +=traceback.format_exc()
                        erreurs_python.append(erreurs_python_)
                
        self.dbg.p(3, "erreurs a la fin : %s" % erreur_indices)
        self.dbg.p(3, "erreurs python : %s" % erreurs_python)
        #text_textedit = entete + '<p>' + erreur_indices + '</p>'
        text_textedit = ""
        if len(erreurs_python) > 0:
            for item in erreurs_python:
                if not item in text_textedit:
                    #text_textedit += erreurs_python1
                    text_textedit += item
                    #text_textedit += erreurs_python2
        else:
            text_textedit += "Pour les points où c'était possible, les expressions python rentrées ont été calculées avec succès !"
        self.dbg.p(3, "dixtionnaires_grandeurs : %s" % self.dictionnaire_grandeurs)

    def MAJ_combox_box_grapheur(self):
        if self.graphe_deja_choisi is None : #premier choix de graphe
            self.ui.comboBox_X.clear()
            self.ui.comboBox_Y.clear()
            self.ui.comboBox_X.insertItem(-1,
                                        _translate("pymecavideo", "Choisir ...", None))
            self.ui.comboBox_Y.insertItem(-1,
                                        _translate("pymecavideo", "Choisir ...", None))
            self.ui.comboBox_X.addItem('t')
            self.ui.comboBox_Y.addItem('t')
            for grandeur in self.dictionnaire_grandeurs.keys():
                if self.dictionnaire_grandeurs[grandeur] != []:
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
                    self.ui.comboBox_X.addItem(grandeur_a_afficher)
                    self.ui.comboBox_Y.addItem(grandeur_a_afficher)
        #else : #il y a déjà eu un choix de graphe
            #self.ui.comboBox_X.setItem(self.graphe_deja_choisi[1])
            #self.ui.comboBox_Y.setItem(self.graphe_deja_choisi[0])
        
    def traite_indices(self, expression, i, n, grandeur):
        """cette fonction traite les indices négatifs afin que python, justement... ne les traite pas"""
        self.dbg.p(1, "rentre dans 'traite_indices'")
        # vérification de la présence d'une expression entre []
        erreur = ""
        expr = ""
        start = False
        liste_expressions_entre_crochets = []
        for c in expression:
            if start:
                expr += c
            if c == '[':
                start = True
            elif c == ']':
                start = False
                liste_expressions_entre_crochets.append(expr[:-1])
                expr = ""
        for expr_a_tester in liste_expressions_entre_crochets:
            if 'n' in expr_a_tester:
                if eval(expr_a_tester) < 0:
                    erreur += "la variable %s du point %s, n'a pas pu être calculée à la position %s<br>" % (
                        grandeur, i+1, n)
                    return "float('NaN')", erreur
        return expression, erreur

    def dessine_graphe_avant(self):
        if self.graphe_deja_choisi is not None : 
            self.graphe_deja_choisi = None #si changement ds les combobox, on réinitilaise le choix.
        self.dessine_graphe()
        
    def dessine_graphe(self):
        """dessine les graphes avec pyqtgraph au moment où les combobox sont choisies"""
        self.dbg.p(1, "rentre dans 'dessine_graphe'")
        X, Y = [], []
        styles = {0: {'pen': None, 'symbol': '+'}, 1: {'pen': (0, 0, 0), 'symbol': '+'}, 2: {'pen': (
            0, 0, 0), 'symbol': None}}  # Dictionnaire contenant les différents styles de graphes
        # Index du comboxBox styles, inspirés de Libreoffice
        style = self.ui.comboBox_style.currentIndex()
        
        if self.graphe_deja_choisi is not None : 
            abscisse = self.graphe_deja_choisi[1].strip('|')
            ordonnee = self.graphe_deja_choisi[0].strip('|')
        else : 
            abscisse = self.ui.comboBox_X.currentText().strip('|')
            ordonnee = self.ui.comboBox_Y.currentText().strip('|')
        # Définition des paramètres 'pen' et 'symbol' pour pyqtgraph
        pen, symbol = styles[style]['pen'], styles[style]['symbol']
        grandeurX = abscisse.replace(
            'Vx', 'xprime').replace('Vy', 'yprime').replace('Ax', 'vabsprime').replace('Ay', 'vordprime')
        grandeurY = ordonnee.replace(
            'Vx', 'xprime').replace('Vy', 'yprime').replace('Ax', 'vabsprime').replace('Ay', 'vordprime')
        if grandeurX == 't':
            X = [i*self.deltaT for i in range(len(self.points))]
        elif grandeurX != "Choisir ...":
            try:
                X = self.dictionnaire_grandeurs[grandeurX]
            except:
                pass
        if grandeurY == 't':
            Y = [i*self.deltaT for i in range(len(self.points))]
        elif grandeurY != "Choisir ...":
            try:
                Y = self.dictionnaire_grandeurs[grandeurY]
            except:
                pass
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

            if not hasattr(self, 'graphWidget'):  # premier tour
                self.ui.widget_graph.setText('')
                self.graphWidget = pg.PlotWidget(
                    title=titre, parent=self.ui.widget_graph)
                self.graphWidget.setMenuEnabled(False)
                self.graphWidget.setLabel('bottom', unite_x)
                self.graphWidget.setLabel('left', unite_y)
                self.verticalLayout_onglet4 = QVBoxLayout(self.ui.widget_graph)
                self.verticalLayout_onglet4.setContentsMargins(0, 0, 0, 0)
                self.verticalLayout_onglet4.setObjectName(
                    "verticalLayout_graph")
                self.verticalLayout_onglet4.addWidget(self.graphWidget)
                self.graphWidget.plot(X, Y, pen=pen, symbol=symbol)
                self.graphWidget.autoRange()
                self.graphWidget.show()
                self.pg_exporter = pg.exporters.ImageExporter(self.graphWidget.plotItem)
            else:
                plotItem = self.graphWidget.getPlotItem()
                plotItem.setTitle(titre)
                self.graphWidget.setLabel('bottom', unite_x)
                self.graphWidget.setLabel('left', unite_y)
                # enlève si besoin les points non calculés
                #X, Y = self.nettoyage_points(X, Y)
                self.graphWidget.clear()
                self.graphWidget.plot(X, Y, pen=pen, symbol=symbol)
                self.graphWidget.autoRange()
                self.graphWidget.show()
            self.graphe_deja_choisi = (ordonnee, abscisse)
                
    def enregistre_graphe(self):
        if hasattr (self, 'pg_exporter'):
            base_name = os.path.splitext(os.path.basename(self.filename))[0]
            defaultName = os.path.join(DOCUMENT_PATH[0], base_name+'.png')
            fichier = QFileDialog.getSaveFileName(self,
                                              _translate(
                                                  "pymecavideo", "Enregistrer le graphique", None),
                                              defaultName, _translate("pymecavideo", "fichiers images(*.png)", None))
            try :
                self.pg_exporter.export(fichier[0])
            except :
                QMessageBox.critical(None, _translate("pymecavideo", "Erreur lors de l'enregistrement", None), _translate("pymecavideo", "Echec de l'enregistrement du fichier:<b>\n{0}</b>", None).format(
                        fichier[0]), QMessageBox.Ok, QMessageBox.Ok)

    def nettoyage_points(self, X_, Y_):
        """permet de tenir compte des expressions "négatives" quand on va chercher des indices : python évlaue corerctement X[-1] alors qu'on ne le veut pas. Un passage dans self.traite_indices à mis certaines valeurs non calculées à False. Il suffit de les enlever dans X et Y"""
        X_f, Y_f = [], []
        for i in range(len(X_)):
            if X_[i] != False and Y_[i] != False:
                Y_f.append(Y_[i])
                X_f.append(X_[i])
        return X_f, Y_f

    def tracer_trajectoires(self, newValue):
        """
        Cette fonction est appelée par un changement de référentiel.
        On peut aussi appeler cette fonction directement, auquel cas on
        donne la valeur "absolu" à newValue pour reconnaître ce cas.
        efface les trajectoires anciennes, puis
        trace les trajectoires en fonction du référentiel choisi.

        """
        self.dbg.p(1, "rentre dans 'tracer_trajectoires'")
        if newValue == "absolu":
            ref = "camera"
            self.label_trajectoire.origine_mvt = self.label_video.origine
            # mets à jour le comboBox referentiel :
            self.ui.comboBox_referentiel.setCurrentIndex(
                self.ui.comboBox_referentiel.count()-1)
            self.ui.comboBox_referentiel.update()
        else:
            ref = self.ui.comboBox_referentiel.currentText().split(" ")[-1]
            self.label_trajectoire.origine_mvt = self.label_video.origine
        if len(ref) == 0:
            return
        if ref != "camera":
            self.ui.button_video.setEnabled(1)
            self.label_trajectoire.chrono = False
            bc = self.mediane_trajectoires(int(ref) - 1)
            origine = vecteur(self.label_video.width() // 2,
                              self.label_video.height() // 2) - bc
            self.label_trajectoire.origine = origine
            self.label_trajectoire.origine_mvt = origine
            self.label_trajectoire.referentiel = ref
        else:  # if camera, all tranlsations are disabled
            self.label_trajectoire.referentiel = 0
            self.label_trajectoire.origine = vecteur(0, 0)
        self.dbg.p(3, "origine %s, ref %s" %
                   (str(self.label_trajectoire.origine), str(ref)))
        self.label_trajectoire.reDraw()

    def affiche_point_attendu(self, n):
        """
        Renseigne sur le numéro du point attendu
        affecte la ligne de statut et la ligne sous le zoom
        """
        self.dbg.p(1, "rentre dans 'affiche_point_attendu'")
        self.dbg.p(1, "Point n° %i" % n)
        self.mets_a_jour_label_infos(
            _translate("pymecavideo", "Pointage des positions : cliquer sur le point N° {0}", None).format(n+1))

    def clic_sur_label_video(self, liste_points=None, interactif=True):
        self.dbg.p(1, "rentre dans 'clic_sur_label_video'")
        self.lance_capture = True
        # on fait des marques pour les points déjà visités
        etiquette = "@abcdefghijklmnopqrstuvwxyz"[
            len(self.listePoints) % self.nb_de_points]
        self.point_attendu = len(self.listePoints) % self.nb_de_points
        self.dbg.p(2, "self.point_attendu %s" % self.point_attendu)
        self.affiche_point_attendu(self.point_attendu)
        if self.index_de_l_image <= self.image_max:  # si on n'atteint pas encore la fin de la vidéo
            self.lance_capture = True
            self.stock_coordonnees_image(
                ligne=int((len(self.listePoints)-1)/self.nb_de_points))
            if interactif:
                self.modifie = True
            self.clic_sur_label_video_ajuste_ui(self.point_attendu)
        if self.index_de_l_image > self.image_max:
            self.lance_capture = False
            self.mets_a_jour_label_infos(_translate(
                "pymecavideo", "Vous avez atteint la fin de la vidéo", None))
            self.index_de_l_image = self.image_max
        self.nb_clics += 1
        if self.nb_clics == self.nb_de_points:
            self.nb_clics = 0
            self.index_de_l_image += 1
            self.affiche_image()
        
            if self.refait_point : #quandon refait 1 seul point faux.
                self.fin_refait_point_depuis_tableau()
        
    def enableDefaire(self, value):
        """
        Contrôle la possibilité de défaire un clic
        @param value booléen
        """
        self.dbg.p(1, "rentre dans 'enableDefaire, %s'" % (str(value)))
        self.ui.pushButton_defait.setEnabled(value)
        self.ui.actionDefaire.setEnabled(value)
        # permet de remettre l'interface à zéro
        if not value:
            self.ui.spinBox_image.setEnabled(True)

    def enableRefaire(self, value):
        """
        Contrôle la possibilité de refaire un clic
        @param value booléen
        """
        self.dbg.p(1, "rentre dans 'enableRefaire, %s'" % (value))
        self.ui.pushButton_refait.setEnabled(value)
        self.ui.actionRefaire.setEnabled(value)

    def clic_sur_label_video_ajuste_ui(self, point_attendu):
        """
        Ajuste l'interface utilisateur pour attendre un nouveau clic
        @param point_attendu le numéro du point qui est à cliquer
        """
        self.dbg.p(1, "rentre dans 'clic_sur_label_video_ajuste_ui'")
        self.lance_capture = True
        if point_attendu == 1:  # pour une acquisition sur une nouvelle image
            self.dbg.p(1, "self.nb_image_deja_analysees >= len(self.points) ? %s %s" % (
                len(self.listePoints), self.nb_de_points-len(self.listePoints) % self.nb_de_points))
            self.affiche_image()
            self.tracer_trajectoires("absolu")
        self.affiche_image()
        self.enableDefaire(len(self.listePoints) > 0)
        self.enableRefaire(self.listePoints.nextCount() > 0)

    def enregistre_dans_listePoints(self, point, index=None):
        """
        enregistre un clic dans self.listePoints à la bonne place.
        on ajoute à cette liste un triplet :
        numéro de l'image, rang du point (0,1 ou 2 s'il y a trois
        points à saisir par image), et le point lui-même.

        Le calcul du rang du point est lié à self.nb_clics, calculé dans clic_sur_label_video()
        @param point un point à enregistrer
        @param index un numéro d'image. S'il est indéfini (par défaut), il
        est remplacé par self.index_de_l_image.
        """
        self.dbg.p(1, "rentre dans 'enregistre_dans_listePoints'")
        if index:
            i = index
        else:
            i = self.index_de_l_image
        nieme  = self.nb_clics
        if self.refait_point : #arrive si on refait qu'un seul point à partir du tableau de l'onglet 3.
            self.listePoints[(self.index_de_l_image-self.premiere_image)*self.nb_de_points+nieme] = [i, nieme, point]
            
        else : 
            self.listePoints.append([i, nieme, point])
        self.dbg.p(3, "dans 'enregistre_dans_listePoints', self.listePoints vaut %s"%self.listePoints)
        return

    def stock_coordonnees_image(self, ligne,  interactif=True, index_image=False):
        """
        place les données dans le tableau, rempli les dictionnaires de pixels
        @param ligne le numérode la ligne où placer les données (commence à 0)
        @param interactif vrai s'il faut rafraîchir tout de suite l'interface utilisateur.
        """
        self.dbg.p(1, "rentre dans 'stock_coordonnees_image'")
        if index_image == False:
            # l'index est sur la dernière image traitée
            index_image = self.listePoints[-1][0]
        else : 
            index_image = self.index_de_l_image-1
        t = "%4f" % ((index_image - self.premiere_image) * self.deltaT)

        self.dbg.p(2, "dans 'stock_coordonnees_image', index_image = %s"%(index_image))


        # construction de l'ensemble des points pour l'image actuelle
        listePointsCliquesParImage = []
        for point in self.listePoints:
            if point[0] == index_image:
                listePointsCliquesParImage.append(point[2])
        self.points[ligne] = [t] + listePointsCliquesParImage

        # Pour chaque point dans liste_points, insère les valeur dans la ligne
        for point in listePointsCliquesParImage:
            # ajoute les coordonnées "en pixel" des points dans des dictionnaires de coordonnées
            x = point.x()
            y = point.y()
            if x in self.pX.keys():
                self.pX[x].append(point)
            else:
                self.pX[x] = [point]
            if y in self.pY.keys():
                self.pY[y].append(point)
            else:
                self.pY[y] = [point]

    def affiche_tableau(self):
        """lancée à cahque affichage du tableau, recalcule les coordonnées à afficher à partir des listes de points."""
        self.dbg.p(1, "rentre dans 'affiche_tableau'")
                
        # active ou désactive les checkbox énergies (n'ont un intérêt que si les échelles sont faites)
        if self.echelle_faite:
            self.ui.checkBox_Ec.setEnabled(1)
            self.ui.checkBox_Epp.setEnabled(1)
            if self.ui.checkBox_Ec.isChecked() and self.ui.checkBox_Epp.isChecked():
                self.ui.checkBox_Em.setEnabled(1)
        else:
            self.ui.checkBox_Ec.setEnabled(0)
            self.ui.checkBox_Em.setEnabled(0)
            self.ui.checkBox_Epp.setEnabled(0)

        # masse de l'objet
        if self.ui.checkBox_Ec.isChecked():
            if self.masse_objet == 0:
                masse_objet_raw = QInputDialog.getText(None,
                                                       _translate(
                                                           "pymecavideo", "Masse de l'objet", None),
                                                       _translate("pymecavideo",
                                                                  "Quelle est la masse de l'objet ? (en kg)",
                                                                  None),
                                                       QLineEdit.Normal, u"1.0")
                if masse_objet_raw[1] == False:
                    return None
                try:
                    masse_objet = [
                        float(masse_objet_raw[0].replace(",", ".")), masse_objet_raw[1]]
                    if masse_objet[0] <= 0 or masse_objet[1] == False:
                        self.mets_a_jour_label_infos(_translate(
                            "pymecavideo", " Merci d'indiquer une masse valable", None))
                    self.masse_objet = float(masse_objet[0])
                except:
                    self.mets_a_jour_label_infos(_translate(
                        "pymecavideo", " Merci d'indiquer une masse valable", None))
                    self.ui.checkBox_Ec.setChecked(0)
        # initialise tout le tableau (nb de colonnes, unités etc.)
        self.cree_tableau()
        colonnes_sup = self.ui.checkBox_Ec.isChecked()+self.ui.checkBox_Epp.isChecked() + \
            self.ui.checkBox_Em.isChecked()
        for ligne in self.points.keys():
            # rentre le temps dans la première colonne
            self.ui.tableWidget.setItem(
                ligne, 0, QTableWidgetItem(self.points[ligne][0]))
            i = 0
            for point in self.points[ligne][1:]:
                try:
                    pm = self.pointEnMetre(point)
                except:
                    pm = point
                self.ui.tableWidget.setItem(
                    ligne, i + 1, QTableWidgetItem(str(pm.x())))
                self.ui.tableWidget.setItem(
                    ligne, i + 2, QTableWidgetItem(str(pm.y())))
                i += 2+colonnes_sup

        # calculs des énergies
        ancienPoint = None
        for ligne in self.points.keys():
            i = 0
            for point in self.points[ligne][1:]:
                try:
                    pm = self.pointEnMetre(point)
                except:
                    pm = point
                if ancienPoint != None:
                    v = (pm - ancienPoint).norme() / self.deltaT
                ancienPoint = pm
                try:
                    for j in range(colonnes_sup):
                        cptr = 0
                        if self.ui.checkBox_Ec.isChecked():
                            Ec = 0.5*self.masse_objet*v*v
                            self.ui.tableWidget.setItem(
                                ligne, 3+cptr + (2+colonnes_sup)*i, QTableWidgetItem(str(Ec)))
                            cptr += 1
                        if self.ui.checkBox_Epp.isChecked():
                            Epp = self.masse_objet*9.81*pm.y()  # TODO faire varier g
                            self.ui.tableWidget.setItem(
                                ligne, 3+cptr + (2+colonnes_sup)*i, QTableWidgetItem(str(Epp)))
                            cptr += 1
                        if self.ui.checkBox_Em.isChecked():
                            self.ui.tableWidget.setItem(
                                ligne, 3+cptr + (2+colonnes_sup)*i, QTableWidgetItem(str(Ec+Epp)))
                            cptr += 1
                except UnboundLocalError:  # pour premier point, la vitesse n'est pas définie
                    pass
                i += 1
        ###Ajout d'un bouton pour refaire le point.
        
            qpushbutton = QPushButton()
            qpushbutton.setIcon(QIcon(":/data/icones/curseur_cible.svg"))
            qpushbutton.setToolTip("refaire le pointage\n de l'image %s"%(ligne+1))
            qpushbutton.setFlat(True)
            qpushbutton.clicked.connect( lambda checked, b=qpushbutton: self.refait_point_depuis_tableau( b ))

            #self.liste_qpushbutton.append(qpushbutton) #nécessaire sinon le ramsse miette vire tout
            self.ui.tableWidget.setCellWidget(
                                    ligne, self.nb_de_points * 2 + 1 + colonnes_sup*self.nb_de_points, qpushbutton)

    def refait_point_depuis_tableau(self, qpbn ):
        self.refait_point=True
        numero_image = qpbn.toolTip().split(' ')[-1]
        self.index_de_l_image_actuelle = self.index_de_l_image
        self.index_de_l_image = int(numero_image)+self.premiere_image-1
        
        self.ui.tabWidget.setCurrentIndex(0)
        point_actuel = len(self.listePoints)%self.nb_de_points
        self.clic_sur_label_video_ajuste_ui(point_actuel)
        
    def fin_refait_point_depuis_tableau(self): 
        self.dbg.p(1, "rentre dans 'transforme_index_en_temps'")
        self.refait_point = False
        
        #####remplacement de la valeur de self.points pour la ligne correspondante
        self.stock_coordonnees_image(self.index_de_l_image-self.premiere_image-1, index_image=True)
        
        self.index_de_l_image = self.index_de_l_image_actuelle
        self.index_de_l_image_actuelle = None
        self.clic_sur_label_video_ajuste_ui(0)
        self.ui.tabWidget.setCurrentIndex(2)
        
        
    def transforme_index_en_temps(self, index):
        self.dbg.p(1, "rentre dans 'transforme_index_en_temps'")
        return float(self.deltaT * (index))

    def affiche_image_spinbox(self):
        self.dbg.p(1, "rentre dans 'affiche_image_spinbox'")
        if self.lance_capture:
            if self.ui.spinBox_image.value() < self.index_de_l_image:
                # si le point est sur une image, on efface le point
                if self.ui.spinBox_image.value() == self.listePoints[len(self.listePoints)-1][0]:
                    for i in range(self.nb_de_points):
                        self.efface_point_precedent()
            if self.ui.spinBox_image.value() > self.index_de_l_image:
                # on refait le point
                if self.ui.spinBox_image.value() <= self.listePoints[len(self.listePoints)-1][0]:
                    for i in range(self.nb_de_points):
                        #self.efface_point_precedent()
                        self.refait_point_suivant()
        self.index_de_l_image = self.ui.spinBox_image.value()
        try:
            self.affiche_image()
        except:
            pass

    def affiche_image(self):
        try:
            self.dbg.p(1, "rentre dans 'affiche_image'" + ' ' +
                       str(self.index_de_l_image) + ' ' + str(self.image_max))
            if self.index_de_l_image <= self.image_max:
                self.index_avant = self.index_de_l_image
                self.dbg.p(1, "affiche_image " +
                           "self.index_de_l_image <= self.image_max")
                ok, self.image_opencv = self.extract_image(
                    self.index_de_l_image)  # 2ms
                self.imageExtraite = toQImage(self.image_opencv)
                self.dbg.p(2, "Image extraite : largeur : %s, hauteur %s: " % (
                    self.imageExtraite.width(), self.imageExtraite.height()))
                if hasattr(self, "label_video"):
                    self.afficheJusteImage()  # 4 ms
                if self.ui.horizontalSlider.value() != self.index_de_l_image:
                    self.dbg.p(1, "affiche_image " + "horizontal")
                    self.ui.horizontalSlider.setValue(self.index_de_l_image)
                    self.ui.spinBox_image.setValue(
                        self.index_de_l_image)  # 0.01 ms
            elif self.index_de_l_image > self.image_max:
                self.index_de_l_image = self.image_max
                self.lance_capture = False
        except:
            # arrive quand on ouvreun fichier pour la prmeière fois, au premier resize.
            pass

    def afficheJusteImage(self):
        self.dbg.p(1, "Rentre dans 'AffichejusteImage'")
        if self.a_une_image:
            self.imageAffichee = self.imageExtraite.scaled(
                self.label_video.width(), self.label_video.height())  # 4-6 ms
            self.label_video.setMouseTracking(True)
            self.label_video.setPixmap(QPixmap.fromImage(self.imageAffichee))
            self.label_video.met_a_jour_crop()

    def recommence_echelle(self):
        self.dbg.p(1, "rentre dans 'recommence_echelle'")
        self.ui.tabWidget.setCurrentIndex(0)
        self.label_video.echelle_image = echelle()
        self.affiche_echelle()
        try:
            self.job.dialog.close()
            self.job.close()
        except AttributeError:
            pass
        self.demande_echelle()

    def affiche_image_slider(self):
        self.dbg.p(1, "rentre dans 'affiche_image_slider'")
        self.index_de_l_image = self.ui.horizontalSlider.value()
        self.affiche_image()

    def affiche_image_slider_move(self):
        """only change spinBox value"""
        self.dbg.p(1, "rentre dans 'affiche_image_slider_move'")
        self.ui.spinBox_image.setValue(self.ui.horizontalSlider.value())
        # self.enableRefaire(0)

    def demande_echelle(self):
        """
        demande l'échelle interactivement
        """
        self.dbg.p(1, "rentre dans 'demande_echelle'")
        echelle_result_raw = QInputDialog.getText(None,
                                                  _translate(
                                                      "pymecavideo", "Définir léchelle", None),
                                                  _translate("pymecavideo",
                                                             "Quelle est la longueur en mètre de votre étalon sur l'image ?",
                                                             None),
                                                  QLineEdit.Normal, u"1.0")
        if echelle_result_raw[1] == False:
            return None
        try:
            echelle_result = [
                float(echelle_result_raw[0].replace(",", ".")), echelle_result_raw[1]]
            if echelle_result[0] <= 0 or echelle_result[1] == False:
                self.mets_a_jour_label_infos(_translate(
                    "pymecavideo", " Merci d'indiquer une échelle valable", None))
            else:
                self.label_video.echelle_image.etalonneReel(echelle_result[0])
                self.job = Label_Echelle(self.label_video, self)
                self.job.setPixmap(QPixmap(toQImage(self.image_opencv)))
                self.job.show()
                self.change_axe_ou_origine()
        except ValueError:
            self.mets_a_jour_label_infos(_translate(
                "pymecavideo", " Merci d'indiquer une échelle valable", None))
            self.demande_echelle()

    def calculeLesVitesses(self):
        """à partir des sets de points, renvoie les vitesses selon l'axe X, selon l'axe Y et les normes des vitesses"""
        self.vitesses = {}

    def recalculLesCoordonnees(self):
        """permet de remplir le tableau des coordonnées à la demande. Se produit quand on ouvre un fichier mecavideo ou quan don recommence l'échelle"""
        for i in range(len(self.points)):
            self.ui.tableWidget.insertRow(i)
            self.ui.tableWidget.setItem(
                i, 0, QTableWidgetItem(self.points[i][0]))
            for j in range(self.nb_de_points):
                try:
                    p = self.pointEnMetre(self.points[i][j+1])
                    self.ui.tableWidget.setItem(
                        i, j*(self.nb_de_points)+1, QTableWidgetItem(str(p.x())))
                    self.ui.tableWidget.setItem(
                        i, j*(self.nb_de_points) + 2, QTableWidgetItem(str(p.y())))
                except:
                    pass  # si pas le bon nb de points cliqués
        # esthétique : enleve la derniere ligne
        self.ui.tableWidget.removeRow(len(self.points))

    def feedbackEchelle(self, p1, p2):
        """
        affiche une trace au-dessus du self.job, qui reflète les positions
        retenues pour l'échelle
        """
        self.dbg.p(1, "rentre dans 'feedbackEchelle'")
        try:
            self.label_echelle_trace.hide()
            del self.label_echelle_trace
        except:
            pass  # si pas de vidéo preexistante

        self.label_echelle_trace = Label_Echelle_Trace(
            self.label_video, p1, p2)
        # on garde les valeurs pour le redimensionnement
        self.dbg.p(2, "Points de l'echelle : p1 : %s, p2 : %s" % (p1, p2))
        self.label_echelle_trace.show()
        if self.echelle_faite:
            self.mets_en_orange_echelle()
            self.ui.Bouton_Echelle.setEnabled(1)

    def closeEvent(self, event):
        """
        Un crochet pour y mettre toutes les procédures à faire lors
        de la fermeture de l'application.
        """
        self.dbg.p(1, "rentre dans 'closeEvent'")
        for plotwidget in self.dictionnairePlotWidget.values():
            plotwidget.parentWidget().close()
            plotwidget.close()
            del plotwidget

    def verifie_donnees_sauvegardees(self):
        self.dbg.p(1, "rentre dans 'verifie_donnees_sauvegardees'")
        if self.modifie:
            retour = QMessageBox.warning(
                self,
                _translate(u"pymecavideo", "Les données seront perdues", None),
                _translate(
                    u"pymecavideo", "Votre travail n'a pas été sauvegardé\nVoulez-vous les sauvegarder ?", None),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if retour == QMessageBox.Yes:
                self.enregistre_ui()
                return True
            elif retour == QMessageBox.No:
                return True
            elif retour == QMessageBox.Cancel:
                return False
        else:
            return True

    def verifie_m_grapheur(self):
        m = self.ui.lineEdit_m.text().replace(',', '.')
        if m != "":
            try:
                float(m)
            except:
                retour = QMessageBox.critical(
                    self,
                    _translate(u"pymecavideo", "MAUVAISE VALEUR !", None),
                    _translate(
                        u"pymecavideo", "La valeur rentrée n'est pas compatible avec le calcul", None),
                    QMessageBox.Yes)
        self.affiche_grapheur()
        self.dessine_graphe()

    def verifie_g_grapheur(self):
        g = self.ui.lineEdit_g.text().replace(',', '.')
        if g != "":
            try:
                float(g)
            except:
                retour = QMessageBox.critical(
                    self,
                    _translate(u"pymecavideo", "MAUVAISE VALEUR !", None),
                    _translate(
                        u"pymecavideo", "La valeur rentrée n'est pas compatible avec le calcul", None),
                    QMessageBox.Yes)
        self.affiche_grapheur()
        self.dessine_graphe()

    def mets_a_jour_label_infos(self, message):
        """
        On utilise la barre de status pour afficher les messages : 
        permet de gagner de la place en envelant le label_infos_image
        @param message message à afficher
        """
        self.dbg.p(1, "rentre dans 'mets_a_jour_label_infos'")
        self.statusBar().showMessage(message)

    def openexample(self):
        self.dbg.p(1, "rentre dans 'openexample'")
        dir_ = "%s" % (self._dir("videos"))
        # self.reinitialise_tout()
        filename, hints = QFileDialog.getOpenFileName(
            self, _translate("pymecavideo", "Ouvrir une vidéo", None), dir_,
            _translate(
                "pymecavideo",
                "fichiers vidéos (*.avi *.mp4 *.ogv *.mpg *.mpeg *.ogg *.mov *.wmv)",
                None
            )
        )
        self.openTheFile(filename)

    def openfile(self):
        """
        Ouvre un dialogue pour choisir un fichier vidéo puis le charge
        """
        self.dbg.p(1, "rentre dans 'openfile'")
        dir_ = self._dir("videos")
        filename, hints = QFileDialog.getOpenFileName(
            self, _translate("pymecavideo", "Ouvrir une vidéo", None),
            dir_,
            _translate("pymecavideo",
                       "fichiers vidéos ( *.avi *.mp4 *.ogv *.mpg *.mpeg *.ogg *.wmv *.mov)",
                       None))
        self.openTheFile(filename)
        try:
            self.reinitialise_capture()
        except:
            pass

    def renomme_le_fichier(self):
        self.dbg.p(1, "rentre dans 'renomme_le_fichier'")
        renomme_fichier = QMessageBox.warning(self, _translate("pymecavideo", "Nom de fichier non conforme", None),
                                              _translate("pymecavideo", """\
Le nom de votre fichier contient des caractères accentués ou des espaces.
Merci de bien vouloir le renommer avant de continuer""", None),
                                              QMessageBox.Ok, QMessageBox.Ok)
        filename = QFileDialog.getOpenFileName(self, _translate("pymecavideo", "Ouvrir une vidéo"),
                                               self._dir("videos", None),
                                               "*.avi")
        self.openTheFile(filename)

    def openTheFile(self, filename):
        """
        Ouvre le fichier de nom filename, enregistre les préférences de
        fichier vidéo.
        @param filename nom du fichier
        """
        self.dbg.p(1, "rentre dans 'openTheFile'")
        if filename != "":
            self.filename = filename
            goOn = self.init_cvReader()
            if goOn:  # video is in good format
                self.prefs.lastVideo = self.filename
                self.ui.tabWidget.setTabEnabled(0, True)
                self.init_image()
                self.init_capture()
                self.ratio = self.determineRatio()
                self.ui.spinBox_chrono.setMaximum(int(self.image_max))
                self.change_axe_ou_origine()
                self.prefs.videoDir = os.path.dirname(self.filename)
                self.prefs.save()

    def init_capture(self):
        """met le panneaux de capture visible"""
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(1)
        self.ui.menuE_xporter_vers.setEnabled(1)
        self.ui.actionSaveData.setEnabled(1)
        self.mets_a_jour_label_infos(
            _translate("pymecavideo", "Veuillez choisir une image (et définir l'échelle)", None))
        self.ui.Bouton_Echelle.setEnabled(True)
        self.ui.spinBox_nb_de_points.setEnabled(True)
        self.ui.horizontalSlider.setEnabled(1)
        self.ui.checkBox_abscisses.setEnabled(1)
        self.ui.checkBox_ordonnees.setEnabled(1)
        self.ui.checkBox_auto.setEnabled(1)
        self.ui.Bouton_lance_capture.setEnabled(True)

    def propos(self):
        self.dbg.p(1, "rentre dans 'propos'")
        try:
            loc = locale.getdefaultlocale()[0][0:2]
        except TypeError:
            loc = ''
        if loc in licence.keys():
            licence_XX = licence[loc] % Version
        else:
            licence_XX = licence["en"] % Version
        QMessageBox.warning(None, u"Licence", licence_XX,
                            QMessageBox.Ok, QMessageBox.Ok)

    def aide(self):
        self.dbg.p(1, "rentre dans 'aide'")
        lang = locale.getdefaultlocale()[0][0:2]
        helpfile = "%s/help-%s.xhtml" % (self._dir("help"), lang)
        if os.path.exists(helpfile):
            command = "firefox --new-window %s" % helpfile
            status = subprocess.call(command, shell=True)
            if status != 0:
                command = "x-www-browser %s" % helpfile
                status = subprocess.call(command, shell=True)
        else:
            QMessageBox.warning(
                None, "Aide",
                _translate("pymecavideo", "Désolé pas de fichier d'aide pour le langage {0}.", None).format(lang))

    def init_image(self):
        """intialise certaines variables lors le la mise en place d'une nouvelle image"""
        self.dbg.p(1, "rentre dans 'init_image'")
        self.index_de_l_image = 1
        ok, self.image_opencv = self.extract_image(self.index_de_l_image)
        self.ratio = self.determineRatio()
        self.init_interface()
        self.trajectoire = {}
        self.ui.spinBox_image.setMinimum(1)
        self.calcul_deltaT()
        self.defini_barre_avancement()
        self.label_video.echelle_image = echelle()
        self.affiche_echelle()
        self.ui.tab_traj.setEnabled(0)
        self.ui.spinBox_image.setEnabled(1)
        self.affiche_image()

    def verifie_IPS(self):
        self.dbg.p(1, "rentre dans 'verifie_IPS'")
        # si ce qui est rentré n'est pas un entier
        if not self.ui.lineEdit_IPS.text().isdigit() and len(self.ui.lineEdit_IPS.text()) > 0:
            retour = QMessageBox.warning(
                self,
                _translate(
                    u"pymecavideo", "Le nombre d'images par seconde doit être un entier", None),
                _translate(u"pymecavideo", "merci de recommencer", None),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        else:
            self.calcul_deltaT(ips_from_line_edit=True)

    def calcul_deltaT(self, ips_from_line_edit=False, rouvre=False):
        self.dbg.p(1, "rentre dans 'calcul_deltaT'")
        if rouvre:  # se produit quand on lit un deltaT depuis un fichier mecavideo
            IPS = round(1/self.deltaT)
            self.ui.lineEdit_IPS.setText(str(IPS))
        else:
            if not ips_from_line_edit:
                framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos()
                self.dbg.p(3,
                           "In :  'calcul_deltaT', framerate, self.image_max = %s, %s" % (framerate, self.image_max))
                self.deltaT = float(1.0 / framerate)
                if math.isnan(self.deltaT):
                    print(
                        "ERREUR à la lecture de la vidéo, vitesse des trames indéfinie, on suppose 40 trames par seconde")
                    self.deltaT = 1.0/40
                # mets à jour le label contenant les IPS
                IPS = round(1/self.deltaT)
                self.ui.lineEdit_IPS.setText(str(IPS))
                print("la vidéo a été détectée à %s Images Par Seconde" % IPS)
            else:
                IPS = int(self.ui.lineEdit_IPS.text())
                self.deltaT = float(1.0 / IPS)
                self.dbg.p(3,
                           "In :  'calcul_deltaT', self.deltaT a été recalculé d'après une rentrée manuelle = %s" % (self.deltaT))

    def defini_barre_avancement(self):
        """récupère le maximum d'images de la vidéo et défini la spinbox et le slider"""
        self.dbg.p(1, "rentre dans 'defini_barre_avancement'")
        framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos()
        self.dbg.p(3,
                   "In :  'defini_barre_avancement', framerate, self.image_max = %s, %s" % (framerate, self.image_max))
        self.ui.horizontalSlider.setMinimum(1)
        self.ui.horizontalSlider.setMaximum(int(self.image_max))
        self.ui.spinBox_image.setMaximum(int(self.image_max))
        self.extract_image(1)

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
            self.mets_a_jour_label_infos(
                _translate("pymecavideo", "Pymecavideo n'arrive pas à lire l'image", None))
            return False, None
        self.a_une_image = ok
        return ok, image_opencv

    def traiteOptions(self):
        self.dbg.p(1, "rentre dans 'traiteOptions'")
        for opt, val in self.opts:
            if opt in ['-f', '--fichier_mecavideo']:
                if os.path.isfile(val) and (os.path.splitext(val)[1] == ".csv" or  os.path.splitext(val)[1] == ".mecavideo"):
                    try:
                        self.rouvre(val)
                    except AttributeError:
                        self.dbg.p(
                            1, "Issue in rouvre for this file : attributeerror")
                if os.path.isfile(val) and os.path.splitext(val)[1] == ".avi":
                    self.openTheFile(val)


def usage():
    print(
        "Usage : pymecavideo [-f fichier | --fichier_pymecavideo=fichier] [--maxi] [-d | --debug=verbosityLevel(1-3)] [nom_de_fichier_video.avi]")


def run():
    global app
    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            args, "f:d:", ["fichier_mecavideo=", "debug="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    ###translation##
    locale = "%s" % QLocale.system().name()
    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale):
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    langdir = os.path.join(StartQt5._dir("langues"),
                           r"pymecavideo_" + locale)
    if appTranslator.load(langdir):
        b = app.installTranslator(appTranslator)
    windows = StartQt5(None, opts, args)
    windows.show()
    sys.exit(app.exec_())


class plotThread(threading.Thread):
    """
    une classe pour lancer un traceur de courbe
    """

    def __init__(self, cmd, dataLines):
        """
        Le constructeur
        @param cmd la commande à lancer dans un shell
        @param dataLines une chaîne de plusieurs lignes (format x y)
        """
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.xy = dataLines
        return

    def run(self):
        p = subprocess.Popen(str(self.cmd), shell=True, stdin=subprocess.PIPE)
        p.communicate(self.xy.encode("utf-8"))
        return


if __name__ == "__main__":
    run()
