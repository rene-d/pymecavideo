"""
    export.py is a module of pymecavideo.
    pymecavideo is a program to track moving points in a video frameset
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

"""
export.py permet d'exporter les données de pymecavideo dans différents formats
"""


from dbg import Dbg
from globdef import DOCUMENT_PATH
from PyQt6.QtWidgets import QFileDialog, QCheckBox, QDialog, QMessageBox, QDialogButtonBox, QVBoxLayout, QGroupBox, QHBoxLayout, QRadioButton, QSpacerItem, QSizePolicy, QGridLayout
from PyQt6.QtCore import Qt, QCoreApplication, QSize, QUrl, QStandardPaths
import sys
import os, time
DBG = Dbg(0)

_translate = QCoreApplication.translate

# On prévient si l'enregistrement est un succès ?
INFO_OK = False

# Dictionnaire contenant les différents formats d'exportation
# nom (str) : nom du format/de l'application
# filtre (str) : filtre utilisé dans le dialogue d'enregistrement
# extension (str)  : extension du fichier, ajoutée automatiquement si besoin
# class (str) : classe appelée pour générer et enregistrer le fichier
# propose_ouverture (bool) : propose ou pas l'ouverture du ficher dans le dialogue d'enregistrement
# modules (list of str) : liste des modules non standards nécessaires ou None
# un_point (bool) : nécessite un seul point cliqué ou pas
EXPORT_FORMATS = {
    1: {'nom': _translate("export", 'Libre/OpenOffice Calc'),
        'filtre': _translate("export", 'Feuille de calcul OpenDocument (*.ods)'),
        'extension': 'ods',
        'class': 'Calc',
        'modules': ['odf'],
        'propose_ouverture': True,
        'un_point': False},

    2: {'nom': _translate("export", 'Python (source)'),
        'filtre': _translate("export", 'Fichier Python (*.py)'),
        'extension': 'py',
        'class': 'PythonSource',
        'modules': None,
        'propose_ouverture': True,
        'un_point': True},

    3: {'nom': _translate("export", 'Python (Numpy)'),
        'filtre': _translate("export", 'Fichier Numpy (*.npy)'),
        'extension': 'npy',
        'class': 'PythonNumpy',
        'modules': ['numpy'],
        'propose_ouverture': False,
        'un_point': True},
    
    4: {'nom' : _translate("export",'Jupyter Notebook'),
        'filtre' : _translate("export",'Notebook (*.ipynb)'),
        'extension' : 'ipynb',
        'class' : 'PythonNotebook',
        'modules' : ['nbformat'],
        'propose_ouverture' : False,
        'un_point' : True},
    
    5: {'nom': _translate("export", 'Fichier CSV'),
        'filtre': _translate("export", 'Fichier CSV (*.csv, *.txt)'),
        'extension': 'csv',
        'class': 'FichierCSV',
        'modules': None,
        'propose_ouverture': True,
        'un_point': False},

    6: {'nom': _translate("export", 'Pandas Dataframe'),
        'filtre': _translate("export", 'Dataframe (*.pkl)'),
        'extension': 'pkl',
        'class': 'DataframePandas',
        'modules': ['pandas'],
        'propose_ouverture': False,
        'un_point': False},

    7: {'nom': _translate("export", 'Qtiplot/Scidavis'),
        'filtre': _translate("export", 'Fichier Qtiplot (*.qti)'),
        'extension': 'qti',
        'class': 'Qtiplot',
        'modules': None,
        'propose_ouverture': True,
        'un_point': False},
}

# Dictionnaire contenant les textes des QMessageBox information, warning...
EXPORT_MESSAGES = {
    0: {'titre': _translate("export", "Erreur lors de l'exportation"),
        'texte': _translate("export", "Echec de l'enregistrement du fichier:<b>\n{0}</b>")},

    1: {'titre': _translate("export", "Impossible de créer le fichier"),
        'texte': _translate("export", "L'export n'est possible que pour 1 seul point cliqué.")},

    2: {'titre': _translate("export", "Exportation terminée"),
        'texte': _translate("export", "Fichier:\n<b>{0}</b>\nenregistré avec succès.")},

    3: {'titre': _translate("export", "Impossible de créer le fichier"),
        'texte': _translate("export", "Le module <b>{0}</b> n'est pas installé.")},
}


# CLASSES D'EXPORT DANS LES DIFFERENTS FORMATS
# En début de fichier pour qu'elles apparaissent dans globals()
# =============================================================

class DataframePandas:

    def __init__(self, app, filepath):
        """
        Crée un fichier Pandas et importe les données de pymecavideo
        """
        import pandas as pd
        self.DataFrame = pd.DataFrame
        table = app.tableWidget
        df = self.write_qtable_to_df(table)
        df.to_pickle(filepath)
        QMessageBox.information(
            None,
            _translate("export_pandas", "Fichier Pandas sauvegardé"),
            _translate(
            "export_pandas", """Pour ouvrir ce fichier depuis Python, taper :\n\nimport pandas as pd\ndf = pd.read_pickle("{}")""".format(os.path.basename(filepath))))

    def write_qtable_to_df(self, table):
        """
        https://stackoverflow.com/questions/37680981/how-can-i-retrieve-data-from-a-qtablewidget-to-dataframe
        """
        #col_count = table.columnCount()
        #modif pour gérer 'refaire le point'
        col_count = table.columnCount()-1
        row_count = table.rowCount()
        headers = [str(table.horizontalHeaderItem(i).text())
                   for i in range(col_count)]
        df_list = []
        for row in range(row_count):
            df_list2 = []
            for col in range(col_count):
                table_item = table.item(row, col)
                df_list2.append(
                    '' if table_item is None else float(table_item.text()))
            df_list.append(df_list2)
        df = self.DataFrame(df_list, columns=headers)
        return df


class FichierCSV:

    def __init__(self, app, filepath):
        """
        Crée un fichier CSV et exporte les données de pymecavideo
        """
        import csv
        d = CsvExportDialog(app)
        if d.exec_() == QDialog.Accepted:
            _decimal = d.decimal
            _field = d.field
            _header = d.checkBox.isChecked()
            tw = app.tableWidget
            with open(filepath, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=_field,
                                       quotechar='"', quoting=csv.QUOTE_MINIMAL)
                if _header:
                    header = [tw.horizontalHeaderItem(
                        col).text() for col in range(tw.columnCount()-1)]
                    csvwriter.writerow(header)
                for row in range(tw.rowCount()):
                    rowdata = []
                    #for col in range(tw.columnCount()-1):
                    #modif pour gérer 'refaire le point'
                    for col in range(tw.columnCount()-1):
                        item = tw.item(row, col)
                        if item is not None:
                            txt = item.text()
                            if _decimal == ',':
                                txt = txt.replace('.', ',')
                            rowdata.append(txt)
                        else:
                            rowdata.append('')
                    csvwriter.writerow(rowdata)


class Qtiplot:
    """
    Une classe pour exporter des fichiers de type Qtiplot
    """
    from string import Template

    qtiFileTemplate = Template("""\
