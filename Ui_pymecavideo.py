# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pymecavideo.ui'
#
# Created: Sun Jan 13 16:28:58 2008
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_pymecavideo(object):
    def setupUi(self, pymecavideo):
        pymecavideo.setObjectName("pymecavideo")
        pymecavideo.resize(QtCore.QSize(QtCore.QRect(0,0,673,675).size()).expandedTo(pymecavideo.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(pymecavideo)
        self.centralwidget.setObjectName("centralwidget")

        self.hboxlayout = QtGui.QHBoxLayout(self.centralwidget)
        self.hboxlayout.setObjectName("hboxlayout")

        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        self.tab_acq = QtGui.QWidget()
        self.tab_acq.setObjectName("tab_acq")

        self.label = QtGui.QLabel(self.tab_acq)
        self.label.setGeometry(QtCore.QRect(10,100,640,480))

        palette = QtGui.QPalette()

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(147,147,147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Window,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(147,147,147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Window,brush)

        brush = QtGui.QBrush(QtGui.QColor(147,147,147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(147,147,147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Window,brush)
        self.label.setPalette(palette)
        self.label.setCursor(QtCore.Qt.ArrowCursor)
        self.label.setAutoFillBackground(True)
        self.label.setObjectName("label")

        self.label_infos_image = QtGui.QLabel(self.tab_acq)
        self.label_infos_image.setGeometry(QtCore.QRect(170,70,341,20))
        self.label_infos_image.setAlignment(QtCore.Qt.AlignCenter)
        self.label_infos_image.setObjectName("label_infos_image")

        self.horizontalSlider = QtGui.QSlider(self.tab_acq)
        self.horizontalSlider.setGeometry(QtCore.QRect(10,50,281,16))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")

        self.Bouton_Echelle = QtGui.QPushButton(self.tab_acq)
        self.Bouton_Echelle.setGeometry(QtCore.QRect(140,20,101,26))
        self.Bouton_Echelle.setObjectName("Bouton_Echelle")

        self.spinBox_image = QtGui.QSpinBox(self.tab_acq)
        self.spinBox_image.setGeometry(QtCore.QRect(69,21,51,26))
        self.spinBox_image.setMinimumSize(QtCore.QSize(51,26))
        self.spinBox_image.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_image.setObjectName("spinBox_image")

        self.label_numero_image = QtGui.QLabel(self.tab_acq)
        self.label_numero_image.setGeometry(QtCore.QRect(11,21,52,26))
        self.label_numero_image.setAutoFillBackground(False)
        self.label_numero_image.setAlignment(QtCore.Qt.AlignCenter)
        self.label_numero_image.setObjectName("label_numero_image")

        self.spinBox_nb_de_points = QtGui.QSpinBox(self.tab_acq)
        self.spinBox_nb_de_points.setGeometry(QtCore.QRect(404,24,51,26))
        self.spinBox_nb_de_points.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_nb_de_points.setMinimum(1)
        self.spinBox_nb_de_points.setMaximum(10)
        self.spinBox_nb_de_points.setObjectName("spinBox_nb_de_points")

        self.label_2 = QtGui.QLabel(self.tab_acq)
        self.label_2.setGeometry(QtCore.QRect(351,1,157,16))
        self.label_2.setObjectName("label_2")

        self.echelleEdit = QtGui.QLineEdit(self.tab_acq)
        self.echelleEdit.setGeometry(QtCore.QRect(251,21,55,26))
        self.echelleEdit.setMinimumSize(QtCore.QSize(55,26))
        self.echelleEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.echelleEdit.setReadOnly(True)
        self.echelleEdit.setObjectName("echelleEdit")

        self.label_4 = QtGui.QLabel(self.tab_acq)
        self.label_4.setGeometry(QtCore.QRect(312,21,28,26))
        self.label_4.setObjectName("label_4")

        self.Bouton_lance_capture = QtGui.QPushButton(self.tab_acq)
        self.Bouton_lance_capture.setGeometry(QtCore.QRect(510,20,136,26))
        self.Bouton_lance_capture.setObjectName("Bouton_lance_capture")
        self.tabWidget.addTab(self.tab_acq,"")

        self.tab_traj = QtGui.QWidget()
        self.tab_traj.setObjectName("tab_traj")

        self.label_3 = QtGui.QLabel(self.tab_traj)
        self.label_3.setGeometry(QtCore.QRect(10,100,640,480))

        palette = QtGui.QPalette()

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(194,197,196))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Window,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(194,197,196))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Window,brush)

        brush = QtGui.QBrush(QtGui.QColor(194,197,196))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(194,197,196))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Window,brush)
        self.label_3.setPalette(palette)
        self.label_3.setCursor(QtCore.Qt.ArrowCursor)
        self.label_3.setAutoFillBackground(True)
        self.label_3.setObjectName("label_3")

        self.widget = QtGui.QWidget(self.tab_traj)
        self.widget.setGeometry(QtCore.QRect(20,10,585,53))
        self.widget.setObjectName("widget")

        self.hboxlayout1 = QtGui.QHBoxLayout(self.widget)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setObjectName("vboxlayout")

        self.label_7 = QtGui.QLabel(self.widget)
        self.label_7.setObjectName("label_7")
        self.vboxlayout.addWidget(self.label_7)

        self.comboBox_referentiel = QtGui.QComboBox(self.widget)
        self.comboBox_referentiel.setMinimumSize(QtCore.QSize(130,25))
        self.comboBox_referentiel.setObjectName("comboBox_referentiel")
        self.vboxlayout.addWidget(self.comboBox_referentiel)
        self.hboxlayout1.addLayout(self.vboxlayout)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.label_5 = QtGui.QLabel(self.widget)
        self.label_5.setObjectName("label_5")
        self.vboxlayout1.addWidget(self.label_5)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.echelle_v = QtGui.QComboBox(self.widget)
        self.echelle_v.setMinimumSize(QtCore.QSize(36,25))
        self.echelle_v.setEditable(True)
        self.echelle_v.setObjectName("echelle_v")
        self.hboxlayout2.addWidget(self.echelle_v)

        self.label_6 = QtGui.QLabel(self.widget)
        self.label_6.setObjectName("label_6")
        self.hboxlayout2.addWidget(self.label_6)
        self.vboxlayout1.addLayout(self.hboxlayout2)
        self.hboxlayout1.addLayout(self.vboxlayout1)

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem2)

        self.comboBox_v = QtGui.QComboBox(self.widget)
        self.comboBox_v.setObjectName("comboBox_v")
        self.hboxlayout1.addWidget(self.comboBox_v)
        self.tabWidget.addTab(self.tab_traj,"")
        self.hboxlayout.addWidget(self.tabWidget)
        pymecavideo.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(pymecavideo)
        self.menubar.setGeometry(QtCore.QRect(0,0,673,24))
        self.menubar.setObjectName("menubar")

        self.menuFichier = QtGui.QMenu(self.menubar)
        self.menuFichier.setObjectName("menuFichier")

        self.menuAide = QtGui.QMenu(self.menubar)
        self.menuAide.setObjectName("menuAide")
        pymecavideo.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(pymecavideo)
        self.statusbar.setObjectName("statusbar")
        pymecavideo.setStatusBar(self.statusbar)

        self.actionOuvrir_un_fichier = QtGui.QAction(pymecavideo)
        self.actionOuvrir_un_fichier.setObjectName("actionOuvrir_un_fichier")

        self.actionAvanceimage = QtGui.QAction(pymecavideo)
        self.actionAvanceimage.setObjectName("actionAvanceimage")

        self.actionReculeimage = QtGui.QAction(pymecavideo)
        self.actionReculeimage.setObjectName("actionReculeimage")

        self.actionQuitter = QtGui.QAction(pymecavideo)
        self.actionQuitter.setObjectName("actionQuitter")

        self.actionSaveData = QtGui.QAction(pymecavideo)
        self.actionSaveData.setObjectName("actionSaveData")

        self.action_propos = QtGui.QAction(pymecavideo)
        self.action_propos.setObjectName("action_propos")

        self.actionAide = QtGui.QAction(pymecavideo)
        self.actionAide.setObjectName("actionAide")

        self.actionExemples = QtGui.QAction(pymecavideo)
        self.actionExemples.setObjectName("actionExemples")
        self.menuFichier.addAction(self.actionOuvrir_un_fichier)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.actionSaveData)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.actionQuitter)
        self.menuAide.addAction(self.actionAide)
        self.menuAide.addAction(self.actionExemples)
        self.menuAide.addSeparator()
        self.menuAide.addAction(self.action_propos)
        self.menubar.addAction(self.menuFichier.menuAction())
        self.menubar.addAction(self.menuAide.menuAction())

        self.retranslateUi(pymecavideo)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(pymecavideo)

    def retranslateUi(self, pymecavideo):
        pymecavideo.setWindowTitle(QtGui.QApplication.translate("pymecavideo", "PyMecaVideo, analyse mécanique des vidéos", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("pymecavideo", "Pas de vidéos chargées", None, QtGui.QApplication.UnicodeUTF8))
        self.label_infos_image.setText(QtGui.QApplication.translate("pymecavideo", "Bienvenue sur pymeca vidéo, pas d\'images chargée", None, QtGui.QApplication.UnicodeUTF8))
        self.Bouton_Echelle.setText(QtGui.QApplication.translate("pymecavideo", "Définir l\'échelle", None, QtGui.QApplication.UnicodeUTF8))
        self.label_numero_image.setText(QtGui.QApplication.translate("pymecavideo", "Image n°", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("pymecavideo", "Nombre de points à étudier", None, QtGui.QApplication.UnicodeUTF8))
        self.echelleEdit.setText(QtGui.QApplication.translate("pymecavideo", "indéf.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("pymecavideo", "px/m", None, QtGui.QApplication.UnicodeUTF8))
        self.Bouton_lance_capture.setText(QtGui.QApplication.translate("pymecavideo", "Démarrer l\'acquisition", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_acq), QtGui.QApplication.translate("pymecavideo", "Acquisition des données", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("pymecavideo", "Origine du référentiel :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("pymecavideo", "Vitesses :", None, QtGui.QApplication.UnicodeUTF8))
        self.echelle_v.addItem(QtGui.QApplication.translate("pymecavideo", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("pymecavideo", "px pour 1 m/s", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_v.addItem(QtGui.QApplication.translate("pymecavideo", "Toujours visibles", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_v.addItem(QtGui.QApplication.translate("pymecavideo", "Visibles près de la souris", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_traj), QtGui.QApplication.translate("pymecavideo", "trajectoires et mesures", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFichier.setTitle(QtGui.QApplication.translate("pymecavideo", "Fichier", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAide.setTitle(QtGui.QApplication.translate("pymecavideo", "Aide", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOuvrir_un_fichier.setText(QtGui.QApplication.translate("pymecavideo", "Ouvrir une vidéo", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAvanceimage.setText(QtGui.QApplication.translate("pymecavideo", "avanceimage", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReculeimage.setText(QtGui.QApplication.translate("pymecavideo", "reculeimage", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuitter.setText(QtGui.QApplication.translate("pymecavideo", "Quitter", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSaveData.setText(QtGui.QApplication.translate("pymecavideo", "Enregistrer les données", None, QtGui.QApplication.UnicodeUTF8))
        self.action_propos.setText(QtGui.QApplication.translate("pymecavideo", "À propos", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAide.setText(QtGui.QApplication.translate("pymecavideo", "Aide", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExemples.setText(QtGui.QApplication.translate("pymecavideo", "Exemples ...", None, QtGui.QApplication.UnicodeUTF8))

