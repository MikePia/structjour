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
Controller for dailyform

Created on April 8, 2019

@author: Mike Petersen
'''
import logging
import os
import sys
from collections import OrderedDict

import numpy as np
import pandas as pd
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QFont, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QDialog, QMessageBox, QWidget, QHBoxLayout, QLabel, QSizePolicy

from structjour.models.trademodels import TradeSum
from structjour.thetradeobject import SumReqFields
from structjour.view.charts.dailyprofit_barchart import Canvas
from structjour.view.forms.dailyform import Ui_Form as DailyForm
from structjour.view.dfmodel import PandasModel
from structjour.view.ejcontrol import EJControl


def fc(val):
    '''formatCurrency'''
    if not isinstance(val, (float, np.floating)):
        return str(val)
    if val >= 0:
        val = '${:.02f}'.format(val)
    else:
        val = '(${:.02f})'.format(val).replace('-', '')

    return val


class QDialogWClose(QDialog):
    '''A message box with a close event handler'''
    def closeEvent(self, event):
        '''Overridden event handler'''
        t = self.windowTitle()
        if t.find('text edited') > 0:
            msg = 'Daily notes contents has changed. Would you like to save it?\n'
            ok = QMessageBox.question(self, 'Save Notes?', msg,
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ok == QMessageBox.Yes:
                self.commitNote()


class DailyControl(QDialog):
    '''
    Controller for the daily summary form. The form includes a user notes saved in db, 2 daily
    summary forms and processed input file showing the days transactions. The daily summaryies
    are driven by data and are not saved.
    '''
    def __init__(self, daDate=None, db=None):
        '''
        Initialize the dialog ui. Optionally set a local db
        '''
        super().__init__(parent=None)

        self.ui = DailyForm()
        self.ui.setupUi(self)
        self.date = None
        if daDate:
            self.date = pd.Timestamp(daDate)
        settings = QSettings('zero_substance', 'structjour')
        if db:
            self.db = db
        else:
            self.db = settings.value('tradeDb')
            if not self.db:
                j = self.settings.value('journal')
                if not j:
                    logging.info('Please set the location of your journal directory.')
                    EJControl()
                    j = self.settings.value('journal')
                    if not j:
                        return
                self.db = os.path.join(j, 'structjour.sqlite')
                settings.setValue('tradeDb', self.db)

    def runDialog(self, df, tradeSum=None):
        '''
        Top level script for this form. Populate the widgets.
        '''
        if not self.date:
            if 'Date' in df.columns:
                self.date = pd.Timestamp(df.Date[0])

        self.ts = tradeSum
        self.modelT = PandasModel(df)
        self.ui.tradeTable.setModel(self.modelT)
        self.ui.tradeTable.resizeColumnsToContents()

        self.modelM = QStandardItemModel(self)
        self.ui.mstkForm.setModel(self.modelM)
        self.ui.mstkForm.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.populateM()

        self.populateS()
        self.setWindowTitle('Daily Summary ... text edited')

        self.setWindowTitle('Daily Summary')

    def gatherDSumData(self, ts=None):
        '''Put together inot a dictionary the data for populating the Daily Summary
        :ts: TradeSummary dictionary. If called without running runDialog, this must be provided
             If this is called from within the dialog, leave it blank.
        '''
        if not self.date:
            return {}, {}
        return TradeSum.getNamesAndProfits(self.date.strftime(self.date.strftime("%Y%m%d")))
        
    def populateS(self):
        '''
        '''
        names, profits = self.gatherDSumData()
        contentWidget = QWidget()
        self.ui.scrollArea.setWidget(contentWidget)
        hbox = QHBoxLayout(contentWidget)
        for account in names:
            if len(names[account]) == 0:
                continue
            canvas = Canvas(self.date.strftime("%Y%m%d"), account)
            canvas.setSizePolicy((QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)))
            hbox.addWidget(canvas)

    def populateM(self):
        '''
        Create and populate the daily mistakes form as a TableView.
        '''
        cell = QStandardItem('Mistake Summary')
        cell.setTextAlignment(Qt.AlignCenter)
        cell.setFont(QFont('Arial Rounded MT Bold', pointSize=24))
        row = [cell]
        self.modelM.appendRow(row)
        row = []
        for d in ['Name', 'PnL', 'Lost Plays', 'Mistake or pertinent feature of trade']:
            cell = QStandardItem(d)
            cell.setFont(QFont('Arial Narrow', pointSize=16, weight=63))
            row.append(cell)
        self.modelM.appendRow(row)

        totalpl = 0.0
        totalPlays = 0.0
        if self.ts:
            for trade in self.ts:
                row = []
                row.append(QStandardItem(trade))

                # Legacy saved object thing
                if 'P / L' in self.ts[trade].keys():
                    self.ts[trade].rename(columns={'P / L': 'PnL'}, inplace=True)
                    self.setStatusTip('Legacy object, open each trade, then save then load')

                pl = self.ts[trade]['PnL'].unique()[0]
                if pl and isinstance(pl, (np.floating, float, np.integer, int)):
                    totalpl += pl
                    pl = fc(pl)
                elif isinstance(pl, (bytes, str)):
                    self.ts[trade]['PnL'] = 0.0
                    pl = 0.0
                row.append(QStandardItem(pl))

                mVal = self.ts[trade]['MstkVal'].unique()[0]
                if mVal and isinstance(mVal, (np.floating, float, np.float)):
                    totalPlays = mVal + totalPlays
                    mVal = fc(mVal)
                if mVal and isinstance(mVal, bytes):
                    mVal = 0
                row.append(QStandardItem(mVal))

                row.append(QStandardItem(self.ts[trade]['MstkNote'].unique()[0]))
                self.modelM.appendRow(row)
        row = [QStandardItem(''), QStandardItem(fc(totalpl)), QStandardItem(fc(totalPlays)), QStandardItem('')]
        self.modelM.appendRow(row)

        self.ui.mstkForm.setSpan(0, 0, 1, 4)
        self.ui.mstkForm.setRowHeight(0, 50)
        self.ui.mstkForm.resizeColumnToContents(1)
        self.ui.mstkForm.resizeColumnToContents(2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fn = 'C:/trader/journal/_201904_April/_0403_Wednesday/trades.csv'
    if not os.path.exists(fn):
        sys.exit(app.exec_())
    dff = pd.read_csv(fn)

    d1 = pd.Timestamp(2020, 2, 7)

    w = DailyControl(daDate=d1)
    w.runDialog(dff)
    w.show()

    sys.exit(app.exec_())