QtiPlot 0.9.0 project file
<scripting-lang>	muParser
<windows>	1
$table
<open>1</open>
""")

    tableTemplate = Template("""\
<table>
Table1	$ligs	$cols	$date
geometry	0	0	664	258	active
header$headers
ColWidth$colWidths
<com>
</com>
ColType$colTypes
ReadOnlyColumn$colRo
HiddenColumn$colHidden
Comments$comments
WindowLabel		2
<data>
$data
</data>
</table>
""")

    def __init__(self, app, filepath):
        """
        Crée l'objet
        @param app l'application de pymecavideo
        """
        self.app = app
        dic = {}
        dic['date'] = time.strftime("%d/%m/%y %H:%M")
        n = len(app.points.keys())
        if n < 30:
            n = 30
        dic['ligs'] = str(n)
        dic['cols'] = str(1 + 2 * app.nb_de_points)
        dic['headers'] = '\tt-s[X]'
        dic['colWidths'] = '\t100'
        dic['colTypes'] = '\t0;0/13'
        dic['colRo'] = '\t0'
        dic['colHidden'] = '\t0'
        dic['comments'] = '\t'
        for i in range(app.nb_de_points):
            dic['headers'] += '\tX%s-m[Y]\tY%s-m[Y]' % (i + 1, i + 1)
            dic['colWidths'] += "\t100\t100"
            dic['colTypes'] += "\t0;0/13\t0;0/13"
            dic['colRo'] += '\t0\t0'
            dic['colHidden'] += '\t0\t0'
            dic['comments'] += '\t\t'
        # deux bizarreries : tabulations supplémentaires
        dic['colWidths'] += '\t'
        dic['comments'] += '\t'
        dic['data'] = ''
        ligne = 0
        dt = app.deltaT
        for k in app.points.keys():
            data = app.points[k]
            dic['data'] += '%i\t%f' % (ligne, dt * ligne)
            for vect in data[1:]:
                vect = app.pointEnMetre(vect)
                dic['data'] += '\t%f\t%f' % (vect.x, vect.y)
            dic['data'] += '\n'
            ligne += 1
        # suppression du dernier retour à la ligne
        dic['data'] = dic['data'][:-1]
        self.table = self.tableTemplate.substitute(dic)
        self.qtifile = self.qtiFileTemplate.substitute({'table': self.table})
        with open(filepath, 'w') as f:
            f.write(self.qtifile)


class Calc():
    """
    Objet capable d'écrire des données textes et numériques dans
    un fichier au fomat ODS
    """

    def __init__(self, app, fichier_ods):
        """
        Crée un fichier ods et importe les données de pymecavideo
        """
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.text import P
        from odf.table import Table, TableRow, TableCell
        self.P = P
        self.TableRow = TableRow
        self.TableCell = TableCell
        self.outfile = open(fichier_ods, 'wb')
        self.doc = OpenDocumentSpreadsheet()
        self.table = Table(name="Pymecavideo {0}".format(
            time.strftime("%Y-%m-%d %Hh%Mm%Ss")))
        self.exportpymeca(app)

    def exportpymeca(self, app):
        """
        exporte les données de pymecavideo
        @param app pointeur vers l'application
        """
        # fait une ligne de titres
        titles = ["t (s)"]
        for obj in app.video.suivis:
            titles.append(f"X{obj} (m)")
            titles.append(f"Y{obj} (m)")
        row = self.TableRow()
        self.table.addElement(row)
        for t in titles:
            tc = self.TableCell()
            row.addElement(tc)
            para = self.P(text=t)
            tc.addElement(para)


        self.tr = []
        def cb_temps(i,t):
            """
            fonction de rappel qui crée les lignes de tableur et
            y inscrit la date, à gauche; construit self.tr la liste des
            pointeurs vers les lignes du tableur
            """
            row = self.TableRow()
            self.tr.append(row)
            self.table.addElement(row)
            row.addElement(
                self.TableCell(valuetype="float", value=str(t)))
            return
        
        def cb_point(i, t, j, obj, p, v):
            """
            fonction de rappel qui inscrit les coordonnées dans le tableur
            """
            self.tr[i].addElement(
                self.TableCell(valuetype="float", value=str(p.x)))
            self.tr[i].addElement(
                self.TableCell(valuetype="float", value=str(p.y)))
            return 

        # écrit dans toutes les cases du tableur
        app.video.iteration_data(cb_temps, cb_point, unite="m")
        # accroche la feuille au document tableur
        self.doc.spreadsheet.addElement(self.table)
        # écrit dans le fichier de sortie
        self.doc.save(self.outfile)
        self.outfile.close()
        return

class PythonSource:
    """
    Exporte les données dans un fichier Python(source)
    """

    # lignes de code en tête du programme Python
    en_tete = """\
