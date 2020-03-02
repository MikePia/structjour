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
Test the methods in the layoutforms module. Seperate tests into 2 classes, One to test the storage
and retrieval of trade info using self.ts, the other for everything else.

Created on June 1, 2019

@author: Mike Petersen
'''
import sqlite3
import sys
from PyQt5 import QtCore
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
from PyQt5 import QtWebEngineWidgets    # noqa:  F401
from PyQt5 import QtWidgets

from collections import deque
# import datetime as dt
import os
import pandas as pd
import random

import unittest

from PyQt5.QtCore import QSettings

from structjour.definetrades import DefineTrades
# from structjour.thetradeobject import TheTradeObject, SumReqFields
from structjour.statements.dasstatement import DasStatement
from structjour.statements.ibstatement import IbStatement
from structjour.statements.ibstatementdb import StatementDB
from structjour.statements.statement import getStatementType
from structjour.stock.utilities import clearTables
from structjour.view.layoutforms import LayoutForms
from structjour.view.sumcontrol import SumControl
from structjour.journalfiles import JournalFiles
from structjour.rtg import RTG

# from PyQt5.QtWidgets import QApplication

app = QtWidgets.qApp = QtWidgets.QApplication(sys.argv)


class Test_LayoutForms(unittest.TestCase):
    '''
    Test the methods that are not related to storing to self.ts but are dependent on it
    '''
    infiles = []
    dates = []
    rtg = None
    lfs = []
    db = ''
    outdir = ''
    sc = None

    @classmethod
    def setUpClass(cls):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

        outdir = 'test/out'
        cls.outdir = os.path.realpath(outdir)
        cls.db = 'data/testdb.sqlite'
        cls.db = os.path.realpath(cls.db)
        if os.path.exists(cls.db):
            clearTables(cls.db)

        cls.rtg = RTG(db=cls.db)
        # cls.dates = ['20200203 09:30', '20200204 07:30', '20200205 09:35', '20200206 11:40', '20200207 10:39']
        cls.dates = ['20200207 10:39']
        cls.infiles = cls.rtg.saveSomeTestFiles(cls.dates, cls.outdir)

        settings = QSettings('zero_substance', 'structjour')
        for i, name in enumerate(cls.infiles):
            name = os.path.join(cls.outdir, name)
            x, cls.inputType = getStatementType(name)
            # print(cls.inputType)
            if cls.inputType == 'DAS':
                ds = DasStatement(name, settings, cls.dates[i])
                ds.getTrades(testFileLoc=cls.outdir, testdb=cls.db)
            elif cls.inputType == "IB_CSV":
                ibs = IbStatement(db=cls.db)
                ibs.openIBStatement(name)
            else:
                continue
            #     self.assertTrue(4 == 5, "Unsupported file type in test_TheTradeObject")

            statement = StatementDB(db=cls.db)
            df = statement.getStatement(cls.dates[i])
            # self.assertFalse(df.empty, f"Found no trades in db on {daDate}")
            dtrade = DefineTrades(cls.inputType)
            dframe, ldf = dtrade.processDBTrades(df)
            # tto = TheTradeObject(ldf[0], False, SumReqFields())
            jf = JournalFiles(indir=cls.outdir, outdir=outdir, theDate=cls.dates[i], infile=name)
            cls.sc = SumControl()
            lf = LayoutForms(cls.sc, jf, dframe)
            lf.runTtoSummaries(ldf)
            # cls.jfs.append(jf)
            # cls.dframes.append(dframe)
            # cls.ttos.append(tto)
            # cls.ldfs.append(ldf)
            cls.lfs.append(lf)
        # rw = runController(w)

    def setUp(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def test_getImageName(self):
        '''
        Create a name for a pasted image. Asserts that all the right parts are in the
        expected places.
        '''
        # for infile, date, ldf, tto, dframe, jf in zip(self.infiles, self.dates, self.ldfs, self.ttos, self.dframes, self.jfs):
        for infile, date, lf in zip(self.infiles, self.dates, self.lfs):
            for key in lf.ts.keys():
                for i in range(1, 4):
                    ckey = 'chart' + str(i)
                    name = f"{'Trade'}{'_'.join(key.split(' '))}"
                    x1 = lf.getImageName(key, ckey)
                    self.assertTrue(x1.startswith(name))
                    self.assertTrue(x1.endswith(ckey + '.png'))

    def test_getImageNameX(self):
        for infile, date, lf in zip(self.infiles, self.dates, self.lfs):
            for key in lf.ts.keys():
                for i in range(1, 4):
                    ckey = 'chart' + str(i)
                    x1 = lf.getImageNameX(key, ckey)
                    name = f"{'Trade'}{'_'.join(key.split(' '))}"
                    self.assertTrue(x1.startswith(name))
                    self.assertTrue(x1.endswith('min.png'))

    def test_populateTradeSumForms(self):
        '''
        It is overwheleming to try to test that sumform was set correctly. This token
        tests the name was set correctly
        '''
        for lf in self.lfs:
            for key in lf.ts.keys():
                lf.populateTradeSumForms(key)
                self.assertEqual(lf.wd['Name'].text(), key[key.find(' ') + 1:])

    def test_setChartData(self):
        for lf in self.lfs:
            d1 = self.rtg.getRandomFuture()
            starts = deque()
            interval = 0
            name = 'thecharttoendallchart'
            data = list()
            for i in range(len(lf.ts)):
                for i in range(0, 6):
                    starts.append(self.rtg.getRandomFuture(d1))
                    d1 = starts[-1]
                interval = random.randint(0, 60)
                namex = name + str(i)
                data.append([namex, starts.popleft(), starts.popleft(), interval])
                data.append([namex, starts.popleft(), starts.popleft(), interval])
                data.append([namex, starts.popleft(), starts.popleft(), interval])

            for i, key in enumerate(lf.ts.keys()):
                for chart in ['chart1', 'chart2', 'chart3']:
                    lf.setChartData(key, data[i], chart)
                    d = lf.getChartData(key, chart)
                    self.assertEqual(d[0], data[i][0])
                    self.assertEqual(pd.Timestamp(d[1]), pd.Timestamp(data[i][1]))
                    self.assertEqual(pd.Timestamp(d[2]), pd.Timestamp(data[i][2]))
                    self.assertEqual(d[3], data[i][3])

    def test_setStopVals(self):
        #  key, stop, diff, rr, maxloss
        stop = 33.33
        diff = .43
        rr = '3 / 1'
        maxloss = -1.80
        lf = self.lfs[0]
        for i, key in enumerate(lf.ts):

            lf.setStopVals(key, stop, diff, rr, maxloss)
            self.assertEqual(stop, lf.ts[key]['StopLoss'].unique()[0])
            self.assertEqual(diff, lf.ts[key]['SLDiff'].unique()[0])
            self.assertEqual(rr, lf.ts[key]['RR'].unique()[0])
            self.assertEqual(maxloss, lf.ts[key]['MaxLoss'].unique()[0])
            stop = stop - (i * 10.48)
            diff = diff - (i * i * .2)
            maxloss = maxloss - ((i + 1) * 30.89)

    def test_setTargVals(self):
        # key, targ, diff, rr
        targ = 33.33
        diff = .43
        rr = '3 / 1'
        lf = self.lfs[0]
        for i, key in enumerate(lf.ts):

            lf.setTargVals(key, targ, diff, rr)
            self.assertEqual(targ, lf.ts[key]['Target'].unique()[0])
            self.assertEqual(diff, lf.ts[key]['TargDiff'].unique()[0])
            self.assertEqual(rr, lf.ts[key]['RR'].unique()[0])
            targ = targ + (i * 10.48)
            diff = diff + (i * i * .2)

    def test_getEntries(self):
        for lf in self.lfs:
            for key in lf.ts.keys():
                self.assertIn(key, lf.entries.keys())
                e = lf.getEntries(key)
                self.assertIsNotNone(e)

    def test_setClean(self):
        for lf in self.lfs:
            for key in lf.ts.keys():
                lf.setClean(key, True)
                self.assertTrue(lf.ts[key]['clean'].unique()[0])

    def test_setExplain(self):
        lf = self.lfs[0]

        for i, key in enumerate(lf.ts):
            note = f'''
