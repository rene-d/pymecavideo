# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pymecavideo.ui'
#
# Created: Mon Jan 18 21:26:34 2010
#      by: PyQt4 UI code generator 4.6.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_pymecavideo(object):
    def setupUi(self, pymecavideo):
        pymecavideo.setObjectName("pymecavideo")
        pymecavideo.resize(865, 700)
        self.centralwidget = QtGui.QWidget(pymecavideo)
        self.centralwidget.setObjectName("centralwidget")
        self.hboxlayout = QtGui.QHBoxLayout(self.centralwidget)
        self.hboxlayout.setObjectName("hboxlayout")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setAutoFillBackground(True)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_acq = QtGui.QWidget()
        self.tab_acq.setObjectName("tab_acq")
        self.label = QtGui.QLabel(self.tab_acq)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(10, 110, 640, 480))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(147, 147, 147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(147, 147, 147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(147, 147, 147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(147, 147, 147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.label.setPalette(palette)
        self.label.setCursor(QtCore.Qt.ArrowCursor)
        self.label.setAutoFillBackground(True)
        self.label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.label.setObjectName("label")
        self.label_infos_image = QtGui.QLabel(self.tab_acq)
        self.label_infos_image.setGeometry(QtCore.QRect(120, 70, 491, 20))
        self.label_infos_image.setAlignment(QtCore.Qt.AlignCenter)
        self.label_infos_image.setObjectName("label_infos_image")
        self.horizontalSlider = QtGui.QSlider(self.tab_acq)
        self.horizontalSlider.setGeometry(QtCore.QRect(130, 50, 281, 16))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.Bouton_Echelle = QtGui.QPushButton(self.tab_acq)
        self.Bouton_Echelle.setEnabled(False)
        self.Bouton_Echelle.setGeometry(QtCore.QRect(300, 20, 101, 26))
        self.Bouton_Echelle.setObjectName("Bouton_Echelle")
        self.spinBox_image = QtGui.QSpinBox(self.tab_acq)
        self.spinBox_image.setGeometry(QtCore.QRect(130, 20, 51, 26))
        self.spinBox_image.setMinimumSize(QtCore.QSize(51, 26))
        self.spinBox_image.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_image.setObjectName("spinBox_image")
        self.label_numero_image = QtGui.QLabel(self.tab_acq)
        self.label_numero_image.setGeometry(QtCore.QRect(120, 0, 61, 26))
        self.label_numero_image.setAutoFillBackground(False)
        self.label_numero_image.setAlignment(QtCore.Qt.AlignCenter)
        self.label_numero_image.setObjectName("label_numero_image")
        self.spinBox_nb_de_points = QtGui.QSpinBox(self.tab_acq)
        self.spinBox_nb_de_points.setGeometry(QtCore.QRect(560, 40, 51, 26))
        self.spinBox_nb_de_points.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_nb_de_points.setMinimum(1)
        self.spinBox_nb_de_points.setMaximum(10)
        self.spinBox_nb_de_points.setObjectName("spinBox_nb_de_points")
        self.label_2 = QtGui.QLabel(self.tab_acq)
        self.label_2.setGeometry(QtCore.QRect(530, 0, 121, 41))
        self.label_2.setObjectName("label_2")
        self.echelleEdit = QtGui.QLineEdit(self.tab_acq)
        self.echelleEdit.setGeometry(QtCore.QRect(400, 20, 55, 26))
        self.echelleEdit.setMinimumSize(QtCore.QSize(55, 26))
        self.echelleEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.echelleEdit.setReadOnly(True)
        self.echelleEdit.setObjectName("echelleEdit")
        self.label_4 = QtGui.QLabel(self.tab_acq)
        self.label_4.setGeometry(QtCore.QRect(460, 20, 31, 26))
        self.label_4.setObjectName("label_4")
        self.Bouton_lance_capture = QtGui.QPushButton(self.tab_acq)
        self.Bouton_lance_capture.setGeometry(QtCore.QRect(660, 110, 141, 26))
        self.Bouton_lance_capture.setObjectName("Bouton_lance_capture")
        self.pushButton_reinit = QtGui.QPushButton(self.tab_acq)
        self.pushButton_reinit.setGeometry(QtCore.QRect(660, 210, 131, 25))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(148, 151, 153))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(138, 143, 148))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.pushButton_reinit.setPalette(palette)
        self.pushButton_reinit.setObjectName("pushButton_reinit")
        self.pushButton_defait = QtGui.QPushButton(self.tab_acq)
        self.pushButton_defait.setEnabled(False)
        self.pushButton_defait.setGeometry(QtCore.QRect(680, 150, 31, 25))
        self.pushButton_defait.setObjectName("pushButton_defait")
        self.pushButton_refait = QtGui.QPushButton(self.tab_acq)
        self.pushButton_refait.setEnabled(False)
        self.pushButton_refait.setGeometry(QtCore.QRect(740, 150, 31, 25))
        self.pushButton_refait.setObjectName("pushButton_refait")
        self.label_zoom = QtGui.QLabel(self.tab_acq)
        self.label_zoom.setEnabled(True)
        self.label_zoom.setGeometry(QtCore.QRect(10, 0, 100, 100))
        self.label_zoom.setAutoFillBackground(True)
        self.label_zoom.setObjectName("label_zoom")
        self.checkBox_avancees = QtGui.QCheckBox(self.tab_acq)
        self.checkBox_avancees.setGeometry(QtCore.QRect(660, 350, 141, 41))
        self.checkBox_avancees.setAutoRepeat(False)
        self.checkBox_avancees.setObjectName("checkBox_avancees")
        self.pushButton_origine = QtGui.QPushButton(self.tab_acq)
        self.pushButton_origine.setEnabled(True)
        self.pushButton_origine.setGeometry(QtCore.QRect(660, 410, 161, 51))
        self.pushButton_origine.setFlat(False)
        self.pushButton_origine.setObjectName("pushButton_origine")
        self.label_axe = QtGui.QLabel(self.tab_acq)
        self.label_axe.setGeometry(QtCore.QRect(660, 490, 181, 20))
        self.label_axe.setObjectName("label_axe")
        self.checkBox_abscisses = QtGui.QCheckBox(self.tab_acq)
        self.checkBox_abscisses.setGeometry(QtCore.QRect(660, 520, 181, 22))
        self.checkBox_abscisses.setObjectName("checkBox_abscisses")
        self.checkBox_ordonnees = QtGui.QCheckBox(self.tab_acq)
        self.checkBox_ordonnees.setGeometry(QtCore.QRect(660, 550, 161, 22))
        self.checkBox_ordonnees.setObjectName("checkBox_ordonnees")
        self.tabWidget.addTab(self.tab_acq, "")
        self.tab_traj = QtGui.QWidget()
        self.tab_traj.setObjectName("tab_traj")
        self.label_3 = QtGui.QLabel(self.tab_traj)
        self.label_3.setGeometry(QtCore.QRect(10, 110, 640, 480))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(194, 197, 196))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(194, 197, 196))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(194, 197, 196))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(194, 197, 196))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.label_3.setPalette(palette)
        self.label_3.setCursor(QtCore.Qt.ArrowCursor)
        self.label_3.setAutoFillBackground(True)
        self.label_3.setObjectName("label_3")
        self.layoutWidget = QtGui.QWidget(self.tab_traj)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 10, 631, 95))
        self.layoutWidget.setObjectName("layoutWidget")
        self.hboxlayout1 = QtGui.QHBoxLayout(self.layoutWidget)
        self.hboxlayout1.setObjectName("hboxlayout1")
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setObjectName("vboxlayout")
        self.label_7 = QtGui.QLabel(self.layoutWidget)
        self.label_7.setObjectName("label_7")
        self.vboxlayout.addWidget(self.label_7)
        self.comboBox_referentiel = QtGui.QComboBox(self.layoutWidget)
        self.comboBox_referentiel.setMinimumSize(QtCore.QSize(130, 25))
        self.comboBox_referentiel.setObjectName("comboBox_referentiel")
        self.vboxlayout.addWidget(self.comboBox_referentiel)
        self.hboxlayout1.addLayout(self.vboxlayout)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")
        self.button_video = QtGui.QPushButton(self.layoutWidget)
        self.button_video.setObjectName("button_video")
        self.vboxlayout1.addWidget(self.button_video)
        self.comboBox_fps = QtGui.QComboBox(self.layoutWidget)
        self.comboBox_fps.setObjectName("comboBox_fps")
        self.comboBox_fps.addItem("")
        self.comboBox_fps.addItem("")
        self.comboBox_fps.addItem("")
        self.comboBox_fps.addItem("")
        self.vboxlayout1.addWidget(self.comboBox_fps)
        self.hboxlayout1.addLayout(self.vboxlayout1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, -1, 0, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_8 = QtGui.QLabel(self.layoutWidget)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_2.addWidget(self.label_8)
        self.comboBox_mode_tracer = QtGui.QComboBox(self.layoutWidget)
        self.comboBox_mode_tracer.setObjectName("comboBox_mode_tracer")
        self.comboBox_mode_tracer.addItem("")
        self.verticalLayout_2.addWidget(self.comboBox_mode_tracer)
        self.hboxlayout1.addLayout(self.verticalLayout_2)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem2)
        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setObjectName("vboxlayout2")
        self.label_5 = QtGui.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.vboxlayout2.addWidget(self.label_5)
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")
        self.echelle_v = QtGui.QComboBox(self.layoutWidget)
        self.echelle_v.setMinimumSize(QtCore.QSize(61, 25))
        self.echelle_v.setEditable(True)
        self.echelle_v.setObjectName("echelle_v")
        self.hboxlayout2.addWidget(self.echelle_v)
        self.label_6 = QtGui.QLabel(self.layoutWidget)
        self.label_6.setObjectName("label_6")
        self.hboxlayout2.addWidget(self.label_6)
        self.vboxlayout2.addLayout(self.hboxlayout2)
        self.hboxlayout1.addLayout(self.vboxlayout2)
        self.tabWidget.addTab(self.tab_traj, "")
        self.tab_coord = QtGui.QWidget()
        self.tab_coord.setObjectName("tab_coord")
        self.pushButton_select_all_table = QtGui.QPushButton(self.tab_coord)
        self.pushButton_select_all_table.setGeometry(QtCore.QRect(40, 40, 241, 25))
        self.pushButton_select_all_table.setObjectName("pushButton_select_all_table")
        self.tabWidget.addTab(self.tab_coord, "")
        self.hboxlayout.addWidget(self.tabWidget)
        pymecavideo.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(pymecavideo)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 865, 23))
        self.menubar.setObjectName("menubar")
        self.menuFichier = QtGui.QMenu(self.menubar)
        self.menuFichier.setObjectName("menuFichier")
        self.menuAide = QtGui.QMenu(self.menubar)
        self.menuAide.setObjectName("menuAide")
        self.menu_dition = QtGui.QMenu(self.menubar)
        self.menu_dition.setObjectName("menu_dition")
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
        self.actionRouvrirMecavideo = QtGui.QAction(pymecavideo)
        self.actionRouvrirMecavideo.setObjectName("actionRouvrirMecavideo")
        self.actionPreferences = QtGui.QAction(pymecavideo)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionCopier_dans_le_presse_papier = QtGui.QAction(pymecavideo)
        self.actionCopier_dans_le_presse_papier.setObjectName("actionCopier_dans_le_presse_papier")
        self.menuFichier.addAction(self.actionOuvrir_un_fichier)
        self.menuFichier.addAction(self.actionRouvrirMecavideo)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.actionCopier_dans_le_presse_papier)
        self.menuFichier.addAction(self.actionSaveData)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.actionQuitter)
        self.menuAide.addAction(self.actionAide)
        self.menuAide.addAction(self.actionExemples)
        self.menuAide.addSeparator()
        self.menuAide.addAction(self.action_propos)
        self.menu_dition.addAction(self.actionPreferences)
        self.menubar.addAction(self.menuFichier.menuAction())
        self.menubar.addAction(self.menu_dition.menuAction())
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
        self.label_2.setText(QtGui.QApplication.translate("pymecavideo", "Nombre de points \n"
" à étudier", None, QtGui.QApplication.UnicodeUTF8))
        self.echelleEdit.setText(QtGui.QApplication.translate("pymecavideo", "indéf.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("pymecavideo", "px/m", None, QtGui.QApplication.UnicodeUTF8))
        self.Bouton_lance_capture.setText(QtGui.QApplication.translate("pymecavideo", "Démarrer l\'acquisition", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_reinit.setText(QtGui.QApplication.translate("pymecavideo", "Tout réinitialiser", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_defait.setToolTip(QtGui.QApplication.translate("pymecavideo", "efface la série précédente", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_refait.setToolTip(QtGui.QApplication.translate("pymecavideo", "rétablit le point suivant", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_avancees.setText(QtGui.QApplication.translate("pymecavideo", " Activer \n"
" les fonctionnalités \n"
" avancées", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_origine.setText(QtGui.QApplication.translate("pymecavideo", "Définir une autre origine", None, QtGui.QApplication.UnicodeUTF8))
        self.label_axe.setText(QtGui.QApplication.translate("pymecavideo", "Changer le système d\'axes", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_abscisses.setText(QtGui.QApplication.translate("pymecavideo", "Abscisses vers la gauche", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ordonnees.setText(QtGui.QApplication.translate("pymecavideo", "Ordonnées vers le bas", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_acq), QtGui.QApplication.translate("pymecavideo", "Acquisition des données", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("pymecavideo", "Origine du référentiel :", None, QtGui.QApplication.UnicodeUTF8))
        self.button_video.setText(QtGui.QApplication.translate("pymecavideo", "Vidéo calculée", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_fps.setItemText(0, QtGui.QApplication.translate("pymecavideo", "V. normale", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_fps.setItemText(1, QtGui.QApplication.translate("pymecavideo", "ralenti /2", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_fps.setItemText(2, QtGui.QApplication.translate("pymecavideo", "ralenti /4", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_fps.setItemText(3, QtGui.QApplication.translate("pymecavideo", "ralenti /8", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("pymecavideo", "Graphique :", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_mode_tracer.setItemText(0, QtGui.QApplication.translate("pymecavideo", "Choisir ...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("pymecavideo", "Échelle de vitesses :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("pymecavideo", "px pour 1 m/s", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_traj), QtGui.QApplication.translate("pymecavideo", "trajectoires", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_select_all_table.setText(QtGui.QApplication.translate("pymecavideo", "Copier les mesures dans le presse papier", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_coord), QtGui.QApplication.translate("pymecavideo", "Coordonnées", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFichier.setTitle(QtGui.QApplication.translate("pymecavideo", "Fichier", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAide.setTitle(QtGui.QApplication.translate("pymecavideo", "Aide", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_dition.setTitle(QtGui.QApplication.translate("pymecavideo", "Édition", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOuvrir_un_fichier.setText(QtGui.QApplication.translate("pymecavideo", "Ouvrir une vidéo", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAvanceimage.setText(QtGui.QApplication.translate("pymecavideo", "avanceimage", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReculeimage.setText(QtGui.QApplication.translate("pymecavideo", "reculeimage", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuitter.setText(QtGui.QApplication.translate("pymecavideo", "Quitter", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSaveData.setText(QtGui.QApplication.translate("pymecavideo", "Enregistrer les données", None, QtGui.QApplication.UnicodeUTF8))
        self.action_propos.setText(QtGui.QApplication.translate("pymecavideo", "À propos", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAide.setText(QtGui.QApplication.translate("pymecavideo", "Aide", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExemples.setText(QtGui.QApplication.translate("pymecavideo", "Exemples ...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRouvrirMecavideo.setText(QtGui.QApplication.translate("pymecavideo", "Rouvrir un fichier mecavidéo", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setText(QtGui.QApplication.translate("pymecavideo", "Préférences", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopier_dans_le_presse_papier.setText(QtGui.QApplication.translate("pymecavideo", "copier dans le presse-papier", None, QtGui.QApplication.UnicodeUTF8))

