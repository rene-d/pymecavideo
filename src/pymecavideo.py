# -*- coding: utf-8 -*-

import sys,os, locale
thisDir = os.path.dirname(__file__)
sys.path.insert(0, thisDir)

import subprocess

from globdef import HOME_PATH, VIDEO_PATH, CONF_PATH, \
    ICON_PATH, LANG_PATH, \
    DATA_PATH, HELP_PATH, DOCUMENT_PATH, \
    pattern_float
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QVBoxLayout, QTableWidgetSelectionRange, QDialog, QPushButton
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QShortcut, QScreen, QAction
from PyQt6.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer

import getopt
import traceback
import time
import numpy as np
import math
import tempfile
import platform
import re
import magic
import pyqtgraph as pg
import pyqtgraph.exporters
import math

from export import Export, EXPORT_FORMATS
from toQimage import toQImage
from version import version, Version, str2version
from dbg import Dbg
from preferences import Preferences
from cadreur import Cadreur, openCvReader
from choix_origine import ChoixOrigineWidget
from trajectoire_widget import TrajectoireWidget
from grandeurs import grandeurs
from glob import glob
from vecteur import vecteur

import interfaces.icon_rc

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

licence['fr'] = """
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


from interfaces.Ui_pymecavideo import Ui_pymecavideo

class FenetrePrincipale(QMainWindow, Ui_pymecavideo):
    def __init__(self, parent=None, opts=[], args=[]):
        """
        le constructeur reçoit les données principales du logiciel :
        @param parent le widget parent, None pour une fenêtre principale
        @param opts les options de l'invocation bien rangées en tableau
        @param args les arguments restants après raitement des options
        """
        QMainWindow.__init__(self, parent)
        Ui_pymecavideo.__init__(self)
        QWidget.__init__(self, parent)
        # version minimale du fichier de configuration :
        self.min_version = version(7, 3, ".0-1")
        self.hauteur = 1
        self.largeur = 0
        self.ratio = 4/3
        self.decalh = 0
        self.decalw = 0
        self.wanted_image_size = vecteur() # taille souhaitée pour l'image
        self.nb_ajuste_image = 20          # nombre d'itérations pour y parvenir
        self.imgdim_hide = time.time() + 2 # moment pour cacher la taille
        self.roleEtat = None               # dict. état => message de statut
        self.dictionnairePlotWidget = {}

        # Mode plein écran
        self.plein_ecran = False
        QShortcut(QKeySequence("F11"), self, self.basculer_plein_ecran)

        g = QApplication.instance().screens()[0].geometry()
        self.height_screen, self.width_screen = g.height(), g.width()

        self.setupUi(self)

        self.dbg = Dbg(0)
        for o in opts:
            if ('-d' in o[0]) or ('--debug' in o[0]):
                self.dbg = Dbg(o[1])
                print(self.dbg)

        self.prefs = Preferences(self)

        # définition des widgets importants
        self.graphWidget = None
        self.pointage.setApp(self)
        self.trajectoire_widget.setApp(self)

        # on cache le widget des dimensions de l'image
        self.hide_imgdim.emit()
        
        self.args = args

        self.platform = platform.system()

        # initialise les répertoires
        self._dir()


        # remplit l'exportCombo
        self.exportCombo.addItem('Exporter vers...')
        # Ajoute les différents formats d'exportation
        for key in sorted(EXPORT_FORMATS.keys()):
            self.exportCombo.addItem(EXPORT_FORMATS[key]['nom'])

        # crée les action exportQactions du menu Fichier
        for key in sorted(EXPORT_FORMATS.keys()):
            action = QAction(EXPORT_FORMATS[key]
                             ['nom'], self.menuE_xporter_vers)
            action.triggered.connect(
                lambda checked, index=key: self.export(index))
            self.menuE_xporter_vers.addAction(action)

        self.init_variables(self.prefs.defaults['lastVideo'])
        # connections internes
        self.ui_connections()

        # crée les débuts de messages pour la ligne de statut
        self.roleEtat = self.pointage.definit_messages_statut()
        
        self.change_etat.emit("debut") # met l'état à "debut"

        # traite un argument ; si ça ne va pas, s'intéresse à la
        # aux préférences du fichier pymecavideo.conf
        self.traite_arg() or self.apply_preferences()

        return

    def traite_arg(self):
        """
        traite les arguments donnés à l'application. Trouve le type de fichier
        et selon le cas, ouvre ou "rouvre" son contenu
        @return vrai si on a réussi à traiter un argument
        """
        OK = False
        if len(self.args) > 0:
            filename = self.args[0]
            mime = magic.Magic(mime=True)
            mt = mime.from_file(filename)
            if mt.startswith("video/"):
                OK = True
                self.pointage.openTheFile(filename)
            elif mt == "text/plain":
                signature = open(filename).read(24)
                if signature.startswith("# version = pymecavideo"):
                    OK = True
                    self.rouvre(filename)
            if not OK:
                QTimer.singleShot(
                    50,
                    lambda: QMessageBox.information(
                        self,
                        self.tr("Argument non pris en compte"),
                        self.tr("Le fichier {filename} n'est ni un fichier vidéo, ni un fichier de sauvegarde de pymecavideo.").format(filename=filename)))
                
        return OK

    def apply_preferences(self, rouvre = False):
        """
        Récupère les préférences sauvegardées, et en applique les données
        ici on s'occupe de ce qui se gère facilement au niveau de la
        fenêtre principale
        @param rouvre est vrai quand on ouvre un fichier pymecavideo ; 
          il est faux par défaut
        """
        self.dbg.p(2, "rentre dans 'FenetrePrincipale.apply_preferences'")
        # on relit les préférences du fichier de configuration, sauf en cas
        # de réouverture d'un fichier pymecavideo, qui contient les préférences
        if not rouvre:
            self.prefs = Preferences(self)
        m = re.match(r"pymecavideo (.*)",
                     self.prefs.config["DEFAULT"]["version"])
        if m:
            thisversion = str2version(m.group(1))
        else:
            thisversion = version(0,0)
        if thisversion < self.min_version:
            QTimer.singleShot(
                50,
                lambda: QMessageBox.information(
                    self,
                    self.tr("Configuration trop ancienne"),
                    self.tr("La version du fichier de configuration, {version} est inférieure à {min_version} : le fichier de configuration ne peut pas être pris en compte").format(version = thisversion, min_version = self.min_version)))
            return
        elif thisversion < Version:
             QTimer.singleShot(
                50,
                lambda: QMessageBox.information(
                    self,
                    self.tr("Configuration ancienne"),
                    self.tr("La version du fichier de configuration, {version} est inférieure à {Version} : certaines dimensions peuvent être légèrement fausses.").format(version = thisversion, Version = Version)))
        # le fichier de configuration a la bonne version, on applique ses
        # données
        self.wanted_image_size = self.prefs.config.getvecteur(
            "DEFAULT", "taille_image")
        self.nb_ajuste_image = 20 # pas plus de 20 itérations
        self.adjust4image.emit()
       
        d = self.prefs.config["DEFAULT"]
        self.radioButtonNearMouse.setChecked(d["proximite"] == "True")
        self.pointage.apply_preferences(rouvre = rouvre)
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
        self.dbg.p(2, "rentre dans 'basculer_plein_ecran'")
        if not self.plein_ecran:
            self.showFullScreen()
        else:
            self.showNormal()
        self.plein_ecran = not (self.plein_ecran)

    def init_variables(self, filename=""):
        self.dbg.p(2, "rentre dans 'init_variables'")
        self.index_max = 1
        self.repere = 0
        self.masse_objet = 0
        # contient les listes des abscisses, vitesses, énergies calculées par le grapheur.
        self.locals = {} # dictionnaire de variables locales, pour eval
        self.motif = []
        self.trajectoire = {}  # dictionnaire des points des trajectoires
        self.index_du_point = 0
        self.couleurs = ["red", "blue", "cyan", "magenta", "yellow", "gray",
                         "green"]  # correspond aux couleurs des points de la trajectoire
        self.nb_de_points = 0  # nombre de points suivis
        self.point_attendu = 0
        self.nb_clics = 0
        self.premierResize = True  # arrive quand on ouvre la première fois la fenetre
        self.pointage.index = 1  # image à afficher
        self.chronoImg = 0
        self.filename = filename
        self.stdout_file = os.path.join(CONF_PATH, "stdout")
        self.exitDecode = False
        self.resizing = False
        self.stopRedimensionne = False
        self.refait_point = False
        self.graphe_deja_choisi = None
        return

    

    ############ les signaux spéciaux #####################
    change_axe_origine = pyqtSignal()
    selection_done = pyqtSignal()
    redimensionneSignal = pyqtSignal(bool)
    updateProgressBar = pyqtSignal()
    change_etat = pyqtSignal(str)
    show_coord = pyqtSignal()               # montre l'onglet des coordonnées
    show_video = pyqtSignal()               # montre l'onglet des vidéos
    sens_axes = pyqtSignal(int, int)        # coche les cases des axes
    stop_n = pyqtSignal(str)                # refait le texte du bouton STOP
    image_n = pyqtSignal(int)               # modifie les contrôles d'image
    adjust4image = pyqtSignal()             # adapte la taille à l'image
    hide_imgdim = pyqtSignal()              # cache la dimension de l'image
    affiche_statut = pyqtSignal(str)        # modifie la ligne de statut
    stopRedimensionnement = pyqtSignal()    # fixe la taille de la fenêtre
    OKRedimensionnement = pyqtSignal()      # libère la taille de la fenêtre
    
    
    def ui_connections(self):
        """connecte les signaux de Qt"""
        self.dbg.p(2, "rentre dans 'ui_connections'")

        #connexion de signaux de menus
        self.actionOuvrir_un_fichier.triggered.connect(self.openfile)
        self.actionExemples.triggered.connect(self.openexample)
        self.action_propos.triggered.connect(self.propos)
        self.actionAide.triggered.connect(self.aide)
        #self.actionDefaire.triggered.connect(self.pointage.efface_point_precedent)
        self.actionRefaire.triggered.connect(self.pointage.refait_point_suivant)
        self.actionQuitter.triggered.connect(self.close)
        self.actionSaveData.triggered.connect(self.pointage.enregistre_ui)
        self.actionCopier_dans_le_presse_papier.triggered.connect(
            self.presse_papier)
        self.actionRouvrirMecavideo.triggered.connect(self.rouvre_ui)

        # connexion de signaux de widgets
        self.exportCombo.currentIndexChanged.connect(self.export)
        self.pushButton_nvl_echelle.clicked.connect(self.recommence_echelle)
        self.checkBox_Ec.stateChanged.connect(self.affiche_tableau)
        self.checkBox_Epp.stateChanged.connect(self.affiche_tableau)
        self.checkBox_Em.stateChanged.connect(self.affiche_tableau)
        self.comboBox_X.currentIndexChanged.connect(self.dessine_graphe_avant)
        self.comboBox_Y.currentIndexChanged.connect(self.dessine_graphe_avant)
        self.lineEdit_m.textChanged.connect(self.verifie_m_grapheur)
        self.lineEdit_g.textChanged.connect(self.verifie_g_grapheur)
        self.comboBox_style.currentIndexChanged.connect(self.dessine_graphe)
        self.pushButton_save.clicked.connect(self.enregistreChrono)
        self.spinBox_chrono.valueChanged.connect(self.changeChronoImg)
        self.pushButton_save_plot.clicked.connect(self.enregistre_graphe)
        self.comboBox_referentiel.currentIndexChanged.connect(
            self.tracer_trajectoires)
        self.tabWidget.currentChanged.connect(self.choix_onglets)
        self.checkBoxScale.currentIndexChanged.connect(self.enableSpeed)
        self.checkBoxScale.currentTextChanged.connect(self.enableSpeed)
        self.checkBoxVectorSpeed.stateChanged.connect(self.enableSpeed)
        self.radioButtonSpeedEveryWhere.clicked.connect(self.enableSpeed)
        self.radioButtonNearMouse.clicked.connect(self.enableSpeed)
        self.button_video.clicked.connect(self.montre_video)
        self.pushButton_select_all_table.clicked.connect(self.presse_papier)
        self.comboBoxChrono.currentIndexChanged.connect(self.chronoPhoto)

        # connexion de signaux spéciaux
        self.change_axe_origine.connect(self.egalise_origine)
        self.redimensionneSignal.connect(self.redimensionneFenetre)
        self.updateProgressBar.connect(self.updatePB)
        self.change_etat.connect(self.changeEtat)
        self.show_coord.connect(self.montre_volet_coord)
        self.show_video.connect(self.montre_volet_video)
        self.sens_axes.connect(self.coche_axes)
        self.stop_n.connect(self.stop_setText)
        self.image_n.connect(self.sync_img2others)
        self.affiche_statut.connect(self.setStatus)
        self.adjust4image.connect(self.ajuste_pour_image)
        self.hide_imgdim.connect(self.cache_imgdim)
        self.affiche_statut.connect(self.setStatus)
        self.stopRedimensionnement.connect(self.fixeLesDimensions)
        self.OKRedimensionnement.connect(self.defixeLesDimensions)
        
        return

    def cache_imgdim(self):
        """
        Cache le widget d'affichage de la dimension de l'image
        quand son temps de présentation est révolu
        """
        if time.time() > self.imgdim_hide:
            self.pointage.imgdimEdit.hide()
        else:
            QTimer.singleShot(200, self.cache_imgdim)
        return
    
    def ajuste_pour_image(self):
        """
        ajuste progressivement la taille de la fenêtre principale
        jusqu'à ce que l'image soit à la taille voulue, c'est à dire
        self.wanted_image_size
        """
        delai = 50 # 20 ajustements par seconde
        w1, h1 = self.width(), self.height()
        self.OKRedimensionnement.emit()
        
        def modifie(x, y):
            """
            fabrique une fonction qui modifie la taille de la fenêtre
            principale de (x,y), et relance la recherched e taille idéale
            """
            def m():
                self.resize(w1 + x, h1 + y)
                self.update()
                self.adjust4image.emit()
                return
            return m
        
        # taille de l'image actuellement
        w, h = int(self.pointage.video.size().width()),  int(self.pointage.video.size().height())
        # taille visée
        w0 , h0 = int(self.wanted_image_size.x), int(self.wanted_image_size.y)
        # erreurs de taille de la fenêtre
        deltaw, deltah = w0 - w, h0 - h
        # modifications à apporter à la taille de la fenêtre
        w2, h2 = 0, 0 
        # on divise par deux l'erreur à compenser, en prenant soin
        # de ne jamais obtenir zéro ; ça doit faire au moins +-1
        if deltaw :
            w2 = int(abs(deltaw)/deltaw*math.ceil(abs(deltaw/2)))
        if deltah:
            h2 = int(abs(deltah)/deltah*math.ceil(abs(deltah/2)))
        if w2 or h2:
            # enfin on prévoit de modifier la fenêtre dans le bons sens
            self.nb_ajuste_image -= 1
            if self.nb_ajuste_image:
                #seulement si on a encore droit à une itération
                QTimer.singleShot(delai, modifie(w2, h2))
            return
        else:
            # fini : il n'y a plus besoin de modifier la taille de la fenêtre
            if self.pointage.etat not in ("debut", "A"):
                self.stopRedimensionnement.emit()
        
        return

    def egalise_origine(self):
        """
        harmonise l'origine : recopie celle de la vidéo vers le
        widget des trajectoires et redessine les deux.
        """
        self.trajectoire_widget.origine_mvt = self.pointage.origine
        self.trajectoire_widget.update()
        self.pointage.update()
        return
    
    def changeChronoImg(self,img):
        self.chronoImg = img
        self.chronoPhoto()

    def enregistreChrono(self):
        self.pixmapChrono = QPixmap(self.trajectoire_widget.size())
        self.trajectoire_widget.render(self.pixmapChrono)
        base_name = os.path.splitext(os.path.basename(self.filename))[0]
        defaultName = os.path.join(DOCUMENT_PATH, base_name)
        fichier = QFileDialog.getSaveFileName(self,
                                              self.tr("Enregistrer comme image"),
                                              defaultName, self.tr("fichiers images(*.png *.jpg)"))
        try :
            self.pixmapChrono.save(fichier[0])
        except Exception as err:
            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
            QMessageBox.critical(None, self.tr("Erreur lors de l'enregistrement"), self.tr("Echec de l'enregistrement du fichier:<b>\n{0}</b>").format(
                    fichier[0]))

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
            self.spinBox_chrono.setMaximum(int(self.pointage.image_max))
            self.spinBox_chrono.setMinimum(1)

        elif self.comboBoxChrono.currentIndex() == 2 :
            self.widget_chronophoto.setEnabled(False)
            self.trajectoire_widget.setEnabled(False)
            self.widget_speed.setEnabled(False)
            self.checkBoxVectorSpeed.setChecked(False)
        self.dbg.p(2, "rentre dans 'chronoPhoto'")
        # ajoute la première image utilisée pour le pointage sur le fond du vidget
        liste_types_photos = ['chronophotographie', 'chronophotogramme']

        if self.comboBoxChrono.currentIndex() != 0:
            photo_chrono = liste_types_photos[self.comboBoxChrono.currentIndex(
            )-1]
            self.dbg.p(2, "dans 'chronoPhoto, on a choisi le type %s'" %
                       (photo_chrono))
            if photo_chrono == 'chronophotographie':  # on extrait le première image que l'on rajoute au widget
                self.trajectoire_widget.chrono = 1  # 1 pour chronophotographie
                ok, img = self.pointage.cvReader.getImage(
                    self.chronoImg, self.pointage.rotation)
                self.imageChrono = toQImage(img).scaled(
                    self.pointage.width(), self.pointage.height(), Qt.KeepAspectRatio)
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
        return

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
        self.dbg.p(2, "rentre dans 'enableSpeed'")
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
        return

    def presse_papier(self):
        """Sélectionne la totalité du tableau de coordonnées
        et l'exporte dans le presse-papier (l'exportation est implicitement
        héritée de la classe utilisée pour faire le tableau). Les
        séparateurs décimaux sont automatiquement remplacés par des virgules
        si la locale est française.
        """
        self.dbg.p(2, "rentre dans 'presse_papier'")
        self.affiche_tableau()
        trange = QTableWidgetSelectionRange(0, 0,
                                            self.tableWidget.rowCount() - 1,
                                            self.tableWidget.columnCount() - 1)
        self.tableWidget.setRangeSelected(trange, True)
        self.tableWidget.selection()

    def export(self, choix_export=None):
        self.dbg.p(2, "rentre dans 'export'")
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
        self.dbg.p(2, "rentre dans 'rouvre_ui'")

        dir_ = DOCUMENT_PATH
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Ouvrir un projet Pymecavideo"),
            dir_,
            self.tr("Projet Pymecavideo (*.mecavideo)"))
        if fichier != "":
            self.rouvre(fichier)
        return

    def redimensionneFenetre(self, tourne=False):
        self.dbg.p(2, "rentre dans 'redimensionneFenetre'")
        if tourne:  # on vient de cliquer sur tourner. rien n'est changé.
            self.dbg.p(2, "Dans 'redimensionneFenetre', tourne")
            self.pointage.remontre_image()
        else:
            self.pointage.affiche_image()
        self.trajectoire_widget.maj()
        return

    def enterEvent(self, e):
        self.gardeLargeur()

    def leaveEvent(self, e):
        self.gardeLargeur()

    def gardeLargeur(self):
        self.largeurAvant = self.largeur

    def resizeEvent(self, event):
        self.dbg.p(2, "rentre dans 'resizeEvent'")
        
        # on montre la taille de l'image
        self.pointage.imgdimEdit.show()
        # pour deux secondes de plus
        self.imgdim_hide = time.time() + 2
        # et on en programme l'extinction
        self.hide_imgdim.emit()
        
        self.redimensionneFenetre(tourne=False)
        return super(FenetrePrincipale, self).resizeEvent(event)

    def showEvent(self, event):
        self.dbg.p(2, "rentre dans 'showEvent'")
        self.redimensionneSignal.emit(False)

    def cree_tableau(self, nb_suivis=1):
        """
        Crée un tableau de coordonnées neuf dans l'onglet idoine.
        @param nb_suivis le nombre d'objets suivis (1 par défaut)
        """
        self.dbg.p(2, "rentre dans 'cree_tableau'")
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
        self.tableWidget.setRowCount(len(self.pointage.data))
        for i in range(nb_suivis):
            unite = "m" if self.pointage.echelle_image \
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
        self.dbg.p(2, "rentre dans 'recalculLesCoordonnees'")
        nb_suivis = self.pointage.nb_obj

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
        self.pointage.iteration_data(cb_temps, cb_point, unite = "m")
        return

    def montre_video(self):
        self.dbg.p(2, "rentre dans 'montre_video'")
        ref = self.comboBox_referentiel.currentText().split(" ")[-1]
        if len(ref) == 0 or ref == "camera":
            return
        c = Cadreur(int(ref), self.pointage)
        c.montrefilm()
        return

    def choix_onglets(self, newIndex):
        """
        traite les signaux émis par le changement d'onglet, ou
        par le changement de référentiel dans l'onglet des trajectoires.
        @param newIndex la variable transmise par le signal currentChanged
          du tabWidget
        """
        self.dbg.p(2, f"rentre dans 'choix_onglets', self.tabWidget.currentIndex() = {self.tabWidget.currentIndex()}, newIndex = {newIndex}")
        self.statusBar().clearMessage()
        if self.tabWidget.currentIndex() == 0:
            # onglet video, on ne fait rien de spécial
            pass
        if self.tabWidget.currentIndex() == 1:
            # onglet des trajectoires
            self.tracer_trajectoires("absolu")
        elif self.tabWidget.currentIndex() == 2:
            # onglet des coordonnées
            self.affiche_tableau()
        elif self.tabWidget.currentIndex() == 3:
            # onglet du grapheur
            self.affiche_grapheur()
            self.MAJ_combox_box_grapheur()
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
                self.pointage.sens_Y * m * g * p.y if p else None)
            return
        self.pointage.iteration_data(None, cb_points, unite="m")

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
        return
        
    def MAJ_combox_box_grapheur(self):
        if self.graphe_deja_choisi is None : #premier choix de graphe
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

    def dessine_graphe_avant(self):
        if self.graphe_deja_choisi is not None :
            self.graphe_deja_choisi = None #si changement ds les combobox, on réinitilaise le choix.
        self.dessine_graphe()

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
            defaultName = os.path.join(DOCUMENT_PATH, base_name+'.png')
            fichier = QFileDialog.getSaveFileName(
                self,
                self.tr("Enregistrer le graphique"),
                defaultName, self.tr("fichiers images(*.png)"))
            self.pg_exporter.export(fichier[0])

    def tracer_trajectoires(self, newValue):
        """
        Cette fonction est appelée par un changement de référentiel.
        On peut aussi appeler cette fonction directement, auquel cas on
        donne la valeur "absolu" à newValue pour reconnaître ce cas.
        efface les trajectoires anciennes, puis
        trace les trajectoires en fonction du référentiel choisi.

        """
        self.dbg.p(2, "rentre dans 'tracer_trajectoires'")
        self.trajectoire_widget.origine_mvt = self.pointage.origine
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
            origine = vecteur(self.pointage.width() // 2, self.pointage.height() // 2)
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
    
    def masse(self, obj):
        """
        Renseigne la masse d'un objet. L'implémentation est actuellement
        incomplète : une seule masse est autorisée, pour tous les objets
        donc on ne tient pas compte du paramètre obj
        @param obj un objet suivi
        @return la masse de cet objet
        """
        if self.masse_objet == 0:
            masse_objet_raw, ok = QInputDialog.getText(
                None,
                self.tr("Masse de l'objet"),
                self.tr("Quelle est la masse de l'objet ? (en kg)"),
                text ="1.0")
            masse_objet_raw = masse_objet_raw.replace(",", ".")
            ok = ok and pattern_float.match(masse_objet_raw)
            masse_objet = float(masse_objet_raw)
            if masse_objet <= 0 or not ok:
                self.affiche_statut.emit(self.tr(
                    "Merci d'indiquer une masse valable"))
                return None
            self.masse_objet = masse_objet
        return self.masse_objet

    def bouton_refaire(self, ligne):
        """
        Crée un bouton servant à refaire un pointage, pour la donnée
        affichée dans une ligne du tableau
        @param ligne une ligne du tableau (indexée à partir de 0)
        @return un bouton
        """
        b = QPushButton()
        b.setIcon(QIcon(":/data/icones/curseur_cible.svg"))
        b.setToolTip(self.tr(
            "refaire le pointage\n de l'image {numero}").format(
                numero = ligne + 1))
        b.setFlat(True)
        b.clicked.connect(lambda state: \
                          self.pointage.refait_point_depuis_tableau( b ))
        b.index_image = ligne + 1
        return b
    
    def affiche_tableau(self):
        """
        lancée à chaque affichage du tableau, recalcule les coordonnées
        à afficher à partir des listes de points.
        """
        self.dbg.p(2, "rentre dans 'affiche_tableau'")

        # active ou désactive les checkbox énergies
        # (n'ont un intérêt que si l'échelle est déterminée)
        if self.pointage.echelle_image:
            self.checkBox_Ec.setEnabled(True)
            self.checkBox_Epp.setEnabled(True)
            if self.checkBox_Ec.isChecked() and self.checkBox_Epp.isChecked():
                self.checkBox_Em.setEnabled(True)
            else:
                # s'il manque Ec ou Epp on décoche Em
                self.checkBox_Em.setChecked(False)
        else:
            self.checkBox_Ec.setEnabled(False)
            self.checkBox_Em.setEnabled(False)
            self.checkBox_Epp.setEnabled(False)

        # masse de l'objet ATTENTION : QUID SI PLUSIEURS OBJETS ?
        if self.checkBox_Ec.isChecked():
            self.masse_objet = self.masse(1)
            self.checkBox_Ec.setChecked(self.masse_objet != 0)
        # initialise tout le tableau (nb de colonnes, unités etc.)
        self.cree_tableau(nb_suivis = self.pointage.nb_obj)
        # le compte de colonnes supplémentaires pour chaque objet
        colonnes_sup = self.checkBox_Ec.isChecked() + \
            self.checkBox_Epp.isChecked() + \
            self.checkBox_Em.isChecked()
        # le numéro de la dernière colonne où on peut refaire les points
        colonne_refait_points = self.pointage.nb_obj * (2 + colonnes_sup) + 1

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
                # n'existe que s'il y a eu un pointage
                derniere = self.pointage.nb_obj * (2 + colonnes_sup) +1
                self.tableWidget.setCellWidget(
                    i, derniere, self.bouton_refaire(i))
            return
        
        self.pointage.iteration_data(
            cb_temps, cb_point,
            unite = "m" if self.pointage.echelle_image else "px")
        
        # rajoute des boutons pour refaire le pointage
        # au voisinage immédiat des zones de pointage
        colonne = self.pointage.nb_obj * (2 + colonnes_sup) +1
        if self.pointage.premiere_image() is None: return
        if self.pointage.premiere_image() > 1:
            i = self.pointage.premiere_image() - 2
            self.tableWidget.setCellWidget(i, colonne, self.bouton_refaire(i))
        if self.pointage.derniere_image() < len(self.pointage):
            i = self.pointage.derniere_image()
            self.tableWidget.setCellWidget(i, colonne, self.bouton_refaire(i))
        return

    def recommence_echelle(self):
        self.dbg.p(2, "rentre dans 'recommence_echelle'")
        self.tabWidget.setCurrentIndex(0)
        self.pointage.echelle_image = echelle()
        self.affiche_echelle()
        self.demande_echelle()
        return

    def closeEvent(self, event):
        """
        Un crochet pour y mettre toutes les procédures à faire lors
        de la fermeture de l'application.
        """
        self.dbg.p(2, "rentre dans 'closeEvent'")
        for plotwidget in self.dictionnairePlotWidget.values():
            plotwidget.parentWidget().close()
            plotwidget.close()
            del plotwidget
        d = self.prefs.config["DEFAULT"]
        d["taille_image"] = f"({self.pointage.video.image_w},{self.pointage.video.image_h})"
        d["rotation"] = str(self.pointage.video.rotation)
        self.prefs.save()
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

    def openexample(self):
        self.dbg.p(2, "rentre dans 'openexample'")
        dir_ = "%s" % (self._dir("videos"))
        filename, hints = QFileDialog.getOpenFileName(
            self,
            self.tr("Ouvrir une vidéo"), dir_,
            self.tr("fichiers vidéos (*.avi *.mp4 *.ogv *.mpg *.mpeg *.ogg *.mov *.wmv)"))
        self.pointage.openTheFile(filename)
        return

    def openfile(self):
        """
        Ouvre un dialogue pour choisir un fichier vidéo puis le charge
        """
        self.dbg.p(2, "rentre dans 'openfile'")
        dir_ = self._dir("videos")
        filename, hints = QFileDialog.getOpenFileName(
            self,
            self.tr("Ouvrir une vidéo"),
            dir_,
            self.tr("fichiers vidéos ( *.avi *.mp4 *.ogv *.mpg *.mpeg *.ogg *.wmv *.mov)"))
        self.pointage.openTheFile(filename)
        self.pointage.reinitialise_capture()
        return
    
    def renomme_le_fichier(self):
        self.dbg.p(2, "rentre dans 'renomme_le_fichier'")
        renomme_fichier = QMessageBox.warning(self, self.tr("Nom de fichier non conforme"),
                                              self.tr("""\
