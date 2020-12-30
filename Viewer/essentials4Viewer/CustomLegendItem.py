'''
    part of flow network result viewer
'''

__author__ = ('John Gerick',) # alphabetical order of surnames
__credits__ = ('Tom Streubel',) # alphabetical order of surnames


'''
    imports
    =======
'''
from pyqtgraph.graphicsItems.GraphicsWidget import GraphicsWidget
from pyqtgraph.graphicsItems.LabelItem import LabelItem
from PyQt5 import QtGui, QtCore, QtWidgets
from pyqtgraph import functions as fn
from pyqtgraph.Point import Point
from pyqtgraph.graphicsItems.ScatterPlotItem import ScatterPlotItem, drawSymbol
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem
from pyqtgraph.graphicsItems.GraphicsWidgetAnchor import GraphicsWidgetAnchor

__all__ = ['CustomLegendItem']


class CustomLegendItem(GraphicsWidget, GraphicsWidgetAnchor):


    def __init__(self, size=None, offset=None):
        GraphicsWidget.__init__(self)
        GraphicsWidgetAnchor.__init__(self)
        self.setFlag(self.ItemIgnoresTransformations)
        self.layout = QtGui.QGraphicsGridLayout()
        self.layout.setAlignment(self.layout, QtCore.Qt.AlignLeft)
        self.setLayout(self.layout)
        self.items = []
        self.size = size
        self.offset = offset
        if size is not None:
            self.setGeometry(QtCore.QRectF(0, 0, self.size[0], self.size[1]))

    def setParentItem(self, p):
        ret = GraphicsWidget.setParentItem(self, p)
        if self.offset is not None:
            offset = Point(self.offset)
            anchorx = 1 if offset[0] <= 0 else 0
            anchory = 1 if offset[1] <= 0 else 0
            anchor = (anchorx, anchory)
            self.anchor(itemPos=anchor, parentPos=anchor, offset=offset)
        return ret

    def addItem(self, item, name):
        label = LabelItem(name, justify="left", color=[0,0,0])
        emptyLabel = LabelItem("")
        if isinstance(item, ItemSample):
            sample = item
        else:
            sample = ItemSample(item)
        row = self.layout.rowCount()
        self.items.append((sample, label))
        self.layout.addItem(sample, row, 0)
        self.layout.addItem(emptyLabel,row,1)
        self.layout.addItem(label, row, 2)
        self.updateSize()

    def removeItem(self, name):
        # Thanks, Ulrich!
        # cycle for a match
        for sample, label in self.items:
            if label.text == name:  # hit
                self.items.remove((sample, label))  # remove from itemlist
                self.layout.removeItem(sample)  # remove from layout
                sample.close()  # remove from drawing
                self.layout.removeItem(label)
                label.close()
                self.updateSize()  # redraq box

    def updateSize(self):
        if self.size is not None:
            return

        height = 0
        width = 0
        # print("-------")
        for sample, label in self.items:
            height += max(sample.height(), label.height()) + 3
            width = max(width, sample.width() + label.width())
            # print(width, height)
        # print width, height
        self.setGeometry(0, 0, width + 25, height)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.width(), self.height())

    def paint(self, p, *args):
        p.setPen(fn.mkPen(255, 255, 255, 0))
        p.setBrush(fn.mkBrush(100, 100, 100, 0))
        p.drawRect(self.boundingRect())

    def hoverEvent(self, ev):
        pass
        #ev.acceptDrags(QtCore.Qt.LeftButton)

    def mouseDragEvent(self, ev):
        pass
        #if ev.button() == QtCore.Qt.LeftButton:
        #    dpos = ev.pos() - ev.lastPos()
        #    self.autoAnchor(self.pos() + dpos)


class ItemSample(GraphicsWidget):
    def __init__(self, item):
        GraphicsWidget.__init__(self)
        self.item = item

    def boundingRect(self):
        return QtCore.QRectF(0, 0, 20, 20)

    def paint(self, p, *args):
        # p.setRenderHint(p.Antialiasing)  # only if the data is antialiased.
        opts = self.item.opts

        if opts.get('fillLevel', None) is not None and opts.get('fillBrush', None) is not None:
            p.setBrush(fn.mkBrush(opts['fillBrush']))
            p.setPen(fn.mkPen(None))
            p.drawPolygon(QtGui.QPolygonF([QtCore.QPointF(2, 18), QtCore.QPointF(2, 2), QtCore.QPointF(18, 2), QtCore.QPointF(18, 18)]))

        if not isinstance(self.item, ScatterPlotItem):
            p.setPen(fn.mkPen(opts['pen']))
            p.drawLine(2, 18, 18, 2)

        symbol = opts.get('symbol', None)
        if symbol is not None:
            if isinstance(self.item, PlotDataItem):
                opts = self.item.scatter.opts

            pen = fn.mkPen(opts['pen'])
            brush = fn.mkBrush(opts['brush'])
            size = opts['size']

            p.translate(10, 10)
            path = drawSymbol(p, symbol, size, pen, brush)
