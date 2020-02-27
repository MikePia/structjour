# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
'''
Controller for getdate form

Created on February 25, 2020

@author: Mike Petersen
'''

import sys

from structjour.stock.utilities import qtime2pd
from structjour.view.getdate import Ui_Dialog as GetDateDialog

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings


class GetDate(QDialog):
    '''
    CreateDirs is a dialog that enables the user to disable the auto gen of directories
    and provides a facility to choose what months of subdirectories to be created.
    '''
    def __init__(self, testSettings=None):
        '''
        :params testSettings: Override the settings key. Intended for testing. Proividing
            a value for testSettings will prevent show from being called.
        '''
        super().__init__(parent=None)
        if testSettings:
            self.settings = testSettings
        else:
            self.settings = QSettings('zero_substance', 'structjour')

        self.ui = GetDateDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))

        self.ui.dateEdit.dateChanged.connect(self.dateChanged)
        self.ui.buttonBox.clicked.connect(self.ok)

        if not testSettings:
            self.show()

    def ok(self, val):
        print(val.text())
        if val.text() == 'OK':
            # print(qtime2pd(self.ui.dateEdit.date()))
            self.settings.setValue('theDate', qtime2pd(self.ui.dateEdit.date()))

    def dateChanged(self, val):
        # print(val)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = GetDate()
    print(w)

    out = sys.exit(app.exec_())
    print(out)
