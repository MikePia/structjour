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
Controller for synchronizefrom

Created on June 11, 2019

@author: Mike Petersen
'''
import os
import sys


from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.QtGui import QPixmap

from journal.stock.utilities import qtime2pd
from journal.view.syncform import Ui_Form as SyncForm
from journal.utilities.synchronizesavedstuff import reportTwinSavedFiles, WeGot

# pylint: disable = C0103


class SyncControl(QDialog):
    def __init__(self, settings):
        super().__init__(parent=None)
        self.settings = settings
        self.ui = SyncForm()
        self.ui.setupUi(self)

        self.ui.startBtn.pressed.connect(self.startSync)

    def startSync(self):
        print ('starting')
        # while True:

        begin = qtime2pd(self.ui.startDate.date())
        result = reportTwinSavedFiles(begin)
        if result[0] == WeGot.ERROR:
            daDate = result[1]
            msg = result[2]
        elif result[0] == WeGot.MISSING_IB_SAVED:
            p, ibname = os.path.split(result[2])
            msg = '<h3>Missing object file</h3>'
            msg = msg + f'''<div>{ibname} from {result[1].strftime('%m/%d/%y')}''' 
            msg = msg + ''' Please open and save the Ib Activity statement from that date</div>'''
            msgbx = QMessageBox()
            msgbx.setIconPixmap(QPixmap("../../images/ZSLogo.png"));
            msgbx.setText(msg)
            msgbx.exec()
        elif result[0] == WeGot.ERROR_MULTIPLE_IB:
            msg = f'<h3>{WeGot.ERROR_MULTIPLE_IB}</h3>'
            msgbx = QMessageBox()
            msgbx.setIconPixmap(QPixmap("../../images/ZSLogo.png"));
            msgbx.setText(msg)
            msgbx.exec()

        else:
            print()
            

if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    settings = QSettings('zero_substance', 'structjour')
    w = SyncControl(settings)
    w.show()
    sys.exit(app.exec_())