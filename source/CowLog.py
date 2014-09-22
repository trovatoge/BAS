#!/usr/bin/python

#Use pythonic API python 2 as well
try:
    import sip
    sip.setapi("QString" , 2)
except:
    pass

from os import system, remove, getcwd
import sys
import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from time import sleep
from subprocess import Popen, PIPE
from help import Help
from ProjectSettings import *
from mplayer import *
from SubjectDialog import *
import pickle

__version__ = "2.0"
MPlayer.directory = getcwd()

#GUI
class CowLog(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('CowLog')
        self.setWindowIcon(QIcon('icons/CowLog.png'))

        #Menus
        #-----------------------
        #File menu
        newSubject = QAction(self.getIcon(QStyle.SP_MediaPlay), 'New subject', self)
        newSubject.triggered.connect(self.createSubject)


        newProject = QAction(self.getIcon(QStyle.SP_FileDialogNewFolder) , 'New project', self)
        newProject.triggered.connect(self.createProject)
        loadProject = QAction(self.getIcon(QStyle.SP_DirOpenIcon), 'Open project', self)
        loadProject.triggered.connect(self.openProject)


        exit = QAction(self.getIcon(QStyle.SP_DialogCloseButton), 'Exit', self)
        exit.triggered.connect(self.close)
        #exit.setStatusTip('Exit application')


        #self.connect(data, QtCore.SIGNAL('triggered()'), self.datadialog)
        menubar = self.menuBar()
        file = menubar.addMenu("File")

        file.addAction(newSubject)
        file.addSeparator()
        file.addAction(newProject)
        file.addAction(loadProject)
        file.addSeparator()
        file.addAction(exit)

        #Help menu
        help = menubar.addMenu("Help")
        about = QAction(self.getIcon(QStyle.SP_MessageBoxInformation), 'About CowLog', self)
        self.connect(about, QtCore.SIGNAL('triggered()'), self.aboutAction)
        manual = QAction(self.getIcon(QStyle.SP_MessageBoxQuestion), 'CowLog Help', self)
        self.connect(manual, QtCore.SIGNAL('triggered()'), self.helpAction)
        help.addAction(manual)
        help.addAction(about)


        #Layout mainwidget
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.mainLO = QVBoxLayout(self.mainWidget)
        self.CodeButtonLO = QHBoxLayout() #Codebuttons are placed here
        self.ControlLOs = QVBoxLayout()
        self.mainLO.addLayout(self.ControlLOs)
        self.mainLO.addSpacing(5)
        self.mainLO.addLayout(self.CodeButtonLO)
        self.mainLO.addStretch(1)

        #Add controls
        self.AddControls()
        #Add coding buttons to layout based on settings
        InitDefaults()
        self.AddCodeButtons()

    def AddControls(self):
        #Controls

        playbutton = QPushButton(self.getIcon(QStyle.SP_MediaPlay) , '')
        playbutton.clicked.connect(self.play)
        pausebutton = QPushButton(self.getIcon(QStyle.SP_MediaPause) ,'')
        pausebutton.clicked.connect(self.pause)
        playSpeedButton = QPushButton(self.getIcon(QStyle.SP_MediaPlay) ,'Set Speed')
        playSpeedButton.clicked.connect(self.playSpeed)
        stopbutton = QPushButton(self.getIcon(QStyle.SP_MediaStop) ,'',)
        stopbutton.clicked.connect(self.stop)
        undobutton = QPushButton("Undo", self)
        undobutton.clicked.connect(self.undo)

        fwdbutton = QPushButton(self.getIcon(QStyle.SP_MediaSeekForward), "" )
        fwdbutton.clicked.connect(self.jump)
        fwdbutton.direction = 1
        backbutton = QPushButton(self.getIcon(QStyle.SP_MediaSeekBackward) ,"")
        backbutton.direction = -1
        backbutton.clicked.connect(self.jump)
        self.jumpsize = QDoubleSpinBox()
        self.jumpsize.setDecimals(1)
        self.jumpsize.setValue(30)

        self.dataFileName = None

        #self.jumpsize.setMinimumWidth(80)

        framebutton = QPushButton(QIcon("icons/go-next.png") ,'&n')
        framebutton.setToolTip("Move single frame")
        framebutton.clicked.connect(self.nextframe)
        posbutton = QPushButton(QIcon("icons/go-jump.png") ,'Jump to:')
        self.connect(posbutton, QtCore.SIGNAL('clicked()'), self.absposition)
        self.jumpinput = QDoubleSpinBox()
        self.jumpinput.setDecimals(1)
        self.jumpinput.setSingleStep(0.1)
        self.jumpinput.setToolTip("Enter position in seconds")
        self.playSpeedSelect = QDoubleSpinBox()
        self.playSpeedSelect.setDecimals(1)
        self.playSpeedSelect.setSingleStep(0.1)
        self.playSpeedSelect.setToolTip("Enter play speed")
        self.playSpeedSelect.setValue(5)
        #jumpinput.setFixedWidth(60)
        #playSpeedSelect.setFixedWidth(95)

        self.timeIndicator = QLabel()
        self.pbar = QSlider(QtCore.Qt.Horizontal)
        self.pbar.setValue(0)
        self.pbar.sliderMoved.connect(self.position)

        #Layout controls


        ControlLO1 = QHBoxLayout()
        ControlLO1.addWidget(self.timeIndicator)
        ControlLO1.addWidget(self.pbar)

        ControlLO2 = QHBoxLayout()
        ControlLO2.addWidget(playbutton)
        ControlLO2.addWidget(pausebutton)
        ControlLO2.addWidget(stopbutton)

        ControlLO3 = QHBoxLayout()
        ControlLO3.addWidget(self.playSpeedSelect)
        ControlLO3.addWidget(playSpeedButton)
        ControlLO3.addWidget(framebutton)

        ControlLO4 = QHBoxLayout()
        ControlLO4.addWidget(backbutton)
        ControlLO4.addWidget(self.jumpsize)
        ControlLO4.addWidget(fwdbutton)

        ControlLO5 = QHBoxLayout()
        ControlLO5.addWidget(self.jumpinput)
        ControlLO5.addWidget(posbutton)
        ControlLO5.addWidget(undobutton)
        #ControlLO5.addWidget(QLabel())
        #ControlLO5.addStretch(1)

        self.CodeLabel = QLabel("<b>Current code:</b><br>Time, Behavior, Class")
        self.currentCode = QLineEdit()
        self.currentCode.setStyleSheet("background-color : white;")
        self.currentCode.setEnabled(False)

        self.ControlLOs.addLayout(ControlLO1)
        self.ControlLOs.addLayout(ControlLO2)
        self.ControlLOs.addLayout(ControlLO3)
        self.ControlLOs.addLayout(ControlLO4)
        self.ControlLOs.addLayout(ControlLO5)
        self.ControlLOs.addSpacing(20)
        self.ControlLOs.addWidget(self.CodeLabel)
        self.ControlLOs.addWidget(self.currentCode)

    def AddCodeButtons(self):
        """Create codebuttons based on project settings."""
        n = len(CowLogSettings.Project["behaviors"])
        self.CodeButtons = []
        self.CodeLOs = []
        self.CodeStretches = []

        for i in range(CowLogSettings.Project["nClasses"]):
            self.CodeLOs.append(QVBoxLayout())
            self.CodeButtonLO.addLayout(self.CodeLOs[i])

        shortcutKeys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                        "q", "w", "e", "r", "t", "y", "u", "i", "v", "o", "p",
                        "a", "b", "c", "d", "e", "f", "g", "h", "j", "k", "4", "l",
                        "z", "x", "c", "v", "b", "n", "m"]


        #Add buttons to layouts
        for i in range(n):
            self.CodeButtons.append(QPushButton("(&" + shortcutKeys[i] + ")" + " " *2 +  CowLogSettings.Project["behaviors"][i]['name']))
            self.CodeButtons[i].CowProperties = CowLogSettings.Project["behaviors"][i]
            self.CodeButtons[i].clicked.connect(self.code)
            self.CodeButtons[i].setCheckable(True)
            self.CodeLOs[CowLogSettings.Project["behaviors"][i]["class"]-1].addWidget(self.CodeButtons[i])

        #Add strech after buttons

        for i in range(CowLogSettings.Project["nClasses"]):
            self.CodeLOs[i].addStretch(1)


        if CowLogSettings.Project["usemodifiers"]:
            self.CodeLabel.setText("<b>Current code:</b><br>Time, Behaviors")
        else:
            self.CodeLabel.setText("<b>Current code:</b><br>Time, Behavior, Class")

        self.updateGeometry()

    def DeleteCodeButtons(self):
        """Delete all coding buttons, used when settings are changed"""

        #self.CodeButtonLO.deleteLater()
        for LO in self.CodeLOs:
            LO.deleteLater()
        self.CodeLOs = []

        for button in self.CodeButtons:
            button.deleteLater()
        self.CodeButtons = []

    def createProject(self):
        self.ProjectDialog = ProjectDialog()
        if self.ProjectDialog.exec_():
            self.DeleteCodeButtons()
            self.AddCodeButtons()

    def openProject(self):
        projectFile = QFileDialog.getOpenFileName(self, "Load project settings from:",
                                                  CowLogSettings.Project["datadirectory"], "JSON (*.json)")
        if projectFile:
            proj = open(projectFile, "r")
            CowLogSettings.Project = json.loads(proj.read())
            proj.close()
            self.DeleteCodeButtons()
            self.AddCodeButtons()

    def createSubject(self):
        subject = SubjectDialog(self)
        #If dialog was used to choose a subject
        if subject.exec_():
            #Create datafile
            dir = CowLogSettings.Project['datadirectory']
            name = CowLogSettings.Subject['name']
            time = CowLogSettings.Subject['time'].toString("yyyyMMdd_hhmmss")
            CowLogSettings.Subject['project'] = CowLogSettings.Project["name"]
            #CowLogSettings.Subject['behaviors'] = CowLogSettings.Project["behaviors"]
            CowLogSettings.Subject['usemodifiers'] = CowLogSettings.Project["usemodifiers"]
            #CowLogSettings.Subject['nClasses'] = CowLogSettings.Project["nClasses"]

            CowLogSettings.Subject['time'] = CowLogSettings.Subject['time'].toString("yyyy-MM-dd hh:mm:ss")
            self.dataFileName = ("%s%s%s_%s.csv" % (dir, os.sep,  name, time))

            #If the file doesn't exist write a header to it
            if not os.path.isfile(self.dataFileName):
                file = open(self.dataFileName, "w")
                file.write("CowLog %s coding data\n" % __version__)
                file.write(json.dumps(CowLogSettings.Subject) + "\n")
                file.write("---" + "\n")
                classheader = ""
                if CowLogSettings.Project["usemodifiers"]:
                    n = CowLogSettings.Project["nClasses"]
                    for i in range((n-1)):
                        classheader += "class" + str(i+1) + ","
                    classheader += "class" + str(n)
                else:
                    classheader = "code,class"
                file.write("time," + classheader + "\n")
                file.close()


            videos = CowLogSettings.Subject["videos"]
            playerName = CowLogSettings.Project['player']['name']
            vo = CowLogSettings.Project["player"]["vo"]
            if vo == "Default":
                vo = None


            #Players interfaces are in mplayer.py file
            if playerName == "MPlayer":
                Player = MPlayer
            if playerName == "VLC player":
                Player = VLC

                #One video
            if len(videos) == 1:
                self.Player = Player(videos[0], vo)
            else:
                self.Player = Players(videos, player = Player, vo=vo)

            self.timeUpdate()
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.timeUpdate)
            self.pbar.setRange(0, self.Player.totalTime)
            self.jumpinput.setMaximum(self.Player.totalTime)
            self. jumpsize.setMaximum(self.Player.totalTime)
            CowLogSettings.Subject['videolength'] = self.Player.totalTime
            self.pbar.setSingleStep(10)
            self.currentCode.setText("")

            #Keys in a modified behavioral coding
            self.coded = []
            self.firstModifier = True
            self.modifiedTime = 0

    def code(self):
        code = self.sender().CowProperties["name"]
        bClass = self.sender().CowProperties["class"]

        if self.dataFileName is not None:
            if CowLogSettings.Project['usemodifiers']:
                hasmodifiers = self.sender().CowProperties["hasmodifiers"]
                self.codeModifiers(code, bClass, hasmodifiers, self.sender())
            else:
                self.codeNoModifiers(code, bClass, self.sender())

    def codeNoModifiers(self, code, bClass, source):
        time = self.Player.currentTime()
        if time is None:
            return
        #Set the style of other buttons in class to normal
        for button in self.CodeButtons:
            if button.CowProperties["class"] == bClass:
                button.setStyleSheet("font : normal")
        #Highlight the button sending the event
        source.setStyleSheet("font : bold")
        file = open(self.dataFileName, "a")
        codes = ("%.2f, %s, %i") % (time ,code, bClass)
        file.write(codes + "\n")
        file.close()
        self.currentCode.setText(codes)

    def codeModifiers(self, code, bClass, hasmodifiers, source):
        time = self.Player.currentTime()
        if time is None:
            return
        if hasmodifiers:
            self.Player.pause()
            #If this first modifier in sequence save time remove all hightlights
            if self.firstModifier:
                self.firstModifier = False
                for button in self.CodeButtons:
                    button.setStyleSheet("font : normal")
            self.coded.append(code)
            source.setStyleSheet("font : bold")
            #Disable all buttons in the class
            for button in self.CodeButtons:
                if button.CowProperties["class"] == bClass:
                    button.setDisabled(True)
        else:
            self.coded.append(code)
            codestring = (", ").join(self.coded)
            displaycodes = ("%.2f, %s") % (time, codestring)
            #Add commas for unused codes, this aids analysis later on
            n = len(self.coded)
            d = CowLogSettings.Project["nClasses"] - n
            if d != 0:
                codestring += ","*(d)
            file = open(self.dataFileName, "a")
            codes = ("%.2f, %s") % (time, codestring)
            file.write(codes + "\n")
            file.close()
            self.Player.play()
            self.currentCode.setText(displaycodes)
            self.coded = []
            for button in self.CodeButtons:
                button.setEnabled(True)
                if self.firstModifier: #If this starts the modifier sequence remove old hightlights
                   button.setStyleSheet("font : normal")
            source.setStyleSheet("font : bold")
            self.firstModifier = True

    def undo(self):
        """Undo latest codebutton"""
        #Remove disabling and highlights
        if self.dataFileName is None:
            return

        for button in self.CodeButtons:
            button.setEnabled(True)
            button.setStyleSheet("font : normal")

        if CowLogSettings.Project["usemodifiers"]:
            self.coded = []
            #If in the middle of sequence break it but do nothing to file
            if not self.firstModifier:
                self.firstModifier = True
                return

        codefile = open(self.dataFileName, 'r')
        codes = codefile.read()
        codefile.close()
        #Remove the last code and last empty line
        newcodes = codes.split("\n")[0:-2]
        if newcodes:
            self.currentCode.setText(newcodes[-1])
            codefile = open(self.dataFileName, 'w')
            codefile.write("\n".join(newcodes) + "\n")
            codefile.close()
        else:
            self.currentCode.setText("No more codes")

    def nextframe(self):
        self.Player.nextFrame()
        self.timeUpdate()

    def timeUpdate(self):
        time = self.Player.currentTime()
        if time is not None:
            time = int(time)
            self.pbar.setValue(time)
            self.timeIndicator.setText(str(time) + '/' + str(int(self.Player.totalTime)) + ' s')
        else:
            self.timer.stop()

    def play(self):
        self.Player.play()
        self.timer.start(1000)

    def playSpeed(self):
        self.Player.play(self.playSpeedSelect.value())
        self.timer.start(1000)

    def jump(self):
        amount = self.sender().direction*self.jumpsize.value()
        self.Player.seekRelative(amount)
        self.timeUpdate()

    def absposition(self):
        self.Player.seek(self.jumpinput.value())
        self.timeUpdate()

    def position(self):
        time = self.pbar.value()
        self.Player.seek(time)
        self.timeIndicator.setText(str(time) + '/' + str(int(self.Player.totalTime)) + ' s')

    def pause(self):
        self.timer.stop()
        self.Player.pause()

    def stop(self):
        self.timer.stop()
        #Try to get current time, if it not available the video has likely come to an end
        time = self.Player.currentTime()
        if time is None:
            time = CowLogSettings.Subject["videolength"]
        self.Player.stop()
        if self.dataFileName is not None:
            file = open(self.dataFileName, "a")
            code = "END"
            codes = ("%.2f %s") % (time ,code)
            file.write(codes + "\n")
            file.close()
            self.currentCode.setText(codes)

    def aboutAction(self):
        QMessageBox.about(self, "About CowLog",
                          """<h3>CowLog</h3> v %s
                          <p>Code behaviors from digital video</p>

                          <p><b>Citation</b><br>
                           H&auml;nninen, L. & Pastell, M. 2009. CowLog: Open source software for coding behaviors from digital video. Behavior Research Methods. 41(2), 472-476.  </p>


                          <p>Matti Pastell, University of Helsinki</p>
                          <br><a href="http://cowlog.org">http://cowlog.org</a></br>

                          """ % (__version__)
                          )

    def helpAction(self):
        a = Help()
        a.__init__()

    def getIcon(self, icon):
        return(QIcon(QApplication.style().standardIcon(icon)))


def main(args):
    app= QApplication(args)
    win= CowLog()
    win.show()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()")
                , app
                , QtCore.SLOT("quit()")
                )
    app.exec_()

if __name__=="__main__":
        main(sys.argv)
