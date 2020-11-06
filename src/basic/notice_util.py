# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMessageBox


def notice(content):
    QMessageBox.information(None, 'Message', content, QMessageBox.Yes, QMessageBox.Yes)


def error(content):
    QMessageBox.information(None, 'Error', content, QMessageBox.Yes, QMessageBox.Yes)