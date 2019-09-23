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
Find and correct db errors
@author: Mike Petersen
@creation_data: 07/03/19
'''

import os
import sqlite3

import pandas as pd
# from structjour.statements.ibstatementdb import StatementDB
from PyQt5.QtCore import QSettings

# pylint: disable = C0103


class DbDoctor:
    '''
    Methods to look for discrepancies in the DB. Currently, just for finding and eliminting
    duplicate records caused by small time differences between IB and DAS transaction records.
    '''

    def __init__(self, db=None, account=None):
        '''Initialize and set the db location'''
        settings = QSettings('zero_substance', 'structjour')
        jdir = settings.value('journal')
        self.settings = settings
        if not db:
            self.db = settings.value('tradeDb', None)
        else:
            self.db = db

        if self.db:
            self.db = os.path.join(jdir, self.db)
        if account:
            self.account = account
        else:
            self.account = settings.value('account')


    def doDups(self, autoDelete=False):
        '''
        Search for duplicate trades and determine which records from ib_trades and trade_sum
        should be removed. This is called in StatementDb.processStatement with autoDelete=True
        :return: List of tuples (ib_trade_id, trade_sum_id) to remove, and the c_dups object, a
            list with info about the duplicated trades. Read with makeDupDict
        '''
        if not self.account:
            # print('You must set the account to search for trades')
            return None, None
        if not self.db or not os.path.exists(self.db):
            print('Database location is not set')
            return None, None
        dups = self.getDuplicateTrades(self.account)
        if not dups:
            return None, None
        print(f"found {len(dups)} suspected duplicates")
        print(dups[0])
        c_dups = dups.copy()
        deleteMe = list()
        for i, dup in enumerate(dups):
            # Remove from dup list if the times are 2 seconds or more different
            t1, t2 = self.makeDupDict(dup)
            t1['dt'] = pd.Timestamp(t1['dt'])
            t2['dt'] = pd.Timestamp(t2['dt'])
            delt = t1['dt'] - \
                t2['dt'] if t1['dt'] > t2['dt'] else t2['dt'] - t1['dt']
            if delt.total_seconds() > 2:
                c_dups.remove(dup)
                continue
            deleteTSum = None

            if t1['tsid'] != t2['tsid']:
                # Recommend deletion of trade if one has no associalted trade_sum_id
                deleteTrade = t1['id'] if t1['tsid'] is None else t2['id'] if t2['tsid'] is None else None

                # Else if they have different trade_sum_id and one has only one ib_trade
                # Delete the single association along with the tradeSum record
                if not deleteTrade:
                    trades1 = len(self.getTradesForTSID(t1['tsid']))
                    trades2 = len(self.getTradesForTSID(t2['tsid']))
                    if trades1 == 1 and trades2 > 1:
                        deleteTrade = t1['id']
                        deleteTSum = t1['tsid']
                    elif trades2 == 1 and trades1 > 1:
                        deleteTrade = t2['id']
                        deleteTSum = t2['tsid']
                    else:
                        raise ValueError('Programmer Exception. How does this happen and what should I do?')

            # Else if they have the same assocaiated trade_sum_id,
            # recommend deletion of the DAS  ('Keep the broker version')
            else:
                deleteTrade = t1['id'] if t1['das'] == 'DAS' else t2['id']
                len_t = self.getTradesForTSID(t1['tsid'])
                if len_t:
                    len_t = len(len_t)
                    if(len_t) < 2:
                        deleteTSum = t1['tsid']
            if not deleteTrade:
                print('No clue which to  delete ', t1['id'], t2['id'])
            else:
                print(f'{i+1}. Recommend deleting {deleteTrade}')
                if autoDelete:
                    self.deleteTradeById(deleteTrade)
            if deleteTSum:
                print(f'     Delete TradeSum record {deleteTSum}')
                if autoDelete:
                    self.deleteTradeSumById(deleteTSum)
            deleteMe.append([deleteTrade, deleteTSum])
        return deleteMe, c_dups


    def deleteTradeById(self, tid):
        '''
        Leaving off the commit till Im nearly done programming it
        '''
        # dbd = DbDoctor()
        # x = dbd.db
        # print(x)
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cursor = cur.execute('''DELETE from ib_trades WHERE id = ?''', (tid, ))
        conn.commit()
        return cursor.rowcount 

    def deleteTradeSumById(self, tid):
        '''
        Leaving off the commit till Im nearly done programming it
        '''
        # dbd = DbDoctor()
        # x = dbd.db
        # print(x)
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cursor = cur.execute('''DELETE from trade_sum WHERE id = ?''', (tid, ))
        conn.commit()
        return cursor.rowcount 

    def getChartsForTSID(self, tid):
        '''
        Retrieve the the records from the chart table that have the foreign key tid to the
        trade_sum table
        '''
        # dbd = DbDoctor()
        # x = dbd.db
        # print(x)
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cursor = cur.execute('''
            select c.id
            from trade_sum as ts
            left join chart as c on c.trade_sum_id = ts.id
            where ts.id = ?''', (tid, ))
        cursor = cursor.fetchall()
        return cursor

    def getTradesForTSID(self, tsid):
        # ibdb = DbDoctor()
        # x = ibdb.db
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cursor = cur.execute('''
            select t.id
            from trade_sum as ts
            left join ib_trades as t on t.trade_sum_id = ts.id
            where ts.id = ?''', (tsid,))
        cursor = cursor.fetchall()
        return cursor

    def getTradesByID(self, tid):
        '''
        Get the trade and return a dict
        '''
        # ibdb = DbDoctor()
        # x = ibdb.db
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cursor = cur.execute('''
            select *
            from ib_trades
            where id = ?''', (tid,))
        cursor = cursor.fetchone()
        t = dict()
        if cursor:
            (t['id'], t['sym'], t['dt'], t['qty'], t['bal'], t['p'], t['avg'],
            t['pl'], t['com'], t['oc'], t['das'], t['ib'], t['acct'], t['ts_id']) = cursor
            return t

        return None

    def getTradeSumByID(self, tid):
        '''
        Get the trade and return a dict
        '''
        # ibdb = DbDoctor()
        # x = ibdb.db
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cursor = cur.execute('''
            select id, Name, Strategy, Account, PnL, Start, Date, Duration, Shares
            from trade_sum
            where id = ?''', (tid,))
        cursor = cursor.fetchone()
        t = dict()
        if cursor:
            (t['id'], t['name'], t['strat'], t['accnt'], t['pl'],
            t['start'], t['date'], t['dur'], t['qty']) = cursor
            return t

        return None

    def getTicketsWoTrades(self, account, theDate):
        # ibdb = DbDoctor()
        # x = ibdb.db
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cursor = cur.execute('''
            select id from ib_trades
                where trade_sum_id is NULL
                and Account = ? 
                and datetime > ?
                order by datetime''', (account, theDate))
        cursor = cursor.fetchall()
        print(cursor)

    def makeDupDict(self, dup):
        '''
        Create 2 dicts for the data returned from getDuplicateTrades query
        '''
        t1 = dict()
        t2 = dict()
        (t1['id'], t2['id'],
        t1['bal'], t2['bal'],
        t1['dt'], t2['dt'],
        t1['das'], t1['ib'],
        t2['das'], t2['ib'],
        t1['tsid'], t2['tsid']) = dup
        return t1, t2

    def getDuplicateTrades(self, account):
        '''
        Find duplicate trades in which one was created by a DAS export  the other 
        by an IB Statement. Price, Qty and day are the same. In most the Balance 
        is the same. In all verified dups, the time differs by 1 second.
        This is not an exact science. Make a utility  to alert the user and let
        them verify
        Need a way to mark a trade a non dup-tho it passes all these tests...
        '''
        # ibdb = DbDoctor()
        # x = ibdb.db
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cursor = cur.execute('''
            SELECT t.id, t2.id,
                    t.Balance, t2.Balance,
                    t.datetime, t2.datetime, 
                    t.DAS, t.IB, t2.DAS, t2.IB,
                    t.trade_sum_id, t2.trade_sum_id
                FROM ib_trades AS t
                    INNER  JOIN ib_trades as t2
                WHERE t.Symb = t2.symb
                AND t.Qty = t2.Qty
                AND t.Price = t2.Price
            
                AND t.datetime < t2.datetime
                AND t.Account = ?
                AND t.Account = t2.Account
                AND substr(t.datetime,1, 8) = substr(t2.datetime,1, 8)
                AND (((t.DAS is NULL or t.DAS = "") and (t2.IB is NULL or t2.IB = ""))
                    or ((t.IB is NULL or t.IB = "") and (t2.DAS is NULL or t2.DAS = "")))
                ORDER BY t.datetime''', (account, ))

        cursor = cursor.fetchall()
        if not cursor:
            return None
        return cursor


def notmain():
    '''Run some local code'''

    # getChartsForTSID(560)
    # getTradesForTSID(560)
    # getTicketsWoTrades("U2429974", "201811")
    dbdr = DbDoctor()
    dbdr.doDups(autoDelete=True)
    print()


if __name__ == '__main__':
    notmain()
