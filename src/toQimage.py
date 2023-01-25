from PyQt6.QtGui import QImage, qRgb

import numpy as np


class NotImplementedException:
    pass


def toQImage(im, copy=False):
    """transforme une image ope,cv (numpy array) en une QImage"""
    if im is None:
        return QImage()

    if im.dtype == np.uint8:
        if len(im.shape) == 3:
            if im.shape[2] == 3:
                qim = QImage(im.data, im.shape[1],
                             im.shape[0], QImage.Format.Format_RGB888)
                return qim.copy() if copy else qim

    raise NotImplementedException
