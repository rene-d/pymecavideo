# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pymecavideo.ui'
#
# Created: Tue Mar 23 15:52:46 2010
#      by: PyQt4 UI code generator 4.6.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_pymecavideo(object):
    def setupUi(self, pymecavideo):
        pymecavideo.setObjectName("pymecavideo")
        pymecavideo.resize(820, 607)
        font = QtGui.QFont()
        font.setPointSize(9)
        pymecavideo.setFont(font)
        self.centralwidget = QtGui.QWidget(pymecavideo)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(820, 570))
        self.centralwidget.setMaximumSize(QtCore.QSize(820, 570))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setAutoFillBackground(True)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_acq = QtGui.QWidget()
        self.tab_acq.setObjectName("tab_acq")
        self.label = QtGui.QLabel(self.tab_acq)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(158, 45, 640, 480))
        self.label.setMinimumSize(QtCore.QSize(640, 480))
        self.label.setMaximumSize(QtCore.QSize(640, 480))
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
        self.label.setFrameShape(QtGui.QFrame.StyledPanel)
        self.label.setFrameShadow(QtGui.QFrame.Sunken)
        self.label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.label.setObjectName("label")
        self.frame = QtGui.QFrame(self.tab_acq)
        self.frame.setGeometry(QtCore.QRect(150, 2, 651, 41))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label_numero_image = QtGui.QLabel(self.frame)
        self.label_numero_image.setGeometry(QtCore.QRect(10, 10, 61, 26))
        self.label_numero_image.setAutoFillBackground(False)
        self.label_numero_image.setAlignment(QtCore.Qt.AlignCenter)
        self.label_numero_image.setObjectName("label_numero_image")
        self.horizontalSlider = QtGui.QSlider(self.frame)
        self.horizontalSlider.setGeometry(QtCore.QRect(160, 10, 281, 21))
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.spinBox_image = QtGui.QSpinBox(self.frame)
        self.spinBox_image.setGeometry(QtCore.QRect(80, 10, 71, 26))
        self.spinBox_image.setMinimumSize(QtCore.QSize(51, 26))
        self.spinBox_image.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_image.setObjectName("spinBox_image")
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(470, 0, 101, 41))
        self.label_2.setObjectName("label_2")
        self.groupBox_2 = QtGui.QGroupBox(self.tab_acq)
        self.groupBox_2.setEnabled(True)
        self.groupBox_2.setGeometry(QtCore.QRect(1, 365, 150, 150))
        self.groupBox_2.setMinimumSize(QtCore.QSize(150, 150))
        self.groupBox_2.setMaximumSize(QtCore.QSize(150, 200))
        self.groupBox_2.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.checkBox_abscisses = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_abscisses.setGeometry(QtCore.QRect(20, 70, 121, 31))
        self.checkBox_abscisses.setObjectName("checkBox_abscisses")
        self.checkBox_ordonnees = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_ordonnees.setGeometry(QtCore.QRect(20, 110, 111, 31))
        self.checkBox_ordonnees.setObjectName("checkBox_ordonnees")
        self.pushButton_origine = QtGui.QPushButton(self.groupBox_2)
        self.pushButton_origine.setEnabled(True)
        self.pushButton_origine.setGeometry(QtCore.QRect(20, 30, 111, 31))
        self.pushButton_origine.setFlat(False)
        self.pushButton_origine.setObjectName("pushButton_origine")
        self.groupBox_3 = QtGui.QGroupBox(self.tab_acq)
        self.groupBox_3.setGeometry(QtCore.QRect(1, 1, 150, 130))
        self.groupBox_3.setMinimumSize(QtCore.QSize(150, 130))
        self.groupBox_3.setMaximumSize(QtCore.QSize(150, 130))
        self.groupBox_3.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_zoom = QtGui.QLabel(self.groupBox_3)
        self.label_zoom.setEnabled(True)
        self.label_zoom.setGeometry(QtCore.QRect(25, 20, 100, 100))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_zoom.sizePolicy().hasHeightForWidth())
        self.label_zoom.setSizePolicy(sizePolicy)
        self.label_zoom.setMinimumSize(QtCore.QSize(100, 100))
        self.label_zoom.setMaximumSize(QtCore.QSize(100, 100))
        self.label_zoom.setAutoFillBackground(True)
        self.label_zoom.setFrameShape(QtGui.QFrame.StyledPanel)
        self.label_zoom.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_zoom.setObjectName("label_zoom")
        self.groupBox = QtGui.QGroupBox(self.tab_acq)
        self.groupBox.setGeometry(QtCore.QRect(1, 132, 150, 230))
        self.groupBox.setMinimumSize(QtCore.QSize(150, 230))
        self.groupBox.setMaximumSize(QtCore.QSize(150, 230))
        self.groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.setObjectName("groupBox")
        self.Bouton_lance_capture = QtGui.QPushButton(self.groupBox)
        self.Bouton_lance_capture.setGeometry(QtCore.QRect(10, 100, 125, 22))
        self.Bouton_lance_capture.setObjectName("Bouton_lance_capture")
        self.pushButton_defait = QtGui.QPushButton(self.groupBox)
        self.pushButton_defait.setEnabled(False)
        self.pushButton_defait.setGeometry(QtCore.QRect(20, 130, 25, 25))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(25)
        sizePolicy.setVerticalStretch(25)
        sizePolicy.setHeightForWidth(self.pushButton_defait.sizePolicy().hasHeightForWidth())
        self.pushButton_defait.setSizePolicy(sizePolicy)
        self.pushButton_defait.setMinimumSize(QtCore.QSize(25, 25))
        self.pushButton_defait.setMaximumSize(QtCore.QSize(25, 25))
        self.pushButton_defait.setObjectName("pushButton_defait")
        self.pushButton_refait = QtGui.QPushButton(self.groupBox)
        self.pushButton_refait.setEnabled(False)
        self.pushButton_refait.setGeometry(QtCore.QRect(90, 130, 25, 25))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(30)
        sizePolicy.setVerticalStretch(30)
        sizePolicy.setHeightForWidth(self.pushButton_refait.sizePolicy().hasHeightForWidth())
        self.pushButton_refait.setSizePolicy(sizePolicy)
        self.pushButton_refait.setMinimumSize(QtCore.QSize(25, 25))
        self.pushButton_refait.setMaximumSize(QtCore.QSize(25, 25))
        self.pushButton_refait.setObjectName("pushButton_refait")
        self.pushButton_reinit = QtGui.QPushButton(self.groupBox)
        self.pushButton_reinit.setGeometry(QtCore.QRect(10, 160, 125, 22))
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
        self.checkBox_avancees = QtGui.QCheckBox(self.groupBox)
        self.checkBox_avancees.setGeometry(QtCore.QRect(20, 190, 121, 31))
        self.checkBox_avancees.setAutoRepeat(False)
        self.checkBox_avancees.setObjectName("checkBox_avancees")
        self.Bouton_Echelle = QtGui.QPushButton(self.groupBox)
        self.Bouton_Echelle.setEnabled(False)
        self.Bouton_Echelle.setGeometry(QtCore.QRect(10, 20, 125, 22))
        self.Bouton_Echelle.setObjectName("Bouton_Echelle")
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(70, 40, 31, 26))
        self.label_4.setObjectName("label_4")
        self.echelleEdit = QtGui.QLineEdit(self.groupBox)
        self.echelleEdit.setGeometry(QtCore.QRect(10, 40, 55, 26))
        self.echelleEdit.setMinimumSize(QtCore.QSize(55, 26))
        self.echelleEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.echelleEdit.setReadOnly(True)
        self.echelleEdit.setObjectName("echelleEdit")
        self.spinBox_nb_de_points = QtGui.QSpinBox(self.groupBox)
        self.spinBox_nb_de_points.setGeometry(QtCore.QRect(70, 70, 71, 26))
        self.spinBox_nb_de_points.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_nb_de_points.setMinimum(1)
        self.spinBox_nb_de_points.setMaximum(10)
        self.spinBox_nb_de_points.setObjectName("spinBox_nb_de_points")
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(10, 60, 51, 41))
        self.label_5.setObjectName("label_5")
        self.tabWidget.addTab(self.tab_acq, "")
        self.tab_traj = QtGui.QWidget()
        self.tab_traj.setObjectName("tab_traj")
        self.label_3 = QtGui.QLabel(self.tab_traj)
        self.label_3.setGeometry(QtCore.QRect(158, 5, 640, 480))
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
        self.groupBox_4 = QtGui.QGroupBox(self.tab_traj)
        self.groupBox_4.setGeometry(QtCore.QRect(1, 1, 150, 71))
        self.groupBox_4.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_4.setObjectName("groupBox_4")
        self.comboBox_referentiel = QtGui.QComboBox(self.groupBox_4)
        self.comboBox_referentiel.setGeometry(QtCore.QRect(10, 30, 130, 25))
        self.comboBox_referentiel.setMinimumSize(QtCore.QSize(130, 25))
        self.comboBox_referentiel.setObjectName("comboBox_referentiel")
        self.groupBox_5 = QtGui.QGroupBox(self.tab_traj)
        self.groupBox_5.setGeometry(QtCore.QRect(1, 75, 151, 91))
        self.groupBox_5.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_5.setObjectName("groupBox_5")
        self.echelle_v = QtGui.QComboBox(self.groupBox_5)
        self.echelle_v.setGeometry(QtCore.QRect(40, 30, 70, 25))
        self.echelle_v.setMinimumSize(QtCore.QSize(61, 25))
        self.echelle_v.setEditable(True)
        self.echelle_v.setObjectName("echelle_v")
        self.label_6 = QtGui.QLabel(self.groupBox_5)
        self.label_6.setGeometry(QtCore.QRect(30, 50, 91, 24))
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.groupBox_6 = QtGui.QGroupBox(self.tab_traj)
        self.groupBox_6.setGeometry(QtCore.QRect(1, 170, 150, 121))
        self.groupBox_6.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_6.setObjectName("groupBox_6")
        self.comboBox_fps = QtGui.QComboBox(self.groupBox_6)
        self.comboBox_fps.setGeometry(QtCore.QRect(30, 80, 92, 24))
        self.comboBox_fps.setObjectName("comboBox_fps")
        self.comboBox_fps.addItem("")
        self.comboBox_fps.addItem("")
        self.comboBox_fps.addItem("")
        self.comboBox_fps.addItem("")
        self.button_video = QtGui.QPushButton(self.groupBox_6)
        self.button_video.setGeometry(QtCore.QRect(20, 30, 113, 22))
        self.button_video.setObjectName("button_video")
        self.label_8 = QtGui.QLabel(self.groupBox_6)
        self.label_8.setGeometry(QtCore.QRect(50, 60, 57, 15))
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.groupBox_7 = QtGui.QGroupBox(self.tab_traj)
        self.groupBox_7.setGeometry(QtCore.QRect(0, 310, 150, 71))
        self.groupBox_7.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_7.setObjectName("groupBox_7")
        self.comboBox_mode_tracer = QtGui.QComboBox(self.groupBox_7)
        self.comboBox_mode_tracer.setGeometry(QtCore.QRect(30, 30, 87, 20))
        self.comboBox_mode_tracer.setObjectName("comboBox_mode_tracer")
        self.comboBox_mode_tracer.addItem("")
        self.tabWidget.addTab(self.tab_traj, "")
        self.tab_coord = QtGui.QWidget()
        self.tab_coord.setObjectName("tab_coord")
        self.pushButton_select_all_table = QtGui.QPushButton(self.tab_coord)
        self.pushButton_select_all_table.setGeometry(QtCore.QRect(40, 10, 271, 25))
        self.pushButton_select_all_table.setObjectName("pushButton_select_all_table")
        self.tabWidget.addTab(self.tab_coord, "")
        self.gridLayout_2.addWidget(self.tabWidget, 1, 0, 1, 1)
        pymecavideo.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(pymecavideo)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 820, 24))
        self.menubar.setObjectName("menubar")
        self.menuFichier = QtGui.QMenu(self.menubar)
        self.menuFichier.setObjectName("menuFichier")
        self.menuAide = QtGui.QMenu(self.menubar)
        self.menuAide.setObjectName("menuAide")
        self.menu_dition = QtGui.QMenu(self.menubar)
        self.menu_dition.setObjectName("menu_dition")
        pymecavideo.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(pymecavideo)
        self.statusbar.setSizeGripEnabled(False)
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
        self.label_numero_image.setText(QtGui.QApplication.translate("pymecavideo", "Image n°", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("pymecavideo", "Points à étudier:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("pymecavideo", "Changer de repère", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_abscisses.setText(QtGui.QApplication.translate("pymecavideo", "Abscisses \n"
"vers la gauche", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ordonnees.setText(QtGui.QApplication.translate("pymecavideo", "Ordonnées \n"
"vers le bas", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_origine.setText(QtGui.QApplication.translate("pymecavideo", "Définir l\'origine", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("pymecavideo", "Zoom", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("pymecavideo", "Acquisition", None, QtGui.QApplication.UnicodeUTF8))
        self.Bouton_lance_capture.setText(QtGui.QApplication.translate("pymecavideo", "Démarrer", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_defait.setToolTip(QtGui.QApplication.translate("pymecavideo", "efface la série précédente", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_refait.setToolTip(QtGui.QApplication.translate("pymecavideo", "rétablit le point suivant", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_reinit.setText(QtGui.QApplication.translate("pymecavideo", "Tout réinitialiser", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_avancees.setText(QtGui.QApplication.translate("pymecavideo", "Fonctionnalités \n"
" avancées", None, QtGui.QApplication.UnicodeUTF8))
        self.Bouton_Echelle.setText(QtGui.QApplication.translate("pymecavideo", "Définir l\'échelle", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("pymecavideo", "px/m", None, QtGui.QApplication.UnicodeUTF8))
        self.echelleEdit.setText(QtGui.QApplication.translate("pymecavideo", "indéf.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("pymecavideo", "Points à \n"
" étudier:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_acq), QtGui.QApplication.translate("pymecavideo", "Acquisition des données", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("pymecavideo", "Origine du référentiel", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("pymecavideo", "Échelle de vitesses", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("pymecavideo", "px pour 1 m/s", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_6.setTitle(QtGui.QApplication.translate("pymecavideo", "Vidéo calculée", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_fps.setItemText(0, QtGui.QApplication.translate("pymecavideo", "V. normale", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_fps.setItemText(1, QtGui.QApplication.translate("pymecavideo", "ralenti /2", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_fps.setItemText(2, QtGui.QApplication.translate("pymecavideo", "ralenti /4", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_fps.setItemText(3, QtGui.QApplication.translate("pymecavideo", "ralenti /8", None, QtGui.QApplication.UnicodeUTF8))
        self.button_video.setText(QtGui.QApplication.translate("pymecavideo", "Calculer la vidéo", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("pymecavideo", "Vitesse :", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_7.setTitle(QtGui.QApplication.translate("pymecavideo", "Graphique", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_mode_tracer.setItemText(0, QtGui.QApplication.translate("pymecavideo", "Choisir ...", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_traj), QtGui.QApplication.translate("pymecavideo", "Trajectoires", None, QtGui.QApplication.UnicodeUTF8))
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

