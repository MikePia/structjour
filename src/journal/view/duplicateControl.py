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
Controller for duplicatetrade.ui

Created on September 2, 2019

@author: Mike Petersen
'''

import os
import sys
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QFont, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QWidget, QDialog

from journal.view.duplicatetrade import Ui_Dialog as DupDialog

class DupControl(QDialog):
    '''
    Controller for the daily summary form. The form includes a user notes saved in db, 2 daily
    summary forms and processed input file showing the days transactions. The daily summaryies
    are driven by data and are not saved.
    '''
    def __init__(self):
        super().__init__(parent=None)
        self.ui = DupDialog()
        self.ui.setupUi(self)



if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    # fn = 'C:/trader/journal/_201904_April/_0403_Wednesday/trades.csv'
    # if not os.path.exists(fn):
    #     sys.exit(app.exec_())
    # dff = pd.read_csv(fn)

    # d1 = pd.Timestamp(2030, 6, 6)
    
    w = DupControl()
    # w.runDialog(dff)
    w.show()
    
    sys.exit(app.exec_())