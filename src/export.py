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


from globdef import DOCUMENT_PATH, HOME_PATH
from PyQt6.QtWidgets import QFileDialog, QCheckBox, QDialog, QMessageBox
from PyQt6.QtCore import Qt, QCoreApplication, QUrl, QStandardPaths
import sys
import os, time

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
    1: {'nom': QCoreApplication.translate("export", 'Libre/OpenOffice Calc'),
        'filtre': QCoreApplication.translate("export", 'Feuille de calcul OpenDocument (*.ods)'),
        'extension': 'ods',
        'class': 'Calc',
        'modules': ['odf'],
        'propose_ouverture': True,
        'un_point': False},

    2: {'nom': QCoreApplication.translate("export", 'Python (source)'),
        'filtre': QCoreApplication.translate("export", 'Fichier Python (*.py)'),
        'extension': 'py',
        'class': 'PythonSource',
        'modules': None,
        'propose_ouverture': True,
        'un_point': True},

    3: {'nom': QCoreApplication.translate("export", 'Python (Numpy)'),
        'filtre': QCoreApplication.translate("export", 'Fichier Numpy (*.npy)'),
        'extension': 'npy',
        'class': 'PythonNumpy',
        'modules': ['numpy'],
        'propose_ouverture': False,
        'un_point': True},
    
    4: {'nom' : QCoreApplication.translate("export",'Jupyter Notebook'),
        'filtre' : QCoreApplication.translate("export",'Notebook (*.ipynb)'),
        'extension' : 'ipynb',
        'class' : 'PythonNotebook',
        'modules' : ['nbformat'],
        'propose_ouverture' : False,
        'un_point' : True},
    
    5: {'nom': QCoreApplication.translate("export", 'Fichier CSV'),
        'filtre': QCoreApplication.translate("export", 'Fichier CSV (*.csv, *.txt)'),
        'extension': 'csv',
        'class': 'FichierCSV',
        'modules': None,
        'propose_ouverture': True,
        'un_point': False},

    6: {'nom': QCoreApplication.translate("export", 'Pandas Dataframe'),
        'filtre': QCoreApplication.translate("export", 'Dataframe (*.pkl)'),
        'extension': 'pkl',
        'class': 'DataframePandas',
        'modules': ['pandas'],
        'propose_ouverture': False,
        'un_point': False},
}