I really dont mind if you sit this one out. My word's
but a whisper, your deafness a shout! {(i+1) * 5} times!!!
'''
            self.lfs[0].setExplain(key, note)
            notex = (lf.ts[key]['Explain'].unique()[0])
            self.assertEqual(note, notex)

    def test_setMstkVals(self):
        lf = self.lfs[0]
        val = 33.33
        for i, key in enumerate(lf.ts):
            note = f'''
We'll make a man of him
Put him to a trade
Teach him to play Monopoly
Not to sing in the rain {(i+1) * 5} times!!!
'''
            val = val + i * 34.12

            lf.setMstkVals(key, val, note)
            valx = (lf.ts[key]['MstkVal'].unique()[0])
            notex = (lf.ts[key]['MstkNote'].unique()[0])
            self.assertEqual(val, valx)
            self.assertEqual(note, notex)

    def test_setNotes(self):
        lf = self.lfs[0]
        for i, key in enumerate(lf.ts):
            note = f'''
We will be geared to the average rather than the exceptional
God is an overwhelming responsibility! {(i+1) * 5} times.
'''
            lf.setNotes(key, note)
            notex = (lf.ts[key]['Notes'].unique()[0])
            self.assertEqual(note, notex)

    def test_setStrategy(self):
        lf = self.lfs[0]
        for i, key in enumerate(lf.ts):
            strat = f'sell for {i + 2} times the purchasce price.'
            lf.setStrategy(key, strat)
            stratx = lf.getStrategy(key)
            self.assertEqual(strat, stratx)


def notmain():
    # outfile = import(7, start='20200202', outfile=outfile, strict=True)
    Test_LayoutForms.setUpClass()
    t = Test_LayoutForms()
    t.setUp()
    # t.test_getImageNameX()
    # t.test_populateTradeSumForms()
    # t.test_setChartData()
    # t.test_getEntries()
    # t.test_setClean()
    # t.test_setExplain()
    # t.test_setMstkVals()
    # t.test_setNotes()
    # t.test_setStrategy()
    t.test_setStopVals()
    t.test_setTargVals()


def main():
    unittest.main()


if __name__ == '__main__':
    # notmain()
    main()
