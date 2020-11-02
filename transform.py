# -*- coding: utf-8 -*-

import os
import time


root = os.getcwd()
ui_root = os.path.join(root, 'ui')
py_root = os.path.join(root, 'src', 'ui_class')


def qt_cmd(ui_path, file):
    os.system('python -m PyQt5.uic.pyuic %s -o %s' % (ui_path, file))
    print(file + '   --Done')


def ui_to_py(ui_path, py_path, py_file):
    if not os.path.exists(py_path):
        os.mkdir(py_path)
    file = os.path.join(py_path, 'base_' + py_file)

    if not os.path.exists(file):
        qt_cmd(ui_path, file)
    else:
        t_ui = os.stat(ui_path).st_mtime
        t_py = os.stat(file).st_mtime
        if t_ui > t_py:
            qt_cmd(ui_path, file)


def main():
    for root, dirs, files in os.walk(ui_root):
        for f in files:
            py_path = os.path.join(py_root, os.path.relpath(root, 'ui'))
            py_file = f.replace('ui', 'py')
            ui_path = os.path.join(root, f)
            ui_to_py(ui_path, py_path, py_file)


if __name__ == '__main__':
    main()