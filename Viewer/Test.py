'''
    part of flow network result viewer
'''

__author__ = ('John Gerick',) # alphabetical order of surnames
__credits__ = ('Tom Streubel',) # alphabetical order of surnames


'''
    imports
    =======
'''
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph


class Test(QtWidgets.QDialog):


    def __init__(self, times4Results, values, elementName, metaDict = None, parent = None):
        super(Test, self).__init__(parent)
        self.initUI(times4Results, values, elementName, metaDict)                                    ## start to initializes the Main Window ##


    def initUI(self,times4Results, values, elementName, metaDict):                                             ## initializes the Main Window ##
        self.windowDFView = QtWidgets.QWidget(self)
        self.setWindowTitle("Druck Fluss Viewer")
        self.resize(800, 600)

        self.meinLayout = QtWidgets.QVBoxLayout()
        druckTitel = '<span style="color: black">'+'Pressure of ' + elementName +'</span>'
        self.graphDruck = pyqtgraph.PlotWidget(title = druckTitel, name = "graphDruck")
        self.graphDruck.addLegend()
        self.graphDruck.setLabel("left", "Pressure", units = "p")
        self.graphDruck.setLabel("bottom", "Time", units = "s")
        self.graphDruck.setBackground([255,255,255,0])
        self.graphDruck.getAxis("bottom").setPen(pyqtgraph.mkPen([0,0,0,255]))
        self.graphDruck.getAxis("left").setPen(pyqtgraph.mkPen([0, 0, 0, 255]))
        #self.graphDruck.setYRange(0,100)
        kurve1 = self.graphDruck.plot(times4Results, values[0], name = "in")
        kurve1.setPen(pyqtgraph.mkPen([255,0,0], width = 2, style = QtCore.Qt.SolidLine))
        kurve2 = self.graphDruck.plot(times4Results, values[1], name = "out")
        kurve2.setPen(pyqtgraph.mkPen([0,0,255], width = 2, style = QtCore.Qt.SolidLine))
        if metaDict != None:
            target1Kurve1 = self.graphDruck.plot(times4Results, metaDict["p_target_lower_pL"], name="target")
            target1Kurve1.setPen(pyqtgraph.mkPen([255, 0, 0], width=2, style=QtCore.Qt.DotLine))
            target2Kurve1 = self.graphDruck.plot(times4Results, metaDict["p_target_upper_pL"], name="")
            target2Kurve1.setPen(pyqtgraph.mkPen([255, 0, 0], width=2, style=QtCore.Qt.DotLine))
            target1Kurve2 = self.graphDruck.plot(times4Results, metaDict["p_target_lower_pR"], name="target")
            target1Kurve2.setPen(pyqtgraph.mkPen([0, 0, 255], width=2, style=QtCore.Qt.DotLine))
            target2Kurve2 = self.graphDruck.plot(times4Results, metaDict["p_target_upper_pR"], name="")
            target2Kurve2.setPen(pyqtgraph.mkPen([0, 0, 255], width=2, style=QtCore.Qt.DotLine))

        flussTitel = '<span style="color: black">'+'Flow of ' + elementName +'</span>'
        self.graphFluss = pyqtgraph.PlotWidget(title = flussTitel, name = "graphFluss")
        self.graphFluss.addLegend()
        self.graphFluss.setLabel("left", "Flow", units = "f")
        self.graphFluss.setLabel("bottom", "Time", units = "s")
        self.graphFluss.setBackground([255,255,255,0])
        self.graphFluss.getAxis("bottom").setPen(pyqtgraph.mkPen([0, 0, 0, 255]))
        self.graphFluss.getAxis("left").setPen(pyqtgraph.mkPen([0, 0, 0, 255]))
        kurve3 = self.graphFluss.plot(times4Results, values[2], name = "in")
        kurve3.setPen(pyqtgraph.mkPen([255,0,0], width = 2, style = QtCore.Qt.SolidLine))
        kurve4 = self.graphFluss.plot(times4Results, values[3], name = "out")
        kurve4.setPen(pyqtgraph.mkPen([0,0,255], width = 2, style = QtCore.Qt.SolidLine))
        if metaDict != None:
            targetKurve34 = self.graphFluss.plot(times4Results, metaDict["q_target_q"], name="target")
            targetKurve34.setPen(pyqtgraph.mkPen([0, 0, 0], width=2, style=QtCore.Qt.DotLine))
        self.meinLayout.addWidget(self.graphDruck,1)
        self.meinLayout.addWidget(self.graphFluss,1)

        self.setLayout(self.meinLayout)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = Test([0,1,2,3,4],[[20,30,20,40,50],[25,30,21,38,53],[10,15,12,11,8],[4,8,12,18,6]],"Rohr3")
    gui.show()
    sys.exit(app.exec_())
