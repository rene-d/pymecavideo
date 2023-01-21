# -*- coding: utf-8 -*-

import sys,os, locale
thisDir = os.path.dirname(__file__)
sys.path.insert(0, thisDir)

import subprocess

from globdef import HOME_PATH, VIDEO_PATH, CONF_PATH, \
    ICON_PATH, LANG_PATH, \
    DATA_PATH, HELP_PATH, DOCUMENT_PATH, \
    _translate
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QVBoxLayout, QTableWidgetSelectionRange, QDialog, QAction, QPushButton
import getopt
import traceback
import time
from aspectlayout import AspectLayout
import functools
import numpy as np
import math
import tempfile
import platform
import threading
from export import Export, EXPORT_FORMATS
import re
import magic
from toQimage import toQImage
from dialogencode import QMessageBoxEncode
from version import Version
from listes import listePointee
from dbg import Dbg
from preferences import Preferences
from cadreur import Cadreur, openCvReader
from choix_origine import ChoixOrigineWidget
from trajectoire_widget import TrajectoireWidget
from grandeurs import grandeurs

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

    Copyright (C) 2007-2023 Georges Khaznadar <georgesk@debian.org>

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

    Copyright (C) 2007-2023 Georges Khaznadar <georgesk@debian.org>

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

from inspect import currentframe

def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno

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


from Ui_pymecavideo_mini_layout import Ui_pymecavideo

