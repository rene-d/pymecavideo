#-*- coding: utf-8 -*-

licence={}
licence['en']="""
    pymecavideo version %s:

    a program to track moving points in a video frameset
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
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
    
    Ce projet est un logiciel libre : vous pouvez le redistribuer, le modifier selon les terme de la GPL (GNU Public License) dans les termes de la Free Software Foundation concernant la version 2 ou plus de la dite licence.
    
    Ce programme est fait avec l'espoir qu'il sera utile mais SANS AUCUNE GARANTIE. Lisez la licence pour plus de détails.
    
    <http://www.gnu.org/licenses/>.
"""

from vecteur import vecteur
from sets import Set
import sys, os, thread, time, commands, linecache, codecs, re
import locale, getopt, pickle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from glob import glob
from Ui_pymecavideo  import Ui_pymecavideo
from echelle import Label_Echelle, echelle
from math import sqrt
from label_video import Label_Video
from point import Point, Repere
from label_trajectoire import Label_Trajectoire
from label_origine import Label_Origine
from cadreur import Cadreur
from preferences import Preferences
from dbg import Dbg
from listes import listePointee
from points_ecran import PointEcran
from version import Version

class StartQT4(QMainWindow):
    def __init__(self, parent, filename, opts):
        #Données principales du logiciel : 
        #self.index_de_l_image : la position de l'image actuellement affichée
        
        ######QT
        QMainWindow.__init__(self)
        QWidget.__init__(self, parent)
        self.ui = Ui_pymecavideo()
        self.ui.setupUi(self)

        ####intilise les répertoires
        self._dir()


        #variables à initialiser
        self.init_variables(filename,opts)
        self.init_interface()
        
        #connections internes
        self.ui_connections()
        


        #prise en compte d'options de la ligne de commande
        self.traiteOptions()
        
        #chargement d'un éventuel premier fichier
        self.splashVideo()
            
    def splashVideo(self):
        for opt,val in self.opts:
            if opt in ['-f','--fichier_mecavideo']:
                return
        if os.path.isfile(self.filename):
            self.openTheFile(self.filename)
        elif os.path.isfile(self.prefs.lastVideo):
            self.openTheFile(self.prefs.lastVideo)
        

    def init_variables(self, filename, opts):
        self.index_max = 1
        self.sens_X=1
        self.sens_Y=1
        self.origine = vecteur(240,320)
        self.dbg=Dbg(0)
        self.deltaT = 0.04       #durée 40 ms par défaut : 25 images/s
        self.lance_capture = False
        self.modifie=False
        self.points={}        #dictionnaire des points cliqués, par n° d'image.
        self.trajectoire = {} #dictionnaire des points des trajectoires
        self.points_ecran = PointEcran() #objet contenant les points apparaissant à l'écran, indexés par numéro
        self.pX={}            #points apparaissant à l'écran, indexés par X
        self.pY={}            #points apparaissant à l'écran, indexés par Y
        self.index_du_point = 0
        self.point_ID=1        #index du point courant
        self.echelle_image = echelle() # objet gérant l'image
        self.nb_image_deja_analysees = 0 #indique le nombre d'images dont on a dejà fait l'étude, ce qui correspond aussi au nombre de lignes dans le tableau.
        self.couleurs=["red", "blue", "cyan", "magenta", "yellow", "gray", "green"] #correspond aux couleurs des points del a trajectoire
        self.nb_de_points = 1        # nombre de points suivis
        self.premiere_image = 1      # n° de la première image cliquée
        self.index_de_l_image = 1    # image à afficher
        self.prefs=Preferences(self)
        self.echelle_v = 0
        self.filename=filename
        self.opts=opts
        self.tousLesClics=listePointee() # tous les clics faits sur l'image
        self.init_interface()
        
    def init_interface(self):
        self.cree_tableau()
        self.label_trajectoire=Label_Trajectoire(self.ui.tab_traj, self)
        self.ui.horizontalSlider.setEnabled(0)
        self.ui.echelleEdit.setEnabled(0)
        self.affiche_echelle()
        self.ui.tab_traj.setEnabled(0)
        self.ui.actionSaveData.setEnabled(0)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(0)
        self.ui.spinBox_image.setEnabled(0)
        self.affiche_lance_capture(False)
        
        self.ui.button_video.setEnabled(0)
        self.affiche_nb_points(False)
        self.ui.Bouton_Echelle.setEnabled(False)
        self.ui.echelle_v.setDuplicatesEnabled(False)
        self.setEchelle_v()
        #création du label qui contiendra la vidéo.
        self.label_video = Label_Video(parent=self.ui.label, app=self)
        self.ui.label_axe.hide()
        self.ui.pushButton_origine.hide()
        self.ui.checkBox_abscisses.hide()
        self.ui.checkBox_ordonnees.hide()


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
         l'échelle courante pour les distances sur l'image
        """
        if self.echelle_image.isUndef():
            self.ui.echelleEdit.setText(self.tr("indéf."))
            self.ui.Bouton_Echelle.setEnabled(True)
        else:
            self.epxParM=self.echelle_image.longueur_pixel_etalon/self.echelle_image.longueur_reelle_etalon
            epxParM=self.echelle_image.longueur_pixel_etalon/self.echelle_image.longueur_reelle_etalon
            self.ui.echelleEdit.setText("%.1f" %epxParM)
            self.ui.Bouton_Echelle.setEnabled(False)
        self.ui.echelleEdit.show()
        self.ui.Bouton_Echelle.show()
 
    def reinitialise_tout(self, echelle_image=None, nb_de_points=None, tousLesClics=None):
        """
        Réinitialise complètement l'interface de saisie. On peut quand même
        passer quelques paramètres à conserver :
        @param echelle_image évite de ressaisir l'échelle de l'image
        @param nb_de_points évite de ressaisir le nombre de points à suivre
        @param tousLesClics permet de conserver une liste de poinst à refaire
        """
        self.montre_vitesses(False)
        #self.oubliePoints()
        self.label_trajectoire.update()
        self.ui.label.update()
        self.label_video.update()
        self.init_variables(self.filename,None)
        self.init_interface()
        for enfant in self.label_video.children():
              enfant.hide()      
              del enfant
        if echelle_image:
            self.echelle_image=echelle_image
        if nb_de_points:
            self.nb_de_points=nb_de_points
        if tousLesClics:
            self.tousLesClics=tousLesClics

    def reinitialise_capture(self):
        self.montre_vitesses(False)
        #self.oubliePoints()
        self.label_trajectoire.update()
        self.ui.label.update()
        self.label_video.update()
        self.label_video.setCursor(Qt.ArrowCursor)

        for enfant in self.label_video.children():
              enfant.hide()
              del enfant
        del self.label_video.zoom_croix
        del self.label_video
        self.init_variables(self.filename,None)
        self.affiche_image()

        self.echelle_image=echelle()
        self.affiche_echelle()
        self.ui.horizontalSlider.setEnabled(1)
        self.ui.spinBox_image.setEnabled(1)
        self.ui.spinBox_image.setValue(1)
        self.ui.pushButton_defait.setEnabled(0)
        self.ui.pushButton_refait.setEnabled(0)
        self.affiche_nb_points(0)
        if self.table_widget:
            self.table_widget.clear()

    def ui_connections(self):
        """connecte les signaux de QT"""
        QObject.connect(self.ui.actionOuvrir_un_fichier,SIGNAL("triggered()"), self.openfile)
        QObject.connect(self.ui.actionExemples,SIGNAL("triggered()"), self.openexample)
        QObject.connect(self.ui.action_propos,SIGNAL("triggered()"), self.propos)
        QObject.connect(self.ui.actionAide,SIGNAL("triggered()"), self.aide)
        QObject.connect(self.ui.actionPreferences,SIGNAL("triggered()"), self.prefs.setFromDialog)
        QObject.connect(self.ui.actionQuitter,SIGNAL("triggered()"), self.close)
        QObject.connect(self.ui.actionSaveData,SIGNAL("triggered()"), self.enregistre_ui)
	QObject.connect(self.ui.actionCopier_dans_le_presse_papier,SIGNAL("triggered()"), self.presse_papier)
	QObject.connect(self.ui.actionRouvrirMecavideo,SIGNAL("triggered()"), self.rouvre_ui)
        QObject.connect(self.ui.Bouton_Echelle,SIGNAL("clicked()"), self.demande_echelle)
        QObject.connect(self.ui.horizontalSlider,SIGNAL("valueChanged(int)"), self.affiche_image_slider)
        QObject.connect(self.ui.spinBox_image,SIGNAL("valueChanged(int)"),self.affiche_image_spinbox)
        QObject.connect(self.ui.Bouton_lance_capture,SIGNAL("clicked()"),self.debut_capture)
        QObject.connect(self,SIGNAL("clic_sur_video()"),self.clic_sur_label_video)
        QObject.connect(self.ui.comboBox_referentiel,SIGNAL("currentIndexChanged (int)"),self.tracer_trajectoires)
        QObject.connect(self.ui.tabWidget,SIGNAL("currentChanged (int)"),self.tracer_trajectoires)
        QObject.connect(self.ui.echelle_v,SIGNAL("currentIndexChanged (int)"),self.refait_vitesses)
        QObject.connect(self.ui.echelle_v,SIGNAL("editTextChanged (int)"),self.refait_vitesses)
        QObject.connect(self.ui.button_video,SIGNAL("clicked()"),self.video)
        QObject.connect(self.ui.pushButton_select_all_table,SIGNAL("clicked()"),self.presse_papier)
        QObject.connect(self.ui.pushButton_reinit,SIGNAL("clicked()"),self.reinitialise_capture)
        QObject.connect(self.ui.pushButton_defait,SIGNAL("clicked()"),self.efface_point_precedent)
        QObject.connect(self.ui.pushButton_refait,SIGNAL("clicked()"),self.refait_point_suivant)
        QObject.connect(self.ui.checkBox_avancees,SIGNAL("stateChanged(int)"),self.affiche_fonctionnalites_avancees)
        QObject.connect(self.ui.pushButton_origine,SIGNAL("clicked()"),self.choisi_nouvelle_origine)
        QObject.connect(self.ui.checkBox_abscisses,SIGNAL("stateChanged(int)"),self.        change_sens_X )
        QObject.connect(self.ui.checkBox_ordonnees,SIGNAL("stateChanged(int)"),self.change_sens_Y )
        QObject.connect(self,SIGNAL('change_axe_origine()'),self.change_axe_origine)

    def choisi_nouvelle_origine(self):
        nvl_origine=QMessageBox.information(self,QString("NOUVELLE ORIGINE"),\
QString("Choisissez, en cliquant sur la video le point qui sera la nouvelle origine"))
        label = Label_Origine(parent=self.ui.label, app=self)
        label.show()
        self.emit(SIGNAL('change_axe_origine()'))
        
    def change_axe_origine(self):
        """mets à jour le tableau de données"""
        #construit un dico plus simple à manier, dont la clef est point_ID et qui contient les coordoonées
        #print "change axe ou origine"
        if not self.points_ecran.isEmpty():
            liste_clef=[]
            donnees={}
            for key in self.points_ecran.keys():
                donnees[self.points_ecran.pointID(key)]=self.points_ecran.pointP(key)
                liste_clef.append(self.points_ecran[key][2])
            liste_clef.sort()
            #print liste_clef
            #print donnees
            #print self.origine
            for key in liste_clef :
                serie,position=self.couleur_et_numero(int(key))
                #print serie,position,donnees[key]
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
        #print "change Y"
        if self.ui.checkBox_ordonnees.isChecked():
            self.sens_Y = -1

        else :
            self.sens_Y = 1
        #print self.sens_Y
        self.emit(SIGNAL('change_axe_origine()'))

    def affiche_fonctionnalites_avancees(self):

        if self.ui.checkBox_avancees.isChecked() :
            self.ui.label_axe.show()
            self.ui.pushButton_origine.show()
            self.ui.checkBox_abscisses.show()
            self.ui.checkBox_ordonnees.show()
        else :
            self.ui.label_axe.hide()
            self.ui.pushButton_origine.hide()
            self.ui.checkBox_abscisses.hide()
            self.ui.checkBox_ordonnees.hide()


    def pointEnMetre(self,p):
        """
        renvoie un point, dont les coordonnées sont en mètre, dans un
        référentiel "à l'endroit"
        @ param point un point en "coordonnées d'écran"
        """
        return vecteur(float(p.x())*self.echelle_image.mParPx(),
                       float(480-p.y())*self.echelle_image.mParPx())
    
    def presse_papier(self):
        """Sélectionne la totalité du eau de coordonnées
        et l'exporte dans le presse-papier (l'exportation est implicitement
        héritée de la classe utilisée pour faire le tableau). Les
        séparateurs décimaux sont automatiquement remplacés par des virgules
        si la locale est française.
        """
        trange=QTableWidgetSelectionRange(0,0,
                                          self.table_widget.rowCount()-1,
                                          self.table_widget.columnCount()-1)
        self.table_widget.setRangeSelected(trange,True)

    def _dir(self,lequel=None):
        """renvoie les répertoires utiles.
        paramètre lequel (chaîne) : peut prendre les valeurs utiles suivantes,
        "cwd", "home", "ressources", "images", "icones"

        quand le paramètre est absent, initialise les répertoires si nécessaire
        """
        
        home = os.getenv("HOME")
        pymecavideo_rep=home+"/.pymecavideo"
        pymecavideo_rep_images=pymecavideo_rep + "/images_extraites"
        pymecavideo_rep_icones=pymecavideo_rep + "/icones"
        pymecavideo_rep_langues=pymecavideo_rep + "/lang"
        if   lequel == "home": return home
        elif lequel == "cwd": return self.cwd
        elif lequel == "ressources": return pymecavideo_rep
        elif lequel == "images": return pymecavideo_rep_images
        elif lequel == "icones": return pymecavideo_rep_icones
        elif lequel == "langues": return pymecavideo_rep_langues
        elif lequel == "share" : return self.pymecavideo_rep_install
        elif lequel == "help" : 
            if os.path.isdir("/usr/share/doc/python-mecavideo/html") :
                return "/usr/share/doc/python-mecavideo/html"
            elif os.path.isdir("/usr/share/doc/HTML/fr/pymecavideo") :
                return "/usr/share/doc/HTML/fr/pymecavideo"
        elif type(lequel) == type(""):
            self.dbg.p(1,"erreur, appel de _dir() avec le paramètre inconnu %s" %lequel)
            self.close()
        else:
            self.pymecavideo_rep_install= os.path.dirname(os.path.abspath(__file__))
            sys.path.append(self.pymecavideo_rep_install) # pour pickle !
            self.cwd=os.getcwd()
 
        self.ui.pushButton_defait.setIcon(QIcon(self._dir("icones")+"/"+"undo.png"))
        self.ui.pushButton_refait.setIcon(QIcon(self._dir("icones")+"/"+"redo.png"))

    def rouvre_ui(self):
        os.chdir(self._dir("home"))
        fichier = QFileDialog.getOpenFileName(self,"FileDialog", "","*.mecavideo")
        if fichier != "":
            self.rouvre(fichier)

    def loads(self,s):
        s=s[1:-1].replace("\n#","\n")
        (self.filename,self.premiere_image,self.echelle_image.longueur_reelle_etalon,self.echelle_image.longueur_pixel_etalon,self.echelle_image.p1,self.echelle_image.p2,self.deltaT,self.nb_de_points) = pickle.loads(s)

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
        self.echelle_image=echelle()
        self.dbg.p(2,self.tr("chemin vers les modules : %s") %sys.path)
        self.loads(dd)
        self.openTheFile(self.filename)
        self.affiche_echelle()
        n=len(self.points.keys())
        self.nb_image_deja_analysees = n
        self.ui.horizontalSlider.setValue(n+self.premiere_image)
        self.ui.spinBox_image.setValue(n+self.premiere_image)
        self.affiche_nb_points(self.nb_de_points)
        self.affiche_image()
        self.debut_capture()


                        
    def entete_fichier(self, msg=""):
        result=u"""#pymecavideo
