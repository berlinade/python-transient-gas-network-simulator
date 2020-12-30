'''
    part of flow network result viewer
'''

__author__ = ('John Gerick',) # alphabetical order of surnames
__credits__ = ('Tom Streubel',) # alphabetical order of surnames


'''
    imports
    =======
'''
import datetime, os, sys, yaml
from math import sqrt
from PyQt5 import QtCore, QtGui, QtWidgets
from Viewer.essentials4Viewer import *


##############################################
# Erstellen der interaktiven Netzwerkansicht #
##############################################


# noinspection PyAttributeOutsideInit
class ResultViewer(QtWidgets.QMainWindow):

    def __init__(self, parent=None, openedFiles=None):
        super(ResultViewer, self).__init__(parent)
        self._location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        # initializes the Menu
        self.initMenu()
        # initializes the Main Window
        self.initUI(openedFiles)

    # loads a smal example with imaginary data to initialize Variables
    def loadStandardExample(self):
        scriptLocation = os.path.dirname(__file__) + "/"
        with open(scriptLocation + "standardExample/StandardExample.times4Results.yaml",
                  mode="r") as file4times4Results:
            self.times4Results = yaml.load(file4times4Results, Loader=yaml.SafeLoader)
        with open(scriptLocation + "standardExample/StandardExample.units.yaml", mode="r") as file4units:
            self.units = yaml.load(file4units, Loader=yaml.SafeLoader)
        with open(scriptLocation + "standardExample/StandardExample.nodes.yaml", mode="r") as file4nodes:
            self.nodes = yaml.load(file4nodes, Loader=yaml.SafeLoader)
        with open(scriptLocation + "standardExample/StandardExample.elements.yaml", mode="r") as file4elements:
            self.elements = yaml.load(file4elements, Loader=yaml.SafeLoader)

    # initializes the actions for the drop down menu
    def initActions(self):
        self.ActionExit = QtWidgets.QAction("EXIT")
        self.ActionExit.setShortcut("Ctrl+Q")
        self.ActionExit.setStatusTip("Exit application")
        self.ActionExit.triggered.connect(lambda: QtWidgets.qApp.quit())

        self.ActionReadNewDictonary = QtWidgets.QAction("Import dictonaries from yaml files")
        self.ActionReadNewDictonary.setStatusTip("read new network data from yaml files"
                                                 "for times, units, nodes and elements")
        self.ActionReadNewDictonary.triggered.connect(lambda: self.fun4ChooseDictonary())

        self.ActionReadMetaData = QtWidgets.QAction("Import MetaData from yaml file")
        self.ActionReadMetaData.setStatusTip("read MetaData from result.meta.yaml files for targetValues")
        self.ActionReadMetaData.triggered.connect(lambda: self.fun4ChooseMetaData())

        self.ActionOpenConverter = QtWidgets.QAction("Open Converter")
        self.ActionOpenConverter.setStatusTip("Opens Converter Tool"
                                              "to convert *.net (and *.result) for the ResultViewer")
        self.ActionOpenConverter.triggered.connect(lambda: self.fun4OpenConverter())

        self.ActionExport2PNGSmal = QtWidgets.QAction("Export view to smal PNG")
        self.ActionExport2PNGSmal.setStatusTip("Exports the current view to 800x600 PNG picture")
        self.ActionExport2PNGSmal.triggered.connect(lambda: self.fun4Export2PNGSmal())

        self.ActionExport2PNGBig = QtWidgets.QAction("Export view to big PNG")
        self.ActionExport2PNGBig.setStatusTip("Exports the current view to 1920×1080 PNG picture")
        self.ActionExport2PNGBig.triggered.connect(lambda: self.fun4Export2PNGBig())

        self.ActionExport2PNGCustom = QtWidgets.QAction("Export view to custom PNG")
        self.ActionExport2PNGCustom.setStatusTip("Exports the current view to picture with custom options")
        self.ActionExport2PNGCustom.triggered.connect(lambda: self.fun4Export2PNGCustom())

        self.ActionExport2SVG = QtWidgets.QAction("Export view to SVG")
        self.ActionExport2SVG.setStatusTip("Exports the current view to SVG")
        self.ActionExport2SVG.triggered.connect(lambda: self.fun4saveSvg())

        self.ActionLoadConfig = QtWidgets.QAction("load Configuration")
        self.ActionLoadConfig.setStatusTip("This will load the configuration from a file.")
        self.ActionLoadConfig.triggered.connect(lambda: self.loadConfig())

        self.ActionSaveConfig = QtWidgets.QAction("save Configuration")
        self.ActionSaveConfig.setStatusTip("This will save the configuration"
                                           "into a file. It is NOT loaded automatically on startup.")
        self.ActionSaveConfig.triggered.connect(lambda: self.saveConfig())

        self.ActionChooseColor4Pressure = QtWidgets.QAction("color for pressure")
        self.ActionChooseColor4Pressure.setStatusTip("This will let you choose new colors"
                                                     "for the color bar used for pressure.")
        self.ActionChooseColor4Pressure.triggered.connect(lambda: self.farbenAusw1())

        self.ActionChooseColor4Flow = QtWidgets.QAction("color for flow")
        self.ActionChooseColor4Flow.setStatusTip("This will let you choose new colors"
                                                 "for the color bar used for flow.")
        self.ActionChooseColor4Flow.triggered.connect(lambda: self.farbenAusw2())

        self.ActionChangeParameters = QtWidgets.QAction("change graphical parameter")
        self.ActionChangeParameters.setStatusTip("This will let you choose new parameters for the view.")
        self.ActionChangeParameters.triggered.connect(lambda: self.fun4ParameterDialog())

        self.ActionResizeArrow1 = QtWidgets.QAction("arrow size")
        self.ActionResizeArrow1.setStatusTip("This will let you choose new facor for the size of the arrows.")
        self.ActionResizeArrow1.triggered.connect(lambda: self.fun4ArrowSizeFactor())

        self.ActionResizeArrow2 = QtWidgets.QAction("arrow thickness")
        self.ActionResizeArrow2.setStatusTip("This will let you choose new facor for the thickness of the arrows.")
        self.ActionResizeArrow2.triggered.connect(lambda: self.fun4ArrowThicknessFactor())

        self.ActionMinFlow = QtWidgets.QAction("minimal flow")
        self.ActionMinFlow.setStatusTip("This will let you choose for which values the arrows are drawn.")
        self.ActionMinFlow.triggered.connect(lambda: self.setMinFlow4ArrowFunction())

        self.ActionElementSize = QtWidgets.QAction("pipe thickness")
        self.ActionElementSize.setStatusTip("This will let you choose the thickness of the drawn elements.")
        self.ActionElementSize.triggered.connect(lambda: self.setElementThickness())

        self.ActionElementThickness = QtWidgets.QAction("pipe diameter dependency")
        self.ActionElementThickness.setStatusTip("This will let you choose the thickness dependency"
                                                 "of the drawn elements. 0 will show no dependency at all"
                                                 "and higher values will result in higher dependency")
        self.ActionElementThickness.triggered.connect(lambda: self.setElementDiameterDependency())

        self.ActionTextSize = QtWidgets.QAction("text size")
        self.ActionTextSize.setStatusTip("This will let you choose the size of the text.")
        self.ActionTextSize.triggered.connect(lambda: self.setTextSize())

    # initializes the Menu
    def initMenu(self):
        # at first the actions are defined
        self.initActions()
        # then the actions are inserted into the Menu
        self.mainMenu = self.menuBar()
        self.FileMenu = self.mainMenu.addMenu("File")
        self.FileMenu.addAction(self.ActionReadNewDictonary)
        self.FileMenu.addAction(self.ActionReadMetaData)
        self.FileMenu.addAction(self.ActionOpenConverter)
        self.FileMenu.addSeparator()
        self.FileMenu.addAction(self.ActionExport2PNGSmal)
        self.FileMenu.addAction(self.ActionExport2PNGBig)
        self.FileMenu.addAction(self.ActionExport2PNGCustom)
        #        self.FileMenu.addAction(self.ActionExport2SVG)   not working, maybe due to intern QT transformation not working

        self.FileMenu.addSeparator()
        self.FileMenu.addAction(self.ActionExit)

        self.OptionMenu = self.mainMenu.addMenu("Options")
        self.OptionMenu.addSection("config")
        self.OptionMenu.addAction(self.ActionSaveConfig)
        self.OptionMenu.addAction(self.ActionLoadConfig)
        self.OptionMenu.addAction(self.ActionChangeParameters)
        self.OptionMenu.addSection("colors")
        self.OptionMenu.addAction(self.ActionChooseColor4Pressure)
        self.OptionMenu.addAction(self.ActionChooseColor4Flow)
        self.OptionMenu.addSection("factors")
        self.OptionMenu.addAction(self.ActionElementSize)
        self.OptionMenu.addAction(self.ActionElementThickness)
        self.OptionMenu.addAction(self.ActionResizeArrow1)
        self.OptionMenu.addAction(self.ActionResizeArrow2)
        self.OptionMenu.addAction(self.ActionTextSize)
        self.OptionMenu.addAction(self.ActionMinFlow)

    def initVars(self, openedFiles=None):
        if openedFiles is None:
            self.loadStandardExample()  ## loads a small example with imaginary data to initialize Variables ##
        else:
            self.times4Results = openedFiles["times"]
            self.units = openedFiles["units"]
            self.nodes = openedFiles["nodes"]
            self.elements = openedFiles["elements"]
        self.myStandFont = QtGui.QFont()
        self.myColorFont = QtGui.QFont()
        self.invisibleBrush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0), QtCore.Qt.SolidPattern)
        self.invisablePen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0, QtCore.Qt.SolidLine)
        self.metaData = None
        self.setMinMaxValues()
        self.PressOrFlow = "pressure"  ## can be "pressure" or "flow" ##
        self.parameterDict = {}
        scriptLocation = os.path.dirname(__file__) + "/"
        with open(scriptLocation + "standardExample/StandardExample.RVConfig.yaml", mode="r") as inputConfig:
            parameterDictInput = yaml.load(inputConfig, Loader=yaml.SafeLoader)
            self.loadConfig(existingParameterDict=parameterDictInput)
        if openedFiles is not None:
            if openedFiles["RVConfig"] is not None:
                for key, value in openedFiles["RVConfig"].items():
                    self.parameterDict[key] = value

    def initUI(self, openedFiles=None):  ## initializes the Main Window ##
        self.MainViewWindow = QtWidgets.QWidget(self)
        self.setCentralWidget(self.MainViewWindow)
        self.setWindowTitle("RESULT VIEWER")
        self.setGeometry(0, 0, 800, 600)
        # the standard configuration for the GUI
        self.initVars(openedFiles)
        # Layout is filled with QtWidgets
        self.subLayoutTop = QtWidgets.QHBoxLayout()
        self.ButtonResetView = QtWidgets.QPushButton()
        self.ButtonResetView.setText("restore view")
        self.ButtonResetView.clicked.connect(self.resetView)
        self.RadioButtonPressure = QtWidgets.QRadioButton("pressure")
        self.RadioButtonPressure.setChecked(True)
        self.RadioButtonPressure.toggled.connect(self.PressSwitch)
        self.RadioButtonFlow = QtWidgets.QRadioButton("flow")
        self.RadioButtonFlow.setChecked(False)
        self.RadioButtonFlow.toggled.connect(self.FlowSwitch)
        self.subLayoutTop.addStretch(1)
        self.subLayoutTop.addWidget(self.ButtonResetView)
        self.subLayoutTop.addSpacing(20)
        self.subLayoutTop.addWidget(self.RadioButtonPressure)
        self.subLayoutTop.addWidget(self.RadioButtonFlow)
        self.subLayoutTop.addStretch(1)

        # Layout is filled with QtWidgets
        self.subLayoutMiddle = QtWidgets.QHBoxLayout()
        self.scene = QtWidgets.QGraphicsScene(self)
        self.ansicht = ViewerWithZoom(self)
        self.ansicht.setScene(self.scene)
        self.ansicht.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.ansicht.show()
        self.subsubLayoutMiddle = QtWidgets.QVBoxLayout()
        self.sceneColorBar = QtWidgets.QGraphicsScene(self)
        self.colorMapBarView = Viewer4ColorBar(self)
        self.colorMapBarView.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                                                 QtWidgets.QSizePolicy.Expanding))
        self.colorMapBarView.setScene(self.sceneColorBar)
        self.colorMapBarView.setFixedWidth(50)
        self.colorMapBarView.show()
        self.colorMapBarLabelTop = QtWidgets.QLabel()
        self.colorMapBarLabelTop.setText("{}".format(self.maxPVal))
        self.colorMapBarLabelTop.setAlignment(QtCore.Qt.AlignCenter)
        self.colorMapBarLabelTop.setFont(self.myColorFont)
        self.colorMapBarLabelBottom = QtWidgets.QLabel()
        self.colorMapBarLabelBottom.setText("{}".format(self.minPVal))
        self.colorMapBarLabelBottom.setAlignment(QtCore.Qt.AlignCenter)
        self.colorMapBarLabelBottom.setFont(self.myColorFont)
        self.fun4ColorBarContruction()
        self.subsubLayoutMiddle.addWidget(self.colorMapBarLabelTop)
        self.subsubLayoutMiddle.addWidget(self.colorMapBarView)
        self.subsubLayoutMiddle.addWidget(self.colorMapBarLabelBottom)
        self.subLayoutMiddle.addLayout(self.subsubLayoutMiddle)
        self.subLayoutMiddle.addWidget(self.ansicht)

        # Layout is filled with QtWidgets
        self.subLayoutBottom = QtWidgets.QHBoxLayout()
        self.timeLabel = QtWidgets.QLabel()
        self.timeLabel.setText("Time: % 12.1f s" % self.times4Results[0])
        self.playButton = QtWidgets.QPushButton()
        self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.autoPlay)
        self.pauseButton = QtWidgets.QPushButton()
        self.pauseButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
        self.pauseButton.clicked.connect(self.autoPause)
        self.timeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.timeSlider.setMinimum(0)
        self.timeSlider.setMaximum(len(self.times4Results))
        self.timeSlider.setFixedHeight(19)
        self.timeSlider.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Preferred))
        self.timeSlider.valueChanged.connect(self.recolor)
        self.wiedergabeSpeedLabel = QtWidgets.QLabel()
        self.wiedergabeSpeedLabel.setText("Speed:")
        self.wiedergabeSpeedLabel.setToolTip("Set the speed factor.\n 1.0 is normal speed.")
        self.wiedergabeSpeedLineEdit = QtWidgets.QLineEdit()
        self.wiedergabeSpeedLineEdit.setFixedWidth(40)
        self.wiedergabeSpeedLineEdit.setText(str(self.parameterDict["wiedergabeSpeedVar"]))
        self.wiedergabeSpeedLineEdit.editingFinished.connect(self.wiedergabeSpeedSwitch)
        self.subLayoutBottom.addWidget(self.timeLabel)
        self.subLayoutBottom.addSpacing(10)
        self.subLayoutBottom.addWidget(self.timeSlider)
        self.subLayoutBottom.addSpacing(10)
        self.subLayoutBottom.addWidget(self.playButton)
        self.subLayoutBottom.addWidget(self.pauseButton)
        self.subLayoutBottom.addSpacing(10)
        self.subLayoutBottom.addWidget(self.wiedergabeSpeedLabel)
        self.subLayoutBottom.addWidget(self.wiedergabeSpeedLineEdit)

        # already filled layouts are put together
        self.meinLayout = QtWidgets.QVBoxLayout()
        self.meinLayout.addLayout(self.subLayoutTop)
        self.meinLayout.addLayout(self.subLayoutMiddle)
        self.meinLayout.addLayout(self.subLayoutBottom)
        self.MainViewWindow.setLayout(self.meinLayout)

        # builds up the scene with the provided Data
        self.show()
        self.updateAfterNeu()
        self.videoTimer = QtCore.QTimer(self)
        self.videoTimer.setSingleShot(True)
        self.videoTimer.timeout.connect(self.nextTimeFrame)
        self.ansicht.fitInView(self.scene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
        self.statusBar().showMessage("Ready")

    # updates the configuration for the GUI
    def updateConfig(self):
        self.wiedergabeSpeedLineEdit.setText(str(self.parameterDict["wiedergabeSpeedVar"]))
        self.myStandFont.setPointSize(self.parameterDict["textdicke"])
        self.myColorFont.setPointSize(self.parameterDict["myColorFontSize"])
        self.updateAfterNeu()

    # loads the standard configuration for the GUI
    def loadConfig(self, filename=None, existingParameterDict=None):
        if existingParameterDict is not None:
            RVConfigDict = existingParameterDict
        elif filename is None:
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
            filename, selectedFilter = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                             caption="load config",
                                                                             directory="",
                                                                             filter="RVConfig files (*.RVConfig.yaml)",
                                                                             options=options)  ## gives a Dialog to choose file ##
            if filename != "":
                try:
                    with open(filename, mode="r") as confFile:
                        RVConfigDict = yaml.load(confFile, Loader=yaml.SafeLoader)
                        print("{} loaded with parameters:/n   {}".format(
                            filename.split("/")[-1],
                            RVConfigDict)
                        )
                except IOError:
                    print("ERROR -> RVConfig not loaded, standard values are used instead.")
                    RVConfigDict = {}  # the config file could not be read and standard values are used
        else:
            try:
                with open(filename, mode="r") as confFile:
                    RVConfigDict = yaml.load(confFile, Loader=yaml.SafeLoader)
                    print("{} loaded with parameters:/n   {}".format(
                        filename.split("/")[-1],
                        RVConfigDict)
                    )
            except IOError:
                print("ERROR -> RVConfig not loaded, standard values are used instead.")
                RVConfigDict = {}  # the config file could not be read and standard values are used
        try:
            self.parameterDict["rohrdicke"] = RVConfigDict["rohrdicke"]  # can be adjusted to fit with the scale
        except KeyError:
            self.parameterDict["rohrdicke"] = 100
        try:
            self.parameterDict["rohrfaktor"] = RVConfigDict[
                "rohrfaktor"]  # to adjust thickness factor depending on diameter
        except KeyError:
            self.parameterDict["rohrfaktor"] = 0.3
        try:
            self.parameterDict["textdicke"] = RVConfigDict["textdicke"]  # to adjust text size in pixel (int)
        except KeyError:
            self.parameterDict["textdicke"] = 50
        try:
            self.parameterDict["arrowSize"] = RVConfigDict["arrowSize"]  # to adjust arrow size
            # (final size also depends on elementSize)
        except KeyError:
            self.parameterDict["arrowSize"] = 15
        try:
            self.parameterDict["symbolSize"] = RVConfigDict["symbolSize"]  # to adjust arrow size
            # (final size also depends on elementSize)
        except KeyError:
            self.parameterDict["symbolSize"] = 15
        try:
            self.parameterDict["arrowThickness"] = RVConfigDict[
                "arrowThickness"]  # to adjust the thickness of the arrows
        except KeyError:
            self.parameterDict["arrowThickness"] = 4
        try:
            self.parameterDict["symbolThickness"] = RVConfigDict[
                "symbolThickness"]  # to adjust the thickness of the arrows
        except KeyError:
            self.parameterDict["symbolThickness"] = 4
        try:
            self.parameterDict["wiedergabeSpeedVar"] = RVConfigDict[
                "wiedergabeSpeedVar"]  # defines the pause between timesteps
            # in milli seconds
        except KeyError:
            self.parameterDict["wiedergabeSpeedVar"] = 1.0
        self.farbenPressure = []  # at least 2 colors have to be given
        try:
            if len(RVConfigDict["farbenPressure"]) > 1:
                for farbe in RVConfigDict["farbenPressure"]:
                    self.farbenPressure.append(QtGui.QColor(farbe[0], farbe[1], farbe[2], 255))
            else:
                self.farbenPressure.append(QtGui.QColor(RVConfigDict["farbenPressure"][0],
                                                        RVConfigDict["farbenPressure"][1],
                                                        RVConfigDict["farbenPressure"][2], 255))
                self.farbenPressure.append(QtGui.QColor(RVConfigDict["farbenPressure"][0],
                                                        RVConfigDict["farbenPressure"][1],
                                                        RVConfigDict["farbenPressure"][2], 255))
        except (IndexError, KeyError):
            self.farbenPressure.append(QtGui.QColor(0, 0, 0, 255))
            self.farbenPressure.append(QtGui.QColor(255, 255, 255, 255))

        self.farbenFlow = []  # at least 2 colors have to be given
        try:
            if len(RVConfigDict["farbenFlow"]) > 1:
                for farbe in RVConfigDict["farbenFlow"]:
                    self.farbenFlow.append(QtGui.QColor(farbe[0], farbe[1], farbe[2], 255))
            else:
                self.farbenFlow.append(QtGui.QColor(RVConfigDict["farbenFlow"][0],
                                                    RVConfigDict["farbenFlow"][1],
                                                    RVConfigDict["farbenFlow"][2], 255))
                self.farbenFlow.append(QtGui.QColor(RVConfigDict["farbenFlow"][0],
                                                    RVConfigDict["farbenFlow"][1],
                                                    RVConfigDict["farbenFlow"][2], 255))
        except (IndexError, KeyError):
            self.farbenFlow.append(QtGui.QColor(0, 0, 0, 255))
            self.farbenFlow.append(QtGui.QColor(255, 255, 255, 255))
        try:
            self.parameterDict["minFlowAnzeige"] = RVConfigDict[
                "minFlowAnzeige"]  # defines wich value of flow will cause an arrow
        except KeyError:
            self.parameterDict["minFlowAnzeige"] = 10
        try:
            self.parameterDict["myColorFontSize"] = RVConfigDict[
                "myColorFontSize"]  # size of the values above and below colorbar
        except KeyError:
            self.parameterDict["myColorFontSize"] = 20
        try:
            self.parameterDict["switchXDirection"] = RVConfigDict["switchXDirection"]
        except KeyError:
            self.parameterDict["switchXDirection"] = 1.0
        try:
            self.parameterDict["switchYDirection"] = RVConfigDict["switchYDirection"]
        except KeyError:
            self.parameterDict["switchYDirection"] = -1.0
        try:
            self.parameterDict["autoReplay"] = RVConfigDict["autoReplay"]
        except KeyError:
            self.parameterDict["autoReplay"] = False
        try:
            self.parameterDict["autoReplayTimerInSek"] = RVConfigDict["autoReplayTimerInSek"]
        except KeyError:
            self.parameterDict["autoReplayTimerInSek"] = 2.0
        try:
            self.parameterDict["standardTimeIntervall"] = RVConfigDict["standardTimeIntervall"]
        except KeyError:
            self.parameterDict["standardTimeIntervall"] = 30.0

    def saveConfig(self, filename=None):  ## saves the current configuration to a file given or choosen by the user ##
        if filename is None:
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
            filename, selectedFilter = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                             caption="save config",
                                                                             directory="",
                                                                             filter="Config files (*.RVConfig.yaml)",
                                                                             selectedFilter="(*.RVConfig.yaml)",
                                                                             options=options)  ## gives a Dialog to choose file ##
            if filename != "":
                ok = True
        else:
            ok = True
        if ok:
            RVConfigDict = {"rohrdicke": self.parameterDict["rohrdicke"],
                            "rohrfaktor": self.parameterDict["rohrfaktor"],
                            "textdicke": self.parameterDict["textdicke"],
                            "arrowSize": self.parameterDict["arrowSize"],
                            "symbolSize": self.parameterDict["symbolSize"],
                            "arrowThickness": self.parameterDict["arrowThickness"],
                            "symbolThickness": self.parameterDict["symbolThickness"],
                            "wiedergabeSpeedVar": self.parameterDict["wiedergabeSpeedVar"],
                            "farbenPressure": [(farbe.red(), farbe.green(), farbe.blue()) for farbe in
                                               self.farbenPressure],
                            "farbenFlow": [(farbe.red(), farbe.green(), farbe.blue()) for farbe in self.farbenFlow],
                            "minFlowAnzeige": self.parameterDict["minFlowAnzeige"],
                            "myColorFontSize": self.parameterDict["myColorFontSize"],
                            "switchXDirection": self.parameterDict["switchXDirection"],
                            "switchYDirection": self.parameterDict["switchYDirection"],
                            "autoReplay": self.parameterDict["autoReplay"],
                            "autoReplayTimerInSek": self.parameterDict["autoReplayTimerInSek"],
                            "standardTimeIntervall": self.parameterDict["standardTimeIntervall"]
                            }
            if len(filename) < 15:
                filename = filename + ".RVConfig.yaml"
            elif filename[-14:] != ".RVConfig.yaml":
                filename = filename + ".RVConfig.yaml"
            with open(filename, mode="w") as fileConfig:
                yaml.dump(RVConfigDict, fileConfig, Dumper=yaml.SafeDumper)
                print("RVConfig saved as file {}".format(filename.split("/")[-1]))
        else:
            print("ERROR -> no RVConfig was saved")

    # set factor used for arrow size
    def fun4ArrowSizeFactor(self):
        size, ok = QtWidgets.QInputDialog.getDouble(self, "ArrowSize", "Set the new factor (standard is 15)",
                                                    value=self.parameterDict["arrowSize"], min=0.1)
        if ok and size > 0:
            self.parameterDict["arrowSize"] = size
            self.recolor()

    def fun4ArrowThicknessFactor(self):
        size, ok = QtWidgets.QInputDialog.getDouble(self, "ArrowThickness", "Set the new factor (standard is 4)",
                                                    value=self.parameterDict["arrowThickness"], min=0.1)
        if ok and size > 0:
            self.parameterDict["arrowThickness"] = size
            self.recolor()

    # import new dictinary from the yaml-files choosen by the dialog
    def fun4ChooseDictonary(self):
        self.fileTimes = ""
        self.fileUnits = ""
        self.fileNodes = ""
        self.fileElements = ""
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        self.fileTimes, selectedFilter = \
            QtWidgets.QFileDialog.getOpenFileName(self,
                                                  caption="select *.times4Results file for the times",
                                                  directory="",
                                                  filter="times4Result files (*.times4Results.yaml)",
                                                  options=options)
        if self.fileTimes != "":
            self.fileUnits, selectedFilter = \
                QtWidgets.QFileDialog.getOpenFileName(self,
                                                      caption="select *.units file for the units",
                                                      directory="",
                                                      filter="units files (*.units.yaml)",
                                                      options=options)
            if self.fileUnits != "":
                self.fileNodes, selectedFilter = \
                    QtWidgets.QFileDialog.getOpenFileName(self,
                                                          caption="select *.nodes file for the nodes",
                                                          directory="",
                                                          filter="node files (*.nodes.yaml)",
                                                          options=options)
                if self.fileNodes != "":
                    self.fileElements, selectedFilter = \
                        QtWidgets.QFileDialog.getOpenFileName(self,
                                                              caption="select *.elements file for the elements",
                                                              directory="",
                                                              filter="element files (*.elements.yaml)",
                                                              options=options)
                    if self.fileElements != "":
                        self.fun4ReadInputDictonary(self.fileTimes, self.fileUnits, self.fileNodes, self.fileElements)
                        self.setMinMaxValues()
                        self.updateAfterNeu()
                        print("succesfully imported {}, {}, {} and {}".format(self.fileTimes.split("/")[-1],
                                                                              self.fileUnits.split("/")[-1],
                                                                              self.fileNodes.split("/")[-1],
                                                                              self.fileElements.split("/")[-1]))
                    else:
                        msgBox = QtWidgets.QMessageBox()
                        msgBox.setText("You need to select a *.elements yaml-file.")
                        msgBox.exec()
                else:
                    msgBox = QtWidgets.QMessageBox()
                    msgBox.setText("You need to select a *.nodes yaml-file.")
                    msgBox.exec()

            else:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setText("You need to select a *.units yaml-file.")
                msgBox.exec()
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("You need to select a *.times4Results yaml-file.")
            msgBox.exec()

    def fun4ChooseMetaData(self):
        self.metaDataFile = None
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        self.metaDataFile, ok = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                      caption="select *.yaml file for the metaData",
                                                                      directory="",
                                                                      filter="metaData files (*.yaml)", options=options)
        if ok:
            with open(self.metaDataFile) as inputMetaFile:
                self.metaData = yaml.load(inputMetaFile, Loader=yaml.SafeLoader)
            self.updateAfterNeu()
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("You need to select a *.yaml file.")
            msgBox.exec()

    def fun4OpenConverter(self):
        self.ConverterWindow = Converter.guiConverter()
        self.ConverterWindow.show()

    def setMinMaxValues(self):
        try:
            self.minPVal = self.minimumPressure()
            self.maxPVal = self.maximumPressure()
            self.minFVal = self.minimumFlow()
            self.maxFVal = self.maximumFlow()
        except:
            self.minPVal = 0
            self.maxPVal = 1
            self.minFVal = 0
            self.maxFVal = 1

    def minimumPressure(self):
        minValue = self.elements[0]["valuesPressure"][0][0]
        for r in range(len(self.elements)):
            for z in range(len(self.times4Results)):
                if minValue > min(self.elements[r]["valuesPressure"][z][0], self.elements[r]["valuesPressure"][z][1]):
                    minValue = min(self.elements[r]["valuesPressure"][z][0], self.elements[r]["valuesPressure"][z][1]);
        return int(minValue)

    def maximumPressure(self):
        maxValue = self.elements[0]["valuesPressure"][0][0]
        for r in range(len(self.elements)):
            for z in range(len(self.times4Results)):
                if maxValue < max(self.elements[r]["valuesPressure"][z][0], self.elements[r]["valuesPressure"][z][1]):
                    maxValue = max(self.elements[r]["valuesPressure"][z][0], self.elements[r]["valuesPressure"][z][1]);
        if int(maxValue) + 1 == self.minPVal:
            return int(maxValue) + 2
        else:
            return int(maxValue) + 1

    def minimumFlow(self):
        minValue = abs(self.elements[0]["valuesFlow"][0][0])
        for r in range(len(self.elements)):
            for z in range(len(self.times4Results)):
                if minValue > min(abs(self.elements[r]["valuesFlow"][z][0]), abs(self.elements[r]["valuesFlow"][z][1])):
                    minValue = min(abs(self.elements[r]["valuesFlow"][z][0]), abs(self.elements[r]["valuesFlow"][z][1]))
        return int(minValue)

    def maximumFlow(self):
        maxValue = abs(self.elements[0]["valuesFlow"][0][0])
        for r in range(len(self.elements)):
            for z in range(len(self.times4Results)):
                if maxValue < max(abs(self.elements[r]["valuesFlow"][z][0]), abs(self.elements[r]["valuesFlow"][z][1])):
                    maxValue = max(abs(self.elements[r]["valuesFlow"][z][0]), abs(self.elements[r]["valuesFlow"][z][1]))
        if int(maxValue) + 1 == self.minFVal:
            return int(maxValue) + 2
        else:
            return int(maxValue) + 1

    def resetView(self):
        self.ansicht.fitInView(self.scene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)

    def PressSwitch(self):
        self.PressOrFlow = "pressure"
        self.recolor()

    def setMinFlow4ArrowFunction(self):
        size, ok = QtWidgets.QInputDialog.getDouble(self,
                                                    "MinFlow4Arrow", "Set the minimal Flow for Arrows to be drawn.",
                                                    value=self.parameterDict["minFlowAnzeige"], min=0.1)
        if ok and size > 0:
            self.parameterDict["minFlowAnzeige"] = size
            self.recolor()

    def FlowSwitch(self):
        self.PressOrFlow = "flow"
        self.recolor()

    def wiedergabeSpeedSwitch(self):
        try:
            self.parameterDict["wiedergabeSpeedVar"] = max(0.01, min(float(self.wiedergabeSpeedLineEdit.text()), 100.0))
            self.wiedergabeSpeedLineEdit.setText(str(self.parameterDict["wiedergabeSpeedVar"]))
        except:
            self.wiedergabeSpeedLineEdit.setText(str(self.parameterDict["wiedergabeSpeedVar"]))
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("You need to type an float for speed-factor\n (1.0 is normal speed 2.0 is doubled speed)")
            msgBox.exec()

    def setElementThickness(self):
        size, ok = QtWidgets.QInputDialog.getDouble(self,
                                                    "element size", "Set the size factor for elements.",
                                                    value=self.parameterDict["rohrdicke"], min=1)
        if ok and size > 0:
            self.parameterDict["rohrdicke"] = size
            self.updateAfterNeu()

    def setElementDiameterDependency(self):
        size, ok = QtWidgets.QInputDialog.getDouble(self,
                                                    "element size", "Set the thickness factor for elements.",
                                                    value=self.parameterDict["rohrdicke"], min=0.0, max=0.99,
                                                    decimals=2)
        if ok:
            self.parameterDict["rohrfaktor"] = size
            self.recolor()

    def setTextSize(self):
        size, ok = QtWidgets.QInputDialog.getInt(self,
                                                 "text size", "Set the size of the text.",
                                                 value=self.parameterDict["textdicke"], min=1)
        if ok:
            self.parameterDict["textdicke"] = size
            self.myStandFont.setPointSize(self.parameterDict["textdicke"])
            for text in self.AlleTexte:
                position = text.pos()
                shiftOld = text.boundingRect().center()
                text.setFont(self.myStandFont)
                shiftNew = text.boundingRect().center()
                text.setPos(-shiftNew + shiftOld + position)
                text.update()

    def updateAfterNeu(self):  # reconstructs all elements
        self.AlleStriche = []
        self.AllePunkte = []
        self.AlleTexte = []
        self.AllePfeile = []
        self.scene.clear()
        self.scene = QtWidgets.QGraphicsScene(self)
        self.ansicht.setScene(self.scene)
        self.timeLabel.setText("Time: {}".format(self.secondsToClocktime(int(self.times4Results[0]))))
        self.timeLabel.repaint()
        diameters = [elem["diameter"] for elem in self.elements if elem["diameter"] is not None]
        for i in range(len(self.elements)):
            element = self.elements[i]
            start = \
                [(self.parameterDict["switchXDirection"] * kno["x"], self.parameterDict["switchYDirection"] * kno["y"])
                 for
                 kno in self.nodes if kno["id"] == element["von"]][0]
            ende = \
                [(self.parameterDict["switchXDirection"] * kno["x"], self.parameterDict["switchYDirection"] * kno["y"])
                 for
                 kno in self.nodes if kno["id"] == element["nach"]][0]
            myLine = ClickableQGraphicsLineItem(self)
            myLine.setLine(start[0], start[1], ende[0], ende[1])
            myLine.data4element = {"times": self.times4Results}
            myLine.data4element.update(element)
            myLine.data4element.update(self.units)
            myLine.dataPointer = i
            if self.PressOrFlow == "pressure":
                brush = self.valuesToGradientBrush(element["valuesPressure"][0], (start, ende))
                #arrow1, arrow2 = self.arrowFunktion(start[0], start[1], ende[0], ende[1], element["valuesPressure"][0])
            else:
                brush = self.valuesToGradientBrush(element["valuesFlow"][0], (start, ende))
                #arrow1, arrow2 = self.arrowFunktion(start[0], start[1], ende[0], ende[1], element["valuesFlow"][0])
            myLine.setToolTip(
                "{}\n diameter {}, length {} \n von {} nach {}\n Drücke:\n wert {}  wert {}\n Flüsse:\n wert {}  wert {}".format(
                    element["id"],
                    element["diameter"],
                    element["length"],
                    element["von"],
                    element["nach"],
                    element["valuesPressure"][0][0],
                    element["valuesPressure"][0][1],
                    element["valuesFlow"][0][0],
                    element["valuesFlow"][0][1],
                )
            )
            if element["diameter"] is None:
                elementSizeFaktor = 1
            elif min(diameters) == max(diameters):
                elementSizeFaktor = 1
            else:
                transform2NullEins = (element["diameter"] - min(diameters)) / float(max(diameters) - min(diameters))
                elementSizeFaktor = transform2NullEins * float(2 * self.parameterDict["rohrfaktor"]) + 1 - \
                                    self.parameterDict["rohrfaktor"]
            lineThickness = self.parameterDict["rohrdicke"] * elementSizeFaktor
            stift = QtGui.QPen(brush, lineThickness, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
            myLine.setPen(stift)
            myText = QtWidgets.QGraphicsSimpleTextItem()
            myText.setText(element["id"].upper())
            myText.setAcceptedMouseButtons(QtCore.Qt.NoButton)
            self.myStandFont.setPointSize(self.parameterDict["textdicke"])
            myText.setFont(self.myStandFont)
            shiftInX = myText.boundingRect().center().x()
            shiftInY = myText.boundingRect().center().y()
            Xposition = (start[0] + ende[0]) / 2
            Yposition = (start[1] + ende[1]) / 2
            myText.setPos((-shiftInX + Xposition), (-shiftInY + Yposition))
            myLine.text = myText
            bypassStatesBool = False
            if "bypass-states" in element.keys():
                bypassStatesBool = True
            openStatesBool = False
            if "opening-states" in element.keys():
                openStatesBool = True
            myLine.symbols = self.symbolFunktion(start[0], start[1], ende[0], ende[1], openStatesBool, bypassStatesBool)
            self.AlleStriche.append(myLine)
            self.AlleTexte.append(myText)
            #self.AllePfeile.append(arrow1)
            #self.AllePfeile.append(arrow2)
            self.scene.addItem(myLine)
            for key, symbol in myLine.symbols.items():
                self.scene.addItem(symbol)
                symbol.hide()

            #self.scene.addItem(arrow1)
            #self.scene.addItem(arrow2)
            self.scene.addItem(myText)
            if not myLine.data4element["showName"]:
                myLine.text.hide()
        for i in range(len(self.nodes)):
            elem = self.nodes[i]
            myText = QtWidgets.QGraphicsSimpleTextItem()
            myText.setText(elem["id"].upper())
            myText.setFont(self.myStandFont)
            shiftInX = myText.boundingRect().center().x()
            shiftInY = myText.boundingRect().center().y()
            myText.setPos(self.parameterDict["switchXDirection"] * elem["x"],
                          self.parameterDict["switchYDirection"] * elem["y"],
                          )
            myText.setAcceptedMouseButtons(QtCore.Qt.NoButton)
            size = self.parameterDict["rohrdicke"]
            myNode = ClickableCircle4Nodes(x=(-size + self.parameterDict["switchXDirection"] * elem["x"]),
                                           y=(-size + self.parameterDict["switchYDirection"] * elem["y"]),
                                           size=(2 * size),
                                           pointer=i,
                                           parent=self)
            myNode.text = myText
            myNode.setPen(self.invisablePen)
            myNode.setBrush(self.invisibleBrush)
            myNode.x = self.parameterDict["switchXDirection"] * elem["x"]
            myNode.y = self.parameterDict["switchYDirection"] * elem["y"]
            self.AllePunkte.append(myNode)
            self.AlleTexte.append(myText)
            self.scene.addItem(myText)
            self.scene.addItem(myNode)
            if not elem["showName"]:
                myNode.text.hide()
        self.timeSlider.setMaximum(len(self.times4Results) - 1)
        self.timeSlider.setSliderPosition(0)
        self.recolor()
        self.ansicht.fitInView(self.scene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)

    # def arrowFunktion(self, x1, y1, x2, y2, values):  # this function will be replaced by self.symbolFunktion()
    #     grFaktor = self.parameterDict["rohrdicke"] * self.parameterDict["arrowSize"] / 10.0
    #     rx = (x1 - x2)
    #     ry = (y1 - y2)
    #     if abs(values[0]) < self.parameterDict["minFlowAnzeige"]:
    #         nx = 0
    #         ny = 0
    #     elif values[0] < 0 and values[1] < 0:
    #         nx = rx / max(sqrt(rx ** 2 + ry ** 2), 0.1)
    #         ny = ry / max(sqrt(rx ** 2 + ry ** 2), 0.1)
    #     elif values[0] > 0 and values[1] > 0:
    #         nx = -rx / max(sqrt(rx ** 2 + ry ** 2), 0.1)
    #         ny = -ry / max(sqrt(rx ** 2 + ry ** 2), 0.1)
    #     else:
    #         nx = 0
    #         ny = 0
    #     mx1 = (x1 + x2) / 2 - ny * grFaktor - 0.5 * nx * grFaktor
    #     my1 = (y1 + y2) / 2 + nx * grFaktor - 0.5 * ny * grFaktor
    #     mx2 = (x1 + x2) / 2 + 0.5 * nx * grFaktor
    #     my2 = (y1 + y2) / 2 + 0.5 * ny * grFaktor
    #     mx3 = (x1 + x2) / 2 + ny * grFaktor - 0.5 * nx * grFaktor
    #     my3 = (y1 + y2) / 2 - nx * grFaktor - 0.5 * ny * grFaktor
    #     arrow1 = QtWidgets.QGraphicsLineItem(mx1, my1, mx2, my2)
    #     pen = arrow1.pen()
    #     pen.setWidthF(self.parameterDict["rohrdicke"] / 2.0 * self.parameterDict["arrowThickness"] / 10.0)
    #     arrow1.setPen(pen)
    #     arrow2 = QtWidgets.QGraphicsLineItem(mx2, my2, mx3, my3)
    #     arrow2.setPen(pen)
    #     return arrow1, arrow2

    def symbolFunktion(self, x1, y1, x2, y2, openStatesBool, bypassStatesBool):  # function to draw all needed symbols on each line
        symbols = {}
        lineThickness = self.parameterDict["rohrdicke"] / 2.0 * self.parameterDict["symbolThickness"] / 10.0
        grFaktor = self.parameterDict["rohrdicke"] * self.parameterDict["symbolSize"] / 10.0
        # positive direction
        rx = (x2 - x1)
        ry = (y2 - y1)
        nx = rx / max(sqrt(rx ** 2 + ry ** 2), 0.1)
        ny = ry / max(sqrt(rx ** 2 + ry ** 2), 0.1)
        mx1 = (x1 + x2) * 0.5 - ny * grFaktor - 0.5 * nx * grFaktor
        my1 = (y1 + y2) * 0.5 + nx * grFaktor - 0.5 * ny * grFaktor
        mx2 = (x1 + x2) * 0.5 + 0.5 * nx * grFaktor
        my2 = (y1 + y2) * 0.5 + 0.5 * ny * grFaktor
        mx3 = (x1 + x2) * 0.5 + ny * grFaktor - 0.5 * nx * grFaktor
        my3 = (y1 + y2) * 0.5 - nx * grFaktor - 0.5 * ny * grFaktor
        positivFlow = QtWidgets.QGraphicsPolygonItem(QtGui.QPolygonF([QtCore.QPointF(mx1, my1),
                                                                      QtCore.QPointF(mx2, my2),
                                                                      QtCore.QPointF(mx3, my3)
                                                                      ]))
        positivFlow.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 255),
                                      lineThickness,
                                      QtCore.Qt.SolidLine))
        positivFlow.setBrush(self.invisibleBrush)
        symbols["positiveFlow"] = positivFlow
        if bypassStatesBool:
            activeStateTriangle = QtWidgets.QGraphicsPolygonItem(QtGui.QPolygonF([QtCore.QPointF(mx1, my1),
                                                                                  QtCore.QPointF(mx2, my2),
                                                                                  QtCore.QPointF(mx3, my3)
                                                                                  ]))
            activeStateTriangle.setPen(QtGui.QPen(QtGui.QColor(0, 0, 255, 255),
                                                  lineThickness,
                                                  QtCore.Qt.SolidLine))
            activeStateTriangle.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 255, 255), QtCore.Qt.SolidPattern))
            symbols["activeState"] = activeStateTriangle
        # negative direction
        mx1 = (x1 + x2) * 0.5 + ny * grFaktor + 0.5 * nx * grFaktor
        my1 = (y1 + y2) * 0.5 - nx * grFaktor + 0.5 * ny * grFaktor
        mx2 = (x1 + x2) * 0.5 - 0.5 * nx * grFaktor
        my2 = (y1 + y2) * 0.5 - 0.5 * ny * grFaktor
        mx3 = (x1 + x2) * 0.5 - ny * grFaktor + 0.5 * nx * grFaktor
        my3 = (y1 + y2) * 0.5 + nx * grFaktor + 0.5 * ny * grFaktor
        negativFlow = QtWidgets.QGraphicsPolygonItem(QtGui.QPolygonF([QtCore.QPointF(mx1, my1),
                                                                      QtCore.QPointF(mx2, my2),
                                                                      QtCore.QPointF(mx3, my3)
                                                                      ]))
        negativFlow.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 255),
                                      lineThickness,
                                      QtCore.Qt.SolidLine))
        negativFlow.setBrush(self.invisibleBrush)
        symbols["negativeFlow"] = negativFlow
        # without direction
        if openStatesBool:
            closedStateCircle = CircleWithCross(x1, x2, y1, y2, lineThickness, grFaktor)
            symbols["closedState"] = closedStateCircle
        return symbols

    def recolor(self):
        zeit = int(self.timeSlider.value())
        self.timeLabel.setText("Time: {}".format(self.secondsToClocktime(int(self.times4Results[zeit]))))
        self.timeLabel.repaint()
        diameters = [elem["diameter"] for elem in self.elements if elem["diameter"] is not None]
        for i, r in enumerate(self.elements):
            start = \
                [(self.parameterDict["switchXDirection"] * kno["x"], self.parameterDict["switchYDirection"] * kno["y"])
                 for
                 kno in self.nodes if kno["id"] == r["von"]][0]
            ende = \
                [(self.parameterDict["switchXDirection"] * kno["x"], self.parameterDict["switchYDirection"] * kno["y"])
                 for
                 kno in self.nodes if kno["id"] == r["nach"]][0]
            if self.PressOrFlow == "pressure":
                currentValues = r["valuesPressure"][zeit]
                brush = self.valuesToGradientBrush(currentValues, (start, ende))
            else:
                currentValues = r["valuesFlow"][zeit]
                brush = self.valuesToGradientBrush(currentValues, (start, ende))

            self.AlleStriche[i].setToolTip(
                "{}\n diameter {}, length {} \n von {} nach {}\n Drücke:\n wert {}  wert {}\n Flüsse:\n wert {}  wert {}".format(
                    r["id"],
                    r["diameter"],
                    r["length"],
                    r["von"],
                    r["nach"],
                    r["valuesPressure"][zeit][0],
                    r["valuesPressure"][zeit][1],
                    r["valuesFlow"][zeit][0],
                    r["valuesFlow"][zeit][1],
                ))
            if r["diameter"] is None:
                elementSizeFaktor = 1
            elif min(diameters) == max(diameters):
                elementSizeFaktor = 1
            else:
                transform2NullEins = (r["diameter"] - min(diameters)) / float(max(diameters) - min(diameters))
                elementSizeFaktor = transform2NullEins * float(2 * self.parameterDict["rohrfaktor"]) + 1 - \
                                    self.parameterDict["rohrfaktor"]
            lineThickness = self.parameterDict["rohrdicke"] * elementSizeFaktor
            stift = QtGui.QPen(brush, lineThickness, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
            self.AlleStriche[i].setPen(stift)
            for key, symbol in self.AlleStriche[i].symbols.items():
                symbol.hide()
            noSymbol = True
            if "opening-states" in r.keys():
                if r["opening-states"][zeit] == 0:
                    self.AlleStriche[i].symbols["closedState"].show()
                    noSymbol = False
                elif "bypass-states" in r.keys():
                    if r["bypass-states"][zeit] == 0:
                        self.AlleStriche[i].symbols["activeState"].show()
                        noSymbol = False
            if noSymbol:
                if (r["valuesFlow"][zeit][0] >= 0 and r["valuesFlow"][zeit][1] >= 0) or\
                        (r["valuesFlow"][zeit][0] <= 0 and r["valuesFlow"][zeit][1] <= 0):
                    if max(abs(r["valuesFlow"][zeit][0]), abs(r["valuesFlow"][zeit][1]) ) >=\
                           self.parameterDict["minFlowAnzeige"]:
                        if r["valuesFlow"][zeit][0] >= 0:
                            self.AlleStriche[i].symbols["positiveFlow"].show()
                        else:
                            self.AlleStriche[i].symbols["negativeFlow"].show()
        for node in self.AllePunkte:
            node.setRect(node.x - self.parameterDict["rohrdicke"],
                         node.y - self.parameterDict["rohrdicke"],
                         2 * self.parameterDict["rohrdicke"],
                         2 * self.parameterDict["rohrdicke"])
        self.ansicht.repaint()
        self.ansicht.show()
        self.fun4ColorBarContruction()

    def farbenAusw1(self):
        num, ok = QtWidgets.QInputDialog.getInt(self, "How many colors", "Choose how many colors you want for pressure",
                                                min=2)
        if ok and num > 1:
            self.farbenPressure = []
            for k in range(0, num):
                pickedColor = QtWidgets.QColorDialog.getColor()
                self.farbenPressure.append(pickedColor)
            self.recolor()

    def farbenAusw2(self):
        num, ok = QtWidgets.QInputDialog.getInt(self, "How many colors", "Choose how many colors you want for flow",
                                                min=2)
        if ok and num > 1:
            self.farbenFlow = []
            for k in range(0, num):
                pickedColor = QtWidgets.QColorDialog.getColor()
                self.farbenFlow.append(pickedColor)
            self.recolor()

    def fun4ParameterDialog(self):
        self.parameterDict = GraphicalParameterAuswahlDialog.returnParameter(self,
                                                                             parameterDict=self.parameterDict)
        self.updateConfig()

    def valuesToGradientBrush(self, values, koords):
        # TODO change valuesToGradientBrush to match new design of not beeing uniformly devided
        #     but instead having self choosen points for each color in between the outer most colors
        if abs(values[0]) < abs(values[1]):
            startVal = abs(values[0])
            endVal = abs(values[1])  # flowVal might be negative, orientation not shown
            (x1, y1), (x2, y2) = koords
        else:
            startVal = abs(values[1])
            endVal = abs(values[0])  # flowVal might be negative, orientation not shown
            (x2, y2), (x1, y1) = koords
        linGrad = QtGui.QLinearGradient(x1, y1, x2, y2)
        if self.PressOrFlow == "pressure":
            gewicht1 = (startVal - self.minPVal) / (self.maxPVal - self.minPVal)
            gewicht2 = (endVal - self.minPVal) / (self.maxPVal - self.minPVal)
            if len(self.farbenPressure) == 2:
                (tmpR, tmpG, tmpB) = self.gewichtToRGB(gewicht1, self.farbenPressure)
                linGrad.setColorAt(0, QtGui.QColor(tmpR, tmpG, tmpB, 255))
                (tmpR, tmpG, tmpB) = self.gewichtToRGB(gewicht2, self.farbenPressure)
                linGrad.setColorAt(1, QtGui.QColor(tmpR, tmpG, tmpB, 255))
            if len(self.farbenPressure) > 2:
                anzF = len(self.farbenPressure)
                breakit = False
                for k in range(1, anzF):
                    if gewicht1 < k / (anzF - 1) or k == anzF - 1:
                        ngew = (anzF - 1) * (gewicht1 - (k - 1) / (anzF - 1))
                        (tmpR, tmpG, tmpB) = self.gewichtToRGB(ngew,
                                                               [self.farbenPressure[k - 1],
                                                                self.farbenPressure[k]])
                        linGrad.setColorAt(0, QtGui.QColor(tmpR, tmpG, tmpB, 255))
                        for m in range(k, anzF):
                            if gewicht2 < m / (anzF - 1) or m == anzF - 1:
                                ngew2 = (anzF - 1) * (gewicht2 - (m - 1) / (anzF - 1))
                                (tmpR2, tmpG2, tmpB2) = self.gewichtToRGB(ngew2,
                                                                          [self.farbenPressure[m - 1],
                                                                           self.farbenPressure[m]])
                                linGrad.setColorAt(1, QtGui.QColor(tmpR2, tmpG2, tmpB2, 255))
                                for s in range(k, m):
                                    neuPosi = ((s / (anzF - 1)) - gewicht1) / (gewicht2 - gewicht1)
                                    linGrad.setColorAt(neuPosi, self.farbenPressure[s])
                                breakit = True
                            if breakit: break
                    if breakit: break
        else:  # this is the flow case
            gewicht1 = (startVal - self.minFVal) / (self.maxFVal - self.minFVal)
            gewicht2 = (endVal - self.minFVal) / (self.maxFVal - self.minFVal)
            if len(self.farbenFlow) == 2:
                (tmpR, tmpG, tmpB) = self.gewichtToRGB(gewicht1, self.farbenFlow)
                linGrad.setColorAt(0, QtGui.QColor(tmpR, tmpG, tmpB, 255))
                (tmpR, tmpG, tmpB) = self.gewichtToRGB(gewicht2, self.farbenFlow)
                linGrad.setColorAt(1, QtGui.QColor(tmpR, tmpG, tmpB, 255))
            if len(self.farbenFlow) > 2:
                anzF = len(self.farbenFlow)
                breakit = False
                for k in range(1, anzF):
                    if gewicht1 < k / (anzF - 1) or k == anzF - 1:
                        ngew = (anzF - 1) * (gewicht1 - (k - 1) / (anzF - 1))
                        (tmpR, tmpG, tmpB) = self.gewichtToRGB(ngew,
                                                               [self.farbenFlow[k - 1],
                                                                self.farbenFlow[k]])
                        linGrad.setColorAt(0, QtGui.QColor(tmpR, tmpG, tmpB, 255))
                        for m in range(k, anzF):
                            if gewicht2 < m / (anzF - 1) or m == anzF - 1:
                                ngew2 = (anzF - 1) * (gewicht2 - (m - 1) / (anzF - 1))
                                (tmpR2, tmpG2, tmpB2) = self.gewichtToRGB(ngew2,
                                                                          [self.farbenFlow[m - 1],
                                                                           self.farbenFlow[m]])
                                linGrad.setColorAt(1, QtGui.QColor(tmpR2, tmpG2, tmpB2, 255))
                                for s in range(k, m):
                                    neuPosi = ((s / (anzF - 1)) - gewicht1) / (gewicht2 - gewicht1)
                                    linGrad.setColorAt(neuPosi, self.farbenFlow[s])
                                breakit = True
                            if breakit: break
                    if breakit: break
        brush = QtGui.QBrush(linGrad)
        return brush

    def gewichtToRGB(self, gewicht, farben):
        (tmpR, tmpG, tmpB) = (round((farben[1].red() - farben[0].red()) * gewicht)
                              + farben[0].red(),
                              round((farben[1].green() - farben[0].green()) * gewicht)
                              + farben[0].green(),
                              round((farben[1].blue() - farben[0].blue()) * gewicht)
                              + farben[0].blue())
        return (tmpR, tmpG, tmpB)

    def fun4ColorBarContruction(self):
        self.sceneColorBar.clear()
        rectangle = QtWidgets.QGraphicsRectItem(-10, -10, 50, 1000)
        if self.PressOrFlow == "pressure":
            tmpBrush = self.valuesToGradientBrush((self.minPVal, self.maxPVal), ((25, 1000), (25, -10)))
            self.colorMapBarLabelTop.setText("{}".format(self.maxPVal))
            self.colorMapBarLabelBottom.setText("{}".format(self.minPVal))
        else:
            tmpBrush = self.valuesToGradientBrush((self.minFVal, self.maxFVal), ((25, 1000), (25, -10)))
            self.colorMapBarLabelTop.setText("{}".format(self.maxFVal))
            self.colorMapBarLabelBottom.setText("{}".format(self.minFVal))
        rectangle.setBrush(tmpBrush)
        self.sceneColorBar.addItem(rectangle)

    def autoPlay(self):
        self.boolPlay = True
        self.nextTimeFrame()

    def autoPause(self):
        self.boolPlay = False

    def nextTimeFrame(self):
        if self.boolPlay:
            i = self.timeSlider.sliderPosition() + 1
            if i == (len(self.times4Results)):
                i = 0
            self.timeSlider.setSliderPosition(i)
            # calculate waiting time using SpeedVar and time differenz
            if i == (len(self.times4Results) - 1):
                if self.parameterDict["autoReplay"]:
                    self.videoTimer.start(int(self.parameterDict["autoReplayTimerInSek"] * 1000))
                else:
                    self.boolPlay = False
            else:
                timeFactor = float(self.times4Results[i + 1] - self.times4Results[i]) / float(
                    self.parameterDict["standardTimeIntervall"])
                self.videoTimer.start(int(1000 / self.parameterDict["wiedergabeSpeedVar"] * timeFactor))

    def secondsToClocktime(self, secVal):
        return str(datetime.timedelta(seconds=secVal))

    def fun4ReadInputDictonary(self, fileTimes, fileUnits, fileNodes, fileElements):
        # reads Dictonaries from yaml files
        with open(fileTimes) as inputTimes:
            self.times4Results = yaml.load(inputTimes, Loader=yaml.SafeLoader)
        with open(fileNodes) as inputNodes:
            self.nodes = yaml.load(inputNodes, Loader=yaml.SafeLoader)
        with open(fileElements) as inputElements:
            self.elements = yaml.load(inputElements, Loader=yaml.SafeLoader)
        with open(fileUnits) as inputUnits:
            self.units = yaml.load(inputUnits, Loader=yaml.SafeLoader)

    def fun4ExportColorBar2png(self):
        pass
        # TODO change this for colorBar and build a subfunction to avoid code redundencies

        # image = QtGui.QImage(self.ansicht.size(), QtGui.QImage.Format_ARGB32_Premultiplied)
        # image.fill(QtGui.QColor(255, 255, 255, 0))
        # pen = QtGui.QPainter(image)
        # self.ansicht.render(pen)
        # del pen
        # scaledImage = image.scaled(1024, 768, 1)
        # options = QtWidgets.QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        # filePicture, selectedFilter = QtWidgets.QFileDialog.getSaveFileName(self,
        #                                                                caption="save image as smal PNG",
        #                                                                filter="image file (*.png)",
        #                                                                options=options)
        # if filePicture != "":
        #     if filePicture[:-4] != ".png" or len(filePicture) < 5:
        #         filePicture = filePicture+".png"
        #     scaledImage.save(filePicture)

    def fun4Export2PNGSmal(self):
        image = QtGui.QImage(self.ansicht.size(), QtGui.QImage.Format_ARGB32_Premultiplied)
        image.fill(QtGui.QColor(255, 255, 255, 0))
        pen = QtGui.QPainter(image)
        self.ansicht.render(pen)
        del pen
        scaledImage = image.scaled(1024, 768, 1)
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filePicture, selectedFilter = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                            caption="save image as smal PNG",
                                                                            filter="image file (*.png)",

                                                                            options=options)
        if filePicture != "":
            if filePicture[:-4] != ".png" or len(filePicture) < 5:
                filePicture = filePicture + ".png"
            scaledImage.save(filePicture)

    def fun4Export2PNGBig(self):
        image = QtGui.QImage(self.ansicht.size(), QtGui.QImage.Format_ARGB32_Premultiplied)
        image.fill(QtGui.QColor(255, 255, 255, 0))
        pen = QtGui.QPainter(image)
        self.ansicht.render(pen)
        del pen
        scaledImage = image.scaled(1920, 1080, 1)
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filePicture, selectedFilter = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                            caption="save image as big PNG",
                                                                            filter="image file (*.png)",
                                                                            options=options)
        if filePicture != "":
            if filePicture[:-4] != ".png" or len(filePicture) < 5:
                filePicture = filePicture + ".png"
            scaledImage.save(filePicture)

    def fun4Export2PNGCustom(self):
        imageW, ok = QtWidgets.QInputDialog.getInt(self, "enter INT", "enter width for image", 500, 100)
        if ok:
            imageH, ok = QtWidgets.QInputDialog.getInt(self, "enter INT", "enter height for image", 500, 100)
            if ok:
                image = QtGui.QImage(self.ansicht.size(), QtGui.QImage.Format_ARGB32_Premultiplied)
                image.fill(QtGui.QColor(255, 255, 255, 0))
                pen = QtGui.QPainter(image)
                self.ansicht.render(pen)
                del pen
                scaledImage = image.scaled(imageW, imageH, 1)
                options = QtWidgets.QFileDialog.Options()
                options |= QtWidgets.QFileDialog.DontUseNativeDialog
                filePicture, selectedFilter = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                                    "save image as custom PNG",
                                                                                    directory="",
                                                                                    filter="image file (*.png)",
                                                                                    options=options)
                if filePicture != "":
                    if filePicture[:-4] != ".png" or len(filePicture) < 5:
                        filePicture = filePicture + ".png"
                    scaledImage.save(filePicture)


