# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from ui_class.base_main_window import Ui_MainWindow
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from basic.fund_handle import fund_information
import datetime


class MatplotWidget(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        super(MatplotWidget, self).__init__(self.fig)
        self.pic = self.fig.add_subplot(111)

    def plot(self, x, y, color, label):
        self.pic.plot(x, y, color=color, label=label)
        self.pic.legend(loc=2)


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('FundTool')
        self.query_button.clicked.connect(self.query)
        self.start_time.setWindowTitle('起始时间')
        self.start_time.setMaximumDate(QDate.currentDate())
        self.start_time.setDate(QDate.currentDate())
        self.end_time.setWindowTitle('结束时间')
        self.start_time.setMaximumDate(QDate.currentDate())
        self.end_time.setDate(QDate.currentDate())

        self.fig = None

    def init_fig(self):
        self.fig = MatplotWidget()
        self.horizontal_layout.addWidget(self.fig)

    def get_code(self):
        return self.fund_code.toPlainText()

    def get_date(self):
        return self.start_time.date().toString('yyyy-MM-dd'), self.end_time.date().toString('yyyy-MM-dd')

    def check_input(self):
        st, en = self.start_time.date(), self.end_time.date()
        if st > en or en > QDate.currentDate():
            return False
        # TODO:报错提醒
        return True

    def query(self):
        if self.check_input():
            code = self.get_code()
            st, en = self.get_date()
            df = fund_information(code, st, en)
            if df is not None:
                self.set_val(df['净值日期'], df['单位净值'])

    def set_val(self, x, y):
        if self.fig is None:
            self.init_fig()
        self.fig.plot(x, y, 'b', '估值')



