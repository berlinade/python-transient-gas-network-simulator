'''
    part of flow network result viewer
'''

__author__ = ('John Gerick',) # alphabetical order of surnames
__credits__ = ('Tom Streubel',) # alphabetical order of surnames


'''
    imports
    =======
'''
from PyQt5 import QtGui, QtWidgets


class GraphicalParameterAuswahlDialog(QtWidgets.QDialog):

    def __init__(self, parent, parameterDict):
        super(GraphicalParameterAuswahlDialog, self).__init__(parent)
        self.parameterDict = parameterDict
        self.newParameterDict = {}
        for key in parameterDict.keys():
            self.newParameterDict[key] = parameterDict[key]

#        self.subLayoutLine1.addSpacing(20)
#        self.subLayoutLine1.addStretch(1)
#        self.LineEditArrowSize.setValidator(QtGui.QDoubleValidator(bottom = 0.1, decimals = 2))

        self.LabelArrowSize = QtWidgets.QLabel("arrow size")
        self.LabelArrowSize.setToolTip("Change the legth of the smal arrows \n which are added to each element \n " +
                                       "for the direction of flow.\n Standard value is 15")
        self.doubleSpinBoxArrowSize = QtWidgets.QDoubleSpinBox()
        self.doubleSpinBoxArrowSize.setMinimum(0.1)
        self.doubleSpinBoxArrowSize.setSingleStep(0.1)
        self.doubleSpinBoxArrowSize.setDecimals(1)
        self.doubleSpinBoxArrowSize.setValue(self.parameterDict["arrowSize"])
        self.doubleSpinBoxArrowSize.editingFinished.connect(self.update)
        self.subLayoutLine1 = QtWidgets.QHBoxLayout()
        self.subLayoutLine1.addWidget(self.LabelArrowSize)
        self.subLayoutLine1.addWidget(self.doubleSpinBoxArrowSize)

        self.LabelArrowThickness = QtWidgets.QLabel("arrow thickness")
        self.LabelArrowThickness.setToolTip("Change the thickness of the smal arrows \n which are added to each element \n " +
                                       "for the direction of flow.\n Standard value is 4")
        self.doubleSpinBoxArrowThickness = QtWidgets.QDoubleSpinBox()
        self.doubleSpinBoxArrowThickness.setMinimum(0.5)
        self.doubleSpinBoxArrowThickness.setSingleStep(0.1)
        self.doubleSpinBoxArrowThickness.setDecimals(1)
        self.doubleSpinBoxArrowThickness.setValue(self.parameterDict["arrowThickness"])
        self.doubleSpinBoxArrowThickness.editingFinished.connect(self.update)
        self.subLayoutLine2 = QtWidgets.QHBoxLayout()
        self.subLayoutLine2.addWidget(self.LabelArrowThickness)
        self.subLayoutLine2.addWidget(self.doubleSpinBoxArrowThickness)

        self.buttonAnwenden = QtWidgets.QPushButton("Apply", self)
        self.buttonAnwenden.clicked.connect(self.fun4ButtonAnwenden)
        self.buttonAbbruch = QtWidgets.QPushButton("Cancel", self)
        self.buttonAbbruch.clicked.connect(self.fun4ButtonAbbruch)
        self.subLayoutLine9 = QtWidgets.QHBoxLayout()
        self.subLayoutLine9.addWidget(self.buttonAnwenden)
        self.subLayoutLine9.addWidget(self.buttonAbbruch)

        self.meinPADLayout = QtWidgets.QVBoxLayout()
        self.meinPADLayout.addLayout(self.subLayoutLine1)
        self.meinPADLayout.addLayout(self.subLayoutLine2)
        self.meinPADLayout.addLayout(self.subLayoutLine9)
        self.setLayout(self.meinPADLayout)


    def update(self):
        self.newParameterDict["arrowSize"] = self.doubleSpinBoxArrowSize.value()
        self.newParameterDict["arrowThickness"] = self.doubleSpinBoxArrowThickness.value()


    def keyPressEvent(self, keyEvent):
        if (keyEvent == QtGui.QKeySequence.InsertParagraphSeparator):
            pass

    def fun4ButtonAndCoFunctions(self):
        pass #will do the work to change self.newParameterDict

    def fun4ButtonAnwenden(self):
        self.update()
        self.parameterDict = self.newParameterDict
        self.close()

    def fun4ButtonAbbruch(self):
        self.close()

    @classmethod
    def returnParameter(cls, parent, parameterDict):
        dialog = cls(parent, parameterDict)
        dialog.exec_()
        return dialog.parameterDict
