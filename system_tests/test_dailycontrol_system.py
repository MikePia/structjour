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
from unittest import TestCase

import pandas as pd
import sqlite3


# https://stackoverflow.com/questions/57426219/how-to-import-qtwebenginewidgets-after-qapplication-has-been-created
# thanks to ekhumoro.
# Strangely the import error occurs using (before installing webengine_hack here):
# python -m unittest discover
# But not when using from the test directory:
# python -m unittest test_dailycontrol
# or any other local run
# def webengine_hack():
#     from PyQt5 import QtWidgets
#     app = QtWidgets.QApplication.instance()
#     if app is not None:
#         import sip
#         app.quit()
#         sip.delete(app)
#     import sys
#     from PyQt5 import QtCore, QtWebEngineWidgets
#     QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
#     app = QtWidgets.qApp = QtWidgets.QApplication(sys.argv)
#     return app


# try:
#     # just for testing
#     from PyQt5 import QtWidgets
#     app = QtWidgets.QApplication([''])
#     from PyQt5 import QtWebEngineWidgets
# except ImportError as exception:
#     logging.info(exception)
#     logging.info('\nRetrying webengine import...')
#     app = webengine_hack()
#     from PyQt5 import QtWebEngineWidgets

# from PyQt5 import QtCore, QtWebEngineWidgets
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QApplication

# from PyQt5.QtTest import QTest
from structjour.view.dailycontrol import DailyControl
from structjour.journalfiles import JournalFiles
from structjour.definetrades import DefineTrades

from structjour.statements.ibstatementdb import StatementDB
from structjour.statements.ibstatement import IbStatement

from structjour.view.layoutforms import LayoutForms
from structjour.view.sumcontrol import SumControl

app = QApplication(sys.argv)


class TestDailyCtrl(TestCase):
    '''Test sytem interaction.'''

    def __init__(self, *args, **kwargs):
        super(TestDailyCtrl, self).__init__(*args, **kwargs)

        self.testdb = 'test/testdb.sqlite'
        self.apiset = QSettings('zero_substance/stockapi', 'structjour')
        self.realdb = self.apiset.value('dbsqlite')

        # Test file has one month of trades including some on theDate
        self.f1 = 'flex.369463.ActivityFlexMonth.20191008.20191106.csv'
        self.theDate = pd.Timestamp('2019-10-16')

    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))
        self.conn = sqlite3.connect(self.testdb)
        self.inputtype = 'IB_CSV'

        indir = 'data/'
        # f2 = 'ActivityStatement.20190313_PL.html'

        jf = JournalFiles(indir=indir, infile=self.f1, theDate=self.theDate, inputType='IB_CSV', mydevel=False)

        jf.inputType = 'IB_CSV'
        # statement = Statement_IBActivity(jf)
        # df = statement.getTrades_IBActivity(jf.inpathfile)

        ibs = IbStatement(db=self.testdb)
        ibdb = StatementDB(self.testdb)
        ibdb.reinitializeTradeTables()
        ibs.openIBStatementCSV(jf.inpathfile)
        df2 = ibdb.getStatement(self.theDate)
        if df2.empty:
            sdate = self.theDate.strftime('%Y-%m-%d')
            msg = f'In test_dailycontrol.setup: Error: found no trades in db for {sdate}'
            self.assertTrue(not df2.empty, msg)

        tu = DefineTrades(jf.inputType)
        self.df, ldf = tu.processDBTrades(df2)
        sc = SumControl()
        lf = LayoutForms(sc, jf, self.df)
        lf.runTtoSummaries(ldf)
        self.ts = lf.ts
        ibdb.addTradeSummaries(self.ts, ldf)

    def tearDown(self):
        # just in case the testdb was written to settings
        self.apiset.setValue('dbsqlite', self.realdb)

    def test_populateStuff(self):
        '''Test the headers for populateS (modelS), populateM (modelM) and the pandas modelT after runDialog'''
        # daDate = pd.Timestamp('2021-06-06')
        dc = DailyControl(self.theDate, db=self.testdb)
        dc.runDialog(self.df, tradeSum=self.ts)
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
        dc = DailyControl(self.theDate, db=self.testdb)
        dc.runDialog(self.df, tradeSum=self.ts)
        headers = ['Name', 'PnL', 'Lost Plays', 'Mistake or pertinent feature of trade']
        for i, head in enumerate(headers):
            self.assertEqual(dc.modelM.item(1, i).text(), head)


def main():
    unittest.main()


def notmain_helper(t, method, count):
    t.setUp()
    method()
    t.tearDown()
    return count + 1


def notmain():

    t = TestDailyCtrl()
    count = notmain_helper(t, t.test_populateStuff, 0)

    t = TestDailyCtrl()
    count = notmain_helper(t, t.test_populateM, count)


if __name__ == '__main__':
    notmain()
    # main()
