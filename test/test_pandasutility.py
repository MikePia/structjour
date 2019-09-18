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
Test the methods in th module journal.pandasutility
Created on Sep 9, 2018

@author: Mike Petersen
'''
from math import isclose
import unittest
import os
import random
import types

import pandas as pd

from structjour.pandasutil import InputDataFrame
from structjour.definetrades import ReqCol
from structjour.journalfiles import JournalFiles

from structjour.rtg import randomTradeGenerator2

# pylint: disable = C0103




class Test_Pandasutility(unittest.TestCase):
    '''
    Test the methods in pandasutility
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(Test_Pandasutility, self).__init__(*args, **kwargs)

        # Input test files can be added here.  Should add files that should fail in another list
        self.infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
                        'trades.8.csv', 'trades.907.WithChangingHolds.csv',
                        'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
                        'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
                        'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv',
                        'trades190221.BHoldPreExit.csv']

    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def test_ZeroPad(self):
        '''
        Test the method pandasutil.InputDataFrame.zeroPadTimeStr.
        '''

        indir = 'data/'
        for infile  in self.infiles:

            inpathfile = os.path.join(indir, infile)

            t = pd.read_csv(inpathfile)

            idf = InputDataFrame()
            t = idf.zeroPadTimeStr(t)

            for x in t['Time']:
                self.assertIsInstance(x, str, 'Excel time in {infile} is a {type(x)}')
                self.assertEqual(len(x), 8)
                self.assertEqual(x[2], ':')
                self.assertEqual(x[5], ':')
                self.assertEqual(len(x), 8)
                (h, m, s) = x.split(':')
                try:
                    h = int(h)
                    m = int(m)
                    s = int(s)
                    self.assertLess(h, 24)
                    self.assertLess(m, 60)
                    self.assertLess(s, 60)
                except NameError:
                    self.fail('Time has a wrong value')


    def test_getOvernightTrades(self):
        '''
        The only way to automate this is to just figure all the same data and compare it.
        '''

        indir = "data/"

        for infile in self.infiles:
            inpathfile = os.path.join(indir, infile)
            os.path.exists(inpathfile)

            dframe = pd.read_csv(inpathfile)

            sl = list()

            # Total up the shares found for each unique ticker/account to create our own
            # list of overnight trades (unbalanced trades are overnight) Then verify its
            # the same list as that from getOvernightTrades
            for symbol in dframe['Symb'].unique():
                # print(symbol)
                df = dframe[dframe['Symb'] == symbol]
                for account in df['Account'].unique():
                    df1 = df[df['Account'] == account]
                    buy = 0
                    for dummy, row in df1.iterrows():
                        # print(row['Side'], row['Qty'])
                        if row['Side'].startswith('S'):
                            buy = buy - row['Qty']
                        elif row['Side'].startswith('B'):
                            buy = buy + row['Qty']
                        else:
                            print('error', 'Side is ', row['Side'])
                    if buy != 0:
                        # Create the same data format used in getOvernightTrades
                        sl.append({'ticker' : symbol, 'shares': buy,
                                   'before':0, 'after': 0, 'acct': account})
            idf = InputDataFrame()
            dframe = idf.mkShortsNegative(dframe)
            st = idf.getOvernightTrades(dframe)
            self.assertEqual(len(sl), len(st))
            for trade in sl:
                self.assertTrue(trade in st)


    def test_addDateFieldx(self):
        '''
        Test the method writeShareBalance. Send some randomly generated trades side and qty and
        test the share balance that returns. Sort both and compare the results using the place
        index iloc
        '''
        NUMTRADES = 4
        start = pd.Timestamp('2018-06-06 09:30:00')
        df = pd.DataFrame()
        exclude = []
        for i in range(NUMTRADES):
            tdf, start = randomTradeGenerator2(i+1, earliest=start,
                                               pdbool=True, exclude=exclude)
            df = df.append(tdf)
            exclude.append(tdf.Symb.unique()[0])

        df.reset_index(drop=True, inplace=True)
        rc=ReqCol()

        df2 = df [[rc.time, rc.ticker, rc.side, rc.shares, rc.acct, rc.PL]].copy()
        idf = InputDataFrame()
        df2 = idf.addDateField(df2, start)

        for i in range(len(df2)):
            rprev=rnext=''
            row = df2.iloc[i]
            rprev = df2.iloc[i-1] if i != 0 else ''
            rnext = df2.iloc[i+1] if i < (len(df2)-1) else ''
            daydelt = pd.Timedelta(days=1)
            # print(row.Side, type(rprev), type(rnext))
            rt = pd.Timestamp(row.Time)
            rd = pd.Timestamp(row.Date)
            assert rt.time() == rd.time()

            if row.Side == 'HOLD-B' or row.Side == 'HOLD+B':
                assert row.Date.date() == rnext.Date.date() - daydelt
            if row.Side == 'HOLD-' or row.Side == 'HOLD+':
                assert row.Date.date() == rprev.Date.date() + daydelt

        return df2


def main():
    '''
    Test discovery is not working in vscode. Use this for debugging.
    Then run cl python -m unittest discovery
    '''
    unittest.main()
    # f = Test_Pandasutility()
    # for name in dir(f):
    #     if name.startswith('test'):
    #         attr = getattr(f, name)

    #         if isinstance(attr, types.MethodType):
    #             attr()



def notmain():
    '''Run some local code'''
    t = Test_Pandasutility()
    # t.test_GetListOfTicketDF()
    # t.walkit()
    # t.test_MkShortNegative()
    # t.testGetOvernightTrades()
    t.test_addDateFieldx()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCheckRequiredColumns']
    # unittest.main()
    notmain()
    # main()