#!/usr/bin/env python3
## Données exportées de Pymecavidéo
## {date}
import numpy as np
import matplotlib.pyplot as plt

# Intervalle de temps auto-détecté
dt={deltaT}
"""
    
    # lignes de code a écrire dans tous les cas, après l'en-tête
    code = """

    ##############################################################
    # Le code auto-généré qui suit peut être effacé à volonté.   #
    ##############################################################
    # Il n'est là qu'à titre d'exemple, et il n'est pas toujours #
    # approprié à l'usage des données que vous avez exportées.   #
    ##############################################################

    ## affichage des points
    plt.plot(x1,y1,'o',markersize= 3)
    plt.xlabel("x (en m)")
    plt.ylabel("y (en m)")

    ## calcul et affichage des vecteurs vitesses



    {cv}
    {vv}

    ## calcul et affichage des vecteurs accélérations

    {ca}
    {va}

    ## présentation du diagramme interactif
    plt.grid()
    plt.show()
    """

    # lignes de code si on veut calculer les vitesses
    cv1 = """
    Δt = 2*dt
    vx = np.array(np.zeros(len(x1)-2))
    vy = np.array(np.zeros(len(x1)-2))
    i=0
    for k in range(1,len(x1)-1):
        Δx = (x1[k+1]-x1[k-1])
        Δy = (y1[k+1]-y1[k-1])
        vx[i] = Δx/Δt
        vy[i] = Δy/Δt
        i+=1
