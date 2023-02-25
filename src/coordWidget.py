# -*- coding: utf-8 -*-

"""
    coordWidget, a module for pymecavideo:
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
    QTableWidgetSelectionRange, QPushButton

import os, time, re, sys
import locale

from version import Version
from vecteur import vecteur
from image_widget import ImageWidget
from globdef import cible_icon, DOCUMENT_PATH, inhibe, pattern_float
from toQimage import toQImage
from suivi_auto import SelRectWidget
from detect import filter_picture
from cadreur import Cadreur, openCvReader
from export import Export, EXPORT_FORMATS
from dbg import Dbg

import interfaces.icon_rc

from interfaces.Ui_coordWidget import Ui_coordWidget
from etatsCoord import Etats

class CoordWidget(QWidget, Ui_coordWidget, Etats):
    """
    Widget principal de l'onglet coordonnées

    paramètres du constructeur :
    @param parent l'onglet des coordonnées
    """
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        Ui_coordWidget.__init__(self)
        Etats.__init__(self)
        self.setupUi(self)
        # remplit l'exportCombo
        self.exportCombo.addItem('Exporter vers...')
        # Ajoute les différents formats d'exportation
        for key in sorted(EXPORT_FORMATS.keys()):
            self.exportCombo.addItem(EXPORT_FORMATS[key]['nom'])
        self.connecte_ui()
        self.masse_objet = 0   # masse du premier objet suivi ???? à déboguer
        return

    def setApp(self, app):
        """
        Crée des liens avec la fenêtre principale, le débogueur,
        le wigdet de pointage
        @param app la fenêtre principale
        """
        self.app = app
        self.dbg = app.dbg
        self.pointage = app.pointage
        return
        
    def connecte_ui(self):
        """
        Connecte les signaux des sous-widgets
        """
        self.exportCombo.currentIndexChanged.connect(self.export)
        self.pushButton_nvl_echelle.clicked.connect(self.recommence_echelle)
        self.checkBox_Ec.stateChanged.connect(self.affiche_tableau)
        self.checkBox_Epp.stateChanged.connect(self.affiche_tableau)
        self.checkBox_Em.stateChanged.connect(self.affiche_tableau)
        self.pushButton_select_all_table.clicked.connect(self.presse_papier)
        return
    
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

    def recommence_echelle(self):
        self.app.new_echelle.emit()
        return
    
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

        for i, t, iter_OPV in self.pointage.gen_iter_TOPV():
            self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{t:.3f}"))
            for j, obj, p, v in iter_OPV:
                if self.pointage.echelle_image:
                    # on convertit les pixels et px/x en mètre et m/s
                    p = self.pointage.pointEnMetre(p)
                    v = self.pointage.pointEnMetre(v)
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
        # copie en format TSV vers le presse-papier
        # merci à tyrtamos : voir https://www.developpez.net/forums/d1502290/autres-langages/python/gui/pyqt/rendre-copiable-qtablewidget/
        # emplacement sélectionné pour copier dans le clipboard
        selected = self.tableWidget.selectedRanges()
        # construction du texte à copier, ligne par ligne et colonne par colonne
        texte = ""
        for i in range(selected[0].topRow(), selected[0].bottomRow() + 1):
            for j in range(selected[0].leftColumn(), selected[0].rightColumn() + 1):
                try:
                    texte += self.tableWidget.item(i, j).text() + "\t"
                except AttributeError:
                    # quand une case n'a jamais été initialisée
                    texte += "\t"
            texte = texte[:-1] + "\n"  # le [:-1] élimine le '\t' en trop
        # enregistrement dans le clipboard
        QApplication.clipboard().setText(texte)
        return

    def cree_tableau(self, nb_suivis=1):
        """
        Crée un tableau de coordonnées neuf dans l'onglet idoine.
        @param nb_suivis le nombre d'objets suivis (1 par défaut)
        """
        self.dbg.p(2, "rentre dans 'cree_tableau'")
        self.tableWidget.clear()
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

        for i, t, iter_OP in self.pointage.gen_iter_TOP():
            self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{t:.3f}"))
            for j, obj, p in iter_OP:
                if p:
                    self.tableWidget.setItem(
                        i, j*(nb_suivis)+1, QTableWidgetItem(str(p.x)))
                    self.tableWidget.setItem(
                        i, j*(nb_suivis) + 2, QTableWidgetItem(str(p.y)))
        return

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

