#!/usr/bin/python
# -*- coding: utf-8 -*-
# boxlayout.py
import sys
from PyQt4 import QtGui, QtCore
class Help(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle('CowLog Help')
        self.setWindowIcon(QtGui.QIcon('icons/help.png'))
        ok = QtGui.QPushButton("Close", self)
        #ok.setMaximumWidth(80)
        self.connect(ok, QtCore.SIGNAL('clicked()'), QtCore.SLOT('hide()'))
        #title = QtGui.QLabel(self)
        #title.setText('<h3>Main help</h3>')
        about = QtGui.QTextBrowser(self)
        #about.setAlignment(QtCore.Qt.AlignCenter)
        about.setMinimumSize(400, 400)
        #CowLog help
        #about.setHtml("""""")
        about.setSource(QtCore.QUrl('manual.html'))
        
        grid = QtGui.QGridLayout(self)
        grid.setSpacing(7)
        #grid.addWidget(title, 1, 1)
        grid.addWidget(about, 2, 0, 5, 3)
        grid.addWidget(ok, 7, 1)
        self.show()

