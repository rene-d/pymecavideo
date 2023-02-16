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
from echelle import EchelleWidget, echelle

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
        self.etat = None
        self.etat_ancien = None
        # version minimale du fichier de configuration :
        self.min_version = version(7, 3, ".0-1")
        self.hauteur = 1
        self.largeur = 0
        self.ratio = 4/3
        self.decalh = 0
        self.decalw = 0
        self.dictionnairePlotWidget = {}

        # Mode plein écran
        self.plein_ecran = False
        QShortcut(QKeySequence("F11"), self, self.basculer_plein_ecran)

        g = QApplication.instance().screens()[0].geometry()
        self.height_screen, self.width_screen = g.height(), g.width()

        self.origine_trace = None
        
        self.setupUi(self)

        self.dbg = Dbg(0)
        for o in opts:
            if ('-d' in o[0]) or ('--debug' in o[0]):
                self.dbg = Dbg(o[1])
                print(self.dbg)

        self.prefs = Preferences(self)

        # définition des widgets importants
        self.graphWidget = None
        self.zoom_zone.setApp(self)
        self.trajectoire_widget.setApp(self)

        # on passe la main au videowidget pour faire les liaisons aux
        # autres widgets de la fenêtre principale
        self.video.setApp(self)

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
        self.definit_messages_statut()
        
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
                self.video.openTheFile(filename)
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
        taille = self.prefs.config.getvecteur("DEFAULT", "taille")
        rect = self.geometry()
        self.setGeometry(rect.x(), rect.y(), int(taille.x), int(taille.y))
        d = self.prefs.config["DEFAULT"]
        self.radioButtonNearMouse.setChecked(d["proximite"] == "True")
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
        self.premier_chargement_fichier_mecavideo = False #gere l'origine au premier chargement
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
        self.video.index = 1  # image à afficher
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
    stopRedimensionnement = pyqtSignal()
    OKRedimensionnement = pyqtSignal()
    redimensionneSignal = pyqtSignal(bool)
    updateProgressBar = pyqtSignal()
    change_etat = pyqtSignal(str)
    apres_echelle = pyqtSignal()
    echelle_modif = pyqtSignal(str, str)    # modifie le bouton d'échelle
    show_coord = pyqtSignal()               # montre l'onglet des coordonnées
    show_video = pyqtSignal()               # montre l'onglet des vidéos
    sens_axes = pyqtSignal(int, int)        # coche les cases des axes
    stop_n = pyqtSignal(str)                # refait le texte du bouton STOP
    update_zoom = pyqtSignal(vecteur)       # agrandit une portion d'image
    image_n = pyqtSignal(int)               # modifie les contrôles d'image
    affiche_statut = pyqtSignal(str)        # modifie la ligne de statut
    afficheXY = pyqtSignal(int, int, str, str) # position de la souris
    
    def ui_connections(self):
        """connecte les signaux de Qt"""
        self.dbg.p(2, "rentre dans 'ui_connections'")

        #connexion de signaux de menus
        self.actionOuvrir_un_fichier.triggered.connect(self.openfile)
        self.actionExemples.triggered.connect(self.openexample)
        self.action_propos.triggered.connect(self.propos)
        self.actionAide.triggered.connect(self.aide)
        #self.actionDefaire.triggered.connect(self.video.efface_point_precedent)
        self.actionRefaire.triggered.connect(self.video.refait_point_suivant)
        self.actionQuitter.triggered.connect(self.close)
        self.actionSaveData.triggered.connect(self.video.enregistre_ui)
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
        self.lineEdit_IPS.textChanged.connect(self.verifie_IPS)
        self.comboBox_style.currentIndexChanged.connect(self.dessine_graphe)
        self.pushButton_save.clicked.connect(self.enregistreChrono)
        self.spinBox_chrono.valueChanged.connect(self.changeChronoImg)
        self.pushButton_save_plot.clicked.connect(self.enregistre_graphe)
        self.spinBox_objets.valueChanged.connect(self.video.dimension_data)
        self.pushButton_defait.clicked.connect(self.video.efface_point_precedent)
        self.pushButton_refait.clicked.connect(self.video.refait_point_suivant)
        self.Bouton_Echelle.clicked.connect(self.demande_echelle)
        self.Bouton_lance_capture.clicked.connect(self.debut_capture)
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
        self.pushButton_reinit.clicked.connect(self.video.reinitialise_capture)
        self.pushButton_origine.clicked.connect(
            self.nouvelle_origine)
        self.checkBox_abscisses.stateChanged.connect(self.change_sens_X)
        self.checkBox_ordonnees.stateChanged.connect(self.change_sens_Y)
        self.pushButton_rot_droite.clicked.connect(self.tourne_droite)
        self.pushButton_rot_gauche.clicked.connect(self.tourne_gauche)

        # connexion de signaux spéciaux
        self.change_axe_origine.connect(self.egalise_origine)
        self.stopRedimensionnement.connect(self.fixeLesDimensions)
        self.OKRedimensionnement.connect(self.defixeLesDimensions)
        self.redimensionneSignal.connect(self.redimensionneFenetre)
        self.pushButton_stopCalculs.clicked.connect(self.video.stopCalculs)
        self.updateProgressBar.connect(self.updatePB)
        self.change_etat.connect(self.etatUI)
        self.apres_echelle.connect(self.restaureEtat)
        self.echelle_modif.connect(self.setButtonEchelle)
        self.show_coord.connect(self.montre_volet_coord)
        self.show_video.connect(self.montre_volet_video)
        self.sens_axes.connect(self.coche_axes)
        self.stop_n.connect(self.stop_setText)
        self.update_zoom.connect(self.loupe)
        self.image_n.connect(self.sync_img2others)
        self.affiche_statut.connect(self.setStatus)
        self.afficheXY.connect(self.affiche_xy)
        
        return

    def affiche_xy(self, xpx, ypx, xm, ym):
        """
        affiche les coordonnées du point central du zoom
        @param xpx abscisse en pixel (int)
        @param ypx ordonnée en pixel (int)
        @param xm abscisse en mètre (str)
        @param ym ordonnée en mètre (str)
        """
        self.editXYpx.setText(f"{xpx}, {ypx}")
        self.editXYm.setText(f"{xm}, {ym}")
        return
        

    def definit_messages_statut(self):
        """
        Définit le début des messages à envoyer dans la ligne de statut;
        il s'agit de définir le dictionnaire self.roleEtat de structure
        etat => fonction de rappel pour renvoyer une chaîne appropriée
        """
        def msgDebut(app):
            return self.tr("Début : ouvrez un fichier, ou un exemple des aides")
        def msgA(app):
            return self.tr("Fichier vidéo : {filename} ... donnez l'échelle ou démarrez le pointage").format(filename = os.path.basename(app.video.filename))
        def msgAB(app):
            return self.tr("Préparation du pointage automatique : sélectionnez les objets à suivre, au nombre de {n}").format(n = app.video.nb_obj)
        def msgB(app):
            return self.tr("Pointage automatique en cours : il peut être interrompu par le bouton STOP")
        def msgC(app):
            return self.tr("Définissez l'échelle, par un tirer-glisser sur l'image")
        def msgD(app):
            return self.tr("Pointage manuel : cliquez sur le premier objet à suivre")
        def msgE(app):
            return self.tr("Pointage manuel : il reste encore des objets à pointer, on en est à {obj}").format(obj = app.video.objet_courant)
        
        self.roleEtat = { # résumé de ce que représente un état
            "debut" : msgDebut,
            "A" :     msgA,
            "AB" :    msgAB,
            "B" :     msgB,
            "C" :     msgC,
            "D" :     msgD,
            "E" :     msgE,
        }
        return

    def etatUI(self, etat):
        """
        Mise en place d'un état de l'interface utilisateur, voir la
        documentation dans le fichier etat_pymecavideo.html

        après l'état C, il faut tenir compte d'un ancien état, A*/D*
        """
        fonctions = { # fonctions de rappel pour chaque changement d'état
            "debut": self.etatDebut,
            "A":     self.etatA,
            "AB":    self.etatAB,
            "B":     self.etatB,
            "C":     self.etatC,
            "D":     self.etatD,
            "E":     self.etatE,
        }

        if self.etat == etat: return # inutile de changer !
        self.dbg.p(1, f"========> État précédent = {self.etat}. État suivant = {etat}")
        self.etat = etat
        if self.etat not in fonctions:
            raise Exception(
                f"L'état doit être {', '.join(list(fonctions.keys()))}, or il est « {repr(self.etat)} »")
        self.etat = etat
        # appel de la fonction liée à l'état courant
        fonctions[self.etat]()
        self.setStatus("")
        return
    
    def etatDebut(self):
        """
        On y arrive quand on lance pymecavideo, et qu’aucune vidéo
        n’est passée, ni par argument, ni par le fichier de
        configuration.

        Tous les onglets sont désactivés ; idéalement, une aide
        pour dire d’aller chercher un fichier vidéo apparaît.
        """
        self.zoomLabel.setText(self.tr(" Zoom autour de x, y ="))
        # désactivation de widgets
        for obj in self.actionDefaire, self.actionRefaire, \
            self.actionCopier_dans_le_presse_papier, self.menuE_xporter_vers, \
            self.actionSaveData, self.widget_chronophoto, self.spinBox_image, \
            self.pushButton_rot_droite, self.pushButton_rot_gauche, \
            self.pushButton_stopCalculs, \
            self.button_video, self.label_nb_de_points, \
            self.spinBox_objets, self.Bouton_Echelle, \
            self.checkBox_auto, self.Bouton_lance_capture, \
            self.pushButton_reinit, self.pushButton_origine, \
            self.pushButton_defait, self.pushButton_refait, \
            self.checkBox_abscisses, self.checkBox_ordonnees, \
            self.label_IPS, self.lineEdit_IPS :
            
            obj.setEnabled(False)
            
        # décochage de widgets
        for obj in self.checkBox_Ec, self.checkBox_Em, self.checkBox_Epp:
            obj.setChecked(False)
        
        # activation de widgets
        for obj in self.tabWidget, self.actionExemples:

            obj.setEnabled(True)

        # on cache certains widgets
        for obj in self.radioButtonNearMouse, \
            self.radioButtonSpeedEveryWhere, self.pushButton_stopCalculs:

            obj.hide()

        # organisation des onglets
        self.tabWidget.setCurrentIndex(0)       # montre l'onglet video
        for i in range(1,4):
            self.tabWidget.setTabEnabled(i, False)  # autres onglets inactifs

         # initialisation de self.trajectoire_widget
        self.trajectoire_widget.chrono = False

        # désactive les contôles de l'image
        self.imgControlImage(False)

        # marque "indéf." dans l'afficheur d'échelle à gauche
        self.affiche_echelle()

        # mise à jour de styles
        self.Bouton_Echelle.setStyleSheet("background-color:None;")

        # autorise le redimensionnement de la fenêtre principale
        self.defixeLesDimensions()

        # inactive le spinner pour les incréments de plus d'une image
        # voir la demande de Isabelle.Vigneau@ac-versailles.fr, 15 Sep 2022
        # non encore implémentée
        self.imgno_incr.hide()
        self.spinBox.hide()

        return
        
    def etatA(self):
        """
        Une vidéo est connue et on en affiche une image.

        Le premier onglet est actif, on voit une image de la
        vidéo, les contrôles pour se déplacer dans le film sont
        actifs, on peut modifier le nombre d’objets à pointer, Le
        bouton Démarrer est visible et actif.

        Inutile de montrer le bouton de réinitialisation

        Sur l’image de la vidéo, le curseur est ordinaire.
        """
        self.zoomLabel.setText(self.tr(" Zoom autour de x, y ="))
        if not self.video.echelle_image:
            self.affiche_echelle() # marque "indéf."
            self.echelle_modif.emit(self.tr("Définir l'échelle"),
                                    "background-color:None;")
            # comme il n'y a pas d'échelle, on peut redimensionner la fenêtre
            self.defixeLesDimensions()
            if self.video.echelle_trace:
                self.video.echelle_trace.hide()
        # ferme les widget d'affichages des x, y, v du 2eme onglet
        # si elles existent
        for plotwidget in self.dictionnairePlotWidget.values():
            plotwidget.parentWidget().close()
            plotwidget.close()
            del plotwidget
        self.init_variables(self.video.filename)
        # active les contrôle de l'image, montre l'image
        self.imgControlImage(True)
        self.video.affiche_image()
        # réactive plusieurs widgets
        for obj in self.label_nb_de_points, self.pushButton_reinit, \
            self.spinBox_objets, self.Bouton_Echelle, \
            self.checkBox_auto, self.Bouton_lance_capture, \
            self.pushButton_origine, self.actionCopier_dans_le_presse_papier, \
            self.checkBox_abscisses, self.checkBox_ordonnees, \
            self.label_IPS, self.lineEdit_IPS, \
            self.menuE_xporter_vers, self.actionSaveData :

            obj.setEnabled(True)

        # si une échelle est définie, on interdit les boutons de rotation
        # sinon on autorise ces boutons
        rotation_possible = not self.video.echelle_image
        for obj in self.pushButton_rot_droite, self.pushButton_rot_gauche :
            obj.setEnabled(rotation_possible)
                
        # ajuste le nombre d'objets suivis
        if self.video.suivis:
            self.spinBox_objets.setValue(self.video.nb_obj)
        else:
            self.video.dimension_data.emit(1)
            self.spinBox_objets.setValue(1)

        # desactive d'autres widgets
        self.pushButton_stopCalculs.setEnabled(False)
        self.pushButton_stopCalculs.hide()
        self.enableDefaire(False)
        self.enableRefaire(False)
        self.checkBox_abscisses.setCheckState(Qt.CheckState.Unchecked)
        self.checkBox_ordonnees.setCheckState(Qt.CheckState.Unchecked)
        self.checkBox_auto.setCheckState(Qt.CheckState.Unchecked)
        for i in 1, 2, 3:
            self.tabWidget.setTabEnabled(i, False)
        self.checkBox_Ec.setChecked(False)
        self.checkBox_Em.setChecked(False)
        self.checkBox_Epp.setChecked(False)
        
        # désactive le grapheur si existant
        if self.graphWidget:
            plotItem = self.graphWidget.getPlotItem()
            plotItem.clear()
            plotItem.setTitle('')
            plotItem.hideAxis('bottom')
            plotItem.hideAxis('left')
 
        """
        Prépare une session de pointage, au niveau de la
        fenêtre principale, et met à jour les préférences
        """
        d = self.prefs.defaults
        d['lastVideo'] = self.video.filename
        d['videoDir'] = os.path.dirname(self.video.filename)
        d['rotation'] = str(self.video.rotation)
        self.prefs.save()

        self.spinBox_image.setMinimum(1)
        self.spinBox_image.setValue(1)
        self.spinBox_chrono.setMaximum(self.video.image_max)
        self.spinBox_objets.setEnabled(True)
        self.tab_traj.setEnabled(0)

        self.affiche_statut.emit(
           self.tr("Veuillez choisir une image (et définir l'échelle)"))
        self.montre_vitesses = False
        self.egalise_origine()
        return

    def etatAB(self):
        """
        On y arrive en cliquant sur le bouton démarrer, si la case
        à cocher « pointage auto » était cochée. On doit définir,
        par tirer-glisser à la souris, autant de zones
        rectangulaires à suivre qu’il y a d’objets à pointer.

        Le premier onglet est actif, mais tous les widgets de
        contrôle y sont inactifs.
        """
        self.zoomLabel.setText(self.tr(" Zoom autour de x, y ="))
        # désactive plusieurs widgets
        for obj in self.pushButton_rot_droite, self.pushButton_rot_gauche, \
            self.label_nb_de_points, \
            self.spinBox_objets, self.Bouton_Echelle, \
            self.checkBox_auto, self.Bouton_lance_capture, \
            self.pushButton_origine, self.actionCopier_dans_le_presse_papier, \
            self.checkBox_abscisses, self.checkBox_ordonnees, \
            self.label_IPS, self.lineEdit_IPS, \
            self.menuE_xporter_vers, self.actionSaveData :

            obj.setEnabled(False)

        QMessageBox.information(
            None, "Capture Automatique",
            self.tr("""\
            Veuillez sélectionner un cadre autour du ou des objets que vous voulez suivre.
            Vous pouvez arrêter à tout moment la capture en appuyant sur le bouton STOP""",None))
        self.affiche_statut.emit(self.tr("Pointage Automatique"))
        self.imgControlImage(False)
        # on démarre la définition des zones à suivre
        self.video.capture_auto()
        return
        
    def etatB(self):
        """
        On y arrive quand les zones rectangulaires à suivre sont
        définies.

        Le premier onglet est actif, mais tous les widgets de contrôle
        y sont inactifs et on fait apparaître le bouton STOP
        """
        self.pushButton_stopCalculs.setText("STOP")
        self.pushButton_stopCalculs.setEnabled(True)
        self.pushButton_stopCalculs.show()
        self.update()
        # initialise la détection des points
        self.video.detecteUnPoint()
        return
    
    def etatC(self):
        """
        L’échelle est en cours de définition.

        Le premier onglet est actif, mais tous les boutons qu’on
        peut y voir sont inactifs jusqu’à la fin de la définition
        de l’échelle.

        Cet état peut se situer entre A et A, ou entre D et D,
        selon la valeur de self.etat_ancien.
        """
        self.zoomLabel.setText(self.tr(" Zoom autour de x, y ="))
        # désactive plusieurs widgets
        for obj in self.pushButton_rot_droite, self.pushButton_rot_gauche, \
            self.label_nb_de_points, \
            self.spinBox_objets, self.Bouton_Echelle, \
            self.checkBox_auto, self.Bouton_lance_capture, \
            self.pushButton_origine, self.actionCopier_dans_le_presse_papier, \
            self.checkBox_abscisses, self.checkBox_ordonnees, \
            self.label_IPS, self.lineEdit_IPS, \
            self.menuE_xporter_vers, self.actionSaveData :

            obj.setEnabled(False)
        
        return
        
    def etatD(self):
        """
        Une vidéo est connue et on en affiche une image.
        Le pointage a été démarré, manuellement, ou un pointage
        automatique vient de finir.Tous les onglets sont actifs.

        Les contrôles pour changer d’image sont actifs, et le seul
        autre bouton actif sur le premier onglet est celui qui
        permet de changer d’échelle. Dans tous les cas, le bouton STOP
        y est caché

        Le pointage n’est possible que dans deux cas :

        quand aucune image n’a été pointée quand le pointage à
        venir est voisin de pointages existants : sur une image
        déjà pointée, ou juste avant, ou juste après.

        Quand le pointage est possible et seulement alors, le
        curseur de souris a la forme d’une grosse cible ;
        idéalement il identifie aussi l’objet à pointer.
        """
        self.zoomLabel.setText(self.tr("Pointage ({obj}) ; x, y =").format(obj = self.video.suivis[0]))
        # empêche de redimensionner la fenêtre
        self.fixeLesDimensions()
        # prépare le widget video
        self.video.setFocus()
        if self.video.echelle_trace: self.video.echelle_trace.lower()
        # on cache le bouton STOP
        self.pushButton_stopCalculs.setEnabled(False)
        self.pushButton_stopCalculs.hide()
        # on force extract_image afin de mettre à jour le curseur de la vidéo
        self.video.extract_image(self.horizontalSlider.value())
        
        self.video.affiche_point_attendu(self.video.suivis[0])
        self.video.lance_capture = True
         # les widgets de contrôle de l'image sont actifs ici
        self.imgControlImage(True)
        
        # tous les onglets sont actifs
        for i in 1, 2, 3:
            self.tabWidget.setTabEnabled(i, True)
            
        # comme l'onglet 2 est actif, il faut s'occuper du statut des
        # boutons pour les énergies !
        for obj in self.checkBox_Ec, self.checkBox_Em, self.checkBox_Epp:
            obj.setChecked(False)
            obj.setEnabled(bool(self.video.echelle_image))
            
        # mise à jour des menus
        self.actionSaveData.setEnabled(True)
        self.actionCopier_dans_le_presse_papier.setEnabled(True)
        self.comboBox_referentiel.setEnabled(True)
        self.pushButton_select_all_table.setEnabled(True)

        self.comboBox_referentiel.clear()
        self.comboBox_referentiel.insertItem(-1, "camera")
        for obj in self.video.suivis:
            self.comboBox_referentiel.insertItem(
                -1, self.tr("objet N° {0}").format(str(obj)))

        # désactive des boutons et des cases à cocher
        for obj in self.pushButton_origine, self.checkBox_abscisses, \
            self.checkBox_ordonnees, self.checkBox_auto, \
            self.Bouton_lance_capture, self.pushButton_rot_droite, \
            self.pushButton_rot_gauche :

            obj.setEnabled(False)

        # si aucune échelle n'a été définie, on place l'étalon à 1 px pour 1 m.
        if self.video.echelle_image.mParPx() == 1:
            self.video.echelle_image.longueur_reelle_etalon = 1
            self.video.echelle_image.p1 = vecteur(0, 0)
            self.video.echelle_image.p2 = vecteur(0, 1)

        # active le bouton de réinitialisation
        self.pushButton_reinit.setEnabled(True)
        return

    def etatE(self):
        """
        On est en train de pointer une série d’objets pour la même date.
        Le curseur de souris a la forme d’une grosse cible ;
        idéalement il identifie aussi l’objet à pointer.

        Durant ce pointage, les contrôles de changement d’image
        sont inactifs, ainsi que les onglets autres que le
        premier.
        """
        self.zoomLabel.setText(self.tr("Pointage ({obj}) ; x, y =").format(obj = self.video.objet_courant))
        self.imgControlImage(False)
        for i in 1, 2, 3:
            self.tabWidget.setTabEnabled(i, False)        
        return
        
    def restaureEtat(self):
        """
        Restauration de l'état A ou D après (re)définition de l'échelle
        """
        self.change_etat.emit(self.etat_ancien)
        return
        
    
    def egalise_origine(self):
        """
        harmonise l'origine : recopie celle de la vidéo vers le
        widget des trajectoires et redessine les deux.
        """
        self.trajectoire_widget.origine_mvt = self.video.origine
        self.trajectoire_widget.update()
        self.video.update()
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
            self.spinBox_chrono.setMaximum(int(self.video.image_max))
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
        return

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

    def refait_echelle(self):
        # """Permet de retracer une échelle et de recalculer les points"""
        self.dbg.p(2, "rentre dans 'refait_echelle'")
        self.recalculLesCoordonnees()
        return

    def nouvelle_origine(self):
        """
        Permet de déplacer l'origine du référentiel de la caméra
        """
        self.dbg.p(2, "rentre dans 'nouvelle_origine'")
        nvl_origine = QMessageBox.information(
            self,
            "NOUVELLE ORIGINE",
            "Choisissez, en cliquant sur la vidéo le point qui sera la nouvelle origine")
        ChoixOrigineWidget(parent=self.video, app=self).show()
        return

    def tourne_droite(self):
        self.dbg.p(2, "rentre dans 'tourne_droite'")
        self.tourne_image("droite")

    def tourne_gauche(self):
        self.dbg.p(2, "rentre dans 'tourne_droite'")
        self.tourne_image("gauche")

    def tourne_image(self, sens):
        self.dbg.p(2, "rentre dans 'tourne_image'")
        if sens == "droite":
            increment = 90
        elif sens == "gauche":
            increment = -90
        self.video.rotation = (self.video.rotation + increment) % 360
        self.dbg.p(2, "Dans 'tourne_image' self rotation vaut" +
                   str(self.video.rotation))

        # gestion de l'origine et de l'échelle :
        self.dbg.p(3, f"Dans 'tourne_image' avant de tourner, self.origine {self.video.origine}, largeur video {self.video.width()}, hauteur video {self.video.height()}")
        self.redimensionneSignal.emit(True)
        return

    def change_sens_X(self):
        self.dbg.p(2, "rentre dans 'change_sens_X'")
        if self.checkBox_abscisses.isChecked():
            self.video.sens_X = -1
        else:
            self.video.sens_X = 1
        self.change_axe_origine.emit()

    def change_sens_Y(self):
        self.dbg.p(2, "rentre dans 'change_sens_Y'")
        if self.checkBox_ordonnees.isChecked():
            self.video.sens_Y = -1
        else:
            self.video.sens_Y = 1
        self.change_axe_origine.emit()

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
            self.video.remontre_image()
        else:
            self.video.affiche_image()
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
        self.dbg.p(2, "rentre dans 'recalculLesCoordonnees'")
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

    def montre_video(self):
        self.dbg.p(2, "rentre dans 'montre_video'")
        ref = self.comboBox_referentiel.currentText().split(" ")[-1]
        if len(ref) == 0 or ref == "camera":
            return
        c = Cadreur(int(ref), self.video)
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
        deltaT = self.video.deltaT
        m = float(m)
        g = float(g)

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
            X = self.video.dates
        elif grandeurX in self.locals :
            X = self.locals[grandeurX]
        if grandeurY == 't':
            Y = self.video.dates
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
            origine = vecteur(self.video.width() // 2, self.video.height() // 2)
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
                          self.video.refait_point_depuis_tableau( b ))
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
        if self.video.echelle_image:
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
                # n'existe que s'il y a eu un pointage
                derniere = self.video.nb_obj * (2 + colonnes_sup) +1
                self.tableWidget.setCellWidget(
                    i, derniere, self.bouton_refaire(i))
            return
        
        self.video.iteration_data(
            cb_temps, cb_point,
            unite = "m" if self.video.echelle_image else "px")
        
        # rajoute des boutons pour refaire le pointage
        # au voisinage immédiat des zones de pointage
        colonne = self.video.nb_obj * (2 + colonnes_sup) +1
        if self.video.premiere_image() is None: return
        if self.video.premiere_image() > 1:
            i = self.video.premiere_image() - 2
            self.tableWidget.setCellWidget(i, colonne, self.bouton_refaire(i))
        if self.video.derniere_image() < len(self.video):
            i = self.video.derniere_image()
            self.tableWidget.setCellWidget(i, colonne, self.bouton_refaire(i))
        return

    def recommence_echelle(self):
        self.dbg.p(2, "rentre dans 'recommence_echelle'")
        self.tabWidget.setCurrentIndex(0)
        self.video.echelle_image = echelle()
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
        d["taille"] = f"({self.size().width()},{self.size().height()})"
        d["rotation"] = str(self.video.rotation)
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
        self.video.openTheFile(filename)
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
        self.video.openTheFile(filename)
        self.video.reinitialise_capture()
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
        self.video.openTheFile(filename)
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

    def verifie_IPS(self):
        self.dbg.p(2, "rentre dans 'verifie_IPS'")
        # si ce qui est rentré n'est pas un entier
        if not self.lineEdit_IPS.text().isdigit() and len(self.lineEdit_IPS.text()) > 0:
            QMessageBox.warning(
                self,
                self.tr("Le nombre d'images par seconde doit être un entier"),
                self.tr("merci de recommencer"))
        else:
            # la vérification est OK, donc on modifie l'intervalle de temps
            # et on refait le tableau de données sans changer le nombre
            # d'objets
            self.video.framerate = int(self.lineEdit_IPS.text())
            self.video.deltaT = 1 / self.video.framerate
            self.video.redimensionne_data(self.video.nb_obj)
        return
    
    def affiche_echelle(self):
        """
        affiche l'échelle courante pour les distances sur l'image
        """
        self.dbg.p(2, "rentre dans 'affiche_echelle'")
        if self.video.echelle_image.isUndef():
            self.echelleEdit.setText(
                self.tr("indéf."))
        else:
            epxParM = self.video.echelle_image.pxParM()
            if epxParM > 20:
                self.echelleEdit.setText("%.1f" % epxParM)
            else:
                self.echelleEdit.setText("%8e" % epxParM)
        self.echelleEdit.show()
        self.Bouton_Echelle.show()
        return

    def enableDefaire(self, value):
        """
        Contrôle la possibilité de défaire un clic
        @param value booléen
        """
        self.dbg.p(2, "rentre dans 'enableDefaire, %s'" % (str(value)))
        self.pushButton_defait.setEnabled(value)
        self.actionDefaire.setEnabled(value)
        # permet de remettre l'interface à zéro
        if not value:
            self.imgControlImage(True)
        return
    
    def enableRefaire(self, value):
        """
        Contrôle la possibilité de refaire un clic
        @param value booléen
        """
        self.dbg.p(2, "rentre dans 'enableRefaire, %s'" % (value))
        self.pushButton_refait.setEnabled(value)
        self.actionRefaire.setEnabled(value)
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
        self.video.rouvre()
        # corrige éventuellement le nombre d'images par seconde à afficher
        self.lineEdit_IPS.setText(f"{self.video.framerate}")
        
        lignes_data = [l for l in lignes if l[0] != "#" and len(l.strip()) > 0]
        # on trouve les données en coupant là où il y a des séparations
        # par des espaces ou des tabulations, on ne conserve pas la
        # première ligne qui commence par "t x1 y1 ..." et aussi
        # on remplace les virgules décimales par des points
        data = [re.split(r"\s+", l.strip().replace(",", "."))
                for l in lignes_data][1:]
        self.video.restaure_pointages(
            data, self.prefs.config["DEFAULT"].getint("index_depart"))
        self.sync_img2others(self.video.index)
        self.affiche_echelle()  # on met à jour le widget d'échelle
        # coche les cases pour les sens des axes
        self.sens_axes.emit(self.video.sens_X, self.video.sens_Y)
        self.change_etat.emit("D")
        return

    def debut_capture(self):
        """
        Fonction de rappel du bouton Bouton_lance_capture

        Passe à l'état D ou AB, selon self.checkBox_auto
        """
        prochain_etat = "AB" if self.checkBox_auto.isChecked() else "D"
        self.change_etat.emit(prochain_etat)
        return
    
    def demande_echelle(self):
        """
        demande l'échelle interactivement
        """
        self.dbg.p(2, "rentre dans 'demande_echelle'")
        reponse, ok = QInputDialog.getText(
            None,
            self.tr("Définir léchelle"),
            self.tr("Quelle est la longueur en mètre de votre étalon sur l'image ?"),
            text = f"{self.video.echelle_image.longueur_reelle_etalon:.3f}")
        reponse = reponse.replace(",", ".")
        ok = ok and pattern_float.match(reponse) and float(reponse) > 0
        if not ok:
            self.affiche_statut.emit(self.tr(
                "Merci d'indiquer une échelle valable : {} ne peut pas être converti en nombre.").format(reponse))
            self.demande_echelle()
            return
        reponse = float(reponse)
        self.video.echelle_image.etalonneReel(reponse)
        self.etat_ancien = self.etat # conserve pour plus tard
        self.change_etat.emit("C")
        job = EchelleWidget(self.video)
        job.show()
        return
    
    def sync_img2others(self, i):
        """
        Fait en sorte que self.horizontalSlider et self.spinBox_image
        aient le numéro i
        @param i le nouvel index
        """
        self.spinBox_image.setValue(i)
        self.horizontalSlider.setValue(i)
        return
    
    def sync_spinbox2others(self):
        """
        Affiche l'image dont le numéro est dans self.spinBox_image et
        synchronise self.horizontalSlider
        """
        self.dbg.p(2, "rentre dans 'sync_spinbox2others'")
        self.video.index = self.spinBox_image.value()
        self.horizontalSlider.setValue(self.video.index)
        self.video.affiche_image()
        return

    def sync_slider2spinbox(self):
        """
        recopie la valeur du slider vers le spinbox
        """
        self.dbg.p(2, "rentre dans 'sync_slider2spinbox'")
        self.spinBox_image.setValue(self.horizontalSlider.value())
        return
        

    def imgControlImage(self, state):
        """
        Gère les deux widgets horizontalSlider et spinBox_image
        @param state si state == True, les deux widgets sont activés
          et leurs signaux valueChanged sont pris en compte ;
          sinon ils sont désactivés ainsi que les signaux valueChanged
        """
        self.dbg.p(2, "rentre dans 'imgControlImage'")
        if state:
            self.horizontalSlider.setMinimum(1)
            self.spinBox_image.setMinimum(1)
            if self.video.image_max:
                self.horizontalSlider.setMaximum(int(self.video.image_max))
                self.spinBox_image.setMaximum(int(self.video.image_max))
            self.horizontalSlider.valueChanged.connect(
                self.sync_slider2spinbox)
            self.spinBox_image.valueChanged.connect(self.sync_spinbox2others)
        else:
            if self.horizontalSlider.receivers(self.horizontalSlider.valueChanged):
                self.horizontalSlider.valueChanged.disconnect()
            if self.spinBox_image.receivers(self.spinBox_image.valueChanged):
                self.spinBox_image.valueChanged.disconnect()
        self.horizontalSlider.setEnabled(state)
        self.spinBox_image.setEnabled(state)
        return

    def setButtonEchelle(self, text, style):
        """
        Signale fortement qu'il est possible de refaire l'échelle
        @param text nouveau texte du bouton self.Bouton_Echelle
        @param style un style CSS
        """
        self.Bouton_Echelle.setEnabled(True)
        self.Bouton_Echelle.setText(text)
        self.Bouton_Echelle.setStyleSheet(style)
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
        self.checkBox_abscisses.setChecked(x < 0)
        self.checkBox_ordonnees.setChecked(y < 0)
        return

    def stop_setText(self, text):
        """
        Change le texte du bouton STOP
        @param text le nouveau texte
        """
        self.pushButton_stopCalculs.setText(text)
        return

    def loupe(self, position):
        """
        Agrandit une partie de self.video.image et la met dans la zone du zoom
        @param position le centre de la zone à agrandir
        """
        self.zoom_zone.fait_crop(self.video.image, position)
        return

    def setStatus(self, text):
        """
        Précise la ligne de statut, qui commence par une indication de l'état
        @param text un texte pour terminer la ligne de statut
        """
        self.statusBar().showMessage(self.roleEtat[self.etat](self) + "| " + text)
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