"""

    # lignes de code si on ne veut pas calculer la vitesse
    cv0 = """
##### à compléter pour calculer les vitesses ####
        ##############
        ##############
"""
    # lignes de code activables éventuellement dans l'éditeur, afin
    # de tracer les vecteurs vitesse
    vv = """
    #Pour afficher les vecteurs vitesses, décommentez la ligne suivante quand le code précédent est prêt.
    #plt.quiver(x1[1:-1], y1[1:-1], vx, vy, scale_units = 'xy', angles = 'xy', width = 0.003)
     """

    # lignes de code si on veut calculer l'accélération
    ca1 = """
    ax = np.array(np.zeros(len(vx)-2))
    ay = np.array(np.zeros(len(vx)-2))
    i=0
    for k in range(1, len(vx)-1):
        Δvx = (vx[k+1]-vx[k-1])
        Δvy = (vy[k+1]-vy[k-1])
        ax[i] = Δvx/Δt
        ay[i] = Δvy/Δt
        i+=1"""

    # lignes de code si on ne veut pas calculer l'accélération
    ca0 = """#####à compléter pour calculer les vitesses####
        ##############
        ##############"""

    # lignes de code si on veut voir les vecteurs accélération
    va = """
    plt.title("Vecteurs accélérations") 
    plt.quiver(x1[2:-2], y1[2:-2], ax, ay, scale_units = 'xy', angles = 'xy', width = 0.003, color = 'r')
"""
    
    def __init__(self, app, filepath):
        # traitement du scénario des vitesses/accélrations :
        # si seule la vitesse est cochée, on calcule et affiche les vitesses
        # si les deux sont cochées, on calcule et affiche les vitesses et accélérations
        # si seule l'accélération est cochée, les vitesses sont calculées mais non affichées
        #self.dbg.p(1, "rentre dans 'python source2'")
        d = PythonExportDialog(app)
        if d.exec_() == QDialog.Accepted:
            calcule_vitesse, affiche_vitesse, calcule_accel, affiche_accel = d.checkBox_v.isChecked(
            ), d.checkBox_v2.isChecked(), d.checkBox_accel.isChecked(), d.checkBox_accel2.isChecked()
        if affiche_vitesse:
            calcule_vitesse = True
        if calcule_accel or affiche_accel:
            "on veut les accelerations, il faut les vitesse"
            calcule_vitesse = True
        if affiche_accel:
            calcule_accel = True
            calcule_vitesse = True
        with open(filepath, "w", encoding="UTF-8") as f:
            date = time.strftime("%d/%m/%y %H:%M")
            f.write(self.en_tete.format(date=date, deltaT=app.video.deltaT))

            commentaires = []
            lignes_x     = []
            lignes_y     = []

            def cb_objet(i, obj):
                """
                fonction de rappel pour chacun des objets; modifie les listes
                commentaires, lignes_x et lignes_y
                @param i index de l'objet, commençant à 0
                @param obj un objet suivi
                """
                commentaires.append(f"""\

# coordonnées du point numéro {obj}

""")
                lignes_x.append(f"x{obj} = np.array([")
                lignes_y.append(f"y{obj} = np.array([")
                return


            def cb_point(i, obj, p):
                """
                fonction de rappel pour les points pointés appartenant à un
                objet
                @param i l'index de l'objet, commençant à 0
                @param obj l'objet suivi
                @param p un pointage (de type vecteur)
                """
                if p is not None:
                    lignes_x[i] += f"{p.x}, "
                    lignes_y[i] += f"{p.y}, "
                return

            # on crée les commentaires et les lignes de déclaration de
            # tableaux de nombres
            app.video.iteration_objet(cb_objet, cb_point, unite="m")
            
            # On termine les lignes de déclaration des tableaux de nombres
            lignes_x = [l + "])\n" for l in lignes_x]
            lignes_y = [l + "])\n" for l in lignes_y]


            for c, lx, ly in zip(commentaires, lignes_x, lignes_y):
                f.write(c); f.write(lx); f.write(ly)
            f.write(self.code.format(
                cv = self.cv1 if calcule_vitesse else self.cv0,
                vv = self.vv,
                ca = self.ca1 if calcule_accel else self.ca0,
                va = self.va if affiche_accel else "",
            ))
        return
    

