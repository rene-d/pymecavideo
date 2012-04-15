# -*- coding: utf-8 -*-

licence={}
licence['en']="""
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

licence['fr']=u"""
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
import sys
if sys.platform == "win32" or sys.argv[0].endswith(".exe"):
    import Error
    
from vecteur import vecteur
import os, thread, time, commands, linecache, codecs, re
import locale, getopt, pickle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtXml 

# création précoce de l'objet application, déjà nécessaire pour traiter les bugs
app = QApplication(sys.argv)

from glob import glob
from echelle import Label_Echelle, echelle
from math import sqrt
from label_video import Label_Video
from label_trajectoire import Label_Trajectoire
from label_origine import Label_Origine
from cadreur import Cadreur, openCvReader
from preferences import Preferences
from dbg import Dbg
from listes import listePointee
from version import Version
from label_auto import Label_Auto
#from altvideo import AltVideo
from dialogencode import QMessageBoxEncode

import qtiplotexport
from subprocess import *
import re

from mpl import traceur2d, MyMplCanvas
# on préfèrera définitivement le module mpl au module traceur ?
#from traceur import traceur2d

import threading
import platform, subprocess
import tempfile

from globdef import PATH, APP_DATA_PATH, GetChildStdErr, IMG_PATH, \
     VIDEO, SUFF, VIDEO_PATH, CONF_PATH, IMG_PATH, ICON_PATH, LANG_PATH, \
     DATA_PATH,HELP_PATH, NEWVID_PATH

from detect import filter_picture


#import Error

class MonThreadDeCalcul(QThread):
    """mon Thread"""
    def __init__(self,parent,motif,image):
        QThread.__init__(self)
        self.parent=parent
        self.motif = motif
        self.image = image

    def run(self):

        point = filter_picture(self.motif,self.image)
        return point



class StartQT4(QMainWindow):
    def __init__(self, parent, opts):
        #Données principales du logiciel : 
        if "maxi" in str(opts) :
            self.mini=False
        else :
            self.mini=True
        
        ######QT
        QMainWindow.__init__(self)
        QWidget.__init__(self, parent)
        try:
            Error._ = self.tr
        except:
            pass
