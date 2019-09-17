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
Test the module dailycontrol

Created on May 22, 2019

@author: Mike Petersen
'''

import os
import sys
import unittest
from  unittest import TestCase

import pandas as pd
import sqlite3

# https://stackoverflow.com/questions/57426219/how-to-import-qtwebenginewidgets-after-qapplication-has-been-created
# thanks to ekhumoro.
# Strangely the import error occurs using (before installing webengine_hack here):
# python -m unittest discover
# But not when using from the test directory:
# python -m unittest test_dailycontrol
# or any other local run
def webengine_hack():
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication.instance()
    if app is not None:
        import sip
        app.quit()
        sip.delete(app)
    import sys
    from PyQt5 import QtCore, QtWebEngineWidgets
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.qApp = QtWidgets.QApplication(sys.argv)
    return app

try:
    # just for testing
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([''])
    from PyQt5 import QtWebEngineWidgets
except ImportError as exception:
    print('\nRetrying webengine import...')
    app = webengine_hack()
    from PyQt5 import QtWebEngineWidgets

# from PyQt5 import QtCore, QtWebEngineWidgets
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QApplication, QLineEdit, QCheckBox, QSpinBox, QComboBox

from PyQt5.QtTest import QTest


from structjour.view.dailycontrol import DailyControl
from structjour.journalfiles import JournalFiles
from structjour.definetrades import DefineTrades
from structjour.pandasutil import InputDataFrame

from structjour.statement import Statement_IBActivity
from structjour.statements.ibstatementdb import StatementDB
from structjour.statements.ibstatement import IbStatement

from structjour.view.layoutforms import LayoutForms
from structjour.view.sumcontrol import SumControl



# pylint: disable = C0103

app = QApplication(sys.argv)

class TestDailyCtrl(TestCase):
    '''Test the db calls and the user interaction stuff'''

    def __init__(self, *args, **kwargs):
        super(TestDailyCtrl, self).__init__(*args, **kwargs)

        self.testdb = 'test/testdb.sqlite'
        self.apiset = QSettings('zero_substance/stockapi', 'structjour')
        self.realdb = self.apiset.value('dbsqlite') 


    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))
        self.conn = sqlite3.connect(self.testdb)
        self.inputtype = 'IB_HTML' 

        indir = 'data/'
        f2 = 'ActivityStatement.20190313_PL.html'
        f1 = 'ActivityStatement.20190404.html'
        theDate = pd.Timestamp('2019-04-04')

        jf = JournalFiles(indir=indir, infile=f1, theDate=theDate, inputType='IB_HTML', mydevel=False)


        jf.inputType = 'IB_HTML'
        # statement = Statement_IBActivity(jf)
        # df = statement.getTrades_IBActivity(jf.inpathfile)

        ibs = IbStatement(db=self.testdb)
        ibdb = StatementDB(self.testdb)
        ibdb.reinitializeTradeTables()
        ibs.openIBStatementHtml(jf.inpathfile)
        df2 = ibdb.getStatement(theDate)
        if df2.empty:
            sdate = theDate.strftime('%Y-%m-%d')
            msg = f'In test_dailycontrol.setup: Error: found no trades in db for {sdate}'
            self.assertTrue(not df2.empty, msg)
        
        tu = DefineTrades(jf.inputType)
        inputlen, dframe, ldf = tu.processDBTrades(df2)
        self.df = dframe
        sc = SumControl()
        lf = LayoutForms(sc, jf, dframe)
        # lf.pickleitnow()
        tradeSummaries = lf.runTtoSummaries(ldf)
        self.ts = lf.ts
        ibdb.addTradeSummaries(tradeSummaries, ldf)
        print()

    def tearDown(self):
        self.apiset.setValue('dbsqlite', self.realdb)

    def test_createTable(self):
        cur = self.conn.cursor()

        cur.execute(''' DROP TABLE IF EXISTS daily_notes''')
        self.conn.commit()

        daDate = pd.Timestamp('2021-06-06')
        dc = DailyControl(daDate, db=self.testdb)
        dc.runDialog(self.df, tradeSum=self.ts)
        dc.createTable()
        self.conn.commit()
        zilch = dc.getNote()
        # If we are still here, no exception, the table exists
        self.assertIs(zilch, None)

    def test_dropTable(self):
        daDate = pd.Timestamp('2021-06-06')
        dc = DailyControl(daDate, db=self.testdb)
        dc.runDialog(self.df, tradeSum=self.ts)
        dc.createTable()
        self.conn.commit()
        zilch = dc.getNote()
        dc.dropTable()
        # self.assertRaises
        self.assertRaises(sqlite3.OperationalError, dc.getNote)

    def test_commitNote(self):
        daDate = pd.Timestamp('2021-06-06')
        dc = DailyControl(daDate, db=self.testdb)
        dc.runDialog(self.df, tradeSum=self.ts)
        dc.dropTable()
        dc.createTable()
        note = '''Twas all hallow's  eve and all throug the grove
                  jabberwock trounced his thro boro-dove'''
        dc.ui.dailyNotes.setText(note)
        dc.commitNote()
        xnote = dc.getNote()
        self.assertEqual(note, xnote)

        updatenote = '''Twas all hallow's  eve and all throug the grove
                        jabberwock trounced his thro boro-dove.
                        The Jack-lanterns sat on porch all alight,
                        the hopes of the ghouls was thick in the night.'''
        dc.ui.dailyNotes.setText(updatenote)
        dc.commitNote()
        xnote = dc.getNote()
        self.assertEqual(updatenote, xnote)

    def test_getnote(self):
        daDate = pd.Timestamp('2021-06-06')
        dc = DailyControl(daDate, db=self.testdb)
        dc.runDialog(self.df, tradeSum = self.ts)
        dc.dropTable()
        dc.createTable()
        note = '''Twas all hallow's  eve and all throug the grove
                  jabberwock trounced his thro boro-dove'''
        dc.ui.dailyNotes.setText(note)
        dc.commitNote()
        xnote = dc.getNote()
        self.assertEqual(note, xnote)

    def test_populateNotes(self):
        daDate = pd.Timestamp('2021-06-06')
        dc = DailyControl(daDate, db=self.testdb)
        dc.runDialog(self.df, tradeSum = self.ts)
        dc.dropTable()
        dc.createTable()
        dc.populateNotes()
        note = '''Twas all hallow's  eve and all throug the grove
                  jabberwock trounced his thro boro-dove'''
        dc.setNote(note)
        widgnote = dc.ui.dailyNotes.toPlainText()
        self.assertTrue(not widgnote)
        dc.populateNotes()
        widgnote = dc.ui.dailyNotes.toPlainText()
        self.assertEqual(widgnote, note)

    def test_populateStuff(self):
        '''Test populateS (modelS), populateM (modelM) and the pandas modelT'''
        daDate = pd.Timestamp('2021-06-06')
        dc = DailyControl(daDate, db=self.testdb)
        dc.runDialog(self.df, tradeSum = self.ts)
        headers = ['Daily P / L Summary', 'Live Total', 'Sim Total', 'Highest Profit',
                   'Largest Loss', 'Average Win', 'Average Loss']
        for i, head in enumerate(headers):
            self.assertEqual(dc.modelS.item(i, 0).text(), head)

        headers = ['Name', 'PnL', 'Lost Plays', 'Mistake or pertinent feature of trade']
        for i, head in enumerate(headers):
            self.assertEqual(dc.modelM.item(1, i).text(), head)

        for i, head in enumerate(list(dc.modelT._df.columns)):
            self.assertEqual(head, dc.modelT.headerData(i, Qt.Horizontal))

    def test_populateM(self):
        daDate = pd.Timestamp('2021-06-06')
        dc = DailyControl(daDate, db=self.testdb)
        dc.runDialog(self.df, tradeSum = self.ts)
        headers = ['Name', 'PnL', 'Lost Plays', 'Mistake or pertinent feature of trade']
        for i, head in enumerate(headers):
            self.assertEqual(dc.modelM.item(1, i).text(), head)

def main():
    unittest.main()

def notmain():
    t = TestDailyCtrl()
    t.setUp()


if __name__ == '__main__':
    main()
    # notmain()