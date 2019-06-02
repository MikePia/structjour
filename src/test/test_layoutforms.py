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

from collections import deque
import os
import random
import sys


from  unittest import TestCase
import unittest

from openpyxl import Workbook, load_workbook
import pandas as pd

from journal.view.layoutforms import LayoutForms
from journal.view.sumcontrol import SumControl
from journalfiles import JournalFiles
from test.rtg import getRandGenTradeStuff, getRandomFuture

from PyQt5.QtWidgets import QApplication


app = QApplication(sys.argv)

class Test_LayoutForms_ts_data(TestCase):
    '''
    Test the ExportToExcel Object. Generally use this class for less elaborate setups and
    Test_ExportToExcel_MistakeData for more elaborate setups (Hyperinks and stuff requiring
    coordinated data)
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(Test_LayoutForms_ts_data, self).__init__(*args, **kwargs)
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))
    
    def setUp(self):
        theDate = pd.Timestamp('2008-06-06')
        jf = JournalFiles(outdir='out/', theDate=theDate, mydevel=False)
        tradeS, ts, entries, imageNames, df, ldf = getRandGenTradeStuff()



        sc = SumControl()
        theDate = pd.Timestamp('2008-06-06')
        jf = JournalFiles(outdir='out/', theDate=theDate, mydevel=False)
        self.lf = LayoutForms(sc, jf, df)
        self.lf.ts = ts
        self.lf.entries = entries


    def test_setChartData(self):
        # [start, end, interval, name]
        d1 = getRandomFuture()
        starts = deque()
        interval = 0
        name = 'thecharttoendallchart'
        data = list()
        for i in range(len(self.lf.ts)):
            for i in range(0, 6):
                starts.append(getRandomFuture(d1))
                d1 = starts[-1]
            interval = random.randint(0,60)
            namex = name + str(i)
            data.append([namex, starts.popleft(), starts.popleft(), interval])
            data.append([namex, starts.popleft(), starts.popleft(), interval])
            data.append([namex, starts.popleft(), starts.popleft(), interval])

        for i, key in enumerate(self.lf.ts):
            for chart in ['chart1', 'chart2', 'chart3']:
                self.lf.setChartData(key, data[i], chart)
                d = self.lf.getChartData(key, chart)
                self.assertEqual(d[0], data[i][0])
                self.assertEqual(pd.Timestamp(d[1]), pd.Timestamp(data[i][1]))
                self.assertEqual(pd.Timestamp(d[2]), pd.Timestamp(data[i][2]))
                self.assertEqual(d[3], data[i][3])
            
    def test_getEntries(self):
        '''test getEntries. Specifically test there is key for entries for every tradekey. '''
        for key in self.lf.ts:
            self.assertIn(key, self.lf.entries.keys())
            e = self.lf.getEntries(key)
            self.assertIsNotNone(e)

    def test_setClean(self):
        for key in self.lf.ts:
            self.lf.setClean(key, True)
            self.assertTrue(self.lf.ts[key]['clean'].unique()[0])

    def test_setExplain(self):
        for i, key in enumerate(self.lf.ts):
            note = f'''
I really dont mind if you sit this one out. My word's
but a whisper, your deafness a shout! {(i+1) * 5} times!!!
'''
            # print(note)
            self.lf.setExplain(key, note)
            notex = (self.lf.ts[key]['Explain'].unique()[0])
            self.assertEqual(note, notex)
    
    def test_setMstkVals(self):
        val = 33.33
        for i, key in enumerate(self.lf.ts):
            note = f'''
We'll make a man of him
Put him to a trade
Teach him to play Monopoly
Not to sing in the rain {(i+1) * 5} times!!!
'''
            # print(note)
            val = val + i*34.12
                      
            self.lf.setMstkVals(key, val, note)
            valx = (self.lf.ts[key]['MstkVal'].unique()[0])
            notex = (self.lf.ts[key]['MstkNote'].unique()[0])
            self.assertEqual(val, valx)
            self.assertEqual(note, notex)

    def test_setNotes(self):
        for i, key in enumerate(self.lf.ts):
            note = f'''
We will be geared to the average rather than the exceptional
God is an overwhelming responsibility! {(i+1) * 5} times.
'''
            # print(note)
            self.lf.setNotes(key, note)
            notex = (self.lf.ts[key]['Notes'].unique()[0])
            self.assertEqual(note, notex)

    def test_setStopVals(self):
        #  key, stop, diff, rr, maxloss
        stop = 33.33
        diff = .43
        rr = '3 / 1'
        maxloss = -1.80
        for i, key in enumerate(self.lf.ts):

            self.lf.setStopVals(key, stop, diff, rr, maxloss)
            self.assertEqual(stop, self.lf.ts[key]['StopLoss'].unique()[0])
            self.assertEqual(diff, self.lf.ts[key]['SLDiff'].unique()[0])
            self.assertEqual(rr, self.lf.ts[key]['RR'].unique()[0])
            self.assertEqual(maxloss, self.lf.ts[key]['MaxLoss'].unique()[0])
            stop = stop - (i * 10.48)
            diff = diff - (i * i * .2)
            maxloss = maxloss - ((i+1) * 30.89)

        def test_setStrategy(self):
            for i, key in enumerate(self.lf.ts):
                strat = f'sell for {i + 2} times the purchasce price.'
                self.lf.setStrategy(key, strat)
                stratx = self.lf.getStrategy(key)
                self.assertEqual(strat, stratx)

    def test_setTargVals(self):
        # key, targ, diff, rr
        targ = 33.33
        diff = .43
        rr = '3 / 1'
        for i, key in enumerate(self.lf.ts):

            self.lf.setTargVals(key, targ, diff, rr)
            self.assertEqual(targ, self.lf.ts[key]['Target'].unique()[0])
            self.assertEqual(diff, self.lf.ts[key]['TargDiff'].unique()[0])
            self.assertEqual(rr, self.lf.ts[key]['RR'].unique()[0])
            targ = targ + (i * 10.48)
            diff = diff + (i * i * .2)





def main():
    unittest.main()

if __name__ == '__main__':
    main()