class FenetrePrincipale(QMainWindow, Ui_pymecavideo):
    def __init__(self, parent=None, opts=[], args=[]):
        """
        le constructeur reçoit les données principales du logiciel :
        @param parent le widget parent, None pour une fenêtre principale
        @param opts les options de l'invocation bien rangées en tableau
        @param args les arguments restants après raitement des options
        """
        # QT
        QMainWindow.__init__(self, parent)
        Ui_pymecavideo.__init__(self)
        QWidget.__init__(self, parent)
        self.min_version = "7.3.0-1" # version minimale du fichier de conf.
        self.hauteur = 1
        self.largeur = 0
        self.ratio = 4/3
        self.decalh = 0
        self.decalw = 0
        # points utilisés pour la détection automatique, définissent une zone où il est probable de trouver un objet suivi
        self.pointsProbables = [None]
        self.methode_thread = 3  # définit la methode de calcul à utiliser pour la détection auto. 1 : 1 thread de calcul  2 : découpage en plusieurs thread 3: 1 thread<-> 1 calcul
        self.dictionnairePlotWidget = {}

        # Mode plein écran
        self.plein_ecran = False
        QShortcut(QKeySequence(Qt.Key_F11), self, self.basculer_plein_ecran)

        self.height_screen, self.width_screen = QDesktopWidget(
        ).screenGeometry().height(), QDesktopWidget().screenGeometry().width()


        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowSystemMenuHint |
                            Qt.WindowMinMaxButtonsHint)

        self.setupUi(self)

        # définition des widgets importants
        self.zoom_zone.setApp(self)
        self.trajectoire_widget.setApp(self)

        # gestion des layout pour redimensionnement
        self.aspectlayout1 = AspectLayout(self.ratio)

        self.aspectlayout2 = AspectLayout(self.ratio)

        self.dbg = Dbg(0)
        for o in opts:
            if ('-d' in o[0]) or ('--debug' in o[0]):
                self.dbg = Dbg(o[1])
                self.dbg.p(1, "Niveau de débogage" + o[1])

        self.args = args

        self.cvReader = None
        self.graphWidget = None

        self.platform = platform.system()

        # initialise les répertoires
        self._dir()

        # lecture du fichier de préférences
        self.apply_preferences()

        # variables à initialiser
        # disable UI at beginning
        self.tabWidget.setEnabled(0)
        self.actionDefaire.setEnabled(0)
        self.actionRefaire.setEnabled(0)
        self.actionCopier_dans_le_presse_papier.setEnabled(0)
        self.menuE_xporter_vers.setEnabled(0)
        self.actionSaveData.setEnabled(0)
        self.actionExemples.setEnabled(0)
        self.widget_chronophoto.setEnabled(False)

        # exportCombo
        self.exportCombo.addItem('Exporter vers...')
        # Ajoute les différents formats d'exportation
        for key in sorted(EXPORT_FORMATS.keys()):
            self.exportCombo.addItem(EXPORT_FORMATS[key]['nom'])

        #exportQactions
        for key in sorted(EXPORT_FORMATS.keys()):
            action = QAction(EXPORT_FORMATS[key]
                             ['nom'], self.menuE_xporter_vers)
            action.triggered.connect(
                lambda checked, index=key: self.export(index))
            self.menuE_xporter_vers.addAction(action)

        self.init_variables(opts, self.prefs.defaults['lastVideo'])
        self.init_interface()
        # connections internes
        self.ui_connections()

        self.traite_arg()
        return

    def traite_arg(self):
        """
        traite les arguments donnés à l'application. Trouve le type de fichier
        et selon le cas, ouvre ou "rouvre" son contenu
        """
        if len(self.args) > 0:
            filename = self.args[0]
            mime = magic.Magic(mime=True)
            mt = mime.from_file(filename)
            OK = False
            if mt.startswith("video/"):
                OK = True
                self.video.openTheFile(filename)
            elif mt == "text/plain":
                signature = open(filename).read(24)
                if signature.startswith("# version = pymecavideo"):
                    OK = True
                    self.video.rouvre(filename)
            if not OK:
                QMessageBox.information(
                    self,
                    _translate("pymecavideo", "Argument non pris en compte", None),
                    _translate("pymecavideo", "Le fichier {filename} n'est ni un fichier vidéo, ni un fichier de sauvegarde de pymecavideo.", None).format(filename=filename))
                
        return

    def apply_preferences(self, rouvre = False):
        """
        Récupère les préférences sauvegardées, et en applique les données
        ici on s'occupe de ce qui se gère facilement au niveau de la
        fenêtre principale
        @param rouvre est vrai quand on ouvre un fichier pymecavideo ; 
          il est faux par défaut
        """
        # on relit les préférences du fichier de configuration, sauf en cas
        # de réouverture d'un fichier pymecavideo, qui contient les préférences
        if not rouvre:
            self.prefs = Preferences(self)
            
        m = re.match(r"pymecavideo (.*)",
                     self.prefs.config["DEFAULT"]["version"])
        if m:
            version = m.group(1)
        else:
            version = "0"
        if version < self.min_version:
            QMessageBox.information(
                self,
                _translate("pymecavideo", "Configuration trop ancienne", None),
                _translate("pymecavideo", "La version du fichier de configuration, {version} est inférieure à {min_version} : le fichier de configuration ne peut pas être pris en compte", None).format(version = version, min_version = self.min_version))
            return
        # le fichier de configuration a la bonne version, on applique ses
        # données
        d = self.prefs.config["DEFAULT"]
        self.dbg = Dbg(d.getint("niveaudbg"))
        taille = self.prefs.config.getvecteur("DEFAULT", "taille")
        rect = self.geometry()
        self.setGeometry(rect.x(), rect.y(), int(taille.x), int(taille.y))
        self.radioButtonNearMouse.setChecked(d["proximite"] == "True")
        # on passe la main au videowidget pour appliquer le reste
        # des données du fichier de préférences
        self.video.setApp(self)
        self.video.apply_preferences(rouvre = rouvre)
        return

    def hasHeightForWidth(self):
        # This tells the layout manager that the banner's height does depend on its width
        return True

    def sizeHint(self):
        return QSize(1024, 768)

    def showFullScreen_(self):
        """gère les dimensions en fonction de la largeur et la hauteur de l'écran"""
        self.setFixedSize(QSize(self.width_screen,self.height_screen ))
        return

    def basculer_plein_ecran(self):
        """Basculer en mode plein écran / mode fenétré"""
        self.dbg.p(1, "rentre dans 'basculer_plein_ecran'")
        if not self.plein_ecran:
            self.showFullScreen()
        else:
            self.showNormal()
        self.plein_ecran = not (self.plein_ecran)

    def init_variables(self, opts, filename=""):
        self.dbg.p(1, "rentre dans 'init_variables'")
        self.logiciel_acquisition = False
        self.index_max = 1
        self.repere = 0
        self.masse_objet = 0
        self.premier_chargement_fichier_mecavideo = False #gere l'origine au premier chargement
        # contient les listes des abscisses, vitesses, énergies calculées par le grapheur.
        self.locals = {} # dictionnaire de variables locales, pour eval
        self.rouvert = False  # positionné a vrai si on vien d'ouvrir un fichier mecavideo
        self.motif = []
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
        self.premierResize = True  # arrive quand on ouvre la première fois la fenetre
        self.premiere_image_pointee = 1  # n° de la première image cliquée
        self.video.index = 1  # image à afficher
        self.chronoImg = 0
        self.filename = filename
        self.opts = opts
        self.stdout_file = os.path.join(CONF_PATH, "stdout")
        self.exitDecode = False
        self.resizing = False
        self.stopRedimensionne = False
        self.refait_point = False
        self.graphe_deja_choisi = None
        self.defixeLesDimensions()
        return

    def init_interface(self, refait=0):
        self.dbg.p(1, "rentre dans 'init_interface'")

        # activation des boutons de rotation (ou pas)
        self.pushButton_rot_droite.setEnabled(self.video.a_une_image)
        self.pushButton_rot_gauche.setEnabled(self.video.a_une_image)
        
        # activation des onglets (ou pas), l'onglet 0 passe devant
        self.tabWidget.setEnabled(1)
        self.tabWidget.setCurrentIndex(0)  # montre l'onglet video
        self.tabWidget.setTabEnabled(0, self.video.a_une_image)
        grain_a_moudre = bool(self.video)
        for tab in (1, 2, 3):
            self.tabWidget.setTabEnabled(tab, grain_a_moudre)
        self.actionExemples.setEnabled(1)

        # activation de certaines actions (ou pas)
        self.actionSaveData.setEnabled(grain_a_moudre)
        self.actionCopier_dans_le_presse_papier.setEnabled(grain_a_moudre)
        self.spinBox_image.setEnabled(grain_a_moudre)
        
        # initialisation de self.trajectoire_widget
        self.trajectoire_widget.chrono = False

        self.video.active_controle_image(False)
        self.echelleEdit.setEnabled(False)

        # marque "indéf." dans l'afficheur d'échelle à gauche
        self.video.affiche_echelle()

        # met à jour du bouton pour définir l'échelle
        self.Bouton_Echelle.setEnabled(True)
        self.Bouton_Echelle.setStyleSheet("background-color:None;")

        self.video.Bouton_lance_capture.setEnabled(True)
        
        if not refait:
            self.horizontalSlider.setValue(1)

        # active l'affichage du nombre d'objets suivis
        self.video.affiche_nb_points(True)

        # cache les boutons radio pour les vecteurs vitesse sur la trajectoire
        self.radioButtonNearMouse.hide()
        self.radioButtonSpeedEveryWhere.hide()

        # désactive et cache le bouton pour l'arrêt du pointage automatique
        self.pushButton_stopCalculs.setEnabled(False)
        self.pushButton_stopCalculs.hide()

        # désactivations diverses
        self.button_video.setEnabled(False)
        self.checkBox_Ec.setChecked(False)
        self.checkBox_Em.setChecked(False)
        self.checkBox_Epp.setChecked(False)

        # inactive le spinner pour les incréments de plus d'une image
        # voir la demande de Isabelle.Vigneau@ac-versailles.fr, 15 Sep 2022
        # non encore implémentée
        self.imgno_incr.hide()
        self.spinBox.hide()
        return
    

    ############ les signaux spéciaux #####################
    change_axe_origine = pyqtSignal()
    selection_done = pyqtSignal()
    stopRedimensionnement = pyqtSignal()
    OKRedimensionnement = pyqtSignal()
    redimensionneSignal = pyqtSignal(bool)
    updateProgressBar = pyqtSignal()
    pythonsourceOK = pyqtSignal(list)
    #chrono_changed = pyqtSignal()

    def ui_connections(self):
        """connecte les signaux de Qt"""
        self.dbg.p(1, "rentre dans 'ui_connections'")
        self.actionOuvrir_un_fichier.triggered.connect(self.openfile)
        self.actionExemples.triggered.connect(self.openexample)
        self.action_propos.triggered.connect(self.propos)
        self.actionAide.triggered.connect(self.aide)
        self.actionDefaire.triggered.connect(self.efface_point_precedent)
        self.actionRefaire.triggered.connect(self.refait_point_suivant)
        self.actionQuitter.triggered.connect(self.close)
        self.actionSaveData.triggered.connect(self.video.enregistre_ui)
        self.actionCopier_dans_le_presse_papier.triggered.connect(
            self.presse_papier)
        self.actionRouvrirMecavideo.triggered.connect(self.rouvre_ui)
        self.Bouton_Echelle.clicked.connect(self.video.demande_echelle)
        self.video.active_controle_image()
        self.Bouton_lance_capture.clicked.connect(self.video.debut_capture)
        self.comboBox_referentiel.currentIndexChanged.connect(
            self.tracer_trajectoires)
        #self.comboBox_mode_tracer.currentIndexChanged.connect(
            #self.tracer_courbe)
        self.tabWidget.currentChanged.connect(self.choix_onglets)
        self.checkBoxScale.currentIndexChanged.connect(self.enableSpeed)
        self.checkBoxScale.currentTextChanged.connect(self.enableSpeed)
        self.checkBoxVectorSpeed.stateChanged.connect(self.enableSpeed)
        self.radioButtonSpeedEveryWhere.clicked.connect(self.enableSpeed)
        self.radioButtonNearMouse.clicked.connect(self.enableSpeed)
        self.button_video.clicked.connect(self.montre_video)
        self.pushButton_select_all_table.clicked.connect(self.presse_papier)
        self.comboBoxChrono.currentIndexChanged.connect(self.chronoPhoto)
        self.pushButton_reinit.clicked.connect(self.video.reinitialise_capture)
        self.pushButton_defait.clicked.connect(self.efface_point_precedent)
        self.pushButton_refait.clicked.connect(self.refait_point_suivant)
        self.pushButton_origine.clicked.connect(
            self.choisi_nouvelle_origine)
        self.checkBox_abscisses.stateChanged.connect(self.change_sens_X)
        self.checkBox_ordonnees.stateChanged.connect(self.change_sens_Y)
        self.pushButton_rot_droite.clicked.connect(self.tourne_droite)
        self.pushButton_rot_gauche.clicked.connect(self.tourne_gauche)
        self.change_axe_origine.connect(self.video.egalise_origine)
        self.selection_done.connect(self.video.picture_detect)
        self.stopRedimensionnement.connect(self.fixeLesDimensions)
        self.OKRedimensionnement.connect(self.defixeLesDimensions)
        self.redimensionneSignal.connect(self.redimensionneFenetre)
        self.pushButton_stopCalculs.clicked.connect(self.video.stopCalculs)
        self.updateProgressBar.connect(self.updatePB)
        self.exportCombo.currentIndexChanged.connect(self.export)
        self.pushButton_nvl_echelle.clicked.connect(self.recommence_echelle)
        self.checkBox_Ec.stateChanged.connect(self.affiche_tableau)
        self.checkBox_Epp.stateChanged.connect(self.affiche_tableau)
        self.checkBox_Em.stateChanged.connect(self.affiche_tableau)
        self.comboBox_X.currentIndexChanged.connect(self.dessine_graphe_avant)
        self.comboBox_Y.currentIndexChanged.connect(self.dessine_graphe_avant)
        self.lineEdit_m.textChanged.connect(self.verifie_m_grapheur)
        self.lineEdit_g.textChanged.connect(self.verifie_g_grapheur)
        self.lineEdit_IPS.textChanged.connect(self.verifie_IPS)
        self.comboBox_style.currentIndexChanged.connect(self.dessine_graphe)
        self.pushButton_save.clicked.connect(self.enregistreChrono)
        self.spinBox_chrono.valueChanged.connect(self.changeChronoImg)
        self.pushButton_save_plot.clicked.connect(self.enregistre_graphe)

    def changeChronoImg(self,img):
        self.chronoImg = img
        self.chronoPhoto()

    def enregistreChrono(self):
        self.pixmapChrono = QPixmap(self.trajectoire_widget.size())
        self.trajectoire_widget.render(self.pixmapChrono)
        base_name = os.path.splitext(os.path.basename(self.filename))[0]
        defaultName = os.path.join(DOCUMENT_PATH[0], base_name)
        fichier = QFileDialog.getSaveFileName(self,
                                              _translate(
                                                  "pymecavideo", "Enregistrer comme image", None),
                                              defaultName, _translate("pymecavideo", "fichiers images(*.png *.jpg)", None))
        try :
            self.pixmapChrono.save(fichier[0])
        except Exception as err:
            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
            QMessageBox.critical(None, _translate("pymecavideo", "Erreur lors de l'enregistrement", None), _translate("pymecavideo", "Echec de l'enregistrement du fichier:<b>\n{0}</b>", None).format(
                    fichier[0]), QMessageBox.Ok, QMessageBox.Ok)

    def chronoPhoto(self):
        """lance la sauvegarde du trajectoire_widget.
        Si chronophotographie, on ajoute l'image et la trace de l'échelle comme pointée.
        Si chronophotogramme, on ne met pas l'image et la trace est en haut.
        """
        # Configure l'UI en fonction du mode
        if self.comboBoxChrono.currentIndex() == 0 :
            self.widget_chronophoto.setEnabled(False)
            self.trajectoire_widget.setEnabled(True)
            self.widget_speed.setEnabled(True)
        elif self.comboBoxChrono.currentIndex() == 1 :
            self.widget_chronophoto.setEnabled(True)
            self.trajectoire_widget.setEnabled(False)
            self.widget_speed.setEnabled(False)
            self.checkBoxVectorSpeed.setChecked(False)
            self.spinBox_chrono.setMaximum(int(self.video.image_max))
            self.spinBox_chrono.setMinimum(1)

        elif self.comboBoxChrono.currentIndex() == 2 :
            self.widget_chronophoto.setEnabled(False)
            self.trajectoire_widget.setEnabled(False)
            self.widget_speed.setEnabled(False)
            self.checkBoxVectorSpeed.setChecked(False)
        self.dbg.p(1, "rentre dans 'chronoPhoto'")
        # ajoute la première image utilisée pour le pointage sur le fond du vidget
        liste_types_photos = ['chronophotographie', 'chronophotogramme']

        if self.comboBoxChrono.currentIndex() != 0:
            photo_chrono = liste_types_photos[self.comboBoxChrono.currentIndex(
            )-1]
            self.dbg.p(2, "dans 'chronoPhoto, on a choisi le type %s'" %
                       (photo_chrono))
            if photo_chrono == 'chronophotographie':  # on extrait le première image que l'on rajoute au widget
                self.trajectoire_widget.chrono = 1  # 1 pour chronophotographie
                ok, img = self.video.cvReader.getImage(
                    self.chronoImg, self.video.rotation)
                self.imageChrono = toQImage(img).scaled(
                    self.video.width(), self.video.height(), Qt.KeepAspectRatio)
                self.trajectoire_widget.setImage(
                    QPixmap.fromImage(self.imageChrono))
            else:
                self.trajectoire_widget.chrono = 2  # 2 pour chronophotogramme
                self.trajectoire_widget.setImage(QPixmap())
            #self.enregistreChrono()
        else:
            self.trajectoire_widget.setImage(QPixmap())
            self.trajectoire_widget.chrono = 0
        self.redimensionneFenetre()
        self.update()

    def fixeLesDimensions(self):
        self.setMinimumWidth(self.width())
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.setFixedSize(QSize(self.width(), self.height()))

    def defixeLesDimensions(self):
        """
        donne une taille minimale à la fenêtre, 640 x 480 ; 
        il s'y ajoute bien sûr les contraintes des widgets définis
        par l'interface utilisateur qui est créée à l'aide de designer.
        """
        self.setMinimumWidth(640)
        self.setMaximumWidth(16000000)
        self.setMinimumHeight(480)
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
        if self.checkBoxVectorSpeed.isChecked():
            self.dbg.p(2, "In enableSpeed")
            self.checkBoxScale.setEnabled(1)
            if self.checkBoxScale.count() < 1:
                self.checkBoxScale.insertItem(0, "1")
            self.radioButtonNearMouse.show()
            self.radioButtonSpeedEveryWhere.show()
            self.trajectoire_widget.prepare_vecteurs_pour_paint()
            self.trajectoire_widget.update()
        else:
            self.checkBoxScale.setEnabled(0)
            self.radioButtonNearMouse.hide()
            self.radioButtonSpeedEveryWhere.hide()
            self.trajectoire_widget.update()

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
                    stdout = stdout_filepointsProbables.readlines()  # à globaliser pour windows
                    if not self.exitDecode:
                        try:
                            pct = stdout[-1].split()[3].replace('%',
                                                                '').replace(')', '').replace('(', '')
                            assert (pct.isalnum())
                            exit = True
                        except IndexError as err:
                            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
                            exit = False
        except Exception as err:
            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
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
        ChoixOrigineWidget(parent=self.video, app=self).show()

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
        self.dbg.p(3, "Dans 'tourne_image' avant de tourner, self.origine %s, largeur video%s, hauteur video%s" % (
            self.video.origine, self.video.width(), self.video.height()))
        try:
            self.dbg.p(3, "Dans 'tourne_image' avant de tourner, self.echelle_image.p1 %s, self.echelle_image.p2 %s" % (
                self.video.echelle_image.p1, self.video.echelle_image.p2))
        except AttributeError as err:
            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
            pass
        self.redimensionneSignal.emit(1)

    def change_sens_X(self):
        self.dbg.p(1, "rentre dans 'change_sens_X'")
        if self.checkBox_abscisses.isChecked():
            self.sens_X = -1
        else:
            self.sens_X = 1
        self.change_axe_origine.emit()

    def change_sens_Y(self):
        self.dbg.p(1, "rentre dans 'change_sens_Y'")
        if self.checkBox_ordonnees.isChecked():
            self.sens_Y = -1
        else:
            self.sens_Y = 1
        self.change_axe_origine.emit()

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
                                            self.tableWidget.rowCount() - 1,
                                            self.tableWidget.columnCount() - 1)
        self.tableWidget.setRangeSelected(trange, True)
        self.tableWidget.selection()

    def export(self, choix_export=None):
        self.dbg.p(1, "rentre dans 'export'")
        """
        Traite le signal venu de exportCombo, puis remet l\'index de ce
        combo à zéro.
        """
        # Si appel depuis les QActions, choix_export contient la clé du dico
        if not choix_export:
            # Si appel depuis le comboBox, on cherche l'index
            choix_export = self.exportCombo.currentIndex()
        if choix_export > 0:
            # Les choix d'export du comboBox commencent à l'index 1. Le dico EXPORT_FORMATS commence à 1 et pas à zéro
            self.exportCombo.setCurrentIndex(0)
            self.affiche_tableau()
            Export(self, choix_export)
        return

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
            dd = FenetrePrincipale._dir("conf")
            if not os.path.exists(dd) and \
               os.access(os.path.dirname(dd), os.W_OK):
                os.makedirs(dd)
    _dir = staticmethod(_dir)

    def rouvre_ui(self):
        self.dbg.p(1, "rentre dans 'rouvre_ui'")

        dir_ = DOCUMENT_PATH[0]
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            _translate("pymecavideo", "Ouvrir un projet Pymecavideo", None),
            dir_,
            _translate("pymecavideo", "Projet Pymecavideo (*.mecavideo)", None))
        if fichier != "":
            self.video.rouvre(fichier)
        return

    def redimensionneFenetre(self, tourne=False, old=None):
        self.dbg.p(1, "rentre dans 'redimensionneFenetre'")

        self.tourne = tourne  # n'est utilisée que ici et dans video
        if tourne:  # on vient de cliquer sur tourner. rien n'est changé.
            self.dbg.p(1, "Dans 'redimensionneFenetre', tourne")
            largeur = self.video.width()
            hauteur = self.video.height()
            self.video.origine = self.video.origine.rotate(
                self.increment, largeur, hauteur)
            self.video.echelle_image.p1 = self.video.echelle_image.p1.rotate(
                self.increment, largeur, hauteur)
            self.video.echelle_image.p2 = self.video.echelle_image.p2.rotate(
                self.increment, largeur, hauteur)
            self.video.setGeometry(0, 0, hauteur, largeur)
            self.ratio = 1/self.ratio
            self.aspectlayout1.aspect = self.ratio
            self.aspectlayout2.aspect = self.ratio
            self.tourne = False
            # HACK : oblige le redimensionnement
            self.resize(self.size()+QSize(1, 0))
            self.resize(self.size()+QSize(-1, 0))

        if self.video.lance_capture:
            self.dbg.p(2, "on fixe les hauteurs du widget")
            self.video.setFixedHeight(
                self.video.height())
            self.video.setFixedWidth(
                self.video.width())
            self.dbg.p(2, "on fixe les hauteurs de la fenetre")

        self.dbg.p(2, "on fixe les hauteurs de video")
        self.dbg.p(2, "widget_vidéo situé en %s %s" %
                   (self.video.pos().x, self.video.pos().y))
        self.dbg.p(3, "widget_vidéo largeur :  %s hauteur : %s" %
                   (self.video.width(), self.video.height()))
        self.dbg.p(2, "MAJ de video")
        self.video.maj()
        self.trajectoire_widget.maj()
        self.video.affiche_image()

        self.dbg.p(2, "On fixe les tailles de centralwidget et tabWidget")
        return

    def widthForHeight_video(self, h):
        # calcule self.largeur et self.hauteur si la hauteur est prédominante
        # si la hauteur est trop petite, ne permet plus de redimensionnement
        self.dbg.p(1, "retre dans 'widthForHeight'")
        self.dbg.p(2, "argument h : %s" % (str(h)))
        return round(h*self.ratio)

    def heightForWidth_video(self, w):
        # calcul self.largeur et self.hauteur
        # si la largeur est trop petite, ne permet plus de redimensionnement
        self.dbg.p(1, "retre dans 'heightForWidth'")
        self.dbg.p(2, "argument w : %s" % (str(w)))
        return round(w/self.ratio)

    def enterEvent(self, e):
        self.gardeLargeur()

    def leaveEvent(self, e):
        self.gardeLargeur()

    def gardeLargeur(self):
        self.largeurAvant = self.largeur

    def resizeEvent(self, event):
        self.dbg.p(1, "rentre dans 'resizeEvent'")
        self.redimensionneFenetre(tourne=False, old=event.oldSize())
        return super(FenetrePrincipale, self).resizeEvent(event)

    def showEvent(self, event):
        self.dbg.p(1, "rentre dans 'showEvent'")
        self.redimensionneSignal.emit(0)

    def cree_tableau(self, nb_suivis=1):
        """
        Crée un tableau de coordonnées neuf dans l'onglet idoine.
        @param nb_suivis le nombre d'objets suivis (1 par défaut)
        """
        self.dbg.p(1, "rentre dans 'cree_tableau'")
        self.tableWidget.clear()
        self.tab_coord.setEnabled(1)
        self.tableWidget.setRowCount(1)
        #le compte de colonnes supplémentaires pour chaque objet
        colonnes_sup = self.checkBox_Ec.isChecked() + \
            self.checkBox_Epp.isChecked() + \
            self.checkBox_Em.isChecked()

        # 2 colonnes par objet, colonnes_sup colonnes par objet
        # une pour la date, une pour refaire le pointage
        self.tableWidget.setColumnCount(nb_suivis * (2 + colonnes_sup) + 2)

        self.tableWidget.setDragEnabled(True)
        # on met des titres aux colonnes.
        self.tableWidget.setHorizontalHeaderItem(
            0, QTableWidgetItem('t (s)'))
        self.tableWidget.setRowCount(len(self.video.data))
        for i in range(nb_suivis):
            unite = "m" if self.video.echelle_image \
                else "px"
            self.tableWidget.setHorizontalHeaderItem(
                1 + (2+colonnes_sup) * i, QTableWidgetItem(
                    f"X{i + 1} ({unite})"))
            self.tableWidget.setHorizontalHeaderItem(
                2 + (2+colonnes_sup) * i, QTableWidgetItem(
                f"Y{i + 1} ({unite})"))
            for j in range(colonnes_sup):
                cptr = 0
                if self.checkBox_Ec.isChecked():
                    self.tableWidget.setHorizontalHeaderItem(
                        3+cptr + (2+colonnes_sup)*i, QTableWidgetItem(f"Ec{1 + i} (J)"))
                    cptr += 1
                if self.checkBox_Epp.isChecked():
                    self.tableWidget.setHorizontalHeaderItem(
                        3+cptr + (2+colonnes_sup)*i, QTableWidgetItem(f"Epp{1 + i} (J)"))
                    cptr += 1
                if self.checkBox_Em.isChecked():
                    self.tableWidget.setHorizontalHeaderItem(
                        3+cptr + (2+colonnes_sup)*i, QTableWidgetItem(f"Em{1 + i} (J)"))
                    cptr += 1
        #dernier pour le bouton
        self.tableWidget.setHorizontalHeaderItem(
            nb_suivis * 2 + 1 + colonnes_sup*nb_suivis,
            QTableWidgetItem("Refaire le point"))
        return

    def recalculLesCoordonnees(self):
        """
        permet de remplir le tableau des coordonnées à la demande. 
        Se produit quand on ouvre un fichier pymecavideo ou quand on 
        redéfinit l'échelle
        """
        self.dbg.p(1, "rentre dans 'recalculLesCoordonnees'")
        nb_suivis = self.video.nb_obj

        def cb_temps(i, t):
            # marque la date dans la colonne de gauche
            self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{t:.3f}"))
            return

        def cb_point(i, t, j, obj, p, v):
            # marque les coordonnées x et y de chaque objet, deux colonnes
            # par deux colonnes.
            if p:
                self.tableWidget.setItem(
                    i, j*(nb_suivis)+1, QTableWidgetItem(str(p.x)))
                self.tableWidget.setItem(
                    i, j*(nb_suivis) + 2, QTableWidgetItem(str(p.y)))
            return

        # dans le tableau, l'unité est le mètre.
        self.video.iteration_data(cb_temps, cb_point, unite = "m")
        return

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
                except Exception as err:
                    self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
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
        self.tableWidget.removeRow(
            int((len(self.listePoints)-1)/self.nb_de_points))
        self.listePoints.decPtr()
        self.dbg.p(2, "self.listePoints" + str(self.listePoints) +
                   "self.points" + str(self.points))
        if len(self.listePoints) % self.nb_de_points != 0:
            try:
                self.points[len(self.listePoints)/self.nb_de_points].pop()
            except KeyError as err:
                self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
                # liée au passage de ptyhon2 à python3 et au changement de comportement de /
                self.dbg.p(1, "Erreur de clé : " +
                           str(len(self.listePoints)/self.nb_de_points))
        else:
            try:
                del self.points[len(self.listePoints)/self.nb_de_points]
            except KeyError as err:
                self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
                self.dbg.p(1, "Erreur de clé : " +
                           str(len(self.listePoints)/self.nb_de_points))
        # dernière image à afficher
        if self.nb_de_points != 1:
            if len(self.listePoints)-1 >= 0:
                if len(self.listePoints) % self.nb_de_points == self.nb_de_points-1:
                    self.video.index = self.listePoints[len(
                        self.listePoints)-1][0]
        else:
            if len(self.listePoints)-1 >= 0:
                if len(self.listePoints) % self.nb_de_points == self.nb_de_points-1:
                    self.video.index = self.listePoints[len(
                        self.listePoints)-1][0]+1
        self.affiche_image()
        self.clic_sur_video_ajuste_ui(self.video.index)

    def refait_point_suivant(self):
        """rétablit le point suivant après un effacement
        """
        self.dbg.p(1, "rentre dans 'refait_point_suivant'")
        self.listePoints.incPtr()
        # on stocke si la ligne est complète
        if len(self.listePoints) % self.nb_de_points == 0:
            self.stock_coordonnees_image(
                ligne=int((len(self.listePoints)-1)/self.nb_de_points))
            self.video.index = self.listePoints[len(
                self.listePoints)-1][0]+1
        self.affiche_image()
        self.clic_sur_video_ajuste_ui(self.video.index)

    def montre_video(self):
        self.dbg.p(1, "rentre dans 'montre_video'")
        ref = self.comboBox_referentiel.currentText().split(" ")[-1]
        if len(ref) == 0 or ref == "camera":
            return
        c = Cadreur(int(ref), self.video)
        c.montrefilm()
        return

    def choix_onglets(self, newValue):
        """
        traite les signaux émis par le changement d'onglet, ou
        par le changement de référentiel dans l'onglet des trajectoires."""
        self.dbg.p(1, "rentre dans 'choix_onglets'")
        if self.tabWidget.currentIndex() == 1:
            self.statusBar().clearMessage() # ClearMessage plutôt que hide, ne décale pas les widgets
            self.tracer_trajectoires("absolu")
        elif self.tabWidget.currentIndex() == 2:
            self.statusBar().clearMessage() # ClearMessage plutôt que hide, ne décale pas les widgets
            self.affiche_tableau()
        elif self.tabWidget.currentIndex() == 3:
            self.affiche_grapheur()
            self.MAJ_combox_box_grapheur()
            self.statusBar().clearMessage() # ClearMessage plutôt que hide, ne décale pas les widgets

    def affiche_grapheur(self, MAJ=True):
        self.dbg.p(1, "rentre dans 'affiche_grapheur'")
        deltaT = self.video.deltaT
        m = float(self.lineEdit_m.text().replace(',', '.'))
        g = float(self.lineEdit_g.text().replace(',', '.'))

        # initialisation de self.locals avec des listes vides
        for obj in self.video.suivis:
            for gr in grandeurs:
                self.locals[gr+str(obj)] = []

        # remplissage des self.locals pour les positions,
        # les vitesses, Ec et Epp
        def cb_points(i, t, j, obj, p, v):
            """
            fonction de rappel pour une itération sur les dates
            """
            self.locals["X"+str(obj)].append(p.x if p else None)
            self.locals["Y"+str(obj)].append(p.y if p else None)
            self.locals["Vx"+str(obj)].append(v.x if v else None)
            self.locals["Vy"+str(obj)].append(v.y if v else None)
            self.locals["V"+str(obj)].append(v.norme if v else None)
            self.locals["Ec"+str(obj)].append(
                0.5 * m * v.norme ** 2 if v else None)
            self.locals["Epp"+str(obj)].append(
                self.video.sens_Y * m * g * p.y if p else None)
            return
        self.video.iteration_data(None, cb_points, unite="m")

        # on complète le remplissage de self.locals
        for obj in self.video.suivis:
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
        return
        
    def MAJ_combox_box_grapheur(self):
        if self.graphe_deja_choisi is None : #premier choix de graphe
            self.comboBox_X.clear()
            self.comboBox_Y.clear()
            self.comboBox_X.insertItem(-1,
                                        _translate("pymecavideo", "Choisir ...", None))
            self.comboBox_Y.insertItem(-1,
                                        _translate("pymecavideo", "Choisir ...", None))
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
            X = self.video.dates
        elif grandeurX != "Choisir ...":
            X = self.locals[grandeurX]
        if grandeurY == 't':
            Y = self.video.dates
        elif grandeurY != "Choisir ...":
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

            if not self.graphWidget:  # premier tour
                self.graphWidget = pg.PlotWidget(
                    title=titre, parent=self.widget_graph)
                self.graphWidget.setMenuEnabled(False)
                self.graphWidget.setLabel('bottom', unite_x)
                self.graphWidget.setLabel('left', unite_y)
                self.verticalLayout_onglet4 = QVBoxLayout(self.widget_graph)
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
                self.graphWidget.clear()
                self.graphWidget.plot(X, Y, pen=pen, symbol=symbol)
                self.graphWidget.autoRange()
                self.graphWidget.show()
            self.graphe_deja_choisi = (ordonnee, abscisse)
        return
    
    def enregistre_graphe(self):
        if hasattr (self, 'pg_exporter'):
            base_name = os.path.splitext(os.path.basename(self.filename))[0]
            defaultName = os.path.join(DOCUMENT_PATH[0], base_name+'.png')
            fichier = QFileDialog.getSaveFileName(self,
                                              _translate(
                                                  "pymecavideo", "Enregistrer le graphique", None),
                                              defaultName, _translate("pymecavideo", "fichiers images(*.png)", None))
            self.pg_exporter.export(fichier[0])

    def tracer_trajectoires(self, newValue):
        """
        Cette fonction est appelée par un changement de référentiel.
        On peut aussi appeler cette fonction directement, auquel cas on
        donne la valeur "absolu" à newValue pour reconnaître ce cas.
        efface les trajectoires anciennes, puis
        trace les trajectoires en fonction du référentiel choisi.

        """
        self.dbg.p(1, "rentre dans 'tracer_trajectoires'")
        self.trajectoire_widget.origine_mvt = self.video.origine
        if newValue == "absolu":
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
            self.trajectoire_widget.chrono = False
            bc = self.mediane_trajectoires(int(ref) - 1)
            origine = vecteur(self.video.width() // 2,
                              self.video.height() // 2) - bc
            self.trajectoire_widget.origine = origine
            self.trajectoire_widget.origine_mvt = origine
            self.trajectoire_widget.referentiel = ref
        else:  # si le référentiel est la caméra, aucune translation !
            self.trajectoire_widget.referentiel = 0
            self.trajectoire_widget.origine = vecteur(0, 0)
        self.dbg.p(3, "origine %s, ref %s" %
                   (str(self.trajectoire_widget.origine), str(ref)))
        self.trajectoire_widget.prepare_vecteurs_pour_paint()
        self.trajectoire_widget.update()
        return
    
    def enregistre_dans_listePoints(self, point, index=None):
        """
        enregistre un clic dans self.listePoints à la bonne place.
        on ajoute à cette liste un triplet :
        numéro de l'image, rang du point (0,1 ou 2 s'il y a trois
        points à saisir par image), et le point lui-même.

        Le calcul du rang du point est lié à self.nb_clics, calculé dans clic_sur_video()
        @param point un point à enregistrer
        @param index un numéro d'image. S'il est indéfini (par défaut), il
        est remplacé par self.video.index.
        """
        self.dbg.p(1, "rentre dans 'enregistre_dans_listePoints'")
        if index:
            i = index
        else:
            i = self.video.index
        nieme  = self.nb_clics
        if self.refait_point : #arrive si on refait qu'un seul point à partir du tableau de l'onglet 3.
            self.listePoints[(self.video.index-self.premiere_image_pointee)*self.nb_de_points+nieme] = [i, nieme, point]

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
            index_image = self.video.index-1
        t = "%4f" % ((index_image - self.premiere_image_pointee) * self.deltaT)

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
            x = point.x
            y = point.y
            if x in self.pX.keys():
                self.pX[x].append(point)
            else:
                self.pX[x] = [point]
            if y in self.pY.keys():
                self.pY[y].append(point)
            else:
                self.pY[y] = [point]

        return

    def masse(self, obj):
        """
        Renseigne la masse d'un objet. L'implémentation est actuellement
        incomplète : une seule masse est autorisée, pour tous les objets
        donc on ne tient pas compte du paramètre obj
        @param obj un objet suivi
        @return la masse de cet objet
        """
        if self.masse_objet == 0:
            masse_objet_raw = QInputDialog.getText(
                None,
                _translate(
                    "pymecavideo", "Masse de l'objet", None),
                _translate("pymecavideo",
                           "Quelle est la masse de l'objet ? (en kg)",
                           None),
                QLineEdit.Normal, u"1.0")
            if masse_objet_raw[1] == False:
                return None
            masse_objet = [
                float(masse_objet_raw[0].replace(",", ".")), masse_objet_raw[1]]
            if masse_objet[0] <= 0 or masse_objet[1] == False:
                self.affiche_barre_statut(_translate(
                    "pymecavideo", " Merci d'indiquer une masse valable", None))
            self.masse_objet = float(masse_objet[0])
        m = self.masse_objet
        return m

    def bouton_refaire(self, ligne):
        """
        Crée un bouton servant à refaire un pointage, pour la donnée
        affichée dans une ligne du tableau
        @param ligne une ligne du tableau (indexée à partir de 0)
        @return un bouton
        """
        b = QPushButton()
        b.setIcon(QIcon(":/data/icones/curseur_cible.svg"))
        b.setToolTip("refaire le pointage\n de l'image %s"%(ligne+1))
        b.setFlat(True)
        b.clicked.connect( lambda state, widget: self.refait_point_depuis_tableau( b ))
        return b
    
    def affiche_tableau(self):
        """
        lancée à chaque affichage du tableau, recalcule les coordonnées
        à afficher à partir des listes de points.
        """
        self.dbg.p(1, "rentre dans 'affiche_tableau'")

        # active ou désactive les checkbox énergies
        # (n'ont un intérêt que si l'échelle est déterminée)
        if self.video.echelle:
            self.checkBox_Ec.setEnabled(1)
            self.checkBox_Epp.setEnabled(1)
            if self.checkBox_Ec.isChecked() and self.checkBox_Epp.isChecked():
                self.checkBox_Em.setEnabled(1)
            else:
                # s'il manque Ec ou Epp on décoche Em
                self.checkBox_Em.setChecked(False)
        else:
            self.checkBox_Ec.setEnabled(0)
            self.checkBox_Em.setEnabled(0)
            self.checkBox_Epp.setEnabled(0)

        # masse de l'objet ATTENTION : QUID SI PLUSIEURS OBJETS ?
        if self.checkBox_Ec.isChecked():
            self.masse_objet = self.masse(1)
            self.checkBox_Ec.setChecked(self.masse_objet != 0)
        # initialise tout le tableau (nb de colonnes, unités etc.)
        self.cree_tableau(nb_suivis = self.video.nb_obj)
        # le compte de colonnes supplémentaires pour chaque objet
        colonnes_sup = self.checkBox_Ec.isChecked() + \
            self.checkBox_Epp.isChecked() + \
            self.checkBox_Em.isChecked()
        # le numéro de la dernière colonne où on peut refaire les points
        colonne_refait_points = self.video.nb_obj * (2 + colonnes_sup) + 1

        def cb_temps(i, t):
            # marque la date dans la colonne de gauche
            self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{t:.3f}"))
            return

        def cb_point(i, t, j, obj, p, v):
            # marque les coordonnées x et y de chaque objet, deux colonnes
            # suivies par des colonnes supplémentaires (Ec, Epp, Em), et après
            # avoir épuisé le compte d'objets, un colonne pour permettre de
            # refaire le pointage
            col = 1 + (2 + colonnes_sup) * j
            if p:
                self.tableWidget.setItem(
                    i, col, QTableWidgetItem(f"{p.x:.4g}"))
                col += 1
                self.tableWidget.setItem(
                    i, col, QTableWidgetItem(f"{p.y:.4g}"))
                col+= 1
                if colonnes_sup:
                    m = self.masse(obj)
                # Énergie cinétique si nécessaire
                if self.checkBox_Ec.isChecked():
                    if v is not None:
                        Ec = 0.5 * m * v.norme ** 2
                        self.tableWidget.setItem(
                            i, col, QTableWidgetItem(f"{Ec:.4g}"))
                    col += 1
                # Énergie potentielle de pesanteur si nécessaire
                if self.checkBox_Epp.isChecked():
                    Epp = m * 9.81 * p.y  # TODO faire varier g
                    self.tableWidget.setItem(
                        i, col, QTableWidgetItem(f"{Epp:.4g}"))
                    col += 1
                # Énergie mécanique si nécessaire
                if self.checkBox_Em.isChecked():
                    if v is not None:
                        self.tableWidget.setItem(
                            i, col, QTableWidgetItem(f"{Ec+Epp:.4g}"))
                    col += 1
            # dernière colonne : un bouton pour refaire le pointage
            # existe même en l'absence de pointage
            derniere = self.video.nb_obj * (2 + colonnes_sup) +1
            self.tableWidget.setCellWidget(
                i, derniere, self.bouton_refaire(i))
            return
        
        self.video.iteration_data(
            cb_temps, cb_point,
            unite = "m" if self.video.echelle_image else "px")
        return

    def refait_point_depuis_tableau(self, qpbn ):
        self.dbg.p(1, "rentre dans 'refait_point_depuis_tableau'")
        self.refait_point=True
        numero_image = qpbn.toolTip().split(' ')[-1]
        self.index_de_l_image_actuelle = self.video.index
        self.video.index = int(numero_image)+self.premiere_image_pointee-1

        self.tabWidget.setCurrentIndex(0)
        point_actuel = len(self.listePoints)%self.nb_de_points
        self.clic_sur_video_ajuste_ui(point_actuel)

    def fin_refait_point_depuis_tableau(self):
        self.dbg.p(1, "rentre dans 'fin_refait_point_depuis_tableau'")
        self.refait_point = False

        #####remplacement de la valeur de self.points pour la ligne correspondante
        self.stock_coordonnees_image(self.video.index-self.premiere_image_pointee-1, index_image=True)

        self.video.index = self.index_de_l_image_actuelle
        self.index_de_l_image_actuelle = None
        self.clic_sur_video_ajuste_ui(0)
        self.tabWidget.setCurrentIndex(2)


    def recommence_echelle(self):
        self.dbg.p(1, "rentre dans 'recommence_echelle'")
        self.tabWidget.setCurrentIndex(0)
        self.video.echelle_image = echelle()
        self.affiche_echelle()
        try:
            self.job.dialog.close()
            self.job.close()
        except AttributeError as err:
            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
            pass
        self.demande_echelle()

    def affiche_image_slider(self):
        self.dbg.p(1, "rentre dans 'affiche_image_slider'")
        self.video.index = self.horizontalSlider.value()
        self.affiche_image()

    def affiche_image_slider_move(self):
        """only change spinBox value"""
        self.dbg.p(1, "rentre dans 'affiche_image_slider_move'")
        self.spinBox_image.setValue(self.horizontalSlider.value())
        # self.enableRefaire(0)

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
        d = self.prefs.config["DEFAULT"]
        d["taille"] = f"({self.size().width()},{self.size().height()})"
        self.prefs.save()
        return

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
        m = self.lineEdit_m.text().replace(',', '.')
        if m != "":
            try:
                float(m)
            except Exception as err:
                self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
                retour = QMessageBox.critical(
                    self,
                    _translate(u"pymecavideo", "MAUVAISE VALEUR !", None),
                    _translate(
                        u"pymecavideo", "La valeur rentrée n'est pas compatible avec le calcul", None),
                    QMessageBox.Yes)
        self.affiche_grapheur()
        self.dessine_graphe()

    def verifie_g_grapheur(self):
        g = self.lineEdit_g.text().replace(',', '.')
        if g != "":
            try:
                float(g)
            except Exception as err:
                self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
                retour = QMessageBox.critical(
                    self,
                    _translate(u"pymecavideo", "MAUVAISE VALEUR !", None),
                    _translate(
                        u"pymecavideo", "La valeur rentrée n'est pas compatible avec le calcul", None),
                    QMessageBox.Yes)
        self.affiche_grapheur()
        self.dessine_graphe()

    def affiche_barre_statut(self, message):
        """
        On utilise la barre de status pour afficher les messages :
        permet de gagner de la place en envelant le message de statut
        @param message message à afficher
        """
        self.dbg.p(1, "rentre dans 'affiche_barre_statut'")
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
        self.video.openTheFile(filename)

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
        self.video.openTheFile(filename)
        try:
            self.reinitialise_capture()
        except Exception as err:
            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
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
        self.video.openTheFile(filename)


    def propos(self):
        self.dbg.p(1, "rentre dans 'propos'")
        try:
            loc = locale.getdefaultlocale()[0][0:2]
        except TypeError as err:
            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
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

    def verifie_IPS(self):
        self.dbg.p(1, "rentre dans 'verifie_IPS'")
        # si ce qui est rentré n'est pas un entier
        if not self.lineEdit_IPS.text().isdigit() and len(self.lineEdit_IPS.text()) > 0:
            retour = QMessageBox.warning(
                self,
                _translate(
                    u"pymecavideo", "Le nombre d'images par seconde doit être un entier", None),
                _translate(u"pymecavideo", "merci de recommencer", None),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        return
    

def usage():
    print("""\
Usage : pymecavideo [-d (1-3)| --debug=(1-3)] [video | mecavideo]
   lance pymecavideo, une application d'analyse des mouvements
   option facultative : -d ou --debug= débogage +- verbeux (entre 1 et 3)
   argument facultatif : fichier video standard ou fichier mecavideo

   les fichiers mecavideo sont créés par l'application pymecavideo""")
    return


def run():
    global app
    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(args, "d:", ["debug="])
    except getopt.GetoptError as err:
        self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
        usage()
        sys.exit(2)

    ###translation##
    locale = "%s" % QLocale.system().name()
    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale):
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    langdir = os.path.join(FenetrePrincipale._dir("langues"),
                           r"pymecavideo_" + locale)
    if appTranslator.load(langdir):
        b = app.installTranslator(appTranslator)
    window = FenetrePrincipale(None, opts, args)
    window.show()
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
