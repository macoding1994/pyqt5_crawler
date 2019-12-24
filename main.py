# -*- coding: utf-8 -*-
import os
import sys
import threading
import time

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog, QTreeWidgetItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
        self._initChrome()

    def _initSheet(self):
        # self.groupBox_3.setStyleSheet("QGroupBox{border:none}")
        pass

    def _initParameter(self):
        self.urllist = []
        self.path = None
        self.driver = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }

    def _initEvent(self):
        self.infoSignal.connect(self.infoshow)

    def _initPool(self):
        self.Pool = ThreadPoolExecutor(max_workers=10)

    def _initChrome(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path='./chromedriver.exe',
                                       chrome_options=chrome_options)
        self.driver.implicitly_wait(10)

    @pyqtSlot()
    def on_pushButton_clicked(self):
        for url in self.urllist:
            self.infoSignal.emit('任务--{}'.format(str(url)))
            future1 = self.Pool.submit(self.action, str(url))
            future1.add_done_callback(self.infoshow)

    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        if self.line_headerskey.text() and self.line_headersvalue.text():
            self.headers[self.line_headerskey.text()] = self.line_headersvalue.text()
            QMessageBox.information(self, '提示', '{}'.format('请求头,添加成功'))
            self.infoSignal.emit('{}'.format(self.headers))
            self.line_headerskey.clear()
            self.line_headersvalue.clear()

    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        dir_choose = QFileDialog.getExistingDirectory(self,
                                                      "选取文件夹",
                                                      os.getcwd())  # 起始路径
        if not dir_choose:
            return
        self.line_path.setText(dir_choose)
        self.path = dir_choose

    @pyqtSlot()
    def on_pushButton_4_clicked(self):
        '''
http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=10&nc=3&ie=utf-8&word=%E8%93%9D%E8%89%B2
        '''
        '''
//*[@id="imgid"]/div[1]/ul/li/div[1]/a/img
        '''
        if self.line_xpath.text():
            process = threading.Thread(target=self.findxpath, args=(self.line_xpath.text(),))
            process.setDaemon(True)
            process.start()

    def findxpath(self, xpath):
        self.infoSignal.emit('正在加载页面--{}'.format(self.line_url.text()))
        self.driver.get(self.line_url.text())
        self.infoSignal.emit('页面加载完毕，开始解析xpath')
        xpathlist = self.driver.find_elements_by_xpath(xpath)
        for xpath in xpathlist:
            self.infoSignal.emit('{}'.format(xpath.get_attribute('src')))
            if xpath.get_attribute('src')[:4] == 'http':
                QTreeWidgetItem(self.treeWidget).setText(0, xpath.get_attribute('src'))
                self.urllist.append(xpath.get_attribute('src'))

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