class CsvExportDialog(QDialog):
    """
    Fenêtre de dialogue permettant de choisir séparateurs de champ et décimal dans le fichier CSV
    """

    def __init__(self, *args, **kwargs):
        super(CsvExportDialog, self).__init__(*args, **kwargs)
        self.setObjectName("CsvExportDialog")
        self.resize(430, 262)
        self.decimal = "."
        self.field = ","
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gbDec = QGroupBox(self)
        self.gbDec.setObjectName("gbDec")
        self.horizontalLayout = QHBoxLayout(self.gbDec)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.rbDecDot = QRadioButton(self.gbDec)
        self.rbDecDot.setMinimumSize(QSize(130, 0))
        self.rbDecDot.setChecked(True)
        self.rbDecDot.setObjectName("rbDecDot")
        self.horizontalLayout.addWidget(self.rbDecDot)
        self.rbDecComma = QRadioButton(self.gbDec)
        self.rbDecComma.setMinimumSize(QSize(130, 0))
        self.rbDecComma.setObjectName("rbDecComma")
        self.horizontalLayout.addWidget(self.rbDecComma)
        spacerItem = QSpacerItem(
            127, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.gbDec)
        self.gbCha = QGroupBox(self)
        self.gbCha.setObjectName("gbCha")
        self.gridLayout_2 = QGridLayout(self.gbCha)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.rbFieldComma = QRadioButton(self.gbCha)
        self.rbFieldComma.setMinimumSize(QSize(130, 0))
        self.rbFieldComma.setChecked(True)
        self.rbFieldComma.setObjectName("rbFieldComma")
        self.gridLayout_2.addWidget(self.rbFieldComma, 0, 0, 1, 1)
        self.rbFieldSemicolon = QRadioButton(self.gbCha)
        self.rbFieldSemicolon.setMinimumSize(QSize(130, 0))
        self.rbFieldSemicolon.setChecked(False)
        self.rbFieldSemicolon.setObjectName("rbFieldSemicolon")
        self.gridLayout_2.addWidget(self.rbFieldSemicolon, 0, 1, 1, 1)
        self.rbFieldTab = QRadioButton(self.gbCha)
        self.rbFieldTab.setMinimumSize(QSize(130, 0))
        self.rbFieldTab.setChecked(False)
        self.rbFieldTab.setObjectName("rbFieldTab")
        self.gridLayout_2.addWidget(self.rbFieldTab, 0, 2, 1, 1)
        self.verticalLayout.addWidget(self.gbCha)
        self.checkBox = QCheckBox(self)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.retranslateUi()
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.rbDecComma.toggled.connect(self.check_if_dot)
        self.rbDecDot.toggled.connect(self.change_dec)
        self.rbFieldComma.toggled.connect(self.change_field)
        self.rbFieldSemicolon.toggled.connect(self.change_field)
        self.rbFieldTab.toggled.connect(self.change_field)

    def change_field(self):
        if self.rbFieldComma.isChecked():
            self.field = ","
        elif self.rbFieldSemicolon.isChecked():
            self.field = ";"
        elif self.rbFieldTab.isChecked():
            self.field = "\t"

    def change_dec(self):
        if self.rbFieldComma.isChecked():
            self.decimal = ","
        elif self.rbDecDot.isChecked():
            self.decimal = "."

    def check_if_dot(self):
        if self.rbDecComma.isChecked():
            if self.rbFieldComma.isChecked():
                self.rbFieldSemicolon.setChecked(True)
            self.rbFieldComma.setEnabled(False)
        else:
            self.rbFieldComma.setEnabled(True)
        self.change_field()

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("CsvExportDialog", "Dialog"))
        self.gbDec.setTitle(_translate(
            "CsvExportDialog", "Séparateur décimal :"))
        self.rbDecDot.setText(_translate("CsvExportDialog", "Point ( . )"))
        self.rbDecComma.setText(_translate("CsvExportDialog", "Virgule ( , )"))
        self.gbCha.setTitle(_translate(
            "CsvExportDialog", "Séparateur de champ :"))
        self.rbFieldComma.setText(_translate(
            "CsvExportDialog", "Virgule ( , )"))
        self.rbFieldSemicolon.setText(_translate(
            "CsvExportDialog", "Point-virgule ( ; )"))
        self.rbFieldTab.setText(_translate(
            "CsvExportDialog", "Tabulation ( \\t )"))
        self.checkBox.setText(_translate(
            "CsvExportDialog", "Ajouter les grandeurs comme en-tête"))


