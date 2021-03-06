#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose: To run DigSilent within a thread
# Created: 30/09/14

import sys
import time
import random
import os

#bling testing git in

try:
    os.environ["PATH"] = r'C:\Program Files\DIgSILENT\PowerFactory 15.2;'+ os.environ["PATH"]
    sys.path.append("C:\\Program Files\\DIgSILENT\\PowerFactory 15.2\\python\\3.4")    

    import powerfactory as pf
except ImportError as e:
    print("Powerfactory not available - {0}".format(e))


from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot

class DesignerMainWindow(QtGui.QMainWindow):
    def __init__(self, Digapp):
        super(DesignerMainWindow, self).__init__()
        
        self.central = MainWindow(Digapp)
        
        self.setWindowTitle('multithreading')
        
        self.setCentralWidget(self.central)
        
    def closeEvent(self,e):
        #self.killthread.emit()
        self.central.closeEvent(e)
        print('pressed close')    
        
        


class MainWindow(QtGui.QWidget):
    
    killthread=pyqtSignal()
    
    
    def __init__(self, Digapp, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui()
        #self.startThreads()
        self.Digapp = Digapp


    def ui(self):

        #self.size=(300,900)
        self.setWindowTitle("The Main Window")
        
        self.edit=QtGui.QLineEdit()
        self.edit2=QtGui.QLineEdit()
        self.dial2 = QtGui.QDial()
        self.slider = QtGui.QSlider()
        self.pushbutton = QtGui.QPushButton('Start the thread')
        
        layout=QtGui.QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.edit2)
        layout.addWidget(self.dial2)
        layout.addWidget(self.slider)
        layout.addWidget(self.pushbutton)
        self.setLayout(layout)
        
        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), self.dial2, QtCore.SLOT('setValue(int)'))
        self.connect(self.dial2, QtCore.SIGNAL('valueChanged(int)'), self.slider, QtCore.SLOT('setValue(int)'))
        
        self.connect(self.pushbutton, QtCore.SIGNAL('clicked()'), self, QtCore.SLOT('startThreads()'))


        
        

    @pyqtSlot()
    def startThreads(self):

        self.worker1 = Worker('In Thread1',self.edit, self.Digapp)
        self.worker2 = Worker('In Thread2',self.edit2, self.Digapp)

        self.thread1 = QtCore.QThread(parent=self)
        self.thread2 = QtCore.QThread(parent=self)

        self.worker1.moveToThread(self.thread1)
        self.worker2.moveToThread(self.thread2)
        
        #Thread One main controls
        self.connect(self.worker1, QtCore.SIGNAL('error(QString)'), self, QtCore.SLOT('error(QString)'))
        self.connect(self.thread1, QtCore.SIGNAL('started()'), self.worker1, QtCore.SLOT('process()'))
        self.connect(self.worker1, QtCore.SIGNAL('resultReady()'),self, QtCore.SLOT('getResult()')) 
        self.connect(self, QtCore.SIGNAL('killthread()'), self.thread1, QtCore.SLOT('quit()'))
        
        #deleting the thread and the worker
        self.connect(self.worker1, QtCore.SIGNAL('finished()'), self.thread1, QtCore.SLOT('quit()'))
        self.connect(self.worker1, QtCore.SIGNAL('finished()'), self.worker1, QtCore.SLOT('deleteLater()'))
        self.connect(self.thread1, QtCore.SIGNAL('finished()'), self.thread1, QtCore.SLOT('deleteLater()'))
        
        #Thread two main controls
        self.connect(self.worker2, QtCore.SIGNAL('error(QtCore.QString)'), self, QtCore.SLOT('error(QString)'))
        self.connect(self.thread2, QtCore.SIGNAL('started()'), self.worker2, QtCore.SLOT('process()'))
        self.connect(self.worker2, QtCore.SIGNAL('resultReady()'),self, QtCore.SLOT('getResult()')) 
        self.connect(self, QtCore.SIGNAL('killthread()'), self.thread2, QtCore.SLOT('quit()'))        
        
        #deleting the thread and the worker
        self.connect(self.worker2, QtCore.SIGNAL('finished()'), self.thread2, QtCore.SLOT('quit()'))
        self.connect(self.worker2, QtCore.SIGNAL('finished()'), self.worker2, QtCore.SLOT('deleteLater()'))
        self.connect(self.thread2, QtCore.SIGNAL('finished()'), self.thread2, QtCore.SLOT('deleteLater()'))
        
        

        self.thread1.start()


        #self.thread2.start()

        print('Thread One is running = ' +str(self.thread1.isRunning()))
        print('Thread Two is running = ' +str(self.thread2.isRunning()))

        ab=QtGui.QMessageBox()
        ab.setText("The thread was started")
        ab.exec_()

        
    @pyqtSlot()
    def getResult(self):
        result1 = self.worker1.getResult() #method of worker
        self.edit.setText(str(result1[4]))
        self.killthread.emit()

    @pyqtSlot(str)
    def error(self,e):
        print (e)
        
        

    def closeEvent(self,e):
        self.killthread.emit()
        print('threads terminated')

