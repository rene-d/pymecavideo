# Sjoerd de Vries, 2017
# partially based on code ported from https://gist.github.com/pavel-perina/1324ff064aedede0e01311aab315f83d, copyright (c) 2017 Pavel Perina

"""
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from PyQt6.QtWidgets import QLayout
from PyQt6.QtCore import Qt, QSize


class AspectLayout(QLayout):
    def __init__(self, aspect):
        self.aspect = aspect
        self.item = None
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item):
        if self.item is not None:
            del (self.item)
            self.item = None
        self.item = item

    def itemAt(self, index):
        if index != 0:
            return None
        if self.item is None:
            return None
        return self.item

    def takeAt(self, index):
        if index != 0:
            return None
        if self.item is None:
            return None
        result = self.item
        self.item = None
        return result

    def setGeometry(self, rect):
        super().setGeometry(rect)
        margins = self.getContentsMargins()
        if self.item is not None:
            availW = rect.width() - margins[1] - margins[3]
            availH = rect.height() - margins[0] - margins[2]
            h = int(availH)
            w = int(h * self.aspect)
            if w > availW:
                x = int(margins[1])
                w = int(availW)
                h = int(w/self.aspect)
                if self.item.alignment() & Qt.AlignTop:
                    y = int(margins[0])
                elif self.item.alignment() & Qt.AlignBottom:
                    y = int(rect.height() - margins[2] - h)
                else:
                    y = int(margins[0] + (availH-h) / 2)
            else:
                y = int(margins[0])
                if self.item.alignment() & Qt.AlignLeft:
                    x = int(margins[1])
                elif self.item.alignment() & Qt.AlignRight:
                    x = int(rect.width() - margins[3] - w)
                else:
                    x = int(margins[1] + (availW-w) / 2)
            self.item.widget().setGeometry(
                int(rect.x() + x),
                int(rect.y() + y),
                int(w), int(h))

    def sizeHint(self):
        margins = self.getContentsMargins()
        if self.item is None:
            return QSize(margins[0]+margins[2], margins[1]+margins[3])
        s = self.item.sizeHint()
        w, h = s.width(), s.height()
        return QSize(margins[0]+margins[2] + w, margins[1]+margins[3] + h)

    def minimumSize(self):
        margins = self.getContentsMargins()
        if self.item is None:
            return QSize(margins[0]+margins[2], margins[1]+margins[3])
        s = self.item.minimumSize()
        w, h = s.width(), s.height()
        return QSize(margins[0]+margins[2] + w, margins[1]+margins[3] + h)

    def expandingDirections(self):
        return Qt.Orientation.Horizontal | Qt.Orientation.Vertical

    def hasHeightForWidth(self):
        return False

    def count(self):
        if self.item is None:
            return 0
        else:
            return 1

    def heightForWidth(self, width):
        margins = self.getContentsMargins()
        height = (width - margins[1] - margins[3]) / self.aspect
        height += margins[0] + margins[2]
        return int(height)
