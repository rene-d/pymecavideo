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
import mimetypes

from export import Export, EXPORT_FORMATS
from toQimage import toQImage
from version import version, Version, str2version
from dbg import Dbg
from preferences import Preferences
from trajWidget import trajWidget
from glob import glob
from vecteur import vecteur
from echelle import echelle

import interfaces.icon_rc
from inspect import currentframe

from interfaces.Ui_pymecavideo import Ui_pymecavideo
from etatsMain import Etats

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



def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno

#from export_python import ExportDialog
# création précoce de l'objet application, déjà nécessaire pour traiter les bugs
app = QApplication(sys.argv)


#import qtiplotexport




class FenetrePrincipale(QMainWindow, Ui_pymecavideo, Etats):
    def __init__(self, parent=None, opts=[], args=[]):
        """
        le constructeur reçoit les données principales du logiciel :
        @param parent le widget parent, None pour une fenêtre principale
        @param opts les options de l'invocation bien rangées en tableau
        @param args les arguments restants après raitement des options
        """
        QMainWindow.__init__(self, parent)
        Ui_pymecavideo.__init__(self)
        Etats.__init__(self)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose)
        # version minimale du fichier de configuration :
        self.min_version = version(7, 3, ".0-1")
        self.wanted_image_size = vecteur() # taille souhaitée pour l'image
        self.nb_ajuste_image = 20          # nombre d'itérations pour y parvenir
        self.imgdim_hide = time.time() + 2 # moment pour cacher la taille
        self.etat = None                   # avant le système d'états

        # Mode plein écran
        self.plein_ecran = False
        QShortcut(QKeySequence("F11"), self, self.basculer_plein_ecran)

        try:
            g = QApplication.instance().screens()[0].geometry()
            self.height_screen, self.width_screen = g.height(), g.width()
        except:
            # il s'agit peut-être bien d'un test, joué sous xvfb-run
            # et dans ce cas QApplication.instance().screens() est vide
            self.height_screen, self.width_screen = 1024, 768

        self.setupUi(self)

        self.dbg = Dbg(0)
        for o in opts:
            if ('-d' in o[0]) or ('--debug' in o[0]):
                self.dbg = Dbg(o[1])
                print(self.dbg)

        self.prefs = Preferences(self)

        # définition des widgets importants
        self.pointage.setApp(self)
        self.trajectoire.setApp(self)
        self.coord.setApp(self)
        self.graph.setApp(self)

        # on cache le widget des dimensions de l'image
        self.hide_imgdim.emit()
        
        self.args = args

        self.platform = platform.system()

        # initialise les répertoires
        self._dir()


       # crée les action exportQactions du menu Fichier
        for key in sorted(EXPORT_FORMATS.keys()):
            action = QAction(EXPORT_FORMATS[key]
                             ['nom'], self.menuE_xporter_vers)
            action.triggered.connect(
                lambda checked, index=key: self.coord.export(index))
            self.menuE_xporter_vers.addAction(action)

        self.init_variables(self.prefs.defaults['lastVideo'])
        # connections internes
        self.connecte_ui()
         # met l'état à "debut"
        self.change_etat.emit("debut")

        # traite un argument ; s'il n'y en a pas, s'intéresse
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
            mt = mimetypes.guess_type(filename)[0]
            if mt is not None : 
                if mt.startswith("video/"):
                    OK = True
                    self.pointage.openTheFile(filename)
            else : 
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

    def check_prefs_version(self):
        """
        Vérifie la version du fichier de préférences
        @return 0 si la version esty trop ancienne, 1 si elle est voisine,
          2 quand tout va bien
        """
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
                    self.tr("La version du fichier de configuration, {version} est inférieure à {min_version} : le fichier de configuration ne peut pas être pris en compte").format(version = thisversion, min_version = self.min_version)))
            return 0
        elif thisversion < Version:
             QTimer.singleShot(
                50,
                lambda: QMessageBox.information(
                    self,
                    self.tr("Configuration ancienne"),
                    self.tr("La version du fichier de configuration, {version} est inférieure à {Version} : certaines dimensions peuvent être légèrement fausses.").format(version = thisversion, Version = Version)))
             return 1
        # le fichier de configuration a la bonne version, on applique ses
        # données
        return 2
        
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
        if not self.check_prefs_version(): return
        self.wanted_image_size = self.prefs.config.getvecteur(
            "DEFAULT", "taille_image")
        self.nb_ajuste_image = 20 # pas plus de 20 itérations
        self.adjust4image.emit()
       
        d = self.prefs.config["DEFAULT"]
        self.pointage.apply_preferences(rouvre = rouvre)
        self.trajectoire.apply_preferences()
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
        # contient les listes des abscisses, vitesses, énergies calculées par le grapheur.
        self.motif = []
        self.index_du_point = 0
        self.couleurs = ["red", "blue", "cyan", "magenta", "yellow", "gray",
                         "green"]  # correspond aux couleurs des points de la trajectoire
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
        return

    

    ############ les signaux spéciaux #####################
    selection_done = pyqtSignal()
    redimensionneSignal = pyqtSignal(bool)
    updateProgressBar = pyqtSignal()
    change_etat = pyqtSignal(str)
    show_coord = pyqtSignal()               # montre l'onglet des coordonnées
    show_video = pyqtSignal()               # montre l'onglet des vidéos
    adjust4image = pyqtSignal()             # adapte la taille à l'image
    hide_imgdim = pyqtSignal()              # cache la dimension de l'image
    affiche_statut = pyqtSignal(str)        # modifie la ligne de statut
    stopRedimensionnement = pyqtSignal()    # fixe la taille de la fenêtre
    OKRedimensionnement = pyqtSignal()      # libère la taille de la fenêtre
    image_n = pyqtSignal(int)               # modifie les contrôles d'image
    new_echelle = pyqtSignal()              # redemande l'échelle
    
    def connecte_ui(self):
        """connecte les signaux de Qt"""
        self.dbg.p(2, "rentre dans 'connecte_ui'")

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
            self.coord.presse_papier)
        self.actionRouvrirMecavideo.triggered.connect(self.rouvre_ui)

        # connexion de signaux de widgets
        self.tabWidget.currentChanged.connect(self.choix_onglets)

        # connexion de signaux spéciaux
        self.redimensionneSignal.connect(self.redimensionneFenetre)
        self.updateProgressBar.connect(self.updatePB)
        self.change_etat.connect(self.changeEtat)
        self.show_coord.connect(self.montre_volet_coord)
        self.show_video.connect(self.montre_volet_video)
        self.affiche_statut.connect(self.setStatus)
        self.adjust4image.connect(self.ajuste_pour_image)
        self.hide_imgdim.connect(self.cache_imgdim)
        self.stopRedimensionnement.connect(self.fixeLesDimensions)
        self.OKRedimensionnement.connect(self.defixeLesDimensions)
        self.image_n.connect(self.sync_img2others)
        self.new_echelle.connect(self.recommence_echelle)
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
            self.pointage.montre_etalon.emit()
            if self.pointage.etat not in ("debut", "A"):
                self.stopRedimensionnement.emit()
        
        return

    def egalise_origine(self):
        """
        harmonise l'origine : recopie celle de la vidéo vers le
        widget des trajectoires et redessine les deux.
        """
        self.trajectoire.trajW.origine_mvt = self.pointage.origine
        self.trajectoire.update()
        self.pointage.update()
        return
    
    def updatePB(self):
        self.qmsgboxencode.updateProgressBar()

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
        self.trajectoire.trajW.maj()
        return

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
            self.trajectoire.trace.emit("absolu")
        elif self.tabWidget.currentIndex() == 2:
            # onglet des coordonnées
            self.coord.affiche_tableau()
        elif self.tabWidget.currentIndex() == 3:
            # onglet du grapheur
            self.graph.affiche_grapheur()
        return

    def recommence_echelle(self):
        self.dbg.p(2, "rentre dans 'recommence_echelle'")
        self.tabWidget.setCurrentIndex(0)
        self.pointage.echelle_image = echelle()
        self.pointage.affiche_echelle()
        self.pointage.demande_echelle()
        return

    def closeEvent(self, event):
        """
        Un crochet pour y mettre toutes les procédures à faire lors
        de la fermeture de l'application.
        """
        self.dbg.p(2, "rentre dans 'closeEvent'")
        d = self.prefs.config["DEFAULT"]
        d["taille_image"] = f"({self.pointage.video.image_w},{self.pointage.video.image_h})"
        d["rotation"] = str(self.pointage.video.rotation)
        self.prefs.save()
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
        self.pointage.video.rotation = 0 #quand on ouvre un nouveau fichier, la rotation doit être remise par défaut
        return
    
    def renomme_le_fichier(self):
        self.dbg.p(2, "rentre dans 'renomme_le_fichier'")
        renomme_fichier = QMessageBox.warning(
            self,
            self.tr("Nom de fichier non conforme"),
            self.tr("""\
Le nom de votre fichier contient des caractères accentués ou des espaces.
Merci de bien vouloir le renommer avant de continuer"""))
        filename = QFileDialog.getOpenFileName(
            self,
            self.tr("Ouvrir une vidéo"),
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
        QMessageBox.information(
            None,
            self.tr("Licence"),
            licence_XX)
        return

    def aide(self):
        self.dbg.p(2, "rentre dans 'aide'")
        lang = locale.getlocale()[0][0:2]
        helpfile = "%s/help-%s.html" % (self._dir("help"), lang)
        if os.path.exists(helpfile):
            command = "firefox --new-window %s" % helpfile
            status = subprocess.call(command, shell=True)
            if status != 0:
                command = "x-www-browser %s" % helpfile
                status = subprocess.call(command, shell=True)
        else:
            QMessageBox.warning(
                None,
                self.tr("Aide"),
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

    def setStatus(self, text):
        """
        Précise la ligne de statut, qui commence par une indication de l'état
        @param text un texte pour terminer la ligne de statut
        """
        if self.etat is None : return
        self.statusBar().showMessage(self.roleEtat[self.etat](self) + "| " + text)
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
    elif "_" in locale:
        locale, _ = locale.split("_")
        langdir = os.path.join(FenetrePrincipale._dir("langues"),
                           r"pymecavideo_" + locale)
        if appTranslator.load(langdir):
            b = app.installTranslator(appTranslator)
    window = FenetrePrincipale(None, opts, args)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
