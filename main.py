# -*- coding: utf-8 -*-
import sys
import threading
import time

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication
from Ui_main import Ui_MainWindow
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import requests


class MainWindow(QMainWindow, Ui_MainWindow):
    infoSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self._initEvent()
        self._initPool()

    def _initEvent(self):
        self.infoSignal.connect(self.infoshow)

    def _initPool(self):
        self.Pool = ThreadPoolExecutor(max_workers=10)

    @pyqtSlot()
    def on_pushButton_clicked(self):
        try:
            self.infoSignal.emit('任务{}'.format(str(self.lineEdit.text())))
            future1 = self.Pool.submit(self.action, int(self.lineEdit.text()))
            future1.add_done_callback(self.infoshow)
        except Exception as e:
            pass

    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        pass

    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        pass

    def infoshow(self, res):
        if isinstance(res, str):
            self.textBrowser.append(res + '\n')
        else:
            self.textBrowser.append(str(res.result()) + '\n')

    def action(self, max):
        '''子线程-任务'''
        my_sum = 0
        for i in range(max):
            my_sum += i
        return '200,{}'.format(threading.current_thread().name)


def main():
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
