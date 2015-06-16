# -*- coding: utf-8 -*-

licence = {}
licence['en'] = """
    pymecavideo version %s:

    a program to track moving points in a video frameset
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>

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
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>
    
    Ce projet est un logiciel libre : vous pouvez le redistribuer, le modifier selon les terme de la GPL (GNU Public License) dans les termes de la Free Software Foundation concernant la version 3 ou plus de la dite licence.
    
    Ce programme est fait avec l'espoir qu'il sera utile mais SANS AUCUNE GARANTIE. Lisez la licence pour plus de détails.
    
    <http://www.gnu.org/licenses/>.
"""
#
# Le module de gestion des erreurs n'est chargé que si on execute le fichier .exe ou si on est sous Linux
#
import sys, os
# if sys.platform == "win32" or sys.argv[0].endswith(".exe"):
# import Error

from vecteur import vecteur
import time, commands, codecs
import locale, getopt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

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

import qtiplotexport
from subprocess import *
import re

from pgraph import traceur2d

import threading
import platform
import tempfile

from globdef import APP_DATA_PATH, VIDEO, SUFF, VIDEO_PATH, CONF_PATH, IMG_PATH, ICON_PATH, LANG_PATH, \
    DATA_PATH, HELP_PATH, NEWVID_PATH

from detect import filter_picture

_encoding = QApplication.UnicodeUTF8


def _translate(context, text, disambig):
    return QApplication.translate(context, text, disambig, _encoding)


class MonThreadDeCalcul(threading.Thread):
    """Thread permettant le calcul des points automatiquement. Version Python"""

    def __init__(self, parent, motif, image, dossTemp):
        threading.Thread.__init__(self)
        self.parent = parent
        self.parent.dbg.p(1, "rentre dans 'monThreadDeCalcul'")
        self.motif = motif
        self.image = image
        self.dossTemp = dossTemp
        self._stopevent = threading.Event()

    def run(self):
        """
        lance le thread.
        """
        while not self._stopevent.isSet():
            self.parent.picture_detect(self.dossTemp)
            self._stopevent.wait(0.01)
        os.remove(self.dossTemp)

    def stop(self):
        self._stopevent.set()


class MonThreadDeCalculQt(QThread):
    """Thread permettant le calcul des points automatiquement. Version Qt. 20/04/2015 : focntionne mal sous windows"""

    def __init__(self, parent, motif, image):
        QThread.__init__(self)
        self.parent = parent
        self.parent.dbg.p(1, "rentre dans 'monThreadDeCalcul'")
        self.motif = motif
        self.image = image
        self.stopped = False

    def run(self):
        """
        lance le thread.
        stocke les corrdonnées des points trouvés
        Envoi un signal quand terminé.
        """
        while not self.stopped:
            self.parent.picture_detect()

    def stop(self):
        self.stopped = True


