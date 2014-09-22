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
from ProjectSettings import CowLogSettings


class SubjectDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setModal(True)
        self.setWindowTitle("New Subject")
        self.setWindowIcon(QIcon('icons/CowLog.png'))
        #self.resize(500, 400)
        
        self.videofiles = None

        mainLO = QVBoxLayout()
        self.setLayout(mainLO)
        self.InputLO = QFormLayout()
        mainLO.addLayout(self.InputLO)

        buttonLO = QHBoxLayout()
        buttonLO.addStretch(0.5)

        okButton = QPushButton("OK")
        okButton.clicked.connect(self.OK)
        buttonLO.addWidget(okButton)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.Cancel)
        buttonLO.addWidget(cancelButton)

        buttonLO.addStretch(0.5)
        mainLO.addSpacing(20)
        mainLO.addLayout(buttonLO)
        
        self.name = QLineEdit()
        self.InputLO.addRow("Subject:", self.name)
        self.time = QDateTimeEdit()
        self.time.setDateTime(QtCore.QDateTime.currentDateTime())
        self.InputLO.addRow("Start time:", self.time)
        
        self.videoButton = QPushButton("Video file(s):")
        self.VideoInd = QLineEdit()
        self.VideoInd.setEnabled(False)
        self.InputLO.addRow(self.videoButton, self.VideoInd)
        self.videoButton.clicked.connect(self.chooseVideo)
        
        #self.dataButton = QPushButton("Data file:")
        #self.dataInd = QLineEdit()
        #self.dataInd.setEnabled(False)
        #self.InputLO.addRow(self.dataButton, self.dataInd)
        #self.dataButton.clicked.connect(self.chooseData)

    def chooseVideo(self):
        self.videofiles = QFileDialog.getOpenFileNames(self, 'Choose video(s)', 
                                                       CowLogSettings.Project['videodirectory'], "Videos (*.*)")
        self.VideoInd.setText(";".join(self.videofiles))

    #def chooseData(self):
    #        pass

    def OK(self):
        #If videofiles were chosen attempt to play
        if self.videofiles is not None:
            CowLogSettings.Subject['videos'] = self.videofiles
            CowLogSettings.Subject['name'] = self.name.text()
            CowLogSettings.Subject['time'] = self.time.dateTime()
        else:
            self.reject()
        self.accept()
    
    def Cancel(self):
        self.reject()
        

if __name__=="__main__":
    app=QApplication(sys.argv)
    win=SubjectDialog()
    win.show()
    sys.exit(app.exec_())

