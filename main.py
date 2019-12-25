# -*- coding: utf-8 -*-
import os
import sys
import threading
import time
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QModelIndex
from PyQt5.QtGui import QTextCursor
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
        # self.line_url.setText(
        #     'http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=10&nc=3&ie=utf-8&word=%E8%93%9D%E8%89%B2')
        # self.line_xpath.setText('//*[@id="imgid"]/div/ul/li/div[1]/a/img')
        # self.line_headerskey.setText('Referer')
        # self.line_headersvalue.setText(
        #     'http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word=%E8%93%9D%E8%89%B2%5C')

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
        self.Pool = ThreadPoolExecutor(max_workers=8)

    def _initChrome(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
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
                future1 = self.Pool.submit(self.action, str(url), node)
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

    @pyqtSlot()
    def on_pushButton_5_clicked(self):
        '''
        https://mei.huazuida.com/20191220/19592_1840d856/1000k/hls/
        '''
        if self.line_url.text():
            if self.comboBox.currentText() == 'm3u8':
                fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                        "选取文件",
                                                                        os.getcwd(),  # 起始路径
                                                                        "All Files (*);;m3u8 Files (*.m3u8)")  # 设置文件扩展名过滤,用双分号间隔
                if not fileName_choose:
                    return
                self.Pool.submit(self.m3u8,fileName_choose)
        else:
            QMessageBox.information(self,'提示','请填写url路径')

    @pyqtSlot(QTreeWidgetItem, int)
    def on_treeWidget_itemClicked(self, item, column):
        print(self.treeWidget.topLevelItemCount())
        print(self.treeWidget.indexOfTopLevelItem(item))
        print(item.text(0))
        print(item.checkState(0))

    def m3u8(self,path):
        '''
        https://mei.huazuida.com/20191220/19592_1840d856/1000k/hls/
        '''
        self.treelist = []
        with open(path,'r') as f:
            m3u8list = f.readlines()
        print(m3u8list)
        for m3u8 in m3u8list:
            if not m3u8[0] == '#':
                url = self.line_url.text() + m3u8.strip()
                node = QTreeWidgetItem(self.treeWidget)
                node.setText(0, url)
                node.setText(1, '未完成')
                node.setCheckState(0, Qt.Checked)
                self.treelist.append(node)

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
        self.textBrowser.moveCursor(QTextCursor.End)

    def action(self, url, node):
        '''子线程-任务'''
        try:
            res = requests.get(url, headers=self.headers,timeout=(2,4))
        except Exception:
            return '{}失败--连接时间过长'.format(url)
        if res.status_code == 200:
            end = url.rsplit('.')[-1]
            name = time.time()
            if self.comboBox.currentText() == 'm3u8':
                name = url.rsplit('/')[-1].split('.')[0]
            if not self.path:
                self.path = os.getcwd()
            with open('{}/{}.{}'.format(self.path, name, end), 'wb') as f:
                f.write(res.content)
            self.treelist.remove(node)
            self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(node))
            return '{}成功,{}'.format(res.status_code, name)
        else:
            return '{}失败,{}'.format(res.status_code, threading.current_thread().name)


def main():
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
