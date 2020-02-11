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
Controller for createdirs

Created on February 8, 2020

@author: Mike Petersen
'''

import sys
import pandas as pd
from structjour.view.createdirs import Ui_Dialog as CreateDirsDialog
from structjour.time import createDirsStructjour

from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSettings


class CreateDirs(QDialog):
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

        self.ui = CreateDirsDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))

        self.ui.createDirsBtn.pressed.connect(self.createDirs)
        self.ui.enabledRb.clicked.connect(self.enableAutoGen)
        self.ui.disabledRb.clicked.connect(self.disableAutoGen)

        autog = self.settings.value('directories_autogen', defaultValue=True, type=bool)
        if autog:
            self.ui.enabledRb.setChecked(True)
            self.enableAutoGen()
        else:
            self.ui.disabledRb.setChecked(True)
            self.disableAutoGen()

        lastDir = self.settings.value('lastDirCreated')
        if lastDir:
            dd = pd.Timestamp(lastDir)
            year = dd.strftime('%Y')
            month = dd.strftime('%B')
            self.ui.createDirsYear.setCurrentText(year)
            self.ui.createDirsMonth.setCurrentText(month)


        if not testSettings:
            self.show()

    def createDirs(self):
        '''Create the sub directories in the journal directory'''
        m = pd.Timestamp(f'{self.ui.createDirsMonth.currentText()} {self.ui.createDirsYear.currentText()}')
        try:
            theDir = createDirsStructjour(m, self.settings)
        except ValueError as m:
            if m.args[0].startswith('Directory Already'):
                msg = f'<h3>{m.args[0]}</h3>'
                msg += f'<p>{m.args[1]}</p>'
                msgbx = QMessageBox()
                msgbx.setIconPixmap(QPixmap("structjour/images/ZSLogo.png"))
                msgbx.setText(msg)
                msgbx.exec()
            else:
                raise ValueError(m)
        else:
            # self.settings.setValue('lastDir')
            self.settings.setValue('lastDirCreated', m.strftime('%Y%m01'))
            if self.debug:
                return theDir
            msg = f'<h3>Directories created</h3>'
            msg += f'<p>under {theDir}</p>'
            msgbx = QMessageBox()
            msgbx.setIconPixmap(QPixmap("structjour/images/ZSLogo.png"))
            msgbx.setText(msg)
            msgbx.exec()
        return theDir

    def disableAutoGen(self):
        self.settings.setValue('directories_autogen', 'false')
        self.ui.createDirsBtn.setEnabled(True)

    def enableAutoGen(self):
        self.settings.setValue('directories_autogen', 'true')
        self.ui.createDirsBtn.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CreateDirs()

    sys.exit(app.exec_())
