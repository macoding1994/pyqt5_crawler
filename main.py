# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow,QApplication
from Ui_main import Ui_MainWindow
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import requests

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

    @pyqtSlot()
    def on_pushButton_clicked(self):
        pass
    
    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        pass
    
    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        pass

    def print_while(self,a):
        while 1:
            print(a)

def main():
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
