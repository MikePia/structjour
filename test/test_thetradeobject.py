#
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
import re
import unittest

from PyQt5.QtCore import QSettings

from structjour.definetrades import DefineTrades
from structjour.thetradeobject import TheTradeObject, SumReqFields
from structjour.colz.finreqcol import FinReqCol

from structjour.statements.ibstatementdb import StatementDB
from structjour.statements.ibstatement import IbStatement
from structjour.statements.statement import getStatementType
from structjour.statements.dasstatement import DasStatement
from structjour.utilities.util import isNumeric

# pylint: disable = C0103, W0212, C0111

# Global
grf = SumReqFields()


class TestTheTradeObject(unittest.TestCase):
    '''
    Test the functions and methods in thetradeobject module. TheTradeObject input requires a bunch of
    prerequisites.
    1. Trade transactions need to be read into the database from DAS or the Broker statement
    2. A statment needs to be created which is a collection of trades from the db from a single day
    3. The transactions in the statment need to be processed into trades (a collection of transactions
        organized by trade with associated data starttime, average price, balance and user info)
    The transition from transactions to trades is achieved by DefineTrades and TheTradeObject.
    DefineTrades is responsible for:
        separating which transactions go together, numbering the trades (for each day), giving
        a common start time for each tx in a trade, calculating PL, calculating PL summary, balance and
        naming the trade. (Note that sometimes information is incomplete)
    TheTradeObject is responsible for:
        Creating the 1 row DataFrame that holds relavant information for a single trade- and multiple tx.
            Includes chartnames, headernames for the form, user info like RR, target... and tx info for
            each trade (up to 8 transactions included) (Note trade_sum table holds all tx as a relation)
        Creating the entries dict that holds the transaction data like price, time, average and shares. Used
            in creating the entry widgets in charts. The same data also goes in theTradeObjectDataFrame--
    '''

    datadir = os.path.join(os.getcwd(), 'data')
    testdb = os.path.join(datadir, 'testdb.sqlite')
    inputType = ''
    ttos = []
    infiles = ['dastrades_20190221.csv']
    thedates = ['20190221']
    # infiles = ['dastrades_20181116.csv.csv', 'dastrades_20180907.csv',
    #            'dastrades_20190117.csv', 'dastrades_20180910.csv',
    #            'dastrades_20181120.csv', 'dastrades_20181105.csv',
    #            'dastrades_20190221.csv', 'ActivityDaily.663710.20191101.csv']
    # thedates = ['20181116', '20180907',
    #             '20190117', '20180910',
    #             '20181120', '20181105',
    #             '20190221', '20191101']


    @classmethod
    def setUpClass(cls):
        '''
        Open up a bunch of statments and add them to a test database for testing stuff
        TODO: Develop the randomtradgenerator write trades to the db for more generic testing
        '''
        settings = QSettings('zero_substance', 'structjour')
        for i, name in enumerate(cls.infiles):
            name = os.path.join(cls.datadir, name)
            x, cls.inputType = getStatementType(name)
            print(cls.inputType)
            if cls.inputType == 'DAS':
                ds = DasStatement(name, settings, cls.thedates[i])
                ds.getTrades(testFileLoc=cls.datadir, testdb=cls.testdb)
            elif cls.inputType == "IB_CSV":
                ibs = IbStatement(db=cls.testdb)
                ibs.openIBStatement(name)
            else:
                continue
            #     self.assertTrue(4 == 5, "Unsupported file type in test_TheTradeObject")

            statement = StatementDB(db=cls.testdb)
            df = statement.getStatement(cls.thedates[i])
            # self.assertFalse(df.empty, f"Found no trades in db on {daDate}")
            dtrade = DefineTrades(cls.inputType)
            dframe, ldf = dtrade.processDBTrades(df)
            tto = TheTradeObject(ldf[0], False, SumReqFields())
            cls.ttos.append(tto)

    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))
        # self.settings.setValue('runType', 'QT')

    def test_TheTradeObjectSetName(self):
        for tto in self.ttos:
            tto._TheTradeObject__setName()

            self.assertTrue(tto.TheTrade[grf.name].unique()[0].startswith(tto.df.at[tto.df.index[0], 'Symb']), "Failed to set the name correctly")

        return

    def test_TheTradeObjectSetAcct(self):
        for tto in self.ttos:
            accnt = 'SIM' if tto.df[grf.acct].unique()[0].startswith('TR') else 'LIVE'
            tto._TheTradeObject__setAcct()

            self.assertEqual(tto.TheTrade[grf.acct].unique()[0].upper(), accnt, "Failed to set the account correctly")

        return

    def test_TheTradeObjectSetSum(self):
        for tto in self.ttos:
            tto._TheTradeObject__setSum()
            daSum = tto.df[grf.pl].sum()
            self.assertEqual(tto.TheTrade[grf.pl].unique()[0], daSum, "Failed to set p/l correctly")

    def test_TheTradeObjectSetStart(self):
        for tto in self.ttos:
            x0 = tto.df.index[0]
            if not tto.df.at[x0, 'Side'].startswith('HOLD'):
                start = tto.df.at[x0, 'Time']
            else:
                self.assertGreater(len(tto.df), 1)
                x1 = tto.df.index[1]
                start = tto.df.at[x1, 'Time']
            tto._TheTradeObject__setStart()
            self.assertEqual(tto.TheTrade[grf.start].unique()[0], start, "Failed to set start time correctly")

    def test_TheTradeObjectSetDur(self):
        '''
        Just test if both tto and the df have the same minutes and seconds.
        '''
        for tto in self.ttos:
            # xl = tto.df.index[-1]
            dur = str(tto.df.at[tto.df.index[-1], 'Duration']).split(':')
            tto._TheTradeObject__setDur()
            ttodur = re.split('\\W+', tto.TheTrade[grf.dur].unique()[0])
            if len(dur) > 1 and len(ttodur) > 1:
                self.assertEqual(int(dur[-2]), int(ttodur[-2]))
                self.assertEqual(int(dur[-1]), int(ttodur[-1]))
            # self.assertEqual(ttodur, dur, "Failed to set duration time correctly")

    def test_TheTradeObjectSetShares_and_setMarketValue(self):
        '''
        Tests the setMarketValue -- and setShares (because the setMarketValue depends on it.)
        Note that shares generally is what is in the db and with the error corrrecting stuff,
        (BAPL and all) any errors in the value generally will reside somewhere else.
        '''
        for tto in self.ttos:
            x0 = tto.df.index[0]

            # side = tto.df.at[x0, 'Side']
            # minmax = True if side.startswith('B') or side.startswith('HOLD+') else False
            # bal = tto.df['Balance'].max() if minmax else tto.df['Balance'].min()

            tto._TheTradeObject__setShares()

            shares = tto.getShares()
            ttoshares = int(float(tto.TheTrade['Shares'].unique()[0].split(' ')[0]))
            self.assertEqual(ttoshares, shares, "Failed to set position correctly")

            tto._TheTradeObject__setMarketValue()
            price = tto.df.at[x0, 'Price']
            mkt = shares * price
            ttomkt = tto.TheTrade[grf.mktval].unique()[0]
            self.assertEqual(ttomkt, mkt, "Failed to set position correctly")

    def test_TheTradeObjectSetHeaders(self):
        for tto in self.ttos:
            tto._TheTradeObject__setHeaders()

            ttopl = tto.TheTrade[grf.plhead].unique()[0]
            ttostart = tto.TheTrade[grf.starthead].unique()[0]
            ttodur = tto.TheTrade[grf.durhead] .unique()[0]
            ttoshare = tto.TheTrade[grf.sharehead].unique()[0]
            ttomkt = tto.TheTrade[grf.mkthead] .unique()[0]
            ttoentry = tto.TheTrade[grf.entryhead].unique()[0]
            ttotarg = tto.TheTrade[grf.targhead].unique()[0]
            ttostop = tto.TheTrade[grf.stophead].unique()[0]
            ttorr = tto.TheTrade[grf.rrhead].unique()[0]
            ttomax = tto.TheTrade[grf.maxhead].unique()[0]
            ttomstk = tto.TheTrade[grf.mstkhead].unique()[0]

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
        for tto in self.ttos:
            tto._TheTradeObject__setEntries()
            # if len(tto.df) < 4:
            #     self.fail('This test requires a longer sample of transactions to run.')
            count = 0
            x0 = tto.df.index[0]

            long = False
            r = tto.df.loc[x0]
            if len(r[rc.oc]) < 1 and (r[rc.side].startswith('B') or r[rc.side].lower().startswith('hold+')):
                long = True
            elif r[rc.oc] == 'O' and r[rc.shares] > 0 or r[rc.oc] == 'C' and r[rc.shares] < 0:
                long = True

            # side = r[rc.side]
            for i, row in tto.df.iterrows():
                count += 1
                if (long and row[rc.shares] > 0) or (not long and row[rc.shares] < 0):
                    if row[rc.price] != 0:
                        entry = 'Entry' + str(count)
                        ttoprice = tto.TheTrade[entry].unique()[0]
                        self.assertEqual(ttoprice, row.Price, "Failed to set entry correctly")
                else:
                    if row[rc.price] != 0:
                        entry = 'Exit' + str(count)
                        ttoprice = tto.TheTrade[entry].unique()[0]
                        self.assertEqual(ttoprice, row[rc.price], "Failed to set exit correctly")
                if row[rc.PL] != 0:
                    PLname = 'PL' + str(count)
                    ttopl = tto.TheTrade[PLname].unique()[0]
                    self.assertEqual(ttopl, row[rc.PL] if isNumeric(row[rc.PL]) else 0, "Failed to set pl correctly")


