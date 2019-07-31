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

from journal.definetrades import FinReqCol
from journal.statements import findfiles as ff
from journal.statements.ibstatementdb import StatementDB
from journal.statements.ibstatement import IbStatement
# pylint: disable = C0103

class Test_StatementDB(unittest.TestCase):
    '''
    Test functions and methods in the ibstatementdb module
    '''
    def __init__(self, *args, **kwargs):
        super(Test_StatementDB, self).__init__(*args, **kwargs)
        self.settings = QSettings('zero_substance', 'structjour')
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        self.db = "testdb.db"
        jdir = self.settings.value('journal')

        self.fulldb = os.path.join(jdir, self.db)

    def test_StatementDB(self):
        '''Test table creation'''
        StatementDB(self.fulldb)
        conn = sqlite3.connect(self.fulldb)
        cur = conn.cursor()
        x = cur.execute('''SELECT name FROM sqlite_master WHERE type='table'; ''')
        x = x.fetchall()
        tabnames = ['holidays', 'ib_trades', 'ib_positions', 'ib_covered']
        self.assertTrue(set(tabnames).issubset(set([y[0] for y in x])))

    def clearTables(self):
        conn = sqlite3.connect(self.fulldb)
        cur = conn.cursor()
        cur.execute('''delete from ib_trades''')
        cur.execute('''delete from ib_positions''')
        cur.execute('''delete from ib_covered''')
        conn.commit()


    def test_insertTrade(self):
        '''
        Test the method insertTrade. Verifys that it inserts a trade and then, with an
        identical trade, it does not insert the trade
        '''
        row = dict()
        row['Symbol'] = 'AAPL'
        row['DateTime'] = '20190101;123045'
        row['Quantity'] = 450
        row['Price'] = 205.43
        row['Commission'] = .75
        row['Codes'] = 'O'
        row['Account'] = 'U1234567'
        row['Balance'] = 450
        row['Average'] = 205.43
        row['PL'] = 0

        ibdb = StatementDB(self.db)

        self.clearTables()
        conn = sqlite3.connect(self.fulldb)
        cur = conn.cursor()
        ibdb.insertTrade(row, cur)
        conn.commit()

        x = cur.execute('''SELECT count() from ib_trades ''')
        x = x.fetchone()
        
        self.assertEqual(x[0], 1)
            
        ibdb.insertTrade(row, cur)
        conn.commit()
        x = cur.execute('''SELECT count() from ib_trades ''')
        x = x.fetchone()
        self.assertEqual(x[0], 1)
        self.clearTables()

    def openStuff(self, allofit=None):
        '''Site specific testing stuff-- open a multi  day statement'''

        # Site specific stuff here Open a monthly or yearly statemnet into the test db 
        bdir = ff.getBaseDir()
        fs = ff.findFilesInDir(bdir, 'U242.csv', True)
        ibs = IbStatement(db=self.db)
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
        ibdb = StatementDB(self.db)
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

    def test_getStatementDays(self):
        '''
        Test the method StatementDB.getStatementDays. Exercises getUncovered. Specifically test that
        when it returns data, it has the correct fields required in FinReqCol. And the the trades
        all occur within the specified dates (this tests on a single day). There is no good way to
        test that we have all available trades beyond opening statemnets/DAS exports and looking.
        '''
        frc = FinReqCol()
        ibs, x = self.openStuff()
        current = ibs.endDate
        ibdb = StatementDB(db=self.db)
        days = list(pd.date_range(start=current-pd.Timedelta(days=21), end=current))
        days.sort(reverse=True)
        for day in days:
            if day.weekday() > 4 or ibdb.isHoliday(current):
                continue
            s = ibdb.getStatementDays(ibs.account, beg=day)
            if not s.empty:
                cols = [frc.ticker, frc.date, frc.shares, frc.bal, frc.price,
                        frc.avg, frc.comm, frc.acct, frc.oc, frc.PL]
                self.assertTrue(set(cols) == set(list(s.columns)))
                for daDate  in s[frc.date].unique():
                    self.assertEqual(day.date(), pd.Timestamp(daDate).date())


def main():
    unittest.main()

def notmain():
    t = Test_StatementDB()
    # t.test_getUncoveredDays()
    t.test_getStatementDays()


if __name__ == '__main__':
    # notmain()
    main()