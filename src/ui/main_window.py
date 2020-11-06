# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from ui_class.base_main_window import Ui_MainWindow
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from basic.fund_handle import fund_information, get_ma
from basic.notice_util import notice
from basic.config import *


class MatplotWidget(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        super(MatplotWidget, self).__init__(self.fig)
        self.pic = self.fig.add_subplot(111)

    def plot(self, x, y, color, label):
        self.pic.plot(x, y, color=color, label=label)

    def finished(self):
        self.pic.legend(loc=2)


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('FundTool')
        self.start_time.setWindowTitle('起始时间')
        self.start_time.setMaximumDate(QDate.currentDate())
        self.start_time.setDate(QDate.currentDate())
        self.end_time.setWindowTitle('结束时间')
        self.start_time.setMaximumDate(QDate.currentDate())
        self.end_time.setDate(QDate.currentDate())

        self.fig = None
        self.df = None
        self.ma10 = None
        self.ma20 = None
        self.query_button.clicked.connect(self.query)
        self.macd.stateChanged.connect(self.repaint)

    def init_fig(self):
        for i in range(self.horizontal_layout.count()):
            self.horizontal_layout.itemAt(i).widget().deleteLater()
        self.fig = MatplotWidget()
        self.horizontal_layout.addWidget(self.fig)

    def init_box(self):
        self.macd.setChecked(False)

    def get_code(self):
        return self.fund_code.toPlainText()

    def get_date(self):
        return self.start_time.date().toString('yyyy-MM-dd'), self.end_time.date().toString('yyyy-MM-dd')

    def check_input(self):
        st, en = self.start_time.date(), self.end_time.date()
        if st > en or en > QDate.currentDate():
            notice('start-date cannot later than end-date')
            return False
        return True

    def query(self):
        self.init_box()
        if self.check_input():
            code = self.get_code()
            st, en = self.get_date()
            print('request for %s ...' % self.get_code())
            self.df = fund_information(code, st, en)
            if self.df is not None:
                self.set_val(self.df['净值日期'], self.df['单位净值'])
                self.ma10 = get_ma(10, self.df)
                self.ma20 = get_ma(20, self.df)
                self.fig.finished()

    def set_val(self, x, y):
        self.init_fig()
        self.fig.plot(x, y, VAL_COLOR, VAL_LABEL)

    def set_ma(self, x, y, color, label):
        self.fig.plot(x, y, color, label)

    def repaint(self):
        self.set_val(self.df['净值日期'], self.df['单位净值'])
        if self.macd.isChecked():
            self.set_ma(self.ma10['净值日期'], self.ma10['单位净值'], MA10_COLOR, MA10_LABEL)
            self.set_ma(self.ma20['净值日期'], self.ma20['单位净值'], MA20_COLOR, MA20_LABEL)
        self.fig.finished()


