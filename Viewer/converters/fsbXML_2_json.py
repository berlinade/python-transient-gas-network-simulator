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

import lxml.etree as ET
from PyQt5 import QtCore, QtGui, QtWidgets
import json

class guiConverter(QtWidgets.QMainWindow):


    def __init__(self, parent = None):
        super(guiConverter,self).__init__(parent)
        self.initUI()                                                                  ## initializes the Main Window ##


    def initUI(self):                                                                  ## initializes the Main Window ##
        self.MainViewWindow = QtWidgets.QWidget(self)
        self.setCentralWidget(self.MainViewWindow)
        self.setWindowTitle("CONVERT 4 RESULTVIEWER")
        self.setGeometry(0, 0, 400, 400)

        self.meinLayout = QtWidgets.QVBoxLayout()
        self.ButtonNetworkOnly = QtWidgets.QPushButton("Convert Network only from *.net")
        self.ButtonNetworkOnly.clicked.connect(self.Fun4ChooseNetzwork)
        self.meinLayout.addWidget(self.ButtonNetworkOnly)
        self.ButtonNetworkWithResult = QtWidgets.QPushButton("Convert Network with Result from *.net and *.result")
        self.ButtonNetworkWithResult.clicked.connect(self.Fun4ChooseFiles)
        self.meinLayout.addWidget(self.ButtonNetworkWithResult)

        self.MainViewWindow.setLayout(self.meinLayout)
        self.statusBar().showMessage('Ready')


    def Fun4ChooseNetzwork(self):                              ## import new data from the file choosen by the dialog ##
        self.fileNetwork = None
        self.times4Results = []
        self.nodes = []
        self.elements = []
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        self.fileNetwork, ok = QtWidgets.QFileDialog.getOpenFileName(self,
                                                           "select *.net file of your network",
                                                           "","Network Files (*.net)", options=options)
        if ok:
            self.Fun4ReadInputNetworkOnly(self.fileNetwork)
            json_file1 = open(self.fileNetwork[:-3]+"times", 'w')
            json.dump(self.times4Results, json_file1, indent = 4)
            json_file2 = open(self.fileNetwork[:-3] + "nodes", 'w')
            json.dump(self.nodes, json_file2, indent = 4)
            json_file3 = open(self.fileNetwork[:-3] + "elements", 'w')
            json.dump(self.elements, json_file3, indent = 4)
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Finished converting files.")
            msgBox.exec()
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("You need to select a *.net file.")
            msgBox.exec()


    def Fun4ChooseFiles(self):                                ## import new data from the files choosen by the dialog ##
        self.fileNetwork = None
        self.fileResult = None
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        self.fileNetwork, ok = QtWidgets.QFileDialog.getOpenFileName(self,
                                                           "select *.net file of your network",
                                                           "","Network Files (*.net)", options=options)
        if ok:
            self.fileResult, ok = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                  "select *.result file of your network",
                                                                  "","Result Files (*.result)", options=options)
            if ok:
                self.Fun4ReadInputData(self.fileNetwork, self.fileResult)
                json_file1 = open(self.fileNetwork[:-3] + "times", 'w')
                json.dump(self.times4Results, json_file1, indent = 4)
                json_file2 = open(self.fileNetwork[:-3] + "nodes", 'w')
                json.dump(self.nodes, json_file2, indent = 4)
                json_file3 = open(self.fileNetwork[:-3] + "elements", 'w')
                json.dump(self.elements, json_file3, indent = 4)
                msgBox = QtWidgets.QMessageBox()
                msgBox.setText("Finished converting files.")
                msgBox.exec()
            else:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setText("You need to select a *.result file.")
                msgBox.exec()
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("You need to select a *.net file.")
            msgBox.exec()


    def Fun4ReadInputNetworkOnly(self, fileNetwork):
        nodes = []
        knoPoint = {}
        nodesZahl = 0
        elements = []
        roPoint = {}
        rohrZahl = 0
        times4Results = []

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.statusBar().insertPermanentWidget(0, self.progressBar, 1)

        parser1 = ET.XMLParser(encoding="utf-8")
        tree1 = ET.parse(fileNetwork, parser=parser1)
        root1 = tree1.getroot()

        self.counter = 0
        self.maxcounter = len(root1.getchildren())

        for child in root1:
            self.counter = self.counter+1
            newValue = float(self.counter) / self.maxcounter * 100
            self.progressBar.setValue(int(newValue))
            self.progressBar.update()

            if ET.QName(child).localname == "nodes":
                for candy in child:
                    if "boundaryNode" in candy.tag:
                        nodes.append({"id":candy.attrib["id"], "x":float(candy.attrib["x"]), "y":-float(candy.attrib["y"]),
                                       "valuesPressure":[0.5], "showName":True})
                        knoPoint[candy.attrib["id"]] = nodesZahl
                        nodesZahl = nodesZahl+1
                    elif "innode" in candy.tag:
                        nodes.append({"id":candy.attrib["id"], "x":float(candy.attrib["x"]), "y":-float(candy.attrib["y"]),
                                       "valuesPressure":[0.5], "showName":False})
                        knoPoint[candy.attrib["id"]] = nodesZahl
                        nodesZahl = nodesZahl+1
            elif ET.QName(child).localname == "connections":
                for candy in child:
                    if ET.QName(candy).localname == "pipe":
                        for sugar in candy:
                            if ET.QName(sugar).localname == "diameter":
                                diameter = sugar.attrib["value"]
                            elif ET.QName(sugar).localname == "length":
                                length = sugar.attrib["value"]
                        if "diameter" not in [ET.QName(sugar).localname for sugar in candy]:
                                diameter = None
                        if "length" not in [ET.QName(sugar).localname for sugar in candy]:
                                length = None
                        elements.append({"id":candy.attrib["id"],
                                         "von":candy.attrib["from"],
                                         "nach":candy.attrib["to"],
                                         "diameter": float(diameter),
                                         "length": float(length),
                                         "valuesFlow":[(0.5,0.5)],
                                         "valuesPressure":[(0.5,0.5)],
                                         "showName":False})
                        roPoint[candy.attrib["id"]] = rohrZahl
                        rohrZahl = rohrZahl+1
                    elif ET.QName(candy).localname in ["compressorStation","valve","controlValve","resistor"]:
                        for sugar in candy:
                            if ET.QName(sugar).localname == "diameter":
                                diameter = sugar.attrib["value"]
                            elif ET.QName(sugar).localname == "length":
                                length = sugar.attrib["value"]
                        if "diameter" not in [ET.QName(sugar).localname for sugar in candy]:
                                diameter = None
                        if "length" not in [ET.QName(sugar).localname for sugar in candy]:
                                length = None
                        elements.append({"id":candy.attrib["id"],
                                         "von":candy.attrib["from"],
                                         "nach":candy.attrib["to"],
                                         "diameter": diameter,
                                         "length": length,
                                         "valuesFlow":[(0.5,0.5)],
                                         "valuesPressure":[(0.5,0.5)],
                                         "showName":True})
                        roPoint[candy.attrib["id"]] = rohrZahl
                        rohrZahl = rohrZahl+1

        self.times4Results = [0]
        self.nodes = nodes
        self.elements = elements
