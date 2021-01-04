# -*- coding: utf-8 -*-

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
import sys, os, os.path, subprocess
# if sys.platform == "win32" or sys.argv[0].endswith(".exe"):
# import Error
thisDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, thisDir)

from vecteur import vecteur
import time
import locale, getopt
from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

# création précoce de l'objet application, déjà nécessaire pour traiter les bugs
app = QApplication(sys.argv)

from glob import glob
from echelle import Label_Echelle, echelle
from label_video import Label_Video
from label_trajectoire import Label_Trajectoire
from label_origine import Label_Origine
from cadreur import Cadreur, openCvReader
from preferences import Preferences
from dbg import Dbg
from listes import listePointee
from version import Version
from label_auto import Label_Auto
from dialogencode import QMessageBoxEncode
from toQimage import toQImage
from echelle import Label_Echelle_Trace

import qtiplotexport
import re

import threading
import platform
import tempfile
import math

from globdef import HOME_PATH,APP_DATA_PATH, VIDEO,\
    SUFF, VIDEO_PATH, CONF_PATH, \
    IMG_PATH, ICON_PATH, LANG_PATH, \
    DATA_PATH, HELP_PATH, NEWVID_PATH

from detect import filter_picture

import functools


def time_it(func):
    """Timestamp decorator for dedicated functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()                 
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        mlsec = repr(elapsed).split('.')[1][:3]
        readable = time.strftime("%H:%M:%S.{}".format(mlsec), time.gmtime(elapsed))
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
        self.tmpdir=tmpdir
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
        self.tmpdir=tmpdir
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

        ######QT
        QMainWindow.__init__(self)
        QWidget.__init__(self, parent)
        self.hauteur = 1
        self.largeur = 0
        self.ratio = 1
        self.decalh = 120
        self.decalw = 197
        self.rotation=0 #permet de retourner une vidéo mal prise
        self.pointsProbables=[None] # points utilisés pour la détection automatique, définissent une zone où il est probable de trouver un objet suivi
        self.methode_thread = 3 # définit la methode de calcul à utiliser pour la détection auto. 1 : 1 thread de calcul  2 : découpage en plusieurs thread 3: 1 thread<-> 1 calcul
        
        #### Mode plein écran
        self.plein_ecran = False
        QShortcut(QKeySequence(Qt.Key_F11), self, self.basculer_plein_ecran)

        self.height_screen, self.width_screen = QDesktopWidget().screenGeometry().height(), QDesktopWidget().screenGeometry().width()

        from Ui_pymecavideo_mini_layout import Ui_pymecavideo

        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowSystemMenuHint |
                            Qt.WindowMinMaxButtonsHint)

        self.ui = Ui_pymecavideo()
        self.ui.setupUi(self)

        self.setMaximumSize(QSize(self.width_screen, self.height_screen))
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
            
        ####intialise les répertoires
        self._dir()
        defait_icon = os.path.join(self._dir("icones"), "undo.png")

        self.ui.pushButton_defait.setIcon(QIcon(defait_icon))
        refait_icon = os.path.join(self._dir("icones"), "redo.png")
        self.ui.pushButton_refait.setIcon(QIcon(refait_icon))

        # variables à initialiser
        # disable UI at beginning
        self.ui.tabWidget.setEnabled(0)
        self.ui.actionDefaire.setEnabled(0)
        self.ui.actionRefaire.setEnabled(0)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(0)
        self.ui.menuE_xporter_vers.setEnabled(0)
        self.ui.actionSaveData.setEnabled(0)
        self.ui.actionExemples.setEnabled(0)

        # Ooo export
        self.exe_ooo = False
        for exe_ooo in ["soffice", "ooffice3.2"]:
            if any(os.access(os.path.join(p, exe_ooo), os.X_OK) for p in os.environ['PATH'].split(os.pathsep)):
                self.exe_ooo = exe_ooo

        # sciDAVis export
        self.scidavis_present = False
        if any(os.access(os.path.join(p, "scidavis"), os.X_OK) for p in os.environ['PATH'].split(os.pathsep)):
            self.scidavis_present = "scidavis"

        # qtiplot export
        self.qtiplot_present = False
        if any(os.access(os.path.join(p, "qtiplot"), os.X_OK) for p in os.environ['PATH'].split(os.pathsep)):
            self.qtiplot_present = "qtiplot"

        self.init_variables(opts)

        # connections internes
        self.ui_connections()

        # prise en compte d'options de la ligne de commande
        self.traiteOptions()

        # chargement d'un éventuel premier fichier
        self.splashVideo()
        
        ##reinitialise_capture HACK pour le redimensionnement de l'échelle.
        #self.reinitialise_capture()
    
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
        for opt, val in self.opts:
            if opt in ['-f', '--fichier_mecavideo']:
                return
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
        try:
            self.origine = vecteur(self.largeur/2, self.hauteur/2)
            self.largeurAvant = self.largeur
            self.hauteurAvant  = self.hauteur
            self.origineAvant = self.origine
        except AttributeError:
            self.origine = vecteur(320, 240)
            self.largeurAvant = self.largeur
            self.hauteurAvant  = self.hauteur
            self.origineAvant = self.origine
        self.rouvert = False #positionné a vrai si on vien d'ouvrir un fichier mecavideo

        self.auto = False
        self.motif = []
        self.lance_capture = False
        self.modifie = False #est Vraie si le fichier est odifié. permet de sauvegarder les changements
        self.points = {}  # dictionnaire des points cliqués, par n d'image.
        self.trajectoire = {}  # dictionnaire des points des trajectoires
        self.pX = {}  # points apparaissant à l'écran, indexés par X
        self.pY = {}  # points apparaissant à l'écran, indexés par Y
        self.index_du_point = 0
        self.echelle_image = echelle()  # objet gérant l'image
        self.couleurs = ["red", "blue", "cyan", "magenta", "yellow", "gray",
                         "green"]  # correspond aux couleurs des points de la trajectoire
        self.nb_de_points = 0  # nombre de points suivis
        self.point_attendu = 0
        self.nb_clics = 0
        self.premiere_image = 1  # n° de la première image cliquée
        self.index_de_l_image = 1  # image à afficher
        
        self.filename = filename
        self.opts = opts
        self.stdout_file = os.path.join(APP_DATA_PATH, "stdout")
        self.exitDecode = False
        self.echelle_faite = False
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)

        self.rotation = 0
        try : 
            self.ratio = self.determineRatio()
        except :
            pass
        self.listePoints = listePointee()
        self.pileDeDetections = []

        self.premierResize = True  # arrive quand on ouvre la première fois la fenetre
        self.chrono = False
        self.a_une_image = False

        self.resizing = False
        self.stopRedimensionne = False
        self.defixeLesDimensions()
        

        
    def init_interface(self, refait=0):
        self.ui.tabWidget.setEnabled(1)
        self.ui.actionExemples.setEnabled(1)
        self.cree_tableau()
        try:
            self.label_trajectoire.clear()
        except AttributeError:
            self.label_trajectoire = Label_Trajectoire(self.ui.label_3, self)
            self.label_trajectoire.show()

        self.update()
        self.ui.horizontalSlider.setEnabled(0)

        self.ui.echelleEdit.setEnabled(0)
        self.ui.echelleEdit.setText(_translate("pymecavideo", "indéf", None))
        self.affiche_echelle()
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

        if not self.qtiplot_present:
            self.desactiveExport("Qtiplot")
        if not self.scidavis_present:
            self.desactiveExport("SciDAVis")

        # création du label qui contiendra la vidéo.
        try:
            self.dbg.p(3, "In : init_interface, clear Label_Video")
            self.label_video.clear()
        except AttributeError:
            self.dbg.p(3, "In : init_interface, cree Label_Video")
            self.label_video = Label_Video(parent=self.ui.label, app=self)
            self.label_video.show()

        self.ui.pushButtonEnregistreChrono.setVisible(0)
        self.ui.tabWidget.setCurrentIndex(0)  # montre l'onglet video

        self.ui.pushButton_stopCalculs.setEnabled(0)
        self.ui.pushButton_stopCalculs.hide()
        


    def desactiveExport(self, text):
        """
        Désactive la possibilité d'exportation, pour l'application dénotée par
        text.
        @param text le texte exact dans l'exportCombo qu'il faut inactiver
        """
        self.dbg.p(1, "rentre dans 'desactiveExport'")
        index = self.ui.exportCombo.findText(text)
        if index > 0:
            self.ui.exportCombo.setItemData(index, Qt.blue, Qt.BackgroundRole)
            self.ui.exportCombo.setItemText(index, _translate("pymecavideo", "NON DISPO : {0}", None).format(text))
            self.ui.exportCombo.setItemData(index, Qt.blue, Qt.BackgroundRole)
        return

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
        if self.echelle_image.isUndef():
            self.ui.echelleEdit.setText(_translate("pymecavideo", "indéf.", None))
            self.ui.Bouton_Echelle.setEnabled(True)
        else:
            epxParM = self.echelle_image.pxParM()
            if epxParM > 20:
                self.ui.echelleEdit.setText("%.1f" % epxParM)
            else:
                self.ui.echelleEdit.setText("%8e" % epxParM)
            self.ui.Bouton_Echelle.setEnabled(False)
        self.ui.echelleEdit.show()
        self.ui.Bouton_Echelle.show()

    def reinitialise_capture(self):
        """
        Efface toutes les données de la capture en cours et prépare une nouvelle
        session de capture.
        """
        self.dbg.p(1, "rentre dans 'reinitialise_capture'")
        self.montre_vitesses = False
        try : 
            self.label_trajectoire.update() #premier lancement sans fichier
        except AttributeError:
            pass
        self.ui.label.update()
        try : 
            self.label_video.update()
            self.label_video.setCursor(Qt.ArrowCursor)
            self.label_video.setEnabled(1)
        except AttributeError: 
            pass
        try:
            self.label_echelle_trace.hide()
            del self.label_echelle_trace
        except AttributeError:
            pass  # quand on demande un effacement tout au début. Comme par exemple, ouvrir les exmples.

        self.init_variables(None, filename=self.filename)
        try  : 
            self.affiche_image()
        except AttributeError:
            pass

        self.echelle_image = echelle()
        self.affiche_echelle()
        self.ui.horizontalSlider.setEnabled(1)
        self.ui.spinBox_image.setEnabled(1)
        self.ui.spinBox_image.setValue(1)
        self.enableDefaire(False)
        self.enableRefaire(False)
        self.affiche_nb_points(1)
        self.ui.Bouton_lance_capture.setEnabled(1)
        
        ##désactive le bouton de calculs si existant : 
        self.ui.pushButton_stopCalculs.setEnabled(0)
        self.ui.pushButton_stopCalculs.hide()
        
        ### Réactiver checkBox_avancees après réinitialisation ###
        self.ui.pushButton_origine.setEnabled(1)
        self.ui.checkBox_abscisses.setEnabled(1)
        self.ui.checkBox_ordonnees.setEnabled(1)
        self.ui.checkBox_auto.setEnabled(1)
        self.ui.checkBox_abscisses.setCheckState(Qt.Unchecked)
        self.ui.checkBox_ordonnees.setCheckState(Qt.Unchecked)
        self.ui.checkBox_auto.setCheckState(Qt.Unchecked)
        
        self.ui.pushButton_rot_droite.setEnabled(1)
        self.ui.pushButton_rot_gauche.setEnabled(1)
        
        #remets le signal enlevé : 
        self.ui.horizontalSlider.valueChanged.connect(self.affiche_image_slider_move)
        self.ui.spinBox_image.valueChanged.connect(self.affiche_image_spinbox)

        if self.ui.tableWidget:
            self.ui.tableWidget.clear()
        

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
    
    def ui_connections(self):
        """connecte les signaux de QT"""
        self.dbg.p(1, "rentre dans 'ui_connections'")
        self.ui.actionOuvrir_un_fichier.triggered.connect(self.openfile)
        self.ui.actionExemples.triggered.connect(self.openexample)
        self.ui.action_propos.triggered.connect(self.propos)
        self.ui.actionAide.triggered.connect(self.aide)
        self.ui.actionDefaire.triggered.connect(self.efface_point_precedent)
        self.ui.actionRefaire.triggered.connect(self.refait_point_suivant)
        self.ui.actionQuitter.triggered.connect(self.close)
        self.ui.actionSaveData.triggered.connect(self.enregistre_ui)
        self.ui.actionCopier_dans_le_presse_papier.triggered.connect(self.presse_papier)
        self.ui.actionOpenOffice_org_Calc.triggered.connect(self.oooCalc)
        self.ui.action_Python_source.triggered.connect(self.pythonSource)
        self.ui.actionQtiplot.triggered.connect(self.qtiplot)
        self.ui.actionScidavis.triggered.connect(self.scidavis)
        self.ui.actionRouvrirMecavideo.triggered.connect(self.rouvre_ui)
        self.ui.Bouton_Echelle.clicked.connect(self.demande_echelle)
        self.ui.horizontalSlider.sliderReleased.connect(self.affiche_image_slider)
        self.ui.horizontalSlider.valueChanged.connect(self.affiche_image_slider_move)
        self.ui.spinBox_image.valueChanged.connect(self.affiche_image_spinbox)
        self.ui.Bouton_lance_capture.clicked.connect(self.debut_capture)
        self.clic_sur_video.connect(self.clic_sur_label_video)
        self.ui.comboBox_referentiel.currentIndexChanged.connect(self.tracer_trajectoires)
        self.ui.comboBox_mode_tracer.currentIndexChanged.connect(self.tracer_courbe)
        self.ui.tabWidget.currentChanged.connect(self.tracer_trajectoires)

        self.ui.checkBoxScale.currentIndexChanged.connect(self.enableSpeed)
        self.ui.checkBoxVectorSpeed.stateChanged.connect(self.enableSpeed)

        self.ui.radioButtonSpeedEveryWhere.clicked.connect(self.enableSpeed)
        self.ui.radioButtonNearMouse.clicked.connect(self.enableSpeed)
        self.ui.button_video.clicked.connect(self.video)
        self.ui.pushButton_select_all_table.clicked.connect(self.presse_papier)
        self.ui.pushButtonChrono.clicked.connect(self.chronoPhoto)
        self.ui.pushButton_reinit.clicked.connect(self.reinitialise_capture)
        self.ui.pushButton_defait.clicked.connect(self.efface_point_precedent)
        self.ui.pushButton_refait.clicked.connect(self.refait_point_suivant)
        self.ui.pushButton_origine.clicked.connect(self.choisi_nouvelle_origine)

        self.ui.checkBox_abscisses.stateChanged.connect(self.change_sens_X)
        self.ui.checkBox_ordonnees.stateChanged.connect(self.change_sens_Y)
        self.ui.pushButton_rot_droite.clicked.connect(self.tourne_droite)
        self.ui.pushButton_rot_gauche.clicked.connect(self.tourne_gauche)
        
        self.change_axe_origine.connect(self.change_axe_ou_origine)
        self.selection_done.connect(self.picture_detect)
        #self.selection_motif_done.connect(self.storeMotif)
        self.selection_motif_done.connect(self.suiviDuMotif)
        
        self.stopRedimensionnement.connect(self.fixeLesDimensions)
        self.OKRedimensionnement.connect(self.defixeLesDimensions)
        self.redimensionneSignal.connect(self.redimensionneFenetre)


        self.ui.pushButtonEnregistreChrono.clicked.connect(self.enregistreChrono)
        self.stopCalculs.connect(self.stopComputing)
        self.ui.pushButton_stopCalculs.clicked.connect(self.stopCalculs)
        self.updateProgressBar.connect(self.updatePB)

        self.ui.exportCombo.currentIndexChanged.connect(self.export)

        self.ui.pushButton_nvl_echelle.clicked.connect(self.recommence_echelle)

    def enregistreChrono(self):
        # self.label_trajectoire.render()
        self.pixmapChrono = QPixmap(self.label_trajectoire.size())
        self.label_trajectoire.render(self.pixmapChrono)
        dir_ = str(self._dir("home")[0])
                
        fichier = QFileDialog.getSaveFileName(self, 
                        caption = _translate("pymecavideo", "Enregistrer la chronophotographie", None),
                        directory =  dir_, filter =  _translate("pymecavideo", "fichiers images(*.png *.jpg)", None))
        self.pixmapChrono.save(fichier[0])

    def chronoPhoto(self):
        self.dbg.p(1, "rentre dans 'chronoPhoto'")
        ##ajoute la première image utilisée pour le pointage sur le fond du label
        self.chrono = not self.chrono
        if self.chrono :
            ok,img = self.cvReader.getImage(self.premiere_image, self.rotation)
            self.imageChrono = toQImage(img).scaled(self.largeur, self.hauteur, Qt.KeepAspectRatio) 
            self.label_trajectoire.setPixmap(QPixmap.fromImage(self.imageChrono))
            self.ui.pushButtonEnregistreChrono.setVisible(1)
            self.ui.pushButtonChrono.setStyleSheet("background-color: red");
        else:
            self.ui.pushButtonEnregistreChrono.setVisible(0)
            self.ui.pushButtonChrono.setStyleSheet("background-color: transparent");
            self.label_trajectoire.setPixmap(QPixmap())
        self.redimensionneFenetre()
    def fixeLesDimensions(self):
        self.setMinimumWidth(self.width())
        self.setMaximumWidth(self.width())
        self.setMinimumHeight(self.height())
        self.setMaximumHeight(self.height())

    def defixeLesDimensions(self):
        self.setMinimumWidth(800+self.decalw)
        self.setMaximumWidth(16000000)
        self.setMinimumHeight(600+self.decalh)
        self.setMaximumHeight(16000000)

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
            self.ui.pushButton_stopCalculs.setText("STOP CALCULS")
            self.ui.pushButton_stopCalculs.setEnabled(1)
            self.ui.pushButton_stopCalculs.show()
            self.label_video.setEnabled(0)
            #self.pileDeDetections=zip(range(self.index_de_l_image, int(self.image_max)+1))
            self.pileDeDetections = []
            for i in range(self.index_de_l_image, int(self.image_max)+1):
                for j in range(self.nb_de_points):
                    self.pileDeDetections.append(i)
            # programme le suivi du point suivant après un délai de 50 ms,
            # pour laisser une chance aux évènement de l'interface graphique
            # d'être traités en priorité
            self.dbg.p(3, "self.pileDeDetections : %s"%self.pileDeDetections)
            timer=QTimer.singleShot(50, self.detecteUnPoint)
    
    #@time_it
    def detecteUnPoint(self):
        """
        méthode (re)lancée pour les détections automatiques de points
        traite une à une les données empilées dans self.pileDeDetections
        et relance un signal si la pile n'est pas vide après chacun
        des traitements.
        """
        self.dbg.p(1, "rentre dans 'detecteUnPoint'")

        if self.pileDeDetections:
            if len(self.pileDeDetections)%self.nb_de_points!=0:
                self.indexMotif+=1
            else :
                self.indexMotif=0
                
            index_de_l_image=self.pileDeDetections.pop(0)
            texteDuBouton = "STOP CALCULS (%d)" %index_de_l_image
            self.ui.pushButton_stopCalculs.setText(texteDuBouton)

            #TODO : principal point noir du calcul.
            self.dbg.p(2, "On lance la detection avec : self.motif %s, self.indexMotif %s"%(self.motif, self.indexMotif))
            point = filter_picture(self.motif, self.indexMotif, self.imageAffichee, self.pointsProbables)

            self.pointsProbables[0]=point
            self.label_video.storePoint(vecteur(point[0], point[1]))

            # programme le suivi du point suivant après un délai de 5 ms,
            # pour laisser une chance aux évènement de l'interface graphique
            # d'être traités en priorité
            timer=QTimer.singleShot(5, self.detecteUnPoint)

                      
    def storeMotif(self):
        self.dbg.p(1, "rentre dans 'storeMotif'")
        if len(self.motif) == self.nb_de_points:
            self.dbg.p(3, "selection des motifs finie")
            self.label_auto.hide()
            self.label_auto.close()
            self.indexMotif = 0
            self.ui.pushButton_stopCalculs.setText("STOP CALCULS")
            self.ui.pushButton_stopCalculs.setEnabled(1)
            self.ui.pushButton_stopCalculs.show()
            self.label_video.setEnabled(0)
            self.goCalcul = True
            # TODO : tests avec les différents mode de threading

            # Python
            if self.methode_thread == 1 : 
                self.monThread = MonThreadDeCalcul(self, self.motif[self.indexMotif], self.imageAffichee)
                self.monThread.start()
            elif self.methode_thread==2 : ##1 thread par image
                for i in range((self.image_max-self.premiere_image)*self.nb_de_points) :
                    self.liste_thread = [MonThreadDeCalcul2(self, self.image, self.motif[self.indexMotif], self.imageAffichee)]
            elif self.methode_thread==3 :  #pour l'instant celle qui foncitonne le mieux
                timer=QTimer.singleShot(5, self.detecteUnPoint)
                

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
                self.pointTrouve = filter_picture(self.motif, self.indexMotif, self.imageAffichee, self.listePoints)
                self.dbg.p(3, "Point Trouve dans mon Thread : " + str(self.pointTrouve))
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
        self.pileDeDetections=[] # vide la liste des points à détecter encore
        try : 
            if self.monThread :                 
                self.monThread.stopped=True
        except AttributeError : 
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
                self.timer.start(100);
            else:
                while not self.exitDecode:
                    stdout_file = open(self.stdout_file, 'w+')
                    stdout = stdout_file.readlines()  ##a gloabliser poru windows
                    if not self.exitDecode:
                        try:
                            pct = stdout[-1].split()[3].replace('%', '').replace(')', '').replace('(', '')
                            assert (pct.isalnum())
                            exit = True
                        except IndexError:

                            exit = False

        except:
            pass


    def refait_echelle(self):
        # """Permet de retracer une échelle et de recalculer les points"""
        self.dbg.p(1, "rentre dans 'refait_echelle'")
        self.cree_tableau()
        self.recalculLesCoordonnees()

    def choisi_nouvelle_origine(self):
        self.dbg.p(1, "rentre dans 'choisi_nouvelle_origine'")
        nvl_origine = QMessageBox.information(
            self,
            u"NOUVELLE ORIGINE",
            u"Choisissez, en cliquant sur la vidéo le point qui sera la nouvelle origine")

        label = Label_Origine(parent=self.ui.label, app=self)
        label.show()
    
    def tourne_droite(self):
        self.tourne_image("droite")

    def tourne_gauche(self):
        self.tourne_image("gauche")

    def tourne_image(self, sens=None):
        self.dbg.p(1, "rentre dans 'tourne_image'")
        if sens=="droite" :
            increment = 90
            
        elif sens=="gauche" : 
            increment = -90
        else : 
            increment=0
        self.rotation+=increment
        if self.rotation>180 : 
            self.rotation=self.rotation-360 #arrive pour 270° par exemple
        elif self.rotation<=-180 :
            self.rotation=self.rotation+360
        
        self.dbg.p(2, "Dans 'tourne_image' self rotation vaut" + str(self.rotation))
        
        
        #self.dbg.p(2, "self.largeur : %s, self.hauteur : %s"%(self.largeur, self.hauteur))
        self.ratio = 1/self.ratio
                
        #gestion de l'origine et de l'échelle : 
        
        ###DEBUG
        self.dbg.p(3, "Dans 'tourne_image' avant de tourner, self.origine %s, self.largeur%s, self.hauteur%s"%(self.origine, self.largeur, self.hauteur))
        try :
            self.dbg.p(3, "Dans 'tourne_image' avant de tourner, self.echelle_image.p1 %s, self.echelle_image.p2 %s"%(self.echelle_image.p1, self.echelle_image.p2))
        except AttributeError : 
            pass
        ###
        
        self.origine = self.origine.rotate(increment, self.largeur, self.hauteur)
        
        
        #rotation vecteur echelle
        self.echelle_image.p1 = self.echelle_image.p1.rotate(increment, self.largeur, self.hauteur)
        self.echelle_image.p2 = self.echelle_image.p2.rotate(increment, self.largeur, self.hauteur) 
        
        
        self.largeur, self.hauteur = self.hauteur, self.largeur
        
        ###DEBUG
        self.dbg.p(3, "Dans 'tourne_image' après avoir tourné, self.origine %s, self.largeur%s, self.hauteur%s"%(self.origine, self.largeur, self.hauteur))
        try :
            self.dbg.p(3, "Dans 'tourne_image' après avoir tourné, self.echelle_image.p1 %s, self.echelle_image.p2 %s"%(self.echelle_image.p1, self.echelle_image.p2))
        except AttributeError : 
            pass
        ###
        
        self.change_axe_origine.emit()
        try : 
            
            self.feedbackEchelle(self.echelle_image.p1, self.echelle_image.p2)
        except AttributeError : 
            pass # pas d'échelle
        
        self.redimensionneSignal.emit(1)


    def change_axe_ou_origine(self):
        """mets à jour le tableau de données"""
        self.dbg.p(1, "rentre dans 'change_axe_ou_origine'")
        # repaint axes and define origine
        self.label_trajectoire.origine_mvt = self.origine
        self.label_trajectoire.update()
        
        self.label_video.origine = self.origine
        
        self.origineAvant = self.origine
        self.largeurAvant = self.largeur
        self.hauteurAvant = self.hauteur
        #try : 
        try :
            self.echelle_imagep1Avant = self.echelle_image.p1
            self.echelle_imagep2Avant = self.echelle_image.p2
        except AttributeError : 
            pass 
        
        self.label_video.update()
        self.echelle_faite=True ###TODO
        #self.stopRedimensionnement.emit()

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
                self.rempli_tableau(serie, position, donnees[key], recalcul=True)
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
        if self.echelle_faite:
            return vecteur(self.sens_X * (float(p.x() - self.origine.x()) * self.echelle_image.mParPx()), self.sens_Y *
                       float(self.origine.y() - p.y()) * self.echelle_image.mParPx())


    def presse_papier(self):
        """Sélectionne la totalité du tableau de coordonnées
        et l'exporte dans le presse-papier (l'exportation est implicitement
        héritée de la classe utilisée pour faire le tableau). Les
        séparateurs décimaux sont automatiquement remplacés par des virgules
        si la locale est française.
        """
        self.dbg.p(1, "rentre dans 'presse_papier'")
        trange = QTableWidgetSelectionRange(0, 0,
                                            self.ui.tableWidget.rowCount() - 1,
                                            self.ui.tableWidget.columnCount() - 1)
        self.ui.tableWidget.setRangeSelected(trange, True)
        self.ui.tableWidget.selection()

    def export(self):
        self.dbg.p(1, "rentre dans 'export'")
        """
        Traite le signal venu de exportCombo, puis remet l\'index de ce 
        combo à zéro.
        """
        if self.ui.exportCombo.currentIndex() > 0:
            option = self.ui.exportCombo.currentText()
            if option == "LibreOffice Calc":
                self.oooCalc()
            elif option == "Python (source)":
                self.pythonSource()
            elif option == "Qtiplot":
                self.qtiplot()
            elif option == "SciDAVis":
                self.scidavis()
            self.ui.exportCombo.setCurrentIndex(0)
        return


    def oooCalc(self):
        """
        Exporte directement les données vers OpenOffice.org Calc
        """
        self.dbg.p(1, "rentre dans 'oooCalc'")
        import oooexport

        calc = oooexport.Calc()
        calc.importPymeca(self)

    def pythonSource(self):
        """
        Exporte les données dans un fichier source Python3
        """
        self.dbg.p(1, "rentre dans 'python source'")
        f = tempfile.NamedTemporaryFile(prefix='pymecaTmp-', suffix=".py")
        fname = f.name
        f.close()
        f = open(fname, "w")
        date = time.strftime("%d/%m/%y %H:%M")
        f.write(f"## Données exportées de Pymecavidéo\n## {date}\n")
        f.write("\nimport numpy as np\nimport matplotlib.pyplot as plt\n")
        f.write(f"\n# Intervalle de temps auto-détecté\ndt={self.deltaT}\n")
        for i in range(self.nb_de_points):
            f.write(f"\n# coordonnées du point numéro {i+1}\n")
            ligne_x = f"x{i+1} = np.array(["
            ligne_y = f"y{i+1} = np.array(["
            for k in self.points.keys():
                data = self.points[k]
                for vect in data[1:]:
                    vect=self.pointEnMetre(vect)
                    ligne_x += f"{vect.x()}, "
                    ligne_y += f"{vect.y()}, "
            ligne_x += "])\n"
            ligne_y += "])\n"
            f.write(ligne_x)
            f.write(ligne_y)
            f.write("""

