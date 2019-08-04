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
from journal.stock.utilities import isNumeric

# pylint: disable = C0103

class StatementDB:
    '''
    Methods to create and manage tables to store Activity Statements. Fields are exactly IB fields
    from activity flex query
    '''

    def __init__(self, db=None, source=None):
        '''Initialize and set the db location'''
        settings = QSettings('zero_substance', 'structjour')
        jdir = settings.value('journal')
        if not db:
            db = 'structjour_test.db'
        self.source = source
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
                {rc.shares}	INTEGER NOT NULL CHECK({rc.shares} != 0),
                {rc.bal} INTEGER,
                {rc.price}	NUMERIC NOT NULL,
                {rc.avg} NUMERIC,
                {rc.PL} NUMERIC,
                {rc.comm}	NUMERIC,
                {rc.oc}	TEXT,
                DAS TEXT,
                IB TEXT,
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

        cur.execute('''
            CREATE TABLE if not exists chart(
                id	INTEGER,
                symb INTEGER,
                name TEXT NOT NULL,
                start TEXT NOT NULL,
                end TEXT NOT NULL,
                interval INTEGER,
                PRIMARY KEY(id))''')

        cur.execute('''
            CREATE TABLE if not exists entries (
                ib_trades_id INTEGER UNIQUE,
                trade_sum_id INTEGER,
                open_close TEXT NOT NULL,
                diff NUMERIC NOT NULL,
                PRIMARY KEY(ib_trades_id, trade_sum_id),
                FOREIGN KEY(ib_trades_id) REFERENCES ib_trades(id),
                FOREIGN KEY(trade_sum_id) REFERENCES trade_sum(id))''') 

        cur.execute('''

            CREATE TABLE if not exists trade_sum (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                strategy TEXT,
                link1 NUMERIC,
                pnl NUMERIC,
                start TEXT NOT NULL UNIQUE,
                duration INTEGER NOT NULL,
                shares INTEGER NOT NULL,
                mktval NUMERIC NOT NULL,
                target NUMERIC,
                targdiff NUMERIC,
                stoploss NUMERIC,
                sldiff NUMERIC,
                rr NUMERIC,
                maxloss NUMERIC,
                mstkval NUMERIC,
                mstknote TEXT,
                explain TEXT,
                notes TEXT,
                clean TEXT,
                chart1_id INTEGER,
                chart2_id INTEGER,
                chart3_id INTEGER,
                FOREIGN KEY(chart1_id) REFERENCES chart(id),
                FOREIGN KEY(chart2_id) REFERENCES chart(id),
                FOREIGN KEY(chart3_id) REFERENCES chart(id))''')
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

    def findTrade(self, datetime, symbol, quantity, account, cur=None):
        rc = self.rc
        if not cur:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
        cursor = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg}, {rc.PL}, {rc.acct}
                FROM ib_trades
                    WHERE datetime = ?
                    AND {rc.ticker} = ?
                    AND {rc.shares} = ?
                    AND {rc.acct} = ?
            ''',
            (datetime, symbol, quantity, account))
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
        if self.findTrade(row['DateTime'], row[rc.ticker], row[rc.shares], row[rc.acct], cur):
            return True
        if rc.oc in row.keys():
            codes = row[rc.oc]
        else:
            codes = ''
        das = None
        ib = None
        if self.source == 'DAS':
            das = 'DAS'
        elif self.source == 'IB':
            ib = 'IB'
        x = cur.execute(f''' 
            INSERT INTO ib_trades ({rc.ticker}, datetime, {rc.shares}, {rc.price}, {rc.comm},
                                   {rc.oc}, {rc.acct}, {rc.bal}, {rc.avg}, {rc.PL}, DAS, IB)
            VALUES(?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (row[rc.ticker], row['DateTime'], row[rc.shares], row[rc.price], row[rc.comm],
             codes, row[rc.acct], row[rc.bal], row[rc.avg], row[rc.PL], das, ib))
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
                cur.execute('''
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

    ########################################################################################
    ############################ methods for structjour ####################################
    ########################################################################################
    
    def getNumTicketsforDay(self, day, account='all'):

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        day = pd.Timestamp(day)
        begin = day.strftime('%Y%m%d')
        end = day.strftime('%Y%m%d;99')
        count = 0
        if account == 'all':
            count = cur.execute(f'''
            SELECT count() FROM ib_trades
                where datetime > ?
                and datetime < ?
            ''', (begin, end))
        else:
            count = cur.execute(f'''
                SELECT count() FROM ib_trades
                where datetime > ?
                and datetime < ?
                and Account = ?
            ''', (begin, end, account))
        if count:
            count = count.fetchone()[0]
        return count

    
    ########################################################################################
    #################### DB Helper methods for refigureAPL #################################
    ########################################################################################

    def DBfigureUnbalancedPL(self, cur, prevTrades, bt):
        '''
        A secondary attempt to get balance for the badTrade bt. bt has a PL but lacks
        balance.
        First set it as a closer and set the average (just incase).
        Look for an adjacent previous opener  (set average and open) and if the averages of 
            that opener == price (within a tolerance) set balances

        Programming note: This is similar to refigureAPL_backwards. Can they combine? share code?
        '''
        rc = self.rc
        pTrades = [self.makeTradeDict(x) for x in prevTrades]
        tdict = pTrades.copy()
        tdict.append(bt)

        # Going to iterate backwards from most recent to previous.
        tdict = list(reversed(tdict))

        LONG = True
        SHORT = False

        # First trade in the list is the last trade chronologically
        postOmega = False
        for i in range(len(tdict)):
            if not postOmega:
                # First trade is a closer or this was called in error, figure out the average
                # average = (pl/qty) + price
                assert isNumeric(tdict[0][rc.PL]) and tdict[0][rc.PL] != 0
                tdict[0][rc.oc] = 'C'
                average = (tdict[0][rc.PL] / tdict[0][rc.shares]) + tdict[0][rc.price]
                tdict[0][rc.avg] = average

                side = LONG if tdict[0][rc.shares] < 0 else SHORT
                postOmega = True

            elif (postOmega and side == LONG and tdict[i][rc.shares] > 0) or (
                    postOmega and side == SHORT and tdict[i][rc.shares] < 0):
                # opener
                # If just before a closer, then the average is shared
                if tdict[i-1][rc.oc] == 'C':
                    tdict[i][rc.oc] = 'O'
                    tdict[i][rc.avg] = average
                # If the average==price, this is the trade opener (for our purposes)
                # and we can now set all the balances
                if math.isclose(tdict[i][rc.price], average, abs_tol=1e-2):
                    # Found a Trade beginning opener balance = quantity
                    # TODO don't leave this in.
                    raise ValueError('Programming note: Not sure what I was thinking here.')
                    balance = tdict[i][rc.shares]
                    tdict[i][rc.bal] = balance
                    for j in range(i-1, -1, -1):
                        balance = balance - tdict[j+1][rc.shares]
                        if j == 0:
                            self.updateAvgBalPlOC(cur, tdict[j], tdict[j][rc.avg], balance,
                                                  tdict[j][rc.PL], tdict[j][rc.oc])
                            return True
        return False

    def makeTradeDict(self, atrade):
        '''
        A convenience to ensure the trade dictionaries are all the same. The arbitrary order
        is set specifically from the db query
        '''
        rc = self.rc
        t = dict()
        (t[rc.ticker], t[rc.date], t[rc.shares], t[rc.bal], t[rc.price], t[rc.avg], t[rc.PL],
         t[rc.acct], t[rc.oc], t['id'], t[rc.comm]) = atrade
        return t

    def getBadTrades(self):
        '''
        Retrive all trades in ib_trades missing either average or balance
        '''
        rc = self.rc
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        rc = self.rc
        found = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg},
            {rc.PL}, {rc.acct}, {rc.oc}, id, {rc.comm} FROM ib_trades
                WHERE {rc.avg} IS NULL
                OR {rc.bal} IS NULL
        ''')
        badTrades = found.fetchall()
        return badTrades

    def getPreviousTrades(self, cur, t):
        '''
        Given the trade bt, retrieve the previou trades from the same symbol/account
        :cur: A cursor
        :bt: Dict representing a trade containing keys for symbol, date and account
        '''
        rc = self.rc
        prevTrades = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg},
            {rc.PL}, {rc.acct}, {rc.oc}, id, {rc.comm} FROM ib_trades
                WHERE {rc.ticker} = ?
                AND datetime < ?
                AND {rc.acct} = ?
                ORDER BY datetime DESC
                ''', (t[rc.ticker], t[rc.date], t[rc.acct]))
        prevTrades = prevTrades.fetchall()
        return prevTrades

    def getNextTrades(self, cur, t):
        '''
        Given the trade bt, retrieve the next trades from the same symbol/account
        :cur: A cursore
        :t: Dict representing a trade containing keys for symbol, date and account
        '''
        rc = self.rc
        prevTrades = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg},
            {rc.PL}, {rc.acct}, {rc.oc}, id, {rc.comm} FROM ib_trades
                WHERE {rc.ticker} = ?
                AND datetime > ?
                AND {rc.acct} = ?
                ORDER BY datetime
                ''', (t[rc.ticker], t[rc.date], t[rc.acct]))
        prevTrades = prevTrades.fetchall()
        return prevTrades

    def updateBal(self, cur, atrade, balance):
        '''
        DB update ib_trades balance
        '''
        cur.execute(f''' UPDATE ib_trades SET {self.rc.bal} = ?
                WHERE  id = ?''', (balance, atrade['id']))

    def updateAvgOC(self, cur, atrade, average, oc):
        '''
        DB update ib_trades for average and OpenClose
        '''
        rc = self.rc
        cur.execute(f'''UPDATE ib_trades SET {rc.avg} = ?, {rc.oc} = ?
                WHERE id = ?''', (average, oc, atrade['id']))

    def updateAvgPlOC(self, cur, atrade, avg, pl, oc):
        '''
        DB update ib_trades for average, PnL and OpenClose
        '''
        rc = self.rc
        cur.execute(f'''UPDATE ib_trades SET {rc.avg} = ?, {rc.PL} = ?, {rc.oc} = ?
                WHERE id = ?''', (avg, pl, oc, atrade['id']))

    def updateAvgBalPlOC(self, cur, atrade, avg, bal, pl, oc):
        '''
        DB update ib_trades for average, balance, PnL and OpenClose
        '''
        rc = self.rc
        cur.execute(f'''UPDATE ib_trades SET {rc.avg} = ?, {rc.bal} = ?, {rc.PL} = ?, {rc.oc} = ?
                WHERE id = ?''', (avg, bal, pl, oc, atrade['id']))

    def reFigureAPL(self, begin, end):
        '''
        Its sketchy still
        Process the ib_trades.balance field for all trade entries between begin and end
        :prerequisites: Balance-- the differenc between refigureBAPL and this one.
        '''
        rc = self.rc
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        badTrades = self.getBadTrades()
        for badTrade in badTrades:
            bt = self.makeTradeDict(badTrade)

            if isNumeric([bt[rc.avg], bt[rc.bal]]):
                print('Already fixed this one', bt)
                continue
            symbol = bt[rc.ticker]
            account = bt[rc.acct]
            prevTrades = self.getPreviousTrades(cur, bt)

            fixthese = []
            for i, prevTrade in enumerate(prevTrades):
                pt = self.makeTradeDict(prevTrade)
                uncovered = self.getUncoveredDays(account, beg=pt[rc.date], end=bt[rc.date])
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

                    # if pt[rc.avg] and pt[rc.shares] == pt[rc.bal]:
                    if pt[rc.avg] and pt[rc.bal] == pt[rc.shares]:
                        # Found Trade opener good trade
                        fixthese.append(prevTrade)
                        fixthese.insert(0, badTrade)
                        fixthese_r = reversed(fixthese)

                        #######
                        balance = 0
                        #Discriminator for first opening transaction
                        pastPrimo = False
                        side = LONG

                        for fixthis in fixthese_r:
                            ft = self.makeTradeDict(fixthis)

                            # Figure Balance first -- adjust offset for overnight
                            prevBalance = balance
                            balance = balance + ft[rc.shares]

                            if not ft[rc.bal]:
                                self.updateBal(cur, ft, balance)
                                ft[rc.bal] = balance

                            # Check for a flipped position. The flipper is figured as an Opener;
                            # the average changes, and no PL is taken.
                            if pastPrimo and side == LONG and balance < 0:
                                side = SHORT
                            elif pastPrimo and side == SHORT and balance > 0:
                                side = LONG

                            # This the first trade Open; average == price and set the side-
                            if not pastPrimo and ft[rc.bal] == ft[rc.shares]:

                                pastPrimo = True
                                average = ft[rc.price]
                                assert math.isclose(ft[rc.price], ft[rc.avg], abs_tol=1e-5)

                                #average should be set for this one
                                # tdf.at[i, 'Average'] = average
                                side = LONG if ft[rc.shares] >= 0 else SHORT

                            # Here are openers -- adding to the trade; average changes
                            # newAvg = ((prevAverage * prevBalance) + (quantity * price)) / balance
                            elif (pastPrimo and side is LONG and ft[rc.shares] >= 0) or (
                                    pastPrimo and side is SHORT and ft[rc.shares] < 0):
                                newAverage = ((average * prevBalance) + (ft[rc.shares] * ft[rc.price])) / ft[rc.bal]
                                average = newAverage
                                ft[rc.oc] = 'O'
                                if not ft[rc.avg]:
                                    ft[rc.avg] = average
                                    self.updateAvgOC(cur, ft, average, 'O')


                            # Here are closers; PL is figured and check for trade ending
                            elif pastPrimo:
                                # Close Tx, P/L is figured on CLOSING transactions only
                                pl = (average - ft[rc.price]) * ft[rc.shares]
                                ft[rc.oc] = 'C'
                                self.updateAvgPlOC(cur, ft, average, pl, 'C')
                                if ft[rc.bal] == 0:
                                    pastPrimo = False
                            else:
                                print('or else')
                        conn.commit()
                        break
                            #######
                    elif isNumeric([pt[rc.avg], pt[rc.PL], pt[rc.bal]]) and pt[rc.PL] != 0:
                        # Found a good closer (has PL and avg)
                        fixthese.append(prevTrade)
                        fixthese.insert(0, badTrade)
                        fixthese_r = reversed(fixthese)

                        average = None
                        nextTrade = False
                        pastPrimo = False
                        for fixthis in fixthese_r:
                            print(fixthis)
                            ft = self.makeTradeDict(fixthis)

                            if pastPrimo and not isNumeric(ft[rc.bal]):
                                 ### Has the balance variable been set????
                                prevBalance = balance
                                balance = balance + ft[rc.shares]
                                self.updateBal(cur, ft, balance)
                                # side = LONG if quantity >= 0 else SHORT
                                ft[rc.bal] = balance

                            if isNumeric([ft[rc.PL], ft[rc.bal], ft[rc.avg]]) and (
                                    ft[rc.PL] != 0 and not pastPrimo):
                                # found a good trade closer
                                pastPrimo = True
                                side = LONG if ft[rc.shares] < 0 else SHORT
                                balance = ft[rc.bal]
                                average = ft[rc.avg]
                                if ft[rc.bal] == 0:
                                    # Found a trade ender
                                    nextTrade = True
                            elif nextTrade:
                                # This is a baginning trade opener. We know because it was
                                # preceeded by bal==0, fix and DB UPDATE
                                nextTrade = False
                                ft[rc.oc] = 'O'
                                if not ft[rc.bal] or math.isnan(ft[rc.bal]):
                                    ft[rc.bal] = ft[rc.shares]
                                else:
                                    assert ft[rc.bal] == ft[rc.shares]

                                if not ft[rc.avg] or math.isnan(ft[rc.avg]):
                                    ft[rc.avg] = ft[rc.price]
                                else:
                                    assert math.isclose(ft[rc.avg], ft[rc.price], abs_tol=1e-5)
                                average = ft[rc.avg]
                                prevBal = ft[rc.bal]
                                pl = 0
                                self.updateAvgBalPlOC(cur, ft, average, ft[rc.bal], pl, 'O')
                                nextTrade = False
                                break
                            elif average and not ft[rc.avg]:
                                # A badTrade -

                                if (side is LONG and ft[rc.shares] >= 0) or (
                                        side is SHORT and ft[rc.shares] < 0):
                                    # Opener
                                    # newAverage = ((prevAverage * prevBalance) +
                                    #                (quantity * price)) / balance
                                    newAverage = ((average * balance) + (
                                        ft[rc.shares] * ft[rc.price])) / ft[rc.bal]
                                    average = newAverage
                                    balance = ft[rc.bal]
                                    ft[rc.avg] = average
                                    ft[rc.oc] = 'O'
                                    self.updateAvgOC(cur, ft, average, 'O')
                                elif average:
                                    # Closer. Enter PL and check for last trade --
                                    pl = (average - ft[rc.price]) * ft[rc.shares]
                                    ft[rc.oc] = 'C'
                                    # if ft[rc.bal] == 0:
                                    #     average = None
                                    self.updateAvgPlOC(cur, ft, average, pl, 'C')
                                    break
                            elif ft[rc.avg]:
                                average = ft[rc.avg]
                                prevBalance = ft[rc.bal]
                                # raise ValueError('Programmer exception to find the statements')
                            else:
                                raise ValueError('What else we got here?')
                        conn.commit()
                        break
                    elif i == len(prevTrades) -1 and isNumeric(bt[rc.PL]) and bt[rc.PL] != 0:
                        # This catches a badTrade if the conditions above have failed (end of
                        # prevTrades) and the badTrade has a PL. Its possible we can figure out the
                        # some of the rest of the details by comparing average price to previous
                        # average price, or the previous price, if the average price is mssing
                        # there too. This algo was worke out in DASStatement.figureUnbalancedPL
                        # (incase its possible to generalize this and share code.)
                        print("are we there yt?")
                        if self.DBfigureUnbalancedPL(cur, prevTrades, bt):
                            conn.commit()
                            break
                    else:
                        fixthese.append(prevTrade)
        self.reFigureAPL_backwards()

    def reFigureAPL_backwards(self):
        '''
        A second algorithm to try to fill in some blanks. A bad trade is missing average and/or
        balance.
        A trade where balance == shares can set avg = price and is an opener (OC = O).
        A trade with a PL value != 0  is a closer and we can figure average. An adjacent and
            previous opener will have the same average.
        '''
        rc = self.rc
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        LONG = True
        SHORT = False

        badTrades = self.getBadTrades()
        for badTrade in badTrades:
            bt = self.makeTradeDict(badTrade)
            nextTrades = self.getNextTrades(cur, bt)
            fixthese = [bt]
            nextTrades = [self.makeTradeDict(x) for x in nextTrades]
            # pastPrimo = False
            for nt in nextTrades:
                uncovered = self.getUncoveredDays(bt[rc.acct], bt[rc.date], nt[rc.date])
                if uncovered:
                    break
                fixthese.append(nt)
            for i, ft in enumerate(fixthese):
                if isNumeric(ft[rc.bal]) and ft[rc.shares] == ft[rc.bal]:
                    print('Got the balance of a future trade with no uncovered days')
                    if not isNumeric(ft[rc.avg]):
                        ft[rc.avg] = ft[rc.price]
                        ft[rc.oc] = 'O'
                        self.updateAvgOC(cur, ft, ft[rc.avg], ft[rc.oc])
                        conn.commit()
                        return
                elif isNumeric(ft[rc.PL]) and ft[rc.PL] != 0:
                    # pastPrimo = True
                    average = ((ft[rc.PL] / ft[rc.shares]) + ft[rc.price])
                    if not ft[rc.avg] or not isNumeric(ft[rc.avg]):
                        ft[rc.avg] = average
                    else:
                        assert math.isclose(average, ft[rc.avg], abs_tol=1e-2)
                    ft[rc.oc] = 'C'
                    # side = LONG if ft[rc.shares] < 0 else SHORT
                    if isNumeric(ft[rc.bal]):
                        balance = ft[rc.bal]
                        for j in range(i-1, -1, -1):
                            balance = balance - fixthese[j+1][rc.shares]
                            self.updateBal(cur, fixthese[j], balance)
                            if j == 0:
                                conn.commit()
                                return

    def processStatement(self, tdf, account, begin, end, openPos=None):
        '''
        Processs the trade, positions, ancd covered tables using the Trades table and the
        OpenPositions table.
        '''
        rc = self.rc
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
            accounts = tdf[rc.acct].unique()
            for account in accounts:
                self.coveredDates(begin, end, account, cur)
        else:
            print('Not all of those trades processed')
        self.insertPositions(cur, openPos)
        conn.commit()
        self.reFigureAPL(begin, end)

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
            days = cur.fetchall()
            self.holidays = [pd.Timestamp(x[0]).date() for x in days]
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

    def getStatement(self, day, account='all'):
        '''
        Get the trades from a single day
        :day: A date string or timestamp. The day to retrieve trades from.min
        :account: Fill in to retrieve trades from only one account
        '''
        rc = self.rc
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        day = pd.Timestamp(day)
        begin = day.strftime('%Y%m%d')
        end = day.strftime('%Y%m%d;99')
        trades = None
        if account == 'all':
            trades = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg},
                   {rc.PL}, {rc.acct}, {rc.oc}, id, {rc.comm} FROM ib_trades
                where datetime > ?
                and datetime < ?
            ''', (begin, end))
        else:
            trades = cur.execute(f'''
                SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg},
                       {rc.PL}, {rc.acct}, {rc.oc}, id, {rc.comm} FROM ib_trades
                    where datetime > ?
                    and datetime < ?
                    and Account = ?
            ''', (begin, end, account))
        if trades:
            trades = trades.fetchall()
        return trades

    def getStatementDays(self, account, beg, end=None):
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
                rc.oc, rc.PL, 'id']
        x = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg},
            {rc.comm}, {rc.acct}, {rc.oc}, {rc.PL},  id
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

    def getUncoveredDays(self, account, beg='20180301', end=None, usecache=False):
        '''
        Get Market days between beg and end for which we are not covered by an IB statement.
        :account:
        :beg:
        :end:
        :usecache: Use the default True is this is to be called repeatedly to check the same dates.
                   Use usecache=False to check for unique dates.
        '''
        if not beg:
            raise ValueError('Missing a value for beg. beg must have a value')
        beg = pd.Timestamp(beg)
        if not end:
            end = pd.Timestamp.now()
        else:
            end = pd.Timestamp(end)
        if not self.covered or not usecache:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
            strbeg = beg.strftime('%Y%m%d')
            strend = end.strftime('%Y%m%d')
            days = cur.execute('''
                SELECT day FROM ib_covered
                    WHERE covered = 'true'
                    AND day >= ?
                    AND day <= ?
                    AND account = ?
                    ORDER BY day''', (strbeg, strend, account))

            days = days.fetchall()
            self.covered = [pd.Timestamp(x[0]).date() for x in days]
        notcovered = []
        current = beg.date()
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
            if current > end.date():
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
        if days and days[0]:
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
    '''Run some local code for devel'''
    settings = QSettings('zero_substance', 'structjour')
    account = settings.value('account')
    db = StatementDB()
    # zz = db.getUncoveredDays(account)
    # zzz = db.isCovered('account'2019-01-10')
    missingdict = db.getMissingCoverage(account)
    if missingdict:
        print('Beginning', missingdict['min'])
        print('Ending', missingdict['max'])
        print('Missing', missingdict['uncovered'])
    print()

def local():
    '''Run some local code for devel'''
    d = pd.Timestamp('2018-12-03')
    e = pd.Timestamp('2018-12-31')
    print(d.strftime("%B, %A %d %Y"))
    db = StatementDB()
    # df = db.getStatementDays('U2429974', d, e)
    x = db.getNumTicketsforDay(d)
    print(x, "tickets")

def main():
    '''Tun some local code for devel'''
    x = StatementDB()
    print()

if __name__ == '__main__':
    # notmain()
    # local()
    main()
