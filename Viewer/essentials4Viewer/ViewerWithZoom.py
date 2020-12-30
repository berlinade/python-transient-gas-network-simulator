'''
    part of flow network result viewer
'''

__author__ = ('John Gerick',) # alphabetical order of surnames
__credits__ = ('Tom Streubel',) # alphabetical order of surnames


'''
    imports
    =======
'''
from PyQt5 import QtWidgets


class ViewerWithZoom(QtWidgets.QGraphicsView):
    #add zoom functionality to the QGraphicsView

    def __init__(self, parent):
        super(ViewerWithZoom, self).__init__(parent)
        self._zoom = 0

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.2
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1
        if self._zoom > 0:
            self.scale(factor, factor)
        elif self._zoom < 0:
            self.scale(factor, factor)