#        Error._ = self.tr
        #### Mode plein écran
        self.plein_ecran = False
        QShortcut(QKeySequence(Qt.Key_F11),self, self.basculer_plein_ecran )
        
        height,width =  QDesktopWidget().screenGeometry().height(), QDesktopWidget().screenGeometry().width()

        if height >= 768 and width >= 1024 and self.mini==False:
        # Importation de l'interface ici car l'import de l'interface "mini" écrase l'interface "standard"
            from Ui_pymecavideo  import Ui_pymecavideo
        
        
        else :
            from Ui_pymecavideo_mini  import Ui_pymecavideo
            message = QMessageBox(self)
            #message.setText(self.trUtf8("Pymecavideo utilise l'interface mini.\nAppuyez sur la touche F11 pour passer en mode plein écran"))
            #message.setText(self.trUtf8("pymecavideo utilise l'interface mini.\nAppuyez sur la touche F11 pour passer en mode plein écran"))
            #message.setWindowTitle(self.trUtf8("Faible résolution"))
            #message.exec_()        
            #self.basculer_plein_ecran
        #changer ici le pichier adéquat pour les petites résolutions.
        self.ui = Ui_pymecavideo()
        self.ui.setupUi(self)
        self.dbg=Dbg(0)
        self.cvReader=None
        self.newVideos=[]            # les vidéos créées par recodage



        self.platform = platform.system()
        self.prefs=Preferences(self)
        ####intialise les répertoires
        self._dir()
        defait_icon=os.path.join(self._dir("icones"),"undo.png")
        
        self.ui.pushButton_defait.setIcon(QIcon(defait_icon))
        refait_icon=os.path.join(self._dir("icones"),"redo.png")
        self.ui.pushButton_refait.setIcon(QIcon(refait_icon))

        #Openoffice.org export
        try :
            import oooexport
            self.pyuno=True
            self.dbg.p(2,"In init_variables pyuno package found")
        except ImportError :
            self.dbg.p(2,"In init_variables no pyuno package")
            self.pyuno=False
        #variables àﾠ initialiser

        #Ooo export
        self.exe_ooo = False
        for exe_ooo in ["soffice","ooffice3.2"]:
            if  any(os.access(os.path.join(p,exe_ooo), os.X_OK) for p in os.environ['PATH'].split(os.pathsep)):
                self.exe_ooo = exe_ooo
            

        # sciDAVis export
        self.scidavis_present = False
        if  any(os.access(os.path.join(p,"scidavis"), os.X_OK) for p in os.environ['PATH'].split(os.pathsep)):
            self.scidavis_present = "scidavis"
        
        #qtiplot export    
        self.qtiplot_present=False
        if  any(os.access(os.path.join(p,"qtiplot"), os.X_OK) for p in os.environ['PATH'].split(os.pathsep)) :
            self.qtiplot_present="qtiplot"
       
            

        self.init_variables(opts)

        #connections internes
        self.ui_connections()

        #prise en compte d'options de la ligne de commande
        self.traiteOptions()
        
        #chargement d'un éventuel premier fichier
        self.splashVideo()
        
        
    # Basculer en mode plein écran / mode fenétré    
    def basculer_plein_ecran(self):
        if not self.plein_ecran :
            self.showFullScreen()
        else:
            self.showNormal()            
        self.plein_ecran = not (self.plein_ecran)
        
        
    def splashVideo(self):
        for opt,val in self.opts:
            if opt in ['-f','--fichier_mecavideo']:
                return
        if os.path.isfile(self.filename):
            self.openTheFile(self.filename)
        elif os.path.isfile(self.prefs.lastVideo):
            try:
                self.openTheFile(self.prefs.lastVideo)
            except:
                pass
       

    def init_variables(self, opts, filename=""):

        self.logiciel_acquisition = False
        self.points_ecran={}
        self.index_max = 1
        self.sens_X=1
        self.sens_Y=1
        self.repere=0
        self.origine = vecteur(320,240)
        self.auto=False
        self.motif = []
        self.lance_capture = False
        self.modifie=False
        self.points={}        #dictionnaire des points cliqués, par n d'image.
        self.trajectoire = {} #dictionnaire des points des trajectoires
        self.pX={}            #points apparaissant à l'écran, indexés par X
        self.pY={}            #points apparaissant à l'écran, indexés par Y
        self.index_du_point = 0
        self.echelle_image = echelle() # objet gérant l'image
        self.nb_image_deja_analysees = 0 #indique le nombre d'images dont on a dejà fait l'étude, ce qui correspond aussi au nombre de lignes dans le tableau.
        self.couleurs=["red", "blue", "cyan", "magenta", "yellow", "gray", "green"] #correspond aux couleurs des points de la trajectoire
        self.pointsProvisoires=[]    # quand on a plusieurs clics à faire
        self.nb_de_points = 1        # nombre de points suivis
        self.premiere_image = 1      # n° de la première image cliquée
        self.index_de_l_image = 1    # image à afficher
        #self.echelle_v = 0
        self.filename=filename
        self.opts=opts
        self.stdout_file = '/tmp/stdout'
        self.exitDecode = False
        
        self.tousLesClics=listePointee() # tous les clics faits sur l'image
        #self.init_interface()

        ######vérification de la présence d'un logiciel connu de capture vidéo dans le path
        for logiciel in ['qastrocam', 'qastrocam-g2', 'wxastrocapture']:
            if  any(os.access(os.path.join(p,logiciel), os.X_OK) for p in os.environ['PATH'].split(os.pathsep)) :
                self.logiciel_acquisition = logiciel
                self.ui.pushButton_video.setEnabled(1)
                break
        if self.logiciel_acquisition :
            self.ui.pushButton_video.setText(self.tr(unicode("Lancer "+self.logiciel_acquisition+"\n pour capturer une vidéo","utf8")))
        else :
            self.ui.pushButton_video.setEnabled(0)
            self.ui.pushButton_video.hide()
        
             

    def init_interface(self):
        self.cree_tableau()
        try : 
            
            self.label_trajectoire.clear()
        except AttributeError:
            self.label_trajectoire=Label_Trajectoire(self.ui.label_3, self)
            self.label_trajectoire.show()
            
        #for child in self.ui.label.children():
            #child.hide()
            #child.deleteLater()
        self.update()
        
        self.ui.horizontalSlider.setEnabled(0)
        

        self.ui.pushButton_video.setEnabled(0)
        
        self.ui.echelleEdit.setEnabled(0)
        self.ui.echelleEdit.setText(self.tr(unicode("indéf","utf8")))
        self.affiche_echelle()
        self.ui.tab_traj.setEnabled(0)
        self.ui.actionSaveData.setEnabled(0)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(0)
        self.ui.spinBox_image.setEnabled(0)
        self.affiche_lance_capture(False)
        self.ui.horizontalSlider.setValue(1)
        
        self.affiche_nb_points(False)
        self.ui.Bouton_Echelle.setEnabled(False)
        self.ui.checkBoxScale.setDuplicatesEnabled(False)
        self.ui.radioButtonNearMouse.hide()
        self.ui.radioButtonSpeedEveryWhere.hide()

        if not self.pyuno :
            self.desactiveExport("Oo.o Calc")
        if not self.qtiplot_present :
            self.desactiveExport("Qtiplot")
        if not self.scidavis_present :
            self.desactiveExport("SciDAVis")

        #création du label qui contiendra la vidéo.

        print "cree"
        try : 
            
            self.label_video.clear()
        except AttributeError:
            self.label_video = Label_Video(parent=self.ui.label, app=self)
            self.label_video.show()

        print self.ui.label.children()

        #self.ui.group_advanced.hide()

        self.ui.tabWidget.setCurrentIndex(0) # montre l'onglet video


    def desactiveExport(self,text):
        """
        Désactive la possibilité d'exportation, pour l'application dénotée par
        text.
        @param text le texte exact dans l'exportCombo qu'il faut inactiver
        """
        index=self.ui.exportCombo.findText(text)
        if index > 0:
            self.ui.exportCombo.setItemData(index,Qt.blue,Qt.BackgroundRole)
            self.ui.exportCombo.setItemText(index,QString(self.tr(u"NON DISPO : "+text)))
            self.ui.exportCombo.setItemData(index,Qt.blue,Qt.BackgroundRole)
        return
    def affiche_lance_capture (self,active=False):
        """
        Met à jour l'affichage du bouton pour lancer la capture
        @param active vrai si le bouton doit être activé
        """
        self.ui.Bouton_lance_capture.setEnabled(active)
        
    def affiche_nb_points(self, active=False):
        """
        Met à jour l'afficheur de nombre de points à saisir
        @param active vrai si on doit permettre la saisie du nombre de points
        """
        self.ui.spinBox_nb_de_points.setEnabled(active)
        self.ui.spinBox_nb_de_points.setValue(self.nb_de_points)
        
    def affiche_echelle(self):
        """
        affiche l'échelle courante pour les distances sur l'image
        """
        if self.echelle_image.isUndef():
            self.ui.echelleEdit.setText(self.tr(unicode("indéf.","utf8")))
            self.ui.Bouton_Echelle.setEnabled(True)
        else:
            epxParM=self.echelle_image.pxParM()
            if epxParM > 20:
                self.ui.echelleEdit.setText("%.1f" %epxParM)
            else:
                self.ui.echelleEdit.setText("%8e" %epxParM)
            self.ui.Bouton_Echelle.setEnabled(False)
        self.ui.echelleEdit.show()
        self.ui.Bouton_Echelle.show()
 
    def reinitialise_tout(self, echelle_image=None, nb_de_points=None, tousLesClics=None,index_point_actuel=None):
        """
        Réinitialise l'interface de saisie, mais pas l'échelle. On
        peut quand même passer quelques paramètres à conserver, ce qui
        permet le défaire/refaire :
        @param echelle_image évite de ressaisir l'échelle de l'image
        @param nb_de_points évite de ressaisir le nombre de points à suivre
        @param tousLesClics permet de conserver une liste de points à refaire
        @param index_point_actuel permet de réinitialiser à partir de l'image de départ.
        """
        self.dbg.p(2,"Dans reinitialise_tout: echelle_image=%s, nb_de_points=None%s, tousLesClics=%s,index_point_actuel=%s" %(echelle_image, nb_de_points, tousLesClics,index_point_actuel))
        self.montre_vitesses=False
        self.label_trajectoire.update()
        self.ui.label.update()
        self.label_video.update()

        #############
        # si il existe un point actuel, cela signifie qu'on réinitialise
        # tout mais qu'on doit garder la position de départ. Cas quand
        #on revient en arrière d'un cran ou que l'on refait le point.
        #############
        if index_point_actuel :
            index = self.premiere_image
            self.init_variables(None, filename=self.filename)

            ############ permet de récupérer les 2 valeurs souhaitées
            self.premiere_image = index
            self.index_de_l_image = index
            ############
        else :
            self.init_variables(None, filename=self.filename)
  
        self.init_interface()
        #self.affiche_fonctionnalites_avancees()
        self.ui.pushButton_origine.setEnabled(1)
        self.ui.checkBox_abscisses.setEnabled(1)
        self.ui.checkBox_ordonnees.setEnabled(1)
        #for enfant in self.label_video.children():
              #enfant.hide()
              #del enfant
        if echelle_image:
            self.echelle_image=echelle_image
            self.feedbackEchelle(self.echelle_image.p1, self.echelle_image.p2)
            
        if nb_de_points:
            self.nb_de_points=nb_de_points
        if tousLesClics!=None and tousLesClics.count():
            self.tousLesClics=tousLesClics

    def reinitialise_capture(self):
        """
        Efface toutes les données de la capture en cours et prépare une nouvelle
        session de capture.
        """
        self.montre_vitesses=False
        
        #self.oubliePoints()
        self.label_trajectoire.update()
        self.ui.label.update()
        self.label_video.update()
        self.label_video.setCursor(Qt.ArrowCursor)
        #for enfant in self.label_video.children():
              #enfant.hide()
              #del enfant
        #del self.label_video.zoom_croix
        
        #del self.label_video
        self.init_variables(None, filename=self.filename)
        self.affiche_image()

        self.echelle_image=echelle()
        self.affiche_echelle()
        self.ui.horizontalSlider.setEnabled(1)
        self.ui.spinBox_image.setEnabled(1)
        self.ui.spinBox_image.setValue(1)
        self.enableDefaire(False)
        self.enableRefaire(False)
        self.affiche_nb_points(1)
        ### Réactiver checkBox_avancees après réinitialisation ###
        #self.ui.checkBox_avancees.setEnabled(1)


        if self.ui.tableWidget:
            self.ui.tableWidget.clear()

    def ui_connections(self):
        """connecte les signaux de QT"""
        QObject.connect(self.ui.actionOuvrir_un_fichier,SIGNAL("triggered()"), self.openfile)
        QObject.connect(self.ui.actionExemples,SIGNAL("triggered()"), self.openexample)
        QObject.connect(self.ui.action_propos,SIGNAL("triggered()"), self.propos)
        QObject.connect(self.ui.actionAide,SIGNAL("triggered()"), self.aide)
        QObject.connect(self.ui.actionPreferences,SIGNAL("triggered()"), self.prefs.setFromDialog)
        QObject.connect(self.ui.actionDefaire,SIGNAL("triggered()"), self.efface_point_precedent)
        QObject.connect(self.ui.actionRefaire,SIGNAL("triggered()"), self.refait_point_suivant)
        QObject.connect(self.ui.actionQuitter,SIGNAL("triggered()"), self.close)
        QObject.connect(self.ui.actionSaveData,SIGNAL("triggered()"), self.enregistre_ui)
        QObject.connect(self.ui.actionCopier_dans_le_presse_papier,SIGNAL("triggered()"), self.presse_papier)
        QObject.connect(self.ui.actionOpenOffice_org_Calc,SIGNAL("triggered()"), self.oooCalc)
        QObject.connect(self.ui.actionQtiplot,SIGNAL("triggered()"), self.qtiplot)
        QObject.connect(self.ui.actionScidavis,SIGNAL("triggered()"), self.scidavis)
        QObject.connect(self.ui.actionRouvrirMecavideo,SIGNAL("triggered()"), self.rouvre_ui)
        QObject.connect(self.ui.Bouton_Echelle,SIGNAL("clicked()"), self.demande_echelle)
        QObject.connect(self.ui.horizontalSlider,SIGNAL("sliderReleased()"), self.affiche_image_slider)
        QObject.connect(self.ui.spinBox_image,SIGNAL("valueChanged(int)"),self.affiche_image_spinbox)
        QObject.connect(self.ui.Bouton_lance_capture,SIGNAL("clicked()"),self.debut_capture)
        QObject.connect(self,SIGNAL("clic_sur_video()"),self.clic_sur_label_video)
        QObject.connect(self.ui.comboBox_referentiel,SIGNAL("currentIndexChanged (int)"),self.tracer_trajectoires)
        QObject.connect(self.ui.comboBox_mode_tracer,SIGNAL("currentIndexChanged (int)"),self.tracer_courbe)
        QObject.connect(self.ui.tabWidget,SIGNAL("currentChanged (int)"),self.tracer_trajectoires)
        #QObject.connect(self.ui.echelle_v,SIGNAL("currentIndexChanged (int)"),self.refait_vitesses)
        #QObject.connect(self.ui.echelle_v,SIGNAL("editTextChanged (int)"),self.refait_vitesses)
        
        QObject.connect(self.ui.checkBoxVectorSpeed,SIGNAL("stateChanged(int)"),self.enableSpeed)
        QObject.connect(self.ui.radioButtonSpeedEveryWhere,SIGNAL("toggled()"),self.enableSpeed)
        QObject.connect(self.ui.radioButtonNearMouse,SIGNAL("toggled()"),self.enableSpeed)
        QObject.connect(self.ui.radioButtonSpeedEveryWhere,SIGNAL("clicked()"),self.enableSpeed)
        QObject.connect(self.ui.radioButtonNearMouse,SIGNAL("clicked()"),self.enableSpeed)
        QObject.connect(self.ui.button_video,SIGNAL("clicked()"),self.video)
        QObject.connect(self.ui.pushButton_select_all_table,SIGNAL("clicked()"),self.presse_papier)
        QObject.connect(self.ui.pushButton_reinit,SIGNAL("clicked()"),self.reinitialise_capture)
        QObject.connect(self.ui.pushButton_defait,SIGNAL("clicked()"),self.efface_point_precedent)
        QObject.connect(self.ui.pushButton_refait,SIGNAL("clicked()"),self.refait_point_suivant)
        QObject.connect(self.ui.pushButton_origine,SIGNAL("clicked()"),self.choisi_nouvelle_origine)
        QObject.connect(self.ui.pushButton_video,SIGNAL("clicked()"),self.lance_logiciel_video)
        QObject.connect(self.ui.checkBox_abscisses,SIGNAL("stateChanged(int)"),self.change_sens_X )
        QObject.connect(self.ui.checkBox_ordonnees,SIGNAL("stateChanged(int)"),self.change_sens_Y )
        QObject.connect(self,SIGNAL('change_axe_origine()'),self.change_axe_ou_origine)
        QObject.connect(self,SIGNAL('selection_done()'),self.picture_detect)
        QObject.connect(self,SIGNAL('selection_motif_done()'),self.storeMotif)
        QObject.connect(self,SIGNAL('updateProgressBar()'),self.updatePB)

        ## QObject.connect(self.ui.calcButton,SIGNAL("clicked()"),self.oooCalc)
        ## QObject.connect(self.ui.qtiplotButton,SIGNAL("clicked()"),self.qtiplot)
        QObject.connect(self.ui.exportCombo,SIGNAL("currentIndexChanged(int)"),self.export)
        #### il faut connecter le combo exportCombo ####
        QObject.connect(self.ui.pushButton_nvl_echelle,SIGNAL("clicked()"),self.recommence_echelle)
        QObject.connect(self,SIGNAL("mplWindowClosed()"),self.mplwindowclosed)
        
    def updatePB(self):
        self.qmsgboxencode.updateProgressBar()
        
    def enableSpeed(self):
        self.dbg.p(2,"In enableSpeed")
        self.ui.checkBoxScale.setEnabled(1)
        self.ui.checkBoxScale.insertItem(0,"1")
        
        self.ui.radioButtonNearMouse.show()
        self.ui.radioButtonSpeedEveryWhere.show()
        self.label_trajectoire.giveCoordonatesToPaint()
        self.label_trajectoire.repaint()
        self.label_trajectoire.update()
        
    def storeMotif(self):
        
        if len(self.motif)==self.nb_de_points:
            self.label_auto.hide()
            self.label_auto.close()
            self.picture_detect()    

        
        
    def mplwindowclosed(self):
        self.canvas.effacerTousLesPlots()
        
        
    def picture_detect(self):
        
        while self.index_de_l_image<self.image_max:
            for motif in self.motif:
                self.run_detect(motif,self.image_640_480)
            
            
    def run_detect(self,motif, image):
        myThread = MonThreadDeCalcul(self,motif,image)
        point = myThread.run()
        
        ##itère d'un cran et lance la détection
        #self.label_video.liste_points.append(vecteur(point[0], point[1]))
        if self.index_de_l_image<=self.image_max:
            self.label_video.pos_avant=self.label_video.pos
            self.label_video.storePoint(vecteur(point[0], point[1]))
            self.label_video.repaint()
            self.clic_sur_label_video()
            
    def readStdout(self):
        
        try : 
            if not self.time.isActive():
                self.timer = QTimer(self)
                QObject.connect(self.timer, SIGNAL("timeout()"), self, SLOT(self.readStdout()))
                self.timer.start(100);
            else : 
                while not self.exitDecode:
                    print "while"
                    stdout_file = open(self.stdout_file, 'w+')
                    stdout = stdout_file.readlines()  ##a gloabliser poru windows
                    #print stdout
                    if not self.exitDecode:
                        try : 
                            pct = stdout[-1].split()[3].replace('%','').replace(')','').replace('(','')
                            print stdout[-1].split()[3].replace('%','').replace(')','').replace('(','')
                            assert(pct.isalnum())
                            exit=True
                        except IndexError:
                            print "indexerror"
                            exit=False
                
        except :
            pass
        
            
        
    def refait_echelle(self):
        #"""Permet de retracer une échelle et de recalculer les points"""
        #self.recommence_echelle()

        
        self.cree_tableau()
        index=0
        for point in  self.tousLesClics:
            self.stock_coordonnees_image(index,point)
            index+=1


    def choisi_nouvelle_origine(self):
        nvl_origine=QMessageBox.information(self,QString("NOUVELLE ORIGINE"),\
                                            QString("Choisissez, en cliquant sur la video le point qui sera la nouvelle origine"))
                                            
        label = Label_Origine(parent=self.ui.label, app=self)
        label.show()

        #self.emit(SIGNAL('change_axe_origine()'))

    def lance_logiciel_video(self):
        #lance un logiciel externe de capture vidéo. Par défaut, qastrocam-g2, possibiltié de changer dans les préférences.
        lance_logiciel = subprocess.Popen(args=[self.logiciel_acquisition], stderr=PIPE)

    def change_axe_ou_origine(self):
        """mets à jour le tableau de données"""
        #repaint axes and define origine
        self.label_trajectoire.origine_mvt=self.origine
        self.label_trajectoire.update()
        
        self.label_video.origine = self.origine
        self.label_video.update()
        
        #construit un dico plus simple à manier, dont la clef est point_ID et qui contient les coordoonées
        if self.points_ecran != {}:
            liste_clef=[]
            donnees={}
            for key in self.points_ecran:
                donnees[self.points_ecran[key][2]]=self.points_ecran[key][3]
                liste_clef.append(self.points_ecran[key][2])
            liste_clef.sort()
            for key in liste_clef :
                serie,position=self.couleur_et_numero(int(key))
                self.rempli_tableau(serie,position,donnees[key],recalcul=True)
        try:
            del self.repere_camera
        except AttributeError:
            pass
    def change_sens_X(self):
        if self.ui.checkBox_abscisses.isChecked():
            self.sens_X = -1
        else :
            self.sens_X = 1
        self.emit(SIGNAL('change_axe_origine()'))

    def change_sens_Y(self):
        if self.ui.checkBox_ordonnees.isChecked():
            self.sens_Y = -1

        else :
            self.sens_Y = 1
        self.emit(SIGNAL('change_axe_origine()'))

    #def affiche_fonctionnalites_avancees(self):
        #"""
        #met à jour l'affichage des fonctions avancées, selon l'état
        #coché ou décoché de la case de choix
        #"""
        #if self.ui.checkBox_avancees.isChecked() :
            #self.ui.group_advanced.setEnabled(1)
            #self.ui.group_advanced.show()
        #else :
            #self.ui.group_advanced.hide()


    def pointEnMetre(self,p):
        """
        renvoie un point, dont les coordonnées sont en mètre, dans un
        référentiel "à l\'endroit"
        @param point un point en "coordonnées d\'écran"
        """
        return vecteur(self.sens_X*(float(p.x()-self.origine.x())*self.echelle_image.mParPx()),self.sens_Y*
                       float(self.origine.y()-p.y())*self.echelle_image.mParPx())
    
    def presse_papier(self):
        """Sélectionne la totalité du tableau de coordonnées
        et l'exporte dans le presse-papier (l'exportation est implicitement
        héritée de la classe utilisée pour faire le tableau). Les
        séparateurs décimaux sont automatiquement remplacés par des virgules
        si la locale est française.
        """
        trange=QTableWidgetSelectionRange(0,0,
                                          self.ui.tableWidget.rowCount()-1,
                                          self.ui.tableWidget.columnCount()-1)
        self.ui.tableWidget.setRangeSelected(trange,True)
        self.ui.tableWidget.selection()

    def export(self):
        """
        Traite le signal venu de exportCombo, puis remet l\'index de ce 
        combo à zéro.
        """
        if self.ui.exportCombo.currentIndex()>0:
            option=self.ui.exportCombo.currentText()
            if option=="Oo.o Calc" : self.oooCalc()
            elif option=="Qtiplot" : self.qtiplot()
            elif option=="SciDAVis" : self.scidavis()
            self.ui.exportCombo.setCurrentIndex(0)
        return

    def oooCalc(self):
        """
        Exporte directement les données vers OpenOffice.org Calc
        """
        if self.pyuno==True :
            import oooexport
        calc=oooexport.Calc()
        calc.importPymeca(self)

    def qtiplot(self):
        """
        Exporte directement les données vers Qtiplot
        """
        plot=qtiplotexport.Qtiplot(self)
        f=tempfile.NamedTemporaryFile(prefix='pymecaTmp-',suffix=".qti")
        fname=f.name
        f.close()
        f=open(fname,"w")
        plot.saveToFile(f)
        f.close()
        t=threading.Thread(target=lanceQtiplot, args=(fname,))
        t.setDaemon(True) # Qtiplot peut survivre à pymecavideo
        t.start()
        
    def scidavis(self):
        """
        Exporte directement les données vers SciDAVis
        """
        plot=qtiplotexport.Qtiplot(self)
        f=tempfile.NamedTemporaryFile(prefix='pymecaTmp-',suffix=".qti")
        fname=f.name
        f.close()
        f=open(fname,"w")
        plot.saveToFile(f)
        f.close()
        t=threading.Thread(target=lanceSciDAVis, args=(fname,))
        t.setDaemon(True) # Scidavis peut survivre à pymecavideo
        t.start()

    
    
    
    def _dir(lequel=None,install=None):
        """renvoie les répertoires utiles.
        paramètre lequel (chaîne) : peut prendre les valeurs utiles suivantes,
        "videos", "home", "conf", "images", "icones", "langues", "data", "help"

        quand le paramètre est absent, initialise les répertoires si nécessaire
        """

        home = unicode(QDesktopServices.storageLocation(8), 'iso-8859-1')

        if   lequel == "home": return  home
        elif lequel == "videos": return VIDEO_PATH
        elif lequel == "conf": return  CONF_PATH
        elif lequel == "images": return IMG_PATH
        elif lequel == "icones": return ICON_PATH
        elif lequel == "langues": return LANG_PATH
        elif lequel == "data" : return DATA_PATH
        elif lequel == "help" : return HELP_PATH
        elif type(lequel) == type(""):
            self.dbg.p(1,"erreur, appel de _dir() avec le paramètre inconnu %s" %lequel)
            self.close()
        else:
            # vérifie/crée les repertoires
            for d in ("conf", "images"):
                dd=StartQT4._dir(str(d))
                if not os.path.exists(dd):
                    call("mkdir -p %s" %dd, shell=True)

    _dir=staticmethod(_dir)

    def init_cvReader(self):
        """
        Initialise le lecteur de flux vidéo pour OpenCV
        et recode la vidéo si nécessaire.
        """
        self.cvReader=openCvReader(self.filename)
        if not self.cvReader : 
            
            sansSuffixe=os.path.basename(self.filename)
            match=re.match("(.*)\.(.*)$",sansSuffixe)
            sansSuffixe=match.group(1)
            dest=os.path.join(NEWVID_PATH,sansSuffixe+".avi")
            self.qmsgboxencode = QMessageBoxEncode(self,dest)
            self.qmsgboxencode.show()
            
            return False
        else : 
            try: 
                self.qmsgboxencode.close()
            except AttributeError:
                pass
            
            return True
            


    def rouvre_ui(self):
        dir_ = self._dir("home")
        fichier = QFileDialog.getOpenFileName(self,self.tr(unicode("Ouvrir un projet Pymecavideo","utf8")), dir_,self.tr(unicode("fichiers pymecavideo ( *.mecavideo)","utf8")))
        
        if fichier != "":
            self.rouvre(fichier)

    def loads(self,s):
        s=s[1:-1].replace("\n#","\n")
        self.filename,self.premiere_image,self.echelle_image.longueur_reelle_etalon,self.echelle_image.p1,self.echelle_image.p2,self.deltaT,self.nb_de_points = pickle.loads(s)
        self.init_cvReader()
        
    def rouvre(self,fichier):
        lignes=open(fichier,"r").readlines()
        i=0
        self.points={}
        dd=""
        for l in lignes:
            if l[0]=="#":
                dd+=l
            else:
                l=l.strip('\t\n')
                d=l.split("\t")
                self.points[i]=[d[0]]
                for j in range(1,len(d),2):
                    self.points[i].append(vecteur(d[j],d[j+1]))
                i+=1
        self.echelle_image=echelle() # on réinitialise l'échelle
        self.loads(dd)               # on récupère les données importantes
        # puis on trace le segment entre les points cliqués pour l'échelle
        self.feedbackEchelle(self.echelle_image.p1, self.echelle_image.p2)
        framerate, self.image_max = self.cvReader.recupere_avi_infos()
        self.defini_barre_avancement()
        self.affiche_echelle()       # on met à jour le widget d'échelle
        n=len(self.points.keys())
        self.nb_image_deja_analysees = n
        self.ui.horizontalSlider.setValue(n+self.premiere_image)
        self.ui.spinBox_image.setValue(n+self.premiere_image)
        self.affiche_nb_points(self.nb_de_points)
        self.enableDefaire(True)
        self.enableRefaire(False)
        # On regénère la liste self.tousLesClics
        for i in self.points.keys():
           self.tousLesClics.append(self.points[i][1:])
        self.affiche_image() # on affiche l'image
        self.debut_capture(departManuel=False)
        # On regénère le tableau d'après les points déjà existants.
        self.cree_tableau()
        ligne=0
        for k in self.points.keys():
            data=self.points[k]
            t="%4f" %(float(data[0]))
            self.ui.tableWidget.insertRow(ligne)
            self.ui.tableWidget.setItem(ligne,0,QTableWidgetItem(t))
            i=1
            for vect in data[1:]:
                vect=self.pointEnMetre(vect)
                self.ui.tableWidget.setItem(ligne,i,QTableWidgetItem(str(vect.x())))
                self.ui.tableWidget.setItem(ligne,i+1,QTableWidgetItem(str(vect.y())))
                i+=2
            ligne+=1
        self.ui.tableWidget.show()
        # attention à la fonction défaire/refaire : elle est mal initialisée !!!

        # On met à jour les préférences
        self.prefs.lastVideo=self.filename
        self.prefs.videoDir=os.path.dirname(self.filename)
        self.prefs.save()

    def entete_fichier(self, msg=""):
        result=u"""#pymecavideo
#video = %s
#index de depart = %d
#echelle %5f m pour %5f pixel
#echelle pointee en %s %s
#intervalle de temps : %f
#suivi de %s point(s)
#%s
#""" %(self.filename,self.premiere_image,self.echelle_image.longueur_reelle_etalon,self.echelle_image.longueur_pixel_etalon(),self.echelle_image.p1,self.echelle_image.p2,self.deltaT,self.nb_de_points,msg)
        return result

    def dumps(self):
        return "#"+pickle.dumps((self.filename,self.premiere_image,self.echelle_image.longueur_reelle_etalon,self.echelle_image.p1,self.echelle_image.p2,self.deltaT,self.nb_de_points)).replace("\n","\n#")
    def enregistre(self, fichier):
        sep_decimal="."
        try:
            if locale.getdefaultlocale()[0][0:2]=='fr':
                # en France, le séparateur décimal est la virgule
                sep_decimal=","
        except TypeError:
            pass
        if fichier != "":
            fichierMecavideo=""+fichier # on force une copie !
            fichierMecavideo.replace(".csv",".mecavideo")
            file = open(fichierMecavideo, 'w')
            liste_des_cles = []
            try :
                file.write(self.dumps())
                for key in self.points:
                    liste_des_cles.append(key)
                liste_des_cles.sort()
                for cle in liste_des_cles:
                    donnee=self.points[cle]
                    t=float(donnee[0])
                    a = "\n%.2f\t" %t
                    for p in donnee[1:]:
                        a+= "%d\t" %p.x()
                        a+= "%d\t" %p.y()
                    file.write(a)
            finally:
                file.close()
            ################# fin du fichier mecavideo ################
            file = codecs.open(fichier, 'w', 'utf8')
            try :
                file.write(self.entete_fichier(self.tr("temps en seconde, positions en mètre")))
                for cle in liste_des_cles:
                    donnee=self.points[cle]
                    t=float(donnee[0])
                    a = ("\n%.2f\t" %t).replace(".", sep_decimal)
                    for p in donnee[1:]:
                        pm=self.pointEnMetre(p)
                        a+= ("%5f\t" %(pm.x())).replace(".", sep_decimal)
                        a+= ("%5f\t" %(pm.y())).replace(".", sep_decimal)
                    file.write(a)
            finally:
                file.close()
            ################# fin du fichier physique ################
            self.modifie=False
        
    def enregistre_ui(self):
        if self.points!={}:
            fichier = QFileDialog.getSaveFileName(self,"FileDialog", "data.csv","*.csv *.txt *.asc *.dat")
            self.enregistre(fichier)

    def debut_capture(self, departManuel=True):
        """
        permet de mettre en place le nombre de point à acquérir
        @param departManuel vrai si on a fixé à la main la première image.

        """
        try :
            self.origine_trace.hide()
            del self.origine_trace
        except :
            pass
        #self.origine_trace = Label_Origine_Trace(parent=self.label_video, origine=self.origine)
        #self.origine_trace.show()
        #self.origine_trace = Label_Origine_Trace(parent=self.label_video, origine=self.origine)
        self.label_video.setFocus()
        self.label_video.show()
        self.label_video.activateWindow()
        self.label_video.setVisible(True)

        #self.origine_trace.show()

        self.label_echelle_trace.lower()  #nécessaire sinon, label_video n'est pas actif.
        #self.origine_trace.lower() 

        self.nb_de_points = self.ui.spinBox_nb_de_points.value()
        self.affiche_nb_points(False)
        self.affiche_lance_capture(False)
        self.ui.horizontalSlider.setEnabled(0)
        self.ui.spinBox_image.setEnabled(0)

        if departManuel==True: # si on a mis la première image à la main
            self.premiere_image=self.ui.horizontalSlider.value()
        self.affiche_point_attendu(1)
        self.lance_capture = True
        self.label_video.setCursor(Qt.CrossCursor)
        self.ui.tab_traj.setEnabled(1)
        self.ui.actionSaveData.setEnabled(1)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(1)
        self.ui.comboBox_referentiel.setEnabled(1)
        self.ui.pushButton_select_all_table.setEnabled(1)

        
        #self.ui.group_advanced.setEnabled(0)
        
        
        self.ui.comboBox_referentiel.clear()
        self.ui.comboBox_referentiel.insertItem(-1, "camera")
        for i in range(self.nb_de_points) :
            self.ui.comboBox_referentiel.insertItem(-1, QString(self.tr(u"point N°")+" "+str(i+1)))
        self.cree_tableau()
        if self.ui.checkBox_auto.isChecked():
            ###############
            
            reponse=QMessageBox.warning(None,"Capture Automatique",QString(u"Veuillez sélectionner un cadre autour de(s) l'objet(s) que vous voulez suivre"), QMessageBox.Ok,QMessageBox.Ok)

            self.label_auto = Label_Auto(self.label_video,self) #in this label, motif is defined.
            self.label_auto.show()
                

    def cree_tableau(self):
        """
        Crée un tableau de coordonnées neuf dans l'onglet idoine.
        """
        self.ui.tableWidget.clear()
        self.ui.tab_coord.setEnabled(1)
        self.ui.tableWidget.setRowCount(1)
        self.ui.tableWidget.setColumnCount(self.nb_de_points*2 + 1)
        self.ui.tableWidget.setDragEnabled(True)
        # on met des titres aux colonnes.
        self.ui.tableWidget.setHorizontalHeaderItem(0,QTableWidgetItem('t (s)'))
        for i in range(self.nb_de_points):
            x="X%d (m)" %(1+i)
            y="Y%d (m)" %(1+i)
            self.ui.tableWidget.setHorizontalHeaderItem(1+2*i,QTableWidgetItem(x))
            self.ui.tableWidget.setHorizontalHeaderItem(2+2*i,QTableWidgetItem(y))

    def traiteSouris(self,p):
        """
        cette fonction est rappelée par label_trajectoire quand la souris
        bouge au-dessus : p est un vecteur, position de la souris.
        """
        #print self.points
        print "################"
        self.dbg.p(2,"entre dans traiteSouris")
        if not self.prefs.proximite: 
	  self.dbg.p(2,"dans traiteSouris, self.prefs.proximite = True")
	  return
	self.dbg.p(2,"dans traiteSouris, self.prefs.proximite = false")
        portee=30
        try:
            pX=set()
            pY=set()
            self.dbg.p(2,"dans traiteSouris, créer 2 sets")
        except:
            import sets # for Python << 2.5
            pX=sets.Set()
            pY=sets.Set()
        for x in self.pX.keys():
            if p.x()-portee<x<p.x()+portee:
                for a in self.pX[x]: pX.add(a)
                self.dbg.p(2,"dans traiteSouris, 1")
            else:
                for a in self.pX[x]: a.montre_vitesse(False)
                self.dbg.p(2,"dans traiteSouris, 2")
        for y in self.pY.keys():
            if p.y()-portee<y<p.y()+portee:
                for a in self.pY[y]: pY.add(a)
                self.dbg.p(2,"dans traiteSouris, 3")
            else:
                for a in self.pY[y]:
		  a.montre_vitesse(False)
		  self.dbg.p(2,"dans traiteSouris, 4")
        intersection=list(pX & pY)
        #print pX, pY
	print intersection
        if intersection:
            # précaution au cas où on a plus d'un point dans l'intersection
            # définie par la variable portee
            min=1000 # plus que la dimension du widget
            index=0
            for i in range(len(intersection)):
                distance=(intersection[i].point-p).norme()
                if distance<min:
                    min=distance
                    index=i
            # montre la vitesse seulement pour le widget le plus
            # proche de la souris
            for i in range(len(intersection)):
                intersection[i].montre_vitesse(index==i)

    def barycentre_trajectoires(self,referentiel):
        """
        calcule le barycentre de tous les points constituant les trajectoires
        rapportées à un référentiel.
        """
        bc=vecteur(0,0)
        compte=0
        for n in range(self.nb_de_points):
            if n==referentiel:
                pass
            for i in self.points.keys():
                bc += self.points[i][1+n]-self.points[i][1+referentiel]
                compte +=1
        bc *= 1.0/compte
        return bc
            
    def mediane_trajectoires(self,referentiel):
        """
        calcule le barycentre de tous les points constituant les trajectoires
        rapportées à un référentiel.
        """
        min=None
        max=None
        for n in range(self.nb_de_points):
            if n==referentiel:
                pass
            for i in self.points.keys():
                p = self.points[i][1+n]-self.points[i][1+referentiel]
                min=p.minXY(min)
                max=p.maxXY(max)
        if min!=None and max!=None:
            return (min+max)*0.5
        else:
            return vecteur(320,240)

    #def refait_vitesses(self, newText=""):
        #"""
        #recalcule les vitesses de tous les points tracés.
        #"""
        #for index in self.trajectoire.keys():
            #if index[:6]=="point-":
                #[p,point] = self.trajectoire[index]
                #self.echelle_v=self.ui.echelle_v.currentText()
                #show=True
                #point.calcule_vitesse(self.echelle_v,show)

    #def setEchelle_v(self):
        #ech_v="%s" %self.echelle_v
        #index=self.ui.echelle_v.findText(ech_v)
        #if index <0:
            #self.ui.echelle_v.addItem(ech_v)
            #index=self.ui.echelle_v.findText(ech_v)
        #self.ui.echelle_v.setCurrentIndex(1)
        #self.refait_vitesses()
        
    def visibilite_vitesses(self):
        """
        change le critère de visibilité des vitesses selon self.prefs
        """
        #if not self.prefs.proximite:
            ##choix par défaut
            #self.label_trajectoire.setMouseTracking(0)
            #self.montre_vitesses(True)
        #else:
            #self.montre_vitesses(False)
            #self.label_trajectoire.setMouseTracking(1)
            #self.label_trajectoire.setFocus()
            #self.label_trajectoire.update()
        pass

                
    #def montre_vitesses(self, show=True):
        #"""
        #montre ou cache les vitesses, selon le paramètre show
        #"""
        #for index in self.trajectoire.keys():
            #if index[:6]=="point-":
                #[p,point] = self.trajectoire[index]
                #point.montre_vitesse(show)
        #if not show:
            #self.label_trajectoire.update()
            
    def efface_point_precedent(self):
        """revient au point précédent
        """
        self.tousLesClics.decPtr()

        self.reinitialise_tout(self.echelle_image, self.nb_de_points, self.tousLesClics,self.index_de_l_image-1)
        self.repasseTousLesClics()
        self.label_echelle_trace.show()
        self.modifie=True

    def refait_point_suivant(self):
        """rétablit le point suivant après un effacement
        """
        self.tousLesClics.incPtr()
        self.reinitialise_tout(self.echelle_image, self.nb_de_points, self.tousLesClics,self.index_de_l_image-1)
        self.repasseTousLesClics()
        self.modifie=True

    def repasseTousLesClics(self):
        """
        repasse en mode non-interactif toute la liste des clics
        sur l'image, jusqu'au pointeur courant de cette liste pointée.
        """

        self.affiche_echelle()
        self.affiche_nb_points()
        self.ui.tab_traj.setEnabled(1)
        

        for clics in self.tousLesClics:
            self.clic_sur_label_video(liste_points=clics, interactif=False)
        self.clic_sur_label_video_ajuste_ui(1)


    def video(self):
        ref=self.ui.comboBox_referentiel.currentText().split(" ")[-1]
        if len(ref)==0 or ref == "camera": return
        c=Cadreur(int(ref),self)
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

        try : 
            self.label_trajectoire.update()
            if self.ui.tabWidget.currentIndex()!=0 :#Pas le premier onglet
                
                origine = vecteur(0,0)
                self.label_video.zoom_croix.hide()
                #self.oubliePoints()
                if newValue=="absolu":
                    ref="camera"
                else:
                    ref = self.ui.comboBox_referentiel.currentText().split(" ")[-1]

                if len(ref)==0 : return
                if ref != "camera":
                    bc=self.mediane_trajectoires(int(ref)-1)
                    origine=vecteur(320,240)-bc
                    self.label_trajectoire.origine = origine

                    self.label_trajectoire.referentiel = ref
                else : 
                    self.label_trajectoire.origine = vecteur(0,0)
                # garnit le menu des courbes à tracer
                self.ui.comboBox_mode_tracer.clear()
                self.ui.comboBox_mode_tracer.insertItem(-1, QString(self.tr("Choisir ...")))
                for i in range(self.nb_de_points) :
                    combo=self.ui.comboBox_mode_tracer
                    combo.addItem(QString("x%d(t)" %(i+1)))
                    combo.addItem(QString("y%d(t)" %(i+1)))
                    combo.addItem(QString("v%d(t)" %(i+1)))
                            
                            
        except ZeroDivisionError:
            print "pb self.tracer_trajectoires"

    def tracer_courbe(self,itemChoisi):
        if self.ui.comboBox_mode_tracer.isEnabled():
