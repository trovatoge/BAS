#Use pythonic API python 2 as well
try:
    import sip
    sip.setapi("QString" , 2)
except:
    pass
    
from PyQt4.QtGui import *
from PyQt4 import QtCore
import sys
import collections
import math
import json
import os

class LastUpdatedOrderedDict(collections.OrderedDict):
    'Store items in the order the keys were last added'
    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        collections.OrderedDict.__setitem__(self, key, value)

class ProjectDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setModal(True)
        self.setWindowTitle("CowLog Project Settings")
        self.setWindowIcon(QIcon('icons/CowLog.png'))
        self.resize(500, 400)
        
        #Buttons
        self.saveButton = QPushButton("Save")
        self.cancelButton = QPushButton("Cancel")
        self.saveButton.setMaximumWidth(80)
        self.cancelButton.setMaximumWidth(80)
        
        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.reject)
        self.buttonLO = QHBoxLayout()
        self.buttonLO.addStretch(0.5)
        self.buttonLO.addWidget(self.saveButton)
        self.buttonLO.addWidget(self.cancelButton)
        self.buttonLO.addStretch(0.5)
        
        #Layout Tabs
        tabWidget = QTabWidget()
        self.layoutGeneralTab()
        self.layoutPlayerTab()
        tabWidget.addTab(self.generalTab, "General Settings")
        tabWidget.addTab(self.playerTab, "Video Player Settings")

        self.mainLO = QVBoxLayout()
        self.mainLO.addWidget(tabWidget)
        self.mainLO.addLayout(self.buttonLO)
        self.setLayout(self.mainLO)
        
    def layoutGeneralTab(self):
        """This function generates the General settings tab"""

        #Dictionary of Inputs from the user, used to build UI
        self.inputs = LastUpdatedOrderedDict()
        self.inputs['name'] = {"label" : "Project Name:", "type" : QLineEdit,  "meta" : ""}
        self.inputs['author'] = {"label" : "Author:", "type" : QLineEdit,  "meta" : ""}
        self.inputs["email"] = {"label" : "E-mail:", "type" : QLineEdit, "meta" : ""}
        self.inputs["videodirectory"] = {"label" : "Video directory:", "type" : QLineEdit, "meta" : "Directory"}
        self.inputs["datadirectory"] = {"label" : "Data directory:", "type" : QLineEdit, "meta" : "Directory"}
        self.inputs["rawcodes"] = {"label" : "Behavioral codes:", "type" : QPlainTextEdit, "meta" : ""}
        self.inputs["usemodifiers"] = {"label" : "Use modifiers:", "type" : QCheckBox, "meta" : ""}
        self.inputs["rawmodified"] = {"label" : "Codes with modifiers:", "type" : QLineEdit, "meta" : ""}
        
        #Form layout for inputs
        self.formLO = QFormLayout()

        #Add text inputs to layout based on dictionary
        for key in self.inputs.keys():
            #Create widget
            self.inputs[key]['widget'] = self.inputs[key]["type"]()

            #Buttons to open directory as labels
            if self.inputs[key]["meta"] == "Directory":
                self.inputs[key]['labelW'] = QPushButton(QIcon("icons/data.png"), self.inputs[key]["label"])
                self.inputs[key]['labelW'].clicked.connect(self.dirDialog)
                #Custom property Output is used in self.dirDialog function
                self.inputs[key]['labelW'].Output = self.inputs[key]["widget"] 
                self.formLO.addRow( self.inputs[key]['labelW'], self.inputs[key]["widget"])
            #Plain text inputs with labels
            else:
                self.formLO.addRow(self.inputs[key]["label"], self.inputs[key]["widget"])

        self.inputs['rawcodes']['widget'].setToolTip("Type in behaviors as comma separated list, each class on its own line")
        self.inputs['rawmodified']['widget'].setToolTip("Type in behaviors that have modifiers as a comma separated list")

        self.generalTab = QWidget()
        self.generalLO = QVBoxLayout(self.generalTab)
        self.generalLO.addLayout(self.formLO)

    def layoutPlayerTab(self):
        """Layout player tab"""

        self.playerInput = QComboBox()
        self.playerInput.addItems(["MPlayer", "VLC player"])
        self.MPlayerVO = QComboBox()
        if sys.platform == "win32":
            self.MPlayerVO.addItems(["Default", "x11", "xv", "sdl", "gl"])
        else:
            self.MPlayerVO.addItems(["Default", "gl", "directx", "direct3d"])

        
        self.playerFormLo = QFormLayout()
        self.playerFormLo.addRow("Video player:", self.playerInput)
        self.playerFormLo.addRow("MPlayer video driver:", self.MPlayerVO)

        self.playerTab = QWidget()
        self.playerLO = QVBoxLayout(self.playerTab)
        self.playerLO.addLayout(self.playerFormLo)

    def save(self):
        #General settings
        for key in self.inputs:
            if type(self.inputs[key]['widget']) == QLineEdit:
                CowLogSettings.Project[key] = self.inputs[key]['widget'].text()
            elif type(self.inputs[key]['widget']) == QPlainTextEdit: 
                CowLogSettings.Project[key] = self.inputs[key]['widget'].document().toPlainText()
            elif type(self.inputs[key]['widget']) == QCheckBox: 
                CowLogSettings.Project[key] = bool(self.inputs[key]['widget'].checkState())

        if CowLogSettings.Project["rawcodes"].strip() !="": 
            CowLogSettings.Project["behaviors"] = self.getBehaviors()
        #Media Player settings
        CowLogSettings.Project["player"]  = {"name" : self.playerInput.currentText(), 
                                             "vo" : self.MPlayerVO.currentText()}
        print(CowLogSettings.Project)
        settingsFile = QFileDialog.getSaveFileName(self, "Save project settings as:", 
                                                   CowLogSettings.Project["datadirectory"] + os.sep + CowLogSettings.Project["name"] + "_project.json",
                                                   "JSON (*.json)")
        
        if settingsFile:
            set = open(settingsFile, "w")
            set.write(json.dumps(CowLogSettings.Project, 
                        sort_keys = True, indent = 4))
            set.close()
        self.accept()
        
        


    def getBehaviors(self):
        rawcodes = CowLogSettings.Project["rawcodes"]
        usemodifiers = CowLogSettings.Project["usemodifiers"]
        modified = CowLogSettings.Project["rawmodified"].split(",")

        lines = rawcodes.splitlines()
        n = len(lines)
        CowLogSettings.Project["nClasses"] = n
        behaviors = []
        for i in range(n):
              codes = lines[i].split(",")
              m = len(codes)
              for code in codes:
                  if usemodifiers:
                      hasmodifiers = code in modified
                  else:
                      hasmodifiers = False
                  behaviors.append({"name" : code, "class" : i+1, "hasmodifiers" : hasmodifiers})
        return(behaviors)

    def dirDialog(self):
        directory = QFileDialog.getExistingDirectory()
        self.sender().Output.setText(directory)

class CowLogSettings():
    Project = {"name" : "DefaultProject", "datadirectory" : "e:\\tmp", "videodirectory" : "e:\\videot", "behaviors" : [], 
               "nClasses" : 3, "player" : {"name" : "MPlayer" ,"vo" : "gl"}, "usemodifiers" : False}
    Subject = {}

def InitDefaults():
    CowLogSettings.Project["behaviors"] = []
    for i in range(1,31):
        behClass = int(math.ceil(i/10.0))
        CowLogSettings.Project["behaviors"].append({"name" : str(i), "class" : behClass , "hasmodifiers" : False})


if __name__=="__main__":
    app=QApplication(sys.argv)
    win=ProjectDialog()
    win.show()
    sys.exit(app.exec_())