Le nom de votre fichier contient des caractères accentués ou des espaces.
Merci de bien vouloir le renommer avant de continuer"""))
        filename = QFileDialog.getOpenFileName(self, self.tr("Ouvrir une vidéo"),
                                               self._dir("videos", None),
                                               "*.avi")
        self.pointage.openTheFile(filename)
        return


    def propos(self):
        self.dbg.p(2, "rentre dans 'propos'")
        try:
            loc = locale.getdefaultlocale()[0][0:2]
        except TypeError as err:
            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
            loc = ''
        if loc in licence.keys():
            licence_XX = licence[loc] % Version
        else:
            licence_XX = licence["en"] % Version
        QMessageBox.information(None, "Licence", licence_XX)
        return

    def aide(self):
        self.dbg.p(2, "rentre dans 'aide'")
        lang = locale.getdefaultlocale()[0][0:2]
        helpfile = "%s/help-%s.html" % (self._dir("help"), lang)
        if os.path.exists(helpfile):
            command = "firefox --new-window %s" % helpfile
            status = subprocess.call(command, shell=True)
            if status != 0:
                command = "x-www-browser %s" % helpfile
                status = subprocess.call(command, shell=True)
        else:
            QMessageBox.warning(
                None, "Aide",
                self.tr("Désolé pas de fichier d'aide pour le langage {0}.").format(lang))
        return

    def rouvre(self, fichier):
        """
        Rouvre un fichier pymecavideo précédemment enregistré
        """
        self.dbg.p(2, "rentre dans 'rouvre'")
        
        lignes = open(fichier).readlines()
        # on récupère les données importantes
        lignes_config = [l for l in lignes if re.match("# .* = .*", l)]
        lignes_config = ["[DEFAULT]\n"] + [re.sub("^# ", "", l) \
                                           for l in lignes_config]
        self.prefs.config.read_string("".join(lignes_config))
        self.apply_preferences(rouvre=True)
        
        # donne la main au videoWidget pour préparer les pointages
        self.pointage.rouvre()
        # corrige éventuellement le nombre d'images par seconde à afficher
        self.lineEdit_IPS.setText(f"{self.pointage.framerate}")
        
        lignes_data = [l for l in lignes if l[0] != "#" and len(l.strip()) > 0]
        # on trouve les données en coupant là où il y a des séparations
        # par des espaces ou des tabulations, on ne conserve pas la
        # première ligne qui commence par "t x1 y1 ..." et aussi
        # on remplace les virgules décimales par des points
        data = [re.split(r"\s+", l.strip().replace(",", "."))
                for l in lignes_data][1:]
        self.pointage.restaure_pointages(
            data, self.prefs.config["DEFAULT"].getint("index_depart"))
        self.sync_img2others(self.pointage.index)
        self.affiche_echelle()  # on met à jour le widget d'échelle
        # coche les cases pour les sens des axes
        self.sens_axes.emit(self.pointage.sens_X, self.pointage.sens_Y)
        self.change_etat.emit("D")
        return

    def sync_img2others(self, i):
        """
        Fait en sorte que self.pointage.horizontalSlider et self.pointage.spinBox_image
        aient le numéro i
        @param i le nouvel index
        """
        self.pointage.spinBox_image.setValue(i)
        self.pointage.horizontalSlider.setValue(i)
        return
    
    def montre_volet_coord(self):
        """
        Met l'onglet des coordonnées sur le dessus
        """
        self.tabWidget.setCurrentIndex(2)
        return

    def montre_volet_video(self):
        """
        Met l'onglet des vidéos sur le dessus
        """
        self.tabWidget.setCurrentIndex(0)
        return

    def coche_axes(self, x, y):
        """
        Met à jour les caches à cocher des axes
        @param x sens de l'axe x (+1 ou -1)
        @param y sens de l'axe y (+1 ou -1)
        """
        self.dbg.p(2, "rentre dans 'coche_axes'")
        self.pointage.checkBox_abscisses.setChecked(x < 0)
        self.pointage.checkBox_ordonnees.setChecked(y < 0)
        return

    def stop_setText(self, text):
        """
        Change le texte du bouton STOP
        @param text le nouveau texte
        """
        self.pushButton_stopCalculs.setText(text)
        return

    def setStatus(self, text):
        """
        Précise la ligne de statut, qui commence par une indication de l'état
        @param text un texte pour terminer la ligne de statut
        """
        if self.roleEtat is None: return
        self.statusBar().showMessage(self.roleEtat[self.pointage.etat](self) + "| " + text)
        return

    def changeEtat(self, etat):
        """
        changement d'état : fait ce qu'il faut faire au niveau de la fenêtre
        principale puis renvoie aux autres widgets actifs
        """
        if etat == "debut":
            for obj in self.actionDefaire, self.actionRefaire, \
                self.actionCopier_dans_le_presse_papier, \
                self.menuE_xporter_vers, self.button_video, \
                self.actionSaveData, self.widget_chronophoto :

                obj.setEnabled(False)
            # décochage de widgets
            print("BUG renvoyer self.checkBox_Ec, self.checkBox_Em, self.checkBox_Ep ailleurs")
            for obj in self.checkBox_Ec, self.checkBox_Em, self.checkBox_Epp:
                obj.setChecked(False)
            self.actionExemples.setEnabled(True)
            self.tabWidget.setEnabled(True)
            # organisation des onglets
            self.tabWidget.setCurrentIndex(0)       # montre l'onglet video
            for i in range(1,4):
                self.tabWidget.setTabEnabled(i, False)  # autres onglets inactifs

            # initialisation de self.trajectoire_widget
            self.trajectoire_widget.chrono = False

            # on cache certains widgets
            print("BUG renvoyer self.radioButtonNearMouse self.radioButtonSpeedEveryWhere ailleurs")
            for obj in self.radioButtonNearMouse, \
                self.radioButtonSpeedEveryWhere:
                obj.hide()
            # autorise le redimensionnement de la fenêtre principale
            self.OKRedimensionnement.emit()

        elif etat == "A":
            if self.pointage.filename is None: return
            self.setWindowTitle(self.tr("Pymecavideo : {filename}").format(
                filename = os.path.basename(self.pointage.filename)))
            if not self.pointage.echelle_image:
                # sans échelle, on peut redimensionner la fenêtre
                self.OKRedimensionnement.emit()
            # ferme les widget d'affichages des x, y, v du 2eme onglet
            # si elles existent
            for plotwidget in self.dictionnairePlotWidget.values():
                plotwidget.parentWidget().close()
                plotwidget.close()
                del plotwidget
            for obj in self.menuE_xporter_vers, self.actionSaveData, \
                self.actionCopier_dans_le_presse_papier:
                obj.setEnabled(True)
            for i in 1, 2, 3:
                self.tabWidget.setTabEnabled(i, False)
                
            print("BUG pour A au sujet de self.checkBox_Ec, self.checkBox_Em, self.checkBox_Epp, self.spinBox_chrono")
            self.checkBox_Ec.setChecked(False)
            self.checkBox_Em.setChecked(False)
            self.checkBox_Epp.setChecked(False)
            self.spinBox_chrono.setMaximum(self.pointage.image_max)
            
            print("BUG pour A au sujet du grapheur")
            # désactive le grapheur si existant
            if self.graphWidget:
                plotItem = self.graphWidget.getPlotItem()
                plotItem.clear()
                plotItem.setTitle('')
                plotItem.hideAxis('bottom')
                plotItem.hideAxis('left')
                
            self.affiche_statut.emit(
               self.tr("Veuillez choisir une image (et définir l'échelle)"))
            self.montre_vitesses = False
            self.egalise_origine()
            self.init_variables(self.pointage.filename)
            
        elif etat == "AB":
            pass
        elif etat == "B":
            pass
        elif etat == "C":
            for obj in self.actionCopier_dans_le_presse_papier, \
                self.menuE_xporter_vers, self.actionSaveData:
                obj.setEnabled(False)

        elif etat == "D":
            pass
        elif etat == "E":
            pass
        self.setStatus("")
        self.pointage.change_etat.emit(etat)
        return

    def fixeLesDimensions(self):
        self.setMinimumWidth(self.width())
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.setFixedSize(QSize(self.width(), self.height()))
        return

    def defixeLesDimensions(self):
        """
        donne une taille minimale à la fenêtre, 640 x 480 ; 
        il s'y ajoute bien sûr les contraintes des widgets définis
        par l'interface utilisateur qui est créée à l'aide de designer.
        """
        self.setMinimumWidth(0)
        self.setMaximumWidth(16000000)
        self.setMinimumHeight(0)
        self.setMaximumHeight(16000000)
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
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
