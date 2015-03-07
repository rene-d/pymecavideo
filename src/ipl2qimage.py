# -*- coding: utf-8 -*-
licence = {}
licence['en'] = """
    pymecavideo version %s:

    a program to track moving points in a video frameset

    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>

    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>

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

licence['fr'] = u"""
    pymecavideo version %s :

    un programme pour tracer les trajectoires des points dans une vidéo.

    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>

    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>

    Ce projet est un logiciel libre : vous pouvez le redistribuer, le modifier selon les terme de la GPL (GNU Public License) dans les termes de la Free Software Foundation concernant la version 3 ou plus de la dite licence.

    Ce programme est fait avec l'espoir qu'il sera utile mais SANS AUCUNE GARANTIE. Lisez la licence pour plus de détails.

    <http://www.gnu.org/licenses/>.
"""

import cv
from PyQt4.QtGui import *

import Image


def IPLtoPIL(cv_image, swap=True, mode="RGB"):
    """
    converts :class:`IPLImage` to :class:`PILImage`.
    :param cv_image: Input image
    :type cv_image:  :class:`IPLImage`
    :param swap: switch RGB/BGR option
    :type swap: bool
    :param mode: color mode
    :type mode: string

    :return: output image
    :rtype: PILImage

    """

    # swaps RGB/BGR

    if (swap):
        copy_image = cv.CreateImage(cv.GetSize(cv_image), cv_image.depth,
                                    cv_image.nChannels)
        cv.CvtColor(cv_image, copy_image, cv.CV_RGB2BGR)
    else:
        copy_image = cv_image
    return Image.fromstring(mode, cv.GetSize(copy_image), copy_image.tostring())


def IPLtoQPixmap(cv_image, swap=True, mode="RGB"):
    """
    converts :class:`IPLImage` to :class:`QPixmap`.
    :param cv_image: input image
    :type cv_image: :class:`IPLImage`
    :param swap: switch RGB/BGR option
    :type swap: bool
    :param mode: color mode
    :type mode: string

    :return: output image

    :rtype: :class:`QPixmap`

    """

    PILstring = IPLtoPIL(cv_image, swap).convert(mode).tostring()
    qimg = QImage(PILstring,
                  cv_image.width,
                  cv_image.height,
                  cv_image.width * 3,
                  QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimg)
    print pixmap.size()
    return pixmap


def PILtoQPixmap(pil_image, swap=True, encoder="jpeg", mode="RGB"):
    """
    converts :class:`PILImage` to :class:`QPixmap`.

    :param cv_image: input image
    :type cv_image: :class:`PILImage`
    :param swap: switch RGB/BGR option
    :type swap: bool
    :param mode: color mode
    :type mode: string

    :return: output image

    :rtype: :class:`QPixmap`.

    """
    # print pil_image
    PILstring = pil_image.convert(mode).tostring()
    #print "#########",pil_image.size[1], pil_image.size[0]
    qimg = QImage(PILstring,
                  pil_image.size[0],
                  pil_image.size[1],
                  pil_image.size[0] * 3,
                  QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimg)
    return pixmap