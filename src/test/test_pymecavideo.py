import sys, os
from subprocess import call

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import unittest
from time import sleep

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QPoint
from src import pymecavideo
from src.echelle import EchelleWidget
from globdef import VIDEO_PATH

# il faut créer l'application même si le module n'est pas __main__
# sinon le PymecavideoTest.setUp ne fonctionnera pas.
app = QApplication(sys.argv)

class PymecavideoTest(unittest.TestCase):
    '''Test the pymecavideo GUI'''
    def setUp(self):
        '''Create the GUI'''
        call ("rm -rf ~/.local/share/pymecavideo/*", shell=True)
        self.w = pymecavideo.FenetrePrincipale()
        self.w.changeEtat("debut")
        self.w.show()
        return

    def tearDown(self):
        '''shutdown the GUI'''
        self.w.close()
        return
    
    def test_defaults(self):
        '''Teste les états par défaut de l'interface graphique'''
        # Le numéro d'image vaut 1 si une vidéo a été chargée par exemple
        # parce qu'il y avait des données de préférence
        self.w.changeEtat("debut")
        self.assertEqual(self.w.pointage.spinBox_image.value(), 1)
        # le slider associé au spinbox précédent est à 1
        self.assertEqual(self.w.pointage.horizontalSlider.value(), 1)
        # le nombre de points à suivre
        self.assertEqual(self.w.pointage.spinBox_objets.value(), 1)
        # la ligne d'édition de la masse d'objet
        self.assertEqual(self.w.graph.lineEdit_m.text(), "1.0")
        # la ligne d'édition de la gravité
        self.assertEqual(self.w.graph.lineEdit_g.text(), "9.8")
        return

    def test_Echelle(self):
        """
        Teste la mise interactive à l'échelle
        """
        start = QPoint(100,100)
        end   = QPoint(600,100)
        # dans un premier temps, on enlève tout fichier de configuration
        # préexistant
        self.w.changeEtat("debut")
        # alors, l'étalon est forcément indéfini
        self.assertEqual(self.w.pointage.echelleEdit.text(), "indéf.")
        # ensuite on charge le fichier
        # f"{VIDEO_PATH}/Principe_inertie.avi"
        self.w.pointage.openTheFile(f"{VIDEO_PATH}/Principe_inertie.avi")
        # l'application est censée "croire" que l'étalon fait 1 mètre
        self.assertEqual(self.w.pointage.echelle_image.longueur_reelle_etalon,1)
        # on démarre un widget EchelleWidget, puis on simule un tirer-glisser
        job = EchelleWidget(self.w.pointage.video, self.w.pointage)
        job.show()
        QTest.mousePress(job, Qt.MouseButton.LeftButton, pos = start)
        QTest.mouseMove(job, pos = end)
        self.w.pointage.etat_ancien = "A"
        QTest.mouseRelease(job, Qt.MouseButton.LeftButton, pos = end)
        # à ce stade le widget est fermé et une nouvelle échelle 500 px/m
        # doit être affichée
        newEchelle = float(self.w.pointage.echelleEdit.text())
        self.assertEqual(newEchelle, 500)
        # on recommence, mais on tire-glisse sur place (=> distance nulle)
        job = EchelleWidget(self.w.pointage.video, self.w.pointage)
        job.show()
        QTest.mousePress(job, Qt.MouseButton.LeftButton, pos = start)
        QTest.mouseRelease(job, Qt.MouseButton.LeftButton, pos = start)
        # à ce stade le widget est fermé et la nouvelle échelle doit
        # être indéfinie.
        newEchelle = self.w.pointage.echelleEdit.text()
        self.assertEqual(newEchelle, "indéf.")
        
        return

if __name__ == "__main__":
    unittest.main(verbosity=2)
    app.exec()
       
