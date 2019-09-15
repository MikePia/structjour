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
from math import isclose
import os
import random
import types
from unittest import TestCase

import numpy as np
import pandas as pd

from structjour.dfutil import DataFrameUtil
from structjour.colz.finreqcol import FinReqCol
from structjour.definetrades import DefineTrades, ReqCol

from structjour.rtg import randomTradeGenerator2, floatValue

# pylint: disable = C0103



class TestDefineTrades(TestCase):
    '''
    Run all of structjour with a collection of input files and test the outcome
    '''

    def __init__(self, *args, **kwargs):
        super(TestDefineTrades, self).__init__(*args, **kwargs)

    def setUp(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))

    def test_addFinReqCol(self):
        '''
        Test the method journal.definetrades.TestDefineTrades.addFinReqCol
        '''
        rc = ReqCol()
        frc = FinReqCol()

        df = pd.DataFrame(np.random.randint(0, 1000, size=(10, len(rc.columns))),
                          columns=rc.columns)
        dtrades = DefineTrades()
        df = dtrades.addFinReqCol(df)
        for x in frc.columns:
            self.assertIn(x, df.columns)
        self.assertGreaterEqual(len(df.columns), len(frc.columns))

    def test_writeShareBalance(self):
        '''
        Test the method writeShareBalance. Send some randomly generated trades. Remove a bunch of
        columns and call writeShareBalance. Test that the share balance was recreated correctly
        test the share balance that returns. Sort both and compare the results using the place
        index iloc
        '''
        NUMTRADES = 4
        trades = list()
        start = pd.Timestamp('2018-06-06 09:30:00')
        df = pd.DataFrame()
        exclude = []
        for i in range(NUMTRADES):
            tdf, start = randomTradeGenerator2(i+1, earliest=start,
                                                pdbool=True, exclude=exclude)
            df = df.append(tdf)
            exclude.append(tdf.Symb.unique()[0])

        df.reset_index(drop=True, inplace=True)

        frc = FinReqCol()
        df2 = df.copy()

        df2[frc.sum] = None
        df2[frc.start] = None
        df2[frc.tix] = None
        df2[frc.PL] = None
        df2[frc.dur] = None
        df2[frc.bal] = 0

        df3 = df2.copy()
        df3 = df3.sort_values(['Symb', 'Account', 'Time'])
        df3.reset_index(drop=True, inplace=True)
        df = df.sort_values(['Symb', 'Account', 'Time'])

        dtrades = DefineTrades()
        df3 = dtrades.writeShareBalance(df3)
        for i in range(len(df3)):
            assert df3.iloc[i][frc.bal] == df.iloc[i][frc.bal]
            # print('{:-20}     {}'.format(df3.iloc[i][frc.bal], df.iloc[i][frc.bal]))


    def test_addStartTime(self):
        '''
        Test the method DefineTrades.addStartTime. Send some randomly generated trades excluding
        the start field and then test the results for the start field.
        '''
        NUMTRADES = 4   
        trades = list()
        start = pd.Timestamp('2019-01-01 09:30:00')
        df = pd.DataFrame()
        exclude = []
        for i in range(NUMTRADES):
            tdf, start = randomTradeGenerator2(i+1, earliest=start,
                                                pdbool=True, exclude=exclude)
            df = df.append(tdf)
            exclude.append(tdf.Symb.unique()[0])

        df.reset_index(drop=True, inplace=True)

        frc = FinReqCol()
        # df = pd.DataFrame(data=trades, columns=[frc.tix, frc.start, frc.time, frc.ticker, frc.side, frc.shares,
        #                                         frc.bal, frc.acct, frc.PL, frc.sum, frc.dur])
        df2 = df.copy()
        df2[frc.start] = None
        
        dtrades = DefineTrades()
        df3 = df2.copy()
        df3.sort_values(['Symb', 'Account', 'Time'], inplace=True)
        df3 = dtrades.addStartTime(df3)
        for i in range(len(df3)):
            # Tests that addtradeIndex recreated the same index locations that rtg did after sorting the trades
            if df3.loc[i][frc.start] != df.loc[i][frc.start]:
                print ('Found and error at index', i)
                print(df3.loc[i][frc.start], df.loc[i][frc.start])
            self.assertEqual(df3.loc[i][frc.start], df.loc[i][frc.start])
        for i in range(NUMTRADES):
            # Test all trades have a single start time
            tradeNum = 'Trade ' + str(i+1)
            tdf = df3[df3.Tindex == tradeNum].copy()
            self.assertEqual(len(tdf.Start.unique()), 1)


    def test_addTradeIndex(self):
        '''
        Test addTradeIndex
        '''
        NUMRUNS = 10
        NUMTRADES = 10 # Number of trades to aggregate into single statement
        for i in range(NUMRUNS):
            # if not i % 20:
            #     print(f'{i}/{NUMRUNS} ', end='')
            earliest = pd.Timestamp('2018-06-06 09:30:00')
            delt = pd.Timedelta(minutes=1)
            df = pd.DataFrame()
            exclude = []
            for j in range(NUMTRADES):
                tdf, earliest = randomTradeGenerator2(j+1, earliest=earliest,
                                                    pdbool=True, exclude=exclude)
                exclude.append(tdf.iloc[0].Symb)
                df = df.append(tdf)
                earliest = earliest + delt


                df.reset_index(drop=True, inplace=True)
                df = df.sort_values(['Symb', 'Account', 'Time'])
            frc = FinReqCol()
            df2 = df.copy()
            df2[frc.tix] = ''
            df2.sort_values(['Symb', 'Account', 'Time'], inplace=True)

            dtrades = DefineTrades()
            ddf = dtrades.addTradeIndex(df2)

            for k in range(4):
                tnum = 'Trade ' + str(k+1)
                tdf = ddf[ddf.Tindex == tnum].copy()
                xl = tdf.index[-1]
                lastd = None
                thisd = None
                for j, row in tdf.iterrows():
                    if j != xl:
                        if tdf.at[j, 'Balance'] == 0:
                            print('Found an error at index', j, 'The Balance should not be 0')
                            print(tdf[['Symb', 'Tindex', 'Account', 'Time', 'Side', 'Qty', 'Balance']])
                        self.assertNotEqual(tdf.at[j, 'Balance'], 0)
                    else:
                        if tdf.at[j, 'Balance'] != 0:
                            print('Found an error at index', xl, 'The balance should be 0')
                            print(df[['Symb','Tindex',  'Account', 'Time', 'Side', 'Qty', 'Balance']])
                        self.assertEqual(tdf.at[j, 'Balance'], 0)
                    if lastd:
                        if lastd > thisd:
                            print('Found an error in the Time sequencing of', tnum)
                            print(thisd, ' > ',  lastd, ' = ',  thisd > lastd)
                            print(df[['Symb', 'Tindex',  'Account', 'Time', 'Side', 'Qty', 'Balance']])
                            self.assertGreater(thisd,  lastd)
        

    # TODO Redo this when the random trades are upgraded to creating accurate PL in all cases
    def test_addSummaryPL(self):
        '''
        Test the method DefineTrades.addStartTime. Send some randomly generated trades excluding
        the start field and then test the results for the start field.
        '''
        NUMTRADES = 4
        trades = list()
        start = pd.Timestamp('2018-06-06 09:30:00')
        df = pd.DataFrame()
        exclude = []
        for i in range(4):
            tdf, start = randomTradeGenerator2(i+1, earliest=start,
                                                pdbool=True, exclude=exclude)
            df = df.append(tdf)
            exclude.append(tdf.Symb.unique()[0])
            
        df.reset_index(drop=True, inplace=True)

        frc = FinReqCol()
        df2 = df.copy()
        
        df2[frc.sum] = None

        df3 = df2.copy()
        
        df3 = df3.sort_values(['Symb', 'Account', 'Time'])
        dtrades = DefineTrades()
        df3 = dtrades.addTradePL(df3)
        
        for i in range(NUMTRADES):
            tnum = 'Trade ' + str(i+1)
            tdf = df3[df3.Tindex == tnum]
            tdf_gen = df[df.Tindex == tnum]


            
            for i, row in tdf.iterrows():
                if row.Balance:
                    assert not row.Sum
                else:
                    
                    assert tdf['P / L'].sum() ==  row.Sum
                    assert row.Sum == tdf_gen.loc[tdf_gen.index[-1]].Sum    


    def test_addTradeDuration(self):
        '''
        Test the method DefineTrades.addStartTime. Send some randomly generated trades excluding
        the start field and then test the results for the start field. Specifically 
        Test that Duration val is placed only when the trade has 0 Shares
        Test that the the original is the same dur as that created by addTradeDuration
        Test Duration is difference from each Last Trade - Start val
        '''
        NUMTRADES = 4
        trades = list()
        start = pd.Timestamp('2018-06-06 09:30:00')
        df = pd.DataFrame()
        exclude = []
        for i in range(NUMTRADES):
            tdf, start = randomTradeGenerator2(i+1, earliest=start,
                                                pdbool=True, exclude=exclude)
            df = df.append(tdf)
            exclude.append(tdf.Symb.unique()[0])
            
        df.reset_index(drop=True, inplace=True)

        frc = FinReqCol()
        df2 = df.copy()
        df2[frc.dur] = None
        df3 = df2.copy()
        
        df3 = df3.sort_values(['Symb', 'Account', 'Time'])
        dtrades = DefineTrades()
        df3 = dtrades.addTradeDuration(df3)
        
        for i in range(NUMTRADES):
            tnum = 'Trade ' + str(i+1)
            tdf = df3[df3.Tindex == tnum]
            tdf_gen = df[df.Tindex == tnum]
            xl = tdf.index[-1]
            xl_gen = tdf_gen.index[-1]

            assert len(tdf.Tindex.unique()) == 1

            
            for i, row in tdf.iterrows():
                if row.Balance:
                    assert not row.Duration
                else:
                    if not row.Duration:
                        assert len(tdf) == 2
                        assert tdf.loc[tdf.index[0]].Side.startswith('HOLD')
                    # assert row.Duration
                    diff = row.Time - row.Start
                    assert diff == row.Duration
                    assert row.Duration == tdf_gen.loc[xl_gen].Duration

    def test_addTradePL(self):
        '''
        Test the method DefineTrades.addTradePL. Create random trade and remove the sum val
        
        Call addtradePL and compare the origianl generation with the new one. 
        Specifically Test that Sum val is placed only when the trade has 0 Shares
        Test that the the original is the same PL as that created by addTradeDuration
        Test Sum is sum or the PL values from the trade.
        '''
        NUMTRADES = 4
        trades = list()
        start = pd.Timestamp('2018-06-06 09:30:00')
        df = pd.DataFrame()
        exclude = []
        for i in range(4):
            tdf, start = randomTradeGenerator2(i+1, earliest=start,
                                                pdbool=True, exclude=exclude)
            df = df.append(tdf)
            exclude.append(tdf.Symb.unique()[0])
            
        df.reset_index(drop=True, inplace=True)

        frc = FinReqCol()
        df2 = df.copy()
        
        df2[frc.sum] = None
        

        df3 = df2.copy()
        
        df3 = df3.sort_values(['Symb', 'Account', 'Time'])
        dtrades = DefineTrades()
        df3 = dtrades.addTradePL(df3)
        
        for i in range(NUMTRADES):
            tnum = 'Trade ' + str(i+1)
            tdf = df3[df3.Tindex == tnum]
            tdf_gen = df[df.Tindex == tnum]


            
            for i, row in tdf.iterrows():
                if row.Balance:
                    assert not row.Sum
                else:
                    
                    assert isclose(tdf['PnL'].sum(),  row.Sum, abs_tol=1e-7)
                    assert isclose(row.Sum, tdf_gen.loc[tdf_gen.index[-1]].Sum, abs_tol=1e-7)

                

    def test_addSummaryPL(self):
        '''
        Test the method DefineTrades.addStartTime. Send some randomly generated trades excluding
        the start field and then test the results for the start field.
        '''
        NUMTRADES = 4
        trades = list()
        start = pd.Timestamp('2018-06-06 09:30:00')
        df = pd.DataFrame()
        exclude = []
        for i in range(4):
            tdf, start = randomTradeGenerator2(i+1, earliest=start,
                                                pdbool=True, exclude=exclude)
            df = df.append(tdf)
            exclude.append(tdf.Symb.unique()[0])
            
        df.reset_index(drop=True, inplace=True)

        frc = FinReqCol()
        df2 = df.copy()
        
        df2[frc.sum] = None

        df3 = df2.copy()
        
        df3 = df3.sort_values(['Symb', 'Account', 'Time'])
        dtrades = DefineTrades()
        df3 = dtrades.addTradePL(df3)
        
        for i in range(NUMTRADES):
            tnum = 'Trade ' + str(i+1)
            tdf = df3[df3.Tindex == tnum]
            tdf_gen = df[df.Tindex == tnum]


            
            for i, row in tdf.iterrows():
                if row.Balance:
                    assert not row.Sum
                else:
                    
                    assert isclose(tdf['PnL'].sum(), row.Sum, abs_tol=1e-7)
                    assert isclose(row.Sum, tdf_gen.loc[tdf_gen.index[-1]].Sum, abs_tol=1e-7)

def notmain():
    '''Run some local code'''
    for i in range(3):
        t = TestDefineTrades()
        # t.test_addStartTime()
        # t.test_addTradeIndex()
    
        # t.test_addTradeDuration()
        t.test_addSummaryPL()
        # t.test_addTradePL()
        # t.test_writeShareBalance()
    
    # t.test_addSummaryPL()


def main():
    '''
    Test discovery is not working in vscode. Use this for debugging.
    Then run cl python -m unittest discovery
    '''
    f = TestDefineTrades()
    for name in dir(f):
        if name.startswith('test'):
            attr = getattr(f, name)

            if isinstance(attr, types.MethodType):
                attr()

if __name__ == '__main__':
    # main()
    notmain()
