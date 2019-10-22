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
Instantiate the ui form and create all the needed connections to run it.

Created on May 8, 2019

@author: Mike Petersen
'''
import logging
import os
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.QtCore import QSettings

from structjour.view.enterjournal import Ui_Dialog as EjDlg

# pylint: disable = C0301, C0103


class EJControl(QDialog):
    '''
    Pop up and request the journal directory
    '''
    def __init__(self):
        super().__init__()


        ui = EjDlg()
        ui.setupUi(self)
        self.ui = ui
        self.ui.browseBtn.pressed.connect(self.browse)
        self.settings = QSettings('zero_substance', 'structjour')

        self.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))

        ok = self.exec()
        if ok:
            j = self.ui.journalEdit.text()
            if os.path.exists(j):
                self.settings.setValue('journal', j)
                logging.info('Successfully set the journal directory')
                return
        logging.info('Failed to set the journal directory')

    def browse(self):
        '''
        Open a file dialog and set the results to the QLineEdit 'journalEdit'. Triggered by its
        neighboring button.
        '''

        path = QFileDialog.getExistingDirectory(None, "Select Directory")
        self.ui.journalEdit.setText(path)
        # self.settings.setValue('journal', path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = EJControl()
    # sys.exit(app.exec_())
    