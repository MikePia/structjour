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
Test the methods in the module journal.definetrades

@created_on Feb 18, 2019

@author: Mike Petersen
'''
# from math import isclose
import datetime as dt
import logging
import os
# import types
import unittest
from unittest import TestCase

import numpy as np
import pandas as pd


from structjour.colz.finreqcol import FinReqCol
from structjour.definetrades import DefineTrades
from structjour.statements.dasstatement import DasStatement
from structjour.statements.ibstatement import IbStatement
from structjour.statements.ibstatementdb import StatementDB
from structjour.statements.statement import getStatementType
from structjour.stock.utilities import clearTables

from structjour.utilities.rtg import RTG

from PyQt5.QtCore import QSettings


class TestDefineTrades(TestCase):
    '''
    Run all of structjour with a collection of input files and test the outcome
    The methods called in the processDBTrades are dependent on their sequence.  The first part of the method
    is re-created in setUpClass. Then the method is redundantly recreated in each subsequent test till the
    appropriate place has been reached
    '''

    outdir = 'test/out'
    db = 'data/testdb.sqlite'

    @classmethod
    def setUpClass(cls):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))
        cls.outdir = os.path.realpath(cls.outdir)
        cls.db = os.path.realpath(cls.db)

        if os.path.exists(cls.db):
            clearTables(cls.db)

        cls.rtg = RTG(db=cls.db, overnight=100)
        cls.theDate = '20200207 10:39'
        cls.infile = cls.rtg.saveSomeTestFiles([cls.theDate], cls.outdir, strict=True, overwrite=False)[0]

        settings = QSettings('zero_substance', 'structjour')
        # for i, name in enumerate(cls.infiles):
        name = os.path.join(cls.outdir, cls.infile)
        x, cls.inputType = getStatementType(name)
        if cls.inputType == 'DAS':
            ds = DasStatement(name, settings, cls.theDate)
            ds.getTrades(testFileLoc=cls.outdir, testdb=cls.db)
        elif cls.inputType == "IB_CSV":
            ibs = IbStatement(db=cls.db)
            ibs.openIBStatement(name)
        else:
            raise ValueError(f'Unsupported File type: {cls.inputType}')

        statement = StatementDB(db=cls.db)
        cls.df = statement.getStatement(cls.theDate)
        cls.dtrades = DefineTrades(cls.inputType)
        cls.rc = FinReqCol(cls.inputType)
        cls.trades = cls.dtrades.addFinReqCol(cls.df)
        rccolumns = cls.rc.columns.copy()
        rccolumns = cls.dtrades.appendCols(rccolumns)

        cls.trades = cls.trades[rccolumns]
        cls.trades.copy()
        cls.trades = cls.trades.sort_values([cls.rc.ticker, cls.rc.acct, cls.rc.date])

    def test_addFinReqCol(self):
        '''
        Test the method journal.definetrades.TestDefineTrades.addFinReqCol
        '''
        rc = self.rc
        frc = FinReqCol()

        df = pd.DataFrame(np.random.randint(0, 1000, size=(10, len(rc.columns))),
                          columns=rc.columns)
        dtrades = DefineTrades()
        df = dtrades.addFinReqCol(df)
        for x in frc.columns:
            self.assertIn(x, df.columns)
        self.assertGreaterEqual(len(df.columns), len(frc.columns))

    def test_addStartTimeDB(self):
        '''
        Test the method DefineTrades.addStartTime. Send some randomly generated trades excluding
        the start field and then test the results for the start field.
        '''
        nt = self.trades.copy()
        nt = self.dtrades.addStartTimeDB(nt)
        for i, row in nt.iterrows():
            start = row['Start']
            self.assertEqual(len(start), 8)
            x = pd.Timestamp(start).time()
            self.assertIsInstance(x, dt.time)

    def test_addTradeIndex(self):
        '''
        Test addTradeIndex. Test that the index is properly formed, balance is only (possibly) 0 on
        the last transaction in the trade and the Times are in the right sequence
        '''
        rc = self.rc
        nt = self.trades.copy()
        nt = self.dtrades.addStartTimeDB(nt)
        nt = nt.sort_values([rc.start, rc.ticker, rc.acct, rc.date, rc.time], ascending=True)
        nt = self.dtrades.addTradeIndex(nt)

        lastd = None
        for i, tindex in enumerate(list(nt['Tindex'].unique())):
            tnum = 'Trade ' + str(i + 1)
            tdf = nt[nt.Tindex == tnum].copy()
            xl = tdf.index[-1]
            lasttime = None
            for j, row in tdf.iterrows():

                if j != xl:
                    self.assertNotEqual(tdf.at[j, 'Balance'], 0)

                if lasttime:
                    self.assertEqual(row['Start'], lasttime)
                lasttime = row['Start']
            if lastd:
                self.assertGreater(tdf['Start'].unique()[0], lastd)
            lastd = tdf['Start'].unique()[0]

    def test_addTradePL(self):
        '''
        Test the method DefineTrades.addTradePL. The method creates a summary pl for each trade
        Check the summary PL for each trade and that the summary pl is placed only in the
        last transaction of each trade.
        '''
        rc = self.rc
        nt = self.trades.copy()
        nt = self.dtrades.addStartTimeDB(nt)
        nt = nt.sort_values([rc.start, rc.ticker, rc.acct, rc.date, rc.time], ascending=True)
        nt = self.dtrades.addTradeIndex(nt)
        nt = self.dtrades.addTradePL(nt)

        for i, tindex in enumerate(list(nt['Tindex'].unique())):
            tdf = nt[nt.Tindex == tindex]
            daSum = tdf[rc.PL].sum()
            daSum2 = tdf.loc[tdf.index[-1]][rc.sum]
            self.assertAlmostEqual(daSum, daSum2, 5, 'The pl summary amount is not equal to the pnl summary')

    def test_addTradeDurationDB(self):
        '''
        Test that Duration val is placed only in the last transaction
        Test Duration is difference from each Last Trade - Start val
        '''
        rc = self.rc
        nt = self.trades.copy()
        nt = self.dtrades.addStartTimeDB(nt)
        nt = nt.sort_values([rc.start, rc.ticker, rc.acct, rc.date, rc.time], ascending=True)
        nt = self.dtrades.addTradeIndex(nt)
        nt = self.dtrades.addTradePL(nt)
        nt = self.dtrades.addTradeDurationDB(nt)
        for i, tindex in enumerate(list(nt['Tindex'].unique())):
            tdf = nt[nt.Tindex == tindex]
            for i, row in tdf.iterrows():
                if i != tdf.index[-1]:
                    itsnothing = row[rc.dur]
                    self.assertTrue(itsnothing == '' or itsnothing is None)
                else:
                    theDur = pd.Timestamp(row[rc.time]) - pd.Timestamp(row[rc.start])
                    self.assertEqual(row[rc.dur], theDur, f'The duration is incorrect for {tindex}: {row[rc.ticker]}')

    def test_addTradeNameDB(self):
        '''
        Test the name is created correctly. Note that flipped trades are figured after addTradeName and,
        if found, the trade name is updated. This tests only the last transaction, as does addTradeName
        '''
        rc = self.rc
        nt = self.trades.copy()
        nt = self.dtrades.addStartTimeDB(nt)
        nt = nt.sort_values([rc.start, rc.ticker, rc.acct, rc.date, rc.time], ascending=True)
        nt = self.dtrades.addTradeIndex(nt)
        nt = self.dtrades.addTradePL(nt)
        nt = self.dtrades.addTradeDurationDB(nt)
        nt = self.dtrades.addTradeNameDB(nt)
        for i, tindex in enumerate(list(nt['Tindex'].unique())):
            tdf = nt[nt.Tindex == tindex]
            long = None
            for i, row in tdf.iterrows():
                if i != tdf.index[-1]:
                    self.assertTrue(row[rc.name] == '' or row[rc.name] is None)
                else:
                    long = 'long' if (row[rc.oc].find('O') >= 0 and row[rc.shares] > 0) or (
                                      row[rc.oc].find('C') >= 0 and row[rc.shares] < 0) else 'short'
                    self.assertEqual(long.lower(), row[rc.name].split(' ')[-1].lower())
            print(tdf[rc.name].unique())

    def test_postProcessingDB(self):
        '''
        Test add Overnight and/or Flipped to name if it is called for.
        Test fix db relation for tsid
        '''
        rc = self.rc
        nt = self.trades.copy()
        nt = self.dtrades.addStartTimeDB(nt)
        nt = nt.sort_values([rc.start, rc.ticker, rc.acct, rc.date, rc.time], ascending=True)
        nt = self.dtrades.addTradeIndex(nt)
        nt = self.dtrades.addTradePL(nt)
        nt = self.dtrades.addTradeDurationDB(nt)
        nt = self.dtrades.addTradeNameDB(nt)
        ldf, nt = self.dtrades.postProcessingDB(self.dtrades.getTradeList(nt))
        for i, tindex in enumerate(list(nt['Tindex'].unique())):
            tdf = nt[nt.Tindex == tindex]
            if not tdf[rc.oc].unique()[0] or tdf[rc.oc].unique()[0] == '':
                logging.error(f'Bad Trade:{self.db}: {self.theDate} {tdf[rc.ticker].unique()[0]}')
                continue
            x0 = tdf.index[0]
            xl = tdf.index[-1]
            blong = True if (tdf.loc[x0][rc.oc].find('O') >= 0 and tdf.loc[x0][rc.shares] > 0) or (
                             tdf.loc[x0][rc.oc].find('C') >= 0 and tdf.loc[x0][rc.shares] < 0) else False

            for i, row in tdf.iterrows():
                if (blong is True and row[rc.bal] < 0) or (blong is not True and row[rc.bal] > 0):
                    self.assertGreaterEqual(tdf.loc[xl][rc.name].lower().find('flipped'), 0)
                    break

    # def test_fixTsid(self):
    #     pass


def notmain():
    '''Run some local code'''
    # for i in range(3):
    TestDefineTrades.setUpClass()
    t = TestDefineTrades()
    t.test_addFinReqCol()
    t.test_addStartTimeDB()
    t.test_addTradeIndex()
    t.test_addTradePL()
    t.test_addTradeDurationDB()
    t.test_addTradeNameDB()
    t.test_postProcessingDB()
    # t.test_addSummaryPL()

    # t.test_addSummaryPL()


def main():
    unittest.main()


if __name__ == '__main__':
    # main()
    notmain()
