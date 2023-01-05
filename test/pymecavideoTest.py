import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QPoint
from src import pymecavideo
from src.echelle import EchelleWidget

class PymecavideoTest(unittest.TestCase):
    '''Test the pymecavideo GUI'''
    def setUp(self):
        '''Create the GUI'''
        self.w = pymecavideo.FenetrePrincipale()
        return
    
    def test_defaults(self):
        '''Teste les états par défaut de l'interface graphique'''
        # Le numéro d'image vaut 1 si une vidéo a été chargée par exemple
        # parce qu'il y avait des données de préférence
        if hasattr(self.w, "imageAffichee"):
            self.assertEqual(self.w.spinBox_image.value(), 1)
        else:
            self.assertEqual(self.w.spinBox_image.value(), 0)
        # le slider associé au spinbox précédent est à 1
        self.assertEqual(self.w.horizontalSlider.value(), 1)
        # le nombre de points à suivre
        self.assertEqual(self.w.spinBox_nb_de_points.value(), 1)
        # la ligne d'édition de la masse d'objet
        self.assertEqual(self.w.lineEdit_m.text(), "1.0")
        # la ligne d'édition de la gravité
        self.assertEqual(self.w.lineEdit_g.text(), "9.8")
        return

    def test_Echelle(self):
        """
        Teste la mise interactive à l'échelle
        """
        start = QPoint(100,100)
        end   = QPoint(600,100)
        # le bouton d'échelle est censé être actif mais on ne le cliquera pas
        self.assertEqual(self.w.Bouton_Echelle.isEnabled(), True)
        # l'application est censée "croire" que l'étalon fait 1 mètre
        self.assertEqual(self.w.video.echelle_image.longueur_reelle_etalon,1)
        # on démarre un widget EchelleWidget, puis on simule un tirer-glisser
        job = EchelleWidget(self.w.video, self.w)
        job.show()
        QTest.mousePress(job, Qt.LeftButton, pos = start)
        QTest.mouseMove(job, pos = end)
        QTest.mouseRelease(job, Qt.LeftButton, pos = end)
        # à ce stade le widget est fermé et une nouvelle échelle 500 px/m
        # doit être affichée
        newEchelle = float(self.w.echelleEdit.text())
        self.assertEqual(newEchelle, 500)
        # on recommence, mais on tire-glisse sur place (=> distance nulle)
        job = EchelleWidget(self.w.video, self.w)
        job.show()
        QTest.mousePress(job, Qt.LeftButton, pos = start)
        QTest.mouseRelease(job, Qt.LeftButton, pos = start)
        # à ce stade le widget est fermé et la nouvelle échelle doit
        # être indéfinie.
        newEchelle = self.w.echelleEdit.text()
        self.assertEqual(newEchelle, "indéf.")
        
        return

# il faut créer l'application même si le module n'est pas __main__
# sinon le PymecavideoTest.setUp ne fonctionnera pas.
app = QApplication(sys.argv)

if __name__ == "__main__":
    unittest.main(verbosity=2)
       