class PythonExportDialog(QDialog):
    """
    Fenêtre de dialogue permettant de choisir les grandeurs à exporter 
    dans le fichier Python(source)
    """

    def __init__(self, *args, **kwargs):
        super(PythonExportDialog, self).__init__(*args, **kwargs)
        self.setGeometry(30, 20, 359, 87)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.checkBox_v = QCheckBox(self)
        self.checkBox_v.setObjectName("checkBox_vitesse")
        self.checkBox_v2 = QCheckBox(self)
        self.checkBox_v2.setObjectName("checkBox_vitesse2")
        self.checkBox_accel = QCheckBox(self)
        self.checkBox_accel.setObjectName("checkBox_accel")
        self.checkBox_accel2 = QCheckBox(self)
        self.checkBox_accel2.setObjectName("checkBox_accel2")
        self.verticalLayout.addWidget(self.checkBox_v)
        self.verticalLayout.addWidget(self.checkBox_v2)
        self.verticalLayout.addWidget(self.checkBox_accel)
        self.verticalLayout.addWidget(self.checkBox_accel2)
        self.layout.addLayout(self.verticalLayout)
        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(_translate("choix_exports", "Choix export python"))
        self.checkBox_v.setText(_translate(
            "choix_exports", "insérer les lignes pour le calcul des vitesses"))
        self.checkBox_accel.setText(_translate(
            "choix_exports", "insérer les lignes pour le calcul des accélérations"))
        self.checkBox_v2.setText(_translate(
            "choix_exports", "insérer les lignes pour l'affichage des vecteurs vitesses"))
        self.checkBox_accel2.setText(_translate(
            "choix_exports", "insérer les lignes pour l'affichage des vecteurs des accélérations"))