#            try:
            self.ui.comboBox_mode_tracer.setCurrentIndex(0)
            if itemChoisi <= 0: return # c'est rien du tout.
            numero=(itemChoisi-1)/3
            typeDeCourbe=("x","y","v")[(itemChoisi-1)%3]
            titre=(self.tr(u"Evolution de l'abscisse du point %1").arg(numero+1),
                   self.tr(u"Evolution de l'ordonnée du point %1").arg(numero+1),
                   self.tr(u"Evolution de la vitesse du point %1").arg(numero+1))[(itemChoisi-1)%3]
            titre=titre.toAscii()
            abscisse=[]
            ordonnee=[]
            t=0
            ancienPoint=None
            ref=self.ui.comboBox_referentiel.currentText().split(" ")[-1]
            for i in self.points.keys():
                if ref == "camera":
                    p = self.pointEnMetre(self.points[i][1+numero])
                else:
                    ref=int(ref)
                    p = self.pointEnMetre(self.points[i][1+numero])-self.pointEnMetre(self.points[i][ref])
                if typeDeCourbe == "x": ordonnee.append(p.x())
                if typeDeCourbe == "y": ordonnee.append(p.y())
                if typeDeCourbe == "v":
                    if ancienPoint != None:
                      abscisse.append(t)
                      v=(p-ancienPoint).norme()/self.deltaT
                      ordonnee.append(v)
                else:
                    abscisse.append(t)
                t+=self.deltaT
                ancienPoint=p
            # les abscisses et les ordonnées sont prêtes
            labelAbscisse="t (s)"
            if typeDeCourbe != "v" : labelOrdonnee=typeDeCourbe+" (m)"
            else: labelOrdonnee=typeDeCourbe+" (m/s)"
            # déterminer le style de tracé
            styleTrace=None
            if typeDeCourbe in ("x","y"):
                if ref == "camera":
                    p1=self.pointEnMetre(vecteur(0,0))
                    p2=self.pointEnMetre(vecteur(640,480))
                    minx=p1.x(); maxx=p2.x()
                    miny=p1.y(); maxy=p2.y()
                    if typeDeCourbe=="x":
                        styleTrace=[0,minx,t,maxx]
                    if typeDeCourbe=="y":
                        styleTrace=[0,miny,t,maxy]
                else:
                    styleTrace="zero"
            else: # type de courbe "v""
                styleTrace="zero"
            
            if not hasattr(self,'canvas'):
                self.canvas = MyMplCanvas(None)
            if not hasattr(self,'traceur'):
              self.traceur = traceur2d(self,abscisse, ordonnee, labelAbscisse, labelOrdonnee, titre, styleTrace,itemChoisi)
            else : #mets juste à jour la fenêtre de matplotlib
              self.traceur.update_canvas(abscisse, ordonnee, labelAbscisse, labelOrdonnee, titre, styleTrace,itemChoisi)
              self.traceur.update()

    
    def affiche_point_attendu(self,n):
        """
        Renseigne sur le numéro du point attendu
        affecte la ligne de statut et la ligne sous le zoom
        """
        self.mets_a_jour_label_infos(self.tr(u"Pointage des positions : cliquer sur le point N°%d" %n))
        #self.ui.label_sous_zoom.setText(self.tr(u"zoom point %d" %n))


    def clic_sur_label_video(self, liste_points=None, interactif=True):

        
        if liste_points==None:
            liste_points = self.label_video.liste_points
        ### on fait des marques pour les points déjà visités
        etiquette="@abcdefghijklmnopqrstuvwxyz"[len(liste_points)]


        if self.nb_de_points > len(liste_points) :
            point_attendu=1+len(liste_points)
            self.affiche_point_attendu(point_attendu)
            #self.affiche_image()




        else:

            point_attendu=1
            self.affiche_point_attendu(point_attendu)
            if self.index_de_l_image<self.image_max : ##si on atteint la fin de la vidéo
                
                self.stock_coordonnees_image(self.nb_image_deja_analysees,liste_points, interactif)
                self.nb_image_deja_analysees += 1
                self.index_de_l_image += 1
                if interactif:
                    self.modifie=True
                self.clic_sur_label_video_ajuste_ui(point_attendu)
                
                       
            elif self.index_de_l_image==self.image_max :

                self.mets_a_jour_label_infos(self.tr(u"Vous avez atteint la fin de la vidéo"))
        
        
    def enableDefaire(self, value):
        """
        Contrôle la possibilité de défaire un clic
        @param value booléen
        """
        self.ui.pushButton_defait.setEnabled(value)
        self.ui.actionDefaire.setEnabled(value)
        
    def enableRefaire(self, value):
        """
        Contrôle la possibilité de refaire un clic
        @param value booléen
        """
        self.ui.pushButton_refait.setEnabled(value)
        self.ui.actionRefaire.setEnabled(value)
        
    def clic_sur_label_video_ajuste_ui(self,point_attendu):
        """
        Ajuste l'interface utilisateur pour attendre un nouveau clic
        @param point_attendu le numéro du point qui est à cliquer
        """

        self.lance_capture = True
        self.enableDefaire(len(self.tousLesClics) > 0)
        self.enableRefaire(self.tousLesClics.nextCount() > 0)

        if point_attendu==1 : # pour une acquisition sur une nouvelle image
            if len(self.label_video.liste_points) > 0:
                self.tousLesClics.append(self.label_video.liste_points)
            self.label_video.liste_points=[]
            self.affiche_image()
            self.tracer_trajectoires("absolu")
        
    def stock_coordonnees_image(self, ligne, liste_points, interactif=True, index_image = False):
        """
        place les données dans le tableau, rempli les dictionnaires de 
        @param ligne le numérode la ligne où placer les données (commence à 0)
        @param liste_points la liste des points cliqués sur l'image courante
        @param interactif vrai s'il faut rafraîchir tout de suite l'interface utilisateur.
        """
        if not index_image :
            index_image = self.index_de_l_image
        t = "%4f" %((ligne)*self.deltaT)
        self.points[ligne]=[t]+liste_points
       
        
        
        #rentre le temps dans la première colonne
        self.ui.tableWidget.insertRow(ligne)
        self.ui.tableWidget.setItem(ligne,0,QTableWidgetItem(t))
        
        i=0
        #Pour chaque point dans liste_points, insère les valeur dans la ligne
        for point in liste_points :
        #ajoute les coordonnées "en pixel" des points dans des dictionnaires de coordonnées
            x=point.x()
            y=point.y()
            if x in self.pX.keys():
                self.pX[x].append(point)
            else:
                self.pX[x]=[point]
                
            if y in self.pY.keys():
                self.pY[y].append(point)
            else:
                self.pY[y]=[point]
            
	    
	    
            pm=self.pointEnMetre(point)
            self.ui.tableWidget.setItem(ligne,i+1,QTableWidgetItem(str(pm.x())))
            self.ui.tableWidget.setItem(ligne,i+2,QTableWidgetItem(str(pm.y())))
            i+=2
        if interactif:
            self.ui.tableWidget.show()
        #enlève la ligne supplémentaire, une fois qu'une ligne a été remplie
        if ligne == 0 :
            self.ui.tableWidget.removeRow(1)

    def transforme_index_en_temps(self, index):
        return float(self.deltaT*(index))
    
    def affiche_image_spinbox(self):
        self.index_de_l_image = self.ui.spinBox_image.value()
        self.affiche_image()
    
    def affiche_image(self):
        self.extract_image(self.filename, self.index_de_l_image)
        image=QImage(self.chemin_image)
     
        self.image_640_480 = image.scaled(640,480,Qt.KeepAspectRatio)