class Worker(QtCore.QObject):

    finished=pyqtSignal()
    resultReady=pyqtSignal()
    error=pyqtSignal(['QString'])

    def __init__(self, name, edit, app, parent=None):
        super(Worker,self).__init__()
        self.name = name
        self.edit = edit
        self.result = []
        self.app = app


        prja = self.app.ActivateProject('test')
        prj = self.app.GetActiveProject()
        if prj is None:
            raise Exception("No project activated. Python Script stopped.")

        self.ldf = self.app.GetFromStudyCase("ComLdf")
        self.shc = self.app.GetFromStudyCase("ComShc")

              
        
    #@pyqtSlot()
    def getResult(self):
        result = self.result
        return result        

    @pyqtSlot()
    def process(self):


        try:
            ######### Load flow study #####
            
            print('beginning load flow')  
            self.ldf.iopt_net = 0
            self.ldf.Execute()

            print("Collecting all calculation relevant terminals..")
            terminals = self.app.GetCalcRelevantObjects("*.ElmTerm")
            if not terminals:
                raise Exception("No calculation relevant terminals found")
            print("Number of terminals found: %d" % len(terminals))

            for terminal in terminals:
                voltage = terminal.__getattr__("m:u")
                self.result.append(voltage)
                print("Voltage at terminal %s is %f p.u." % (terminal.cDisplayName , voltage))
                
        except Exception as e:
            print('Load flow errors {}'.format(e))
            
        print('beginning fault study')
                  
        try:
                
            ################# Fault Study ###################
            self.shc.iopt_mde=3 # for complete method
            self.shc.Execute()


            print("Collecting all calculation relevant terminals..")
            terminals = self.app.GetCalcRelevantObjects("*.ElmTerm")
            if not terminals:
                raise Exception("No calculation relevant terminals found")
            print("Number of terminals found: %d" % len(terminals))

            terminals = self.app.GetCalcRelevantObjects("*.ElmTerm")

            for terminal in terminals:
                voltage = terminal.__getattr__("m:U1")
                self.result2.append(voltage)
                print("Voltage at terminal %s is %f p.u." % (terminal.cDisplayName , voltage))



            print("Collecting all calculation relevant lines..")
            lines = self.app.GetCalcRelevantObjects("*.ElmLne")

            for line in lines:
                amps = line.__getattr__("m:Ikss:bus1:A")
                Z0 = line.__getattr__("m:Z0:bus1")
                print("Amps in line %s is %f p.u.and %f" % (line.cDisplayName , amps, Z0))


        except Exception as err:
            print("Fault study error is {}".format(err))

        self.resultReady.emit()

    @pyqtSlot()
    def processComplete(self):
        self.finished.emit()
        #return self.result
        

def main():
    app=QtGui.QApplication(sys.argv)
    Digapp = pf.GetApplication('counties')
    dmw = DesignerMainWindow(Digapp) # instantiate a window and pass the Digapp to the mainwindow
    dmw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