class PythonNumpy:
    """
    Exporte les données dans un fichier Numpy
    """

    def __init__(self, app, filepath):
        import numpy as np

        liste_temps = app.video.liste_t_pointes()
        
        x_objets = {o: [] for o in app.video.suivis}
        y_objets = {o: [] for o in app.video.suivis}
        def cb_points(i, t, j, obj, p, v):
            """
            fonction de rappel pour chaque point
            """
            if p is None: return
            x_objets[obj].append(p.x)
            y_objets[obj].append(p.y)
            return

        app.video.iteration_data(None, cb_points, unite = "m")
        
        export = [liste_temps]
        for obj in app.video.suivis:
            export.append(x_objets[obj])
            export.append(y_objets[obj])

        np.save(filepath, export)
        QMessageBox.information(
            None,
            _translate("export_numpy", "Fichier Numpy sauvegardé"),
            _translate("export_numpy",
                       """Pour ouvrir ce fichier depuis Python, taper :

import numpy as np\nt,x1,y1 ... = np.load("{}")""".format(
    os.path.basename(filepath))))
        return

class NotebookExportDialog(QDialog):
    """
    Fenêtre de dialogue permettant de choisir les grandeurs à exporter 
    dans le fichier Notebook Jupyterlab
    """

    def __init__(self, *args, **kwargs):
        super(NotebookExportDialog, self).__init__(*args, **kwargs)
        self.resize(390,225)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.checkBox_c = QCheckBox(self)
        self.checkBox_v = QCheckBox(self)        
        self.checkBox_v2 = QCheckBox(self)
        self.checkBox_a = QCheckBox(self)
        self.checkBox_e = QCheckBox(self)
        for w in (self.checkBox_c, self.checkBox_v, self.checkBox_v2, self.checkBox_a, self.checkBox_e) :
            w.setTristate(False)
            w.setChecked(True)
        self.verticalLayout.addWidget(self.checkBox_c)
        self.verticalLayout.addWidget(self.checkBox_v)
        self.verticalLayout.addWidget(self.checkBox_v2)
        self.verticalLayout.addWidget(self.checkBox_a)
        self.verticalLayout.addWidget(self.checkBox_e)
        self.layout.addLayout(self.verticalLayout)
        self.retranslateUi()
        self.checkBox_v.stateChanged.connect(self.etat_vitesse)
        
    def etat_vitesse(self,etat):
        if etat == 0 :
            for w in (self.checkBox_v2, self.checkBox_a, self.checkBox_e):
                w.setChecked(False)
                w.setEnabled(False)
        else : 
            for w in (self.checkBox_v2, self.checkBox_a, self.checkBox_e):
                w.setEnabled(True)    
            
    def retranslateUi(self):
        self.setWindowTitle(_translate("choix_exports_notebook", "Choix des représentations graphiques"))
        self.checkBox_c.setText(_translate(
            "choix_exports_notebook", "Chronogramme des positions"))
        self.checkBox_v.setText(_translate(
            "choix_exports_notebook", "Vecteurs vitesse"))
        self.checkBox_a.setText(_translate(
            "choix_exports_notebook", "Vecteurs accélération"))
        self.checkBox_v2.setText(_translate(
            "choix_exports_notebook", "Vecteurs variation de vitesse"))
        self.checkBox_e.setText(_translate(
            "choix_exports_notebook", "Energies"))
        
class PythonNotebook :
    """
    Exporte les données dans un fichier Notebook Jupyterlab
    Attention : seul le premier objet est exporté !
    """
    def __init__(self, app, filepath):
        import nbformat as nbf
        from template_ipynb import genere_notebook
        ligne_t = "np.array({})".format(app.video.liste_t_pointes())
        points = app.video.liste_pointages()
        ligne_x = "np.array({})".format([p.x for p in points])
        ligne_y = "np.array({})".format([p.y for p in points])
        d = NotebookExportDialog(app)
        if d.exec_() == QDialog.Accepted:
            graphs = (d.checkBox_c.isChecked(), d.checkBox_v.isChecked(
            ), d.checkBox_v2.isChecked(), d.checkBox_a.isChecked(), d.checkBox_e.isChecked())
        nb = genere_notebook((ligne_t, ligne_x, ligne_y), graphs = graphs)
        nbf.write(nb, filepath)
        return

