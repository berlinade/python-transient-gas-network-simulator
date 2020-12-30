'''
    part of flow network result viewer
'''

__author__ = ('John Gerick',) # alphabetical order of surnames
__credits__ = ('Tom Streubel',) # alphabetical order of surnames


'''
    imports
    =======
'''
from PyQt5 import QtWidgets, QtCore


class Viewer4ColorBar(QtWidgets.QGraphicsView):
    # add special QGraphicsView 4 ColorBar

    def __init__(self, parent):
        super(Viewer4ColorBar, self).__init__(parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        tmpRect = QtCore.QRectF(self.scene().itemsBoundingRect().left() + 5,
                                self.scene().itemsBoundingRect().top() + 5,
                                self.scene().itemsBoundingRect().width() - 10,
                                self.scene().itemsBoundingRect().height() - 10)
        self.fitInView(tmpRect, QtCore.Qt.IgnoreAspectRatio)
