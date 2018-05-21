#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

"""
    dicopoint, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2010 Jean-Baptiste Butet <ashashiwa@gmail.com>
    Copyright (C) 2007-2018 Georges Khaznadar <georgesk.debian.org>

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

from vecteur import vecteur


class Point(vecteur):
    """
    Une classe qui implémente un point repéré sur une image de vidéo
    """
    # une suite de constantes pour les genres de points
    inconnu = 0
    userClick = 1
    openCv = 2
    # et les explications texte qui vont avec
    genres = ["nul", "saisi", "auto"]

    def __init__(self, x=0, y=0, genre=None):
        """
        Le constructeur
        @param x abscisse
        @param y ordonnée
        @param genre indique la façon dont le point a été déterminé
        """
        vecteur.__init__(self, x, y)
        if genre == None:
            self.genre = Point.inconnu
        else:
            self.genre = genre

    def __str__(self):
        return "videoPoint<" + vecteur.__str__(self) + "," + Point.genres[self.genre] + ">"


class Points:
    """
    Une classe pour géréer un dictionnaire de points.
    ses principales propriétés sont :
    """

    def __init__(self, nbTrames, nbObj=1):
        """
        Le constructeur
        @param nbTrames le nombre de trames du film où on suit les points
        @param nbObj le nombre d'ojets qu'on suivra (par défaut : 1)
        """
        self.nbTrames = nbTrames
        self.nbObj = nbObj
        self.data = []
        for obj in range(nbObj):
            self.data.append([])

    def __setitem__(self, cle, point):
        """
        affecte un point dans le dictionnaire
        @param cle une paire (trame,index) ; trame est la trame dans la vidéo, index est l'index parmi la séquence d'objets suivis. Si cle est juste un entier on considère que c'est la trame et que l'index est nul
        @param point le point
        @return un point qui est "null" s'il n'existait pas avant.
        """
        if type(cle) == type(0):
            trame = cle;
            index = 0
        else:
            trame, index = cle
        if index < self.nbObj:
            liste = self.data[index]
            l = len(liste)
            for i in range(l, trame + 1):
                """ remplit les cases vides s'il y en a."""
                liste.append(None)
            liste[trame] = point
        else:
            raise IndexError("trop de points suivis")

    def __getitem__(self, cle):
        """
        Renvoie un point du dictionnaire
        @param cle une paire (trame,index) ; trame est la trame dans la vidéo, index est l'index parmi la séquence d'objets suivis. Si cle est juste un entier on considère que c'est la trame et que l'index est nul
        @return le point du dictionnaire correspondant au doublet trame, index
        @return une erreur si on demande un point après la vidéo
        @return une erreur si on demande un objet qui n'existe pas
        @return une erreur si on demande un point sans préciser l'objet alors qu'il y a en a plusieurs.
        """
        if type(cle) == type(0):
            trame = cle;
            index = 0
            if index != self.nbObj:
                raise IndexError("numéro d'objet non précisé")
        else:
            trame, index = cle
        if index < self.nbObj:
            liste = self.data[index]
            l = len(liste)
            if trame < l and liste[trame] != None:
                return liste[trame]
            else:
                if trame >= self.nbTrames:
                    raise IndexError("point après la fin de la vidéo")
                else:
                    return Point()  # un point de genre inconnu par défaut.
        else:
            raise IndexError("trop de points suivis")

    def __str__(self):
        result = "\ndicoPoints\n"
        for i in range(self.nbTrames):
            result += "  Trame %d :" % i
            for j in range(self.nbObj):
                result += "%s " % (self.__getitem__((i, j)))
            result += "\n"
        return result

    def voisins(self, trame, index=-1):
        """Retourne les points voisins du point demandé, identifié par la trame et le numéro de l'objet suivi.
        @param trame : numero de l'image, index : index de l'objet suivi
        @param peut etre un tuple de coordonnées. A ce moment là on retourne les voisins du vecteur.
        @return Retourne le point précédent puis le point suivant.
        @return None si pas de point suivant ou précédent"""
        vect = (0, 0)
        if type(trame) == type(vect):  # on a à faire à un vecteur
            #cherche le vecteur dans tous les points du dictionnaire
            liste = []
            vecteur = trame
            for index in range(self.nbObj):
                for trame in range(self.nbTrames):
                    if vecteur == (self.__getitem__((trame, index))[0], self.__getitem__((trame, index))[1]):
                        liste.append((vecteur, trame, index))
            if len(liste) >= 1:
                liste_point = []
                for i in range(len(liste)):
                    liste_point.append(self.voisins(liste[0][1], liste[0][2]))
                return liste_point
            else:
                raise NameError("vecteur non trouvé")
        else:
            if index == -1 and 0 != self.nbObj:
                raise IndexError("numéro d'objet non précisé")
            elif index == -1:
                index = 0
            if trame == self.nbTrames - 1:  # fin de série
                pt_apres = None
            else:
                pt_apres = self.__getitem__((trame + 1, index))
            if trame == 0:
                pt_avant = None
            else:
                pt_avant = self.__getitem__((trame - 1, index))
            return pt_avant, pt_apres


if __name__ == "__main__":
    print ("coucou")
    pts = Points(8, 2)  # 8 trames vidéo, deux points suivis
    try:
        p = Point(10, 20, Point.userClick)
        p2 = Point(2, 2, Point.userClick)
        p3 = Point(3, 3, Point.userClick)
        p4 = Point(4, 4, Point.userClick)
        pts[2, 1] = p2
        pts[3, 1] = p3
        pts[4, 1] = p4
        pts[5] = p
        p = Point(30, 40, Point.openCv)
        pts[6, 1] = p
        pts[7, 1] = p
        print ("pts[6,1]", pts[6, 1])
        print ("pts[7,1]", pts[7, 1])
        print ("voisins du dernier, le point 7, objet 0", pts.voisins(7, 0))
        print ("voisins du dernier, le point 7, objet 1", pts.voisins(7, 1))
        print ("voisins du premier, le point 0", pts.voisins(0, 1))
        print ("voisins du point 5, objet 0", pts.voisins(5, 0))
        print ("voisins du point 5, objet 1", pts.voisins(5, 1))
        print ("appel d'un tuple (3,3), retourne les voisins", pts.voisins((3, 3)))
        print ("pts[15,1]", pts[15, 1])


    except IndexError as err:
        print ("erreur d'index :", err.message)
    try:
        print ("pts[5]", pts[5])
    except IndexError as err:
        print ("erreur d'index :", err.message)
    print (pts)
        
