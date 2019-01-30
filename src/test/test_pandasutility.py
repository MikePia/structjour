'''
Test the methods in th module journal.pandasutility
Created on Sep 9, 2018

@author: Mike Petersen
'''
from math import isclose
import unittest
import os
import types

import pandas as pd

from journal.pandasutil import InputDataFrame, ToCSV_Ticket as Ticket
from journal.tradeutil import ReqCol
from journalfiles import JournalFiles

# pylint: disable = C0103


class Test_SingleTicket(unittest.TestCase):
    '''
    Test the methods in ToCSV_Ticket
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(Test_SingleTicket, self).__init__(*args, **kwargs)
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

        # Input test files can be added here.  Should add files that should fail in another list
        self.infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
                        'trades.8.csv', 'trades.907.WithChangingHolds.csv',
                        'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
                        'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
                        'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv']

    def test_GetListOfTicketDF(self):
        '''
        Test the method ToCSV_Ticket.getListOfTicketDF.
        Explicitly tests: Each ticket has only long or short only
                          Each ticket has a single ticker symbol, cloid, and account
        '''
        rc = ReqCol()

        outdir = 'data/'
        # A list of files that were problematic
        infiles = self.infiles

        # otherinfiles = ['trades.911.noPL.csv', 'trades.csv']
        for f in infiles:
            trade = os.path.join(outdir, f)
            jf = JournalFiles(indir=outdir, infile=f, outdir='out/', mydevel=True)

            tkt = Ticket(jf)
            tktList = tkt.getListOfTicketDF()

            totalTX = 0
            for ticket in tktList:
                self.assertEqual(len(ticket[rc.side].unique(
                )), 1, "There can only be one side, long or short, in a ticket")
                self.assertEqual(len(ticket[rc.ticker].unique(
                )), 1, "There can only be one ticker in a ticket")
                self.assertEqual(
                    len(ticket['Cloid'].unique()), 1, "There can be only one Cloid in a ticket")
                self.assertEqual(
                    len(ticket[rc.acct].unique()), 1, "There can be only one account in a ticket")

                totalTX = totalTX + len(ticket)

            trades = pd.read_csv(jf.inpathfile)
            msg = "There is a discrepancy in number of transactions in the  tickets"
            self.assertEqual(len(trades), totalTX, msg)

    def testCreateSingleTicket(self):
        '''
        Test the method ToCSV_Ticket.createSingleTicket.  Requires the list of dfs created by
        getListOfTicketDF. Explicitly test that each element is a 1 row DataFrame. That the new
        price, (the average price of its transactions) is always greater than the min and less
        than the max. And finally check that the total number of shares (total) is the same as
        the sum of shares in constituent transactions.
        '''
        rc = ReqCol()
        indir = 'data/'
        outdir = 'out/'
        infiles = self.infiles

        for infile in infiles:
            jf = JournalFiles(indir=indir,
                              infile=infile, outdir=outdir)
            tkt = Ticket(jf)

            listTick = tkt.getListOfTicketDF()
            totalSharesForDay = 0
            for tick in listTick:

                singleTicket = tkt.createSingleTicket(tick)
                self.assertIsInstance(singleTicket, type(
                    pd.DataFrame()), "Failed to create a DataFrame")
                self.assertEqual(len(singleTicket), 1,
                                 "Failed to create a single item ticket")
                # print(tick[rc.price].min())
                # print(singleTicket[rc.price].unique()[0])
                # print(tick[rc.price].max())
                # print()
                try:
                    isclose(singleTicket[rc.price].unique()[0], tick[rc.price].max(), abs_tol=1e-8)
                except AssertionError:
                    self.assertLessEqual(singleTicket[rc.price].unique()[0], tick[rc.price].max())
                try:
                    isclose(singleTicket[rc.price].unique()[0], tick[rc.price].min(), abs_tol=1e-8)
                except AssertionError:
                    self.assertGreaterEqual(singleTicket[rc.price].unique()[0], 
                                            tick[rc.price].min())

                totalSharesForDay = totalSharesForDay + tick[rc.shares].sum()

            dframe = pd.read_csv(jf.inpathfile)
            self.assertEqual(dframe[rc.shares].sum(),
                             totalSharesForDay, "Failed to acount for all the shares transacted.")

    def testNewSingleTxPerTicket(self):
        '''
        Test the method ToCSV_Ticket.newSingleTxPerTicket. That method creates a new csv file
        reducing multi row transactions to a single row, averaging the prices, totaling the
        amounts. 
        Explicitly tests: A newFile has been created and made the infile of JournalFiles.
                          The PL summary is the same between the two files .
                          The shares total for each symbol/account/buy/sell is the same

        '''
        rc = ReqCol()
        for infile in self.infiles:
            # infile = "trades.910.tickets.csv"
            outdir = 'out/'
            indir = 'data/'
            indir = os.path.realpath(indir)

            inpathfile = os.path.join(indir, infile)
            jf = JournalFiles(indir=indir, infile=infile, outdir=outdir)

            origdframe = pd.read_csv(jf.inpathfile)
            originfile = jf.infile

            tkt = Ticket(jf)
            newDF, jf = tkt.newDFSingleTxPerTicket()

            self.assertNotEqual(originfile, jf.infile)
            newdframe = pd.read_csv(jf.inpathfile)

            self.assertAlmostEqual(origdframe[rc.PL].sum(), newdframe[rc.PL].sum(), places=10)
            self.assertAlmostEqual(newDF[rc.PL].sum(), newdframe[rc.PL].sum(), places=10)

            for symbol in origdframe[rc.ticker].unique():
                for accnt in origdframe[rc.acct].unique():
                    d = origdframe
                    n = newDF

                    d = d[d[rc.ticker] == symbol]
                    d = d[d[rc.acct] == accnt]
                    dbuy = d[d[rc.side].str.startswith('B')]
                    dsell = d[d[rc.side].str.startswith('S')]

                    n = n[n[rc.ticker] == symbol]
                    n = n[n[rc.acct] == accnt]
                    nbuy = n[n[rc.side].str.startswith('B')]
                    nsell = n[n[rc.side].str.startswith('S')]

                    self.assertEqual(dbuy[rc.shares].sum(), nbuy[rc.shares].sum())
                    self.assertEqual(dsell[rc.shares].sum(), nsell[rc.shares].sum())

    def testZeroPad(self):
        '''
        Both this method and the tested method are extremely dependent on extra outside
        circumstances. For example This method depends on the transactions to begin between 9 and
        10 as recorded by DAS. (A purchase at 8 will cause this test to fail) Right now I have only
        one case to test ('data/TradesExcelEdited.csv')so wtf, leave it till I have a test case.
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
                self.assertEqual(len(x),  8)
                (h,m,s) = x.split(':')
                try:
                    h = int(h)
                    m = int(m)
                    s = int(s)
                    self.assertLess(h, 24)
                    self.assertLess(m, 60)
                    self.assertLess(s, 60)
                except NameError:
                    self.fail('Time has a wrong value')

    def testMkShortNegative(self):
        '''
        Test the method ToCSV_Ticket.mkShortsNegative
        '''
        rc = ReqCol()
        side = ['B', 'S', 'S', 'SS', 'B', 'B']
        mult = [1, -1, -1, -1, 1, 1]
        shares = [100, 200, 300, 400, 500, 600]
        testSet = list(zip(side, shares))

        apd = pd.DataFrame(testSet, columns=[rc.side, rc.shares])

        for i in range(6):
            self.assertEqual(apd[rc.shares][i], shares[i])

        idf = InputDataFrame()
        apd = idf.mkShortsNegative(apd)
        for i in range(6):
            self.assertEqual(apd[rc.shares][i], shares[i] * mult[i])

    def testGetListTickerDF(self):
        '''
        Testing ToCSV_Ticket.getListTickerDF
        '''

        rc = ReqCol()

        tickers = ['MU', 'MU', 'MU',
                   'TWTR', 'TWTR', 'TWTR', 'TWTR', 'TWTR', 'TWTR',
                   'AAPL', 'AAPL', 'AAPL', 'AAPL', 'AAPL', 'AAPL', 'AAPL',
                   'MU', 'MU', 'MU']
        U1 = "U12345"
        U2 = "TR12345"
        accounts = [U1, U1, U1,
                    U1, U1, U1, U2, U2, U2,
                    U2, U1, U2, U2, U1, U1, U1,
                    U2, U2, U2]

        testSet = list(zip(tickers, accounts))

        apd = pd.DataFrame(testSet, columns=[rc.ticker, rc.acct])

        ipd = InputDataFrame()
        listDf = ipd.getListTickerDF(apd)

        #A dataframe for each ticker in both accounts
        self.assertEqual(len(listDf), 6)
        for df in listDf:
            self.assertEqual(len(df[rc.ticker].unique()), 1)
            self.assertEqual(len(df[rc.acct].unique()), 1)

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
                            print ('error', 'Side is ', row['Side'])
                    if buy != 0:
                        # Create the same data format used in getOvernightTrades
                        sl.append({'ticker' : symbol, 'shares': buy, 'before':0, 'after': 0, 'acct': account})
            idf = InputDataFrame()
            dframe = idf.mkShortsNegative(dframe)
            st = idf.getOvernightTrades(dframe)
            self.assertEqual(len(sl), len(st))
            for trade in sl:
                self.assertTrue(trade in sl)



def main():
    '''
    Test discovery is not working in vscode. Use this for debugging.
    Then run cl python -m unittest discovery
    '''
    f = Test_SingleTicket()
    for name in dir(f):
        if name.startswith('test'):
            attr = getattr(f, name)

            if isinstance(attr, types.MethodType):
                attr()



def notmain():
    '''Run some local code'''
    t = Test_SingleTicket()
    t.test_GetListOfTicketDF()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCheckRequiredColumns']
    # unittest.main()
    # notmain()
    main()