# opens the ResultViewer with needed dictonaries or with paths for needed *.yaml files (*.RVConfig.yaml is optional)
def viewResults(pathTimes, pathNodes, pathElements, pathUnits, pathRVConfig = None):
    if isinstance(pathTimes, str):
        with open(pathTimes, mode="r") as times, open(pathNodes, mode="r") as nodes, \
                open(pathElements, mode="r") as elements, open(pathUnits, mode="r") as units:
            openedFiles = {"times": yaml.load(times, Loader=yaml.SafeLoader),
                           "nodes": yaml.load(nodes, Loader=yaml.SafeLoader),
                           "elements": yaml.load(elements, Loader=yaml.SafeLoader),
                           "units": yaml.load(units, Loader=yaml.SafeLoader)}
    else:
        openedFiles = {"times": pathTimes,
                       "nodes": pathNodes,
                       "elements": pathElements,
                       "units": pathUnits}
    if pathRVConfig is not None:
        if isinstance(pathRVConfig, str):
            with open(pathRVConfig, mode="r") as RVConfig:
                openedFiles["RVConfig"] = yaml.load(RVConfig, Loader=yaml.SafeLoader)
        else:
            openedFiles["RVConfig"] = pathRVConfig
    else:
        openedFiles["RVConfig"] = None

    app = QtWidgets.QApplication(sys.argv)
    gui = ResultViewer(openedFiles=openedFiles)
    sys.exit(app.exec_())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = ResultViewer()
    sys.exit(app.exec_())