# Dictionnaire contenant les textes des QMessageBox information, warning...
EXPORT_MESSAGES = {
    0: {'titre': QCoreApplication.translate("export", "Erreur lors de l'exportation"),
        'texte': QCoreApplication.translate("export", "Echec de l'enregistrement du fichier:<b>\n{0}</b>")},

    1: {'titre': QCoreApplication.translate("export", "Impossible de créer le fichier"),
        'texte': QCoreApplication.translate("export", "L'export n'est possible que pour 1 seul point cliqué.")},

    2: {'titre': QCoreApplication.translate("export", "Exportation terminée"),
        'texte': QCoreApplication.translate("export", "Fichier:\n<b>{0}</b>\nenregistré avec succès.")},

    3: {'titre': QCoreApplication.translate("export", "Impossible de créer le fichier"),
        'texte': QCoreApplication.translate("export", "Le module <b>{0}</b> n'est pas installé.")},
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
            QCoreApplication.translate("export_pandas", "Fichier Pandas sauvegardé"),
            QCoreApplication.translate(
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
        if d.exec() == QDialog.DialogCode.Accepted:
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
        exporte les données de pymecavideo vers le tableur Calc
        @param app pointeur vers l'application
        """
        # fait une ligne de titres
        titles = ["t (s)"]
        for obj in app.pointage.suivis:
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

        for i, t, iter_OP in app.pointage.gen_iter_TOP():
            row = self.TableRow()
            self.tr.append(row)
            self.table.addElement(row)
            row.addElement(
                self.TableCell(valuetype="float", value=str(t)))
            for j, obj, p in iter_OP:
                if p is None: continue
                # conversion en mètre, toujours
                p = app.pointage.pointEnMetre(p)
                self.tr[i].addElement(
                    self.TableCell(valuetype="float", value=str(p.x)))
                self.tr[i].addElement(
                    self.TableCell(valuetype="float", value=str(p.y)))
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
        #self.dbg.p(2, "rentre dans 'python source2'")
        d = PythonExportDialog(app)
        if d.exec() == QDialog.DialogCode.Accepted:
            calcule_vitesse, affiche_vitesse, calcule_accel, affiche_accel = \
                d.checkBox_v.isChecked(), \
                d.checkBox_v2.isChecked(), \
                d.checkBox_a.isChecked(),  \
                d.checkBox_a2.isChecked()
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
            f.write(self.en_tete.format(date=date, deltaT=app.pointage.deltaT))

            commentaires = []
            lignes_x     = []
            lignes_y     = []

            for i, obj, iter_P in app.pointage.gen_iter_OP():
                commentaires.append(f"""\

# coordonnées du point numéro {obj}

""")
                lignes_x.append(f"x{obj} = np.array([")
                lignes_y.append(f"y{obj} = np.array([")
                for p in iter_P:
                    if p is not None:
                        p = app.pointage.pointEnMetre(p)
                        lignes_x[i] += f"{p.x}, "
                        lignes_y[i] += f"{p.y}, "
            
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
    
from interfaces.Ui_csv_dialog import Ui_Dialog as Ui_csv_Dialog

class CsvExportDialog(QDialog, Ui_csv_Dialog):
    """
    Fenêtre de dialogue permettant de choisir séparateurs de champ et décimal dans le fichier CSV
    """

    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        Ui_csv_Dialog.__init__(self)
        self.setupUi(self)
        self.change_field()
        self.change_dec()
        return
    
    def change_field(self):
        if self.rbFieldComma.isChecked():
            self.field = ","
        elif self.rbFieldSemicolon.isChecked():
            self.field = ";"
        elif self.rbFieldTab.isChecked():
            self.field = "\t"
        return

    def change_dec(self):
        if self.rbFieldComma.isChecked():
            self.decimal = ","
        elif self.rbDecDot.isChecked():
            self.decimal = "."
        return
    
    def check_if_dot(self):
        if self.rbDecComma.isChecked():
            if self.rbFieldComma.isChecked():
                self.rbFieldSemicolon.setChecked(True)
            self.rbFieldComma.setEnabled(False)
        else:
            self.rbFieldComma.setEnabled(True)
        self.change_field()
        return

from interfaces.Ui_python_dialog import Ui_Dialog as Ui_Python

class PythonExportDialog(QDialog, Ui_Python):
    """
    Fenêtre de dialogue permettant de choisir les grandeurs à exporter 
    dans le fichier Python(source)
    """

    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        Ui_Python.__init__(self)
        self.setupUi(self)
        return

class PythonNumpy:
    """
    Exporte les données dans un fichier Numpy
    """

    def __init__(self, app, filepath):
        import numpy as np

        liste_temps = app.pointage.liste_t_pointes()
        
        x_objets = {o: [] for o in app.pointage.suivis}
        y_objets = {o: [] for o in app.pointage.suivis}

        for i, t, iter_OP in app.pointage.gen_iter_TOP():
            for j, obj, p in iter_OP:
                if p is None: continue
                p = app.pointage.pointEnMetre(p)
                x_objets[obj].append(p.x)
                y_objets[obj].append(p.y)
        
        export = [liste_temps]
        for obj in app.pointage.suivis:
            export.append(x_objets[obj])
            export.append(y_objets[obj])

        np.save(filepath, export)
        QMessageBox.information(
            None,
            QCoreApplication.translate("export_numpy", "Fichier Numpy sauvegardé"),
            QCoreApplication.translate("export_numpy",
                       """Pour ouvrir ce fichier depuis Python, taper :

import numpy as np\nt,x1,y1 ... = np.load("{}")""".format(
    os.path.basename(filepath))))
        return
from interfaces.Ui_jupyter_dialog import Ui_Dialog as Jupyter_Dialog

class NotebookExportDialog(QDialog, Jupyter_Dialog):
    """
    Fenêtre de dialogue permettant de choisir les grandeurs à exporter 
    dans le fichier Notebook Jupyterlab
    """

    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        Jupyter_Dialog.__init__(self)
        self.setupUi(self)
        return
        
    def etat_vitesse(self,etat):
        if etat == 0 :
            for w in (self.checkBox_v2, self.checkBox_a, self.checkBox_e):
                w.setChecked(False)
                w.setEnabled(False)
        else : 
            for w in (self.checkBox_v2, self.checkBox_a, self.checkBox_e):
                w.setEnabled(True)
        return
    
            
class PythonNotebook :
    """
    Exporte les données dans un fichier Notebook Jupyterlab
    Attention : seul le premier objet est exporté !
    """
    def __init__(self, app, filepath):
        import nbformat as nbf
        from template_ipynb import genere_notebook
        ligne_t = "np.array({})".format(app.pointage.liste_t_pointes())
        points = app.pointage.liste_pointages()
        ligne_x = "np.array({})".format([p.x for p in points])
        ligne_y = "np.array({})".format([p.y for p in points])
        d = NotebookExportDialog(app)
        if d.exec() == QDialog.DialogCode.Accepted:
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
        self.setOption(QFileDialog.Option.DontUseNativeDialog)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        #self.setWindowFlags(self.windowFlags() & ~Qt.WindowFlags.Dialog)
        urls = [QUrl.fromLocalFile(DOCUMENT_PATH),
                QUrl.fromLocalFile(HOME_PATH),
                QUrl.fromLocalFile(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation))
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
    """
    Une classe qui gère l'exportation des données

    paramètres du constructeur
    @param coord le widget principale de l'onglet coodonnées
    """

    def __init__(self, coord, choix_export):
        self.coord = coord
        self.app = coord.app
        self.pointage = coord.pointage
        self.dbg = coord.dbg
        self.dbg.p(1, "rentre dans 'Export'")
        propose_ouverture = EXPORT_FORMATS[choix_export]['propose_ouverture']
        base_name = os.path.splitext(os.path.basename(self.pointage.filename))[0]
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
                    self.dbg.p(3, "erreur d'export")
                    self.dbg.p(3, EXPORT_MESSAGES)
                    msg = EXPORT_MESSAGES[3]
                    QMessageBox.critical(None, msg['titre'], msg['texte'].format(
                        mod))
                    return
        self.demande_nom_fichier(
            base_name, filtre, extension, propose_ouverture)
        return

    def demande_nom_fichier(self, filename, filtre, extension, propose_ouverture):
        defaultName = os.path.join(DOCUMENT_PATH, filename)
        fd = SaveThenOpenFileDialog(None, 'Exporter...', defaultName,
                                    filtre, extension=extension, proposeOuverture=propose_ouverture)
        ouvre = False
        if fd.exec() == QDialog.DialogCode.Accepted:
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
        dynamic_class(self.coord, filepath)

    def ouvre_fichier(self, filepath):
        if sys.platform.startswith('linux'):
            os.system("xdg-open "+filepath)
        elif sys.platform.startswith('darwin'):
            os.system("open "+filepath)
        elif sys.platform.startswith('win'):
            os.startfile(os.path.realpath(filepath))