#video = %s
#index de depart = %d
#echelle %5f m pour %5f pixel
#echelle pointee en %s %s
#intervalle de temps : %f
#suivi de %s point(s)
#%s
#""" %(self.filename,self.premiere_image,self.echelle_image.longueur_reelle_etalon,self.echelle_image.longueur_pixel_etalon,self.echelle_image.p1,self.echelle_image.p2,self.deltaT,self.nb_de_points,msg)
        return result

    def dumps(self):
        return "#"+pickle.dumps((self.filename,self.premiere_image,self.echelle_image.longueur_reelle_etalon,self.echelle_image.longueur_pixel_etalon,self.echelle_image.p1,self.echelle_image.p2,self.deltaT,self.nb_de_points)).replace("\n","\n#")
    def enregistre(self, fichier):
        sep_decimal="."
        try:
            if locale.getdefaultlocale()[0][0:2]=='fr':
                # en France, le séparateur décimal est la virgule
                sep_decimal=","
        except TypeError:
            pass
        if fichier != "":
            file = open(fichier+".mecavideo", 'w')
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
            #self.modifie=False
        
    def enregistre_ui(self):
        os.chdir(self._dir("home"))
        
        if self.points!={}:
            fichier = QFileDialog.getSaveFileName(self,"FileDialog", "data.csv","*.csv *.txt *.asc *.dat")
            self.enregistre(fichier)

    def debut_capture(self):
        """permet de mettre en place le nombre de point à acquérir"""
        #self.label_video.
        #self.label_echelle_trace.lower()

        #self.ui.label.lower()
        self.label_echelle_trace.hide()
        self.label_video.setVisible(True)
        self.label_video.setFocus()
        self.label_video.activateWindow()
        
        self.nb_de_points = self.ui.spinBox_nb_de_points.value()
        self.affiche_nb_points(False)
        self.affiche_lance_capture(False)
        self.ui.horizontalSlider.setEnabled(1)
        self.premiere_image=self.ui.horizontalSlider.value()
        #self.affiche_image()
        #self.label_video.zoom_croix.hide()
        self.affiche_point_attendu(1)
        self.lance_capture = True
        self.label_video.setCursor(Qt.CrossCursor)
        self.ui.tab_traj.setEnabled(1)
        self.ui.actionSaveData.setEnabled(1)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(1)
        self.ui.comboBox_referentiel.setEnabled(1)
        self.ui.pushButton_select_all_table.setEnabled(1)
        
        self.label_trajectoire = Label_Trajectoire(self.ui.tab_traj,self)
        self.ui.comboBox_referentiel.clear()
        self.ui.comboBox_referentiel.insertItem(-1, "camera")
        for i in range(self.nb_de_points) :
            self.ui.comboBox_referentiel.insertItem(-1, QString(self.tr("point N°")+" "+str(i+1)))
        self.cree_tableau()

    def cree_tableau(self):
        """
        Crée un tableau de coordonnées neuf dans l'onglet idoine.
        """
        try: # efface tout tableau existant préalablement
            self.table_widget.hide()
            self.table_widget.close()
        except AttributeError:
            pass
        from table import standardDragTable
        self.table_widget=standardDragTable(self.ui.tab_coord)
        self.ui.tab_coord.setEnabled(1)
        self.table_widget.setRowCount(1)
        self.table_widget.setColumnCount(self.nb_de_points*2 + 1)
        # on met des titres aux colonnes.
        self.table_widget.setHorizontalHeaderItem(0,QTableWidgetItem('t (s)'))
        for i in range(self.nb_de_points):
            x="X%d (m)" %(1+i)
            y="Y%d (m)" %(1+i)
            self.table_widget.setHorizontalHeaderItem(1+2*i,QTableWidgetItem(x))
            self.table_widget.setHorizontalHeaderItem(2+2*i,QTableWidgetItem(y))
        self.table_widget.setGeometry(QRect(10, 100, 640, 480))
        self.table_widget.setDragEnabled(True)

    def traiteSouris(self,p):
        """
        cette fonction est rappelée par label_trajectoire quand la souris
        bouge au-dessus : p est un vecteur.
        """
        if not self.prefs.proximite: return
        portee=30
        pX=Set()
        pY=Set()
        for x in self.pX.keys():
            if p.x()-portee<x<p.x()+portee:
                for a in self.pX[x]: pX.add(a)
            else:
                for a in self.pX[x]: a.montre_vitesse(False)
        for y in self.pY.keys():
            if p.y()-portee<y<p.y()+portee:
                for a in self.pY[y]: pY.add(a)
            else:
                for a in self.pY[y]: a.montre_vitesse(False)
        intersection=list(pX & pY)
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
        #for n in range(self.nb_de_points):
            ##if n==referentiel:
                ##pass
            
        self.liste_points=list(range(self.points_ecran.length()))
        
        for key in self.points_ecran.keys():
   
            self.liste_points[self.points_ecran.pointID(key) - 1] = self.points_ecran.pointP(key)
        #print liste_clef
        #print liste_clef
        #print donnees
        #print self.origine
        #i=0
        for i in range(len(self.liste_points)//self.nb_de_points) :
            #print i, referentiel
            coord_ref = self.liste_points[referentiel+self.nb_de_points*i]
            for n in range(self.nb_de_points):
                coord_point=self.liste_points[self.nb_de_points*i+n]
                p = coord_point-coord_ref
                min=p.minXY(min)
                max=p.maxXY(max)
    
        print min, max
        if min!=None and max!=None:
            return (min+max)*0.5
        else:
            return vecteur(320,240)

    def refait_vitesses(self, newText=""):
        """
        recalcule les vitesses de tous les points tracés.
        """
        for index in self.trajectoire.keys():
            if index[:6]=="point-":
                [p,point] = self.trajectoire[index]
                self.echelle_v=self.ui.echelle_v.currentText()
                show=True
                point.calcule_vitesse(self.echelle_v,show)

    def setEchelle_v(self):
        ech_v="%s" %self.echelle_v
        index=self.ui.echelle_v.findText(ech_v)
        if index <0:
            self.ui.echelle_v.addItem(ech_v)
            index=self.ui.echelle_v.findText(ech_v)
        self.ui.echelle_v.setCurrentIndex(index)
        self.refait_vitesses()
        
    def visibilite_vitesses(self):
        """
        change le critère de visibilité des vitesses selon self.prefs
        """
        if not self.prefs.proximite:
            #choix par défaut
            self.label_trajectoire.setMouseTracking(0)
            self.montre_vitesses(True)
        else:
            self.montre_vitesses(False)
            self.label_trajectoire.setMouseTracking(1)
            self.label_trajectoire.setFocus()
            self.label_trajectoire.update()

                
    def montre_vitesses(self, show=True):
        """
        montre ou cache les vitesses, selon le paramètre show
        """
        for index in self.trajectoire.keys():
            if index[:6]=="point-":
                [p,point] = self.trajectoire[index]
                point.montre_vitesse(show)
        if not show:
            self.label_trajectoire.update()

    def refait_point_suivant(self):
        a = self.ui.spinBox_image.value()
        self.ui.spinBox_image.setValue(a+1)
        self.affiche_image_spinbox()
        
        
    def efface_point_precedent(self):
        """revient au point précédent
        """
        
        a = self.ui.spinBox_image.value()
        self.ui.spinBox_image.setValue(a-1)
        self.affiche_image_spinbox()
        self.ui.pushButton_refait.setEnabled(1)
        self.nb_image_deja_analysees -= 1
        




    def video(self):
        ralenti=[1,2,4,8][self.ui.comboBox_fps.currentIndex()]
        ref=self.ui.comboBox_referentiel.currentText().split(" ")[-1]
        if len(ref)==0 or ref == "camera": return
        c=Cadreur(int(ref),self)
        c.cropimages()
        c.creefilm(ralenti)
        c.montrefilm()
        
        
    def tracer_trajectoires(self, newValue):
        """
        traite les signaux émis par le changement d'onglet, ou
        par le changement de référentiel dans l'onglet des trajectoires.
        On peut aussi appeler cette fonction directement, auquel cas on
        donne la valeur "absolu" à newValue pour reconnaître ce cas.
        efface les trajectoires anciennes, puis
        trace les trajectoires en fonction du référentiel choisi.
        Pour le moment l'origine a pour coordonéees QT -> (320,240).
        """
        self.origine_qt=vecteur(320,240)
        if self.ui.tabWidget.currentIndex()!=0 :#Pas le premier onglet
            self.label_video.zoom_croix.hide()
            #self.oubliePoints()
            if newValue=="absolu":
                ref="camera"
            else:
                ref = self.ui.comboBox_referentiel.currentText().split(" ")[-1]
            #print "ref", ref
            if len(ref)==0 : return
            if ref != "camera":
                bc=self.mediane_trajectoires(int(ref)-1)
                self.origine_qt=vecteur(320,240)-bc
                
                if self.nb_de_points > 1:
                    self.ui.button_video.setEnabled(1)
            else:
                    # pas de vidéo si ref == "camera"
                    self.ui.button_video.setEnabled(0)
                    self.repere_camera = Repere(self.label_trajectoire, self.origine_qt, "black", 0, self)
                    self.repere_camera.show()

            #effaçage des points dans label_trajectoire
            if ref != "camera":
                liste_coord_new_ref=[]
                for i in range(len(self.liste_points)//self.nb_de_points) :
                    #print i, referentiel
                    coord_ref = self.liste_points[int(ref)-1+self.nb_de_points*i]
                    for n in range(self.nb_de_points):
                        coord_point=self.liste_points[self.nb_de_points*i+n]
                        p = coord_point-coord_ref+self.origine_qt
                        liste_coord_new_ref.append(p)
                for key in self.points_ecran.keys():
                    point_label_trajectoire =self.points_ecran.pointTraj(key)
                    serie,position = self.couleur_et_numero(self.points_ecran.pointID(key))
                    point_label_trajectoire.hide()
                    del point_label_trajectoire
                    point_label_trajectoire = Point(self.label_trajectoire, liste_coord_new_ref[self.points_ecran.pointID(key)-1],
self.couleurs[position-1],serie+1,self)
                    point_label_trajectoire.show()
                    self.points_ecran.pointTraj(key,point_label_trajectoire)
            else :
                for key in self.points_ecran.keys():
                    point_label_trajectoire =self.points_ecran.pointTraj(key)
                    serie,position = self.couleur_et_numero(self.points_ecran.pointID(key))
                    point_label_trajectoire.hide()
                    del point_label_trajectoire
                    point_label_trajectoire = Point(self.label_trajectoire,self.points_ecran.pointP(key) ,self.couleurs[position-1],serie+1,self)
                    point_label_trajectoire.show()
                    self.points_ecran.pointTraj(key, point_label_trajectoire)

            
    def affiche_point_attendu(self,n):
        """
        Renseigne sur le numéro du point attendu
        """
        self.mets_a_jour_label_infos(self.tr("Cliquer sur le point N°%d" %n))

    def couleur_et_numero(self,point_ID):
        """retourne la position du point sous forme d'un tuple. Exemple : le point numéro 17, avec des série de 3 points retourne : (5,2) cinquième série de
points, psition 2."""
        serie = int((point_ID-1)//self.nb_de_points)
        position = point_ID-1-serie*self.nb_de_points
        return (serie,position)
        #Attention, ça démarre de 0

    def clic_sur_label_video(self, liste_points=None, interactif=True):
        #if liste_points==None:
            #liste_points = self.label_video.liste_points
        #if self.nb_de_points > len(liste_points) :
            #point_attendu=1+len(liste_points)
        #else:
            #point_attendu=1
            #self.stock_coordonnees_image(self.nb_image_deja_analysees,liste_points, interactif)
        self.affiche_points()
        
        #si reotur en arrière
        #if (self.point_ID + 1) < (self.index_de_l_image)
        self.point_ID += 1
        
    def affiche_points(self):
        "affiche la liste des points dans les labels trajectoire et label_video"
        #crée le label contenant le point, dans les 2 labels
        p = self.label_video.liste_points_QT[-1]
        #print len(self.label_video.liste_points_QT),p
        (serie,position) = self.couleur_et_numero(len(self.label_video.liste_points_QT))
        #print (serie,position)
        point_label_trajectoire = Point(self.label_trajectoire, p, self.couleurs[position-1],position+1,self)
        point_label_trajectoire.show()
        point_label_video = Point(self.label_video, p, self.couleurs[position-1],position+1,self)
        point_label_video.show()
        self.points_ecran.addPoint((self.index_de_l_image,position), point_label_trajectoire,point_label_video,self.point_ID,p)

        self.ui.pushButton_defait.setEnabled(1)

        if position==self.nb_de_points-1 :
            if self.index_max <= self.index_de_l_image:
                self.index_max=self.index_de_l_image
            self.index_de_l_image += 1
            
        

        self.affiche_image()
        
        self.rempli_tableau(serie,position,p)

    def rempli_tableau(self,serie,position,coordonnees,recalcul=None):
        """rempli le tableau avec les coordoonées d'un point)"""
        if not recalcul :
            t = "%4f" %((self.index_de_l_image-self.premiere_image)*self.deltaT)
        x = (self.sens_X*(coordonnees.x()-self.origine.x()))/float(self.epxParM)
        #print self.sens_Y
        y = (self.sens_Y*(self.origine.y()-coordonnees.y()))/float(self.epxParM)
        if not recalcul :
            if position ==0:
                self.table_widget.insertRow(serie)
                self.table_widget.setItem(serie,0,QTableWidgetItem(t))
        self.table_widget.setItem(serie,2*position+1,QTableWidgetItem(str(x)))
        self.table_widget.setItem(serie,2*position+2,QTableWidgetItem(str(y)))
        #print x,y

    
    def affiche_image_spinbox(self):
        self.index_de_l_image = self.ui.spinBox_image.value()
        if self.index_de_l_image-1==self.index_max:
            self.ui.pushButton_refait.setEnabled(0)
        liste=[]
        if self.lance_capture:
            
            for key in self.points_ecran.keys():
                a = self.points_ecran.pointTraj(key)
                b = self.points_ecran.pointVid(key)
                if key[0] > self.index_de_l_image-1:
                        b.hide()
                        a.hide()
                elif key[0]<self.index_de_l_image:
                        a.show()
                        b.show()

        self.affiche_image()

    def affiche_image(self):
        self.extract_image(self.filename, self.index_de_l_image)
        image=QImage(self.chemin_image)
        self.image_640_480 = image.scaled(640,480,Qt.KeepAspectRatio)
        self.label_video.setMouseTracking(True)
        self.ui.label.setPixmap(QPixmap.fromImage(self.image_640_480))
        self.label_video.met_a_jour_crop()
        self.label_video.update()
        self.label_video.show()
        self.ui.horizontalSlider.setValue(self.index_de_l_image)
        self.ui.spinBox_image.setValue(self.index_de_l_image)
        
    def recommence_echelle(self):
        self.echelle_image=echelle()
        self.affiche_echelle()
        self.job.dialog.close()
        self.job.close()
        self.demande_echelle()
        
    def affiche_image_slider(self):
        self.index_de_l_image = self.ui.horizontalSlider.value()
        self.affiche_image()

    def demande_echelle(self):
        
        echelle_result_raw = QInputDialog.getText(None, self.tr("Définir une échelle"), self.tr("Quelle est la longueur en mètre de votre étalon sur l'image ?")
,QLineEdit.Normal, QString("1.0"))
        if echelle_result_raw[1] == False :
            return None
        try :
            echelle_result = [float(echelle_result_raw[0].replace(",",".")), echelle_result_raw[1]]

            if echelle_result[0] <= 0 or echelle_result[1] == False :
                self.mets_a_jour_label_infos(self.tr(" Merci d'indiquer une échelle valable"))
            else :
                self.echelle_image.longueur_reelle_etalon=float(echelle_result[0])
                self.job = Label_Echelle(self.ui.label,self)
                self.job.setPixmap(QPixmap(self.chemin_image))
                self.job.show()
        except ValueError :
            self.mets_a_jour_label_infos(self.tr(" Merci d'indiquer une échelle valable"))
            self.demande_echelle()

    def feedbackEchelle(self, p1, p2):
        """
        affiche une trace au-dessus du self.job, qui reflète les positions
        retenues pour l'échelle
        """
        from echelle import Label_Echelle_Trace
        self.label_echelle_trace = Label_Echelle_Trace(self.ui.label, p1,p2)
        self.label_echelle_trace.show()
        
    def reinitialise_environnement(self):
        os.chdir(self._dir("images"))
        for filename in glob("*.jpg"):  # a remettre à la fin ;) 
                os.remove(filename)
        
    def closeEvent(self,event):
        if self.verifie_donnees_sauvegardees() :
            self.reinitialise_environnement()
        else :
            event.ignore()

    def verifie_donnees_sauvegardees(self):
        if self.modifie:
            retour = QMessageBox.warning(self,QString(self.tr("Les données seront perdues")),QString(self.tr("Votre travail n'a pas été sauvegardé\nVoulez-vous les sauvegarder ?")),QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel )
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
            self.mets_a_jour_label_infos(self.tr("Vous avez atteint le début de la vidéo"))
            self.affiche_image()
    
    def mets_a_jour_label_infos(self, message):
        self.ui.label_infos_image.setText(message)

    def openexample(self):
        dir="%s/video" %(self._dir("share"))
        self.reinitialise_tout()
        filename=QFileDialog.getOpenFileName(self,self.tr("Ouvrir une vidéo"), dir,"*.avi")
        self.openTheFile(filename)
        
    def openfile(self):
        dir=self._dir("cwd")
        filename=QFileDialog.getOpenFileName(self,self.tr("Ouvrir une vidéo"), dir,"*.avi")
        self.openTheFile(filename)

    def renomme_le_fichier(self):
        renomme_fichier = QMessageBox.warning(self,self.tr("Nom de fichier non conforme"),QString(self.tr("Le nom de votre fichier contient des caractères accentués ou des espaces.\n Merci de bien vouloir le renommer avant de continuer")), QMessageBox.Ok,QMessageBox.Ok)
        filename=QFileDialog.getOpenFileName(self,self.tr("Ouvrir une vidéo"), self._dir("cwd"),"*.avi")
        self.openTheFile(filename)
    def openTheFile(self,filename):
        if filename != "" : 
            try :
                str(filename)
            except UnicodeEncodeError :
                self.renomme_le_fichier()
            if len(filename.split(" ")) > 2 :
                self.renomme_le_fichier()
            else :
                self.filename=str(filename)
                self.prefs.lastVideo=filename
                self.prefs.videoDir=os.path.dirname(unicode(filename))
                self.prefs.save()
                self.init_image()
                self.mets_a_jour_label_infos(self.tr("Veuillez choisir une image et définir l'échelle"))
                self.ui.Bouton_Echelle.setEnabled(True)
                self.ui.horizontalSlider.setEnabled(1)
                self.label_video.show()

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
            QMessageBox.warning(None,"Aide",QString(self.tr("Désolé pas de fichier d'aide pour ce langage %s.") %lang))
        
    def init_image(self):
        """intialise certaines variables lors le la mise en place d'une nouvelle image"""
        self.index_de_l_image = 1
        self.trajectoire = {}
        self.ui.spinBox_image.setMinimum(1)
        self.defini_barre_avancement()
        self.echelle_image=echelle()
        self.affiche_echelle()
        self.ui.tab_traj.setEnabled(0)
        self.ui.spinBox_image.setEnabled(1)
        self.a_une_image = True
        self.reinitialise_environnement() 
        self.affiche_image()
        
            
    def defini_barre_avancement(self):
        """récupère le maximum d'images de la vidéo et défini la spinbox et le slider"""
        
        framerate, self.image_max = self.recupere_avi_infos(self.filename)
        self.deltaT = float(1.0/framerate)
        self.ui.horizontalSlider.setMinimum(0)
        
        self.ui.horizontalSlider.setMaximum(int(self.image_max))
        self.ui.spinBox_image.setMaximum(int(self.image_max))
        
        os.chdir(self._dir("images"))
        try :
              os.remove("video_000001.jpg")
              a = self.extract_image(self.filename, 1)
              os.chdir(self._dir("images"))
              os.remove("video_000001.jpg")
        except OSError:
              pass
    def extract_image(self, video, index):
        """
        extrait l'image d'index "index" de la video à l'aide de ffmpeg
        et l'enregistre sur le disque
        """
        os.chdir(self._dir("images"))
        output = ""

        imfilename="video_%06d.jpg" % index
        if os.path.isfile(imfilename): #si elle existe déjà et , ne fait rien
            self.chemin_image = imfilename
        else : #sinon, extrait depuis la video
            #attention au cas de la dernière image.
            cmd0="ffmpeg -i %s -ss %f -vframes 1 -f image2 -vcodec mjpeg %s"
            i=1
            imfilename=imfilename.replace(" ","\ ")
	    cmd= cmd0 %(video,(index-i)*self.deltaT,imfilename)
            
	    status, output = commands.getstatusoutput(cmd)
            if status==0:
                while not os.path.exists(imfilename) and i<index:
                    i+=1
                    imfilename="video_%06d.jpg" %(index-i+1)
                    cmd= cmd0 %(video,(index-i)*self.deltaT,imfilename)
                    status, output = commands.getstatusoutput(cmd)
                self.chemin_image = imfilename
	    elif status<32512:
		    mauvaisevideo = QMessageBox.warning(self,self.tr("La video que vous tentez d'ouvrir n'est pas dans un format lisible, ou FFMPEG est mal installé"), QString(self.tr(" Merci d'en ouvrir une autre ou de l'encoder autrement")), QMessageBox.Ok,QMessageBox.Ok)
            elif status ==32512 :
                pas_ffmpeg = QMessageBox.warning(self,self.tr("FFmpeg n'est pas présent"),QString(self.tr("le logiciel ffmpeg n'a pas été trouvé sur votre système. Merci de bien vouloir l'installer avant de poursuivre")), QMessageBox.Ok,QMessageBox.Ok)
                self.close()
    def recupere_avi_infos(self, fileName):
        "Ouvre une vidéo AVI et retourne son framerate ainsi que le nombre d'images de la vidéo."
        framerate = 0
        try:
            fsock = open(fileName, "rb", 0)
            fsock.seek(128)
            echelle = self.construit_entier(fsock.read(4))
            taux = self.construit_entier(fsock.read(4))
            framerate = taux/echelle
            pouet = self.construit_entier(fsock.read(4)) #avance de 4
            nb_images = self.construit_entier(fsock.read(4))
            fsock.close()
        except IOError:
            self.dbg.p(0, self.tr("Impossible de lire %s") %fileName)

        return framerate,nb_images

    def construit_entier(self,bytes):
        if len(bytes) != 4:
            return -1
        else:
            return ord(bytes[0]) | ord(bytes[1]) << 8  | \
                    ord(bytes[2]) << 16 | ord(bytes[3]) << 24
        
    def traiteOptions(self):
        for opt,val in self.opts:
            if opt in ['-f','--fichier_mecavideo']:
                self.rouvre(val)
        
def usage():
    print self.tr("Usage : pymecavideo [-f fichier | --fichier_pymecavideo=fichier]")

def run():
    app = QApplication(sys.argv)
    
    args=sys.argv[1:]
    try:                                
        opts, args = getopt.getopt(args, "f:", ["fichier_mecavideo="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    filename=""
    if len(args)>0:
        filename=args[-1]# passe le dernier paramètre
        locale = QLocale.system().name()

    # ainsi pickle peut trouver le module "vecteur"

    ###translation##
    locale = QLocale.system().name()
    #locale = QString("en_EN")
    
    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale):
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    
    home = os.getenv("HOME")
    pymecavideo_rep=home+"/.pymecavideo"
    pymecavideo_rep_images=pymecavideo_rep + "/images_extraites"
    pymecavideo_rep_icones=pymecavideo_rep + "/icones"
    pymecavideo_rep_langues=pymecavideo_rep + "/lang"

    pymecavideo_rep_install= os.path.dirname(os.path.abspath(__file__))
    os.chdir(home)
    if os.path.exists(pymecavideo_rep):
        pass
    else:
        os.mkdir(pymecavideo_rep)
        os.mkdir(pymecavideo_rep_images)
        os.mkdir(pymecavideo_rep_icones)
        os.mkdir(pymecavideo_rep_langues)
        copy_commands='cp -R '+pymecavideo_rep_install+'/icones/* '+pymecavideo_rep_icones
        
        status,output=commands.getstatusoutput(copy_commands)
        copy_commands_lang='cp -R '+pymecavideo_rep_install+'/lang/* '+pymecavideo_rep_langues
        status,output=commands.getstatusoutput(copy_commands_lang)
        
    if appTranslator.load(pymecavideo_rep_langues+"/pymecavideo_" + locale):
        b = app.installTranslator(appTranslator)
        
    windows = StartQT4(None,os.path.abspath(filename),opts)

    windows.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
