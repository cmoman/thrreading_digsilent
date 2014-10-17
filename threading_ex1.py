#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose:
# Created: 30/09/14

import sys
import time
import random

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot

class DesignerMainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(DesignerMainWindow, self).__init__()
        
        central = MainWindow()
        
        self.setCentralWidget(central)
        
        


class MainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui()
        self.startThreads()


    def ui(self):

        self.size=(300,900)
        self.setWindowTitle("The Main Window")
        
        self.edit=QtGui.QLineEdit()
        self.edit2=QtGui.QLineEdit()
        
        layout=QtGui.QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.edit2)
        
        self.setLayout(layout)


    def startThreads(self):

        self.worker1 = Worker('In Thread1',self.edit)
        self.worker2 = Worker('In Thread2',self.edit2)

        self.thread1 = QtCore.QThread()
        self.thread2 = QtCore.QThread()

        self.worker1.moveToThread(self.thread1)
        self.worker2.moveToThread(self.thread2)

        self.connect(self.worker1, QtCore.SIGNAL('error(QString)'), self, QtCore.SLOT('error(QString)'))
        self.connect(self.thread1, QtCore.SIGNAL('started()'), self.worker1, QtCore.SLOT('process()'))
        self.connect(self.worker1, QtCore.SIGNAL('resultReady()'),self, QtCore.SLOT('getResult()')) 
        self.connect(self.worker1, QtCore.SIGNAL('finished()'), self.thread1, QtCore.SLOT('quit()'))
        self.connect(self.worker1, QtCore.SIGNAL('finished()'), self.worker1, QtCore.SLOT('deleteLater()'))
        self.connect(self.thread1, QtCore.SIGNAL('finished()'), self.thread1, QtCore.SLOT('deleteLater()'))

        self.connect(self.worker2, QtCore.SIGNAL('error(QtCore.QString)'), self, QtCore.SLOT('error(QString)'))
        self.connect(self.thread2, QtCore.SIGNAL('started()'), self.worker2, QtCore.SLOT('process()'))
        self.connect(self.worker2, QtCore.SIGNAL('finished()'), self.thread2, QtCore.SLOT('quit()'))
        self.connect(self.worker2, QtCore.SIGNAL('finished()'), self.worker2, QtCore.SLOT('deleteLater()'))
        self.connect(self.thread2, QtCore.SIGNAL('finished()'), self.thread2, QtCore.SLOT('deleteLater()'))

        self.thread1.start()
        self.thread2.start()

        print(self.thread1.isRunning())
        print(self.thread2.isRunning())
        
    @pyqtSlot()
    def getResult(self):
        result = self.worker1.result
        self.edit.setText(str(result[4]))

    @pyqtSlot(str)
    def error(self,e):
        print (e)

    def closeEvent(self,e):
        print('pressed close')

class Worker(QtCore.QObject):

    finished=pyqtSignal()
    resultReady=pyqtSignal()
    error=pyqtSignal(['QString'])

    def __init__(self, name, edit, parent=None):
        super(Worker,self).__init__()
        self.name = name
        self.edit = edit
        self.result = []

    @pyqtSlot()
    def process(self):
        for _ in range(5):
            #self.edit.setText(self.name)
            self.result.append((_*2))
        self.resultReady.emit()
    
    @pyqtSlot()
    def getResult(self):
        self.finished.emit()
        #return self.result
        

def main():
    app=QtGui.QApplication(sys.argv)
    dmw = DesignerMainWindow() # instantiate a window
    dmw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
