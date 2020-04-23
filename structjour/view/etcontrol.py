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
Grab a tag from the user.
Instantiate the ui form and create all the needed connections to run it.

Created on April 21, 2020

@author: Mike Petersen
'''
import logging
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QSettings

from structjour.models.trademodels import Tags
from structjour.view.forms.entertag import Ui_Dialog as EtDlg


class ETControl(QDialog):

    def __init__(self):
        super().__init__()

        ui = EtDlg()
        ui.setupUi(self)
        self.ui = ui
        self.settings = QSettings('zero_substance', 'structjour')

        self.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))

        ok = self.exec()
        if ok:
            j = self.ui.tagEdit.text()
            Tags.addTag(j)
            return
        logging.info('Failed to set the journal directory')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ETControl()
    sys.exit(app.exec_())
