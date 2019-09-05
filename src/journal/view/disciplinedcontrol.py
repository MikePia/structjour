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
import pandas as pd
import sys

from openpyxl import load_workbook

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QSettings

from journal.discipline.disciplined import registerTrades
from journal.stock.utilities import qtime2pd, pd2qtime
from journal.view.disciplinedform import Ui_Dialog as DisciplineDialog

# pylint: disable = C0103

class DisciplineControl(QDialog):
    '''
    Controller for the disciplinedform.ui form
    '''
    def __init__(self):
        super().__init__(parent=None)


        self.ui = DisciplineDialog()
        self.ui.setupUi(self)
        # self.setWindowTitle('Database Tool')
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../../'))

        self.setWindowIcon(QIcon("images/ZSLogo.png"))

        self.settings = QSettings('zero_substance', 'structjour')
        

        self.ui.startBtn.pressed.connect(self.start)
        today = pd.Timestamp.today().date()
        today = pd2qtime(today, qdate=True)
        self.ui.importDateEdit.setDate(today)


    def start(self):
        if not self.settings.value('disciplined'):
            self.ui.showResults.setText('Please set your disciplined file location in file->settings')
            return
        fn = self.settings.value('disciplined')
        if not os.path.exists(fn):
            msg = f'Your set file: {fn} does not exist'
            msg +='\nPlease re-set your disciplined file location in file->settings'
            self.ui.showResults.setText(msg)
            return
        if not self.ui.importDateRadio.isChecked() and not self.ui.importSinceDateRadio.isChecked():
            self.ui.importDateRadio.setChecked(True)
        wb = load_workbook(fn)
        begin = qtime2pd(self.ui.importDateEdit.date())
        self.ui.showResults.setText('')
        if self.ui.importSinceDateRadio.isChecked():
            current = begin
            now = pd.Timestamp.today()
            delt = pd.Timedelta(days=1)
            while now > current:
                msg = registerTrades(wb, current)
                if not msg:
                    msg = f'''Processed date: {current.strftime('%A, %B %d, %Y')}'''
                self.ui.showResults.append(msg)
                # self.ui.showResults.update()
                QApplication.processEvents() #update gui for pyqt
                current += delt
        else:
            msg = registerTrades(wb, begin)
            if not msg:
                msg = f'''Processed date {begin.strftime('%A, %B %d, %Y')}'''
            self.ui.showResults.append(msg)

        wb.save(fn)
        self.ui.showResults.append('done!')
    
        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w  = DisciplineControl()
    w.show()
    # w.runDialog()

    sys.exit(app.exec_())
