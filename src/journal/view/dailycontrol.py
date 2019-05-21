import os
import random
import sqlite3.test.transactions
import sys
from collections import OrderedDict
from journal.view.ejcontrol import EJControl


import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QAbstractItemView
from PyQt5.QtGui import QIntValidator, QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import Qt, QSettings

from journal.view.dailyform import  Ui_Form as DailyForm
from journal.view.dfmodel import PandasModel

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

class DailyControl(QWidget):
    def __init__(self, daDate=None):
        super().__init__(parent=None)
        self.ui = DailyForm()
        self.ui.setupUi(self)
        self.ui.dailyNotes.textChanged.connect(self.dNotesChanged)
        self.date = daDate

    def createTable(self):
        # self.dropTable()

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE if not exists "daily_notes" (
                	"date"	INTEGER,
                	"note"	TEXT,
                	PRIMARY KEY("date"))''')
        conn.commit()

    def dropTable(self):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''DROP TABLE IF EXISTS daily_notes''')
        conn.commit()


    def commitNote(self):
        if not self.date:
            print('Cannot save without a date')
            return
        d = self.date.strftime('%Y%m%d')
        d = int(d)
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
                    VALUES(?,?)''',
                    (d, note))
        conn.commit()

    def getNote(self):
        if not self.date:
            print('Cannot retrieve a not without a date')
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
        note = self.getNote()
        if note:
            self.ui.dailyNotes.setText(note)


    def dNotesChanged(self):
        print(self.ui.dailyNotes.toPlainText())
        self.setWindowTitle('Daily Summary ... text edited')
        

    def runDialog(self, df, tradeSum=None):
        if self.date == None:
            if 'Date' in df.columns:
                self.date = df.Date[0]

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


        self.createTable()
        self.populateNotes()

        d = df.index[0]
        print()
        self.setWindowTitle('Daily Summary')
      
    def saveNotes(self, event):
        print('Here ..... .....', event)
        desc = self.ui.dailyNotes.toPlainText()
        self.commitNote()

        self.setWindowTitle('Daily Summary')


    def populateS(self):
        '''
        '''

        cell = QStandardItem('Daily P / L Summary')
        cell.setTextAlignment(Qt.AlignCenter)
        cell.setFont(QFont('Arial Rounded MT Bold', pointSize=24))
        row = [cell]
        self.modelS.appendRow(row)
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

            # A bug-ish inspired baby-sitter
            if isinstance(pl, str):
                if pl == '':
                    pl = 0
                else:
                    try:
                        pl = float(pl)
                    except NameError:
                        raise ValueError(
                            'Malformed float for variable pl in createDailySummary')

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
        print()


    def populateM(self):
        cell = QStandardItem('Mistake Summary')
        cell.setTextAlignment(Qt.AlignCenter)
        cell.setFont(QFont('Arial Rounded MT Bold', pointSize=24))
        row = [cell]
        self.modelM.appendRow(row)
        row = []
        for d in ['Name', 'P / L', 'Lost P/L', 'Mistake or pertinent feature of trade']:
            cell = QStandardItem(d)
            cell.setFont(QFont('Arial Narrow', pointSize=16, weight=63))
            row.append(cell)
        self.modelM.appendRow(row)

        totalpl = 0
        if self.ts:
            for trade in self.ts:
                row = []
                row.append(QStandardItem(trade))

                pl = self.ts[trade]['P / L'].unique()[0]
                if pl and isinstance(pl, (np.floating, float)):
                    totalpl += pl
                    pl = fc(pl)
                row.append(QStandardItem(pl))

                mVal = self.ts[trade]['MstkVal'].unique()[0]
                if mVal and isinstance(mVal, (np.floating, float)):
                    mVal = fc(mVal)
                row.append(QStandardItem(mVal))
                
                row.append(QStandardItem(self.ts[trade]['MstkNote'].unique()[0]))
                self.modelM.appendRow(row)
        q = QStandardItem('')
        row = [q, q, QStandardItem(fc(totalpl)), q]
        self.modelM.appendRow(row)

        self.ui.mstkForm.setSpan(0, 0, 1, 4)
        self.ui.mstkForm.setRowHeight(0, 50)
        self.ui.mstkForm.resizeColumnToContents(1)
        self.ui.mstkForm.resizeColumnToContents(2)
        print()


from journal.thetradeobject import SumReqFields
# pylint: disable = C0103


class MistakeSummaryQ:
    '''
    Creation of these tables in Qt and excel has completely diverged
    TODO Figure a way to unify the excel and qt table stuff for the mistake and daily summary. Or
    at least to use a combined data structure for creating them. Or maybe its not worth it. The 
    coordinates and data are different. For now I continue thie diverged stuff.
    '''

    def __init__(self, numTrades, anchor=(1, 1)):

        # Create the data structure to create a styled shape for the Daily Summary Form
        # 'key':[rng, style, value] 
        dailySummaryFields = {
            'title': [[(0, 0), (0, 3)], 'titleStyle', "Daily P / L Summary"],
            'headlivetot': [(1, 0), 'normStyle', "Live Total"],
            'livetot': [(1, 1), 'normalNumber'],
            'livetotnote': [(1, 2), 'normStyle'],

            'headsimtot': [(2, 0),  'normStyle', "Sim Total"],
            'simtot': [(2, 1), 'normalNumber'],
            'simtotnote': [(2, 2), 'normStyle'],

            'headhighest': [(3, 0), 'normStyle', "Highest Profit"],
            'highest': [(3, 1), 'normalNumber'],
            'highestnote': [(3, 2), 'normStyle'],

            'headlowest': [ (4, 0), 'normStyle', "Largest Loss"],
            'lowest': [(4, 1), 'normalNumber'],
            'lowestnote': [(4, 2), 'normStyle'],

            'headavgwin': [ (5, 0), 'normStyle', "Average Win"],
            'avgwin': [(5, 1), 'normalNumber'],
            'avgwinnote': [(5, 2), 'normStyle'],

            'headavgloss': [ (6, 0), 'normStyle', "Average Loss"],
            'avgloss': [(6, 1), 'normalNumber'],
            'avglossnote': [(6, 2), 'normStyle'],
        }


        # # Excel formulas belong in the mstkval and mstknote columns. The srf.tfcolumns bit
        # # are the target addresses for the Excel formula. The cell translation
        # # takes place when we create and populate the Workbook.
        # formulas = dict()
        # srf = SumReqFields()
        # for i in range(numTrades):

        #     tp = "tpl" + str(i+1)
        #     formulas[tp] = ['={0}', srf.tfcolumns[srf.pl][0][0]]
        #     p = "pl" + str(i + 1)
        #     formulas[p] = ['={0}', srf.tfcolumns[srf.mstkval][0][0]]
        #     m = "mistake" + str(i + 1)
        #     formulas[m] = ['={0}', srf.tfcolumns[srf.mstknote][0][0]]

        self.dailySummaryFields = dailySummaryFields

if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    d = pd.Timestamp(2030, 6, 6)
    w = DailyControl(daDate=d)
    fn = 'C:/trader/journal/_201904_April/_0403_Wednesday/trades.csv'
    if not os.path.exists(fn):
        sys.exit(app.exec_())
    dff = pd.read_csv(fn)
    print('gotta create swingTrade data type here to run this thing seperately')
    w.runDialog(dff)
    w.show()
    sys.exit(app.exec_())
