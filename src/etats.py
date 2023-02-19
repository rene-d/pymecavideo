# -*- coding: utf-8 -*-

"""
    etats, a module for pymecavideo:
      a program to track moving points in a video frameset
      
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

from PyQt6.QtCore import QObject
import os

class Etats_Base(QObject):
    """
    Une classe qui permet de définir les états pour le pointageWidget
    debut, A, AB, B, C, D, E : voir le fichier etats_pymecavideo.html
    """

    def __init__(self):
        QObject.__init__(self)
        # la liste des états de Pymecavideo
        self.etats = "debut,A,AB,B,C,D,E".split(",")
        # dictionnaire etat => message pour la barre de statut
        self.roleEtat = self.definit_messages_statut()
        self.etat_ancien = None    # état précédent
        return

    def changeEtat(self, etat):
        """
        Mise en place d'un état de l'interface utilisateur, voir la
        documentation dans le fichier etat_pymecavideo.html

        Cette fonction est virtuelle elle doit être surchargée
        """
        raise(Exception, "Etats_Base.changeEtat est une fonction virtuelle, elle doit être surchargée.")
    
              
    def definit_messages_statut(self):
        """
        Définit les correspondances en état et message de barre de statut
        """
        # les fonction qui permettent d'avoir les débuts de messages de statut
        def msgDebut(app):
            return self.tr("Début : ouvrez un fichier, ou un exemple des aides")
        def msgA(app):
            if app.filename is None: return ""
            return self.tr("Fichier vidéo : {filename} ... définissez l'échelle ou démarrez le pointage | Il est possible de redimensionner la fenêtre").format(filename = os.path.basename(app.filename))
        def msgAB(app):
            return self.tr("Préparation du pointage automatique : sélectionnez les objets à suivre, au nombre de {n}").format(n = app.pointage.nb_obj)
        def msgB(app):
            return self.tr("Pointage automatique en cours : il peut être interrompu par le bouton STOP")
        def msgC(app):
            return self.tr("Définissez l'échelle, par un tirer-glisser sur l'image")
        def msgD(app):
            return self.tr("Pointage manuel : cliquez sur le premier objet à suivre")
        def msgE(app):
            return self.tr("Pointage manuel : il reste encore des objets à pointer, on en est à {obj}").format(obj = app.pointage.objet_courant)
        return { # résumé de ce que représente un état
            "debut" : msgDebut,
            "A" :     msgA,
            "AB" :    msgAB,
            "B" :     msgB,
            "C" :     msgC,
            "D" :     msgD,
            "E" :     msgE,
        }
    
