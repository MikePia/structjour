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
import datetime as dt
import os
import random
import sys


from  unittest import TestCase
import unittest

from openpyxl import Workbook, load_workbook
import pandas as pd

from journal.view.layoutforms import LayoutForms
from journal.view.sumcontrol import SumControl
from journal.journalfiles import JournalFiles
from test.rtg import getRandGenTradeStuff, getRandomFuture, getLdf

from PyQt5.QtWidgets import QApplication


app = QApplication(sys.argv)

class Test_LayoutForms(TestCase):
    '''
    Test the methods that are not related to storing to self.ts
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(Test_LayoutForms, self).__init__(*args, **kwargs)
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))


    def setUp(self):
        theDate = pd.Timestamp('2008-06-06')
        self.jf = JournalFiles(outdir='out/', theDate=theDate, mydevel=False)
        tradeS, ts, entries, imageNames, df, ldf = getRandGenTradeStuff()
        # ldf, df = getLdf()



        sc = SumControl()
        theDate = pd.Timestamp('2008-06-06')
        # jf = JournalFiles(outdir='out/', theDate=theDate, mydevel=False)
        self.lf = LayoutForms(sc, self.jf, df)
        self.lf.ts = ts
        self.lf.entries = entries

    def test_getImageName(self):
        '''
        Create a name for a pasted image. Asserts that all the right parts are in the
        expected places.
        '''
        print(self.lf.ts.keys())
        for key in self.lf.ts:
            n = self.lf.getImageName(key, 'chart1')
            # print (n)
            tindex, symb, side, start, numday, x, end, widg = n.split('_');
            start = pd.Timestamp('20190101 ' + start).time()
            numday = int(numday)
            end = pd.Timestamp('20190101 ' + end).time()

            self.assertTrue(tindex.startswith('Trade'))
            self.assertTrue(key.find(symb) >  0)
            self.assertTrue(side in ['Long', 'Short'])
            self.assertIsInstance(start, dt.time)

            self.assertIsInstance(numday, int)
            self.assertIsInstance(end, dt.time)
            self.assertIn('chart1', widg)




    def test_getImageNameX(self):
        '''Create a name for an API retrieved chart. lf.getChartData uses self.ts[key]'''
        print(self.lf.ts.keys())
        for key in self.lf.ts:
            n = self.lf.getImageNameX(key, 'chart1')
            tindex, symb, side, start, numday, x, end, interval = n.split('_')

            print (n)
            
            start = pd.Timestamp('20190101 ' + start).time()
            numday = int(numday)
            end = end.replace('.', '')
            end = pd.Timestamp('20190101 ' + end).time()
            interval = interval.split('.')[0]

            self.assertTrue(tindex.startswith('Trade'))
            self.assertTrue(key.find(symb) >  0)
            self.assertTrue(side in ['Long', 'Short'])
            self.assertIsInstance(start, dt.time)

            self.assertIsInstance(numday, int)
            self.assertIsInstance(end, dt.time)
            # self.assertIn('chart1', widg)
        pass


    def test_loadSavedFile(self):
        '''TODO: Place all this default/static in filesettings and simplify this to a single setting
            {sc.getOutdir}.{sc.ui.infileEdit.text().zst}
            (static: settings-outdir
            default: getDirectory()/out/)
        '''
        name = self.lf.sc.getSaveName()
        print()
        pass
    def test_populateTradeSumForms(self):
        '''Populates the sc widgets. Depends on self.ts, sc'''
        pass


    def test_toggleTimeFormat(self):
        '''Used by sc to toggle the time with date and time in trade summary entries widgets
        (called from sc). Values from self.ts are reformatted into widgets. 
        Depends on sc and self.ts'''
        pass

    
    def test_runTtoSummaries(self):
        '''Nearly top level script called from runtrade.runnit-- fefactored most of it -- moved
        Creates TradeSummaries which will become self.ts dict.'''
        pass

    def test_getStoredTradeName(self):
        '''The name for the pickled DataFrame for the active statement. {outdir}/.{infile}.zst
        Depends on self.jf for theDate and dayformat'''
        pass

    def test_pickleitnow(self):
        '''Called when loading from input file, store the DataFrame object. Depends on the processed
        input df'''
        pass
    def test_saveTheTradeObject(self):
        '''
                self.ts
        self.entries
        settings: stored_trades for default DataFrame
            self.df for other DataFrame
        '''
        pass






class Test_LayoutForms_ts_data(TestCase):
    '''
    Test the methods that save to self.ts in LayoutForms
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
