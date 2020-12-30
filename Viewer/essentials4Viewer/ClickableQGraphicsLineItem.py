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
from Viewer.essentials4Viewer.PressureFlowViewer import PressureFlowViewer


class ClickableQGraphicsLineItem(QtWidgets.QGraphicsLineItem):
    def __init__(self, parent=None):
        QtWidgets.QGraphicsLineItem.__init__(self)
        self.parent = parent
        self.data4element = None
        self.dataPointer = 0
        self.ViewerDFWindow = None
        self.text = None
        self.symbols = None

    def mousePressEvent(self, mouseEvent):
        if mouseEvent.button() == QtCore.Qt.LeftButton:
            self.ViewerDFWindow = PressureFlowViewer(self.data4element, self.parent)
            self.ViewerDFWindow.show()
        if mouseEvent.button() == QtCore.Qt.RightButton:
            if self.text.isVisible():
                self.data4element["showName"] = False
                self.parent.elements[self.dataPointer]["showName"] = False
                self.text.hide()
            else:
                self.data4element["showName"] = True
                self.parent.elements[self.dataPointer]["showName"] = True
                self.text.show()
