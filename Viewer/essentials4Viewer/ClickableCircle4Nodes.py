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


class ClickableCircle4Nodes(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, x, y, size, pointer, parent=None):
        self.parent = parent
        QtWidgets.QGraphicsEllipseItem.__init__(self, x - 0.5 * size, y - 0.5 * size, size, size, parent=None)
        self.x = 0.0
        self.y = 0.0
        self.text = None
        self.dataPointer = pointer

    def mousePressEvent(self, mouseEvent):
        if mouseEvent.button() == QtCore.Qt.RightButton:
            if self.text.isVisible():
                self.text.hide()
                self.parent.nodes[self.dataPointer]["showName"] = False
            else:
                self.text.show()
                self.parent.nodes[self.dataPointer]["showName"] = True
