'''
    part of flow network result viewer
'''

__author__ = ('John Gerick',) # alphabetical order of surnames
__credits__ = ('Tom Streubel',) # alphabetical order of surnames


'''
    imports
    =======
'''
from PyQt5 import QtWidgets, QtGui, QtCore
from math import sqrt


class CircleWithCross(QtWidgets.QGraphicsItemGroup):
    def __init__(self, x1, x2, y1, y2, lineThickness, grFaktor, parent=None):
        QtWidgets.QGraphicsItemGroup.__init__(self)
        self.parent = parent
        correction = 0.85
        rx = (x1 - x2)
        ry = (y1 - y2)
        nx = rx / max(sqrt(rx ** 2 + ry ** 2), 0.1)
        ny = ry / max(sqrt(rx ** 2 + ry ** 2), 0.1)
        mx1 = (x1 + x2) * 0.5 - ny * grFaktor * correction - 0.5 * nx * grFaktor * correction
        my1 = (y1 + y2) * 0.5 + nx * grFaktor * correction - 0.5 * ny * grFaktor * correction
        mx2 = (x1 + x2) * 0.5 + ny * grFaktor * correction - 0.5 * nx * grFaktor * correction
        my2 = (y1 + y2) * 0.5 - nx * grFaktor * correction - 0.5 * ny * grFaktor * correction
        mx3 = (x1 + x2) * 0.5 + ny * grFaktor * correction + 0.5 * nx * grFaktor * correction
        my3 = (y1 + y2) * 0.5 - nx * grFaktor * correction + 0.5 * ny * grFaktor * correction
        mx4 = (x1 + x2) * 0.5 - ny * grFaktor * correction + 0.5 * nx * grFaktor * correction
        my4 = (y1 + y2) * 0.5 + nx * grFaktor * correction + 0.5 * ny * grFaktor * correction
        circle = QtWidgets.QGraphicsEllipseItem((x1 + x2) * 0.5 - grFaktor,
                                                (y1 + y2) * 0.5 - grFaktor,
                                                2.0 * grFaktor,
                                                2.0 * grFaktor,
                                                parent=parent)
        circle.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0, 255),
                                 lineThickness,
                                 QtCore.Qt.SolidLine))
        circle.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 255), QtCore.Qt.SolidPattern))
        line1 = QtWidgets.QGraphicsLineItem(mx1, my1, mx3, my3)
        line1.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0, 255),
                                 lineThickness,
                                 QtCore.Qt.SolidLine))
        line2 = QtWidgets.QGraphicsLineItem(mx2, my2, mx4, my4)
        line2.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0, 255),
                                 lineThickness,
                                 QtCore.Qt.SolidLine))
        self.addToGroup(circle)
        self.addToGroup(line1)
        self.addToGroup(line2)
