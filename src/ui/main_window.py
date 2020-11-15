# -*- coding: utf-8 -*-
import datetime
import numpy as np

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from ui_class.base_main_window import Ui_MainWindow
import matplotlib
import matplotlib.ticker as mtk
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from basic.fund_handle import *
from basic.notice_util import notice
from basic.config import *


class MatplotWidget(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        super(MatplotWidget, self).__init__(self.fig)
        self.pic = {}

    def red_or_green(self, y):
        color = []
        for i in range(y.shape[0]):
            if y.iloc[i] >= 0:
                color.append('r')
            else:
                color.append('g')
        return color

    def plot(self, index, x, y, color, label):
        if self.pic.get(index) is None:
            self.pic[index] = self.fig.add_subplot(index)

        def x_fmt_func(ind, pos=None):
            idx = np.clip(int(ind + 0.5), 0, y.shape[0] - 1)
            return x.iat[idx].strftime('%Y-%m-%d')

        self.pic[index].plot(np.arange(x.shape[0]), y, color=color, label=label)
        self.pic[index].xaxis.set_major_formatter(mtk.FuncFormatter(x_fmt_func))

    def plot_bar(self, index, x, y):
        if self.pic.get(index) is None:
            self.pic[index] = self.fig.add_subplot(index)

        color = self.red_or_green(y)

        def x_fmt_func(ind, pos=None):
            idx = np.clip(int(ind + 0.5), 0, y.shape[0] - 1)
            return x.iat[idx].strftime('%Y-%m-%d')

        self.pic[index].bar(np.arange(x.shape[0]), y, color=color)
        self.pic[index].xaxis.set_major_formatter(mtk.FuncFormatter(x_fmt_func))

    def finished(self, index):
        if self.pic.get(index) is None:
            return
        self.pic[index].legend(loc=2)


class MainWindow(Ui_MainWindow, QMainWindow):
    switch = {
        '1个月': datetime.timedelta(days=31),
        '3个月': datetime.timedelta(days=31 * 3),
        '6个月': datetime.timedelta(days=31 * 6),
        '1年': datetime.timedelta(days=365),
        '2年': datetime.timedelta(days=365 * 2),
        '3年': datetime.timedelta(days=365 * 3),
    }

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('FundTool')

        self.main_fig = None
        self.df = None
        self.ma12 = None
        self.ma26 = None
        self.dif = None
        self.dea = None
        self.macd_bar = None
        self.query_button.clicked.connect(self.query)
        self.val_choose.toggled.connect(self.repaint)
        self.macd_choose.toggled.connect(self.repaint)

        self.init_box()

    def init_main_fig(self):
        for i in range(self.vertical_layout.count()):
            self.vertical_layout.itemAt(i).widget().deleteLater()
        self.main_fig = MatplotWidget()
        self.vertical_layout.addWidget(self.main_fig)

    def init_box(self):
        self.val_choose.setChecked(True)
        self.macd_choose.setChecked(False)

    def get_code(self):
        return self.fund_code.toPlainText()

    def get_date(self):
        en = datetime.datetime.now()
        begin = en - self.switch[self.choose_time.currentText()]
        st = begin - datetime.timedelta(days=59)

        return begin.strftime('%F'), st.strftime('%F'), en.strftime('%F')

    def reset_date(self, begin):
        begin = pd.to_datetime(begin, format='%Y/%m/%d')
        self.ma12 = self.ma12[self.ma12[DATE_FIELD] > begin]
        self.ma26 = self.ma26[self.ma26[DATE_FIELD] > begin]
        self.dif = self.dif[self.dif[DATE_FIELD] > begin]
        self.dea = self.dea[self.dea[DATE_FIELD] > begin]
        self.macd_bar = self.macd_bar[self.macd_bar[DATE_FIELD] > begin]

    def query(self):
        self.init_box()
        code = self.get_code()
        begin, st, en = self.get_date()
        print('request for %s, from %s to %s' % (self.get_code(), st, en))
        self.df, self.val = fund_information(code, st, en, begin)
        if self.df is not None:
            self.ma12 = get_ma(12, self.df)
            self.ma26 = get_ma(26, self.df)
            self.dif = get_dif(self.ma12, self.ma26)
            self.dea = get_dea(self.dif)
            self.macd_bar = get_macd_bar(self.dif, self.dea)
            self.reset_date(begin)
            self.repaint()

    def set_main_fig(self, index, x, y, color, label):
        if (x is not None) and (y is not None):
            self.main_fig.plot(index, x, y, color, label)

    def show_fig(self, index):
        self.main_fig.finished(index)

    def repaint(self):
        if self.df is None: return
        print(self.val)
        self.init_main_fig()
        if self.val_choose.isChecked():
            self.set_main_fig(111, self.val[DATE_FIELD], self.val['单位净值'], VAL_COLOR, VAL_LABEL)
            self.set_main_fig(111, self.val[DATE_FIELD], self.val['累计净值'], SUM_VAL_COLOR, SUM_VAL_LABEL)
            self.show_fig(111)
        elif self.macd_choose.isChecked():
            self.set_main_fig(211, self.val[DATE_FIELD], self.val[VAL_FIELD], VAL_COLOR, SUM_VAL_LABEL)
            self.set_main_fig(211, self.ma12[DATE_FIELD], self.ma12[VAL_FIELD], MA10_COLOR, MA10_LABEL)
            self.set_main_fig(211, self.ma26[DATE_FIELD], self.ma26[VAL_FIELD], MA20_COLOR, MA20_LABEL)
            self.show_fig(211)
            self.set_main_fig(212, self.dif[DATE_FIELD], self.dif[VAL_FIELD], DIF_COLOR, DIF_LABEL)
            self.set_main_fig(212, self.dea[DATE_FIELD], self.dea[VAL_FIELD], DEA_COLOR, DEA_LABEL)
            self.main_fig.plot_bar(212, self.macd_bar[DATE_FIELD], self.macd_bar[VAL_FIELD])
            self.show_fig(212)

