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
import numpy
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph
from Viewer.essentials4Viewer.CustomLegendItem import CustomLegendItem
from PyQt5.QtWidgets import QWidget


class PressureFlowViewer(QtWidgets.QDialog):


    def __init__(self, data4element, parent=None):
        super(PressureFlowViewer, self).__init__(parent)
        self.steps = len(data4element["times"])
        self.element = data4element
        self.keys = data4element.keys()
        if parent is not None:
            self.infLineF = pyqtgraph.InfiniteLine(pos=data4element["times"][self.parent().timeSlider.sliderPosition()],
                                                   pen=[0, 0, 0])
            self.infLineD = pyqtgraph.InfiniteLine(pos=data4element["times"][self.parent().timeSlider.sliderPosition()],
                                                   pen=[0, 0, 0])
            self.parent().timeSlider.valueChanged.connect(
                lambda t=self.parent().timeSlider.sliderPosition(): self.updateSlider(t))
        self.initUI()

    # construct state bars if data exists
    def constructBars(self, pressurOrFlow, element, keys, steps):
        t = element["times"]
        openingStates = []
        bypassStates = []
        beginOfBar = None
        if "opening-states" in keys:
            allValues = []
            if pressurOrFlow == "pressure":
                for i in range(2):
                    allValues += [tupel[i] for tupel in element["valuesPressure"]]
                for namespace in ["p_target_upper_pL", "p_target_lower_pL", "p_target_upper_pR", "p_target_lower_pR"]:
                    if namespace in keys:
                        allValues += element[namespace]
            if pressurOrFlow == "flow":
                for i in range(2):
                    allValues += [tupel[i] for tupel in element["valuesFlow"]]
                if "q_target_q" in keys:
                    allValues += element["q_target_q"]
            hightOfBar = 1.1 * max(allValues)
            beginOfBar = min(allValues) - 0.1 * max(allValues)
            for i in range(steps):
                if element["opening-states"][i] == 0:
                    if i == 0:
                        openingStates.append(
                            {"x": [t[0],
                                   0.5 * (t[0] + t[1])],
                             "y": [hightOfBar, hightOfBar]
                             }
                        )
                    elif 0 < i < (steps - 1):
                        # not first or last time step
                        if len(openingStates) > 0:
                            if element["opening-states"][i-1] == 0:
                                openingStates[-1]["x"][1] = 0.5 * (t[i] + t[i + 1])
                            else:
                                openingStates.append(
                                    {"x": [0.5 * (t[i - 1] + t[i]),
                                           0.5 * (t[i] + t[i + 1])],
                                     "y": [hightOfBar, hightOfBar]
                                     }
                                )
                        else:
                            openingStates.append(
                                {"x": [0.5 * (t[i - 1] + t[i]),
                                       0.5 * (t[i] + t[i + 1])],
                                 "y": [hightOfBar, hightOfBar]
                                 }
                            )
                    elif i == (steps - 1):
                        # last time step
                        if len(openingStates) > 0:
                            if element["opening-states"][i-1] == 0:
                                openingStates[-1]["x"][1] = t[steps - 1]
                            else:
                                openingStates.append(
                                    {"x": [0.5 * (t[i - 1] + t[i]),
                                           t[steps - 1]],
                                     "y": [hightOfBar, hightOfBar]
                                     }
                                )
                        else:
                            openingStates.append(
                                {"x": [0.5 * (t[i - 1] + t[i]),
                                       t[steps - 1]],
                                 "y": [hightOfBar, hightOfBar]
                                 }
                            )
            if "bypass-states" in keys:
                for i in range(steps):
                    if element["opening-states"][i] == 1 and element["bypass-states"][i] == 1:
                        if i == 0:
                            # first time step
                            bypassStates.append(
                                {"x": [t[0],
                                       0.5 * (t[0] + t[1])],
                                 "y": [hightOfBar, hightOfBar]
                                 }
                            )
                        elif 0 < i < (steps - 1):
                            # not first or last time step
                            if len(bypassStates) > 0:
                                if element["bypass-states"][i-1] == 1:
                                    bypassStates[-1]["x"][1] = 0.5 * (t[i] + t[i + 1])
                                else:
                                    bypassStates.append(
                                        {"x": [0.5 * (t[i - 1] + t[i]),
                                               0.5 * (t[i] + t[i + 1])],
                                         "y": [hightOfBar, hightOfBar]
                                         }
                                    )
                            else:
                                bypassStates.append(
                                    {"x": [0.5 * (t[i - 1] + t[i]),
                                           0.5 * (t[i] + t[i + 1])],
                                     "y": [hightOfBar, hightOfBar]
                                     }
                                )
                        elif i == (steps - 1):
                            # last time step
                            if len(bypassStates) > 0:
                                if element["bypass-states"][i-1] == 1:
                                    bypassStates[-1]["x"][1] = t[steps - 1]
                                else:
                                    bypassStates.append(
                                        {"x": [0.5 * (t[i - 1] + t[i]),
                                               t[steps - 1]],
                                         "y": [hightOfBar, hightOfBar]
                                         }
                                    )
                            else:
                                bypassStates.append(
                                    {"x": [0.5 * (t[i - 1] + t[i]),
                                           t[steps - 1]],
                                     "y": [hightOfBar, hightOfBar]
                                     }
                                )
        return openingStates, bypassStates, beginOfBar


    # initializes the FlowPressure Window
    def initUI(self):
        self.windowDFView = QtWidgets.QWidget(self)
        self.setWindowTitle("ELEMENT VIEWER")
        self.resize(800, 600)
        self.meinLayout = QtWidgets.QVBoxLayout()

        # PLOT FOR PRESSURE
        druckTitel = '<span style="color: black">' + 'pressure of ' + self.element["id"] + '</span>'
        self.graphDruck = pyqtgraph.PlotWidget(title=druckTitel, name="graph pressure")
        self.graphDruck.setLabel("left", "PRESSURE", units=self.element["pressure"])
        self.graphDruck.setLabel("bottom", "TIME", units="s")
        self.graphDruck.setBackground([255, 255, 255, 0])
        self.graphDruck.getAxis("bottom").setPen(pyqtgraph.mkPen([0, 0, 0, 255]))
        self.graphDruck.getAxis("left").setPen(pyqtgraph.mkPen([0, 0, 0, 255]))

        # draw bars if data exists
        (self.openingStatesBarPressure, self.bypassStatesBarsPressure, self.beginOfBar) = \
            self.constructBars("pressure", self.element, self.keys, self.steps)
        for stateBar in self.openingStatesBarPressure:
            self.graphDruck.plot(stateBar["x"], stateBar["y"], fillLevel=self.beginOfBar, fillBrush=[200, 200, 200])
            pass
        for stateBar in self.bypassStatesBarsPressure:
            self.graphDruck.plot(stateBar["x"], stateBar["y"], fillLevel=self.beginOfBar, fillBrush=[200, 200, 255])
            pass

        self.graphDruck.addItem(self.infLineD)

        # draw lines if data exists
        if "valuesPressure" in self.keys:
            self.pressureIn = self.graphDruck.plot(self.element["times"],
                                              [tupel[0] for tupel in self.element["valuesPressure"]],
                                              name="pressure in")
            self.pressureIn.setPen(pyqtgraph.mkPen([255, 0, 0], width=2, style=QtCore.Qt.SolidLine))
        if "p_target_upper_pL" in self.keys:
            self.upperTargetIn = self.graphDruck.plot(self.element["times"],
                                                 self.element["p_target_upper_pL"],
                                                 name="upper target")
            self.upperTargetIn.setPen(pyqtgraph.mkPen([255, 0, 0], width=2, style=QtCore.Qt.DashLine))
        if "p_target_lower_pL" in self.keys:
            self.lowerTargetIn = self.graphDruck.plot(self.element["times"],
                                                 self.element["p_target_lower_pL"],
                                                 name="lower target")
            self.lowerTargetIn.setPen(pyqtgraph.mkPen([255, 0, 0], width=2, style=QtCore.Qt.DashDotDotLine))
        if "valuesPressure" in self.keys:
            self.pressureOut = self.graphDruck.plot(self.element["times"],
                                               [tupel[1] for tupel in self.element["valuesPressure"]],
                                               name="pressure out")
            self.pressureOut.setPen(pyqtgraph.mkPen([0, 0, 255], width=2, style=QtCore.Qt.SolidLine))
        if "p_target_upper_pR" in self.keys:
            self.upperTargetOut = self.graphDruck.plot(self.element["times"],
                                                  self.element["p_target_upper_pR"],
                                                  name="upper target")
            self.upperTargetOut.setPen(pyqtgraph.mkPen([0, 0, 255], width=2, style=QtCore.Qt.DashLine))
        if "p_target_lower_pR" in self.keys:
            self.lowerTargetOut = self.graphDruck.plot(self.element["times"],
                                                  self.element["p_target_lower_pR"],
                                                  name="lower target")
            self.lowerTargetOut.setPen(pyqtgraph.mkPen([0, 0, 255], width=2, style=QtCore.Qt.DashDotDotLine))

        # PLOT FOR FLOW
        flussTitel = '<span style="color: black">' + 'flow of ' + self.element["id"] + '</span>'
        self.graphFluss = pyqtgraph.PlotWidget(title=flussTitel, name="graph flow")
        self.graphFluss.setLabel("left", "FLOW", units=self.element["flow"])
        self.graphFluss.setLabel("bottom", "TIME", units="s")
        self.graphFluss.setBackground([255, 255, 255, 0])
        self.graphFluss.getAxis("bottom").setPen(pyqtgraph.mkPen([0, 0, 0, 255]))
        self.graphFluss.getAxis("left").setPen(pyqtgraph.mkPen([0, 0, 0, 255]))
        # self.graphFluss.setYRange(self.element["times"][0], self.element["times"][-1])

        # draw bars if data exists
        (self.openingStatesBarsFlow, self.bypassStatesBarsFlow, self.beginOfBar) = \
            self.constructBars("flow", self.element, self.keys, self.steps)
        for stateBar in self.openingStatesBarsFlow:
            self.openstateFlow = self.graphFluss.plot(stateBar["x"], stateBar["y"], fillLevel=self.beginOfBar,
                                                      fillBrush=[200, 200, 200])  # name="closed"
            pass
        for stateBar in self.bypassStatesBarsFlow:
            self.bypassstateFlow = self.graphFluss.plot(stateBar["x"], stateBar["y"], fillLevel=self.beginOfBar,
                                                        fillBrush=[200, 200, 255])  # name="bypass"
            pass

        self.graphFluss.addItem(self.infLineF)

        if "valuesFlow" in self.keys:
            self.flowIn = self.graphFluss.plot(self.element["times"],
                                          [tupel[0] for tupel in self.element["valuesFlow"]],
                                          name="flow in")
            self.flowIn.setPen(pyqtgraph.mkPen([255, 0, 0], width=2, style=QtCore.Qt.SolidLine))
        if "valuesFlow" in self.keys:
            self.flowOut = self.graphFluss.plot(self.element["times"],
                                           [tupel[1] for tupel in self.element["valuesFlow"]],
                                           name="flow out")
            self.flowOut.setPen(pyqtgraph.mkPen([0, 0, 255], width=2, style=QtCore.Qt.SolidLine))
        if "q_target_q" in self.keys:
            self.target = self.graphFluss.plot(self.element["times"],
                                          self.element["q_target_q"],
                                          name="target")
            self.target.setPen(pyqtgraph.mkPen([0, 0, 0], width=2, style=QtCore.Qt.DotLine))

        # CREATE LEGENDS
        self.legendDruckView = pyqtgraph.PlotWidget(name="legend pressure", background=[0,0,0,0], foreground=[0,0,0])
        self.legendDruckView.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.legendDruckView.setFixedWidth(160)
        self.legendDruckView.getPlotItem().hideAxis("bottom")
        self.legendDruckView.getPlotItem().hideAxis("left")
        self.legendDruck = CustomLegendItem()
        self.legendDruck.setParentItem(self.legendDruckView.getPlotItem())
        self.legendDruck.addItem(self.pressureIn, "  in")
        self.legendDruck.addItem(self.pressureOut, "  out")
        if "p_target_lower_pL" in self.keys:
            self.legendDruck.addItem(self.lowerTargetIn, "  lower in")
        if "p_target_upper_pL" in self.keys:
            self.legendDruck.addItem(self.upperTargetIn, "  upper in")
        if "p_target_lower_pR" in self.keys:
            self.legendDruck.addItem(self.lowerTargetOut, "  lower out")
        if "p_target_upper_pR" in self.keys:
            self.legendDruck.addItem(self.upperTargetOut, "  upper out")
        if len(self.openingStatesBarsFlow) > 0:
            self.legendDruck.addItem(self.openstateFlow, "  closed")
        if len(self.bypassStatesBarsFlow) > 0:
            self.legendDruck.addItem(self.bypassstateFlow, "  bypass")
        self.legendFlussView = pyqtgraph.PlotWidget(name="legend flow", background=[0,0,0,0], foreground=[0,0,0])
        self.legendFlussView.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.legendFlussView.setFixedWidth(160)
        #self.legendFlussView.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.legendFlussView.getPlotItem().hideAxis("bottom")
        self.legendFlussView.getPlotItem().hideAxis("left")
        self.legendFluss = CustomLegendItem()
        self.legendFluss.setParentItem(self.legendFlussView.getPlotItem())
        self.legendFluss.addItem(self.flowIn, "  in")
        self.legendFluss.addItem(self.flowOut, "  out")
        if "q_target_q" in self.keys:
            self.legendFluss.addItem(self.target, "  target")
        if len(self.openingStatesBarsFlow) > 0:
            self.legendFluss.addItem(self.openstateFlow, "  closed")
        if len(self.bypassStatesBarsFlow) > 0:
            self.legendFluss.addItem(self.bypassstateFlow, "  bypass")

        # LAYOUT BOTH PLOTS
        self.HLayoutDruck = QtWidgets.QHBoxLayout()
        self.HLayoutDruck.addWidget(self.graphDruck, 1)
        self.HLayoutDruck.addWidget(self.legendDruckView, 0)

        self.HLayoutFluss = QtWidgets.QHBoxLayout()
        self.HLayoutFluss.addWidget(self.graphFluss, 1)
        self.HLayoutFluss.addWidget(self.legendFlussView, 0)

        self.meinLayout.addLayout(self.HLayoutDruck, 1)
        self.meinLayout.addLayout(self.HLayoutFluss, 1)
        self.setLayout(self.meinLayout)
        self.update()
        # self.connectNotify(self, QtCore.pyqtSignal("newTime"), self.updateSlider)

    def updateSlider(self, newTime):
        self.infLineF.setPos(self.element["times"][newTime])
        self.infLineD.setPos(self.element["times"][newTime])
        self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = PressureFlowViewer(
        {"id": "compressor",
         "von": "innode",
         "nach": "sink_2",
         "diameter": 400,
         "length": None,
         "valuesFlow": [(10, 5), (12, 8), (4, 5), (10, 15), (0, 0), (0, 0)],
         "valuesPressure": [(50, 40), (40, 35), (35, 40), (40, 35), (35, 40), (40, 40)],
         "bypass-states": [1, 1, 0, 0, 0, 0],  # optional
         "opening-states": [1, 1, 1, 1, 1, 0],  # optional
         "p_target_lower_pL": [30, 30, 25, 25, 22, 30],  # optional
         "p_target_lower_pR": [25, 25, 20, 25, 24, 24],  # optional
         "p_target_upper_pL": [70, 70, 70, 70, 70, 68],  # optional
         "p_target_upper_pR": [60, 70, 70, 60, 60, 60],  # optional
         "q_target_q": [5, 5, 5, 5, 5, 4],  # optional
         "showName": False,
         "flow": "kg_per_s",
         "pressure": "bar",
         "times": [0, 2, 7, 10, 20, 22]
         },
        parent=None
    )
    gui.show()
    sys.exit(app.exec_())
