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
Test the methods in the module thetradeobject. 
Created on Nov 5, 2018

TODO: Expand on the random trade generator to create a random TradeObject generator for all the
relavent tests in this module. Should not have to run the program to test these methods and doing
so severely limits the effectiveness of these tests to pre hand-checked data

@author: Mike Petersen
'''
import os
import unittest
import types
from random import randint

from PyQt5.QtCore import QSettings

from structjour.journalfiles import JournalFiles
from structjour.definetrades import DefineTrades
from structjour.thetradeobject import TheTradeObject, SumReqFields
from structjour.colz.finreqcol import FinReqCol

# pylint: disable = C0103, W0212, C0111

# Global
grf = SumReqFields()

@unittest.skip("Uses the old stuff in setup")
class TestTheTradeObject(unittest.TestCase):
    '''
    Test the functions in methods in thetradeobject module. The tests for TheTradeObject test the
    results of a single known trade. Its pretty weak
    '''

    def __init__(self, *args, **kwargs):
        super(TestTheTradeObject, self).__init__(*args, **kwargs)
        # global DD

        # Input test files can be added here.  Should add files that should fail in another list
        # Not using yet. Create accompanying positions.csv for files with HOLDs. Incrementally 
        # getting rid of the interview thing as much as possible at least in the testing.
        self.infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
                        'trades.8.csv', 'trades.907.WithChangingHolds.csv',
                        'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
                        'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
                        'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv',
                        'trades190221.BHoldPreExit.csv']

        self.settings = QSettings('zero_substance', 'structjour')
        self.tto = self.setupForTheTradeObject(infile=self.infiles[2])

    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def test_SumReqFields(self):
        '''
        This class is just data. The only thing that can go wrong is to let it get
        out of sync which is very difficult to auto test. The real test is to visually
        verify the output above. Will test the data is the correct type
        '''
        srf = SumReqFields()
        theStyles = srf.getStyles()
        skiphack = ['date', 'clean', 'id']      # these keys are not found on summary form (or tfcolumns)
        for k in srf.rc.keys():
            if k in skiphack:
                continue
            value = srf.rc[k]
            address = srf.tfcolumns[value][0]
            style = srf.tfcolumns[value][1]
            self.assertIn(style, theStyles, f'{style} is not registered')
            # print("{0:12} {1:10} {2}  ".format(k, value, address))
            if isinstance(address, list):
                self.assertIsInstance(address[0], tuple)
                self.assertIsInstance(address[1], tuple)
                self.assertIsInstance(address[0][0], int)
                self.assertIsInstance(address[0][1], int)
                self.assertIsInstance(address[1][0], int)
                self.assertIsInstance(address[1][1], int)
            else:
                self.assertIsInstance(address[0], int)
                self.assertIsInstance(address[1], int)



        # print(self.test_SumReqFields.__doc__)
        self.assertEqual(len(srf.columns), len(
            srf.rc.keys()), "This cannot fail! FLW")
        # print(srf.getStyles())
        self.assertIn("normStyle", srf.getStyles())
        self.assertIn("explain", srf.getStyles())
        self.assertIn("normalNumberTopRight", srf.getStyles())
        self.assertIn("normalSubLeft", srf.getStyles())

    def setupForTheTradeObject(self, getMax=False, infile="trades.8.csv"):
        '''Set up the DataFrames'''
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))
        self.settings.setValue('runType', 'QT')
        # x = os.getcwd()
        # print('===============================================================')
        # print(" callin JournalFiles from ", x)
        jf = JournalFiles(mydevel=True, infile=infile, indir="data/",
                          outdir="out/", inputType='DAS')

    def test_TheTradeObjectSetName(self):

        tto = self.setupForTheTradeObject()

        x0 = self.tto.df.index[0]

        side = self.tto.df.at[x0, 'Side']
        ticker = self.tto.df.at[x0, 'Symb']
        side = ' Long' if side.startswith('B') or side.startswith('HOLD+') else ' Short'
        name = ticker + side
        tto._TheTradeObject__setName()
        tto._TheTradeObject__setName()
        self.assertEqual(tto.TheTrade[grf.name].unique()[0],
                         name, "Failed to set the name correctly")

    def test_TheTradeObjectSetAcct(self):
        # tto = self.setupForTheTradeObject()
        self.tto._TheTradeObject__setAcct()
        self.assertEqual(self.tto.TheTrade[grf.acct].unique()[
            0], "SIM", "Failed to set the account correctly")

    def test_TheTradeObjectSetSum(self):
        self.tto._TheTradeObject__setSum()
        daSum = self.tto.df[grf.pl].sum()
        self.assertEqual(self.tto.TheTrade[grf.pl].unique()[
            0], daSum, "Failed to set p/l correctly")

    def test_TheTradeObjectSetStart(self):
        x0 = self.tto.df.index[0]
        xl = self.tto.df.index[-1]
        l = len(self.tto.df)
        if not self.tto.df.at[x0, 'Side'].startswith('HOLD'):
            start = self.tto.df.at[x0, 'Time']
        else:
            self.assertGreater(len(self.tto.df), 1)
            x1 = self.tto.df.index[1]
            start = self.tto.df.at[x1, 'Time']


        self.tto._TheTradeObject__setStart()
        self.assertEqual(self.tto.TheTrade[grf.start].unique()[
            0], start, "Failed to set start time correctly")

    def test_TheTradeObjectSetDur(self):
        '''
        Just test if both tto and the df have the same minutes and seconds.
        '''
        self.tto._TheTradeObject__setDur()
        xl = self.tto.df.index[-1]
        dur = str(self.tto.df.at[xl, 'Duration']).split(':')
        ttodur = self.tto.TheTrade[grf.dur].unique()[0].split(':')
        if len(dur) > 1 and len(ttodur) > 1:
            secdur = int(dur[-1])
            sectto = int(ttodur[-1])
            mindur = int(dur[-2])
            mintto = int(ttodur[-2])
            self.assertEqual(mindur, mintto)
            self.assertEqual(secdur, sectto)
        # self.assertEqual(ttodur, dur, "Failed to set duration time correctly")

    def test_TheTradeObjectSetStrategy(self):
        '''Skipping because I don't do mock...(yet) The mechanics are the 
        same for all of theses anyway. ... Now im just lazy'''

    def test_TheTradeObjectSetShares(self):
        x0 = self.tto.df.index[0]

        mult = 1 if self.tto.df.at[x0, 'Side'].startswith('B') else -1
        mag = 0
        daShares = 0
        side = self.tto.df.at[x0, 'Side']
        minmax = True if side.startswith('B') or side.startswith('HOLD+') else False
        bal = self.tto.df['Balance'].max() if minmax else self.tto.df['Balance'].min()
    
        self.tto._TheTradeObject__setShares()
        ttoshares = self.tto.TheTrade[grf.shares].unique()[0]
        daShares = str(bal) + ' shares'
        self.assertEqual(ttoshares, daShares, "Failed to set position correctly")

        shares = self.tto.getShares()
        self.assertEqual(bal, shares, "Failed to set position correctly")

    def test_TheTradeObjectSetMarketValue(self):
        self.tto._TheTradeObject__setMarketValue()
        x0 = self.tto.df.index[0]
        side = self.tto.df.at[x0, 'Side']
        minmax = True if side.startswith('B') or side.startswith('HOLD+') else False
        qty = self.tto.df['Balance'].max() if minmax else self.tto.df['Balance'].min()
        price = self.tto.df.at[x0, 'Price']
        mkt = qty * price
        ttomkt = self.tto.TheTrade[grf.mktval].unique()[0]
        self.assertEqual(ttomkt, mkt, "Failed to set position correctly")

    def test_TheTradeObjectSetHeaders(self):
        self.tto._TheTradeObject__setHeaders()

        ttopl = self.tto.TheTrade[grf.plhead].unique()[0]
        ttostart = self.tto.TheTrade[grf.starthead].unique()[0]
        ttodur = self.tto.TheTrade[grf.durhead] .unique()[0]
        ttoshare = self.tto.TheTrade[grf.sharehead].unique()[0]
        ttomkt = self.tto.TheTrade[grf.mkthead] .unique()[0]
        ttoentry = self.tto.TheTrade[grf.entryhead].unique()[0]
        ttotarg = self.tto.TheTrade[grf.targhead].unique()[0]
        ttostop = self.tto.TheTrade[grf.stophead].unique()[0]
        ttorr = self.tto.TheTrade[grf.rrhead].unique()[0]
        ttomax = self.tto.TheTrade[grf.maxhead].unique()[0]
        ttomstk = self.tto.TheTrade[grf.mstkhead].unique()[0]


        self.assertEqual(ttopl, "P/L", "Failed to set head correctly")
        self.assertEqual(ttostart, "Start", "Failed to set head correctly")
        self.assertEqual(ttodur, "Dur", "Failed to set head correctly")
        self.assertEqual(ttoshare, "Pos", "Failed to set head correctly")
        self.assertEqual(ttomkt, "Mkt", "Failed to set head correctly")
        self.assertEqual(ttoentry, 'Entries and Exits', "Failed to set head correctly")
        self.assertEqual(ttotarg, 'Target', "Failed to set head correctly")
        self.assertEqual(ttostop, 'Stop', "Failed to set head correctly")
        self.assertEqual(ttorr, 'R:R', "Failed to set head correctly")
        self.assertEqual(ttomax, 'Max Loss', "Failed to set head correctly")
        self.assertEqual(ttomstk, "Proceeds Lost", "Failed to set head correctly")

    def test_TheTradeObjectSetEntries(self):
        rc = FinReqCol()
        self.tto._TheTradeObject__setEntries()
        # if len(self.tto.df) < 4:
        #     self.fail('This test requires a longer sample of transactions to run.')
        count = 0
        x0 = self.tto.df.index[0]
        side = self.tto.df.at[x0, rc.side]
        for i, row in self.tto.df.iterrows():
            count += 1
            # print (row[rc.price], row[rc.side], row[rc.PL])
            if (side.startswith('B') and row[rc.side].startswith('B')) or (
                side.startswith('S') and row[rc.side].startswith('S')):
                if row[rc.price] != 0:
                    entry = 'Entry' + str(count)
                    ttoprice = self.tto.TheTrade[entry].unique()[0]
                    self.assertEqual(ttoprice, row.Price, "Failed to set entry correctly")
            elif (side.startswith('B') and row[rc.side].startswith('S')) or (
                side.startswith('S') and row[rc.side].startswith('B')):
                if row[rc.price] != 0:
                    entry = 'Exit' + str(count)
                    ttoprice = self.tto.TheTrade[entry].unique()[0]
                    self.assertEqual(ttoprice, row[rc.price], "Failed to set exit correctly")
            if row[rc.PL] != 0:
                PLname = 'PL' + str(count)
                ttopl =  self.tto.TheTrade[PLname].unique()[0]

                self.assertEqual(ttopl, row[rc.PL], "Failed to set pl correctly")


def main():
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


def notmain():
    '''
    Test discovery is not working in vscode. Use this for debugging.
    Then run cl python -m unittest discovery
    '''
    f = TestTheTradeObject()
    for name in dir(f):
        if name.startswith('test'):
            attr = getattr(f, name)

            if isinstance(attr, types.MethodType):
                attr()
def reallylocal():
    f = TestTheTradeObject()
    f.test_TheTradeObjectSetDur()
    f.test_TheTradeObjectSetSum()
    f.test_TheTradeObjectSetStart()
    f.test_TheTradeObjectSetShares()
    f.test_TheTradeObjectSetName()
    f.test_TheTradeObjectSetMarketValue()
    f.setupForTheTradeObject(getMax=True)
    f.test_TheTradeObjectSetEntries()
    f.test_TheTradeObjectSetDur()


if __name__ == "__main__":
    # notmain()
    main()
    # reallylocal()
