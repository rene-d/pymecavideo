import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pointage import Pointage
from vecteur import vecteur

import unittest

# echelle1 est l'échelle pour la vidéo retromars2018
etalon_m1 = 140000000000.0
etalon_org1 = vecteur(503, 377)
etalon_ext1 = vecteur(344, 565)
etalon_px1 = (etalon_ext1-etalon_org1).norme
echelle1 =  etalon_px1 / etalon_m1

# origine1 est l'origine pour la vidéo retromars2018
origine1 = vecteur(503, 377)

# data1 : t, x1, x2, y1, y2 (seconde et mètre), séparés par des TABs
# extrait d'un pointage automatique sur la vidéo retromars2018

data1 ="""\
0,000	-9,02927e+10	-1,05474e+11	-2,12768e+11	9,69453e+10
0,100	-1,17699e+11	-8,03423e+10	-1,95994e+11	1,18722e+11
0,200	-1,37259e+11	-4,95814e+10	-1,76435e+11	1,38851e+11
0,300	-1,47323e+11	-1,54658e+10	-1,53463e+11	1,56761e+11
0,400	-1,47323e+11	1,92185e+10	-1,27763e+11	1,71306e+11
0,500	-1,37827e+11	5,33341e+10	-9,97882e+10	1,83047e+11
0,600	-1,19348e+11	8,35264e+10	-7,01645e+10	1,90877e+11
0,700	-9,30788e+10	1,08658e+11	-3,8835e+10	1,95346e+11
0,800	-6,12376e+10	1,26569e+11	-6,9937e+09	1,95346e+11
0,900	-2,54161e+10	1,36633e+11	2,5473e+10	1,91991e+11
1,000	1,20542e+10	1,3777e+11	5,73143e+10	1,83605e+11
1,100	4,89559e+10	1,30492e+11	8,75066e+10	1,71306e+11
1,200	8,2503e+10	1,15368e+11	1,15481e+11	1,54544e+11
1,300	1,10421e+11	9,24534e+10	1,41182e+11	1,34416e+11
1,400	1,31686e+11	6,39668e+10	1,63016e+11	1,10933e+11
1,500	1,43968e+11	3,15001e+10	1,8087e+11	8,46636e+10
1,600	1,47323e+11	-3,12727e+09	1,94289e+11	5,61202e+10
1,700
1,800
1,900
2,000
2,100
2,200
2,300
2,400
"""

class PointageTest(unittest.TestCase):
    '''Test du module pointage'''
    
    def setUp(self):
        return

    def test1(self):
        p=Pointage()
        lignes = data1.strip().replace(",",".").split("\n")
        # on se sert de data1 pour vérifier quelques propriétés
        p.dimensionne(2, 0.1, len(lignes))
        for i, l in enumerate(lignes):
            d = l.strip().split("\t")
            t = float(d[0])
            if len(d) > 1:
                p_terre = vecteur(float(d[1]), float(d[2])) * echelle1
                p_mars  = vecteur(float(d[3]), float(d[4])) * echelle1
                p.pointe(1, p_terre, index = i)
                p.pointe(2, p_mars,  index = i)

        # on vérifie que la terre (objet 1) et la lune ont des trajectoires
        # environ circulaires en comparant le rayon à l'unité astronomique
        # voici les distances de la terre et de la lune :
        distances_ua = {
            1: 1.0,
            2: 1.43}
        # pour ce qui est des vitesses, on est censé parcourir le 24°
        # de 2 * pi * le rayon entre deux images (avec delta_t = 0.1 s)
        # comme les images correcpondent à 15 jours environ
        # pour Mars, il faut diviser par 1.88 (révolution en 1.88 ans)
        vi_ua_par_s = {
            1 : 1.0 * 3.14 / 12 / 0.1,
            2 : 1.43 * 3.14 / 12 / 0.1 / 1.88
        }
        def callback(i, t, j, obj, p, v):
            if p is not None:
                erreur = abs(p.norme / etalon_px1 / distances_ua[obj] - 1.0)
                assert(erreur < 0.18)
            if v is not None:
                erreur = abs((v.norme / etalon_px1 / vi_ua_par_s[obj]) - 1.0)
                assert(erreur < 0.19)
            return
        p.iteration_data(None, callback, unite="px")
        print("GRRRR deuxième méthode")
        for i, t, iter_OPV in p.iter_TOPV():
            for j, obj, p, v in iter_OPV:
                if p is not None:
                    erreur = abs(p.norme / etalon_px1 / distances_ua[obj] \
                                 - 1.0)
                    assert(erreur < 0.18)
                if v is not None:
                    erreur = abs((v.norme / etalon_px1 / vi_ua_par_s[obj]) - 1.0)
                    assert(erreur < 0.19)
        return


if __name__ == "__main__":
    unittest.main(verbosity=2)
