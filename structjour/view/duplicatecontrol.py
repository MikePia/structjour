# Structjour -- a daily trade review helper
# Copyright (C) 2020 Zero Substance Trading
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
import logging
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog

from structjour.view.forms.duplicatetrade import Ui_Dialog as DupDialog
from structjour.statements.dbdoctor import DbDoctor
# pylint: disable = C0103


class DupControl(QDialog):
    '''
    Controller for the duplicatetrade.ui
    '''
    def __init__(self):
        super().__init__(parent=None)
        self.ui = DupDialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Database Tool')

        self.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))
        self.nextRecord = None
        self.numDups = None
        self.deletMe = None
        self.dups = None
        self.settings = QSettings('zero_substance', 'structjour')

        # Format of actionTaken:
        # [[[done, action],[done, action)]], ...]
        # Keep track of action taken on [[[dups], [deleteMe]], ...]
        self.actionTaken = list()

        self.ui.deleteTxBtn.setEnabled(False)
        self.ui.deleteTradeBtn.setEnabled(False)
        self.ui.showDupPrevBtn.setEnabled(False)

        self.ui.showDupBtn.pressed.connect(self.showNext)
        self.ui.showDupPrevBtn.pressed.connect(self.showPrev)
        self.ui.deleteTxBtn.pressed.connect(self.deleteTx)
        self.ui.deleteTradeBtn.pressed.connect(self.deleteTrade)
        self.ui.accountEdit.editingFinished.connect(self.setAccount)

        acnt = self.settings.value('account')
        self.ui.accountEdit.setText(acnt)
        self.account = acnt
        self.dbdr = None

    def deleteTrade(self):
        ts_id = self.ui.deleteTradeEdit.text()
        tsid1 = self.dups[self.nextRecord][10]
        tsid2 = self.dups[self.nextRecord][11]

        if int(ts_id) not in [tsid1, tsid2]:
            logging.info(f'''Deleting {ts_id} is not an option''')
            return
        if self.dbdr.deleteTradeSumById(int(ts_id)):
            self.actionTaken[self.nextRecord][1] = [True, int(ts_id)]
            self.showTrades()
            self.ui.deleteTradeEdit.setText('')
            self.ui.deleteTradeBtn.setEnabled(False)
            self.ui.deleteTxBtn.setEnabled(False)

    def deleteTx(self):
        t_id = self.ui.deleteTxEdit.text()
        id1 = self.dups[self.nextRecord][0]
        id2 = self.dups[self.nextRecord][1]

        if int(t_id) not in [id1, id2]:
            logging.info(f'''Deleting {t_id} is not an option''')
            return
        if self.dbdr.deleteTradeById(int(t_id)):
            self.actionTaken[self.nextRecord][0] = [True, int(t_id)]
            self.showTrades()
            sid = self.ui.deleteTradeEdit.text()
            if sid:
                self.ui.deleteTradeBtn.setEnabled(True)
                self.ui.deleteTxBtn.setEnabled(False)

    def initialize(self):
        if not self.dbdr:
            self.dbdr = DbDoctor(account=self.account)
        deleteMe, dups = self.dbdr.doDups()
        if dups:
            self.nextRecord = 0
            self.numDups = len(dups)
            self.deleteMe = deleteMe
            self.dups = dups
            self.actionTaken = [[[False, None], [False, None]] for i in range(self.numDups)]

    def dictToTable(self, d):
        '''
        Create an html table that displays the dict d
        :d: A dict or a list of dict of the same type
        '''

        if not isinstance(d, list):
            d = [d]
        columns = list(d[0].keys())
        msg = '''<table style="width100%"><tr>'''
        for col in columns:
            msg += f'<th>{col}</th>'
        msg += '</tr>'

        for dic in d:
            msg += '<tr>'
            for col in columns:
                msg += f'<td>{dic[col]}</td>'
            msg += '</tr>'
        msg += '</table>'
        return msg

    def showPrev(self):
        if self.dups is None:
            self.initialize()
        if not self.dups:
            self.ui.showDuplicate.setHtml('<h2>No duplicates have been found.</h2>')
            return

        if self.nextRecord > 0:
            self.nextRecord -= 1
            if self.nextRecord == 0:
                self.ui.showDupPrevBtn.setEnabled(False)
            else:
                self.ui.showDupPrevBtn.setEnabled(True)
            if self.nextRecord < self.numDups - 1:
                self.ui.showDupBtn.setEnabled(True)
        self.showTrades()

    def showNext(self):
        if self.dups is None:
            self.initialize()
        if not self.dups:
            self.ui.showDuplicate.setHtml('<h2>No duplicates have been found.</h2>')
            return
        if self.nextRecord < self.numDups - 1:
            self.nextRecord += 1
            if self.nextRecord == self.numDups - 1:
                self.ui.showDupBtn.setEnabled(False)
            else:
                self.ui.showDupBtn.setEnabled(True)
            if self.nextRecord > 0:
                self.ui.showDupPrevBtn.setEnabled(True)
            else:
                self.ui.showDupPrevBtn.setEnabled(False)
        self.showTrades()

    def setAccount(self):
        acnt = self.ui.accountEdit.text()
        if not acnt:
            acnt = self.settings.value('account')
        if acnt:
            self.settings.setValue('account', acnt)
            self.account = acnt
        if self.dbdr:
            self.dbdr.account = acnt

    def showTrades(self):
        id1 = self.dups[self.nextRecord][0]
        id2 = self.dups[self.nextRecord][1]
        delMe = self.deleteMe[self.nextRecord]

        # head and stylesheet
        msg = '<!DOCTYPE html<!DOCTYPE HTML> <html> <head> <meta charset="utf-8"> <style type="text/css">'
        msg += '''table, th, td { border: 1px solid black; border-collapse: collapse; }'''
        msg += '</style></head><body>'

        # Beginning of doc
        msg += f'<h2>The records {id1} and {id2} appear to be duplicates.</h2>'
        msg += f'<h3>Trade {self.nextRecord+1} of {self.numDups}.      Recommend to delete {delMe[0]}</h3>'
        t1 = self.dbdr.getTradesByID(id1)
        t2 = self.dbdr.getTradesByID(id2)

        if self.actionTaken[self.nextRecord][0][0]:
            msg += f'<h4>Action has been taken. Deleted record {self.actionTaken[self.nextRecord][0][1]}'
            self.ui.deleteTxBtn.setEnabled(False)
            self.ui.deleteTxEdit.setText('')
        else:
            self.ui.deleteTxEdit.setText(str(delMe[0]))
            self.ui.deleteTxBtn.setEnabled(True)
            # Display both duplicate records as html table
            msg += self.dictToTable([t1, t2])

        if delMe[1]:
            # Show trade_sum record or action taken
            msg += f'<h3>Recommend to delete trade_sum record {delMe[1]}</h4>'
            if self.actionTaken[self.nextRecord][1][0]:
                msg += f'<h4>Action has been taken. Deleted trade sum record {self.actionTaken[self.nextRecord][1][1]}'
            else:
                self.ui.deleteTradeEdit.setText(str(delMe[1]))

                tstab = list()

                # Get 1 or 2 records to show and and a column showing the related trade ids for each
                ts_1 = self.dbdr.getTradeSumByID(delMe[1])
                t1_ids = self.dbdr.getTradesForTSID(delMe[1])
                if t1_ids:
                    t1_ids = [x[0] for x in t1_ids]
                ts_1['RelTrades'] = t1_ids
                tstab.append(ts_1)

                ts2_id = None
                # t1 or t2 may have been deleted but we still want to show any the trade_sums records
                if t1 and t1['ts_id'] != delMe[1]:
                    ts2_id = t1['ts_id']
                elif t2 and t2['ts_id'] != delMe[1]:
                    ts2_id = t2['ts_id']
                if ts2_id:
                    ts_2 = self.dbdr.getTradeSumByID(ts2_id)
                    t2_ids = self.dbdr.getTradesForTSID(ts2_id)
                    if t2_ids:
                        t2_ids = [x[0] for x in t2_ids]
                    ts_2['RelTrades'] = t2_ids
                    tstab.append(ts_2)

                msg += self.dictToTable(tstab)

        msg += '</body></html>'

        self.ui.showDuplicate.setHtml(msg)
        # self.ui.deleteTxBtn.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # fn = 'C:/trader/journal/_201904_April/_0403_Wednesday/trades.csv'
    # if not os.path.exists(fn):
    #     sys.exit(app.exec_())
    # dff = pd.read_csv(fn)

    # d1 = pd.Timestamp(2030, 6, 6)

    w = DupControl()
    w.show()
    # w.runDialog()

    sys.exit(app.exec_())
