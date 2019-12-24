# -*- coding: utf-8 -*-
import os
import sys
import threading
import time

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from Ui_main import Ui_MainWindow
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import requests


class MainWindow(QMainWindow, Ui_MainWindow):
    infoSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self._initSheet()
        self._initParameter()
        self._initEvent()
        self._initPool()

    def _initSheet(self):
        # self.groupBox_3.setStyleSheet("QGroupBox{border:none}")
        pass

    def _initParameter(self):
        self.path = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }

    def _initEvent(self):
        self.infoSignal.connect(self.infoshow)

    def _initPool(self):
        self.Pool = ThreadPoolExecutor(max_workers=10)

    @pyqtSlot()
    def on_pushButton_clicked(self):
        try:
            self.infoSignal.emit('任务--{}'.format(str(self.line_url.text())))
            future1 = self.Pool.submit(self.action, self.line_url.text())
            future1.add_done_callback(self.infoshow)
        except Exception as e:
            QMessageBox.information(self, '提示', '{}'.format(e))

    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        if self.line_headerskey.text() and self.line_headersvalue.text():
            self.headers[self.line_headerskey.text()] = self.line_headersvalue.text()
            QMessageBox.information(self, '提示', '{}'.format('请求头,添加成功'))
            self.infoSignal.emit('{}'.format(self.headers))

    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        dir_choose = QFileDialog.getExistingDirectory(self,
                                                      "选取文件夹",
                                                      os.getcwd())  # 起始路径
        if not dir_choose:
            return
        self.line_path.setText(dir_choose)
        self.path = dir_choose

    def infoshow(self, res):
        if isinstance(res, str):
            self.textBrowser.append(res + '\n')
        else:
            self.textBrowser.append(str(res.result()) + '\n')

    def action(self, url):
        '''子线程-任务'''
        res = requests.get(url, headers=self.headers)
        if res.status_code == 200:
            if not self.path:
                self.path = os.getcwd()
            with open('{}/{}.png'.format(self.path, time.time()), 'wb') as f:
                f.write(res.content)
        return '{},{}'.format(res.status_code, threading.current_thread().name)


def main():
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
