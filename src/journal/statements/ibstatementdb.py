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
import math
import os
import sqlite3

import pandas as pd

from PyQt5.QtCore import QSettings

from journal.definetrades import FinReqCol

# pylint: disable = C0103



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
        self.rc = FinReqCol()
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
        rc = self.rc
        cur.execute(f'''
            CREATE TABLE if not exists ib_trades (
                id	INTEGER PRIMARY KEY AUTOINCREMENT,
                {rc.ticker}	TEXT NOT NULL,
                datetime	TEXT NOT NULL,
                {rc.shares}	INTEGER NOT NULL,
                {rc.bal} INTEGER NOT NULL,
                {rc.price}	NUMERIC NOT NULL,
                {rc.avg} NUMERIC,
                {rc.PL} NUMERIC,
                {rc.comm}	NUMERIC,
                {rc.oc}	TEXT,
                {rc.acct}	TEXT NOT NULL);''')

        cur.execute('''
            CREATE TABLE if not exists ib_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account TEXT NOT NULL,
                symbol TEXT NOT NULL,
	            quantity INTEGER NOT NULL,
                date TEXT NOT NULL);''')
                

        cur.execute('''
            CREATE TABLE if not exists ib_covered (
                day	TEXT NOT NULL,
                account TEXT NOT NULL,
                covered	TEXT NOT NULL DEFAULT "false",
                PRIMARY KEY(day, account))''')

        cur.execute('''
            CREATE TABLE if not exists holidays(
                day TEXT NOT NULL,
                name TEXT)''')
        conn.commit()

    def findTrades(self, datetime, symbol, quantity, price,  account, cur=None):
        rc = self.rc
        if not cur:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
        cursor = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg}, {rc.PL}, {rc.acct}
                FROM ib_trades
                    WHERE datetime = ?
                    AND {rc.ticker} = ?
                    AND {rc.price} = ?
                    AND {rc.shares} = ?
                    AND {rc.acct} = ?
            ''',
            (datetime, symbol, price, quantity, account))
        x = cursor.fetchall()
        if x:
            return x
        # print('Adding a trade', row['Symbol'], row['DateTime'])
        return False

    def findTrade(self, datetime, symbol, price, quantity, balance, account, cur=None):
        rc = self.rc
        if not cur:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
        cursor = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg}, {rc.PL}, {rc.acct}
                FROM ib_trades
                    WHERE datetime = ?
                    AND {rc.ticker} = ?
                    AND {rc.price} = ?
                    AND {rc.shares} = ?
                    AND {rc.bal} = ?
                    AND {rc.acct} = ?
            ''',
            (datetime, symbol, price, quantity, balance, account))
        x = cursor.fetchall()
        if x:
            if len(x) !=1:
                print('Duplicates ? ', symbol, datetime)
            # print('. ', end='')
            return x
        # print('Adding a trade', row['Symbol'], row['DateTime'])
        return False

    def insertTrade(self, row, cur):
        '''Insert a trade. Commit not included'''
        rc = self.rc
        if self.findTrade(row['DateTime'], row[rc.ticker], row[rc.price], row[rc.shares], row[rc.bal], row[rc.acct], cur):
            return True
        if rc.oc in row.keys():
            codes = row[rc.oc]
        else:
            codes = ''
        x = cur.execute(f''' 
            INSERT INTO ib_trades ({rc.ticker}, datetime, {rc.shares}, {rc.price}, {rc.comm}, {rc.oc}, {rc.acct}, {rc.bal}, {rc.avg}, {rc.PL})
            VALUES(?,?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (row[rc.ticker], row['DateTime'], row[rc.shares], row[rc.price], row[rc.comm],
             codes, row[rc.acct], row[rc.bal], row[rc.avg], row[rc.PL]))
        if x.rowcount == 1:
            return True
        return False

    def isDateCovered(self, cur, account, d):
        '''
        Test if date d is covered in the given account
        '''
        d = d.strftime("%Y%m%d")
        cursor = cur.execute('''
            SELECT * from ib_covered 
                WHERE day = ?
                AND account = ?
                ''', (d, account))
        x = cursor.fetchone()
        return x

    def coveredDates(self, begin, end, account, cur=None):
        '''
        Inserts the dates between begin and end  into the ib_covered table
        '''
        if not cur:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
        delt = pd.Timedelta(days=1)
        begin = pd.Timestamp(begin).date()
        current = begin
        if not end:
            end=current
        else:
            end = pd.Timestamp(end).date()
        while current <= end:
            if not self.isDateCovered(cur, account, current):
                d = current.strftime('%Y%m%d')
                cursor = cur.execute('''
                    INSERT INTO ib_covered(day, covered, account)
                    VALUES(?, ?, ?)''',  (d, 'true', account))
            current = current + delt
        # conn.commit()

    def insertPositions(self, cur, posTab):
        '''
        Stores the daily positions. Each statement can have only one day of positions. That is the
        existing positions after close on the end day of the statemnet
        '''
        if posTab is None or not posTab.any()[0]:
            return
        assert len(posTab['Date'].unique()) == 1
        for i, row in posTab.iterrows():
            d = pd.Timestamp(row['Date']).strftime("%Y%m%d")
            found = cur.execute('''
                SELECT symbol, quantity, date 
                    FROM ib_positions
                    WHERE account = ?
                    AND symbol = ?
                    AND date = ?''',
                    (row['Account'], row['Symbol'], d) )
            found = found.fetchall()
            if not found:
                cur.execute('''
                    INSERT INTO ib_positions (account, symbol, quantity, date)
                    VALUES(?, ?, ?, ?)''',
                (row['Account'], row['Symbol'], row['Quantity'], d) )
        
    def reFigureAPL(self, cur, begin, end):
        '''
        Its sketchy still
        Process the ib_trades.balance field for all trade entries between begin and end
        :prerequisites: Balance-- the differenc between refigureBAPL and this one.
        '''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        rc = self.rc
        found = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg}, {rc.PL}, {rc.acct} FROM ib_trades
            WHERE {rc.avg} IS NULL
        ''')
        badTrades = found.fetchall()
        for badTrade in badTrades:
            bt = dict()
            bt['sym'], bt['dt'], bt['qty'], bt['bal'], bt['p'], bt['avg'], bt['pl'], bt['act'] = badTrade
            dbTrade = self.findTrade(bt['dt'], bt['sym'],bt['p'], bt['qty'], bt['bal'], bt['act'], cur)
            if dbTrade and dbTrade[0][5]:
                print('Already fixed this one', dbTrade)
                continue
            symbol = bt['sym']
            account = bt['act']

            prevTrades = cur.execute(f'''
                SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg}, {rc.PL}, {rc.acct} FROM ib_trades
                    WHERE {rc.ticker} = ?
                    AND datetime < ?
                    AND {rc.acct} = ?
                    ORDER BY datetime DESC
                ''', (symbol, bt['dt'], account))
            prevTrades = prevTrades.fetchall()
            fixthese = []
            for prevTrade in prevTrades:
                pt = dict()
                pt['sym'], pt['dt'], pt['qty'], pt['bal'], pt['p'], pt['avg'], pt['pl'], pt['act'] = prevTrade
                uncovered = self.getUncoveredDays(account, beg=pt['dt'], end=bt['dt'])
                if uncovered:
                    break
                else:
                    # We have continuous coverage...
                    # We can update badTrade if we found a trade that has either
                    # 1) both average and PL (PL tells us if we are long or short-(closing trade)) 
                    # or 2) A trade opener identified by quantity == balance
                    # print()
                    LONG = True
                    SHORT = False
                    
                    # if pt['avg'] and pt['qty'] == pt['bal']:
                    if pt['avg'] and pt['bal'] == pt['qty']:
                        fixthese.append(prevTrade)
                        fixthese.insert(0, badTrade)
                        fixthese = reversed(fixthese)

                        #######
                        balance = 0
                        #Discriminator for first opening transaction
                        pastPrimo = False
                        side = LONG
                        
                        for fixthis in fixthese:
                            ft = dict()
                            ft['sym'], ft['dt'], ft['qty'], ft['bal'], ft['p'], ft['avg'], ft['pl'], ft['act'] = fixthis


                            # Figure Balance first -- adjust offset for overnight
                            # for i, row in tdf.iterrows():
                            # quantity = ft['qty']
                            prevBalance = balance
                            balance = balance + ft['qty']

                            if not ft['bal']:
                                cur.execute(f'''
                                    UPDATE ib_trades SET {rc.bal} = ?
                                        WHERE {rc.ticker} = ?
                                        AND datetime = ?
                                        AND {rc.shares} = ?
                                        AND {rc.acct} = ?''', (balance, ft['sym'], pt['dt'], pt['qty'], pt['act']))
                                # side = LONG if quantity >= 0 else SHORT
                                ft['bal'] = balance

                            

                            # Check for a flipped position. The flipper is figured like Opener; the average
                            # changes, and no PL is taken 
                            if pastPrimo and side == LONG and balance < 0:
                                side = SHORT
                            elif pastPrimo and side == SHORT and balance > 0:
                                side = LONG

                            # This the first trade Open; average == price and set the side- 
                            if not pastPrimo and ft['bal'] == ft['qty']:
                                
                                pastPrimo = True
                                average = ft['p']
                                assert math.isclose(ft['p'], ft['avg'], abs_tol=1e-5)

                                #average should be set for this one
                                # tdf.at[i, 'Average'] = average
                                side = LONG if ft['qty'] >= 0 else SHORT

                            # Here are openers -- adding to the trade; average changes
                            # newAverage = ((prevAverage * prevBalance) + (quantity * price)) / balance
                            elif (pastPrimo and side is LONG and ft['qty'] >= 0) or (
                                pastPrimo and side is SHORT and ft['qty'] < 0):
                                newAverage = ((average * prevBalance) + (ft['qty'] * ft['p'])) / ft['bal']
                                average = newAverage

                                if not ft['avg']:

                                    cur.execute(f'''
                                        UPDATE ib_trades SET {rc.avg} = ?
                                            WHERE {rc.ticker} = ?
                                            AND datetime = ?
                                            AND {rc.shares} = ?
                                            AND {rc.acct} = ?''', (average, ft['sym'], ft['dt'], ft['qty'], ft['act']))


                            # Here are closers; PL is figured and check for trade ending
                            elif pastPrimo:
                                # Close Tx, P/L is figured on CLOSING transactions only
                                pl = (average - ft['p']) * ft['qty']
                                x = cur.execute(f'''
                                    UPDATE ib_trades SET {rc.avg} = ?, {rc.PL} = ?
                                        WHERE {rc.ticker} = ?
                                        AND datetime = ?
                                        AND {rc.shares} = ?
                                        AND {rc.acct} = ?''', (average, pl, ft['sym'], ft['dt'], ft['qty'], ft['act']))
                                if ft['bal'] == 0:
                                    pastPrimo = False
                            else:
                                # This should be a first trade for this statmenet/Symbol. Could be Open or
                                # Close. We are lacking the previous balance so cannot reliably figure the
                                # average.
                                print(f'''There is a  trade for {ft['sym']} that lacks a transaction in this statement''')
                        conn.commit()
                        break
                            #######
                    elif pt['avg'] and pt['pl']:
                        fixthese.append(prevTrade)
                        fixthese.insert(0, badTrade)
                        fixthese_r = reversed(fixthese)
                        average = None
                        for fixthis in fixthese_r:
                            print(fixthis)
                            ft = dict()
                            ft['sym'], ft['dt'], ft['qty'], ft['bal'], ft['p'], ft['avg'], ft['pl'], ft['act'] = fixthis
                            if ft['pl']:
                                side = LONG if ft['qty'] < 0 else SHORT
                                balance = ft['bal']
                                average = ft['avg']
                            elif average and not ft['avg']:
                                # Opener
                                # newAverage = ((prevAverage * prevBalance) + (quantity * price)) / balance 
                                if (side is LONG and ft['qty'] >= 0) or (
                                    side is SHORT and ft['qty'] < 0):
                                    newAverage = ((average * balance) + (ft['qty'] * ft['p'])) / ft['bal']
                                    average = newAverage
                                    balance = ft['bal']
                                    cur.execute(f'''
                                    UPDATE ib_trades SET {rc.avg} = ?
                                        WHERE {rc.ticker} = ?
                                        AND datetime = ?
                                        AND {rc.shares} = ?
                                        AND {rc.acct} = ?''', (average, ft['sym'], ft['dt'], ft['qty'], ft['act']))
                                # Closer. Enter PL and check for last trade
                                elif average:
                                    pl = (average - ft['p']) * ft['qty']
                                    x = cur.execute(f'''
                                        UPDATE ib_trades SET {rc.avg} = ?, {rc.PL} = ?
                                            WHERE {rc.ticker} = ?
                                            AND datetime = ?
                                            AND {rc.shares} = ?
                                            AND {rc.acct} = ?''', (average, pl, ft['sym'], ft['dt'], ft['qty'], ft['act']))
                                    if ft['bal'] == 0:
                                        average = None
                            elif ft['avg']:
                                average = ft['avg']
                                prevBalance = ft['bal']
                                # raise ValueError('Programmer exception to find the statements')
                            else:
                                raise ValueError('What else we got here?')
                        conn.commit()




                                



                        break
                    else:
                        fixthese.append(prevTrade)

    def processStatement(self, tdf, account, begin, end, openPos=None):
        '''
        Processs the trade, positions, ancd covered tables using the Trades table and the 
        OpenPositions table.
        '''
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
            self.coveredDates(begin, end, account, cur)
        else:
            print('Not all of those trades processed')
        self.insertPositions(cur, openPos)
        conn.commit()
        self.reFigureAPL(cur, begin, end)

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
        '''Returns T or F is given day is a market holiday
        '''
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

    def isCovered(self, account, d):
        '''
        returns True or False if this day is covered in the db. It is True if we have processed a
        Statement that covers this day. There may be no trades on a covered day.
        '''
        d = pd.Timestamp(d).date()
        beg = end = d
        unc = self.getUncoveredDays(account, beg, end)
        if d in unc:
            return False
        return True

    def getStatement(self, account, beg, end=None):
        '''
        Retrieve all the trades for the given days.
        :account:
        :beg:
        :end:
        :return: If not all days are covered return empty list. Otherwise return a df with all
                 trades inclusive of the days beg and end, column names drawn from FinReqCol)
        '''
        beg = pd.Timestamp(beg).date()
        eformat = '%Y%m%d;%H%M%S'
        bformat = '%Y%m%d'
        rc = self.rc

        if not end:
            end = pd.Timestamp(beg.year, beg.month, beg.day, 23, 59, 59)
        else:
            end = pd.Timestamp(end.year, end.month, end.day, 23, 59, 59)
        beg = beg.strftime(bformat)
        end = end.strftime(eformat)
        uncovered = self.getUncoveredDays(account, beg, end, usecache=False)
        if uncovered:
            return []
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cols = [rc.ticker, rc.date, rc.shares, rc.bal, rc.price, rc.avg, rc.comm, rc.acct,
                rc.oc, rc.PL]
        x = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg},
            {rc.comm}, {rc.acct}, {rc.oc}, {rc.PL}
                    FROM ib_trades
                    WHERE datetime >= ?
                    AND datetime <= ?
                    ''', (beg, end))
        x = x.fetchall()
        if x:
            df = pd.DataFrame(data=x, columns=cols)
            return df
        # print()
        return pd.DataFrame()

    def getUncoveredDays(self, account, beg='20180301', end=None, usecache=True):
        '''
        Get Market days between beg and end for which we are not covered by an IB statement.
        :account:
        :beg:
        :end:
        :usecache: Use the default True is this is to be called repeatedly to check the same dates.
                   Use usecache=False to check for unique dates.
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
                    AND account = ?
                    ORDER BY day''', (beg.strftime('%Y%m%d'), end.strftime('%Y%m%d'), account))

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
        # print()
        return notcovered

    def getMissingCoverage(self, account):
        '''Get all the missing market days between the min and max covered days'''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute('''SELECT min(day), max(day) 
            FROM ib_covered
            WHERE account = ?''', (account,))
        days = cur.fetchone()
        if days:
            uncovered = self.getUncoveredDays(account, days[0], days[1])
            return {'min': pd.Timestamp(days[0]).date(), 
                    'max': pd.Timestamp(days[1]).date(),
                    'uncovered': uncovered}
        # print()
        
    def getTradesByDates(self, account, sym, daMin, daMax):
        '''
        Get trades between  times min and max for a ticker/account
        '''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        rc = self.rc
        cur.execute('''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal} FROM ib_trades
                WHERE {rc.acct} = ?
                AND {rc.ticker} = ?
                AND datetime >= ?
                AND datetime <= ?
                ORDER BY datetime''', (account, sym, daMin, daMax))
        found = cur.fetchall()
        return found

def notmain():
    settings = QSettings('zero_substance', 'structjour')
    account = settings.value('account')
    db = StatementDB()
    # zz = db.getUncoveredDays(account)
    # zzz = db.isCovered('account'2019-01-10')
    missingdict = db.getMissingCoverage(account)
    print('Beginning', missingdict['min'])
    print('Ending', missingdict['max'])
    print('Missing', missingdict['uncovered'])
    print()
if __name__ == '__main__':
    notmain()

