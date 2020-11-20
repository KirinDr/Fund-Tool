# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMessageBox
from basic.config import *
import os

def notice(content):
    QMessageBox.information(None, 'Message', content, QMessageBox.Yes, QMessageBox.Yes)


def error(content):
    QMessageBox.information(None, 'Error', content, QMessageBox.Yes, QMessageBox.Yes)


def read_local_code():
    with open(os.path.join(BASIC_PATH, LOCAL_CODE), "r") as f:
        codes = f.readlines()
    for i in range(len(codes)):
        codes[i] = codes[i].rstrip('\n')
    return codes