def main():
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


def notmain():
    unittest.main()


def reallylocal():
    TestTheTradeObject.setUpClass()
    f = TestTheTradeObject()
    f.setUp()
    f.test_TheTradeObjectSetName()
    f.test_TheTradeObjectSetAcct()
    f.test_TheTradeObjectSetSum()
    f.test_TheTradeObjectSetStart()
    f.test_TheTradeObjectSetDur()
    f.test_TheTradeObjectSetShares_and_setMarketValue()
    f.test_TheTradeObjectSetHeaders()
    f.test_TheTradeObjectSetEntries()


if __name__ == "__main__":
    notmain()
    # main()
    # reallylocal()

    # def test_SumReqFields(self):
    #     '''
    #     This class is just data. The only thing that can go wrong is to let it get
    #     out of sync which is very difficult to auto test. The real test is to visually
    #     verify the output above. Will test the data is the correct type
    #     '''
    #     srf = SumReqFields()
    #     theStyles = srf.getStyles()
    #     skiphack = ['date', 'clean', 'id']      # these keys are not found on summary form (or tfcolumns)
    #     for k in srf.rc.keys():
    #         if k in skiphack:
    #             continue
    #         value = srf.rc[k]
    #         address = srf.tfcolumns[value][0]
    #         style = srf.tfcolumns[value][1]
    #         self.assertIn(style, theStyles, f'{style} is not registered')
    #         # print("{0:12} {1:10} {2}  ".format(k, value, address))
    #         if isinstance(address, list):
    #             self.assertIsInstance(address[0], tuple)
    #             self.assertIsInstance(address[1], tuple)
    #             self.assertIsInstance(address[0][0], int)
    #             self.assertIsInstance(address[0][1], int)
    #             self.assertIsInstance(address[1][0], int)
    #             self.assertIsInstance(address[1][1], int)
    #         else:
    #             self.assertIsInstance(address[0], int)
    #             self.assertIsInstance(address[1], int)

    #     # print(self.test_SumReqFields.__doc__)
    #     self.assertEqual(len(srf.columns), len(
    #         srf.rc.keys()), "This cannot fail! FLW")
    #     # print(srf.getStyles())
    #     self.assertIn("normStyle", srf.getStyles())
    #     self.assertIn("explain", srf.getStyles())
    #     self.assertIn("normalNumberTopRight", srf.getStyles())
    #     self.assertIn("normalSubLeft", srf.getStyles())
