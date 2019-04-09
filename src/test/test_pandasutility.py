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

from journal.pandasutil import InputDataFrame
from journal.statement import Statement_DAS
from journal.definetrades import ReqCol
from journalfiles import JournalFiles
from test.rtg import randomTradeGenerator2

# pylint: disable = C0103




class Test_Pandasutility(unittest.TestCase):
    '''
    Test the methods in Statement_DAS
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(Test_Pandasutility, self).__init__(*args, **kwargs)
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

        # Input test files can be added here.  Should add files that should fail in another list
        self.infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
                        'trades.8.csv', 'trades.907.WithChangingHolds.csv',
                        'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
                        'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
                        'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv',
                        'trades190221.BHoldPreExit.csv']

    

    def testZeroPad(self):
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

    

    def testGetOvernightTrades(self):
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


    # @patch('journal.pandasutil.askUser')
    # def walkit(self, mock_askUser):
    def walkit(self):
        '''
        Run Structjour multiple times with test files
        I think this methods usefulness is done. Leave for now (3/30/19)
        '''
        from trade import run

        tests = [[1, 'trades.1116_messedUpTradeSummary10.csv',
                  [['PCG', 'Sim', 'Short', 'After', 4000]]],
                 [2, 'trades.8.WithHolds.csv',
                  [['MU', 'Sim', 'Short', 'After', 750],
                   ['IZEA', 'SIM', 'Long', 'After', 3923]]],
                 [3, 'trades.8.csv', []],
                 [4, 'trades.907.WithChangingHolds.csv',
                  [['MU', 'Live', 'Long', 'After', 50],
                   ['AMD', 'Sim', 'Long', 'After', 600],
                   ['FIVE', 'Live', 'Long', 'After', 241]]],
                 [5, 'trades_190117_HoldError.csv',
                  [['PCG', 'Live', 'Short', 'After', 169]]],
                 [6, 'trades.8.ExcelEdited.csv', []],
                 [7, 'trades.910.tickets.csv',
                  [['AMD', 'Sim', 'Long', 'Before', 600]]],
                 [8, 'trades_tuesday_1121_DivBy0_bug.csv', []],
                 [9, 'trades.8.WithBothHolds.csv',
                  [['MU', 'Sim', 'Short', 'Before', 750],
                   ['TSLA', 'Sim', 'Long', 'After', 50]]],
                 [10, 'trades1105HoldShortEnd.csv',
                  [['AMD', 'Live', 'Short', 'After', 600]]]]


        #Will give an arbitrary date to avoid name conflicts
        for count, infile in enumerate(self.infiles):
            # infile = 'trades.csv'
            outdir = 'out/'
            theDate = pd.Timestamp(2019, 1, count+1)
            print(theDate)
            indir = 'data/'
            mydevel = True
            # mock_askUser.
            #         some_func.return_value = (20, False)
            # num, stat = f2()
            # self.assertEqual((num, stat), (40, False))

            run(infile=infile, outdir=outdir, theDate=theDate,
                indir=indir, infile2=None, mydevel=mydevel)

            # for i in tests:
            #     print (i[0], i[1])
            if tests[count][2]:
                for j in tests[count][2]:
                    print(infile, tests[count][1])
                    print('     ', j)

            if count == 31:
                exit()

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

        df2 = df [['Time', 'Symb', 'Side', 'Qty', 'Account', 'P / L']].copy()
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
    f = Test_Pandasutility()
    for name in dir(f):
        if name.startswith('test'):
            attr = getattr(f, name)

            if isinstance(attr, types.MethodType):
                attr()



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
