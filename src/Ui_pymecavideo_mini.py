# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pymecavideo_mini.ui'
#
# Created: Sun Apr 15 17:16:02 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_pymecavideo(object):
    def setupUi(self, pymecavideo):
        pymecavideo.setObjectName(_fromUtf8("pymecavideo"))
        pymecavideo.resize(833, 579)
        pymecavideo.setMinimumSize(QtCore.QSize(833, 579))
        pymecavideo.setMaximumSize(QtCore.QSize(833, 579))
        font = QtGui.QFont()
        font.setPointSize(9)
        pymecavideo.setFont(font)
        self.centralwidget = QtGui.QWidget(pymecavideo)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(833, 540))
        self.centralwidget.setMaximumSize(QtCore.QSize(833, 540))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.centralwidget.setFont(font)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setAutoFillBackground(True)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.West)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_acq = QtGui.QWidget()
        self.tab_acq.setObjectName(_fromUtf8("tab_acq"))
        self.label = QtGui.QLabel(self.tab_acq)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(153, 40, 640, 480))
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
        self.label.setObjectName(_fromUtf8("label"))
        self.frame = QtGui.QFrame(self.tab_acq)
        self.frame.setGeometry(QtCore.QRect(150, 2, 641, 34))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label_numero_image = QtGui.QLabel(self.frame)
        self.label_numero_image.setGeometry(QtCore.QRect(170, 0, 81, 26))
        self.label_numero_image.setAutoFillBackground(False)
        self.label_numero_image.setAlignment(QtCore.Qt.AlignCenter)
        self.label_numero_image.setObjectName(_fromUtf8("label_numero_image"))
        self.horizontalSlider = QtGui.QSlider(self.frame)
        self.horizontalSlider.setGeometry(QtCore.QRect(330, 10, 281, 21))
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.spinBox_image = QtGui.QSpinBox(self.frame)
        self.spinBox_image.setGeometry(QtCore.QRect(250, 0, 71, 26))
        self.spinBox_image.setMinimumSize(QtCore.QSize(51, 26))
        self.spinBox_image.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_image.setObjectName(_fromUtf8("spinBox_image"))
        self.pushButton_video = QtGui.QPushButton(self.frame)
        self.pushButton_video.setGeometry(QtCore.QRect(10, 0, 161, 31))
        self.pushButton_video.setObjectName(_fromUtf8("pushButton_video"))
        self.groupBox_3 = QtGui.QGroupBox(self.tab_acq)
        self.groupBox_3.setEnabled(True)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 0, 121, 130))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_3.setMaximumSize(QtCore.QSize(150, 170))
        self.groupBox_3.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_zoom = QtGui.QLabel(self.groupBox_3)
        self.label_zoom.setEnabled(True)
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
        self.label_zoom.setText(_fromUtf8(""))
        self.label_zoom.setObjectName(_fromUtf8("label_zoom"))
        self.verticalLayout_3.addWidget(self.label_zoom)
        self.groupBox = QtGui.QGroupBox(self.tab_acq)
        self.groupBox.setGeometry(QtCore.QRect(0, 140, 150, 210))
        self.groupBox.setMinimumSize(QtCore.QSize(150, 210))
        self.groupBox.setMaximumSize(QtCore.QSize(150, 230))
        self.groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.Bouton_lance_capture = QtGui.QPushButton(self.groupBox)
        self.Bouton_lance_capture.setGeometry(QtCore.QRect(10, 100, 125, 22))
        self.Bouton_lance_capture.setObjectName(_fromUtf8("Bouton_lance_capture"))
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
        self.pushButton_defait.setText(_fromUtf8(""))
        self.pushButton_defait.setObjectName(_fromUtf8("pushButton_defait"))
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
        self.pushButton_refait.setText(_fromUtf8(""))
        self.pushButton_refait.setObjectName(_fromUtf8("pushButton_refait"))
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
        self.pushButton_reinit.setObjectName(_fromUtf8("pushButton_reinit"))
        self.Bouton_Echelle = QtGui.QPushButton(self.groupBox)
        self.Bouton_Echelle.setEnabled(False)
        self.Bouton_Echelle.setGeometry(QtCore.QRect(10, 20, 125, 22))
        self.Bouton_Echelle.setObjectName(_fromUtf8("Bouton_Echelle"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(70, 40, 31, 26))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.echelleEdit = QtGui.QLineEdit(self.groupBox)
        self.echelleEdit.setGeometry(QtCore.QRect(10, 40, 55, 26))
        self.echelleEdit.setMinimumSize(QtCore.QSize(55, 26))
        self.echelleEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.echelleEdit.setReadOnly(True)
        self.echelleEdit.setObjectName(_fromUtf8("echelleEdit"))
        self.spinBox_nb_de_points = QtGui.QSpinBox(self.groupBox)
        self.spinBox_nb_de_points.setGeometry(QtCore.QRect(70, 70, 71, 26))
        self.spinBox_nb_de_points.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_nb_de_points.setMinimum(1)
        self.spinBox_nb_de_points.setMaximum(10)
        self.spinBox_nb_de_points.setObjectName(_fromUtf8("spinBox_nb_de_points"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(10, 60, 51, 41))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.layoutWidget = QtGui.QWidget(self.tab_acq)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 360, 138, 153))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.checkBox_auto = QtGui.QCheckBox(self.layoutWidget)
        self.checkBox_auto.setObjectName(_fromUtf8("checkBox_auto"))
        self.verticalLayout_4.addWidget(self.checkBox_auto)
        self.pushButton_origine = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_origine.setEnabled(True)
        self.pushButton_origine.setFlat(False)
        self.pushButton_origine.setObjectName(_fromUtf8("pushButton_origine"))
        self.verticalLayout_4.addWidget(self.pushButton_origine)
        self.checkBox_abscisses = QtGui.QCheckBox(self.layoutWidget)
        self.checkBox_abscisses.setObjectName(_fromUtf8("checkBox_abscisses"))
        self.verticalLayout_4.addWidget(self.checkBox_abscisses)
        self.checkBox_ordonnees = QtGui.QCheckBox(self.layoutWidget)
        self.checkBox_ordonnees.setObjectName(_fromUtf8("checkBox_ordonnees"))
        self.verticalLayout_4.addWidget(self.checkBox_ordonnees)
        self.tabWidget.addTab(self.tab_acq, _fromUtf8(""))
        self.tab_traj = QtGui.QWidget()
        self.tab_traj.setObjectName(_fromUtf8("tab_traj"))
        self.label_3 = QtGui.QLabel(self.tab_traj)
        self.label_3.setGeometry(QtCore.QRect(153, 40, 640, 480))
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
        self.label_3.setText(_fromUtf8(""))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.groupBox_4 = QtGui.QGroupBox(self.tab_traj)
        self.groupBox_4.setGeometry(QtCore.QRect(0, 60, 141, 321))
        self.groupBox_4.setTitle(_fromUtf8(""))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_4)
        self.verticalLayout.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.checkBoxVectorSpeed = QtGui.QCheckBox(self.groupBox_4)
        self.checkBoxVectorSpeed.setObjectName(_fromUtf8("checkBoxVectorSpeed"))
        self.verticalLayout.addWidget(self.checkBoxVectorSpeed)
        self.radioButtonNearMouse = QtGui.QRadioButton(self.groupBox_4)
        self.radioButtonNearMouse.setChecked(True)
        self.radioButtonNearMouse.setObjectName(_fromUtf8("radioButtonNearMouse"))
        self.verticalLayout.addWidget(self.radioButtonNearMouse)
        self.radioButtonSpeedEveryWhere = QtGui.QRadioButton(self.groupBox_4)
        self.radioButtonSpeedEveryWhere.setObjectName(_fromUtf8("radioButtonSpeedEveryWhere"))
        self.verticalLayout.addWidget(self.radioButtonSpeedEveryWhere)
        self.label_7 = QtGui.QLabel(self.groupBox_4)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout.addWidget(self.label_7)
        self.checkBoxScale = QtGui.QComboBox(self.groupBox_4)
        self.checkBoxScale.setEnabled(False)
        self.checkBoxScale.setMinimumSize(QtCore.QSize(61, 25))
        self.checkBoxScale.setEditable(True)
        self.checkBoxScale.setObjectName(_fromUtf8("checkBoxScale"))
        self.verticalLayout.addWidget(self.checkBoxScale)
        self.label_6 = QtGui.QLabel(self.groupBox_4)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout.addWidget(self.label_6)
        self.line = QtGui.QFrame(self.groupBox_4)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label_2 = QtGui.QLabel(self.groupBox_4)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.comboBox_mode_tracer = QtGui.QComboBox(self.groupBox_4)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_mode_tracer.sizePolicy().hasHeightForWidth())
        self.comboBox_mode_tracer.setSizePolicy(sizePolicy)
        self.comboBox_mode_tracer.setObjectName(_fromUtf8("comboBox_mode_tracer"))
        self.comboBox_mode_tracer.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.comboBox_mode_tracer)
        self.button_video = QtGui.QPushButton(self.tab_traj)
        self.button_video.setGeometry(QtCore.QRect(540, 10, 130, 25))
        self.button_video.setObjectName(_fromUtf8("button_video"))
        self.comboBox_referentiel = QtGui.QComboBox(self.tab_traj)
        self.comboBox_referentiel.setGeometry(QtCore.QRect(400, 10, 130, 25))
        self.comboBox_referentiel.setMinimumSize(QtCore.QSize(130, 25))
        self.comboBox_referentiel.setObjectName(_fromUtf8("comboBox_referentiel"))
        self.label_8 = QtGui.QLabel(self.tab_traj)
        self.label_8.setGeometry(QtCore.QRect(219, 10, 181, 20))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.tabWidget.addTab(self.tab_traj, _fromUtf8(""))
        self.tab_coord = QtGui.QWidget()
        self.tab_coord.setObjectName(_fromUtf8("tab_coord"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_coord)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox_5 = QtGui.QGroupBox(self.tab_coord)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.pushButton_select_all_table = QtGui.QPushButton(self.groupBox_5)
        self.pushButton_select_all_table.setObjectName(_fromUtf8("pushButton_select_all_table"))
        self.horizontalLayout_5.addWidget(self.pushButton_select_all_table)
        self.exportCombo = QtGui.QComboBox(self.groupBox_5)
        self.exportCombo.setObjectName(_fromUtf8("exportCombo"))
        self.exportCombo.addItem(_fromUtf8(""))
        self.exportCombo.addItem(_fromUtf8(""))
        self.exportCombo.addItem(_fromUtf8(""))
        self.exportCombo.addItem(_fromUtf8(""))
        self.horizontalLayout_5.addWidget(self.exportCombo)
        self.pushButton_nvl_echelle = QtGui.QPushButton(self.groupBox_5)
        self.pushButton_nvl_echelle.setObjectName(_fromUtf8("pushButton_nvl_echelle"))
        self.horizontalLayout_5.addWidget(self.pushButton_nvl_echelle)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.groupBox_5)
        self.tableWidget = standardDragTable(self.tab_coord)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tableWidget)
        self.tabWidget.addTab(self.tab_coord, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        pymecavideo.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(pymecavideo)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 833, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFichier = QtGui.QMenu(self.menubar)
        self.menuFichier.setObjectName(_fromUtf8("menuFichier"))
        self.menuE_xporter_vers = QtGui.QMenu(self.menuFichier)
        self.menuE_xporter_vers.setObjectName(_fromUtf8("menuE_xporter_vers"))
        self.menuAide = QtGui.QMenu(self.menubar)
        self.menuAide.setObjectName(_fromUtf8("menuAide"))
        self.menu_dition = QtGui.QMenu(self.menubar)
        self.menu_dition.setObjectName(_fromUtf8("menu_dition"))
        pymecavideo.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(pymecavideo)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        pymecavideo.setStatusBar(self.statusbar)
        self.actionOuvrir_un_fichier = QtGui.QAction(pymecavideo)
        self.actionOuvrir_un_fichier.setShortcut(_fromUtf8("Ctrl+O"))
        self.actionOuvrir_un_fichier.setObjectName(_fromUtf8("actionOuvrir_un_fichier"))
        self.actionAvanceimage = QtGui.QAction(pymecavideo)
        self.actionAvanceimage.setObjectName(_fromUtf8("actionAvanceimage"))
        self.actionReculeimage = QtGui.QAction(pymecavideo)
        self.actionReculeimage.setObjectName(_fromUtf8("actionReculeimage"))
        self.actionQuitter = QtGui.QAction(pymecavideo)
        self.actionQuitter.setShortcut(_fromUtf8("Ctrl+Q"))
        self.actionQuitter.setObjectName(_fromUtf8("actionQuitter"))
        self.actionSaveData = QtGui.QAction(pymecavideo)
        self.actionSaveData.setShortcut(_fromUtf8("Ctrl+S"))
        self.actionSaveData.setObjectName(_fromUtf8("actionSaveData"))
        self.action_propos = QtGui.QAction(pymecavideo)
        self.action_propos.setObjectName(_fromUtf8("action_propos"))
        self.actionAide = QtGui.QAction(pymecavideo)
        self.actionAide.setShortcut(_fromUtf8("F1"))
        self.actionAide.setObjectName(_fromUtf8("actionAide"))
        self.actionExemples = QtGui.QAction(pymecavideo)
        self.actionExemples.setObjectName(_fromUtf8("actionExemples"))
        self.actionRouvrirMecavideo = QtGui.QAction(pymecavideo)
        self.actionRouvrirMecavideo.setObjectName(_fromUtf8("actionRouvrirMecavideo"))
        self.actionPreferences = QtGui.QAction(pymecavideo)
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))
        self.actionCopier_dans_le_presse_papier = QtGui.QAction(pymecavideo)
        self.actionCopier_dans_le_presse_papier.setShortcut(_fromUtf8("Ctrl+C"))
        self.actionCopier_dans_le_presse_papier.setObjectName(_fromUtf8("actionCopier_dans_le_presse_papier"))
        self.actionDefaire = QtGui.QAction(pymecavideo)
        self.actionDefaire.setShortcut(_fromUtf8("Ctrl+Z"))
        self.actionDefaire.setObjectName(_fromUtf8("actionDefaire"))
        self.actionRefaire = QtGui.QAction(pymecavideo)
        self.actionRefaire.setShortcut(_fromUtf8("Ctrl+Y"))
        self.actionRefaire.setObjectName(_fromUtf8("actionRefaire"))
        self.actionOpenOffice_org_Calc = QtGui.QAction(pymecavideo)
        self.actionOpenOffice_org_Calc.setObjectName(_fromUtf8("actionOpenOffice_org_Calc"))
        self.actionQtiplot = QtGui.QAction(pymecavideo)
        self.actionQtiplot.setObjectName(_fromUtf8("actionQtiplot"))
        self.actionScidavis = QtGui.QAction(pymecavideo)
        self.actionScidavis.setObjectName(_fromUtf8("actionScidavis"))
        self.menuE_xporter_vers.addAction(self.actionOpenOffice_org_Calc)
        self.menuE_xporter_vers.addAction(self.actionQtiplot)
        self.menuE_xporter_vers.addAction(self.actionScidavis)
        self.menuFichier.addAction(self.actionOuvrir_un_fichier)
        self.menuFichier.addAction(self.actionRouvrirMecavideo)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.actionCopier_dans_le_presse_papier)
        self.menuFichier.addAction(self.menuE_xporter_vers.menuAction())
        self.menuFichier.addAction(self.actionSaveData)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.actionQuitter)
        self.menuAide.addAction(self.actionAide)
        self.menuAide.addAction(self.actionExemples)
        self.menuAide.addSeparator()
        self.menuAide.addAction(self.action_propos)
        self.menu_dition.addAction(self.actionDefaire)
        self.menu_dition.addAction(self.actionRefaire)
        self.menu_dition.addSeparator()
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
        self.pushButton_video.setText(QtGui.QApplication.translate("pymecavideo", "Acquisition video", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("pymecavideo", "Zoom", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("pymecavideo", "Acquisition", None, QtGui.QApplication.UnicodeUTF8))
        self.Bouton_lance_capture.setText(QtGui.QApplication.translate("pymecavideo", "Démarrer", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_defait.setToolTip(QtGui.QApplication.translate("pymecavideo", "efface la série précédente", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_refait.setToolTip(QtGui.QApplication.translate("pymecavideo", "rétablit le point suivant", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_reinit.setText(QtGui.QApplication.translate("pymecavideo", "Tout réinitialiser", None, QtGui.QApplication.UnicodeUTF8))
        self.Bouton_Echelle.setText(QtGui.QApplication.translate("pymecavideo", "Définir l\'échelle", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("pymecavideo", "px/m", None, QtGui.QApplication.UnicodeUTF8))
        self.echelleEdit.setText(QtGui.QApplication.translate("pymecavideo", "indéf.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("pymecavideo", "Points à \n"
" étudier:", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_auto.setText(QtGui.QApplication.translate("pymecavideo", "suivi\n"
"automatique", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_origine.setText(QtGui.QApplication.translate("pymecavideo", "Changer d\'origine", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_abscisses.setText(QtGui.QApplication.translate("pymecavideo", "Abscisses \n"
"vers la gauche", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ordonnees.setText(QtGui.QApplication.translate("pymecavideo", "Ordonnées \n"
"vers le bas", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_acq), QtGui.QApplication.translate("pymecavideo", "Acquisition des données", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxVectorSpeed.setText(QtGui.QApplication.translate("pymecavideo", "Montrer \n"
"les vecteurs\n"
"vitesses", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonNearMouse.setText(QtGui.QApplication.translate("pymecavideo", "près de\n"
"la souris", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonSpeedEveryWhere.setText(QtGui.QApplication.translate("pymecavideo", "partout", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("pymecavideo", "Échelle de vitesses", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("pymecavideo", "px pour 1 m/s", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("pymecavideo", "Voir un graphique", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_mode_tracer.setItemText(0, QtGui.QApplication.translate("pymecavideo", "Choisir ...", None, QtGui.QApplication.UnicodeUTF8))
        self.button_video.setText(QtGui.QApplication.translate("pymecavideo", "Voir la vidéo", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("pymecavideo", "Définir un autre référentiel : ", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_traj), QtGui.QApplication.translate("pymecavideo", "Trajectoires", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("pymecavideo", "Tableau des dates et des coordonnées", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_select_all_table.setText(QtGui.QApplication.translate("pymecavideo", "Copier les mesures dans le presse papier", None, QtGui.QApplication.UnicodeUTF8))
        self.exportCombo.setItemText(0, QtGui.QApplication.translate("pymecavideo", "Exporter vers ....", None, QtGui.QApplication.UnicodeUTF8))
        self.exportCombo.setItemText(1, QtGui.QApplication.translate("pymecavideo", "Oo.o Calc", None, QtGui.QApplication.UnicodeUTF8))
        self.exportCombo.setItemText(2, QtGui.QApplication.translate("pymecavideo", "Qtiplot", None, QtGui.QApplication.UnicodeUTF8))
        self.exportCombo.setItemText(3, QtGui.QApplication.translate("pymecavideo", "SciDAVis", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_nvl_echelle.setText(QtGui.QApplication.translate("pymecavideo", "changer d\'échelle ?", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_coord), QtGui.QApplication.translate("pymecavideo", "Coordonnées", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFichier.setTitle(QtGui.QApplication.translate("pymecavideo", "&Fichier", None, QtGui.QApplication.UnicodeUTF8))
        self.menuE_xporter_vers.setTitle(QtGui.QApplication.translate("pymecavideo", "E&xporter vers ...", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAide.setTitle(QtGui.QApplication.translate("pymecavideo", "&Aide", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_dition.setTitle(QtGui.QApplication.translate("pymecavideo", "&Edition", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOuvrir_un_fichier.setText(QtGui.QApplication.translate("pymecavideo", "&Ouvrir une vidéo (Ctrl-O)", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAvanceimage.setText(QtGui.QApplication.translate("pymecavideo", "avanceimage", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReculeimage.setText(QtGui.QApplication.translate("pymecavideo", "reculeimage", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuitter.setText(QtGui.QApplication.translate("pymecavideo", "Quitter (Ctrl-Q)", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSaveData.setText(QtGui.QApplication.translate("pymecavideo", "Enregistrer les données (Ctrl-S)", None, QtGui.QApplication.UnicodeUTF8))
        self.action_propos.setText(QtGui.QApplication.translate("pymecavideo", "À &propos", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAide.setText(QtGui.QApplication.translate("pymecavideo", "Aide (F1)", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExemples.setText(QtGui.QApplication.translate("pymecavideo", "Exemples ...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRouvrirMecavideo.setText(QtGui.QApplication.translate("pymecavideo", "Ouvrir un projet &mecavidéo", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setText(QtGui.QApplication.translate("pymecavideo", "&Préférences", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopier_dans_le_presse_papier.setText(QtGui.QApplication.translate("pymecavideo", "&Copier dans le presse-papier (Ctrl-C)", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDefaire.setText(QtGui.QApplication.translate("pymecavideo", "Défaire (Ctrl-Z)", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRefaire.setText(QtGui.QApplication.translate("pymecavideo", "Refaire (Ctrl-Y)", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpenOffice_org_Calc.setText(QtGui.QApplication.translate("pymecavideo", "OpenOffice.org &Calc", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQtiplot.setText(QtGui.QApplication.translate("pymecavideo", "Qti&plot", None, QtGui.QApplication.UnicodeUTF8))
        self.actionScidavis.setText(QtGui.QApplication.translate("pymecavideo", "Sci&davis", None, QtGui.QApplication.UnicodeUTF8))

from standarddragtable import standardDragTable
