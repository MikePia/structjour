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

Test methods in the class ibstatement.IbStatement
'''

import unittest
from unittest import TestCase
import pandas as pd

from structjour.statements.ibstatement import IbStatement
from structjour.statements.ibstatementdb import StatementDB

from PyQt5.QtCore import QSettings


class TestIbStatement(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestIbStatement, self).__init__(*args, **kwargs)
        self.fred = 'Fred'
        self.db = 'test/test.sqlite'
        self.apiset = QSettings('zero_substance/stockapi', 'structjour')

        # The date of file1
        self.theDate = '20191101'
        self.testfile1 = 'data/ActivityDaily.663710.20191101.csv'

        self.testfile2 = "data/flex.369463.ActivityFlexMonth.20191008.20191106.csv"

    def test_openIbStatement(self):

        ibs = IbStatement(db=self.db)
        ibdb = StatementDB(db=self.db)
        ibdb.reinitializeTradeTables()
        x = ibs.openIBStatement(self.testfile1)
        self.assertIsNotNone(x)
        self.assertIsInstance(x[0], dict)
        self.assertTrue('TRNT' in x[0].keys() or 'Trades' in x[0].keys())
        st = ibdb.getStatement(self.theDate)
        self.assertIsInstance(st, pd.DataFrame)
        self.assertGreater(len(st), 0)

    def test_openIbStatement_notcsv(self):
        ibs = IbStatement(db=self.db)
        ibdb = StatementDB(db=self.db)
        ibdb.reinitializeTradeTables()
        x = ibs.openIBStatement('data\alittleOrgTODO.txt')
        self.assertEqual(len(x[0]), 0)

    def test_fixNumericTypes(self):
        df = pd.DataFrame(data=[['2,344.78', '126.99', '3.50']], columns=['Quantity', 'Price', 'Commission'])
        df2 = pd.DataFrame(data=[['2,344.78', ]], columns=['Qty', ])
        ibs = IbStatement()
        t = ibs.fixNumericTypes(df)
        t2 = ibs.fixNumericTypes(df2)
        self.assertIsInstance(t['Quantity'].unique()[0], float)
        self.assertIsInstance(t['Price'].unique()[0], float)
        self.assertIsInstance(t['Commission'].unique()[0], float)
        self.assertIsInstance(t2['Qty'].unique()[0], float)

    def test_unifyDateFormat(self):
        ts = ('2020-03-04, 15:30:45')
        df = pd.DataFrame(data=[[ts, ]], columns=['DateTime', ])
        ibs = IbStatement()

        df = ibs.unifyDateFormat(df)
        self.assertTrue(df['DateTime'].unique()[0] == '20200304;153045')

    # def test_figureBAPL(self):
    #     pass

    # def test_openIBStatementCSV(self):
    #     # openIBStatment is now just a wrapper for openIbStatementCSV
    #     pass

    # def test_parseDefaultCSVPeriod(self):
    #     # tests = [ 'June 14, 2019', 'May 1, 2019 - June 13, 2019' '14-Jun-19']
    #     pass

    # def test_combinePartialsDefaultCSV(self):
    #     pass

    # def test_doctorDefaultCSVStatement(self):
    #     pass

    # def test_getTablesFromDefaultStatement(self):
    #     pass

    # def test_combinePartialsFlexTrade(self):
    #     pass

    # def test_cheatForBAPL(self):
    #     pass

    # def test_combineOrdersByTime(self):
    #     pass

    # def test_combinePartialsFlexCSV(self):
    #     pass

    # def test_doctorActivityFlexTrades(self):
    #     pass

    # def test_getFrame(self):
    #     pass

    # def test_doctorFlexTables(self):
    #     pass

    # def test_openActivityFlexCSV(self):
    #     pass

    # def test_getColsByTabid(self):
    #     pass

    # def test_verifyAvailableCols(self):
    #     pass


if __name__ == '__main__':
    unittest.main()
