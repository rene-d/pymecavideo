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
from echelle import Echelle_TraceWidget
from image_widget import ImageWidget, Zoom
from pointage import Pointage
from globdef import cible_icon, DOCUMENT_PATH, inhibe, pattern_float
from cadreur import openCvReader
from toQimage import toQImage
from suivi_auto import SelRectWidget
from detect import filter_picture
from dbg import Dbg
from suivi_auto import SelRectWidget
from choix_origine import ChoixOrigineWidget
from pointage import Pointage
from etatsPointage import Etats
from echelle import EchelleWidget, echelle
from detect import filter_picture


import interfaces.icon_rc

from interfaces.Ui_pointage import Ui_pointageWidget


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

        self.app = None            # la fenêtre principale
        self.dbg = None            # le débogueur
        self.etat = "A"            # état initial ; différent de "debut"
        self.image = None          # l'image tirée du film
        self.origine = vecteur()   # origine du repère
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
        self.filename = None       # nom du fichier video
        self.selRect = None        # sélecteur de zones à suivre
        self.indexMotif = 0        # le numéro du motif à entourer
        self.pileDeDetections = [] # pile d'index d'images où détecter
        
        # fait un beau gros curseur
        cible_pix = QPixmap(cible_icon).scaledToHeight(32)
        self.pointageCursor = QCursor(cible_pix)
        self.zoom_zone = Zoom(parent=self)
        self.zoom_zone.setFixedSize(100,100)

        self.connecte_ui()
        self.connecte_signaux()
        return

    ########### signaux #####################
    update_imgedit = pyqtSignal(int, int, int) # met à jour la dimension d'image
    update_origine = pyqtSignal(float, float)  # met à jour l'origine
    dimension_data = pyqtSignal(int)           # redimensionne les données
    stopCalculs = pyqtSignal()                 # arrete le pointage auto
    label_zoom = pyqtSignal(str)               # change le label du zoom
    update_zoom = pyqtSignal(vecteur)          # agrandit une portion d'image
    disable_zoom = pyqtSignal()                # desactive la fenetre de zoom
    remet_zoom = pyqtSignal()                  # remet la fenetre de zoom
    echelle_modif = pyqtSignal(str, str)       # modifie le bouton d'échelle
    apres_echelle = pyqtSignal()               # après dénition de l'échelle
    selection_motif_done = pyqtSignal()        # prêt à commencer la détection
    fin_pointage = pyqtSignal()                # après un pointage
    fin_pointage_manuel = pyqtSignal(QEvent)   # après un pointage manuel
    stop_n = pyqtSignal(str)                   # refait le texte du bouton STOP
    change_axe_origine = pyqtSignal()          # inverse un des axes du repère
    sens_axes = pyqtSignal(int, int)           # coche les cases des axes
    montre_etalon = pyqtSignal()               # montre l'étalon utilisé
    
    ########### connexion des signaux #######
    def connecte_signaux(self):
        self.update_imgedit.connect(self.affiche_imgsize)
        self.update_origine.connect(self.updateOrigine)
        self.dimension_data.connect(self.redimensionne_data)
        self.stopCalculs.connect(self.stopComputing)
        self.label_zoom.connect(self.labelZoom)
        self.update_zoom.connect(self.loupe)
        self.disable_zoom.connect(self.annule_loupe)
        self.remet_zoom.connect(self.remet_loupe)
        self.echelle_modif.connect(self.setButtonEchelle)
        self.apres_echelle.connect(self.restaureEtat)
        self.fin_pointage.connect(self.termine_pointage)
        self.fin_pointage_manuel.connect(self.termine_pointage_manuel)
        self.selection_motif_done.connect(self.suiviDuMotif)
        self.stop_n.connect(self.stop_setText)
        self.sens_axes.connect(self.coche_axes)
        self.montre_etalon.connect(self.feedbackEchelle)

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
        Crée une relation avec la fenêtre principale, son débogueur et
        ses préférences
        @param app le fenêtre principale (QMainWindoWidget)
        """
        self.app = app
        self.dbg = app.dbg
        self.prefs = app.prefs
        self.video.setParent(self)
        self.zoom_zone.setApp(app)
        self.change_axe_origine.connect(self.app.egalise_origine)
        return


    def updateOrigine(self, rx, ry):
        """
        Met à jour l'origine
        @param rx ratio horizontal
        @param ry ratio vertical
        """
        self.origine = vecteur(self.origine.x * rx, self.origine.y * ry)
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
            self.app.redimensionneSignal.emit(True)
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
        self.sens_axes.emit(self.sens_X, self.sens_Y)
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
            QMessageBox.warning(
                None,
                self.tr("Format vidéo non pris en charge"),
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
        self.video.rotation = 0
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
            self.etat in ("D", "E") and \
            (not self or index in range(self.premiere_image() - 1, \
                                        self.derniere_image() + 2))
        if self.pointageOK:
            # beau gros curseur seulement si le pointage est licite ;
            self.video.setCursor(self.pointageCursor)
        else:
            self.video.setCursor(Qt.CursorShape.ArrowCursor)
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
                self.lineEdit_IPS.setText(str(self.framerate))
            else:
                IPS = int(self.lineEdit_IPS.text())
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
            text = f"{self.echelle_image.longueur_reelle_etalon:.3f}")
        reponse = reponse.replace(",", ".")
        ok = ok and pattern_float.match(reponse) and float(reponse) > 0
        if not ok:
            self.affiche_statut.emit(self.tr(
                "Merci d'indiquer une échelle valable : {} ne peut pas être converti en nombre.").format(reponse))
            self.demande_echelle()
            return
        reponse = float(reponse)
        self.echelle_image.etalonneReel(reponse)
        self.app.change_etat.emit("C")
        job = EchelleWidget(self.video, self)
        job.show()
        return
    
    def debut_capture(self):
        """
        Fonction de rappel du bouton Bouton_lance_capture

        Passe à l'état D ou AB, selon self.checkBox_auto
        """
        self.app.change_etat.emit(
            "AB" if self.checkBox_auto.isChecked() else "D")
        return
    
    def nouvelle_origine(self):
        """
        Permet de déplacer l'origine du référentiel de la caméra
        """
        self.dbg.p(2, "rentre dans 'nouvelle_origine'")
        nvl_origine = QMessageBox.information(
            self,
            self.tr("NOUVELLE ORIGINE"),
            self.tr("Choisissez, en cliquant sur la vidéo le point qui sera la nouvelle origine"))
        ChoixOrigineWidget(self.video, self).show()
        return

    def change_sens_X(self):
        self.dbg.p(2, "rentre dans 'change_sens_X'")
        if self.checkBox_abscisses.isChecked():
            self.sens_X = -1
        else:
            self.sens_X = 1
        self.video.update()
        self.change_axe_origine.emit()

    def change_sens_Y(self):
        self.dbg.p(2, "rentre dans 'change_sens_Y'")
        if self.checkBox_ordonnees.isChecked():
            self.sens_Y = -1
        else:
            self.sens_Y = 1
        self.video.update()
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
        self.video.rotation = (self.video.rotation + increment) % 360
        self.dbg.p(2, "Dans 'tourne_image' self rotation vaut" +
                   str(self.video.rotation))

        # gestion de l'origine et de l'échelle :
        self.dbg.p(3, f"Dans 'tourne_image' avant de tourner, self.origine {self.origine}, largeur video {self.video.width()}, hauteur video {self.video.height()}")
        self.app.redimensionneSignal.emit(True)
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
            self.video.placeImage(
                self.imageExtraite, self.ratio, self.largeurFilm)
            self.reinit_origine()
        elif self.index > self.image_max:
            self.index = self.image_max
            self.lance_capture = False
        return
    
    def reinit_origine(self):
        """
        Replace l'origine au centre de l'image
        """
        self.origine = vecteur(self.video.image_w//2, self.video.image_h//2)
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
        self.echelle_modif.emit(self.tr("Définir l'échelle"),
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
        self.sens_axes.emit(self.sens_X, self.sens_Y)
        self.app.change_etat.emit("A")
        self.disable_zoom.emit()
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
        self.app.sync_img2others(self.index)
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
        self.app.sync_img2others(self.index)
        self.prepare_futur_clic()
        return
    
    def refait_point_suivant(self):
        """rétablit le point suivant après un effacement
        """
        self.dbg.p(2, "rentre dans 'refait_point_suivant'")
        if inhibe("refaire",100): return # corrige un bug de Qt 5.15
        self.refaire()
        # ce serait moins long de remettre juste une ligne dans le tableau
        self.app.coord.recalculLesCoordonnees()
        if self.index < self.image_max:
            self.index += 1
        self.app.sync_img2others(self.index)
        self.prepare_futur_clic()
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
        d['proximite'] = str(self.app.trajectoire.radioButtonNearMouse.isChecked())
        d['lastvideo'] = self.filename
        d['videodir'] = os.path.dirname(self.filename)
        d['niveaudbg'] = str(self.dbg.verbosite)
        d['sens_x'] = str(self.sens_X)
        d['sens_y'] = str(self.sens_Y)
        d["taille_image"] = f"({self.video.image_w},{self.video.image_h})"
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

    def labelZoom(self, label):
        """
        Met à jour le label au-dessus du zoom
        @param label le nouveau label
        """
        self.zoomLabel.setText(label)
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
            if self.image_max:
                self.horizontalSlider.setMaximum(int(self.image_max))
                self.spinBox_image.setMaximum(int(self.image_max))
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

    def affiche_echelle(self):
        """
        affiche l'échelle courante pour les distances sur l'image
        """
        self.dbg.p(2, "rentre dans 'affiche_echelle'")
        if self.echelle_image.isUndef():
            self.echelleEdit.setText(
                self.tr("indéf."))
        else:
            epxParM = self.echelle_image.pxParM()
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
        self.app.actionDefaire.setEnabled(value)
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
        self.app.actionRefaire.setEnabled(value)
        return

    def annule_loupe(self):
        self.dbg.p(2, "rentre dans 'annule_loupe'")

        self.zoom_zone.setVisible(0)

    def remet_loupe(self):
        self.dbg.p(2, "rentre dans 'remet_loupe'")

        self.zoom_zone.setVisible(1)

    def loupe(self, position):
        """
        Agrandit deux fois une partie de self.video.image et la met
        dans la zone du zoom, puis met à jour les affichages de coordonnées ;
        sauf dans l'état B (pointage auto)
        @param position le centre de la zone à agrandir
        """
        self.dbg.p(2, "rentre dans 'loupe'")

        if self.etat == "B" : return
        elif (self.app.etat=='D' or self.app.etat=='C' or self.app.etat=='E'):
            self.dbg.p(3, f"Mets à jour ZOOM à la position {position}")

            self.zoom_zone.fait_crop(self.video.image, position)
            xpx, ypx, xm, ym = self.coords(position)
            self.editXpx.setText(f"{xpx}")
            self.editYpx.setText(f"{ypx}")
            self.editXm.setText(f"{xm}")
            self.editYm.setText(f"{ym}")
            self.zoom_zone.raise_()

            return

    def coords(self, p):
        """
        @param p un point, vecteur de coordonnées entières
        @return les valeurs de x, y en px et puis en mètre (formatées :.2e)
        """
        # on se rapporte à l'origine du repère
        p = p - self.origine
        # et aux sens des axes
        p.redresse(self)
        
        if not self.echelle_image:
            return int(p.x), int(p.y), self.tr("indéf."), self.tr("indéf.")
        return int(p.x), int(p.y), \
            f"{p.x/self.echelle_image.pxParM():.2e}", \
            f"{p.y/self.echelle_image.pxParM():.2e}"

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

    def sync_slider2spinbox(self):
        """
        recopie la valeur du slider vers le spinbox
        """
        self.dbg.p(2, "rentre dans 'sync_slider2spinbox'")
        self.spinBox_image.setValue(self.horizontalSlider.value())
        return
        

    def sync_spinbox2others(self):
        """
        Affiche l'image dont le numéro est dans self.pointage.spinBox_image et
        synchronise self.horizontalSlider
        """
        self.dbg.p(2, "rentre dans 'sync_spinbox2others'")
        self.index = self.spinBox_image.value()
        self.horizontalSlider.setValue(self.index)
        self.affiche_image()
        return

    def feedbackEchelle(self):
        """
        affiche une trace au-dessus du self.job, qui reflète les positions
        retenues pour l'échelle
        """
        self.dbg.p(2, "rentre dans 'feedbackEchelle'")
        if self.echelle_trace:
            self.echelle_trace.hide()
        self.echelle_trace = Echelle_TraceWidget(
            self.video, self.echelle_image.p1, self.echelle_image.p2)
        # on garde les valeurs pour le redimensionnement
        self.echelle_trace.show()
        if self.echelle:
            self.echelle_modif.emit(self.tr("Refaire l'échelle"), "background-color:orange;")
        return

    def capture_auto(self):
        """
        fonction appelée au début de l'état AB : prépare la sélection
        des motifs à suivre en capture automatique
        """
        self.dbg.p(2, "rentre dans 'capture_auto'")
        self.auto = True # inhibe le pointage à la souris !
        # recouvre l'image avec le widget selRect pour définir des
        # rectangles pour chaque motif à suivre
        self.zoomLabel.setText(self.tr("Zone à suivre n° {zone} x, y =").format(zone=self.suivis[0]))
        self.selRect = SelRectWidget(self.video, self)
        self.selRect.show()
        return

    def suiviDuMotif(self):
        self.dbg.p(2, "rentre dans 'suiviDuMotif'")
        if len(self.motifs_auto) == self.nb_obj:
            self.dbg.p(3, "selection des motifs finie")
            self.selRect.hide()
            self.indexMotif = 0
            self.pileDeDetections = []
            for i in range(self.index, self.image_max+1):
                self.pileDeDetections.append(i)
            self.dbg.p(3, "self.pileDeDetections : %s" % self.pileDeDetections)
            self.app.change_etat.emit("B")
        else:
            self.label_zoom.emit(self.tr("Zone à suivre n° {zone} x, y =").format(zone=self.suivis[len(self.motifs_auto)]))
        return

    # @time_it
    def detecteUnPoint(self):
        """
        méthode (re)lancée pour les détections automatiques de points
        traite une à une les données empilées dans self.pileDeDetections
        et relance un signal si la pile n'est pas vide après chacun
        des traitements.
        """
        self.dbg.p(2, f"rentre dans 'detecteUnPoint', pileDeDetection = {self.pileDeDetections}")
        if self.pileDeDetections:
            # on dépile un index de détections à faire et on met à jour
            # le bouton de STOP
            self.stop_n.emit(f"STOP ({self.pileDeDetections.pop(0)})")
            ok, image = self.cvReader.getImage(
                self.index, self.video.rotation, rgb=False)
            # puis on boucle sur les objets à suivre et on
            # détecte leurs positions
            # Ça pourrait bien se faire dans des threads, en parallèle !!!
            for i, part in enumerate(self.motifs_auto):
                self.indexMotif = i
                zone_proche = self.pointsProbables.get(self.objet_courant, None)
                point = filter_picture(part, image, zone_proche)
                self.pointsProbables[self.objet_courant] = point
                echelle = self.video.image_w / self.largeurFilm
                # on convertit selon l'échelle, et on recentre la détection
                # par rapport au motif `part`
                self.storePoint(vecteur(
                    echelle*(point[0]+part.shape[1]/2),
                    echelle*(point[1]+part.shape[0]/2)))
                # le point étant détecté, on passe à l'objet suivant
                # et si nécessaire à l'image suivante
                self.objetSuivant()
            # programme le suivi du point suivant après un délai de 50 ms,
            # pour laisser une chance aux évènement de l'interface graphique
            # d'être traités en priorité
            QTimer.singleShot(50, self.detecteUnPoint)
        else:
            # fin de la détection automatique
            self.auto = False
            # si la pile d'images à détecter a été vidée par self.stopComputing,
            # il faut passer à l'image suivante si possible
            self.fin_pointage.emit()
            self.app.change_etat.emit("D")
        return

    def storePoint(self, point):
        """
        enregistre un point, quand self.index et self.objet_courant
        sont déjà bien réglés.
        @param point la position à enregistrer
        """
        self.dbg.p(2, "rentre dans 'storePoint'")
        if self.lance_capture or self.auto:
            self.pointe(self.objet_courant, point, index=self.index-1)
            self.fin_pointage.emit()
        return

    def termine_pointage(self):
        self.dbg.p(2, "rentre dans 'clic_sur_video'")
        self.purge_defaits() # oublie les pointages à refaire
        self.prepare_futur_clic()
        self.app.sync_img2others(self.index)
        return

    def termine_pointage_manuel(self, event):
        """
        Fonction appelée en cas de pointage manuel sur l'image de la vidéo
        après un mouserelease (bouton gauche)
        """
        if self.pointageOK:
            self.app.change_etat.emit("E")
            self.pointe(self.objet_courant, event, index=self.index-1)
            self.objetSuivant()
            self.fin_pointage.emit()
            if self.refait_point and self.objet_courant == self.suivis[0]:
                # on a été délégué pour corriger le tableau
                # le dernier objet est pointé, retour au tableau de coords
                self.refait_point = False
                self.app.show_coord.emit()
            self.app.update()
            self.update_zoom.emit(vecteur(qPoint = event.position()))

        return
    
    def prepare_futur_clic(self):
        """
        Ajuste l'interface utilisateur pour attendre un nouveau clic
        """
        self.dbg.p(2, "rentre dans 'prepare_futur_clic'")
        self.affiche_image()
        self.affiche_point_attendu(self.objet_courant)
        self.enableDefaire(self.peut_defaire())
        self.enableRefaire(self.peut_refaire())
        return

    def stop_setText(self, text):
        """
        Change le texte du bouton STOP
        @param text le nouveau texte
        """
        self.pushButton_stopCalculs.setText(text)
        return

    def objetSuivant(self):
        """
        passage à l'objet suivant pour le pointage.
        revient au premier objet quand on a fait le dernier, et
        change d'image aussi
        """
        i = self.suivis.index(self.objet_courant)
        if i < self.nb_obj - 1 :
            self.objet_courant = self.suivis[i+1]
            self.label_zoom.emit(self.tr("Pointage ({obj}) ; x, y =").format(obj = self.objet_courant))
        else:
            # on passe à l'image suivante, et on revient au premier objet
            self.objet_courant = self.suivis[0]
            if self.index < self.image_max:
                self.index +=1
            # on revient à l'état D sauf en cas de suivi automatique
            # auquel cas l'état E perdure
            if not self.auto:
                self.app.change_etat.emit("D")
            else:
                # on reste dans l'état E, néanmoins on synchronise
                # les contrôles de l'image
                self.app.image_n.emit(self.index)
        
        return

    def affiche_point_attendu(self, obj):
        """
        Renseigne sur le numéro d'objet du point attendu
        affecte la ligne de statut et la ligne sous le zoom
        @param obj l'objet courant
        """
        self.dbg.p(2, "rentre dans 'affiche_point_attendu'")
        self.app.affiche_statut.emit(self.tr("Cliquez sur l'objet : {0}").format(obj))
        return

    def vecteursVitesse(self, echelle_vitesse):
        """
        Calcule les vecteurs vitesse affichables étant donné la collection
        de points. Un vecteur vitesse a pour origine un point de la 
        trajectoire, et sa direction, sa norme sont basées sur le point
        précédent et le point suivant ; il faut donc au moins trois pointages
        pour que le résultat ne soit pas vide.

        @param echelle_vitesse le nombre de pixels pour 1 m/s
        @return un dictionnaire objet => [(org, ext), ...] où org et ext
          sont l'origine et l'extrémité d'un vecteur vitesse
        """
        self.dbg.p(2, "rentre dans 'vecteursVitesse'")
        result = {obj : [] for obj in self.suivis}
        trajectoires = self.les_trajectoires()
        for obj in self.suivis:
            precedent = trajectoires[obj][0]
            suivant = None
            for i in range(1, len(trajectoires[obj]) - 1):
                # itération le long de la trajectoire, sauf
                # sur les points extrêmes.
                if suivant:
                    point = suivant # le point est l'ancien suivant s'il existe
                else:
                    point = trajectoires[obj][i]
                suivant = trajectoires[obj][i+1]
                vitesse = (self.pointEnMetre(suivant) - self.pointEnMetre(precedent)) * (1 / self.deltaT / 2)
                # attention, l'axe Y de l'écran est vers le bas !!
                if self.sens_Y == 1: vitesse.miroirY()
                result[obj].append ((point, point + (vitesse * echelle_vitesse)))
                precedent = point # on conserve les coordonnées pour la suite
        return result

    def rouvre(self):
        """
        Ici c'est la partie dévolue au pointageWidget quand on rouvre un
        fichier pymecavideox
        """
        self.sens_axes.emit(self.sens_X, self.sens_Y)
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = \
            self.cvReader.recupere_avi_infos(self.video.rotation)
        self.ratio = self.largeurFilm / self.hauteurFilm
        # réapplique la préférence de deltat, comme openCV peut se tromper
        self.deltaT = float(self.prefs.config["DEFAULT"]["deltat"])
        self.framerate = round(1/self.deltaT)
        self.lineEdit_IPS.setText(f"{self.framerate}")
        self.sens_axes.emit(self.sens_X, self.sens_Y)
        # on met à jour le widget d'échelle
        self.affiche_echelle()
        self.feedbackEchelle()
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

    def restaure_pointages(self, data, premiere_image_pointee) :
        """
        Rejoue les pointages issus d'un fichier pymecavideo
        @param data une liste de listes de type [t, x1, y1, ..., xn, yn]
        @param premiere_image_pointee la toute première image pointée
          (au moins 1)
        """
        self.dimensionne(self.nb_obj, self.deltaT, self.image_max)
        for i in range(len(data)) :
            for obj in self.suivis:
                j = int(obj)*2-1 # index du début des coordonnées xj, yj
                if len(data[i]) > j:
                    x, y = data[i][j:j + 2]
                    # À ce stade x et y sont en mètre
                    # on remet ça en pixels
                    x = self.origine.x + self.sens_X * \
                        round(float(x) * self.echelle_image.pxParM())
                    y = self.origine.y - self.sens_Y * \
                        round(float(y) * self.echelle_image.pxParM())
                    self.pointe(
                        obj, vecteur(x, y),
                        index = i + premiere_image_pointee - 1)
        # affiche la dernière image pointée
        der = self.derniere_image()
        if der is not None:
            if der < self.image_max:
                self.index = der + 1
            else:
                self.index = self.image_max
        else:
            self.index = 1
        self.prepare_futur_clic()
        self.echelle_modif.emit(self.tr("Refaire l'échelle"), "background-color:orange;")
        return
    
    def refait_point_depuis_tableau(self, qpbn ):
        """
        fonction de rappel déclenchée quand on clique dans la dernière
        colonne du tableau
        @param qbbn le bouton qui a été cliqué pour en arriver là
        """
        self.dbg.p(2, "rentre dans 'refait_point_depuis_tableau'")
        self.refait_point=True
        self.objet_courant = self.suivis[0]
        self.index = qpbn.index_image
        self.prepare_futur_clic()
        self.app.show_video.emit()
        return

    def entete_fichier(self, msg=""):
        """
        Crée l'en-tête du fichier pymecavideo
        On recopie sous forme de commentaires préfixée par "# "
        tout le fichier de configuration sauf la ligne "[DEFAULT]"
        puis on ajoute le message
        @param msg le message
        @return le texte de l'en-tête (multi-ligne)
        """
        self.dbg.p(2, "rentre dans 'entete_fichier'")
        config = open(self.prefs.conffile).readlines()
        return "".join(["# "+l for l in config[1:]]) + "# " + msg + "\n"

