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
import datetime as dt
import os
import sqlite3.test.transactions
import sys
from collections import OrderedDict

import numpy as np
import pandas as pd
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QFont, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QWidget, QDialog, QMessageBox

from journal.thetradeobject import SumReqFields
from journal.view.dailyform import Ui_Form as DailyForm
from journal.view.dfmodel import PandasModel
from journal.view.ejcontrol import EJControl

# pylint: disable = C0103, W0201

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
   def closeEvent(self, event):
    print("X is clicked")
    t = self.windowTitle()
    if t.find('text edited') > 0:
        msg = 'Daily notes contents has changed. Would you like to save it?\n'
        ok = QMessageBox.question(self, 'Save Notes?', msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ok == QMessageBox.Yes:
            self.commitNote()

class DailyControl(QDialogWClose):
    '''
    Controller for the daily summary form. The form includes a user notes saved in db, 2 daily
    summary forms and processed input file showing the days transactions. The daily summaryies
    are driven by data and are not saved.
    '''
    def __init__(self, daDate=None):
        super().__init__(parent=None)
        self.ui = DailyForm()
        self.ui.setupUi(self)
        self.date = None
        if daDate:
            self.date = pd.Timestamp(daDate)
        apiset = QSettings('zero_substance/stockapi', 'structjour')
        self.db = apiset.value('dbsqlite')
        if not self.db:
            j = self.settings.value('journal')
            if not j:
                print('Please set the location of the your journal directory.')
                EJControl()
                j = self.settings.value('journal')
                if not j:
                    return
            self.db = os.path.join(j, 'structjour.sqlite')
            apiset.setValue('dbsqlite', self.db)

    def createTable(self):
        '''create db table'''

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE if not exists "daily_notes" (
                	"date"	INTEGER,
                	"note"	TEXT,
                	PRIMARY KEY("date"))''')
        conn.commit()

    def dropTable(self):
        '''Drop db table daily_notes'''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''DROP TABLE IF EXISTS daily_notes''')
        conn.commit()

    def commitNote(self, note=None):
        '''Save or update the db file for the notes field. This commits the text in the dailyNotes widget.
        Use setNote for a vanilla db commit'''
        if not self.date:
            print('Cannot save without a date')
            return
        d = self.date.strftime('%Y%m%d')
        d = int(d)
        if not note:
            note = self.ui.dailyNotes.toPlainText()

        exist = self.getNote()

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        if exist:
            cur.execute('''UPDATE daily_notes
                SET note = ? 
                WHERE date = ?''', (note, d))

        else:
            cur.execute('''INSERT INTO daily_notes (date, note)
                        VALUES(?,?)''', (d, note))
        conn.commit()

    def setNote(self, note):
        '''
        Commit or update the dailyNotes db table with self.date and note
        '''
        if not self.date:
            print('Cannot save without a date')
            return
        d = self.date.strftime('%Y%m%d')
        d = int(d)

        exist = self.getNote()

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        if exist:
            cur.execute('''UPDATE daily_notes
                SET note = ? 
                WHERE date = ?''', (note, d))

        else:
            cur.execute('''INSERT INTO daily_notes (date, note)
                        VALUES(?,?)''', (d, note))
        conn.commit()

    def getNote(self):
        '''
        Retrieve the notes field for the db entry for the date associated with this object. The
        date can be given as an argument or retrieved from the df argument for runDialog.
        '''
        if not self.date:
            print('Cannot retrieve a note without a date')
            return
        d = self.date.strftime('%Y%m%d')
        d = int(d)

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''SELECT * from daily_notes where date = ?''', (d,))
        cursor = cur.fetchone()
        if cursor:
            return cursor[1]
        return cursor

    def populateNotes(self):
        '''
        Get a saved note for this object
        '''
        note = self.getNote()
        if not note:
            note = ''
        self.ui.dailyNotes.setText(note)

    def dNotesChanged(self):
        ''' daily notes field changed. Set the edited flag. '''
        self.setWindowTitle('Daily Summary ... text edited')
    
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

        self.modelS = QStandardItemModel(self)
        self.ui.dailyStatTab.setModel(self.modelS)
        self.ui.dailyStatTab.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.populateS()
        self.setWindowTitle('Daily Summary ... text edited')

        self.ui.dailyNotes.clicked.connect(self.saveNotes)
        self.ui.dailyNotes.textChanged.connect(self.dNotesChanged)



        self.createTable()
        self.populateNotes()

        self.setWindowTitle('Daily Summary')

    def saveNotes(self, event):
        '''
        Connected method from a context menu for the dailyNotes widget.
        '''
        self.commitNote()

        self.setWindowTitle('Daily Summary')   
    
    def gatherDSumData(self, ts=None):
        '''Put together inot a dictionary the data for populating the Daily Summary
        :ts: TradeSummary dictionary. If called without running runDialog, this must be provided
             If this is called from within the dialog, leave it blank. 
        '''
        if ts:
            self.ts = ts
        srf = SumReqFields()
        liveWins = list()
        liveLosses = list()
        simWins = list()
        simLosses = list()
        maxTrade = (0, "notrade")
        minTrade = (0, "notrade")
        #Didnot save the Trade number in TheTrade.  These should be the same order...
        count = 0

        if not self.ts:
            print('Trade data not found')
            return

        # Gather all the data
        for key in self.ts:
            TheTrade = self.ts[key]
            pl = TheTrade[srf.pl].unique()[0]
            live = True if TheTrade[srf.acct].unique()[0] == "Live" else False
            count = count + 1

            if pl is None:
                pl = 0.0
            # A bug-ish inspired baby-sitter
            elif isinstance(pl, str):
                if pl == '':
                    pl = 0
                else:
                    try:
                        pl = float(pl)
                    except NameError:
                        raise ValueError('Malformed float for variable pl in createDailySummary')
            if float(pl) > maxTrade[0]:
                maxTrade = (pl, "Trade{0}, {1}, {2}".format(
                    count, TheTrade[srf.acct].unique()[0], TheTrade[srf.name].unique()[0]))
            if pl < minTrade[0]:
                minTrade = (pl, "Trade{0}, {1}, {2}".format(
                    count, TheTrade[srf.acct].unique()[0], TheTrade[srf.name].unique()[0]))

            if live:
                if pl > 0:
                    liveWins.append(pl)
                else:
                    liveLosses.append(pl)
            else:
                if pl > 0:
                    simWins.append(pl)
                else:
                    simLosses.append(pl)

        dailySumData = OrderedDict()

        #row1
        dailySumData['livetot'] = fc(sum([sum(liveWins), sum(liveLosses)]))

        numt = len(liveWins) + len(liveLosses)
        if numt == 0:
            dailySumData['livetotnote'] = "0 Trades"
        else:
            note = "{0} Trade{1}, {2} Winner{3}, {4}, Loser{5}"
            note = note.format(numt, "" if numt == 1 else "s", len(liveWins),
                               "" if len(liveWins) == 1 else "s", len(
                                   liveLosses),
                               "" if len(liveLosses) == 1 else "s")
            dailySumData['livetotnote'] = note

        #row2
        dailySumData['simtot'] = fc(sum([sum(simWins), sum(simLosses)]))

        # 9 trades,  3 Winners, 6 Losers
        numt = len(simWins) + len(simLosses)
        if numt == 0:
            dailySumData['simtotnote'] = "0 Trades"
        else:  # 4 trades, 1 Winner, 3 Losers
            note = "{0} Trade{1}, {2} Winner{3}, {4}, Loser{5}"
            note = note.format(numt, "" if numt == 1 else "s",
                               len(simWins), "" if len(simWins) == 1 else "s",
                               len(simLosses), "" if len(simLosses) == 1 else "s")
            dailySumData['simtotnote'] = note

        # row3
        dailySumData['highest'] = fc(maxTrade[0])
        dailySumData['highestnote'] = maxTrade[1]

        # row 4
        dailySumData['lowest'] = fc(minTrade[0])
        dailySumData['lowestnote'] = minTrade[1]

        # row 5
        if (len(liveWins) + len(simWins)) == 0:
            dailySumData['avgwin'] = '$0.00'
        else:
            dailySumData['avgwin'] = fc(sum(
                [sum(liveWins), sum(simWins)]) / (len(liveWins) + len(simWins)))
        dailySumData['avgwinnote'] = "X {} =  {}".format(
            len(liveWins) + len(simWins), fc(sum([sum(liveWins), sum(simWins)])))

        # row 6
        if len(liveLosses) + len(simLosses) == 0:
            dailySumData['avgloss'] = '$0.00'
        else:
            dailySumData['avgloss'] = fc(sum([sum(liveLosses), sum(
                simLosses)]) / (len(liveLosses) + len(simLosses)))
        dailySumData['avglossnote'] = "X {} =  (${:.2f})".format(
            len(liveLosses) + len(simLosses), abs(sum([sum(liveLosses), sum(simLosses)])))
        return dailySumData

    def populateS(self):
        '''
        Create and populate the daily summary form as a tableView
        '''
        cell = QStandardItem('Daily P / L Summary')
        cell.setTextAlignment(Qt.AlignCenter)
        cell.setFont(QFont('Arial Rounded MT Bold', pointSize=24))
        row = [cell]
        self.modelS.appendRow(row)

        dailySumData = self.gatherDSumData()
        if not dailySumData:
            return


        ro1 = [QStandardItem('Live Total'), QStandardItem(str(dailySumData['livetot'])), QStandardItem(dailySumData['livetotnote'])]
        ro2 = [QStandardItem('Sim Total'), QStandardItem(str(dailySumData['simtot'])), QStandardItem(dailySumData['simtotnote'])]
        ro3 = [QStandardItem('Highest Profit'), QStandardItem(str(dailySumData['highest'])), QStandardItem(dailySumData['highestnote'])]
        ro4 = [QStandardItem('Largest Loss'), QStandardItem(str(dailySumData['lowest'])), QStandardItem(dailySumData['lowestnote'])]
        ro5 = [QStandardItem('Average Win'), QStandardItem(str(dailySumData['avgwin'])), QStandardItem(dailySumData['avgwinnote'])]
        ro6 = [QStandardItem('Average Loss'), QStandardItem(str(dailySumData['avgloss'])), QStandardItem(dailySumData['avglossnote'])]

        for row in [ro1, ro2, ro3, ro4, ro5, ro6]:
            self.modelS.appendRow(row)

        self.ui.dailyStatTab.setSpan(0, 0, 1, 3)
        self.ui.dailyStatTab.setRowHeight(0, 50)
        self.ui.dailyStatTab.resizeColumnToContents(1)

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

                #Legacy saved object thing
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
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    fn = 'C:/trader/journal/_201904_April/_0403_Wednesday/trades.csv'
    if not os.path.exists(fn):
        sys.exit(app.exec_())
    dff = pd.read_csv(fn)

    d1 = pd.Timestamp(2030, 6, 6)
    
    w = DailyControl(daDate=d1)
    w.runDialog(dff)
    w.show()
    
    sys.exit(app.exec_())
