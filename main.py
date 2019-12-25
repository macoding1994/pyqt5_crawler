# -*- coding: utf-8 -*-
import os
import sys
import threading
import time
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QModelIndex
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
        self.line_url.setText(
            'http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=10&nc=3&ie=utf-8&word=%E8%93%9D%E8%89%B2')
        self.line_xpath.setText('//*[@id="imgid"]/div/ul/li/div[1]/a/img')
        self.line_headerskey.setText('Referer')
        self.line_headersvalue.setText(
            'http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word=%E8%93%9D%E8%89%B2%5C')

    def _initParameter(self):
        self.treelist = []
        self.treename = []
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
        # chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path='./chromedriver.exe',
                                       chrome_options=chrome_options)
        self.driver.implicitly_wait(10)

    @pyqtSlot()
    def on_pushButton_clicked(self):
        for node in self.treelist:
            url = node.text(0)
            status = int(node.checkState(0))
            if status == 2:
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
        if self.line_url.text():
            process = threading.Thread(target=self.findxpath, args=(self.line_xpath.text(),))
            process.setDaemon(True)
            process.start()

    @pyqtSlot(QTreeWidgetItem, int)
    def on_treeWidget_itemClicked(self, item, column):
        print(self.treeWidget.topLevelItemCount())
        print(self.treeWidget.indexOfTopLevelItem(item))
        print(item.text(0))
        print(item.checkState(0))

    def findxpath(self, xpath):
        if int(self.treeWidget.topLevelItemCount()) == 0:
            self.infoSignal.emit('正在加载页面--{}'.format(self.line_url.text()))
            self.driver.get(self.line_url.text())
        self.infoSignal.emit('页面加载完毕，开始解析xpath')
        self.driver.switch_to.window(self.driver.window_handles[-1])
        xpathlist = self.driver.find_elements_by_xpath(xpath)
        self.infoSignal.emit(str(len(xpathlist)))
        for xpath in xpathlist:
            self.infoSignal.emit('{}'.format(xpath.get_attribute('src')))
            if xpath.get_attribute('src')[:4] == 'http':
                if not xpath.get_attribute('src') in self.treename:
                    node = QTreeWidgetItem(self.treeWidget)
                    node.setText(0, xpath.get_attribute('src'))
                    node.setText(1, '未完成')
                    node.setCheckState(0, Qt.Checked)
                    self.treelist.append(node)
                    self.treename.append(xpath.get_attribute('src'))
        # else:
        #     self.infoSignal.emit('{}'.format(self.treelist))

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
            return '{}成功,{}'.format(res.status_code, threading.current_thread().name)
        else:
            return '{}失败,{}'.format(res.status_code, threading.current_thread().name)


def main():
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
