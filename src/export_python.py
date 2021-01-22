from PyQt5.QtCore import *
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage
from PyQt5.QtWidgets import *

class ExportDialog(QDialog):
    donnees = pyqtSignal(list)
    def __init__(self, *args, **kwargs):
        super(ExportDialog, self).__init__(*args, **kwargs)
        self.setGeometry(QRect(30, 20, 359, 87))
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        
        
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.quitter)
        self.buttonBox.rejected.connect(self.annuler)

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
        
        self.retranslateUi(self)
        
    
    def quitter(self):
        self.donnees.emit([self.checkBox_v.isChecked(), self.checkBox_v2.isChecked(), self.checkBox_accel.isChecked(), self.checkBox_accel2.isChecked()])
        self.close()
        
        #========================================================================
    def annuler(self):
        """annulation de la recherche de données (bouton "Annuler")
           NB: idem pour la fermeture  par la croix ou le menu système 
        """
        self.donnees.emit([None, None])
        self.close()
        
    def retranslateUi(self, choix_exports):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("choix_exports", "Choix export python"))
        self.checkBox_v.setText(_translate("choix_exports", "insérer les lignes pour le calcul des vitesses"))
        self.checkBox_accel.setText(_translate("choix_exports", "insérer les lignespour le calcul des accélérations"))
        self.checkBox_v2.setText(_translate("choix_exports", "insérer les lignes pour l'affichage des vecteurs vitesses"))
        self.checkBox_accel2.setText(_translate("choix_exports", "insérer les lignes pour l'affichage des vecteurs des accélérations"))
