#-*- coding: utf-8 -*-

licence="""
    pymecavideo : a program to track moving points in a video frameset
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>

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

licence_fr=u"""
    pymecavideo : un programme pour tracer les trajectoires des points dans une vidéo.
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
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
from cadreur import Cadreur
from preferences import Preferences
from dbg import Dbg

class StartQT4(QMainWindow):
    def __init__(self, parent, filename, opts):
        #Données principales du logiciel : 
        #self.index_de_l_image : la position de l'image actuellement affichée
        #self.index_de_l_image_du_pointk : le nombre de click fait sur l'image. ceci signifie donc que c'est le nombre de lignes dans le tableau. démarre à zéro
        
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
        
        #création du label qui contiendra la vidéo.
        self.label_video = Label_Video(parent=self.ui.label, app=self)

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
        self.dbg=Dbg(0)
        self.deltaT = 0.04       #durée 40 ms par défaut : 25 images/s
        self.lance_capture = False
        self.modifie=False
        self.points={}        #dictionnaire des points cliqués, par n° d'image.
        self.trajectoire = {} #dictionnaire des points des trajectoires
        self.pX={}            #points apparaissant à l'écran, indexés par X
        self.pY={}            #points apparaissant à l'écran, indexés par Y
        self.index_du_point = 0
        self.echelle_image = echelle() # objet gérant l'image
        self.nb_image_deja_analysees = 0 #indique le nombre d'images dont on a dejà fait l'étude, ce qui correspond aussi au nombre de lignes dans le tableau.
        self.couleurs=["red", "blue", "cyan", "magenta", "yellow", "gray", "green"] #correspond aux couleurs des points del a trajectoire
        self.nb_de_points = 1        # nombre de points suivis
        self.encore_a_cliquer = -1   # combien de points encore à cliquer
        self.premiere_image = 1      # n° de la première image cliquée
        self.prefs=Preferences(self)
        self.echelle_v = 1
        self.filename=filename
        self.opts=opts
        self.init_interface()
        
    def init_interface(self):
        self.label_trajectoire=Label_Trajectoire(self.ui.tab_traj, self)
        self.ui.Bouton_Echelle.setEnabled(0)
        self.ui.horizontalSlider.setEnabled(0)
        self.ui.echelleEdit.setEnabled(0)
        self.ui.echelleEdit.setText(u"indéf.")
        self.ui.tab_traj.setEnabled(0)
        self.ui.actionSaveData.setEnabled(0)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(0)
        self.ui.spinBox_image.setEnabled(0)
        self.ui.Bouton_lance_capture.setEnabled(0)
        self.ui.spinBox_nb_de_points.setEnabled(0)
        self.ui.spinBox_nb_de_points.setValue(1)
        self.ui.button_video.setEnabled(0)
        self.ui.echelle_v.setDuplicatesEnabled(False)
        self.setEchelle_v()

    def reinitialise_tout(self):
        self.montre_vitesses(False)
        self.oubliePoints()
        self.label_trajectoire.update()
        self.init_variables(self.filename,None)
        self.init_interface()
        
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
        QObject.connect(self.ui.Bouton_Echelle,SIGNAL("clicked()"), self.echelle)
        QObject.connect(self.ui.horizontalSlider,SIGNAL("valueChanged(int)"), self.affiche_image_slider)
        QObject.connect(self.ui.spinBox_image,SIGNAL("valueChanged(int)"),self.affiche_image_spinbox)
        QObject.connect(self.ui.Bouton_lance_capture,SIGNAL("clicked()"),self.debut_capture)
        QObject.connect(self,SIGNAL("clic_sur_video()"),self.clic_sur_label_video)
        QObject.connect(self.ui.comboBox_referentiel,SIGNAL("currentIndexChanged (int)"),self.tracer_trajectoires)
        QObject.connect(self.ui.tabWidget,SIGNAL("currentChanged (int)"),self.tracer_trajectoires)
        QObject.connect(self.ui.echelle_v,SIGNAL("currentIndexChanged (int)"),self.refait_vitesses)
        QObject.connect(self.ui.echelle_v,SIGNAL("editTextChanged (int)"),self.refait_vitesses)
        QObject.connect(self.ui.button_video,SIGNAL("clicked()"),self.video)

    def presse_papier(self):
      
      table = ""
      liste_des_cles = []
      sep_decimal="."
      if locale.getdefaultlocale()[0][0:2]=='fr':
            # en France, le séparateur décimal est la virgule
            sep_decimal=","
      for key in self.points:
          liste_des_cles.append(key)
          liste_des_cles.sort()
          for cle in liste_des_cles:
              donnee=self.points[cle]
              t=float(donnee[0])
              a = ("%.2f\t" %t).replace(".", sep_decimal)


              for p in donnee[1:]:
                  a+= ("%5f\t"
%(float(p.x())*self.echelle_image.mParPx())).replace(".", sep_decimal)
                  a+= ("%5f\t"
%(float(480-p.y())*self.echelle_image.mParPx())).replace(".", sep_decimal)

              a+="\n"
          table = table + a
      print table
      self.clipboard = QApplication.clipboard()

      self.clipboard.setText(table)

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

        if   lequel == "home": return home
        elif lequel == "cwd": return self.cwd
        elif lequel == "ressources": return pymecavideo_rep
        elif lequel == "images": return pymecavideo_rep_images
        elif lequel == "icones": return pymecavideo_rep_icones
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
            os.chdir(home)
            if os.path.exists(pymecavideo_rep):
                pass
            else:
                os.mkdir(pymecavideo_rep)
                os.mkdir(pymecavideo_rep_images)
                os.mkdir(pymecavideo_rep_icones)
                copy_commands='cp -R '+pymecavideo_rep_install+'/icones/* '+pymecavideo_rep_icones
                status,output=commands.getstatusoutput(copy_commands)
            os.chdir(self.cwd)

    def rouvre_ui(self):
        os.chdir(self._dir("home"))
        fichier = QFileDialog.getOpenFileName(self,"FileDialog", "","*.mecavideo")
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
        self.dbg.p(2,"chemin vers les modules : %s" %sys.path)
        self.loads(dd)
        self.openTheFile(self.filename)
        epxParM=self.echelle_image.longueur_pixel_etalon/self.echelle_image.longueur_reelle_etalon
        self.ui.echelleEdit.setText("%.1f" %epxParM)
        n=len(self.points.keys())
        self.nb_image_deja_analysees = n
        self.ui.horizontalSlider.setValue(n+self.premiere_image)
        self.ui.spinBox_image.setValue(n+self.premiere_image)
        self.ui.spinBox_nb_de_points.setValue(self.nb_de_points)
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
        if locale.getdefaultlocale()[0][0:2]=='fr':
            # en France, le séparateur décimal est la virgule
            sep_decimal=","
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
                file.write(self.entete_fichier(u"temps en seconde, positions en mètre"))
                for cle in liste_des_cles:
                    donnee=self.points[cle]
                    t=float(donnee[0])
                    a = ("\n%.2f\t" %t).replace(".", sep_decimal)
                    for p in donnee[1:]:
                        a+= ("%5f\t" %(float(p.x())*self.echelle_image.mParPx())).replace(".", sep_decimal)
                        a+= ("%5f\t" %(float(480-p.y())*self.echelle_image.mParPx())).replace(".", sep_decimal)
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
        self.nb_de_points = self.ui.spinBox_nb_de_points.value()
        self.ui.spinBox_nb_de_points.setEnabled(0)
        self.ui.Bouton_lance_capture.setEnabled(0)
        self.ui.horizontalSlider.setEnabled(0)
        self.premiere_image=self.ui.horizontalSlider.value()
        self.encore_a_cliquer = self.nb_de_points
        self.affiche_point_attendu(1)
        self.lance_capture = True
        self.label_video.setCursor(Qt.CrossCursor)
        self.ui.tab_traj.setEnabled(1)
        self.ui.actionSaveData.setEnabled(1)
        self.ui.actionCopier_dans_le_presse_papier.setEnabled(1)
        self.ui.comboBox_referentiel.setEnabled(1)
        
        self.label_trajectoire = Label_Trajectoire(self.ui.tab_traj,self)
        
        self.ui.comboBox_referentiel.insertItem(-1, "camera")
        for i in range(self.nb_de_points) :
            self.ui.comboBox_referentiel.insertItem(-1, str(i+1))


        #met en place le tableau des coordonnées
        from table import standardDragTable
        self.table_widget=standardDragTable(self.ui.tab_coord)
        self.ui.tab_coord.setEnabled(1)
        self.table_widget.setRowCount(1)
        self.table_widget.setColumnCount(self.nb_de_points*2 + 1)
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

    def retientPoint(self,n,ref,i,p,point):
        """
        mémorise un point visible à l'écran, dans plusieurs dictionnaires
        """
        self.trajectoire["point-%s_%s-%s" %(n,ref,i)] = [p, point]
        x=p.x(); y=p.y()
        if x in self.pX.keys():
            self.pX[x].append(point)
        else:
            self.pX[x]=[point]
        if y in self.pY.keys():
            self.pY[y].append(point)
        else:
            self.pY[y]=[point]

    def oubliePoints(self):
        """
        vide la mémoire des points visibles à l'écran
        """
        self.pX={}
        self.pY={}
        for index in self.trajectoire.keys():
            if index[:6]=="point-":
                [p,point] = self.trajectoire[index]
                point.hide()
                del point
                del p
        self.trajectoire={}

    def video(self):
        ralenti=[1,2,4,8][self.ui.comboBox_fps.currentIndex()]
        ref=self.ui.comboBox_referentiel.currentText()
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
        self.ui.label_3.setEnabled(1)

        self.oubliePoints()
        if newValue=="absolu":
            ref="camera"
        else:
            ref = self.ui.comboBox_referentiel.currentText()
        if len(ref)==0 : return
        if ref != "camera":
            bc=self.mediane_trajectoires(int(ref)-1)
            origine=vecteur(320,240)-bc
            self.ui.button_video.setEnabled(1)
        else:
            # pas de vidéo si ref == "camera"
            self.ui.button_video.setEnabled(0)
        for n in range(self.nb_de_points):
            couleur = self.couleurs[n]
            ancienPoint=None #ancienPoint sert à chaîner les points consécutifs
            for i in self.points.keys():
                if ref == "camera":
                    p = self.points[i][1+n]
                else:
                    ref=int(ref)
                    p = self.points[i][1+n]-self.points[i][ref]+origine
                if ref != "camera" and n == ref-1:
                    # on a affaire au tracé du repère du référentiel :
                    # une seule instance suffira, vu qu'il ne bouge pas.
                    if newValue!="absolu":
                        if i == self.points.keys()[0]:
                            point = Repere(self.label_trajectoire, p, couleur, 0, self)
                            point.show()
                            self.retientPoint(n,ref,i,p,point)
                else:
                    if newValue!="absolu":
                        point = Point(self.label_trajectoire, p, couleur, i+1, self,ancienPoint) # le point est chaîné au précédent s'il existe.
                        ancienPoint=point
                        point.show()
                        self.retientPoint(n,ref,i,p,point)
                    else: #newValue=="absolu"
                        point = Point(self.label_video, p, couleur, i+1, self,ancienPoint) # le point est chaîné au précédent s'il existe.
                        ancienPoint=point
                        point.show()
                        self.retientPoint(n,ref,i,p,point)
        #self.label_trajectoire.update()
        
    def affiche_point_attendu(self,n):
        """
        Renseigne sur le numéro du point attendu
        """
        self.mets_a_jour_label_infos(u"Cliquer sur le point N°%d" %n)

    def clic_sur_label_video(self):
        self.encore_a_cliquer -= 1
        if self.encore_a_cliquer > 0 :
            self.affiche_point_attendu(1+self.nb_de_points-self.encore_a_cliquer)
        elif self.encore_a_cliquer == 0:
            self.encore_a_cliquer = self.nb_de_points
            self.affiche_point_attendu(1)
            self.stock_coordonnees_image(self.nb_image_deja_analysees,self.label_video.liste_points)
            self.nb_image_deja_analysees += 1
            self.label_video.liste_points=[]
            self.index_de_l_image += 1
            self.affiche_image()
            self.tracer_trajectoires("absolu")
            
    def stock_coordonnees_image(self, ligne, liste_points):
        """ """
        t = ligne*self.deltaT
        liste_points.insert(0,"%4f" % t)
        self.points[ligne]=liste_points
        print liste_points, ligne

        #rentre le temps dans la première colonne
        self.table_widget.setItem(ligne,0,QTableWidgetItem(liste_points[0]))
        i=1
        #Pour chaque point dans liste_points, insère les vlauer dans la ligne
        for point in liste_points[1:] :
            print  ligne,2*i-1,int(point.x()), ligne,2*i,int(point.y())
            self.table_widget.insertRow(ligne)
            
            self.table_widget.setItem(ligne,2*i-1,QTableWidgetItem(int(point.x())))
            self.table_widget.setItem(ligne,2*i,QTableWidgetItem(int(point.y())))
            i+=1
        self.table_widget.show()
    def transforme_index_en_temps(self, index):
        return float(self.deltaT*(index))
    
    def affiche_image_spinbox(self):
        self.index_de_l_image = self.ui.spinBox_image.value()
        self.affiche_image()
    
    def affiche_image(self):
        self.extract_image(self.filename, self.index_de_l_image)
        image=QImage(self.chemin_image)
        self.image_640_480 = image.scaled(640,480,Qt.KeepAspectRatio)
        self.label_video.setPixmap(QPixmap.fromImage(self.image_640_480))
        self.ui.horizontalSlider.setValue(self.index_de_l_image)
        self.ui.spinBox_image.setValue(self.index_de_l_image)
        
    def recommence_echelle(self):
        self.ui.Bouton_Echelle.setEnabled(1)
        self.ui.tab_acq.echelle_definie=False
        self.job.dialog.close()
        self.job.close()
        self.echelle()
        
    def affiche_image_slider(self):
        self.index_de_l_image = self.ui.horizontalSlider.value()
        self.affiche_image()

    def echelle(self):
        
        echelle_result = QInputDialog.getDouble(self, u"Définir une échelle", u"Quelle est la longueur en mètre de votre étalon sur l'image ?", 1, 0, 2147483647, 2)
        
        if echelle_result[0] <= 0 or echelle_result[1] == False :
            self.mets_a_jour_label_infos(u" Merci d'indiquer une échelle valable")
        else : 
            self.echelle_image.longueur_reelle_etalon=float(echelle_result[0])
            self.job = Label_Echelle(self.ui.tab_acq,self)
            self.job.setPixmap(QPixmap(self.chemin_image))
            self.job.show()
        
    def feedbackEchelle(self):
        """
        affiche une trace au-dessus du self.job, qui reflète les positions
        retenues pour l'échelle
        """
        # à implémenter
        return
    
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
            retour = QMessageBox.warning(self,QString(u"Les données seront perdues"),QString(u"Votre travail n'a pas été sauvegardé\nVoulez-vous les sauvegarder ?"),QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel )
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
            self.mets_a_jour_label_infos("Vous avez atteint le début de la vidéo")
            self.affiche_image()
    
    def mets_a_jour_label_infos(self, message):
        self.ui.label_infos_image.setText(message)
    
    def init_tableau(self, tableau, sorte="pixels", largeurCol=60):
        """mets à zéro le tableau passé en argument"""
        if sorte == "pixels":
            titres=["t (s)","x (px)","y (px)","x0 (px)","y0 (px)"]
        else:
            titres=["t (s)","x (m)","y (m)","x0 (m)","y0 (m)"]
        tableau.setRowCount(1)
        tableau.setColumnCount(5)
        tableau.clear()
        tableau.setColumnCount(5)
        tableau.setRowCount(1)
        #for i in range(5):
            #tableau.setColumnWidth(i,largeurCol)
            #headerItem = QTableWidgetItem()
            #headerItem.setText(QApplication.translate("pymecavideo", titres[i], None, QApplication.UnicodeUTF8))
            #tableau.setHorizontalHeaderItem(i,headerItem)

    def openexample(self):
        dir="%s/video" %(self._dir("share"))
        filename=QFileDialog.getOpenFileName(self,u"Ouvrir une vidéo", dir,"*.avi")
        self.reinitialise_tout()
        self.openTheFile(filename)
        
    def openfile(self):
        dir=self._dir("cwd")
        filename=QFileDialog.getOpenFileName(self,u"Ouvrir une vidéo", dir,"*.avi")
        self.reinitialise_tout()
        self.openTheFile(filename)
            
            
    def openTheFile(self,filename):
        if filename != "" : 
            self.filename=filename
            self.prefs.lastVideo=filename
            self.prefs.videoDir=os.path.dirname(str(filename))
            self.prefs.save()
            self.init_image()
            self.mets_a_jour_label_infos(u" Veuillez choisir une image et définir l'échelle")
            self.ui.horizontalSlider.setEnabled(1)
            self.label_video.show()

    def propos(self):
        QMessageBox.warning(None,"Licence",QString(licence_fr), QMessageBox.Ok,QMessageBox.Ok)
        
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
            QMessageBox.warning(None,"Aide",QString("Sorry, no help file for the language %s." %lang))
        
    def init_image(self):
        """intialise certaines variables lors le la mise en place d'une nouvelle image"""
        self.index_de_l_image = 1
        self.trajectoire = {}
        self.ui.spinBox_image.setMinimum(1)
        self.defini_barre_avancement()
        self.ui.Bouton_Echelle.setEnabled(1)
        self.ui.tab_traj.setEnabled(0)
        self.ui.spinBox_image.setEnabled(1)
        self.a_une_image = True
        self.reinitialise_environnement() 
        self.affiche_image()
        self.Bouton_lance_capture=False
        
            
    def defini_barre_avancement(self):
        """récupère le maximum d'images de la vidéo et défini la spinbox et le slider"""
        
        framerate, self.image_max = self.recupere_avi_infos(self.filename)
        self.deltaT = float(1.0/framerate)
        self.ui.horizontalSlider.setMinimum(0)
        
        self.ui.horizontalSlider.setMaximum(int(self.image_max))
        self.ui.spinBox_image.setMaximum(int(self.image_max))
        
        os.chdir(self._dir("images"))
        os.remove("video_000001.jpg")
        a = self.extract_image(self.filename, 1)
        os.chdir(self._dir("images"))
        os.remove("video_000001.jpg")

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
            cmd= cmd0 %(video,(index-i)*self.deltaT,imfilename)
            status, output = commands.getstatusoutput(cmd)
            while not os.path.exists(imfilename) and i<index:
                i+=1
                imfilename="video_%06d.jpg" %(index-i+1)
                cmd= cmd0 %(video,(index-i)*self.deltaT,imfilename)
                status, output = commands.getstatusoutput(cmd)
            self.chemin_image = imfilename
            
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
            self.dbg.p(0, "Impossible de lire %s" %fileName)

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
    print "Usage : pymecavideo [-f fichier | --fichier_pymecavideo=fichier]"

def run():
    app = QApplication(sys.argv)
    
    #translation
    #locale = QLocale.system().name()

    #qtTranslator = QTranslator()
    #if qtTranslator.load("qt_" + locale):
    #    app.installTranslator(qtTranslator)
    #appTranslator = QTranslator()
        
   # if appTranslator.load("lang/pyfocus_" + locale):
        #app.installTranslator(appTranslator)

    args=sys.argv[1:]
    try:                                
        opts, args = getopt.getopt(args, "f:", ["fichier_mecavideo="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    filename=""
    if len(args)>0:
        filename=args[-1]# passe le dernier paramètre

    # ainsi pickle peut trouver le module "vecteur"
    windows = StartQT4(None,os.path.abspath(filename),opts)
    windows.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
