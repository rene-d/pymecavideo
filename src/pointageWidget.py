# -*- coding: utf-8 -*-

"""
    pointageWidget, a module for pymecavideo:
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
    QSize, QTimer, QObject, QRect, QPoint, QPointF
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, \
    QCursor, QPen, QColor, QFont, QResizeEvent, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, \
    QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, \
    QTableWidgetSelectionRange

import os, time, re, sys
import locale

from version import Version
from vecteur import vecteur
from echelle import Echelle_TraceWidget
from image_widget import ImageWidget
from pointage import Pointage
from globdef import cible_icon, DOCUMENT_PATH, inhibe
from cadreur import openCvReader
from toQimage import toQImage
from suivi_auto import SelRectWidget
from detect import filter_picture
from dbg import Dbg

import interfaces.icon_rc

from interfaces.Ui_pointage import Ui_pointageWidget
from pointage import Pointage
from etats import Etats

class PointageWidget(QWidget, Ui_pointageWidget, Pointage, Etats):
    """
    Une classe qui affiche l'image d'une vidéo et qui gère le pointage
    d'objets mobiles dans cette vidéo. Elle gère les données de pointage
    et celles liées aux échelles de temps et d'espace

    paramètres du constructeur :
    @param parent un QWidget parent
    @param verbosite entre 1 et 3 pour les messages de débogage
    """

    def __init__(self, parent, verbosite = 0):
        self.dbg = Dbg(verbosite)
        QWidget.__init__(self, parent)
        Ui_pointageWidget.__init__(self)
        Pointage.__init__(self)
        Etats.__init__(self)
        self.setupUi(self)
        
        self.app = None                 # la fenêtre principale
        self.dbg = None                 # le débogueur
        self.etat = None
        self.etat_ancien = None
        self.hotspot = None             # vecteur (position de la souris)
        self.image = None               # l'image tirée du film
        self.origine = vecteur(self.width()//2, self.height()//2)
        self.couleurs = [
            "red", "blue", "cyan", "magenta", "yellow", "gray", "green"] *2
        self.image_max = None      # numéro de la dernière image de la vidéo
        self.framerate = None      # nombre d'images par seconde
        # dimensions natives des images de la vidéo
        self.largeurFilm, self.hauteurFilm = None, None
        self.a_une_image = False   # indication quant à une image disponible
        self.imageExtraite = None  # référence de l'image courante
        self.lance_capture = False # un pointage est en cours
        self.echelle_trace = None  # widget pour tracer l'échelle
        self.selRect = None        # un objet gérant la sélection par rectangle
        self.lance_cature = False  # devient vrai quand on commence à pointer
        self.auto = False          # devient vrai pour le pointage automatique
        self.motifs_auto = []      # liste de motifs pour le suivi auto
        self.pointsProbables = {}  # dict. de points proches de la détection ?
        self.refait_point = False  # on doit repointer une date
        self.pointageOK = False    # il est possible de faire un pointage
        self.pointageCursor = None # le curseur pour le pointage
        
       # fait un beau gros curseur
        cible_pix = QPixmap(cible_icon).scaledToHeight(32)
        self.pointageCursor = QCursor(cible_pix)

        self.connecte_ui()
        self.connecte_signaux()
        return

    ########### signaux #####################
    update_imgedit = pyqtSignal(int, int, int) # met à jour la dimension d'image
    dimension_data = pyqtSignal(int)
    stopCalculs = pyqtSignal()
    
    ########### connexion des signaux #######
    def connecte_signaux(self):
        self.update_imgedit.connect(self.affiche_imgsize)
        self.dimension_data.connect(self.redimensionne_data)
        self.stopCalculs.connect(self.stopComputing)
        return

    def connecte_ui(self):
        """
        Connecte des signaux issus de l'UI
        """
        self.lineEdit_IPS.textChanged.connect(self.verifie_IPS)
        self.spinBox_objets.valueChanged.connect(self.dimension_data)
        self.pushButton_defait.clicked.connect(self.efface_point_precedent)
        self.pushButton_refait.clicked.connect(self.refait_point_suivant)
        self.Bouton_Echelle.clicked.connect(self.demande_echelle)
        self.Bouton_lance_capture.clicked.connect(self.debut_capture)
        self.pushButton_reinit.clicked.connect(self.reinitialise_capture)
        self.pushButton_origine.clicked.connect(
            self.nouvelle_origine)
        self.checkBox_abscisses.stateChanged.connect(self.change_sens_X)
        self.checkBox_ordonnees.stateChanged.connect(self.change_sens_Y)
        self.pushButton_rot_droite.clicked.connect(self.tourne_droite)
        self.pushButton_rot_gauche.clicked.connect(self.tourne_gauche)
        self.pushButton_stopCalculs.clicked.connect(self.stopComputing)
        
        return

    def setApp(self, app):
        """
        Crée une relation avec la fenêtre principale, et son débogueur
        @param app le fenêtre principale (QMainWindoWidget)
        """
        self.app = app
        self.dbg = app.dbg
        self.video.setApp(app)
        self.zoom_zone.setApp(app)
        return


    def affiche_imgsize(self, w, h, r):
        """
        Affiche la taille de l'image
        @param w largeur de l'image
        @param h hauteur de l'image
        @param r rotation de l'image
        """
        self.imgdimEdit.setText(f"{w} x {h} ({r}°)")
        return
        
    def openTheFile(self, filename):
        """
        Ouvre le fichier de nom filename, enregistre les préférences de
        fichier vidéo.
        @param filename nom du fichier
        """
        self.dbg.p(2, "rentre dans 'openTheFile'")
        if not filename :
            return
        self.filename = filename
        if self.init_cvReader():
            # le fichier vidéo est OK, et son format est reconnu
            self.init_image()
            # s'il y avait déjà une échelle, il faut l'oublier,
            # quitter l'état A pour y revenir
            if self.echelle_image:
                self.clearEchelle()
                self.app.change_etat.emit("debut")
            self.app.change_etat.emit("A")
        else:
            QMessageBox.warning(
                None,
                self.tr("Erreur lors de la lecture du fichier"),
                self.tr("Le fichier<b>{0}</b> ...\nn'est peut-être pas dans un format vidéo supporté.").format(
                    filename))
        return
    
    def apply_preferences(self, rouvre=False):
        """
        Récupère les préférences sauvegardées, et en applique les données
        ici on s'occupe de ce qui se gère facilement au niveau du widget
        video
        @param rouvre est vrai quand on ouvre un fichier pymecavideo ; 
          il est faux par défaut
        """
        self.dbg.p(2, "rentre dans 'VideoWidget.apply_preferences'")
        d = self.app.prefs.config["DEFAULT"]
        self.filename = d["lastvideo"]
        self.video.rotation = d.getint("rotation")
        if os.path.isfile(self.filename):
            self.openTheFile(self.filename)
        else:
            # si le fichier video n'existe pas, inutile d'aller plus
            # loin dans la restauration des données !
            return
        self.reinitialise_capture()
        self.sens_X = d.getint("sens_x")
        self.sens_Y = d.getint("sens_y")
        self.origine = self.app.prefs.config.getvecteur("DEFAULT", "origine")
        if rouvre:
            # on est en train de réouvrir un fichier pymecavideo
            # et on considère plus de données
            #!!!! self.premiere_image_pointee = d.getint("index_depart")
            self.deltatT = d.getfloat("deltat")
            self.dimensionne(d.getint("nb_obj"), self.deltaT, self.image_max)
            self.echelle_image.longueur_reelle_etalon = d.getfloat('etalon_m')
            p1 = self.app.prefs.config.getvecteur("DEFAULT", "etalon_org")
            p2 = self.app.prefs.config.getvecteur("DEFAULT", "etalon_ext")
            if p1 != vecteur(0,0) and p2 != vecteur(0,0):
                self.echelle_image.p1 = p1
                self.echelle_image.p2 = p2
            else:
                self.echelle_image.p1 = None
                self.echelle_image.p2 = None
        # coche les cases du sens des axes
        self.app.sens_axes.emit(self.sens_X, self.sens_Y)
        return

    def init_cvReader(self):
        """
        Initialise le lecteur de flux vidéo pour OpenCV
        et recode la vidéo si nécessaire.
        """
        self.dbg.p(2, "rentre dans 'init_cvReader', ouverture de %s" %
                   (self.filename))
        self.cvReader = openCvReader(self.filename)
        time.sleep(0.1)
        if not self.cvReader.ok:
            QMessageBox.warning(None, "Format vidéo non pris en charge",
                                self.tr("Le format de cette vidéo n'est pas pris en charge par pymecavideo"))
        else:
            return True

    def init_image(self):
        """
        initialise certaines variables lors le la mise en place d'une 
        nouvelle vidéo
        """
        self.dbg.p(2, "rentre dans 'init_image'")
        self.index = 1
        self.extract_image(1)
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = \
            self.cvReader.recupere_avi_infos(self.video.rotation)
        self.ratio = self.largeurFilm / self.hauteurFilm
        self.calcul_deltaT()
        # on dimensionne les données pour les pointages
        self.redimensionne_data(self.nb_obj)
        self.affiche_image()
        return

    def extract_image(self, index):
        """
        extrait une image de la video à l'aide d'OpenCV ; met à jour
        self.pointageOK s'il est licite de pointer dans l'état actuel;
        met à jour le curseur à utiliser aussi
        @param index le numéro de l'image (commence à 1)

        @return un boolen (ok), et l'image au format d'openCV ; l'image
          au bon format pour Qt est dans self.imageExtraite
        """
        self.dbg.p(2, "rentre dans 'extract_image' " + 'index : ' + str(index))
        ok, image_opencv = self.cvReader.getImage(index, self.video.rotation)
        if not ok:
            self.app.affiche_statut.emit(
                self.tr("Pymecavideo n'arrive pas à lire l'image"))
            return False, None
        self.a_une_image = ok
        self.imageExtraite = toQImage(image_opencv)
        # il est licite de pointer dans l'état D à condition
        # qu'il n'y ait encore aucun pointage, ou que l'index soit
        # connexe aux pointages existants
        self.pointageOK = \
            self.app.etat in ("D", "E") and \
            (not self or index in range(self.premiere_image() - 1, \
                                        self.derniere_image() + 2))
        if self.pointageOK:
            # beau gros curseur seulement si le pointage est licite ;
            self.setCursor(self.pointageCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
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
        self.dbg.p(2, "rentre dans 'calcul_deltaT'")
        if rouvre:
            # se produit quand on lit un deltaT depuis un fichier mecavideo
            IPS = round(1/self.deltaT)
            self.app.lineEdit_IPS.setText(str(IPS))
        else:
            if not ips_from_line_edit:
                self.deltaT = 1 / self.framerate
                # mets à jour le widget contenant les IPS
                self.app.pointage.lineEdit_IPS.setText(str(self.framerate))
            else:
                IPS = int(self.app.lineEdit_IPS.text())
                self.framerate = IPS
                self.deltaT = 1 / IPS
        return
    
    def redimensionne_data(self, dim):
        """
        redimensionne self.data (fonction de rappel connectée au signal
        self.dimension_data)
        @param dim la nouvelle dimension des données
          (en nombre d'objets à suivre)
        """
        self.dbg.p(2, "rentre dans 'redimensionne_data'")
        if self.image_max and self.deltaT:
            self.dimensionne(dim, self.deltaT, self.image_max)
            # self.app.cree_tableau(nb_suivis = self.nb_obj)
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
            self.framerate = int(self.lineEdit_IPS.text())
            self.deltaT = 1 / self.framerate
            self.redimensionne_data(self.nb_obj)
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
            text = f"{self.pointage.video.echelle_image.longueur_reelle_etalon:.3f}")
        reponse = reponse.replace(",", ".")
        ok = ok and pattern_float.match(reponse) and float(reponse) > 0
        if not ok:
            self.affiche_statut.emit(self.tr(
                "Merci d'indiquer une échelle valable : {} ne peut pas être converti en nombre.").format(reponse))
            self.demande_echelle()
            return
        reponse = float(reponse)
        self.pointage.video.echelle_image.etalonneReel(reponse)
        self.etat_ancien = self.etat # conserve pour plus tard
        self.change_etat.emit("C")
        job = EchelleWidget(self.pointage.video)
        job.show()
        return
    
    def debut_capture(self):
        """
        Fonction de rappel du bouton Bouton_lance_capture

        Passe à l'état D ou AB, selon self.checkBox_auto
        """
        prochain_etat = "AB" if self.pointage.checkBox_auto.isChecked() else "D"
        self.change_etat.emit(prochain_etat)
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
        ChoixOrigineWidget(parent=self.pointage.video, app=self).show()
        return

    def change_sens_X(self):
        self.dbg.p(2, "rentre dans 'change_sens_X'")
        if self.checkBox_abscisses.isChecked():
            self.pointage.video.sens_X = -1
        else:
            self.pointage.video.sens_X = 1
        self.change_axe_origine.emit()

    def change_sens_Y(self):
        self.dbg.p(2, "rentre dans 'change_sens_Y'")
        if self.checkBox_ordonnees.isChecked():
            self.pointage.video.sens_Y = -1
        else:
            self.pointage.video.sens_Y = 1
        self.change_axe_origine.emit()

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
        self.pointage.video.rotation = (self.pointage.video.rotation + increment) % 360
        self.dbg.p(2, "Dans 'tourne_image' self rotation vaut" +
                   str(self.pointage.video.rotation))

        # gestion de l'origine et de l'échelle :
        self.dbg.p(3, f"Dans 'tourne_image' avant de tourner, self.origine {self.pointage.video.origine}, largeur video {self.pointage.video.width()}, hauteur video {self.pointage.video.height()}")
        self.redimensionneSignal.emit(True)
        return

    def affiche_image(self, index= None):
        '''
        À condition qu'on ait ouvert le fichier vidéo,
        extrait l'image courante ou l'image spécifiée
        par l'index, et affiche cette image
        @param index permet de modifier l'image courante si c'est un entier
          (None par défaut)
        '''
        if index is not None: self.index = index
        if not self.filename or self.index is None or self.image_max is None:
            return
        self.dbg.p(2, f"rentre dans 'affiche_image' self.index = {self.index} self.image_max = {self.image_max}")
        if self.index <= self.image_max:
            self.extract_image(self.index)  # 2ms
            self.placeImage(self.imageExtraite, self.ratio)
        elif self.index > self.image_max:
            self.index = self.image_max
            self.lance_capture = False
        return
    
    def reinit_origine(self):
        """
        Replace l'origine au centre de l'image
        """
        self.origine = vecteur(self.image_w//2, self.image_h//2)
        return

    def reinitialise_capture(self):
        """
        Efface toutes les données de la capture en cours et prépare une nouvelle
        session de capture. Retourne à l'état A
        """
        self.dbg.p(2, "rentre dans 'reinitialise_capture'")
        # oublie self.echelle_image
        self.clearEchelle()
        if self.echelle_trace is not None:
            self.echelle_trace.hide()
        self.echelle_trace = None
        self.app.echelle_modif.emit(self.tr("Définir l'échelle"),
                                    "background-color:None;")
        self.index = 1
        self.remontre_image()
        # reinitialisation du widget video
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setEnabled(True)
        self.reinit_origine()
        self.pointsProbables = {}
        self.motifs_auto = []
        # retire les objets déjà pointés
        self.redimensionne_data(self.nb_obj)
        self.sens_X = self.sens_Y = 1
        self.app.sens_axes.emit(self.sens_X, self.sens_Y)
        # passage par deux états afin de forcer une réinitialisation complète
        self.app.change_etat.emit("debut")
        self.app.change_etat.emit("A")
        return

    def remontre_image(self):
        """
        Il peut être nécessaire de remontrer l'image après un changement
        de self.video.rotation
        """
        self.extract_image(self.index)
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = \
            self.cvReader.recupere_avi_infos(self.video.rotation)
        self.ratio = self.largeurFilm / self.hauteurFilm
        self.affiche_image()
        return
    
    def efface_point_precedent(self):
        """
        revient au point précédent
        """
        self.dbg.p(2, "rentre dans 'efface_point_precedent'")
        if inhibe("defaire",100): return # corrige un bug de Qt 5.15
        if not self.peut_defaire(): return
        self.defaire()
        # dernière image à afficher
        der = self.derniere_image()
        if der:
            self.index = self.derniere_image() + 1
        else:
            self.purge_defaits() # si on a retiré le dernier pointage visible
            if self.index > 1: self.index -= 1
        self.clic_sur_video_ajuste_ui()
        return
    
    def refait_point_suivant(self):
        """rétablit le point suivant après un effacement
        """
        self.dbg.p(2, "rentre dans 'refait_point_suivant'")
        if inhibe("refaire",100): return # corrige un bug de Qt 5.15
        self.refaire()
        # ce serait moins long de remettre juste une ligne dans le tableau
        self.app.recalculLesCoordonnees()
        if self.index < self.image_max:
            self.index += 1
        self.clic_sur_video_ajuste_ui()
        return

    def enregistre_ui(self):
        self.dbg.p(2, "rentre dans 'enregistre_ui'")
        if self.data and self.echelle_image:
            base_name = os.path.splitext(os.path.basename(self.filename))[0]
            defaultName = os.path.join(DOCUMENT_PATH, base_name+'.mecavideo')
            fichier = QFileDialog.getSaveFileName(
                self,
                self.tr("Enregistrer le projet pymecavideo"),
                defaultName,
                self.tr("Projet pymecavideo (*.mecavideo)"))
            self.enregistre(fichier[0])
        else :
            QMessageBox.critical(None, self.tr("Erreur lors de l'enregistrement"), self.tr("Il manque les données, ou l'échelle"))
        return
    
    def enregistre(self, fichier):
        """
        Enregistre les données courantes dans un fichier,
        à un format CSV, séparé par des tabulations
        """
        self.dbg.p(2, "rentre dans 'enregistre'")
        sep_decimal = "."
        if locale.getdefaultlocale()[0][0:2] == 'fr':
            # en France, le séparateur décimal est la virgule
            sep_decimal = ","
        if not fichier:
            return
        # mise à jour des préférences, afin d'en faire aussi l'en-tête
        # pour le fichier pymecavideo
        self.savePrefs()
        with open(fichier, 'w') as outfile:
            message = self.tr("temps en seconde, positions en mètre")
            outfile.write(self.entete_fichier(message))
            donnees = self.csv_string(
                sep = "\t", unite = "m",
                debut = self.premiere_image(),
                origine = self.origine
            ).replace(".",sep_decimal)
            outfile.write(donnees)
        return

    def savePrefs(self):
        d = self.app.prefs.defaults
        d['version'] = f"pymecavideo {Version}"
        d['proximite'] = str(self.app.radioButtonNearMouse.isChecked())
        d['lastvideo'] = self.filename
        d['videodir'] = os.path.dirname(self.filename)
        d['niveaudbg'] = str(self.dbg.verbosite)
        d['sens_x'] = str(self.sens_X)
        d['sens_y'] = str(self.sens_Y)
        d["taille_image"] = f"({self.image_w},{self.image_h})"
        d['rotation'] = str(self.video.rotation)
        d['origine'] = f"({round(self.origine.x)}, {round(self.origine.y)})"
        d['index_depart'] = str(self.premiere_image())
        d['etalon_m'] = str(self.echelle_image.longueur_reelle_etalon)
        d['etalon_px'] = str(self.echelle_image.longueur_pixel_etalon())
        d['etalon_org'] = self.echelle_image.p1.toIntStr() \
            if self.echelle_image else "None"
        d['etalon_ext'] = self.echelle_image.p2.toIntStr() \
            if self.echelle_image else "None"
        d['deltat'] = str(self.deltaT)
        d['nb_obj'] = str(len(self.suivis))
        self.app.prefs.save()
        
    def stopComputing(self):
        self.dbg.p(2, "rentre dans 'stopComputing'")
        self.pileDeDetections = []  # vide la liste des points à détecter encore
        # la routine self.detecteUnPoint reviendra à l'état D après que
        # le dernier objet aura été détecté
        return