#        print(self.nodes)
#        print(self.elements)
        self.statusBar().removeWidget(self.progressBar)


    def Fun4ReadInputData(self, fileNetwork, fileResult):
        nodes = []
        knoPoint = {}
        nodesZahl = 0
        elements = []
        roPoint = {}
        rohrZahl = 0
        times4Results = []

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.statusBar().insertPermanentWidget(0, self.progressBar, 1)

        parser1 = ET.XMLParser(encoding="utf-8")
        tree1 = ET.parse(fileNetwork, parser=parser1)
        root1 = tree1.getroot()

        parser2 = ET.XMLParser(encoding="utf-8")
        tree2 = ET.parse(fileResult, parser=parser2)
        root2 = tree2.getroot()

        self.counter = 0
        self.maxcounter = len(root1.getchildren())+len(root2.getchildren())

        for child in root1:
            self.counter = self.counter+1
            newValue = float(self.counter) / self.maxcounter * 100
            self.progressBar.setValue(int(newValue))
            self.progressBar.update()
            if ET.QName(child).localname == "nodes":
                for candy in child:
                    if "boundaryNode" in candy.tag:
                        nodes.append({"id":candy.attrib["id"], "x":float(candy.attrib["x"]), "y":-float(candy.attrib["y"]),
                                       "valuesPressure":[], "showName":True})
                        knoPoint[candy.attrib["id"]] = nodesZahl
                        nodesZahl = nodesZahl+1
                    elif "innode" in candy.tag:
                        nodes.append({"id":candy.attrib["id"], "x":float(candy.attrib["x"]), "y":-float(candy.attrib["y"]),
                                       "valuesPressure":[], "showName":False})
                        knoPoint[candy.attrib["id"]] = nodesZahl
                        nodesZahl = nodesZahl+1
            elif ET.QName(child).localname == "connections":
                for candy in child:
                    if ET.QName(candy).localname == "pipe":
                        for sugar in candy:
                            if ET.QName(sugar).localname == "diameter":
                                diameter = sugar.attrib["value"]
                            elif ET.QName(sugar).localname == "length":
                                length = sugar.attrib["value"]
                        if "diameter" not in [ET.QName(sugar).localname for sugar in candy]:
                                diameter = None
                        if "length" not in [ET.QName(sugar).localname for sugar in candy]:
                                length = None
                        elements.append({"id":candy.attrib["id"],
                                         "von":candy.attrib["from"],
                                         "nach":candy.attrib["to"],
                                         "diameter": float(diameter),
                                         "length": float(length),
                                         "valuesFlow":[],
                                         "valuesPressure":[],
                                         "showName":False})
                        roPoint[candy.attrib["id"]] = rohrZahl
                        rohrZahl = rohrZahl+1
                    elif ET.QName(candy).localname in ["compressorStation","valve","controlValve","resistor"]:
                        for sugar in candy:
                            if ET.QName(sugar).localname == "diameter":
                                diameter = sugar.attrib["value"]
                            elif ET.QName(sugar).localname == "length":
                                length = sugar.attrib["value"]
                        if "diameter" not in [ET.QName(sugar).localname for sugar in candy]:
                                diameter = None
                        if "length" not in [ET.QName(sugar).localname for sugar in candy]:
                                length = None
                        elements.append({"id":candy.attrib["id"],
                                         "von":candy.attrib["from"],
                                         "nach":candy.attrib["to"],
                                         "diameter": diameter,
                                         "length": length,
                                         "valuesFlow":[],
                                         "valuesPressure":[],
                                         "showName":True})
                        roPoint[candy.attrib["id"]] = rohrZahl
                        rohrZahl = rohrZahl+1
        for child in root2:
            self.counter = self.counter+1
            newValue = float(self.counter) / self.maxcounter *100
            self.progressBar.setValue(int(newValue))

            if ET.QName(child).localname == "state": # "state" in child.tag.split("}")[len(child.tag.split("}"))-1] :
                times4Results.append(float(child[0][0].attrib["value"]))
                kno = child[1]
                cons = child[2]
                for elem in cons:
                    if ET.QName(elem).localname == "pipeState":
                        val1 = float( elem[0][0].attrib["value"] )
                        val2 = float( elem[0][1].attrib["value"] )
                        elements[roPoint[elem.attrib["id"]]]["valuesFlow"].append( (val1,val2) )
                    elif ET.QName(elem).localname == "compressorStationState":
                        val1 = float( elem[0].attrib["value"] )
                        val2 = float( elem[1].attrib["value"] )
                        elements[roPoint[elem.attrib["id"]]]["valuesFlow"].append( (val1,val2) )
                    elif ET.QName(elem).localname == "valve":
                        val1 = float( elem[0].attrib["value"] )
                        val2 = float( elem[1].attrib["value"] )
                        elements[roPoint[elem.attrib["id"]]]["valuesFlow"].append( (val1,val2) )
                    elif ET.QName(elem).localname == "controlValve":
                        val1 = float( elem[0].attrib["value"] )
                        val2 = float( elem[1].attrib["value"] )
                        elements[roPoint[elem.attrib["id"]]]["valuesFlow"].append( (val1,val2) )
                    elif ET.QName(elem).localname == "resistor":
                        val1 = float( elem[0].attrib["value"] )
                        val2 = float( elem[0].attrib["value"] )
                        elements[roPoint[elem.attrib["id"]]]["valuesFlow"].append( (val1,val2) )
                for elem in kno:
                    for child in elem:
                        nodesID = child.attrib["id"]
                        nodes[knoPoint[nodesID]]["valuesPressure"].append( float(child[0].attrib["value"]) )
        for idx, rohr in enumerate(elements): #creates values pressure on each elements based on the values of the nodes
            rohr["valuesPressure"] = list(zip(nodes[knoPoint[elements[idx]["von"]]]["valuesPressure"],
                                                  nodes[knoPoint[elements[idx]["nach"]]]["valuesPressure"]))
        self.times4Results = times4Results
        self.nodes = nodes
        self.elements = elements
        self.statusBar().removeWidget(self.progressBar)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = guiConverter()
    gui.show()
    sys.exit(app.exec_())