class StartQT4(QMainWindow):
    def __init__(self, parent=None, opts=[], args=[]):
        """
        le constructeur reçoit les données principales du logiciel : 
        @param parent le widget parent, None pour une fenêtre principale
        @param opts les options de l'invocation bien rangées en tableau
        @param args les arguments restants après raitement des options
        """

        if "maxi" in str(opts):
            self.mini = False
        else:
            self.mini = True

        ######QT
        QMainWindow.__init__(self)
        QWidget.__init__(self, parent)

        #### Mode plein écran
        self.plein_ecran = False
        QShortcut(QKeySequence(Qt.Key_F11), self, self.basculer_plein_ecran)

        height, width = QDesktopWidget().screenGeometry().height(), QDesktopWidget().screenGeometry().width()

        if height >= 768 and width >= 1024 and self.mini == False:
            # Importation de l'interface ici car l'import de l'interface "mini" écrase l'interface "standard"
            from Ui_pymecavideo import Ui_pymecavideo
        else:
            from Ui_pymecavideo_mini_layout import Ui_pymecavideo

            message = QMessageBox(self)

        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowSystemMenuHint |
                            Qt.WindowMinMaxButtonsHint)

        self.ui = Ui_pymecavideo()
        self.ui.setupUi(self)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)

        self.setSizePolicy(sizePolicy)

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


    # Basculer en mode plein écran / mode fenétré


    def heightForWidth(self):
        return 0.5

    def basculer_plein_ecran(self):
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
        self.myThreads = []
        self.origine = vecteur(320, 240)
        self.auto = False
        self.motif = []
        self.lance_capture = False
        self.modifie = False
        self.points = {}  # dictionnaire des points cliqués, par n d'image.
        self.trajectoire = {}  # dictionnaire des points des trajectoires
        self.pX = {}  # points apparaissant à l'écran, indexés par X
        self.pY = {}  # points apparaissant à l'écran, indexés par Y
        self.index_du_point = 0
        self.echelle_image = echelle()  # objet gérant l'image
        self.nb_image_deja_analysees = 0  # indique le nombre d'images dont on a dejà fait l'étude, ce qui correspond aussi au nombre de lignes dans le tableau.
        self.couleurs = ["red", "blue", "cyan", "magenta", "yellow", "gray",
                         "green"]  # correspond aux couleurs des points de la trajectoire
        self.pointsProvisoires = []  # quand on a plusieurs clics à faire
        self.nb_de_points = 1  # nombre de points suivis
        self.premiere_image = 1  # n° de la première image cliquée
        self.index_de_l_image = 1  # image à afficher

        self.filename = filename
        self.opts = opts
        self.stdout_file = os.path.join(APP_DATA_PATH, "stdout")
        self.exitDecode = False
        self.echelle_faite = False

        self.tousLesClics = listePointee()  # tous les clics faits sur l'image

        self.goCalcul = True  # Booléen vérifiant la disponibilté du thread de calcul
        self.updatePicture = True
        self.premierResize = True  # arrive quand on ouvre la première fois la fenetre
        self.chrono = False

        ######vérification de la présence d'un logiciel connu de capture vidéo dans le path
        # for logiciel in ['qastrocam', 'qastrocam-g2', 'wxastrocapture', 'wxAstroCapture']:
        # if any(os.access(os.path.join(p, logiciel), os.X_OK) for p in os.environ['PATH'].split(os.pathsep)):
        #         self.logiciel_acquisition = logiciel
        #         # self.ui.pushButton_video.setEnabled(1)
        #         break
        # if self.logiciel_acquisition:
        #     # self.ui.pushButton_video.setText(
        #         _translate("pymecavideo", "Lancer %1\n pour capturer une vidéo", None)
        #             .arg(self.logiciel_acquisition)
        #     )
        # else:
        #     self.ui.pushButton_video.setEnabled(0)
        #     self.ui.pushButton_video.hide()


    def init_interface(self, refait=0):
        self.ui.tabWidget.setEnabled(1)
        self.ui.tabWidget.setEnabled(1)
        self.ui.actionDefaire.setEnabled(1)
        self.ui.actionRefaire.setEnabled(1)
        self.ui.actionExemples.setEnabled(1)
        self.cree_tableau()
        try:

            self.label_trajectoire.clear()
        except AttributeError:
            self.label_trajectoire = Label_Trajectoire(self.ui.label_3, self)
            self.label_trajectoire.show()

        self.update()

        self.emit(SIGNAL('OKRedimensionnement'))
        self.ui.horizontalSlider.setEnabled(0)

        # self.ui.pushButton_video.setEnabled(0)

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

        self.ui.pushButton_video.setEnabled(0)
        self.ui.pushButton_video.hide()


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
            self.ui.exportCombo.setItemText(index, _translate("pymecavideo", "NON DISPO : %1", None).arg(text))
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

    def reinitialise_tout(self, echelle_image=None, nb_de_points=None, tousLesClics=None, index_point_actuel=None):
        """
        Réinitialise l'interface de saisie, mais pas l'échelle. On
        peut quand même passer quelques paramètres à conserver, ce qui
        permet le défaire/refaire :
        @param echelle_image évite de ressaisir l'échelle de l'image
        @param nb_de_points évite de ressaisir le nombre de points à suivre
        @param tousLesClics permet de conserver une liste de points à refaire
        @param index_point_actuel permet de réinitialiser à partir de l'image de départ.
        """

        self.dbg.p(1, "rentre dans 'reinitialise_tout'")
        self.dbg.p(2,
                   "Dans reinitialise_tout: echelle_image=%s, nb_de_points=%s, tousLesClics=%s,index_point_actuel=%s" % (
                       echelle_image, nb_de_points, tousLesClics, index_point_actuel))
        self.montre_vitesses = False
        self.label_trajectoire.update()
        self.ui.label.update()
        self.label_video.update()

        #############
        # si il existe un point actuel, cela signifie qu'on réinitialise
        # tout mais qu'on doit garder la position de départ. Cas quand
        # on revient en arrière d'un cran ou que l'on refait le point.
        #############

        if index_point_actuel:
            self.init_interface(refait=1)
            ############ permet de récupérer les 2 valeurs souhaitées

            ############
            self.init_variables(None, filename=self.filename)
            self.index_de_l_image = index_point_actuel

            self.premiere_image = index_point_actuel
            self.ui.spinBox_image.setValue(self.index_de_l_image)
        else:
            self.init_interface()
            self.init_variables(None, filename=self.filename)
        if echelle_image:
            self.echelle_image = echelle_image
            self.feedbackEchelle(self.echelle_image.p1, self.echelle_image.p2)
        else:  # destroy scale
            try:
                self.label_echelle_trace.hide()
                del self.label_echelle_trace
            except AttributeError:
                pass  # quand on demande un effacement tout au début. Comme par exemple, ouvrir les exmples.

        if nb_de_points:
            self.nb_de_points = nb_de_points
        if tousLesClics != None and tousLesClics.count():
            self.tousLesClics = tousLesClics


    def reinitialise_capture(self):
        """
        Efface toutes les données de la capture en cours et prépare une nouvelle
        session de capture.
        """
        self.dbg.p(1, "rentre dans 'reinitialise_capture'")
        self.montre_vitesses = False

        self.label_trajectoire.update()
        self.ui.label.update()
        self.label_video.update()
        self.label_video.setCursor(Qt.ArrowCursor)
        self.init_variables(None, filename=self.filename)
        self.affiche_image()

        self.echelle_image = echelle()
        self.affiche_echelle()
        self.ui.horizontalSlider.setEnabled(1)
        self.ui.spinBox_image.setEnabled(1)
        self.ui.spinBox_image.setValue(1)
        self.enableDefaire(False)
        self.enableRefaire(False)
        self.affiche_nb_points(1)
        self.ui.Bouton_lance_capture.setEnabled(0)
        self.defixeLesDimensions()

        ### Réactiver checkBox_avancees après réinitialisation ###
        self.ui.pushButton_origine.setEnabled(1)
        self.ui.checkBox_abscisses.setEnabled(1)
        self.ui.checkBox_ordonnees.setEnabled(1)
        self.ui.checkBox_auto.setEnabled(1)
        self.ui.checkBox_abscisses.setCheckState(Qt.Unchecked)
        self.ui.checkBox_ordonnees.setCheckState(Qt.Unchecked)
        self.ui.checkBox_auto.setCheckState(Qt.Unchecked)
        self.determineHauteurLargeur()

        if self.ui.tableWidget:
            self.ui.tableWidget.clear()

    def ui_connections(self):
        """connecte les signaux de QT"""
        self.dbg.p(1, "rentre dans 'ui_connections'")
        QObject.connect(self.ui.actionOuvrir_un_fichier, SIGNAL("triggered()"), self.openfile)
        QObject.connect(self.ui.actionExemples, SIGNAL("triggered()"), self.openexample)
        QObject.connect(self.ui.action_propos, SIGNAL("triggered()"), self.propos)
        QObject.connect(self.ui.actionAide, SIGNAL("triggered()"), self.aide)
        # QObject.connect(self.ui.actionPreferences,SIGNAL("triggered()"), self.prefs.setFromDialog)
        QObject.connect(self.ui.actionDefaire, SIGNAL("triggered()"), self.efface_point_precedent)
        QObject.connect(self.ui.actionRefaire, SIGNAL("triggered()"), self.refait_point_suivant)
        QObject.connect(self.ui.actionQuitter, SIGNAL("triggered()"), self.close)
        QObject.connect(self.ui.actionSaveData, SIGNAL("triggered()"), self.enregistre_ui)
        QObject.connect(self.ui.actionCopier_dans_le_presse_papier, SIGNAL("triggered()"), self.presse_papier)
        QObject.connect(self.ui.actionOpenOffice_org_Calc, SIGNAL("triggered()"), self.oooCalc)
        QObject.connect(self.ui.actionQtiplot, SIGNAL("triggered()"), self.qtiplot)
        QObject.connect(self.ui.actionScidavis, SIGNAL("triggered()"), self.scidavis)
        QObject.connect(self.ui.actionRouvrirMecavideo, SIGNAL("triggered()"), self.rouvre_ui)
        QObject.connect(self.ui.Bouton_Echelle, SIGNAL("clicked()"), self.demande_echelle)
        QObject.connect(self.ui.horizontalSlider, SIGNAL("sliderReleased()"), self.affiche_image_slider)
        QObject.connect(self.ui.horizontalSlider, SIGNAL("valueChanged(int)"), self.affiche_image_slider_move)
        QObject.connect(self.ui.spinBox_image, SIGNAL("valueChanged(int)"), self.affiche_image_spinbox)
        QObject.connect(self.ui.Bouton_lance_capture, SIGNAL("clicked()"), self.debut_capture)
        QObject.connect(self, SIGNAL("clic_sur_video()"), self.clic_sur_label_video)
        QObject.connect(self.ui.comboBox_referentiel, SIGNAL("currentIndexChanged (int)"), self.tracer_trajectoires)
        QObject.connect(self.ui.comboBox_mode_tracer, SIGNAL("currentIndexChanged (int)"), self.tracer_courbe)
        QObject.connect(self.ui.tabWidget, SIGNAL("currentChanged (int)"), self.tracer_trajectoires)

        QObject.connect(self.ui.checkBoxScale, SIGNAL("currentIndexChanged(int)"), self.enableSpeed)
        QObject.connect(self.ui.checkBoxVectorSpeed, SIGNAL("stateChanged(int)"), self.enableSpeed)

        QObject.connect(self.ui.radioButtonSpeedEveryWhere, SIGNAL("clicked()"), self.enableSpeed)
        QObject.connect(self.ui.radioButtonNearMouse, SIGNAL("clicked()"), self.enableSpeed)
        QObject.connect(self.ui.button_video, SIGNAL("clicked()"), self.video)
        QObject.connect(self.ui.pushButton_select_all_table, SIGNAL("clicked()"), self.presse_papier)
        QObject.connect(self.ui.pushButtonChrono, SIGNAL("clicked()"), self.chronoPhoto)
        QObject.connect(self.ui.pushButton_reinit, SIGNAL("clicked()"), self.reinitialise_capture)
        QObject.connect(self.ui.pushButton_defait, SIGNAL("clicked()"), self.efface_point_precedent)
        QObject.connect(self.ui.pushButton_refait, SIGNAL("clicked()"), self.refait_point_suivant)
        QObject.connect(self.ui.pushButton_origine, SIGNAL("clicked()"), self.choisi_nouvelle_origine)

        QObject.connect(self.ui.checkBox_abscisses, SIGNAL("stateChanged(int)"), self.change_sens_X)
        QObject.connect(self.ui.checkBox_ordonnees, SIGNAL("stateChanged(int)"), self.change_sens_Y)
        QObject.connect(self, SIGNAL('change_axe_origine()'), self.change_axe_ou_origine)
        QObject.connect(self, SIGNAL('selection_done()'), self.picture_detect)
        QObject.connect(self, SIGNAL('selection_motif_done()'), self.storeMotif)
        QObject.connect(self, SIGNAL('stopRedimensionnement()'), self.fixeLesDimensions)
        QObject.connect(self, SIGNAL('OKRedimensionnement()'), self.defixeLesDimensions)
        QObject.connect(self, SIGNAL('redimensionneSignal()'), self.redimensionne)

        QObject.connect(self.ui.pushButtonEnregistreChrono, SIGNAL('clicked()'), self.enregistreChrono)
        QObject.connect(self, SIGNAL('stopCalculs()'), self.stopComputing)
        QObject.connect(self.ui.pushButton_video, SIGNAL('clicked()'), self.stopComputing)
        QObject.connect(self, SIGNAL('updateProgressBar()'), self.updatePB)

        QObject.connect(self.ui.exportCombo, SIGNAL("currentIndexChanged(int)"), self.export)

        QObject.connect(self.ui.pushButton_nvl_echelle, SIGNAL("clicked()"), self.recommence_echelle)

    def enregistreChrono(self):
        # self.label_trajectoire.render()
        self.pixmapChrono = QPixmap(self.label_trajectoire.size())
        self.label_trajectoire.render(self.pixmapChrono)
        dir_ = self._dir("home")
        fichier = QFileDialog.getSaveFileName(self,
                                              _translate("pymecavideo", "Enregistrer la chronophotographie", None),
                                              dir_,
                                              _translate("pymecavideo", "fichiers images(*.png *.jpg)", None))
        self.pixmapChrono.save(fichier)

    def chronoPhoto(self):
        self.dbg.p(1, "rentre dans 'chronoPhoto'")
        ##ajoute la première image utilisée pour le pointage sur le fond du label
        imfilename = os.path.join(IMG_PATH, VIDEO + SUFF % self.premiere_image)
        self.chrono = True
        self.imageChrono = QImage(imfilename).scaled(self.largeur, self.hauteur, Qt.KeepAspectRatio)
        self.label_trajectoire.setPixmap(QPixmap.fromImage(self.imageChrono))
        self.ui.pushButtonEnregistreChrono.setVisible(1)


    def fixeLesDimensions(self):
        self.setMinimumWidth(self.width())
        self.setMaximumWidth(self.width())

    def defixeLesDimensions(self):
        self.setMinimumWidth(833)
        self.setMaximumWidth(16000000)

    def updatePB(self):
        self.qmsgboxencode.updateProgressBar()

    def enableSpeed(self):
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
            self.ui.checkBoxScale.insertItem(0, "1")

            self.ui.radioButtonNearMouse.hide()
            self.ui.radioButtonSpeedEveryWhere.hide()
            self.label_trajectoire.reDraw()

    def storeMotif(self):
        self.dbg.p(1, "rentre dans 'storeMotif'")
        if len(self.motif) == self.nb_de_points:
            self.dbg.p(3, "selection des motifs finie")
            self.label_auto.hide()
            self.label_auto.close()
            self.indexMotif = 0
            # self.picture_detect()
            self.ui.pushButton_video.setText("STOP CALCULS")
            self.ui.pushButton_video.setEnabled(1)
            self.ui.pushButton_video.show()
            # self.ui.pushButton_video.setFocus()
            self.label_video.setEnabled(0)
            self.goCalcul = True

            # TODO : tests avec les différents mode de threading
            ##Qthread (fonctionne mal)
            # self.monThread = MonThreadDeCalculQt(self, self.motif[self.indexMotif], self.imageAffichee)

            # Python
            dossTemp = tempfile.NamedTemporaryFile(delete=False).name
            self.monThread = MonThreadDeCalcul(self, self.motif[self.indexMotif], self.imageAffichee, dossTemp)
            self.monThread.start()


    def picture_detect(self, dossTemp):
        """
        Est lancée lors de la détection automatique des points. Gère l'ajout des thread de calcul.
        self.myThreads : tableau contenant les thread
        self.motifs : tableau des motifs

        """
        self.dbg.p(1, "rentre dans 'picture_detect'")
        self.dbg.p(3, "début 'picture_detect'" + str(self.indexMotif))
        if self.index_de_l_image <= self.image_max:
            self.pointsFound = []
            if self.indexMotif <= len(self.motif) - 1:
                self.dbg.p(1, "'picture_detect' : While")
                # self.pointTrouve = filter_picture(self.motif[self.indexMotif], self.imageAffichee)
                self.pointTrouve = filter_picture(self.motif, self.indexMotif, self.imageAffichee, dossTemp)
                self.dbg.p(3, "Point Trouve dans mon Thread : " + str(self.pointTrouve))
                self.onePointFind()

                self.indexMotif += 1
            else:
                self.indexMotif = 0

        if self.index_de_l_image == self.image_max:
            if self.indexMotif == 0 and not self.goCalcul:  # dernier passage
                self.emit(SIGNAL('stopCalculs()'))
            elif self.indexMotif == 0 and self.goCalcul:  # premier passage, premier calcul de la dernière image
                self.goCalcul = False

    def stopComputing(self):
        self.dbg.p(1, "rentre dans 'stopComputing'")
        self.monThread.stop()
        del self.monThread
        self.label_video.setEnabled(1)
        self.ui.pushButton_video.setEnabled(0)
        self.ui.pushButton_video.hide()

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
                QObject.connect(self.timer, SIGNAL("timeout()"), self, SLOT(self.readStdout()))
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
        # self.recommence_echelle()
        self.dbg.p(1, "rentre dans 'refait_echelle'")
        self.cree_tableau()
        index = 0
        for point in self.tousLesClics:
            self.stock_coordonnees_image(index, point)
            index += 1

    def choisi_nouvelle_origine(self):
        self.dbg.p(1, "rentre dans 'choisi_nouvelle_origine'")
        nvl_origine = QMessageBox.information(self, QString("NOUVELLE ORIGINE"), \
                                              QString(
                                                  "Choisissez, en cliquant sur la vidéo le point qui sera la nouvelle origine"))

        label = Label_Origine(parent=self.ui.label, app=self)
        label.show()

    def change_axe_ou_origine(self):
        """mets à jour le tableau de données"""
        self.dbg.p(1, "rentre dans 'change_axe_ou_origine'")
        # repaint axes and define origine
        self.label_trajectoire.origine_mvt = self.origine
        self.label_trajectoire.update()

        self.label_video.origine = self.origine
        self.label_video.update()
        self.emit(SIGNAL('stopRedimensionnement()'))

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
        self.emit(SIGNAL('change_axe_origine()'))

    def change_sens_Y(self):
        self.dbg.p(1, "rentre dans 'change_sens_Y'")
        if self.ui.checkBox_ordonnees.isChecked():
            self.sens_Y = -1
        else:
            self.sens_Y = 1
        self.emit(SIGNAL('change_axe_origine()'))

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
            if option == "Oo.o Calc":
                self.oooCalc()
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

        home = unicode(QDesktopServices.storageLocation(8), 'iso-8859-1')

        if lequel == "home":
            return home
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
                dd = StartQT4._dir(str(d))
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
        dir_ = self._dir("home")
        fichier = QFileDialog.getOpenFileName(self, _translate("pymecavideo", "Ouvrir un projet Pymecavideo", None),
                                              dir_,
                                              _translate("pymecavideo", "fichiers pymecavideo(*.csv)", None))

        if fichier != "":
            self.rouvre(fichier)

    def loads(self, s):
        self.dbg.p(1, "rentre dans 'loads'")
        s = s[1:-2].replace("\n#", "\n")

        self.filename, self.sens_X, self.sens_Y, self.origine, \
        self.premiere_image, self.echelle_image.longueur_reelle_etalon \
            , point, self.deltaT, self.nb_de_points = s.splitlines()[1:-1]
        self.filename = self.filename.split('=')[-1][1:]
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.filename))
        self.sens_X = int(self.sens_X.split()[-1])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.sens_X))
        self.sens_Y = int(self.sens_Y.split()[-1])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.sens_Y))
        self.origine = vecteur(self.origine.split()[-2][1:-1], self.origine.split()[-1][:-1])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.origine))
        self.premiere_image = int(self.premiere_image.split()[-1])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.filename))
        self.echelle_image.longueur_reelle_etalon = float(self.echelle_image.longueur_reelle_etalon.split()[-2])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.filename))
        self.echelle_image.p1, self.echelle_image.p2 = vecteur(point.split()[-4][1:-1], point.split()[-3][:-1]) \
            , vecteur(point.split()[-2][1:-1], point.split()[-1][:-1])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.filename))
        self.deltaT = float(self.deltaT.split()[-1])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.filename))
        self.nb_de_points = int(self.nb_de_points.split()[-2])
        self.dbg.p(3, "rentre dans 'loads' %s" % (self.filename))

        self.init_cvReader()

    def rouvre(self, fichier):
        """Open a mecavideo file"""
        self.dbg.p(1, "rentre dans 'rouvre'")

        lignes = open(fichier, "r").readlines()
        i = 0
        self.points = {}
        dd = ""
        for l in lignes:
            if l[0] == "#":
                dd += l
        self.echelle_image = echelle()  # on réinitialise l'échelle
        self.loads(dd)  # on récupère les données importantes
        self.check_uncheck_direction_axes()  # check or uncheck axes Checkboxes
        self.init_interface()
        self.change_axe_ou_origine()
        for l in lignes:
            if l[0] == "#":
                pass
            else:
                l = l.strip('\t\n')
                d = l.split("\t")
                t = "%4f" % (float(d[0].replace(",", ".")))
                self.ui.tableWidget.insertRow(i)
                self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(t))
                self.points[i] = [t]

                for j in range(1, len(d), 2):
                    self.points[i].append(
                        vecteur(float(d[j].replace(",", ".")) * self.echelle_image.longueur_reelle_etalon \
                                + self.origine.x(), self.origine.y() - float(
                            d[j + 1].replace(",", ".")) * self.echelle_image.longueur_reelle_etalon))
                    self.ui.tableWidget.setItem(i, j, QTableWidgetItem(str(float(d[j].replace(",", ".")))))
                    self.ui.tableWidget.setItem(i, j + 1, QTableWidgetItem(str(float(d[j + 1].replace(",", ".")))))
                i += 1

        # puis on trace le segment entre les points cliqués pour l'échelle
        self.feedbackEchelle(self.echelle_image.p1, self.echelle_image.p2)
        framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos()

        self.determineHauteurLargeur()

        self.defini_barre_avancement()
        self.affiche_echelle()  # on met à jour le widget d'échelle
        n = len(self.points.keys())
        self.nb_image_deja_analysees = n
        self.ui.horizontalSlider.setValue(n + self.premiere_image)
        self.ui.spinBox_image.setValue(n + self.premiere_image)
        self.affiche_nb_points(self.nb_de_points)
        self.enableDefaire(True)
        self.enableRefaire(False)

        # On regénère la liste self.tousLesClics
        for i in self.points.keys():
            self.tousLesClics.append(self.points[i][1:])
        self.affiche_image()  # on affiche l'image
        self.debut_capture(departManuel=False)

        self.ui.tableWidget.show()

        # On met à jour les préférences
        self.prefs.lastVideo = self.filename
        self.prefs.videoDir = os.path.dirname(self.filename)
        self.prefs.save()


    def determineHauteurLargeur(self, largeur=None):
        ##si le film est trop large on le fixe vers les 3/4 de l'écran
        self.dbg.p(1, "rentre dans 'determineHauteurLargeur'")
        if self.premierResize:

            if self.cvReader is None:
                self.image_max, self.largeurFilm, self.hauteurFilm = 10, 320, 200
            else:
                framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos()

                # sizeEcran = QDesktopWidget().screenGeometry()
            #        posVideo = self.ui.label.mapTo(self, QPoint(0,0))

        ratioFilm = self.largeurFilm / self.hauteurFilm
        ratioLabel = 1.0 * self.ui.label.width() / self.ui.label.height()

        if ratioFilm > ratioLabel:
            self.largeur = 1.0 * (self.ui.label.width())
            self.hauteur = int(self.largeur / ratioFilm)
        else:
            self.hauteur = 1.0 * (self.ui.label.height())
            self.largeur = int(self.hauteur * ratioFilm)

        self.origine = vecteur(int(self.largeur / 2), int(self.hauteur / 2))
        try:
            self.label_video.origine = self.origine
        except AttributeError:
            pass  # premier passage


            # rapportLH = float(self.largeurFilm) / self.hauteurFilm
        #        if self.largeurFilm > sizeEcran.width() * 3.0 / 4.0:
        #            self.dbg.p(2, 'film trop grand')
        #            self.largeur = int(sizeEcran.width() * 3.0 / 4.0)
        #        elif self.largeurFilm < 640:
        #            self.dbg.p(2, 'film trop petit')
        #            self.largeur = 640
        #        else:
        #            self.largeur = self.largeurFilm
        #        try:
        #            if largeur:
        #                self.largeur = largeur - 190
        #                self.hauteur = int(self.largeur / rapportLH)
        #                self.origine = vecteur(int(self.largeur / 2), int(self.hauteur / 2))
        #                self.label_video.origine = self.origine
        #            self.hauteur = int(self.largeur / rapportLH)
        #
        #        except AttributeError:
        #            pass  # premier passage

    def resizeEvent(self, event):
        self.dbg.p(1, "rentre dans resizeEvent")
        self.setFixedHeight(self.width() * 0.75)
        self.emit(SIGNAL('redimensionneSignal()'))
        QApplication.instance().processEvents()


    # def showEvent(self, event):
    # self.emit(SIGNAL('redimensionneSignal()'))

    def redimensionne(self, premier=False):
        """
        redimensionne la fenêtre principale
        @param premier booléen, force le redimensionnement comme la première fois s'il est
        vrai ; faux par défaut.
        """
        self.dbg.p(1, "rentre dans 'redimensionne'")
        self.layout()
        if self.premierResize or premier:
            self.determineHauteurLargeur()
            self.premierResize = False
        else:
            self.determineHauteurLargeur(self.width())

        """
        OBSOLÈTE : la méthode de calcul de hauteur fait perdre la ligne de statut
        =========================================================================
        if sys.platform != "win32":
            posVideo = self.ui.label.mapTo(self, QPoint(0,0))
            #rect = self.geometry()
            #self.setGeometry(rect.x(), rect.y(), self.largeur + 190, self.hauteur + 130)
            #self.setFixedHeight(self.hauteur + posVideo.y())
        =========================================================================
        """

        if hasattr(self, 'label_video'):
            self.label_video.maj()
            self.label_trajectoire.maj()
            self.afficheJusteImage()


    def entete_fichier(self, msg=""):
        self.dbg.p(1, "rentre dans 'entete_fichier'")
        result = u"""#pymecavideo
#video = %s
#sens axe des X = %d
#sens axe des Y = %d
#origine de pointage = %s
#index de depart = %d
#echelle %5f m pour %5f pixel
#echelle pointee en %s %s
#intervalle de temps : %f
#suivi de %s point(s)
#%s
#""" % (self.filename, self.sens_X, self.sens_Y, self.origine, self.premiere_image \
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
            fichier = unicode(fichier)
            fichier = fichier.encode('utf8')
            file = codecs.open(fichier, 'w', 'utf8')
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
            fichier = QFileDialog.getSaveFileName(self, "FileDialog", "data.csv", "*.csv *.txt *.asc *.dat")

            self.enregistre(fichier)

    def debut_capture(self, departManuel=True):
        self.dbg.p(1, "rentre dans 'debut_capture'")
        """
        permet de mettre en place le nombre de point à acquérir
        @param departManuel vrai si on a fixé à la main la première image.

        """

        try:
            self.origine_trace.hide()
            del self.origine_trace
        except:
            pass

        self.label_video.setFocus()
        self.label_video.show()
        self.label_video.activateWindow()
        self.label_video.setVisible(True)

        self.label_echelle_trace.lower()  # nécessaire sinon, label_video n'est pas actif.

        self.nb_de_points = self.ui.spinBox_nb_de_points.value()
        self.affiche_nb_points(False)
        self.affiche_lance_capture(False)
        self.ui.horizontalSlider.setEnabled(0)
        self.ui.spinBox_image.setEnabled(0)

        self.arretAuto = False

        if departManuel == True:  # si on a mis la première image à la main
            self.premiere_image = self.ui.horizontalSlider.value()
        self.affiche_point_attendu(1)
        self.lance_capture = True
        self.label_video.setCursor(Qt.CrossCursor)
        self.ui.tab_traj.setEnabled(1)
        self.ui.actionSaveData.setEnabled(1)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(1)
        self.ui.comboBox_referentiel.setEnabled(1)
        self.ui.pushButton_select_all_table.setEnabled(1)

        self.ui.comboBox_referentiel.clear()
        self.ui.comboBox_referentiel.insertItem(-1, "camera")
        for i in range(self.nb_de_points):
            self.ui.comboBox_referentiel.insertItem(-1, _translate("pymecavideo", "point N° %1", None).arg(str(i + 1)))
        self.cree_tableau()

        self.ui.pushButton_origine.setEnabled(0)
        self.ui.checkBox_abscisses.setEnabled(0)
        self.ui.checkBox_ordonnees.setEnabled(0)
        self.ui.checkBox_auto.setEnabled(0)

        #######automatic capture
        if self.ui.checkBox_auto.isChecked():
            self.auto = True
            reponse = QMessageBox.warning(None, "Capture Automatique",
                                          _translate("pymecavideo", """\
Veuillez sélectionner un cadre autour de(s) l'objet(s) que vous voulez suivre.
Vous pouvez arrêter à tous moments la capture en appuyant sur le bouton""",
                                                     None),
                                          QMessageBox.Ok, QMessageBox.Ok)

            self.label_auto = Label_Auto(self.label_video, self)  # in this label, motif(s) are defined.
            self.label_auto.show()


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
            x = "X%d (m)" % (1 + i)
            y = "Y%d (m)" % (1 + i)
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
        self.tousLesClics.decPtr()

        self.reinitialise_tout(self.echelle_image, self.nb_de_points, self.tousLesClics, self.premiere_image)
        self.repasseTousLesClics()
        self.label_echelle_trace.show()
        self.modifie = True

    def refait_point_suivant(self):
        """rétablit le point suivant après un effacement
        """
        self.dbg.p(1, "rentre dans 'refait_point_suivant'")
        self.tousLesClics.incPtr()
        self.reinitialise_tout(self.echelle_image, self.nb_de_points, self.tousLesClics, self.premiere_image)
        self.repasseTousLesClics()
        self.modifie = True

    def repasseTousLesClics(self):
        """
        repasse en mode non-interactif toute la liste des clics
        sur l'image, jusqu'au pointeur courant de cette liste pointée.
        """
        self.dbg.p(1, "rentre dans 'repasseTousLesClics'")
        self.affiche_echelle()
        self.affiche_nb_points()
        self.ui.tab_traj.setEnabled(1)
        compteurClic = 0
        for clics in self.tousLesClics:
            compteurClic += 1
            if compteurClic == len(self.tousLesClics):
                self.updatePicture = True  # afficeh la dernière mage
            else:
                self.updatePicture = False  # afficeh la dernière mage
            self.clic_sur_label_video(liste_points=clics, interactif=False)
        self.clic_sur_label_video_ajuste_ui(1)


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
                    combo.addItem(QString("x%d(t)" % (i + 1)))
                    combo.addItem(QString("y%d(t)" % (i + 1)))
                    combo.addItem(QString("v%d(t)" % (i + 1)))

                self.dbg.p(3, "origine %s, ref %s" % (str(origine), str(ref)))
        except ZeroDivisionError:
            self.dbg.p(1, "ERROR : ZeroDivisionError in Self.tracer_trajectoires")
        self.label_trajectoire.reDraw()


    def tracer_courbe(self, itemChoisi):
        self.dbg.p(1, "rentre dans 'tracer_courbe'")
        if self.ui.comboBox_mode_tracer.isEnabled():
            # try:
            self.ui.comboBox_mode_tracer.setCurrentIndex(0)
            if itemChoisi <= 0: return  # c'est rien du tout.
            numero = (itemChoisi - 1) / 3
            typeDeCourbe = ("x", "y", "v")[(itemChoisi - 1) % 3]
            titre = (_translate("pymecavideo", "Evolution de l'abscisse du point %1", None).arg(numero + 1),
                     _translate("pymecavideo", "Evolution de l'ordonnée du point %1", None).arg(numero + 1),
                     _translate("pymecavideo", "Evolution de la vitesse du point %1", None).arg(numero + 1))[
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
            # déterminer le style de tracé
            styleTrace = None
            if typeDeCourbe in ("x", "y"):
                if ref == "camera":
                    p1 = self.pointEnMetre(vecteur(0, 0))
                    p2 = self.pointEnMetre(vecteur(self.largeur, self.hauteur))
                    minx = p1.x();
                    maxx = p2.x()
                    miny = p1.y();
                    maxy = p2.y()
                    if typeDeCourbe == "x":
                        styleTrace = [0, minx, t, maxx]
                    if typeDeCourbe == "y":
                        styleTrace = [0, miny, t, maxy]
                else:
                    styleTrace = "zero"
            else:  # type de courbe "v""
                styleTrace = "zero"

            if not hasattr(self, 'traceur'):
                self.traceur = traceur2d(self, abscisse, ordonnee, labelAbscisse, labelOrdonnee, titre, styleTrace,
                                         itemChoisi)
            else:  # mets juste à jour la fenêtre de matplotlib
                self.traceur.update(abscisse, ordonnee, labelAbscisse, labelOrdonnee, titre, styleTrace, itemChoisi)


    def affiche_point_attendu(self, n):
        self.dbg.p(1, "rentre dans 'affiche_point_attendu'")
        """
        Renseigne sur le numéro du point attendu
        affecte la ligne de statut et la ligne sous le zoom
        """
        self.mets_a_jour_label_infos(
            _translate("pymecavideo", "Pointage des positions : cliquer sur le point N° %1", None).arg(n))


    def clic_sur_label_video(self, liste_points=None, interactif=True):
        self.dbg.p(1, "rentre dans 'clic_sur_label_video'")
        self.lance_capture = True

        if liste_points == None:
            liste_points = self.label_video.liste_points
        ### on fait des marques pour les points déjà visités
        etiquette = "@abcdefghijklmnopqrstuvwxyz"[len(liste_points)]

        if self.nb_de_points > len(liste_points):
            point_attendu = 1 + len(liste_points)
            self.affiche_point_attendu(point_attendu)  # peut etre ici un update de l'image a optimiser

        else:
            point_attendu = 1
            self.affiche_point_attendu(point_attendu)
            if self.index_de_l_image <= self.image_max:  ##si on atteint la fin de la vidéo
                self.lance_capture = True
                self.stock_coordonnees_image(self.nb_image_deja_analysees, liste_points, interactif)
                self.nb_image_deja_analysees += 1
                self.index_de_l_image += 1
                if interactif:
                    self.modifie = True
                self.clic_sur_label_video_ajuste_ui(point_attendu)

            if self.index_de_l_image > self.image_max:
                self.lance_capture = False
                self.mets_a_jour_label_infos(_translate("pymecavideo", "Vous avez atteint la fin de la vidéo", None))
                self.index_de_l_image = self.image_max

    def enableDefaire(self, value):
        """
        Contrôle la possibilité de défaire un clic
        @param value booléen
        """
        self.dbg.p(1, "rentre dans 'enableDefaire'")
        self.ui.pushButton_defait.setEnabled(value)
        self.ui.actionDefaire.setEnabled(value)

        ##permet de remettre l'interface à zéro
        if not value:
            self.init_capture()
            self.ui.horizontalSlider.setEnabled(True)
            self.ui.spinBox_image.setEnabled(True)

    def enableRefaire(self, value):
        """
        Contrôle la possibilité de refaire un clic
        @param value booléen
        """
        self.dbg.p(1, "rentre dans 'enableRefaire'")
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
            if len(self.label_video.liste_points) > 0:
                self.tousLesClics.append(self.label_video.liste_points)
            self.label_video.liste_points = []
            self.dbg.p(1, "self.nb_image_deja_analysees >= len(self.points) ? %s %s" % (
                len(self.tousLesClics), len(self.points)))

            if len(self.tousLesClics) == len(
                    self.points):  # update image only at last point. use to optimise undo/redo fucntions.
                self.affiche_image()
            self.tracer_trajectoires("absolu")

        self.enableDefaire(len(self.tousLesClics) > 0)
        self.enableRefaire(self.tousLesClics.nextCount() > 0)

    def stock_coordonnees_image(self, ligne, liste_points, interactif=True, index_image=False):
        """
        place les données dans le tableau, rempli les dictionnaires de 
        @param ligne le numérode la ligne où placer les données (commence à 0)
        @param liste_points la liste des points cliqués sur l'image courante
        @param interactif vrai s'il faut rafraîchir tout de suite l'interface utilisateur.
        """
        self.dbg.p(1, "rentre dans 'stock_coordonnees_image'")
        if not index_image:
            index_image = self.index_de_l_image
        t = "%4f" % ((ligne) * self.deltaT)
        self.points[ligne] = [t] + liste_points

        # rentre le temps dans la première colonne
        self.ui.tableWidget.insertRow(ligne)
        self.ui.tableWidget.setItem(ligne, 0, QTableWidgetItem(t))

        i = 0
        # Pour chaque point dans liste_points, insère les valeur dans la ligne
        for point in liste_points:
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

            pm = self.pointEnMetre(point)
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
        self.index_de_l_image = self.ui.spinBox_image.value()
        self.affiche_image()

    def affiche_image(self):
        self.dbg.p(1, "rentre dans 'affiche_image'")
        try:
            self.dbg.p(1, "rentre dans 'affiche_image'" + ' ' + str(self.index_de_l_image) + ' ' + str(self.image_max))
            if self.updatePicture:
                if self.index_de_l_image <= self.image_max:
                    self.dbg.p(1, "affiche_image " + "self.index_de_l_image <= self.image_max")
                    self.extract_image(self.filename, self.index_de_l_image)
                    image = QImage(self.chemin_image)
                    self.imageAffichee = image.scaled(self.largeur, self.hauteur, Qt.KeepAspectRatio)
                    if hasattr(self, "label_video"):
                        self.afficheJusteImage()

                        if self.ui.horizontalSlider.value() != self.index_de_l_image:
                            self.dbg.p(1, "affiche_image " + "horizontal")
                            self.ui.horizontalSlider.setValue(self.index_de_l_image)
                            self.ui.spinBox_image.setValue(self.index_de_l_image)
                elif self.index_de_l_image > self.image_max:
                    self.index_de_l_image = self.image_max
                    self.lance_capture = False

        except AttributeError:
            pass


    def afficheJusteImage(self):
        self.dbg.p(1, "affiche_image " + "video")
        self.label_video.setMouseTracking(True)
        self.label_video.setPixmap(QPixmap.fromImage(self.imageAffichee))
        self.label_video.met_a_jour_crop()
        #self.label_video.update()
        #self.label_video.show()

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
        self.enableRefaire(0)

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
                                                  QLineEdit.Normal, QString("1.0"))
        if echelle_result_raw[1] == False:
            return None
        try:
            echelle_result = [float(echelle_result_raw[0].replace(",", ".")), echelle_result_raw[1]]

            if echelle_result[0] <= 0 or echelle_result[1] == False:
                self.mets_a_jour_label_infos(_translate("pymecavideo", " Merci d'indiquer une échelle valable", None))
            else:
                self.echelle_image.etalonneReel(echelle_result[0])

                self.job = Label_Echelle(self.label_video, self)
                self.job.setPixmap(QPixmap(self.chemin_image))
                self.job.show()
        except ValueError:
            self.mets_a_jour_label_infos(_translate("pymecavideo", " Merci d'indiquer une échelle valable", None))
            self.demande_echelle()
            # self.ui.pushButton_video.setEnabled(0)

    def feedbackEchelle(self, p1, p2):
        """
        affiche une trace au-dessus du self.job, qui reflète les positions
        retenues pour l'échelle
        """
        self.dbg.p(1, "rentre dans 'feedbackEchelle'")
        from echelle import Label_Echelle_Trace

        self.label_echelle_trace = Label_Echelle_Trace(self.label_video, p1, p2)
        self.label_echelle_trace.show()
        self.emit(SIGNAL('stopRedimensionnement()'))


    def reinitialise_environnement(self):
        self.dbg.p(1, "rentre dans 'reinitialise_environnement'")
        for filename in glob(os.path.join(IMG_PATH, "*.jpg")):
            os.remove(filename)

    def closeEvent(self, event):
        """
        Un crochet pour y mettre toutes les procédures à faire lors
        de la fermeture de l'application.
        """
        self.dbg.p(1, "rentre dans 'closeEvent'")
        from tempfile import gettempdir

        self.nettoieVideosRecodees()
        if self.verifie_donnees_sauvegardees():
            self.reinitialise_environnement()
            liste_fichiers = os.listdir(gettempdir())
            for fichier in liste_fichiers:
                if "pymeca" in fichier:
                    try:
                        os.remove(fichier)
                    except OSError:
                        pass
            event.accept()
        else:
            event.ignore()

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
            retour = QMessageBox.warning(self, QString(_translate("pymecavideo", "Les données seront perdues", None)), \
                                         QString(_translate("pymecavideo",
                                                            "Votre travail n'a pas été sauvegardé\nVoulez-vous les sauvegarder ?",
                                                            None)),
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

    def aller_a_l_image(self, increment):
        self.dbg.p(1, "rentre dans 'aller_a_l_image'")
        increment = int(increment)
        self.index_de_l_image = self.index_de_l_image + increment
        if self.index_de_l_image <= self.image_max:
            self.affiche_image()

        elif self.index_de_l_image == 0:
            self.index_de_l_image = 1
            self.mets_a_jour_label_infos(_translate("pymecavideo", "Vous avez atteint le début de la vidéo", None))
            self.affiche_image()

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
        self.reinitialise_tout()
        filename = QFileDialog.getOpenFileName(self, _translate("pymecavideo", "Ouvrir une vidéo"), dir_,
                                               _translate("pymecavideo",
                                                          "fichiers vidéos ( *.avi *.mp4 *.ogv *.mpg *.mpeg *.ogg *.mov *.wmv)",
                                                          None))
        self.openTheFile(filename)

    def openfile(self):
        """
        Ouvre un dialogue pour choisir un fichier vidéo puis le charge
        """
        self.dbg.p(1, "rentre dans 'openfile'")
        dir_ = self._dir("videos")
        filename = QFileDialog.getOpenFileName(self, _translate("pymecavideo", "Ouvrir une vidéo", None), dir_,
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
        @param filename chaîne de caractère, de type string,QSring ou QByteArray
         le forçage de type permet d'accepter chacune des variantes en entrée.
         N.B.: l'attribut self.prefs.lastVideo sera qui sera enregistré est de
         type string et d'encodage unicode.
        """
        self.dbg.p(1, "rentre dans 'openTheFile'")
        if filename != "":
            filename = QString(filename)
            filename = filename.toUtf8()
            data = filename.data()
            self.filename = data.decode('utf-8')
            goOn = self.init_cvReader()

            if goOn:  # video is in good format

                self.prefs.lastVideo = self.filename
                self.determineHauteurLargeur()

                #                self.ui.label.setGeometry(153, 40, self.largeur, self.hauteur)

                self.init_image()
                self.init_capture()
                self.redimensionne(premier=1)
                self.label_video.show()
                self.prefs.videoDir = os.path.dirname(self.filename)
                self.prefs.save()

    def init_capture(self):
        """met le panneaux de capture visible"""
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(1)
        self.ui.menuE_xporter_vers.setEnabled(1)
        self.ui.actionSaveData.setEnabled(1)
        self.mets_a_jour_label_infos(
            _translate("pymecavideo", "Veuillez choisir une image et définir l'échelle", None))
        self.ui.Bouton_Echelle.setEnabled(True)
        self.ui.spinBox_nb_de_points.setEnabled(True)
        self.ui.horizontalSlider.setEnabled(1)
        self.ui.checkBox_abscisses.setEnabled(1)
        self.ui.checkBox_ordonnees.setEnabled(1)
        self.ui.checkBox_auto.setEnabled(1)
        try:
            if self.label_echelle_trace:
                self.ui.Bouton_lance_capture.setEnabled(True)
        except AttributeError:
            pass  # si l'échelle n'est pas défine encore


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
        QMessageBox.warning(None, "Licence", QString(licence_XX), QMessageBox.Ok, QMessageBox.Ok)

    def aide(self):
        self.dbg.p(1, "rentre dans 'aide'")
        lang = locale.getdefaultlocale()[0][0:2]
        helpfile = "%s/help-%s.xhtml" % (self._dir("help"), lang)
        if os.path.exists(helpfile):
            command = "firefox --new-window %s" % helpfile
            status, output = commands.getstatusoutput(command)
            if status != 0:
                command = "x-www-browser %s" % helpfile
                status, output = commands.getstatusoutput(command)
        else:
            QMessageBox.warning(None, "Aide",
                                _translate("pymecavideo", "Désolé pas de fichier d'aide pour le langage %1.", None).arg(
                                    lang))


    def init_image(self):
        """intialise certaines variables lors le la mise en place d'une nouvelle image"""
        self.dbg.p(1, "rentre dans 'init_image'")
        self.index_de_l_image = 1
        self.init_interface()
        self.trajectoire = {}
        self.ui.spinBox_image.setMinimum(1)
        self.defini_barre_avancement()
        self.echelle_image = echelle()
        self.affiche_echelle()
        self.ui.tab_traj.setEnabled(0)
        self.ui.spinBox_image.setEnabled(1)
        self.a_une_image = True
        self.affiche_image()
        self.reinitialise_environnement()


    def defini_barre_avancement(self):
        """récupère le maximum d'images de la vidéo et défini la spinbox et le slider"""
        self.dbg.p(1, "rentre dans 'defini_barre_avancement'")
        framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos()
        self.dbg.p(3,
                   "In :  'defini_barre_avancement', framerate, self.image_max = %s, %s" % (framerate, self.image_max))
        self.deltaT = float(1.0 / framerate)
        self.ui.horizontalSlider.setMinimum(1)

        self.ui.horizontalSlider.setMaximum(int(self.image_max))
        self.ui.spinBox_image.setMaximum(int(self.image_max))

        fichier = os.path.join(IMG_PATH, VIDEO + SUFF % 1)
        try:
            os.remove(fichier)
            self.extract_image(self.filename, 1)
            os.remove(fichier)
        except OSError:
            pass

    def extract_image(self, video, index, force=False):
        """
        extrait une image de la video à l'aide d'OpenCV et l'enregistre
        @param video le nom du fichier video
        @param index le numéro de l'image
        @param force permet de forcer l'écriture d'une image
        """
        self.dbg.p(1, "rentre dans 'extract_image' " + 'index : ' + str(index))
        imfilename = os.path.join(IMG_PATH, VIDEO + SUFF % index)
        if force or not os.path.isfile(imfilename):
            self.cvReader.writeImage(index, imfilename)
        self.chemin_image = imfilename

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
        opts, args = getopt.getopt(args, "f:md:", ["fichier_mecavideo=", "maxi", "debug="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)


    ###translation##
    locale = "%s" % QLocale.system().name()

    # locale = "%s" %QString("en_EN")

    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale):
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()

    langdir = os.path.join(StartQT4._dir("langues"),
                           r"pymecavideo_" + locale)

    if appTranslator.load(langdir):
        b = app.installTranslator(appTranslator)

    windows = StartQT4(None, opts, args)

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


if __name__ == "__main__":
    run()