##############################################################
# Le code auto-généré qui suit peut être effacé à volonté.   #
##############################################################
# Il n'est là qu'à titre d'exemple, et il n'est pas toujours #
# approprié à l'usage des données que vous avez exportées.   #
##############################################################

## affichage des points
plt.plot(x1,y1,'o',markersize= 3)
plt.xlabel("x (en m)")
plt.ylabel("y (en m)")

## affichage des vecteurs vitesses
plt.title("Vecteurs vitesse")

for k in range(1,len(x1)):
    vx = (x1[k]-x1[k-1])/dt
    vy = (y1[k]-y1[k-1])/dt
    plt.quiver(x1[k-1], y1[k-1], vx, vy, scale=20, scale_units="xy")

## présentation du diagramme interactif
plt.grid()
plt.show()
""")
            f.close()
            reponse = QMessageBox.warning(
                None,
                _translate("pymecavideo", "Fichier Python créé", None),
                _translate("pymecavideo", """\
Le fichier {filename} a été créé dans un espace temporaire.
Pymecavideo essaiera de l'ouvrir dans un éditeur approprié.
""".format(
    filename=fname
    ),
                           None),
                QMessageBox.Ok, QMessageBox.Ok)
            # on essaie d'ouvrir le programme Python dans un
            # éditeur approprié
            for editor in ("geany", "thonny", "gedit"):
                if os.path.exists(f"/usr/bin/{editor}"):
                    subprocess.call(f"({editor} {fname}&)", shell=True)
                    # un éditeur est trouvé, inutile d'en essayer d'autres
                    break
        return
        
    def qtiplot(self):
        """
        Exporte directement les données vers Qtiplot
        """
        self.dbg.p(1, "rentre dans 'qtiplot'")
        plot = qtiplotexport.Qtiplot(self)
        f = tempfile.NamedTemporaryFile(prefix='pymecaTmp-', suffix=".qti")
        fname = f.name
        f.close()
        f = open(fname, "w")
        plot.saveToFile(f)
        f.close()
        t = threading.Thread(target=lanceQtiplot, args=(fname,))
        t.setDaemon(True)  # Qtiplot peut survivre à pymecavideo
        t.start()

    def scidavis(self):
        """
        Exporte directement les données vers SciDAVis
        """
        self.dbg.p(1, "rentre dans 'scidavis'")
        plot = qtiplotexport.Qtiplot(self)
        f = tempfile.NamedTemporaryFile(prefix='pymecaTmp-', suffix=".qti")
        fname = f.name
        f.close()
        f = open(fname, "w")
        plot.saveToFile(f)
        f.close()
        t = threading.Thread(target=lanceSciDAVis, args=(fname,))
        t.setDaemon(True)  # Scidavis peut survivre à pymecavideo
        t.start()

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
        elif lequel == "images":
            return IMG_PATH
        elif lequel == "icones":
            return ICON_PATH
        elif lequel == "langues":
            return LANG_PATH
        elif lequel == "data":
            return DATA_PATH
        elif lequel == "help":
            return HELP_PATH
        elif type(lequel) == type(""):
            self.dbg.p(1, "erreur, appel de _dir() avec le paramètre inconnu %s" % lequel)
            self.close()
        else:
            # vérifie/crée les repertoires
            for d in ("conf", "images"):
                dd = StartQt5._dir(str(d))
                if not os.path.exists(dd):
                    os.makedirs(dd)

    _dir = staticmethod(_dir)

    def init_cvReader(self):
        """
        Initialise le lecteur de flux vidéo pour OpenCV
        et recode la vidéo si nécessaire.
        """
        self.dbg.p(1, "rentre dans 'init_cvReader'")

        self.cvReader = openCvReader(self.filename)

        time.sleep(0.1)
        if not self.cvReader.ok and (
                    "/".join(self.filename.split('/')[:-1]) != NEWVID_PATH):  # if video is ever encoded, don't get in

            sansSuffixe = os.path.basename(self.filename)
            match = re.match("(.*)\.(.*)$", sansSuffixe)
            sansSuffixe = match.group(1)
            dest = os.path.join(NEWVID_PATH, sansSuffixe + ".avi")
            self.qmsgboxencode = QMessageBoxEncode(self, dest)  # in this, thread to encode
            self.qmsgboxencode.show()
        else:
            return True

    def rouvre_ui(self):
        self.dbg.p(1, "rentre dans 'rouvre_ui'")
        dir_ = self._dir("home")[0]
        fichier, _ = QFileDialog.getOpenFileName(self, _translate("pymecavideo", "Ouvrir un projet Pymecavideo", None),
                                              dir_,
                                              _translate("pymecavideo", "fichiers pymecavideo(*.csv)", None))

        if fichier != "":
            self.rouvre(fichier)

    def loads(self, s):
        self.dbg.p(1, "rentre dans 'loads'")
        s = s[1:-2].replace("\n#", "\n")
        self.echelle_image.longueur_reelle_etalon, point, self.deltaT, self.nb_de_points = s.splitlines()[1:-1][-4:]
        
        donnees_fichier = s.splitlines()[1:-1]
        dico_donnee = {}
        for donnee in donnees_fichier :
            if len(donnee.split('='))==2:
                cle, valeur = donnee.split('=')
                dico_donnee[cle.strip()]=valeur.strip()
        
        self.filename = dico_donnee["video"]
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.filename))
        try : 
            self.sens_X = int(dico_donnee['sens axe des X'])
        except KeyError: 
            self.sens_X = 1
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.sens_X))
        try : 
            self.sens_Y = int(dico_donnee['sens axe des Y'])
        except KeyError : 
            self.sens_Y = 1
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.sens_Y))
        try : 
            self.largeur = int(dico_donnee['largeur video'])
        except KeyError:
            self.largeur = 640
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.largeur))
        try : 
            self.hauteur = int(dico_donnee['hauteur video'])
        except KeyError : 
            self.largeur = 480
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.hauteur))
        try : 
            self.rotation = int(dico_donnee['rotation'])
        except KeyError: 
            self.rotation=0
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.rotation))      
        try : 
            self.origine = vecteur(dico_donnee['origine de pointage'].split()[-2][1:-1], dico_donnee['origine de pointage'].split()[-1][:-1])        
        except KeyError:
            self.origine = vecteur(self.largeur//2, self.hauteur//2)
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.origine))
        self.premiere_image = int(dico_donnee['index de depart'])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.premiere_image))
        self.echelle_image.longueur_reelle_etalon = float(self.echelle_image.longueur_reelle_etalon.split()[1])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.echelle_image.longueur_reelle_etalon))
        if self.echelle_image.mParPx() == 1 :
            self.echelle_faite = False
        else :
            self.echelle_faite = True

        self.echelle_image.p1, self.echelle_image.p2 = vecteur(point.split()[-4][1:-1], point.split()[-3][:-1]) \
            , vecteur(point.split()[-2][1:-1], point.split()[-1][:-1])
        self.dbg.p(3, "rentre dans 'loads' %s" % ([self.echelle_image.p1, self.echelle_image.p2]))
        self.deltaT = float(self.deltaT.split()[-1])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.deltaT))
        self.nb_de_points = int(self.nb_de_points.split()[-2])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.nb_de_points))

        self.init_cvReader()

    def rouvre(self, fichier):
        """Open a mecavideo file"""
        self.dbg.p(1, "rentre dans 'rouvre'")
        self.reinitialise_capture()
        lignes = open(fichier, "r").readlines()
        i = 0
        self.points = {} #dictionnaire des données, simple. Les clefs sont les index de l'image. les données les
        self.listePoints = listePointee()
        dd = ""
        for l in lignes:
            if l[0] == "#":
                dd += l
        self.echelle_image = echelle()  # on réinitialise l'échelle
        self.loads(dd)  # on récupère les données importantes
        self.check_uncheck_direction_axes()  # check or uncheck axes Checkboxes
        self.init_interface()
        self.change_axe_ou_origine()
        # puis on trace le segment entre les points cliqués pour l'échelle
        self.feedbackEchelle(self.echelle_image.p1, self.echelle_image.p2)
        framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos(self.rotation)
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
                    pos = vecteur(float(d[j].replace(",", ".")) * self.echelle_image.pxParM() \
                                + self.origine.x(), self.origine.y() - float(
                            d[j + 1].replace(",", ".")) * self.echelle_image.pxParM())

                    self.enregistre_dans_listePoints(
                        pos, index=int(float(t)*framerate)+self.premiere_image
                    )
                    self.points[i].append(pos)

                i += 1

        self.defini_barre_avancement()

        self.affiche_echelle()  # on met à jour le widget d'échelle
        derniere_image = self.listePoints[len(self.listePoints)-1][0]+1
        self.ui.horizontalSlider.setValue(derniere_image)
        self.ui.spinBox_image.setValue(derniere_image)
        self.affiche_nb_points(self.nb_de_points)
        self.enableDefaire(True)
        self.enableRefaire(False)

        self.affiche_image()  # on affiche l'image
        self.debut_capture(departManuel=False)
        self.ui.tableWidget.show()
        self.recalculLesCoordonnees()
        # On met à jour les préférences
        
        self.prefs.lastVideo = self.filename
        self.prefs.videoDir = os.path.dirname(self.filename)
        self.prefs.save()
       # self.metsAjourLesDimensions()


    def metsAjourLesDimensions(self):
        self.dbg.p(1, "rentre dans 'metsAjourLesDimensions'")
        self.resize(self.largeur+self.decalw,self.hauteur+self.decalh)
        self.ui.centralwidget.setGeometry(0,15,self.largeur+self.decalw,self.hauteur+self.decalh)
        self.ui.label.setFixedSize(self.largeur, self.hauteur)
        self.label_video.setFixedSize(self.largeur, self.hauteur)
        self.label_trajectoire.setFixedSize(self.largeur, self.hauteur)

    def determineRatio(self):
        self.dbg.p(1, "rentre dans 'determineRatio'")
        if self.premierResize:
            if self.cvReader is None:
                self.image_max, self.largeurFilm, self.hauteurFilm = 10, 320, 200
            else:
                framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos()
        framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos()
        
        ratioFilm = float(self.largeurFilm) / self.hauteurFilm

        return ratioFilm

    
    def redimensionneFenetre(self, tourne=False):
        """si l'image est horizontale : (self.ratio >1)
                on fixe la largeur minimale : 800
                on détermine la hauteur minimale et on la fixe 
                
           Si l'image est verticale : (self.ratio <1)
                on fixe la hauteur minimale  :600
                on détermine la largeur minimale et on la fixe 
            
        """
        self.dbg.p(1, "rentre dans 'redimensionne Fenetre'")
        
        #if not self.isFullScreen() : -> ne fonctionne pas. TODO
        if not self.width()==self.width_screen and not self.height()==self.height_screen : 
            ###dimensions minimum        
            if self.ratio >= 1 : 
                self.dbg.p(2, "self.ratio supérieur à 1'")
                self.setMinimumSize(QSize(800+self.decalw, self.heightForWidth(800)))
                self.largeur = self.width()-self.decalw
                self.hauteur = self.heightForWidth(self.largeur)
                
                if abs(self.height()- int(self.hauteur+self.decalh))>10: #si la hauteur est vraiment différente, on redimensionne. Permet de sortir d'une boucle infinie.
                    self.setFixedHeight(self.hauteur+self.decalh) 
            else : 
                self.dbg.p(2, "self.ratio < à 1'")
                self.setMinimumSize(QSize(self.widthForHeight(600), 600))
                
                #traitement spécial si on vient de tourner l'image : on détermine la hauteur maximale de la vidéo
                #if tourne : 
                    #self.setFixedHeight(self.hauteur+self.decalh)
                self.hauteur = self.height()-self.decalh
                self.largeur = self.widthForHeight(self.hauteur)
                if abs(self.width()-int(self.largeur+self.decalw))>10 : 
                    self.setFixedWidth(self.largeur+self.decalw)

            if self.largeurAvant==0 : #premier redimensionnement
                self.largeurAvant = self.largeur
                self.hauteurAvant = self.hauteur
        
        else : #isFullScreen
            #détermination de la valeur maximum de self.largeur et self.hauteur : 
            ratio_ecran = self.width_screen/self.height_screen
            self.dbg.p(2, "ratio ecran %s, ration %s"%(ratio_ecran, self.ratio))
            if self.ratio >= ratio_ecran : #largeur qui fixe les dimensions 
                self.largeur = self.width_screen()-self.decalw
                self.hauteur = self.heightForWidth(self.largeur)

                
            else : #hauteur qui est limitante
                self.hauteur = self.height_screen-self.decalh
                self.largeur = self.widthForHeight(self.hauteur)
                
                #    self.setFixedWidth(self.largeur+self.decalw)
            #self.setFixed
            
        self.dbg.p(2, "on fixe les hauteurs du label")
        self.ui.label.setFixedHeight(self.hauteur)
        self.ui.label.setFixedWidth(self.largeur)
        
        if hasattr(self, 'label_video'):
            self.dbg.p(2, "on fixe les hauteurs de label_video")            
            self.label_video.setFixedHeight(self.hauteur)
            self.label_video.setFixedWidth(self.largeur)
            self.dbg.p(2, "label_vidéo situé en %s %s"%(self.label_video.pos().x(),self.label_video.pos().y() ))
            self.dbg.p(3, "label_vidéo largeur :  %s hauteur : %s"%(self.label_video.width(),self.label_video.height()))
        
        self.dbg.p(2, "On fixe les tailles de centralwidget et tabWidget") 
        self.ui.centralwidget.setFixedSize(self.size()-QSize(1,1))
        self.ui.tabWidget.setFixedSize(self.size()-QSize(1,1))
        
        
        if tourne : #besoin de changer l'image lors d'un retournement
            self.dbg.p(2, "image tournée -> affiche_image pour mettre à jour l'extraction de l'image")
            self.affiche_image() 
            
        else : 
            try : #gère le  cas où on démarre sans vidéos
                self.dbg.p(2, "L'image est juste affichée, non rééextraite.")
                self.afficheJusteImage()
            except AttributeError:
                pass
        
        #prise en compte de l'échelle 
        
        self.dbg.p(2, "Recalcul de l'origine")
        self.dbg.p(3, "origine avant transformation : %s"%self.origine)
        self.origine = vecteur(self.origineAvant.x()*float(self.largeur)/self.largeurAvant, self.origineAvant.y()*float(self.largeur)/self.largeurAvant)
        self.dbg.p(3, "origine après transformation : %s"%self.origine)
        try :
            self.dbg.p(2, "traçage de l'échelle")
            self.dbg.p(3, "echelle avant transformation : p1 : %s  p2 : %s"%(self.echelle_image.p1, self.echelle_image.p2))
            self.echelle_image.p1 = vecteur(self.echelle_imagep1Avant.x()*float(self.largeur)/self.largeurAvant, self.echelle_imagep1Avant.y()*float(self.largeur)/self.largeurAvant)
            self.echelle_image.p2 = vecteur(self.echelle_imagep2Avant.x()*float(self.largeur)/self.largeurAvant, self.echelle_imagep2Avant.y()*float(self.largeur)/self.largeurAvant)
            self.dbg.p(3, "echelle après transformation : p1 : %s  p2 : %s"%(self.echelle_image.p1, self.echelle_image.p2))
            #self.label_echelle_trace.setGeometry(0,0,self.largeur, self.hauteur)
            self.feedbackEchelle(self.echelle_image.p1, self.echelle_image.p2)
        except : pass
        
        if hasattr(self, 'label_video'):
                self.dbg.p(2, "MAJ de label_video")

                self.label_video.origine = self.origine
                self.label_video.maj()
                self.label_trajectoire.maj()
                self.afficheJusteImage()
        try : 
            self.dbg.p(3, """largeur LABEL %s  hauteur LABEL, %s position LABEL %s %s \n
                   self.largeur %s  self.hauteur %s \n, 
                   largeur FENETRE : %s  hauteur FENETRE : %s\n, 
                   largeur ÉCRAN : %s  hauteur ÉCRAN : %s\n,
                   largeur label_video %s, hauteur label_video %s, position label_video %s %s\n
                   largeur tabWidget %s, hauteur tabWidget %s\n
                   largeur centralwidget %s, hauteur centralwidget %s\n
                   """
                   % (self.ui.label.width(), self.ui.label.height(), self.ui.label.pos().x(), self.ui.label.pos().y(), self.largeur, self.hauteur, self.width(), self.height(), self.width_screen, self.height_screen, self.label_video.width(), self.label_video.height(), self.label_video.pos().x(), self.label_video.pos().y(), self.ui.tabWidget.width(), self.ui.tabWidget.height(), self.ui.centralwidget.width(), self.ui.centralwidget.height()))
        except : 
            pass
        
    def widthForHeight(self, h):
        #calcule self.largeur et self.hauteur si la hauteur est prédominante
        #si la hauteur est trop petite, ne permet plus de redimensionnement
        self.dbg.p(1, "retre dans 'widthForHeight'")
        self.dbg.p(2, "argument h : %s"%(str(h)))
    
        return int(h*self.ratio)
        
        
    def heightForWidth(self, w):
        #calcul self.largeur et self.hauteur
        #si la largeur est trop petite, ne permet plus de redimensionnement
        self.dbg.p(1, "retre dans 'heightForWidth'")
        self.dbg.p(2, "argument w : %s"%(str(w)))
        
        return int(w/self.ratio)
        
    
    def resizeEvent(self, event):
        self.dbg.p(1, "rentre dans 'resizeEvent'")
        if self.largeur !=0 : 
            self.redimensionneFenetre()    
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
#""" % (self.filename, self.sens_X, self.sens_Y, self.largeur, self.hauteur,self.rotation, self.origine, self.premiere_image \
                             , self.echelle_image.longueur_reelle_etalon, self.echelle_image.longueur_pixel_etalon(),
        self.echelle_image.p1, self.echelle_image.p2, self.deltaT, self.nb_de_points, msg)
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
                file.write(self.entete_fichier(_translate("pymecavideo", "temps en seconde, positions en mètre", None)))
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
            fichier, hints = QFileDialog.getSaveFileName(
                self,
                "FileDialog",
                "data.csv",
                "*.csv *.txt *.asc *.dat")

            self.enregistre(fichier)

    def debut_capture(self, departManuel=True):
        self.dbg.p(1, "rentre dans 'debut_capture'")
        """
        permet de mettre en place le nombre de point à acquérir
        @param departManuel vrai si on a fixé à la main la première image.

        """

        #try:
            #self.origine_trace.hide()
            #del self.origine_trace
        #except:
            #pass

        self.label_video.setFocus()
        self.label_video.show()
        self.label_video.activateWindow()
        self.label_video.setVisible(True)
        try:
            self.label_echelle_trace.lower()  # nécessaire sinon, label_video n'est pas actif.
        except AttributeError:
            pass

        self.nb_de_points = self.ui.spinBox_nb_de_points.value()
        self.affiche_nb_points(False)
        self.affiche_lance_capture(False)
        self.ui.horizontalSlider.setEnabled(0)
        self.ui.spinBox_image.setEnabled(1)

        self.arretAuto = False

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
            self.ui.comboBox_referentiel.insertItem(-1, _translate("pymecavideo", "point N° {0}", None).format(i+1))
        self.cree_tableau()

        self.ui.pushButton_origine.setEnabled(0)
        self.ui.checkBox_abscisses.setEnabled(0)
        self.ui.checkBox_ordonnees.setEnabled(0)
        self.ui.checkBox_auto.setEnabled(0)
        self.ui.Bouton_Echelle.setEnabled(0)
        self.ui.Bouton_lance_capture.setEnabled(0)
        self.ui.pushButton_rot_droite.setEnabled(0)
        self.ui.pushButton_rot_gauche.setEnabled(0)

        #on empêche le redimensionnement
        self.fixeLesDimensions()

        #si aucune échelle n'a été définie, on place l'étalon à 1 px pou 1 m.
        if not self.echelle_faite:
            self.echelle_image.longueur_reelle_etalon = 1
            self.echelle_image.p1 = vecteur(0,0)
            self.echelle_image.p1 = vecteur(0,1)
            self.echelle_faite = True
        #######automatic capture
        if self.ui.checkBox_auto.isChecked():
            #self.auto = True
            self.mets_a_jour_label_infos(
            _translate("pymecavideo", "Pointage Automatique", None))
            reponse = QMessageBox.warning(None, "Capture Automatique",
                                          _translate("pymecavideo", """\
Veuillez sélectionner un cadre autour de(s) l'objet(s) que vous voulez suivre.
Vous pouvez arrêter à tous moments la capture en appuyant sur le bouton""",
                                                     None),
                                          QMessageBox.Ok, QMessageBox.Ok)
            try: 
                self.label_auto.hide()
                del self.label_auto
            except : 
                pass
            self.label_auto = Label_Auto(self.label_video, self)  # in this label, motif(s) are defined.
            self.label_auto.show()
            #IMPORTANT : permet de gagner en fluidité de l'affichage lors du poitnage autmatique. BUG lié au rafraichissment du slider.
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
        self.ui.tableWidget.setColumnCount(self.nb_de_points * 2 + 1)
        self.ui.tableWidget.setDragEnabled(True)
        # on met des titres aux colonnes.
        self.ui.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem('t (s)'))

        for i in range(self.nb_de_points):
            if  self.echelle_faite:
                x = "X%d (m)" % (1 + i)
                y = "Y%d (m)" % (1 + i)
            else:
                x = "X%d (px)" % (1 + i)
                y = "Y%d (px)" % (1 + i)

            self.ui.tableWidget.setHorizontalHeaderItem(1 + 2 * i, QTableWidgetItem(x))
            self.ui.tableWidget.setHorizontalHeaderItem(2 + 2 * i, QTableWidgetItem(y))


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
        min = None
        max = None
        for n in range(self.nb_de_points):
            if n == referentiel:
                pass
            for i in self.points.keys():
                p = self.points[i][1 + n] - self.points[i][1 + referentiel]
                min = p.minXY(min)
                max = p.maxXY(max)
        if min != None and max != None:
            return (min + max) * 0.5
        else:
            return vecteur(self.largeur / 2, self.hauteur / 2)

    def efface_point_precedent(self):
        """revient au point précédent
        """
        self.dbg.p(1, "rentre dans 'efface_point_precedent'")
        #efface la dernière entrée dans le tableau
        self.ui.tableWidget.removeRow(int((len(self.listePoints)-1)/self.nb_de_points))
        self.listePoints.decPtr()
        self.dbg.p(2, "self.listePoints" + str(self.listePoints) + "self.points" +str( self.points))
        if len(self.listePoints)%self.nb_de_points!=0:
            try : 
                self.points[len(self.listePoints)/self.nb_de_points].pop()
            except KeyError:
                self.dbg.p(1, "Erreur de clé : "+str(len(self.listePoints)/self.nb_de_points)) #liée au passage de ptyhon2 à python3 et au changement de comportement de /
        else:
            try : 
                del self.points[len(self.listePoints)/self.nb_de_points]
            except KeyError : 
                self.dbg.p(1, "Erreur de clé : "+str(len(self.listePoints)/self.nb_de_points))

        ##dernière image à afficher
        if self.nb_de_points!=1:
            if len(self.listePoints)-1>=0 :
                if len(self.listePoints)%self.nb_de_points==self.nb_de_points-1:
                    self.index_de_l_image = self.listePoints[len(self.listePoints)-1][0]
        else :
            if len(self.listePoints)-1>=0 :
                if len(self.listePoints)%self.nb_de_points==self.nb_de_points-1:
                    self.index_de_l_image = self.listePoints[len(self.listePoints)-1][0]+1
        self.affiche_image()

        self.clic_sur_label_video_ajuste_ui(self.index_de_l_image)


    def refait_point_suivant(self):
        """rétablit le point suivant après un effacement
        """
        self.dbg.p(1, "rentre dans 'refait_point_suivant'")
        self.listePoints.incPtr()
        #on stocke si la ligne est complète
        if len(self.listePoints)%self.nb_de_points==0:
            self.stock_coordonnees_image(ligne=int((len(self.listePoints)-1)/self.nb_de_points))
            self.index_de_l_image = self.listePoints[len(self.listePoints)-1][0]+1
        self.affiche_image()

        self.clic_sur_label_video_ajuste_ui(self.index_de_l_image)


    def video(self):
        self.dbg.p(1, "rentre dans 'videos'")
        ref = self.ui.comboBox_referentiel.currentText().split(" ")[-1]
        if len(ref) == 0 or ref == "camera": return
        c = Cadreur(int(ref), self)
        c.montrefilm()


    def tracer_trajectoires(self, newValue):
        """
        traite les signaux émis par le changement d'onglet, ou
        par le changement de référentiel dans l'onglet des trajectoires.
        On peut aussi appeler cette fonction directement, auquel cas on
        donne la valeur "absolu" à newValue pour reconnaître ce cas.
        efface les trajectoires anciennes, puis
        trace les trajectoires en fonction du référentiel choisi.
       
        """
        self.dbg.p(1, "rentre dans 'tracer_trajectoires'")

        try:

            if self.ui.tabWidget.currentIndex() != 0:  # Pas le premier onglet
                self.statusBar().hide()

                origine = vecteur(0, 0)
                if newValue == "absolu":
                    ref = "camera"
                else:
                    ref = self.ui.comboBox_referentiel.currentText().split(" ")[-1]

                if len(ref) == 0: return
                if ref != "camera":
                    self.ui.pushButtonChrono.setEnabled(0)
                    self.ui.pushButtonEnregistreChrono.setVisible(0)
                    self.chrono = False
                    bc = self.mediane_trajectoires(int(ref) - 1)
                    origine = vecteur(self.largeur / 2, self.hauteur / 2) - bc
                    self.label_trajectoire.origine = origine

                    self.label_trajectoire.referentiel = ref
                else:  # if camera, all tranlsations are disabled
                    self.ui.pushButtonChrono.setEnabled(1)

                    self.label_trajectoire.referentiel = 0
                    self.label_trajectoire.origine = vecteur(0, 0)

                # rempli le menu des courbes à tracer
                self.ui.comboBox_mode_tracer.clear()
                self.ui.comboBox_mode_tracer.insertItem(-1, _translate("pymecavideo", "Choisir ...", None))
                for i in range(self.nb_de_points):
                    combo = self.ui.comboBox_mode_tracer
                    combo.addItem(u"x%d(t)" % (i + 1))
                    combo.addItem(u"y%d(t)" % (i + 1))
                    combo.addItem(u"v%d(t)" % (i + 1))

                self.dbg.p(3, "origine %s, ref %s" % (str(origine), str(ref)))
            else :
                self.statusBar().show()
        except ZeroDivisionError:
            self.dbg.p(1, "ERROR : ZeroDivisionError in Self.tracer_trajectoires")
        self.label_trajectoire.reDraw()


    def tracer_courbe(self, itemChoisi):
        """
        trace une courbe
        @param itemChoisi est un numéro d'item dans la liste des
        courbes qu'on peut tracer ; c'est trop lié à l'implémentation :
        à rendre plus propre si possible !!!!
        """
        self.dbg.p(1, "rentre dans 'tracer_courbe'")
        if not self.ui.comboBox_mode_tracer.isEnabled():
            return
        
        # try:
        self.ui.comboBox_mode_tracer.setCurrentIndex(0)
        if itemChoisi <= 0: return  # c'est rien du tout.
        numero = (itemChoisi - 1) // 3 ## force le type entier !
        typeDeCourbe = ("x", "y", "v")[(itemChoisi - 1) % 3]
        titre = (_translate("pymecavideo", "Evolution de l'abscisse du point {0}", None).format(numero + 1),
                 _translate("pymecavideo", "Evolution de l'ordonnée du point {0}", None).format(numero + 1),
                 _translate("pymecavideo", "Evolution de la vitesse du point {0}", None).format(numero + 1))[
            (itemChoisi - 1) % 3]
        abscisse = []
        ordonnee = []
        t = 0
        ancienPoint = None
        ref = self.ui.comboBox_referentiel.currentText().split(" ")[-1]
        for i in self.points.keys():
            if ref == "camera":
                p = self.pointEnMetre(self.points[i][1 + numero])
            else:
                ref = int(ref)
                p = self.pointEnMetre(self.points[i][1 + numero]) - self.pointEnMetre(self.points[i][ref])
            if typeDeCourbe == "x": ordonnee.append(p.x())
            if typeDeCourbe == "y": ordonnee.append(p.y())
            if typeDeCourbe == "v":
                if ancienPoint != None:
                    abscisse.append(t)
                    v = (p - ancienPoint).norme() / self.deltaT
                    ordonnee.append(v)
            else:
                abscisse.append(t)
            t += self.deltaT
            ancienPoint = p
        # les abscisses et les ordonnées sont prêtes
        labelAbscisse = "t (s)"
        if typeDeCourbe != "v":
            labelOrdonnee = typeDeCourbe + " (m)"
        else:
            labelOrdonnee = typeDeCourbe + " (m/s)"
        
        #TODO source de bug selon la PATH de python. A tester sous windows.
        if sys.platform == "win32" : 
            python_exe = """python.exe"""
        else : 
            python_exe = """python3"""
        cmd=str("""{0} pgraph.py "{1}" "{2}" "{3}" """.format(python_exe,
            titre, labelAbscisse, labelOrdonnee))
        xy ="\n".join(["{0} {1}". format(abscisse[i], ordonnee[i]) for i in range(len(abscisse))])
        thread=plotThread(cmd, xy)
        thread.daemon=True
        thread.start()
        return

    def affiche_point_attendu(self, n):
        """
        Renseigne sur le numéro du point attendu
        affecte la ligne de statut et la ligne sous le zoom
        """
        self.dbg.p(1, "rentre dans 'affiche_point_attendu'")
        self.dbg.p(1, "Point n° %i"%n)

        self.mets_a_jour_label_infos(
            _translate("pymecavideo", "Pointage des positions : cliquer sur le point N° {0}", None).format(n+1))

    def clic_sur_label_video(self, liste_points=None, interactif=True):
        self.dbg.p(1, "rentre dans 'clic_sur_label_video'")
        self.lance_capture = True 
        
        ### on fait des marques pour les points déjà visités
        etiquette = "@abcdefghijklmnopqrstuvwxyz"[len(self.listePoints)%self.nb_de_points]
        self.point_attendu = len(self.listePoints)%self.nb_de_points
        self.dbg.p(2, "self.point_attendu %s"%self.point_attendu)
        self.affiche_point_attendu(self.point_attendu)
        if self.index_de_l_image <= self.image_max:  ##si on n'atteint pas encore la fin de la vidéo
            self.lance_capture = True
            self.stock_coordonnees_image(ligne=int((len(self.listePoints)-1)/self.nb_de_points))
                
            if interactif:
                self.modifie = True
            self.clic_sur_label_video_ajuste_ui(self.point_attendu)

        if self.index_de_l_image > self.image_max:
            
            self.lance_capture = False
            self.mets_a_jour_label_infos(_translate("pymecavideo", "Vous avez atteint la fin de la vidéo", None))
            self.index_de_l_image = self.image_max
        self.nb_clics+=1
        if self.nb_clics==self.nb_de_points : 
            self.nb_clics=0
            self.index_de_l_image += 1
            self.affiche_image()
    def enableDefaire(self, value):
        """
        Contrôle la possibilité de défaire un clic
        @param value booléen
        """
        self.dbg.p(1, "rentre dans 'enableDefaire, %s'" % (str(value)))
        self.ui.pushButton_defait.setEnabled(value)
        self.ui.actionDefaire.setEnabled(value)

        ##permet de remettre l'interface à zéro
        if not value:
            # self.init_capture()
            self.ui.horizontalSlider.setEnabled(True)
            self.ui.spinBox_image.setEnabled(True)

    def enableRefaire(self, value):
        """
        Contrôle la possibilité de refaire un clic
        @param value booléen
        """
        self.dbg.p(1, "rentre dans 'enableRefaire, %s'" %(value))
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
                
                len(self.listePoints), self.nb_de_points-len(self.listePoints)%self.nb_de_points))
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

        Le calcul du rang du point se déduit de la longueur de
        self.listePoints.
        @param point un point à enregistrer
        @param index un numéro d'image. S'il est indéfini (par défaut), il
        est remplacé par self.index_de_l_image.
        """
        if index:
            i=index
        else:
            i=self.index_de_l_image
        nieme=len(self.listePoints)%self.nb_de_points
        self.listePoints.append([i,nieme,point])
        return
    
    def stock_coordonnees_image(self, ligne,  interactif=True, index_image=False):
        """
        place les données dans le tableau, rempli les dictionnaires de pixels
        @param ligne le numérode la ligne où placer les données (commence à 0)
        @param interactif vrai s'il faut rafraîchir tout de suite l'interface utilisateur.
        """
        self.dbg.p(1, "rentre dans 'stock_coordonnees_image'")
        if index_image==False:
            # l'index est sur la dernière image traitée
            index_image = self.listePoints[-1][0]
        t = "%4f" % ((index_image - self.premiere_image) * self.deltaT)

        #construction de l'ensemble des points pour l'image actuelle
        listePointsCliquesParImage = []
        for point in self.listePoints:
            if point[0]==index_image :
                listePointsCliquesParImage.append(point[2])
        self.points[ligne] = [t] + listePointsCliquesParImage

        # rentre le temps dans la première colonne
        self.ui.tableWidget.insertRow(ligne)
        self.ui.tableWidget.setItem(ligne, 0, QTableWidgetItem(t))

        i = 0
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

            try:
                pm = self.pointEnMetre(point)
            except ZeroDivisionError:
                pm = point

            self.ui.tableWidget.setItem(ligne, i + 1, QTableWidgetItem(str(pm.x())))
            self.ui.tableWidget.setItem(ligne, i + 2, QTableWidgetItem(str(pm.y())))
            i += 2
        if interactif:
            self.ui.tableWidget.show()
        # enlève la ligne supplémentaire, une fois qu'une ligne a été remplie
        if ligne == 0:
            self.ui.tableWidget.removeRow(1)

    def transforme_index_en_temps(self, index):
        self.dbg.p(1, "rentre dans 'transforme_index_en_temps'")
        return float(self.deltaT * (index))

    def affiche_image_spinbox(self):
        self.dbg.p(1, "rentre dans 'affiche_image_spinbox'")

        if self.lance_capture:
            if self.ui.spinBox_image.value() < self.index_de_l_image:
                #self.ui.spinBox_image.setValue(self.index_de_l_image)
                #si le point est sur une image, on efface le point
                if self.ui.spinBox_image.value()==self.listePoints[len(self.listePoints)-1][0]:
                    for i in range(self.nb_de_points):
                        self.efface_point_precedent()
                

        self.index_de_l_image = self.ui.spinBox_image.value()
        try : 
            self.affiche_image()
        except : 
            pass

    def affiche_image(self):

        self.dbg.p(1, "rentre dans 'affiche_image'" + ' ' + str(self.index_de_l_image) + ' ' + str(self.image_max))

        if self.index_de_l_image <= self.image_max:
            self.index_avant = self.index_de_l_image
            self.dbg.p(1, "affiche_image " + "self.index_de_l_image <= self.image_max")
            ok, self.image_opencv = self.extract_image(self.index_de_l_image) #2ms
            
            self.imageExtraite = toQImage(self.image_opencv)
            self.dbg.p(2, "Image extraite : largeur : %s, hauteur %s: "%(self.imageExtraite.width(), self.imageExtraite.height()))
            if self.largeur==0 : 
                self.largeur = self.imageExtraite.width()
                self.hauteur = self.imageExtraite.height()
                self.largeurAvant = self.largeur
                self.hauteurAvant = self.hauteur
                           
            if hasattr(self, "label_video"):
                self.afficheJusteImage()  #4 ms

            if self.ui.horizontalSlider.value() != self.index_de_l_image:
                self.dbg.p(1, "affiche_image " + "horizontal")
                self.ui.horizontalSlider.setValue(self.index_de_l_image) 
                self.ui.spinBox_image.setValue(self.index_de_l_image) #0.01 ms
        elif self.index_de_l_image > self.image_max:
            self.index_de_l_image = self.image_max
            self.lance_capture = False

    def afficheJusteImage(self):
        self.dbg.p(1, "Rentre dans 'AffichejusteImage'" )
        self.imageAffichee = self.imageExtraite.scaled(self.largeur, self.hauteur, Qt.KeepAspectRatio) #4-6 ms
        self.label_video.setMouseTracking(True)
        self.label_video.setPixmap(QPixmap.fromImage(self.imageAffichee))
        self.label_video.met_a_jour_crop()


    def recommence_echelle(self):
        self.dbg.p(1, "rentre dans 'recommence_echelle'")
        self.ui.tabWidget.setCurrentIndex(0)
        self.echelle_image = echelle()

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
        #self.enableRefaire(0)

    def demande_echelle(self):
        """
        demande l'échelle interactivement
        """
        self.dbg.p(1, "rentre dans 'demande_echelle'")
        echelle_result_raw = QInputDialog.getText(None,
                                                  _translate("pymecavideo", "Définir une échelle", None),
                                                  _translate("pymecavideo",
                                                             "Quelle est la longueur en mètre de votre étalon sur l'image ?",
                                                             None),
                                                  QLineEdit.Normal, u"1.0")
        if echelle_result_raw[1] == False:
            return None
        try:
            echelle_result = [float(echelle_result_raw[0].replace(",", ".")), echelle_result_raw[1]]

            if echelle_result[0] <= 0 or echelle_result[1] == False:
                self.mets_a_jour_label_infos(_translate("pymecavideo", " Merci d'indiquer une échelle valable", None))
            else:
                self.echelle_image.etalonneReel(echelle_result[0])

                self.job = Label_Echelle(self.label_video, self)
                self.job.setPixmap(QPixmap(toQImage(self.image_opencv)))
                self.job.show()
                self.change_axe_ou_origine()
            

        except ValueError:
            self.mets_a_jour_label_infos(_translate("pymecavideo", " Merci d'indiquer une échelle valable", None))
            self.demande_echelle()

    def calculeLesVitesses(self):
        """à partir des sets de points, renvoie les vitesses selon l'axe X, selon l'axe Y et les normes des vitesses"""
        self.vitesses = {}

    def recalculLesCoordonnees(self):
        """permet de remplir le tableau des coordonnées à la demande. Se produit quand on ouvre un fichier mecavideo ou quan don recommence l'échelle"""
        for i in range(len(self.points)):
            self.ui.tableWidget.insertRow(i)
            self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(self.points[i][0]))
            for j in range(self.nb_de_points):
                p = self.pointEnMetre(self.points[i][j+1])
                self.ui.tableWidget.setItem(i, j*(self.nb_de_points)+1, QTableWidgetItem(str(p.x())))
                self.ui.tableWidget.setItem(i, j*(self.nb_de_points) + 2, QTableWidgetItem(str(p.y())))
        #esthétique : enleve la derniere ligne
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
        except :
            pass
        self.label_echelle_trace = Label_Echelle_Trace(self.label_video, p1, p2)
        
        #on garde les valeurs pour le redimensionnement
        self.dbg.p(2, "Points de l'echelle : p1 : %s, p2 : %s"%(p1, p2))
        self.label_echelle_p1Avant = self.label_echelle_trace.p1
        self.label_echelle_p2Avant = self.label_echelle_trace.p2
        
        self.label_echelle_trace.show()
        #self.stopRedimensionnement.emit()

    def reinitialise_environnement(self):
        self.dbg.p(1, "rentre dans 'reinitialise_environnement'")

    def closeEvent(self, event):
        """
        Un crochet pour y mettre toutes les procédures à faire lors
        de la fermeture de l'application.
        """
        self.dbg.p(1, "rentre dans 'closeEvent'")
        from tempfile import gettempdir
        self.nettoieVideosRecodees()


    def nettoieVideosRecodees(self):
        """
        Retire les vidéos recodées automatiquement
        """
        self.dbg.p(1, "rentre dans 'nettoieVideosRecodees'")

        for fichier in os.listdir(NEWVID_PATH):
            os.remove(os.path.join(NEWVID_PATH, fichier))


    def verifie_donnees_sauvegardees(self):
        self.dbg.p(1, "rentre dans 'verifie_donnees_sauvegardees'")
        if self.modifie:
            retour = QMessageBox.warning(
                self,
                _translate(u"pymecavideo", "Les données seront perdues", None),
                _translate(u"pymecavideo", "Votre travail n'a pas été sauvegardé\nVoulez-vous les sauvegarder ?", None),
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
        #self.reinitialise_tout()
        filename,hints = QFileDialog.getOpenFileName(
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
        renomme_fichier = QMessageBox.warning(self, _translate("pymecavideo", "Nom de fichier non conforme", None), \
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
                
                self.init_image()
                self.init_capture()
                self.ratio = self.determineRatio()
                self.label_video.repaint()
                self.label_video.show()
                self.origine = vecteur(self.largeur/2, self.hauteur/2)
                self.change_axe_ou_origine()
                self.label_video.origine = self.origine
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
        QMessageBox.warning(None, u"Licence", licence_XX, QMessageBox.Ok, QMessageBox.Ok)

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
        self.ration = self.determineRatio()
        self.init_interface()
        self.trajectoire = {}
        self.ui.spinBox_image.setMinimum(1)
        self.defini_barre_avancement()
        self.echelle_image = echelle()
        self.affiche_echelle()
        self.ui.tab_traj.setEnabled(0)
        self.ui.spinBox_image.setEnabled(1)

        self.affiche_image()
        self.reinitialise_environnement()


    def defini_barre_avancement(self):
        """récupère le maximum d'images de la vidéo et défini la spinbox et le slider"""
        self.dbg.p(1, "rentre dans 'defini_barre_avancement'")
        framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos()
        self.dbg.p(3,
                   "In :  'defini_barre_avancement', framerate, self.image_max = %s, %s" % (framerate, self.image_max))
        self.deltaT = float(1.0 / framerate)
        if math.isnan(self.deltaT):
            print ("ERREUR à la lecture de la vidéo, vitesse des trames indéfinie, on suppose 40 trames par seconde")
            self.deltaT=1.0/40
        self.ui.horizontalSlider.setMinimum(1)

        self.ui.horizontalSlider.setMaximum(int(self.image_max))
        self.ui.spinBox_image.setMaximum(int(self.image_max))

        fichier = os.path.join(IMG_PATH, VIDEO + SUFF % 1)
        try:
            os.remove(fichier)
            self.extract_image(1)
            os.remove(fichier)
        except OSError:
            pass

    def extract_image(self, index):
        """
        extrait une image de la video à l'aide d'OpenCV et l'enregistre
        @param video le nom du fichier video
        @param index le numéro de l'image
        @param force permet de forcer l'écriture d'une image
        """
        self.dbg.p(1, "rentre dans 'extract_image' " + 'index : ' + str(index))
        ok, image_opencv = self.cvReader.getImage(index, self.rotation)
        if not ok :
            self.mets_a_jour_label_infos(
            _translate("pymecavideo", "Pymecavideo n'arrive pas à lire l'image", None))
            return False, None
        
        
        self.a_une_image = ok
        return ok, image_opencv
        
    def traiteOptions(self):
        self.dbg.p(1, "rentre dans 'traiteOptions'")
        for opt, val in self.opts:
            if opt in ['-f', '--fichier_mecavideo']:
                if os.path.isfile(val) and os.path.splitext(val)[1] == ".csv":
                    try:
                        self.rouvre(val)
                    except AttributeError:
                        self.dbg.p(1, "Issue in rouvre for this file : attributeerror")

                if os.path.isfile(val) and os.path.splitext(val)[1] == ".avi":
                    self.openTheFile(val)


def usage():
    print (
        "Usage : pymecavideo [-f fichier | --fichier_pymecavideo=fichier] [--maxi] [-d | --debug=verbosityLevel(1-3)] [nom_de_fichier_video.avi]")


def run():
    global app

    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(args, "f:d:", ["fichier_mecavideo=", "debug="])
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


def lanceQtiplot(fichier):
    """
    lanceur pour Qtiplot, dans un thread
    param @fichier le fichier de projet
    """
    os.system("qtiplot %s" % fichier)


def lanceSciDAVis(fichier):
    """
    lanceur pour SciDAVis, dans un thread
    param @fichier le fichier de projet
    """
    os.system("scidavis %s" % fichier)
    return

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
        self.cmd=cmd
        self.xy=dataLines
        return

    def run(self):
        p=subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE)
        p.communicate(self.xy.encode("utf-8"))
        return
    

if __name__ == "__main__":
    run()
