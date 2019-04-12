'''
Instantiate the ui form and create all the needed connections to run it.

Created on April 12, 2019

@author: Mike Petersen
'''

import os
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLCDNumber
from journal.view.unbalanced import Ui_Dialog


class UnbalControl:

    def __init__(self, ui):
        ui.unbalLcd.setSegmentStyle(QLCDNumber.Flat)

        pass

if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))

    app = QApplication(sys.argv)
    w = QDialog()
    ui  = Ui_Dialog()
    ui.setupUi(w)
    ubd = UnbalControl(ui)
    w.show()
    sys.exit(app.exec_())