class SaveThenOpenFileDialog(QFileDialog):
    """
    Enregistre un fichier et propose de l'ouvrir ensuite
    """

    def __init__(self, *args, extension=None, proposeOuverture=True):
        super().__init__(*args)
        DBG.p(1, "rentre dans 'SaveThenOpenFileDialog'")
        self.setOption(QFileDialog.DontUseNativeDialog)
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setWindowFlags(self.windowFlags() & ~Qt.Dialog)
        urls = [QUrl.fromLocalFile(QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]),
                QUrl.fromLocalFile(QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]),
                QUrl.fromLocalFile(QStandardPaths.standardLocations(QStandardPaths.DesktopLocation)[0])
                ]
        self.setSidebarUrls(urls)
        self.setDefaultSuffix(extension)
        self.checkbox = QCheckBox(self)
        self.checkbox.setStyleSheet("color: rgb(255, 0, 0);")
        self.checkbox.setText("Ouvrir le fichier après enregistrement")
        self.layout().addWidget(self.checkbox)
        if not proposeOuverture:
            self.checkbox.setVisible(False)

# CLASSE PRINCIPALE
# en fin de fichier pour récupérer les globals()
# ==============================================


class Export:

    def __init__(self, app, choix_export):
        DBG.p(1, "rentre dans 'Export'")
        self.app = app
        propose_ouverture = EXPORT_FORMATS[choix_export]['propose_ouverture']
        base_name = os.path.splitext(os.path.basename(app.filename))[0]
        filtre = EXPORT_FORMATS[choix_export]['filtre']
        extension = EXPORT_FORMATS[choix_export]['extension']
        self.class_str = EXPORT_FORMATS[choix_export]['class']
        un_point = EXPORT_FORMATS[choix_export]['un_point']
        modules = EXPORT_FORMATS[choix_export]['modules']
        # On vérifie si les modules additionnels sont présents
        if modules:
            for mod in modules:
                try:
                    m = __import__(mod)
                except ImportError:
                    DBG.p(3, "erreur d'export")
                    DBG.p(3, EXPORT_MESSAGES)
                    msg = EXPORT_MESSAGES[3]
                    QMessageBox.critical(None, msg['titre'], msg['texte'].format(
                        mod))
                    return
        # On vérifie si le nombre de points est adapté
        if un_point and app.nb_de_points > 1:
            msg = EXPORT_MESSAGES[1]
            QMessageBox.warning(
                None, msg['titre'], msg['texte'], QMessageBox.Ok, QMessageBox.Ok)
            return
        self.demande_nom_fichier(
            base_name, filtre, extension, propose_ouverture)

    def demande_nom_fichier(self, filename, filtre, extension, propose_ouverture):
        defaultName = os.path.join(DOCUMENT_PATH[0], filename)
        fd = SaveThenOpenFileDialog(None, 'Exporter...', defaultName,
                                    filtre, extension=extension, proposeOuverture=propose_ouverture)
        ouvre = False
        if fd.exec_() == QDialog.Accepted:
            filepath = fd.selectedFiles()[0]
            ouvre = fd.checkbox.isChecked()
            # self.enregistre_fichier(filepath)
            self.enregistre_fichier(filepath)
            if INFO_OK:
                msg = EXPORT_MESSAGES[2]
                QMessageBox.information(None, msg['titre'], msg['texte'].format(
                    filepath))
        if ouvre:
            self.ouvre_fichier(filepath)
        return

    def enregistre_fichier(self, filepath):
        """
        Redirige vers la routine d'exportation qui est définie par
        self.class_str
        """
        dynamic_class = globals()[self.class_str]
        dynamic_class(self.app, filepath)

    def ouvre_fichier(self, filepath):
        if sys.platform.startswith('linux'):
            os.system("xdg-open "+filepath)
        elif sys.platform.startswith('darwin'):
            os.system("open "+filepath)
        elif sys.platform.startswith('win'):
            os.startfile(os.path.realpath(filepath))
