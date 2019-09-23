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
Test the methods in th module journal.statement
Created on Mar 30, 2019

@author: Mike Petersen
'''

from math import isclose
import unittest
import os
import random
import types

import pandas as pd

from structjour.statement import Statement_DAS, Statement_IBActivity
from structjour.definetrades import ReqCol
from structjour.journalfiles import JournalFiles



def getTestSet(length=6):
    '''Utility test set generator for MkShortNegative
    '''
    side = []
    mult = []
    shares = []
    for dummy in range(length):
        s = random.random()
        s2 = random.randint(1, 20)

        if s < 0.5:
            side.append('S')
            mult.append(-1)
        else:
            side.append('B')
            mult.append(1)
        shares.append(s2*50)

    return side, mult, shares


class Test_Statements(unittest.TestCase):
    '''
    Test the methods and functions in statement module
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(Test_Statements, self).__init__(*args, **kwargs)

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

    def test_GetListOfTicketDF(self):
        '''
        Test the method Statement_DAS.getListOfTicketDF.
        Explicitly tests: Each ticket has only long or short only
                          Each ticket has a single ticker symbol, cloid, and account
        '''
        rc = ReqCol()

        outdir = 'data/'
        # A list of files that were problematic
        infiles = self.infiles

        # otherinfiles = ['trades.911.noPL.csv', 'trades.csv']
        for f in infiles:
            # trade = os.path.join(outdir, f)
            jf = JournalFiles(indir=outdir, infile=f, outdir='out/', mydevel=True)

            tkt = Statement_DAS(jf)
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

    def test_CreateSingleTicket(self):
        '''
        Test the method Statement_DAS.createSingleTicket.  Requires the list of dfs created by
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
            tkt = Statement_DAS(jf)

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

    def test_NewSingleTxPerTicket(self):
        '''
        Test the method Statement_DAS.newSingleTxPerTicket. That method creates a new csv file
        reducing multi row transactions to a single row, averaging the prices, totaling the
        amounts.
        Explicitly tests: A newFile has been created and made the infile of JournalFiles.
                          The PL summary is the same between the two files .
                          The shares total for each symbol/account/buy/sell is the same

        '''
        rc = ReqCol()
        for infile in self.infiles:
            outdir = 'out/'
            indir = 'data/'
            indir = os.path.realpath(indir)

            jf = JournalFiles(indir=indir, infile=infile, outdir=outdir)

            if not os.path.exists(jf.inpathfile):
                msg = os.path.realpath(jf.inpathfile)
                raise ValueError(msg)

            origdframe = pd.read_csv(jf.inpathfile)
            originfile = jf.infile

            tkt = Statement_DAS(jf)
            newDF, jf = tkt.getTrades()

            self.assertNotEqual(originfile, jf.infile)
            newdframe = pd.read_csv(jf.inpathfile)

            self.assertAlmostEqual(origdframe['P / L'].sum(), newdframe[rc.PL].sum(), places=10)
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



    def test_getPositionsIB(self):


        infile= 'ActivityStatement.20190411.html'

        jf = JournalFiles(infile=infile, theDate='2019-04-11', mydevel=True)

        st = Statement_IBActivity(jf)
        df = st.getPositions()



def notmain():
    t = Test_Statements()
    # t.test_GetListOfTicketDF()
    # t.test_CreateSingleTicket()
    t.test_NewSingleTxPerTicket()
    # t.test_MkShortNegative()
    t.testGetListTickerDF()
    t.test_getPositionsIB()

def main():
    unittest.main()

if __name__ == '__main__':
    # notmain()
    main()