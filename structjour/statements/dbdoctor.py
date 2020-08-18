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

import logging
import os
from structjour.models.meta import ModelBase
from structjour.models.trademodels import Trade, TradeSum, Tags

from sqlalchemy import and_
from sqlalchemy.orm import aliased
import pandas as pd
# from structjour.statements.ibstatementdb import StatementDB
from PyQt5.QtCore import QSettings

# pylint: disable = C0103


class DbDoctorCrud:
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
            return None, None
        if not self.db or not os.path.exists(self.db):
            logging.warning('Database location is not set')
            return None, None
        dups = self.getDuplicateTrades(self.account)
        if not dups:
            return None, None
        logging.info(f"found {len(dups)} suspected duplicates")
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
                    trades1 = len(self.getTradesBySumId(t1['tsid']))
                    trades2 = len(self.getTradesBySumId(t2['tsid']))
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
                len_t = self.getTradesBySumId(t1['tsid'])
                if len_t:
                    len_t = len(len_t)
                    if(len_t) < 2:
                        deleteTSum = t1['tsid']
            if not deleteTrade:
                msg = f'''User must choose which to delete: {t1['id']},  {t2['id']}'''
                logging.info(msg)
            else:
                logging.info(f'{i+1}. Recommend deleting {deleteTrade}')
                if autoDelete:
                    self.deleteTradeById(deleteTrade)
            if deleteTSum:
                logging.info(f'     Delete TradeSum record {deleteTSum}')
                if autoDelete:
                    self.deleteTradeSumById(deleteTSum)
            deleteMe.append([deleteTrade, deleteTSum])
        return deleteMe, c_dups

    def deleteTradeById(self, tid):
        return Trade.deleteById(tid)

    def deleteTradeSumById(self, tid):
        return TradeSum.deleteById(tid)

    def getTradesBySumId(self, tsid):
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        q = session.query(Trade, TradeSum).filter(Trade.trade_sum_id == TradeSum.id).filter(TradeSum.id==tsid).with_entities(Trade.id).all()
        return q

    def getTradesById(self, tid):
        q = Trade.getById(tid)
        if not q:
            return None
        # Now, unfortunately, going to return the same dict that the old interface did ... maybe fix this later to return the SA obj
        t = dict()
        t['id'] = q.id
        t['sym'] = q.symb
        t['dt'] = q.datetime
        t['qty'] = q.qty
        t['bal'] = q.balance
        t['p'] = q.price
        t['avg'] = q.average
        t['pl'] = q.pnl
        t['com'] = q.commission
        t['oc'] = q.oc
        t['das'] = q.das
        t['ib'] = q.ib
        t['acct'] = q.account
        t['ts_id'] = q.trade_sum_id
        return t

    def getTradeSumById(self, tid):
        q = TradeSum.getById(tid)
        if not q:
            return q
        # TODO
        # Unfortunately, formatting to match the old interface. Definitely fix later
        t = dict()
        t['id'] = q.id
        t['name'] = q.name
        t['strat'] = q.strategy
        t['accnt'] = q.account
        t['pl'] = q.pnl
        t['start'] = q.start
        t['date'] = q.date
        t['dur'] = q.duration
        t['qty'] = q.shares
        return t

    def makeDupDict(self, dup):
        '''
        By reimplementing this for the SA SQL thing, I can avoid rewriting some gnarley stuff
        '''
        t1 = dict()
        t2 = dict()

        t1['id'] = dup['t1_id']
        t1['bal'] = dup['t1_bal']
        t1['dt'] = dup['t1_dt']
        t1['das'] = dup['t1_das']
        t1['ib'] = dup['t1_ib']
        t1['tsid'] = dup['t1_tsid']
        t1['price'] = dup['t1_price']

        t2['id'] = dup['t2_id']
        t2['bal'] = dup['t2_bal']
        t2['dt'] = dup['t2_dt']
        t2['das'] = dup['t2_das']
        t2['ib'] = dup['t2_ib']
        t2['tsid'] = dup['t2_tsid']
        t2['price'] = dup['t2_price']

        return t1, t2

    def getDuplicateTradesnew(self, account):
        '''
        Cold not figure the ORM equiivalent of a bunch of stuff here. Going to get
        a more basic select/join and then process in python 

        '''
        import math
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        t1 = aliased(Trade)
        t2 = aliased(Trade)
        pairs = session.query(t1, t2).filter(and_(
            t1.symb == t2.symb, 
            # (((t1.price - t2.price) < .00001) or ((t2.price - t1.price) < .00001)),
            # math.isclose(t1.price, t2.price, abs_tol=.00001),
            t1.datetime < t2.datetime,
            t1.account == account,
            t2.account == account, 
            t1.id != t2.id,
            # (t2.das is None) and (t1.ib == "IB")
            # (t2.das is None or t2.das == "") and (t1.ib is None or t1.ib == "")
            )).all()
        


        # q = session.query(Trade).join(t2).filter( and_(
            # substr(Trade.datetime, 1, 8) == substr(t2.datetime, 1, 8),
        #     ((Trade.das is Null or Trade.das == "") and (t2.ib is Null or t2.ib == "")) or (
        #      (Trade.ib is Null or Trade.ib == "") and (t2.das is Null and t2.das == ""))
        # )).order_by(Trade.datetime).all()
        print(q)
        print()

    def getDuplicateTrades(self, account):
        '''
        Have been unable to write a usable query using the ORM. Here it is
        in SQL
        '''
        from sqlalchemy.sql import text
        ModelBase.connect(new_session=True)
        
        conn = ModelBase.engine.connect()
        statement  =  f'''
            SELECT t.id as t1_id, t2.id as t2_id,
                    t.balance as t1_bal, t2.balance as t2_bal,
                    t.datetime as t1_dt, t2.datetime as t2_dt,
                    t.DAS as t1_das, t2.das as t2_das,
                     t.ib as t1_ib, t2.ib as t2_ib,
                    t.trade_sum_id as t1_tsid, t2.trade_sum_id as t2_tsid,
                    t.price as t1_price, t2.price as t2_price
                FROM ib_trades AS t
                    INNER  JOIN ib_trades as t2
                WHERE t.Symb = t2.symb
                AND t.Qty = t2.Qty
                AND (t.Price - t2.Price < .00001 or t2.Price - t.price < .00001)

                AND t.datetime < t2.datetime
                AND t.Account = "{account}"
                AND t.Account = t2.Account
                AND substr(t.datetime,1, 8) = substr(t2.datetime,1, 8)
                AND (((t.DAS is NULL or t.DAS = "") and (t2.IB is NULL or t2.IB = ""))
                    or ((t.IB is NULL or t.IB = "") and (t2.DAS is NULL or t2.DAS = "")))
                ORDER BY t.datetime'''
        statement = text(statement)
        result = ModelBase.engine.execute(statement)
        result = [x for x in result]
        return result
        print()
   


def notmain():
    '''Run some local code'''
    q = TradeSum.getById(1786)
    print(q.shares)

    dbdr = DbDoctorCrud()
    qq= dbdr.getTradeSumById(1786)

    # getChartsForTSID(560)
    # dbdr.getDuplicateTrades("U2429974")
    # dbdr.doDups()
    # dbdr.getTradesById(5670)


if __name__ == '__main__':
    notmain()