#        try :
        if hasattr(self, "label_video"):
            self.label_video.setMouseTracking(True)
            self.label_video.setPixmap(QPixmap.fromImage(self.image_640_480))
            self.label_video.met_a_jour_crop()
            self.label_video.update()

            self.label_video.show()
            self.ui.horizontalSlider.setValue(self.index_de_l_image)
            self.ui.spinBox_image.setValue(self.index_de_l_image)

        
    def recommence_echelle(self):
        self.ui.tabWidget.setCurrentIndex(0)
        self.echelle_image=echelle()
        self.affiche_echelle()
        try:
            self.job.dialog.close()
            self.job.close()
        except AttributeError:
            pass


        self.demande_echelle()
        
    def affiche_image_slider(self):
        print self.index_de_l_image
        self.index_de_l_image = self.ui.horizontalSlider.value()
        self.affiche_image()

    def demande_echelle(self):
        """
        demande l'échelle interactivement
        """
        echelle_result_raw = QInputDialog.getText(None,
                                                  self.tr(u"Définir une échelle"), 
                                                  self.tr(u"Quelle est la longueur en mètre de votre étalon sur l'image ?"),
                                                  QLineEdit.Normal, QString("1.0"))
        if echelle_result_raw[1] == False :
            return None
        try :
            echelle_result = [float(echelle_result_raw[0].replace(",",".")), echelle_result_raw[1]]

            if echelle_result[0] <= 0 or echelle_result[1] == False :
                self.mets_a_jour_label_infos(self.tr(u" Merci d'indiquer une échelle valable"))
            else :
                self.echelle_image.etalonneReel(echelle_result[0])
                
                self.job = Label_Echelle(self.label_video,self)
                self.job.setPixmap(QPixmap(self.chemin_image))
                self.job.show()
        except ValueError :
            self.mets_a_jour_label_infos(self.tr(u" Merci d'indiquer une échelle valable"))
            self.demande_echelle()
        self.ui.pushButton_video.setEnabled(0)

    def feedbackEchelle(self, p1, p2):
        """
        affiche une trace au-dessus du self.job, qui reflète les positions
        retenues pour l'échelle
        """
        from echelle import Label_Echelle_Trace
        self.label_echelle_trace = Label_Echelle_Trace(self.label_video, p1,p2)
        self.label_echelle_trace.show()


    def reinitialise_environnement(self):
        for filename in glob(os.path.join(IMG_PATH,"*.jpg")):
            os.remove(filename)
                
    def on_closeCanvas(self, event):
        self.canvas.fig.clear()
        
    def closeEvent(self,event):
        """
        Un crochet pour y mettre toutes les procédures à faire lors
        de la fermeture de l'application.
        """
        from tempfile import gettempdir
        if hasattr(self,'canvas'):
            self.canvas.close()
            del self.canvas
        self.nettoieVideosRecodees()
        if self.verifie_donnees_sauvegardees() :
            self.reinitialise_environnement()
            liste_fichiers = os.listdir(gettempdir())
            for fichier in liste_fichiers :
                if "pymeca" in fichier :
                    try :
                        os.remove(fichier)
                    except OSError:
                        pass
            event.accept()
        else :
            event.ignore()

    def nettoieVideosRecodees(self):
        """
        Retire les vidéos recodées automatiquement
        """
        for f in self.newVideos:
            subprocess.call("rm -f %s" %f, shell=True)

    def verifie_donnees_sauvegardees(self):
        if self.modifie:
            retour = QMessageBox.warning(self,QString(self.tr(unicode("Les données seront perdues","utf8"))),QString(self.tr(unicode("Votre travail n'a pas été sauvegardé\nVoulez-vous les sauvegarder ?","utf8"))),QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel )
            if retour == QMessageBox.Yes :
                self.enregistre_ui()
                return True
            elif retour == QMessageBox.No :
                return True
            elif retour == QMessageBox.Cancel :
                return False
        else :
            return True
    
    def aller_a_l_image(self, increment):
        increment = int(increment)
        self.index_de_l_image = self.index_de_l_image + increment
        if self.index_de_l_image <= self.image_max :
            self.affiche_image()
            
        elif self.index_de_l_image==0 : 
            self.index_de_l_image=1
            self.mets_a_jour_label_infos(self.tr(unicode("Vous avez atteint le début de la vidéo","utf8")))
            self.affiche_image()
    
    def mets_a_jour_label_infos(self, message):
    ### On utilise la barre de status pour afficher les messages : permet de ganager un la place en envelant le label_infos_image ###
        self.statusBar().showMessage(message)


    def openexample(self):
        dir_="%s" %(self._dir("videos"))
        self.reinitialise_tout()
        filename=QFileDialog.getOpenFileName(self,self.tr(unicode("Ouvrir une vidéo","utf8")), dir_,self.tr(unicode("fichiers vidéos ( *.avi *.mp4 *.ogv *.mpg *.mpeg *.ogg *.mov *.wmv)","utf8")))
        self.openTheFile(filename)
        
    def openfile(self):
        """
        Ouvre un dialogue pour choisir un fichier vidéo puis le charge
        """
        dir_=self._dir("videos")
        filename=QFileDialog.getOpenFileName(self,self.tr(unicode("Ouvrir une vidéo","utf8")), dir_,self.tr(unicode("fichiers vidéos ( *.avi *.mp4 *.ogv *.mpg *.mpeg *.ogg *.wmv *.mov)","utf8")))
        self.openTheFile(filename)
        try :
            self.reinitialise_capture()
        except :
            pass
        
    def renomme_le_fichier(self):
        renomme_fichier = QMessageBox.warning(self,self.tr("Nom de fichier non conforme"),QString(self.tr(unicode("Le nom de votre fichier contient des caractères accentués ou des espaces.\n Merci de bien vouloir le renommer avant de continuer","utf8"))), QMessageBox.Ok,QMessageBox.Ok)
        filename=QFileDialog.getOpenFileName(self,self.tr(unicode("Ouvrir une vidéo","utf8")), self._dir("videos"),"*.avi")
        self.openTheFile(filename)

    def openTheFile(self,filename):
        """
        Ouvre le fichier de nom filename, enregistre les préférences de
         fichier vidéo.
        @param filename chaîne de caractère, de type string,QSring ou QByteArray
         le forçage de type permet d'accepter chacune des variantes en entrée.
         N.B.: l'attribut self.prefs.lastVideo sera qui sera enregistré est de
         type string et d'encodage unicode.
        """
        if filename != "" : 
            filename = QString(filename)
            filename = filename.toUtf8()
            data = filename.data()
            self.filename = data.decode('utf-8')
            goOn = self.init_cvReader()
            if goOn : #video is in goo format
                
                self.prefs.lastVideo=self.filename
                self.init_image()
                self.mets_a_jour_label_infos(self.tr(u"Veuillez choisir une image et définir l'échelle"))
                self.ui.Bouton_Echelle.setEnabled(True)
                self.ui.spinBox_nb_de_points.setEnabled(True)
                self.ui.horizontalSlider.setEnabled(1)
                self.label_video.show()

                self.prefs.videoDir=os.path.dirname(self.filename)
                self.prefs.save()

                

    def propos(self):
        try:
            loc = locale.getdefaultlocale()[0][0:2]
        except TypeError:
            loc=''
        if loc in licence.keys():
            licence_XX=licence[loc] %Version
        else:
            licence_XX=licence["en"] %Version
        QMessageBox.warning(None,"Licence",QString(licence_XX), QMessageBox.Ok,QMessageBox.Ok)
        
    def aide(self):
        lang=locale.getdefaultlocale()[0][0:2]
        helpfile="%s/help-%s.xhtml" %(self._dir("help"),lang)
        if os.path.exists(helpfile):
            command="firefox --new-window %s" %helpfile
            status,output=commands.getstatusoutput(command)
            if status != 0:
                command="x-www-browser %s" %helpfile
                status,output=commands.getstatusoutput(command)
        else:
            QMessageBox.warning(None,"Aide",self.trUtf8("Désolé pas de fichier d'aide pour le langage %1.").arg(lang))
        
        
    def init_image(self):
        """intialise certaines variables lors le la mise en place d'une nouvelle image"""
        self.index_de_l_image = 1
        self.init_interface()
        self.trajectoire = {}
        self.ui.spinBox_image.setMinimum(1)
        self.defini_barre_avancement()
        self.echelle_image=echelle()
        self.affiche_echelle()
        self.ui.tab_traj.setEnabled(0)
        self.ui.spinBox_image.setEnabled(1)
        self.a_une_image = True
        self.affiche_image()
        self.reinitialise_environnement()
        
        
    def defini_barre_avancement(self):
        """récupère le maximum d'images de la vidéo et défini la spinbox et le slider"""
        framerate, self.image_max = self.cvReader.recupere_avi_infos()
        #print framerate, self.image_max
        self.deltaT = float(1.0/framerate)
        self.ui.horizontalSlider.setMinimum(1)
        
        self.ui.horizontalSlider.setMaximum(int(self.image_max))
        self.ui.spinBox_image.setMaximum(int(self.image_max))
        
        fichier = os.path.join(IMG_PATH, VIDEO + SUFF %1 )
        try :
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
        imfilename=os.path.join(IMG_PATH, VIDEO + SUFF %index)
        if force or not os.path.isfile(imfilename):
            self.cvReader.writeImage(index,imfilename)
        self.chemin_image = imfilename
          
    def traiteOptions(self):
        for opt,val in self.opts:
            if opt in ['-f','--fichier_mecavideo']:
                if os.path.isfile(val) and os.path.splitext(val)[1] == ".mecavideo":
                    try:
                        self.rouvre(val)
                    except:
                        pass
                if os.path.isfile(val) and os.path.splitext(val)[1] == ".avi":
                    self.openTheFile(val)
                    
        
def usage():
    print ("Usage : pymecavideo [-f fichier | --fichier_pymecavideo=fichier] [--maxi]")

def run():
    global app
    
    args=sys.argv[1:]
    try:
        opts, args = getopt.getopt(args, "f:m:", ["fichier_mecavideo=","maxi"] )
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    
    ###translation##
    locale = "%s" %QLocale.system().name()
    #locale = "%s" %QString("en_EN")
    
    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale):
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    langdir=os.path.join(StartQT4._dir("langues"),
                         "pymecavideo_"+locale)
    if appTranslator.load(langdir):
        b = app.installTranslator(appTranslator)
    
    windows = StartQT4(None,opts)
    
    windows.show()
    
    sys.exit(app.exec_())

def lanceQtiplot(fichier):
    """
    lanceur pour Qtiplot, dans un thread
    param @fichier le fichier de projet
    """
    os.system("qtiplot %s" %fichier)

def lanceSciDAVis(fichier):
    """
    lanceur pour SciDAVis, dans un thread
    param @fichier le fichier de projet
    """
    os.system("scidavis %s" %fichier)

if __name__ == "__main__":
    run()
