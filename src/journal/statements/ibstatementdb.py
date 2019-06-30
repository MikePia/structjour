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
DB archive of all ib statements
@author: Mike Petersen
@creation_data: 06/28/19
'''

import datetime as dt
import os
import sqlite3

import pandas as pd

from PyQt5.QtCore import QSettings

from journal.definetrades import ReqCol



class StatementDB:
    '''
    Methods to create and manage tables to store Activity Statements. Fields are exactly IB fields
    from activity flex query
    '''

    def __init__(self, db=None):
        '''Initialize and set the db location'''
        settings = QSettings('zero_substance', 'structjour')
        jdir = settings.value('journal')
        if not db:
            db = 'structjour_test.db'
        self.db = os.path.join(jdir, db)
        self.createTradeTables()

        self.holidays = [ 
                        ['New Year’s Day', '20180101', '20190101', '20200101', '21210101', '20220101', '20230101'],
                        ['Martin Luther King, Jr. Day', '20180115', '20190121', '20200120', '20210118', '20220117', '20230116'],
                        ['Washington’s Birthday', '20180219', '20190218',	'20200217', '20210221', '20220221', '20230220'],
                        ['Good Friday', '', '20190419', '20200410', '20210402', '20220415', '20230407'],
                        ['Memorial Day', '20180528', '20190527', '20200525', '20210531', '20220530', '20230529'],
                        ['Independence Day', '20180704', '20190704', '20200704', '20210704', '20220704', '20230704'],
                        ['Labor Day', '20180903', '20190902', '20200907', '20210906', '20220905', '20230904'], 
                        ['Thanksgiving Day', '20181122', '20191128', '20201126', '20211125', '20221124', '20231123'], 
                        ['Christmas Day', '20181225', '20191225', '20201225', '20211225', '20221225', '20231225']
        ]
        self.popHol()
        self.holidays = None
        self.covered = None
        self.rc = ReqCol()

    

    def account(self):
        '''Create account table'''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE if not exists account_information (
            id	INTEGER PRIMARY KEY AUTOINCREMENT,
            ClientAccountID TEXT, 
            AccountAlias TEXT);''')
        conn.commit()

    def createTradeTables(self):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE if not exists ib_trades (
                id	INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol	TEXT NOT NULL,
                datetime	TEXT NOT NULL,
                quantity	INTEGER NOT NULL,
                price	NUMERIC NOT NULL,
                commission	NUMERIC,
                codes	TEXT,
                account	TEXT NOT NULL,
                balance INTEGER);''')

        cur.execute('''
            CREATE TABLE if not exists ib_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
	            quantity INTEGER,
                date TEXT);''')
                

        cur.execute('''
            CREATE TABLE if not exists ib_covered (
                day	TEXT,
                covered	TEXT NOT NULL DEFAULT "false",
                PRIMARY KEY(day))''')

        cur.execute('''
            CREATE TABLE if not exists holidays(
                day TEXT,
                name TEXT)''')
        conn.commit()

        def findTrade(self, row, cur):
        cursor = cur.execute('''
            SELECT * from ib_trades where datetime = ?
            AND symbol = ?
            AND quantity = ?
            AND account = ?
            ''',
            (row['DateTime'], row['Symbol'], row['Quantity'], row['Account']))
        x = cursor.fetchall()
        if x:
            if len(x) !=1:
                print('Duplicates ? ', row['Symbol'], row['DateTime'])
            # print('. ', end='')
            return True
        # print('Adding a trade', row['Symbol'], row['DateTime'])
        return False

    def insertTrade(self, row, cur):
        '''Insert a trade. Commit not included'''
        if self.findTrade(row, cur):
            return True
        if 'Codes' in row.keys():
            codes = row['Codes']
        else:
            codes = ''
        x = cur.execute(''' 
            INSERT INTO ib_trades (symbol, datetime, quantity, price, commission, codes, account, balance)
            VALUES(?,?, ?, ?, ?, ?, ?, ?)''',
            (row['Symbol'], row['DateTime'], row['Quantity'], row['Price'], row['Commission'],
             codes, row['Account'], None))
        if x.rowcount == 1:
            return True
        return False

    def isDateCovered(self, cur, d):
        d = d.strftime("%Y%m%d")
        cursor = cur.execute('''
            SELECT * from ib_covered where day = ?
            ''', (d, ))
        x = cursor.fetchone()
        return x

    def coveredDates(self, begin, end, cur):
        delt = pd.Timedelta(days=1)
        current = begin
        if not end:
            end=current
        while current < end:
            if not self.isDateCovered(cur, current):
                d = current.strftime('%Y%m%d')
                cursor = cur.execute('''
                    INSERT INTO ib_covered(day, covered)
                    VALUES(?, ?)''',  (d, 'true'))
            current = current + delt
        # conn.commit()

    def insertPositions(self, cur, posTab):
        endDate=posTab['Date'].unique()
        assert len(endDate) == 1
        endDate = pd.Timestamp(endDate[0])
        found = cur.execute('''
            SELECT symbol, quantity, date 
                FROM ib_positions
                WHERE date = ?''', (endDate.strftime('%Y%m%d'),) )
        found = found.fetchall()
        if found:
            assert len(found) == len(posTab)
            return
        for i, row in posTab.iterrows():
            d = pd.Timestamp(row['Date']).strftime("%Y%m%d")
            cur.execute('''
                INSERT INTO ib_positions (symbol, quantity, date)
                VALUES(?, ?, ?)''',
               (row['Symbol'], row['Quantity'], d) )
        
        # cur.execute('''
        #     SELECT * FROM 
        # ''')
        

    def processStatement(self, tdf, begin, end, openPos=None):
        assert begin
        # print(begin, type(begin), end, type(end))
        assert isinstance(begin, dt.date)
        if end:
            assert isinstance(end, dt.date)

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        count = 0
        for i, row in tdf.iterrows():
            if self.insertTrade(row, cur):
                count = count + 1
        if count == len(tdf):
            self.coveredDates(begin, end, cur)
            # print('These dates are covered')
            pass
        else:
            print('Not all of those trades processed')
        self.insertPositions(cur, openPos)

        conn.commit()

    def popHol(self):
        '''
        Populat the holidays table.
        '''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        didsomething = False
        for i in range(1, 6):
            for year in self.holidays:
                cur.execute('''SELECT * from holidays where day = ?''', (year[i],))
                cursor = cur.fetchone()
                if not cursor:
                    didsomething = True
                    cur.execute('''INSERT INTO holidays (day, name)
                        VALUES(?,?)''', (year[i], year[0]))
        if didsomething:
            conn.commit()
    def isHoliday(self, d):
        if not self.holidays:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
            cur.execute('''
                SELECT day FROM holidays ORDER BY day''')
            all = cur.fetchall()
            self.holidays = [pd.Timestamp(x[0]).date() for x in all]
        d = pd.Timestamp(d).date()
        if d in self.holidays:
            return True
        return False

    def isCovered(self, d):
        d = pd.Timestamp(d).date()
        beg = end = d
        unc = self.getUncoveredDays(beg, end)
        if d in unc:
            return False
        return True

    def getStatement(self, beg, end=None):
        beg = pd.Timestamp(beg).date()

        if not end:
            end = beg
        else:
            end = pd.Timestamp(end).date()
        current = beg
        delt = pd.Timedelta(days=1)
        uncovered = self.getUncoveredDays(beg, end)
        if uncovered:
            return uncovered
        beg = pd.Timestamp(beg.year, beg.month, beg.day, 0, 0, 0)
        end = pd.Timestamp(end.year, end.month, end.day, 23, 59, 59)
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        rc=self.rc
        df = pd.DataFrame(columns=[rc.ticker, rc.date, rc.shares, rc.price, 'Commission', rc.acct,
                                   'Codes', rc.side, rc.PL])
        x = cur.execute('''
            SELECT symbol, datetime, quantity, price, commission, account, codes 
                    FROM ib_trades
                    WHERE datetime >= ?
                    AND datetime <= ?
                    ''', (beg.strftime('%Y%m%d;%H%M%S'), end.strftime('%Y%m%d;%H%M%S') ))
        for t in x:
            print(t)
        all = cur.fetchall()
        print()
        return all 


    def getUncoveredDays(self, beg='20180301', end=None, usecache=True):
        '''
        Get Market days between beg and end for which we are not covered by an IB statement
        '''
        beg = pd.Timestamp(beg).date()
        if not end:
            end = pd.Timestamp.now().date()
        else:
            end = pd.Timestamp(end).date()
        if not self.covered or usecache == False:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
            all = cur.execute('''
                SELECT day FROM ib_covered
                    WHERE covered = 'true'
                    AND day >= ?
                    AND day <= ?
                    ORDER BY day''', (beg.strftime('%Y%m%d'), end.strftime('%Y%m%d')))

            all = all.fetchall()
            self.covered = [pd.Timestamp(x[0]).date() for x in all]
        notcovered = []
        current = beg
        delt = pd.Timedelta(days=1)
        while True:
            if current.weekday() > 4 or self.isHoliday(current):
                pass
            elif current not in self.covered:
                notcovered.append(current)
            else:
                pass
                # print(f'''FOUND: {current.strftime('%A, %B %d')}''')
            current = current + delt
            if current > end:
                break
        print()
        return notcovered

    def genericTbl(self, tabname, fields):
        '''
        Create a table with an id plus all the fields in fields as TEXT
        '''
        tabname = tabname.lower().replace(' ', '_').replace(';', '')
        query = f'''
            CREATE TABLE if not exists {tabname} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,'''
        for field in fields:
            query = query + f'''
                {field} TEXT,'''

            print(query)
        query = query[:-1]
        query = query + ')'
        print(query)
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

def notmain():
    db = StatementDB()
    # zz = db.getUncoveredDays()
    # zzz = db.isCovered('2019-01-10')
    s = db.getStatement('20181203')
    if s:
        print(s)
    print()


if __name__ == '__main__':
    notmain()

