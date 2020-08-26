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
@author: Mike Petersen

@creation_date: 2019-07-10

Test methods in the class ibstatementdb.StatementDB.  Need to yet devise tests for
processStatement and refigureAPL (Still sketchy).
'''

import os
import sqlite3
import unittest

import pandas as pd
from PyQt5.QtCore import QSettings
from sqlalchemy.sql import text

from structjour.colz.finreqcol import FinReqCol
from structjour.definetrades import DefineTrades
from structjour.models.meta import ModelBase
from structjour.statements import findfiles as ff
from structjour.statements.ibstatement import IbStatement
from structjour.statements.ibstatementdb import StatementDB
from structjour.thetradeobject import runSummaries
from structjour.utilities.backup import Backup

# from structjour.dfutil import DataFrameUtil

# from structjour.view.layoutforms import LayoutForms

# from structjour.colz.finreqcol import FinReqCol


class Test_StatementDB(unittest.TestCase):
    '''
    Test functions and methods in the ibstatementdb module
    '''
    def __init__(self, *args, **kwargs):
        super(Test_StatementDB, self).__init__(*args, **kwargs)
        self.settings = QSettings('zero_substance', 'structjour')


    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))

    def test_findTradeSummarySA(self):
        '''
        Test findTradeSummary, a helper method for addTradeSummaries and updateTradeSummaries.
        Note that one of those needs to have run and succeeded inorder to test this method.
        '''
        infile = "data/flex.369463.ActivityFlexMonth.20191008.20191106.csv"
        theDate = pd.Timestamp('2019-10-16')

        # Create these three objects
        ibs = IbStatement()
        ibdb = StatementDB()
        ibdb.reinitializeTradeTables()
        trades = DefineTrades("DB")

        # This call loads the statement into the db
        ibs.openIBStatementCSV(infile)

        # Here is an example of processing a single day of trades (3 calls)
        # This gets a collection of trades from a single day that can become a trade_sum entry
        df = ibdb.getStatement(theDate)

        # The following method and function process the statement transactions into a collection
        # of trades where each trade is a single row representing multiple transactions
        dframe, ldf = trades.processDBTrades(df)
        tradeSummaries, ts, entries, initialImageNames = runSummaries(ldf)

        ibdb.addTradeSummariesSA(ts, ldf)

        # The test database trades_sum should now only the trades from theDate, one
        # entry per trade
        for i, trade in enumerate(tradeSummaries):
            x = ibdb.findTradeSummarySA(theDate, trade['Start'].unique()[0])
            self.assertEqual(trade['Name'].unique()[0], x.name)

        bu = Backup()
        bu.restore()

    def test_addTradeSummariesSA(self):
        '''
        Tests addTradeSummaries. The method requires trades are already in the database.
        We achieve that with openStuff.
        For this test, I load everything (openStuff) and run
        addTradeSummaries on all covered days. Its slow. Could be partially sqlite but
        all the APL BAPL stuff is probably the main crawler. In practice, this will add
        daily or monthly statements. And in running the program there is no way to run
        the trade summaries in mass. Its desinged to load up a single day. ITs day-trader
        centric. Let it stay slow for now.
        '''
        ibdb = StatementDB()
        self.clearTables()
        ibs, x = self.openStuff()
        # ibdb.getUncoveredDays
        covered = ibdb.getCoveredDays()

        for count, day in enumerate(covered):
            df = ibdb.getStatement(day)
            if not df.empty:
                tu = DefineTrades("DB")
                dframe, ldf = tu.processDBTrades(df)
                tradeSummaries, ts, entries, initialImageNames = runSummaries(ldf)
                ibdb.addTradeSummariesSA(ts, ldf)
                summaries = ibdb.getTradeSumByDateSA(day)
                for summary in summaries:
                    entryTrades = ibdb.getEntryTradesSA(summary.id)
                    self.assertGreater(len(entryTrades), 0)

                break   # Use this to just test addTradeSummaries once
        bu = Backup()
        bu.restore()

    def test_findTrade(self):
        '''
        Tests find a unique trade using findTrade with date, ticker, shares and account.
        The method is meant to be more exclusive than inclusive.
        '''
        rc = FinReqCol()

        ibdb = StatementDB()
        row = {
            rc.ticker: 'SNRK',
            "DateTime": '20191212;093145',
            rc.shares: 3000,
            rc.price: 150.23,
            rc.comm: None,
            rc.oc: 'O',
            rc.acct: "U2229999",
            rc.bal: 3000,
            rc.avg: 150.23,
            rc.PL: None,
            "DAS": 'DAS',
            "IB": None}
        data = list(row.values())
        columns = list(row.keys())
        x = pd.DataFrame(data=[data], columns=columns)
        ibdb.insertTradeSA(x.iloc[0])
        ModelBase.session.commit()
        # conn.commit()
        foundit = ibdb.findTradesSA(x.iloc[0]['DateTime'], x.iloc[0][rc.ticker], x.iloc[0][rc.shares], x.iloc[0][rc.acct])
        self.assertTrue(foundit)
        bu = Backup()
        bu.restore()

    def test_insertPositions(self):
        '''
        This is not used by anything anymore. might delete insertPositions
        In making this test, I have discovered that stuctjour never uses this database table.
        When the info is needed, the program checks the statement or export file. hmmm ....
        The data in the active db has 339 rows between 20181231 and 20200122.
        '''
        pass
        # data = [['XXXXXXX', 'GOG', -349, '20170304'], ['XXXXXXX', 'ORNG', 550, '20170304']]

        # posTab = pd.DataFrame(data=data, columns=['Account', 'Symbol', 'Quantity', 'Date'])
        # conn = sqlite3.connect(self.db)
        # cur = conn.cursor()
        # ibdb = StatementDB(db=self.db)
        # ibdb.insertPositions(cur, posTab)
        # print()

    def test_ibstatement(self):
        '''Test basic usage loading an ib statement and getting a statement'''

        infile = "data/flex.369463.ActivityFlexMonth.20191008.20191106.csv"
        theDate = pd.Timestamp('2019-10-16')

        # Create these two objects
        ibs = IbStatement()
        ibdb = StatementDB()
        ibdb.reinitializeTradeTables()

        # This call loads the statement into the db
        ibs.openIBStatementCSV(infile)

        # This call will then retrieve one day of trades as a dataframe. theDate is string or timestamp
        df2 = ibdb.getStatement(theDate)
        self.assertIsInstance(df2, pd.DataFrame)
        self.assertFalse(df2.empty)
        bu = Backup()
        bu.restore()

    def test_StatementDB(self):
        '''Test table creation called from __init__'''
    
        ibdb = StatementDB()
        tns_expected = ['api_keys', 'chart', 'daily_notes', 'description', 'holidays', 'ib_covered',
               'ib_positions', 'ib_trades', 'images', 'inspire', 'links', 'migrate_model',
               'source', 'sqlite_sequence', 'strategy', 'tags', 'trade_sum', 'trade_sum_tags']
        tns = ibdb.tcrud.getTableNames()
        print(set(tns))
        self.assertEqual(set(tns_expected), set(tns))

    def test_popHol(self):
        ModelBase.connect(new_session=True)
        statement = text('delete from holidays')
        ModelBase.engine.execute(statement)
        ibdb = StatementDB()
        for holiday in ibdb.holidays:
            for day in holiday[1:]:
                if day:
                    self.assertTrue(ibdb.tcrud.isHoliday(day))



    def clearTables(self):
        statements = ['''delete from chart''',
                      '''delete from holidays''',
                      '''delete from ib_covered''',
                      '''delete from ib_trades''',
                      '''delete from ib_positions''',
                      '''delete from trade_sum'''
        ]
        ModelBase.connect(new_session=True)
        for statement in statements:
            s = text(statement)
            result = ModelBase.engine.execute(s)

    def test_insertTrade(self):
        '''
        Test the method insertTrade. Verifys that it inserts a trade and then, with an
        identical trade, it does not insert the trade. The col DateTime requires fxn.
        '''
        rc = FinReqCol()
        row = dict()
        row[rc.ticker] = 'AAPL'
        row['DateTime'] = '20190101;123045'
        row[rc.shares] = 450
        row[rc.price] = 205.43
        row[rc.comm] = .75
        row[rc.oc] = 'O'
        row[rc.acct] = 'U1234567'
        row[rc.bal] = 450
        row[rc.avg] = 205.43
        row[rc.PL] = 0

        ibdb = StatementDB()
        self.clearTables()

        ibdb.insertTradeSA(row)
        ModelBase.session.commit()
        c = ibdb.tcrud.getTradeCount()
        self.assertEqual(c, 1)

        ibdb.insertTradeSA(row)
        ModelBase.session.commit()
        c = ibdb.tcrud.getTradeCount()
        self.assertEqual(c, 1)

        bu = Backup()
        bu.restore()

    def openStuff(self, allofit=None):
        '''Site specific testing stuff-- open a multi  day statement'''
        # Site specific stuff here Open a monthly or yearly statemnet into the test db.
        # Currently set to search the journal root dir, so it may load an annual or two.
        bdir = ff.getBaseDir()
        fs = ff.findFilesInDir(bdir, 'U242.csv', True)
        ibs = IbStatement()
        for f in fs:

            x = ibs.openIBStatement(f)
            delt = ibs.endDate - ibs.beginDate
            assert delt.days > 20
            if not allofit:
                break
        return ibs, x

    def test_getUncoveredDays(self):
        '''Tests several methods in the covered process from'''
        self.clearTables()
        ibdb = StatementDB()
        ibs, x = self.openStuff()
        delt = ibs.endDate - ibs.beginDate
        assert delt.days > 20

        begin = ibs.endDate - pd.Timedelta(days=15)
        end = ibs.endDate + pd.Timedelta(days=15)
        covered = ibdb.getUncoveredDays(ibs.account, begin, end)
        self.assertTrue(len(covered) > 0)
        for c in covered:
            self.assertTrue(c > ibs.endDate)
            self.assertTrue(c <= end)
        bu = Backup()
        bu.restore()



def main():
    unittest.main()


def notmain():
    t = Test_StatementDB()
    # t.test_addTradeSummariesSA()
    # t.test_findTrade()
    # t.test_findTradeSummarySA()
    # t.test_getUncoveredDays()
    # t.test_ibstatement()
    # t.test_insertPositions()
    # t.test_insertTrade()
    # t.test_popHol()
    # t.test_getStatementDays()
    t.test_StatementDB()


if __name__ == '__main__':
    notmain()
    # main()
