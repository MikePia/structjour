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
import logging
import math
import os
import sqlite3

import pandas as pd
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import inspect
from sqlalchemy.sql import text

from structjour.colz.finreqcol import FinReqCol
from structjour.models.meta import ModelBase
from structjour.models.trademodels import Charts
from structjour.statements.dbdoctor import DbDoctorCrud
from structjour.statements.findfiles import getDirectory
from structjour.statements.statementcrud import TradeCrud
from structjour.stock.utilities import qtime2pd
from structjour.thetradeobject import SumReqFields
from structjour.utilities.util import isNumeric

# pylint: disable = C0103


class StatementDB:
    '''
    Methods to create and manage tables to store Activity Statements. Fields are exactly IB fields
    from activity flex query
    '''

    def __init__(self, db=None, source=None):
        '''Initialize and set the db location'''
        settings = QSettings('zero_substance', 'structjour')
        # jdir = settings.value('journal')
        self.settings = settings
        self.db = None
        if not db:
            db = self.settings.value('tradeDb')
        else:
            db = db
        if db:
            self.db = db
        if not self.db:
            title = 'Warning'
            msg = ('<h3>Database files have not been set</h3>'
                   '<p>Please set a valid location when calling setDB or you may select or '
                   'create a new location by selecting file->filesettings</p>')
            msgbx = QMessageBox(QMessageBox.Warning, title, msg, QMessageBox.Ok)
            msgbx.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))
            msgbx.exec()
            return

        self.source = source
        self.rc = FinReqCol()
        self.sf = SumReqFields()
        self.tcrud = TradeCrud()

        self.holidays = [
                        ['New Year’s Day', '20180101', '20190101', '20200101', '21210101', '20220101', '20230101'],
                        ['Martin Luther King, Jr. Day', '20180115', '20190121', '20200120', '20210118', '20220117', '20230116'],
                        ['Washington’s Birthday', '20180219', '20190218', '20200217', '20210221', '20220221', '20230220'],
                        ['Good Friday', '', '20190419', '20200410', '20210402', '20220415', '20230407'],
                        ['Memorial Day', '20180528', '20190527', '20200525', '20210531', '20220530', '20230529'],
                        ['Independence Day', '20180704', '20190704', '20200704', '20210704', '20220704', '20230704'],
                        ['Labor Day', '20180903', '20190902', '20200907', '20210906', '20220905', '20230904'],
                        ['Thanksgiving Day', '20181122', '20191128', '20201126', '20211125', '20221124', '20231123'],
                        ['Christmas Day', '20181225', '20191225', '20201225', '20211225', '20221225', '20231225']
        ]
        self.popHol()
        self.covered = None

    def reinitializeTradeTables(self):
        '''
        This is intended for testing code only. Be sure the db either
        has a backup or is initialized to a test db.
        '''
        statements = ['DROP TABLE IF EXISTS ib_covered', 'DROP TABLE IF EXISTS ib_positions',
                      'DROP TABLE IF EXISTS ib_trades', 'DROP TABLE IF EXISTS holidays',
                      'DROP TABLE IF EXISTS chart', 'DROP TABLE IF EXISTS chart_sum',
                      'DROP TABLE IF EXISTS entries', 'DROP TABLE IF EXISTS trade_sum',
                      'DROP TABLE IF EXISTS date_start']
        ModelBase.connect(new_session=True)
        for statement in statements:
            ModelBase.engine.execute(text(statement))

    def makeTradeSumDict(self, ts):
        '''
        :ts: a trade_sum record as retrieved by getTradeSumBy... methods
        '''
        ts = self.renameKeys(ts.__dict__)
        return ts

    def findTradeSummarySA(self, date, start):
        '''
        A helper method for addTradeSummariesSA and updateTradeSummaries
        Get a single trade summary record by date and time
        :date: A Date string or Timestamp for the date to find.
        :start: A Time string or Timestamp for the time to find
        :return: The found record as a tuple or False
        '''
        sf = self.sf

        date = pd.Timestamp(date)
        date = date.strftime("%Y%m%d")
        start = pd.Timestamp(start)
        start = start.strftime("%H:%M:%S")
        return  self.tcrud.findTradeSummary(date, start)

    def formatDate(self, daDate, frmt='%Y%m%d'):
        '''
        Format the date into a string for uniform DB format
        '''
        daDate = pd.Timestamp(daDate)
        daDate = daDate.strftime(frmt)
        return daDate

    def formatTime(self, daTime, frmt='%H:%M:%S'):
        '''
        Format the time into a string for uniform DB format
        '''
        daTime = pd.Timestamp(daTime)
        daTime = daTime.strftime(frmt)
        return daTime

    def findChart(self, cur, ts_id, slot):
        '''
        FInd the charts related to a trade summary record for each of three slots
        '''
        cursor = cur.execute('''SELECT * from chart WHERE trade_sum_id = ? and slot = ?''',
                             (ts_id, slot))
        cursor = cursor.fetchone()
        return cursor

    def addChart(self, ts):
        '''
        symb, path, name, source, start, end, interval, slot, trade_sum_id
        '''
        pass

    def updateChartsSA(self, tradesum, trade):
        '''
        Helper method for updateTradeSummaries. Not intended for api use
        '''
        sf = self.sf
        trade_sum_id = int(tradesum.id)
        name = tradesum.name
        ticker = name.split(' ')[0]

        chartSA =  Charts()
        chartSA.symb = ticker
        chartSA.name = name
        chartSA.trade_sum_id = trade_sum_id
        for i in range(0, 3):
            chart = 'chart' + str(i + 1)
            start = chart + 'Start'
            end = chart + 'End'
            interval = chart + 'Interval'
            chart = trade[chart].unique()[0]
            start = trade[start].unique()[0]
            end = trade[end].unique()[0]
            start = qtime2pd(start)
            end = qtime2pd(end)

            chartSA.start = self.formatDate(start, frmt='%Y%m%d;%H%M%S')
            chartSA.end = self.formatDate(end, frmt='%Y%m%d;%H%M%S')
            chartSA.interval = int(trade[interval].unique()[0])
            chartSA.path, chartSA.name = os.path.split(chart)
            chartSA.slot = i+1
            self.tcrud.updateChart(trade_sum_id, chartSA,  i+1)

    def updateEntriesSA(self, tsid, tdf):
        self.tcrud.updateEntries(tsid, tdf)

    def getEntryTradesSA(self, tsid):
        ''' Get the transactions (ib_trades) related to a trade (trade_sum) by trade_sum_id. '''

        return self.tcrud.getEntryTrades(tsid)

    def doctorTheTrade(self, trade):
        '''
        Basically this fixes up my stuff (developer) and should be unnecessary by release time
        Fix up the legacy objects (which is every object that was ever saved as an
        object [currently 8/8/19]).
        '''
        sf = self.sf
        if sf.date not in trade.columns:
            theDate = self.settings.value('theDate')
            theDate = qtime2pd(theDate)
            theDate = theDate.strftime("%Y%m%d")
            trade[sf.date] = theDate
        if sf.clean not in trade.columns:
            trade[sf.clean] = ''
        if sf.id not in trade.columns:
            trade[sf.id] = None

        if sf.pl not in trade.columns:
            if 'P / L' in trade.columns:
                trade = trade.rename(columns={'P / L': sf.pl})
        if trade[sf.mktval].unique()[0] is None:
            trade[sf.mktval] = 0
        return trade

    def updateTradeSummariesSA(self, ts):
        '''
        '''
        sf = self.sf
        rc = self.rc
        newts = dict()
        for dkey in ts:
            trade = ts[dkey]
            trade = self.doctorTheTrade(trade)
            newts[dkey] = trade
            tradesum = self.tcrud.updateTradeSummary(trade)
            if not tradesum:
                continue
            trade[sf.id] = tradesum.id

            self.updateChartsSA(tradesum, trade)

        ModelBase.session.commit()
        return newts

    def addTradeSummariesSA(self, tsDict, ldf):
        '''Create DB entries in trade_sum and its relations they do not already exist'''
        # Summary Fields
        sf = self.sf
        for dkey, tdf in zip(tsDict, ldf):
            ts = tsDict[dkey]
            daDay = self.formatDate(ts[sf.date].unique()[0])
            daTime = self.formatTime(ts[sf.start].unique()[0])
            if not self.findTradeSummarySA(daDay, daTime):
                tradesum = self.tcrud.insertTradeSummary(ts)
                self.updateChartsSA(tradesum, ts)
                self.updateEntriesSA(tradesum.id, tdf)

    def findTradesSA(self, datetime, symbol, quantity, account):
        '''
        Find a unique trade for date, symbol, quantity and account. This method is here
        to prevent duplicate trades, not to get a collection of trades.
        '''
        return self.tcrud.findTrade(datetime, symbol, quantity, account)

    def insertTradeSA(self, row, update=False):
        '''
        Insert a trade into ib_trades table. Commit not included for speed.
        :params row:A pandas object that includes the headers:
            ticker, 'DateTime', shares, price, comm, acct, bal, avg, rc.PL. For the precise
            names of the headers see the required columns object self.rc

        '''
        rc = self.rc
        atrade = self.findTradesSA(row['DateTime'], row[rc.ticker], row[rc.shares], row[rc.acct])
        if atrade:
            if update:
                self.updateAvgBalPlOC_SA(atrade, row[rc.avg], row[rc.bal], row[rc.PL], row[rc.oc], new_session=False)
            return True
        return self.tcrud.insertTrade(row, self.source)

    def updateMstkValsSA(self, ts_id, val, note):
        if not ts_id:
            return
        if not conn:
            conn = sqlite3.connect(self.db)

        cur = conn.cursor()
        ts_id = int(ts_id)
        sf = self.sf
        cur.execute(f'''UPDATE trade_sum SET {sf.mstkval} = ?, {sf.mstknote} = ?
                WHERE id = ?''', (val, note, ts_id))
        conn.commit()

    def updateMstkVals(self, ts_id, val, note, conn=None):
        if not ts_id:
            return
        if not conn:
            conn = sqlite3.connect(self.db)

        cur = conn.cursor()
        ts_id = int(ts_id)
        sf = self.sf
        cur.execute(f'''UPDATE trade_sum SET {sf.mstkval} = ?, {sf.mstknote} = ?
                WHERE id = ?''', (val, note, ts_id))
        conn.commit()

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

    def coveredDatesSA(self, begin, end, account):
        '''
        Inserts the dates between begin and end  into the ib_covered table
        '''
        delt = pd.Timedelta(days=1)
        begin = pd.Timestamp(begin).date()
        current = begin
        end = pd.Timestamp(end).date() if end else current
        while current <= end:
            if not self.tcrud.isDateCovered(account, current):
                d = current.strftime('%Y%m%d')
                self.tcrud.insertCovered(account, d)
            current = current + delt

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
            end = current
        else:
            end = pd.Timestamp(end).date()
        while current <= end:
            if not self.isDateCovered(cur, account, current):
                d = current.strftime('%Y%m%d')
                cur.execute('''
                    INSERT INTO ib_covered(day, covered, account)
                    VALUES(?, ?, ?)''', (d, 'true', account))
            current = current + delt
        # conn.commit()

    def insertPositions(self, cur, posTab):
        '''
        This table is not being used 1/29/20. Will review its need with next iteration of db.
        A helper for processStatement to create an entry in the positions table
        Stores the daily overnight positions. Each statement can have only one day of positions.
        The regulation is not enforced here but in processStatment.
        Multiday statments make this entry unnecessary for all but the end day. That is the
        existing positions after close on the end day of the statement. Likewise, consecutive
        days of statements make this information unnecessary (but possibly rednudant) for all
        but the 'outside' day before a missing day.
        :params cur: a database cursor
        :params posTab: A data frame with the headers 'Account', 'Symbol', 'Quantity'  'Date. It could
            be retrieved from broker statement, created from a DAS export of positions window
            (or just created for testing).
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
                    (row['Account'], row['Symbol'], d))
            found = found.fetchall()
            if not found:
                cur.execute('''
                    INSERT INTO ib_positions (account, symbol, quantity, date)
                    VALUES(?, ?, ?, ?)''',
                (row['Account'], row['Symbol'], row['Quantity'], d))

    ########################################################################################
    # ########################### methods for structjour ###################################
    ########################################################################################

    def getNumTicketsForDay(self, day, account='all'):
        '''
        Queries the database to get the count of transactions recorded from a single day.
        By default will retrieve the tickets from all accouts.
        :param day: str or timestamp. The day to query
        :param all: str, send an account number to restrict to a single account
        :return: int
        '''

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        day = pd.Timestamp(day)
        begin = day.strftime('%Y%m%d')
        end = day.strftime('%Y%m%d;99')
        count = 0
        countt = 0
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
            count = count.fetchone()
            count = count[0] if count else 0

        countt = cur.execute('''
            SELECT count() FROM trade_sum
                WHERE Date = ?''', (begin, ))
        if countt:
            countt = countt.fetchone()
            countt = countt[0] if countt else 0
        return count, countt

    def updateTSID(self, t_id, ts_id):
        '''
        Update the tsid in the ib_trades record
        :params t_id: Trade id from the ib_trades table
        :params ts_id: Trade summary id from the trade_sums table (foreign key) relation to ib_trades
        '''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        ts_id = int(ts_id)

        cursor = cur.execute(f'''
            SELECT trade_sum_id FROM ib_trades WHERE id = ?''', (t_id, ))
        theId = cursor.fetchone()
        if not isNumeric(theId[0]) or theId[0] != ts_id:
            cur.execute(f''' UPDATE ib_trades SET trade_sum_id = ?
                WHERE  id = ?''', (ts_id, t_id))
            conn.commit()

    ########################################################################################
    # ################### DB Helper methods for refigureAPL ################################
    ########################################################################################

    def DBfigureUnbalancedPL_SA(self, prevTrades, bt):
        '''
        A secondary attempt to get balance for the badTrade bt. bt has a PL but lacks
        balance.
        First set it as a closer and set the average (just incase).
        Look for an adjacent previous opener  (set average and open) and if the averages of
            that opener == price (within a tolerance) set balances

        Programming note: This is similar to refigureAPL_backwards. Can they combine? share code?
        '''
        pTrades = [x.__dict__.copy() for x in prevTrades]
        pTrades.append(bt.__dict__.copy())

        # Going to iterate backwards from most recent to previous.
        tdict = list(reversed(pTrades))

        LONG = True
        SHORT = False

        # First trade in the list is the last trade chronologically
        postOmega = False
        for i in range(len(tdict)):
            if not postOmega:
                # First trade is a closer or this was called in error, figure out the average
                # average = (pl/qty) + price
                assert isNumeric(tdict[0]['pnl']) and tdict[0]['pnl'] != 0
                tdict[0]['oc'] = 'C'
                average = (tdict[0]['pnl'] / tdict[0]['qty']) + tdict[0]['price']
                tdict[0]['average'] = average

                side = LONG if tdict[0]['qty'] < 0 else SHORT
                postOmega = True

            elif (postOmega and side == LONG and tdict[i]['qty'] > 0) or (
                    postOmega and side == SHORT and tdict[i]['qty'] < 0):
                # opener
                # If just before a closer, then the average is shared
                if tdict[i - 1]['oc'] == 'C':
                    tdict[i]['oc'] = 'O'
                    tdict[i]['average'] = average
                # If the average==price, this is the trade opener (for our purposes)
                # and we can now set all the balances
                if math.isclose(tdict[i]['price'], average, abs_tol=1e-2):
                    # Found a Trade beginning opener balance = quantity
                    # TODO don't leave this in.
                    return
                    # raise ValueError('Programming note: Not sure what I was thinking here.')
                    balance = tdict[i][rc.shares]
                    tdict[i][rc.bal] = balance
                    for j in range(i - 1, -1, -1):
                        balance = balance - tdict[j + 1][rc.shares]
                        if j == 0:
                            self.updateAvgBalPlOC(cur, tdict[j], tdict[j][rc.avg], balance,
                                                  tdict[j][rc.PL], tdict[j][rc.oc])
                            return True
        return False

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
                if tdict[i - 1][rc.oc] == 'C':
                    tdict[i][rc.oc] = 'O'
                    tdict[i][rc.avg] = average
                # If the average==price, this is the trade opener (for our purposes)
                # and we can now set all the balances
                if math.isclose(tdict[i][rc.price], average, abs_tol=1e-2):
                    # Found a Trade beginning opener balance = quantity
                    # TODO don't leave this in.
                    return
                    # raise ValueError('Programming note: Not sure what I was thinking here.')
                    balance = tdict[i][rc.shares]
                    tdict[i][rc.bal] = balance
                    for j in range(i - 1, -1, -1):
                        balance = balance - tdict[j + 1][rc.shares]
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

    def getBadTradesSA(self):
        '''
        Retrive all trades in ib_trades missing either average or balance
        '''
        return self.tcrud.getBadTrades()

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

    def getPreviousTradesSA(self, bt):
        '''
        Given the trade bt, retrieve the previou trades from the same symbol/account. 
        :params bt: TradeObject
        '''
        return self.tcrud.getPreviousTrades(bt)

    def getPreviousTrades(self, cur, bt):
        '''
        Given the trade bt, retrieve the previou trades from the same symbol/account. This is
        used to find misssing position size, average and PnL.
        :cur: A cursor
        :bt: Dict representing a trade. The dict must contain keys for symbol, date and account
        '''
        rc = self.rc
        prevTrades = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg},
            {rc.PL}, {rc.acct}, {rc.oc}, id, {rc.comm} FROM ib_trades
                WHERE {rc.ticker} = ?
                AND datetime < ?
                AND {rc.acct} = ?
                ORDER BY datetime DESC
                ''', (bt[rc.ticker], bt[rc.date], bt[rc.acct]))
        prevTrades = prevTrades.fetchall()
        return prevTrades

    def getNextTradesSA(self, bt):
        '''
        Given the trade bt, retrieve the next trades from the same symbol/account
        :cur: A cursore
        :bt: Dict representing a trade containing keys for symbol, date and account
        '''
        return self.tcrud.getNextTrades(bt)

    def getNextTrades(self, cur, bt):
        '''
        Given the trade bt, retrieve the next trades from the same symbol/account
        :cur: A cursore
        :bt: Dict representing a trade containing keys for symbol, date and account
        '''
        rc = self.rc
        prevTrades = cur.execute(f'''
            SELECT {rc.ticker}, datetime, {rc.shares}, {rc.bal}, {rc.price}, {rc.avg},
            {rc.PL}, {rc.acct}, {rc.oc}, id, {rc.comm} FROM ib_trades
                WHERE {rc.ticker} = ?
                AND datetime > ?
                AND {rc.acct} = ?
                ORDER BY datetime
                ''', (bt[rc.ticker], bt[rc.date], bt[rc.acct]))
        prevTrades = prevTrades.fetchall()
        return prevTrades

    def updateBal(self, cur, atrade, balance):
        '''
        DB update ib_trades balance
        '''
        cursor = cur.execute(f'''
            SELECT {self.rc.bal} FROM ib_trades
            WHERE id = ?''', (atrade['id'], ))
        bal = cursor.fetchone()
        if not isNumeric(bal[0]):
            cur.execute(f''' UPDATE ib_trades SET {self.rc.bal} = ?
                WHERE  id = ?''', (balance, atrade['id']))
        else:
            assert balance == bal[0]

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

    def updateAvgBalPlOC_SA(self, atrade, avg, bal, pl, oc, new_session=False):
        '''
        DB update ib_trades for average, balance, PnL and OpenClose
        :params atrade: A Trade model instance
        '''
        self.tcrud.updateAvgBalPlOC(atrade, avg, bal, pl, oc, new_session)

    def updateAvgBalPlOC(self, cur, atrade, avg, bal, pl, oc):
        '''
        DB update ib_trades for average, balance, PnL and OpenClose
        :params atrade: A dict that includes the key 'id' for id value.
        '''
        rc = self.rc
        cur.execute(f'''UPDATE ib_trades SET {rc.avg} = ?, {rc.bal} = ?, {rc.PL} = ?, {rc.oc} = ?
                WHERE id = ?''', (avg, bal, pl, oc, atrade['id']))

    def reFigureAPL_SA(self, begin, end):
        '''
        Its sketchy still
        Process the ib_trades.balance field for all trade entries between begin and end
        :prerequisites: Balance-- the differenc between refigureBAPL and this one.
        '''
        badTrades = self.getBadTradesSA()
        for bt in badTrades:
            # bt = self.makeTradeDict(badTrade)

            if isNumeric([bt.average, bt.balance]):
                continue
            account = bt.account
            prevTrades = self.getPreviousTradesSA(bt)

            fixthese = []
            for i, pt in enumerate(prevTrades):
                # pt = self.makeTradeDict(prevTrade)
                uncovered = self.getUncoveredDaysSA(account, beg=pt.datetime, end=bt.datetime)
                if uncovered:
                    break
                else:
                    # We have continuous coverage...
                    # We can update badTrade if we found a trade that has either
                    # 1) both average and PL (PL tells us if we are long or short-(closing trade))
                    # or 2) A trade opener identified by quantity == balance
                    LONG = True
                    SHORT = False

                    # if pt[rc.avg] and pt[rc.shares] == pt[rc.bal]:
                    if pt.average and pt.balance == pt.qty:
                        # Found Trade opener good trade
                        fixthese.append(pt)
                        fixthese.insert(0, bt)
                        fixthese_r = reversed(fixthese)

                        #######
                        balance = 0
                        # Discriminator for first opening transaction
                        pastPrimo = False
                        side = LONG

                        for ft in fixthese_r:
                            # ft = self.makeTradeDict(fixthis)

                            # Figure Balance first -- adjust offset for overnight
                            prevBalance = balance
                            balance = balance + ft.qty

                            if not ft.balance:
                                ft = self.tcrud.updateBal(ft, balance)

                            # Check for a flipped position. The flipper is figured as an Opener;
                            # the average changes, and no PL is taken.
                            if pastPrimo and side == LONG and balance < 0:
                                side = SHORT
                            elif pastPrimo and side == SHORT and balance > 0:
                                side = LONG

                            # This the first trade Open; average == price and set the side-
                            if not pastPrimo and ft.balance == ft.qty:

                                pastPrimo = True
                                average = ft.price
                                assert math.isclose(ft.price, ft.average, abs_tol=1e-5)

                                # average should be set for this one
                                # tdf.at[i, 'Average'] = average
                                side = LONG if ft.qty >= 0 else SHORT

                            # Here are openers -- adding to the trade; average changes
                            # newAvg = ((prevAverage * prevBalance) + (quantity * price)) / balance
                            elif (pastPrimo and side is LONG and ft.qty >= 0) or (
                                    pastPrimo and side is SHORT and ft.qty < 0):
                                newAverage = ((average * prevBalance) + (ft.qty * ft.price)) / ft.balance
                                average = newAverage
                                ft.oc = 'O'
                                if not ft.average:
                                    ft.average = average
                                    ModelBase.session.add(ft)

                            # Here are closers; PL is figured and check for trade ending
                            elif pastPrimo:
                                # Close Tx, P/L is figured on CLOSING transactions only
                                pl = (average - ft.price) * ft.qty
                                ft.oc = 'C'
                                ModelBase.session.add(ft)
                                if ft.balance == 0:
                                    pastPrimo = False
                        ModelBase.session.commit()
                        break
                        # ######
                    elif isNumeric([pt.average, pt.pnl, pt.balance]) and pt.pnl != 0:
                        # Found a good closer (has PL and avg)
                        fixthese.append(pt)
                        fixthese.insert(0, bt)
                        fixthese_r = reversed(fixthese)

                        average = None
                        nextTrade = False
                        pastPrimo = False
                        for ft in fixthese_r:
                            # ft = self.makeTradeDict(fixthis)

                            if pastPrimo and not isNumeric(ft.balance):
                                # ## Has the balance variable been set????
                                prevBalance = balance
                                balance = balance + ft.qty
                                ft = self.tcrud.updateBal(ft, balance)
                                # side = LONG if quantity >= 0 else SHORT

                            if isNumeric([ft.pnl, ft.balance, ft.average]) and (
                                    ft.pnl != 0 and not pastPrimo):
                                # found a good trade closer
                                pastPrimo = True
                                side = LONG if ft.qty < 0 else SHORT
                                balance = ft.balance
                                average = ft.average
                                if ft.balance == 0:
                                    # Found a trade ender
                                    nextTrade = True
                            elif nextTrade:
                                # This is a baginning trade opener. We know because it was
                                # preceeded by bal==0, fix and DB UPDATE
                                nextTrade = False
                                ft.oc = 'O'
                                if not ft.balance or math.isnan(ft.balance):
                                    ft.balance = ft.qty
                                else:
                                    assert ft.balance == ft.qty

                                if not ft.average or math.isnan(ft.average):
                                    ft.average = ft.price
                                else:
                                    assert math.isclose(ft.average, ft.price, abs_tol=1e-5)
                                average = ft.average
                                # prevBal = ft[rc.bal]
                                pl = 0
                                ModelBase.session.add(ft)
                                nextTrade = False
                                break
                            elif average and not ft.average:
                                # A badTrade -

                                if (side is LONG and ft.qty >= 0) or (
                                        side is SHORT and ft.qty < 0):
                                    # Opener
                                    # newAverage = ((prevAverage * prevBalance) +
                                    #                (quantity * price)) / balance
                                    newAverage = ((average * balance) + ( ft.qty * ft.price)) / ft.balance
                                    average = newAverage
                                    balance = ft.balance
                                    ft.average = average
                                    ft.oc = 'O'
                                    ModelBase.session.add(ft)
                                elif average:
                                    # Closer. Enter PL and check for last trade --
                                    pl = (average - ft.price) * ft.qty
                                    ft.oc = 'C'
                                    # if ft[rc.bal] == 0:
                                    #     average = None
                                    ModelBase.session.add(ft)
                                    break
                            elif ft.average:
                                average = ft.average
                                prevBalance = ft.balance
                                # raise ValueError('Programmer exception to find the statements')
                            else:
                                raise ValueError('What else we got here?')
                        ModelBase.session.commit()
                        break
                    elif i == len(prevTrades) - 1 and isNumeric(bt.pnl) and bt.pnl != 0:
                        # This catches a badTrade if the conditions above have failed (end of
                        # prevTrades) and the badTrade has a PL. Its possible we can figure out the
                        # some of the rest of the details by comparing average price to previous
                        # average price, or the previous price, if the average price is mssing
                        # there too. This algo was worke out in DASStatement.figureUnbalancedPL
                        # (incase its possible to generalize this and share code.)
                        if self.DBfigureUnbalancedPL_SA(prevTrades, bt):
                            ModelBase.session.commit()
                            break
                    else:
                        fixthese.append(pt)
        self.reFigureAPL_backwardsSA()


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
                continue
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
                        # Discriminator for first opening transaction
                        pastPrimo = False
                        side = LONG

                        for ft in fixthese_r:
                            # ft = self.makeTradeDict(fixthis)

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

                                # average should be set for this one
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
                        conn.commit()
                        break
                        # ######
                    elif isNumeric([pt[rc.avg], pt[rc.PL], pt[rc.bal]]) and pt[rc.PL] != 0:
                        # Found a good closer (has PL and avg)
                        fixthese.append(prevTrade)
                        fixthese.insert(0, badTrade)
                        fixthese_r = reversed(fixthese)

                        average = None
                        nextTrade = False
                        pastPrimo = False
                        for ft in fixthese_r:
                            # ft = self.makeTradeDict(fixthis)

                            if pastPrimo and not isNumeric(ft[rc.bal]):
                                # ## Has the balance variable been set????
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
                                # prevBal = ft[rc.bal]
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
                    elif i == len(prevTrades) - 1 and isNumeric(bt[rc.PL]) and bt[rc.PL] != 0:
                        # This catches a badTrade if the conditions above have failed (end of
                        # prevTrades) and the badTrade has a PL. Its possible we can figure out the
                        # some of the rest of the details by comparing average price to previous
                        # average price, or the previous price, if the average price is mssing
                        # there too. This algo was worke out in DASStatement.figureUnbalancedPL
                        # (incase its possible to generalize this and share code.)
                        if self.DBfigureUnbalancedPL(cur, prevTrades, bt):
                            conn.commit()
                            break
                    else:
                        fixthese.append(prevTrade)
        self.reFigureAPL_backwards()

    def reFigureAPL_backwardsSA(self):
        '''
        A second algorithm to try to fill in some blanks. A bad trade is missing average and/or
        balance.
        A trade where balance == shares can set avg = price and is an opener (OC = O).
        A trade with a PL value != 0  is a closer and we can figure average. An adjacent
            (to the closer) and previous opener will have the same average.
        '''
        rc = self.rc
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        # LONG = True
        # SHORT = False

        badTrades = self.getBadTradesSA()
        for bt in badTrades:
            nextTrades = self.getNextTradesSA(bt)
            fixthese = [bt]
            # pastPrimo = False
            for nt in nextTrades:
                uncovered = self.getUncoveredDaysSA(bt.account, beg=bt.datetime, end=nt.datetime)
                if uncovered:
                    break
                fixthese.append(nt)
            for i, ft in enumerate(fixthese):
                if isNumeric(ft.balance) and ft.qty == ft.balance:
                    if not isNumeric(ft.average):
                        ft.average = ft.price
                        ft.oc = 'O'
                        ModelBase.session.add(ft)
                        ModelBase.session.commit()
                        return
                elif isNumeric(ft.pnl) and ft.pnl != 0:
                    # pastPrimo = True
                    average = ((ft.pnl / ft.qty) + ft.price)
                    if not ft.average or not isNumeric(ft.average):
                        ft.average = average
                    else:
                        assert math.isclose(average, ft.average, abs_tol=1e-2)
                    ft.oc = 'C'
                    # side = LONG if ft[rc.shares] < 0 else SHORT
                    if isNumeric(ft.balance):
                        balance = ft.balance
                        for j in range(i - 1, -1, -1):
                            balance = balance - fixthese[j + 1].qty
                            fixthese[j].balance = balance
                            ModelBase.session.add(fixthese[j])
                            # self.updateBal(cur, fixthese[j], balance)
                            if j == 0:
                                ModelBase.session.commit()
                                return
    def reFigureAPL_backwards(self):
        '''
        A second algorithm to try to fill in some blanks. A bad trade is missing average and/or
        balance.
        A trade where balance == shares can set avg = price and is an opener (OC = O).
        A trade with a PL value != 0  is a closer and we can figure average. An adjacent
            (to the closer) and previous opener will have the same average.
        '''
        rc = self.rc
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        # LONG = True
        # SHORT = False

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
                        for j in range(i - 1, -1, -1):
                            balance = balance - fixthese[j + 1][rc.shares]
                            self.updateBal(cur, fixthese[j], balance)
                            if j == 0:
                                conn.commit()
                                return

    def processStatementSA(self, tdf, account, begin, end, openPos=None):
        '''
        Processs the trade, positions, and covered tables using the Trades table and the
        OpenPositions table.
        '''
        rc = self.rc
        assert begin
        assert isinstance(begin, dt.date)
        if end:
            assert isinstance(end, dt.date)

        count = 0
        for i, row in tdf.iterrows():
            if self.insertTradeSA(row, update=True):
                count = count + 1
        if count == len(tdf):
            accounts = tdf[rc.acct].unique()
            for account in accounts:
                self.coveredDatesSA(begin, end, account)
        else:
            pass
        # self.insertPositions(openPos)
        ModelBase.session.commit()
        # conn.commit()
        self.reFigureAPL_SA(begin, end)
        dbdr = DbDoctorCrud()
        dbdr.doDups(autoDelete=True)

    def popHol(self):
        '''
        Populat the holidays table.
        '''
        didsomething = False
        for holiday in self.holidays:
            for i in range(1, len(holiday)):
                if holiday[i] and not self.tcrud.isHoliday(holiday[i]):
                    didsomething = True
                    self.tcrud.insertHoliday(holiday[i], holiday[0], commit=False)
        if didsomething:
            ModelBase.session.commit()
            ModelBase.session.close()

    def isCovered(self, account, d):
        '''
        returns True or False if this day is covered in the db. It is True if we have processed a
        Statement that covers this day. There may be no trades on a covered day. It imay be marked
        covered when processing a multi-day statement that spans the day or when processing a
        statement with no trades. We assume statments coave an  entire day. If the user imports
        partial DAS data, it may be untrue.
        '''
        d = pd.Timestamp(d).date()
        beg = end = d
        unc = self.getUncoveredDays(account, beg, end)
        if d in unc:
            return False
        return True

    def getTradeSumByDateSA(self, daDate):
        tsums2 = self.tcrud.getTradeSumByDate(daDate)
        return tsums2

        # Unfortunately, going to format as  [dicts] to match the old API
        ret = []
        for ts in tsums2:
            tsd = dict()
            tsd['sf.name'] = ts.name
            tsd['sf.strat'] = ts.strategy
            tsd['sf.link1'] = ts.link1
            tsd['sf.acct'] = ts.account
            tsd['sf.pl'] = ts.pnl
            tsd['sf.start'] = ts.start
            tsd['sf.date'] = ts.date
            tsd['sf.dur'] = ts.duration
            tsd['sf.shares'] = ts.shares
            tsd['sf.mktval'] = ts.mktval
            tsd['sf.targ'] = ts.target
            tsd['sf.targdiff'] = ts.targdiff
            tsd['sf.stoploss'] = ts.stoploss
            tsd['sf.sldiff'] = ts.sldiff
            tsd['sf.rr'] = ts.rr
            tsd['sf.realrr'] = ts.realrr
            tsd['sf.maxloss'] = ts.maxloss
            tsd['sf.mstkval'] = ts.mstkval
            tsd['sf.mstknote'] = ts.mstknote
            tsd['sf.explain'] = ts.explain
            tsd['sf.notes'] = ts.notes
            tsd['clean'] = ts.clean
            ret.append(tsd)
        return ret

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        sf = self.sf

        daDate = self.formatDate(daDate)
        tsums = cur.execute(f'''
            SELECT id,
                   {sf.name}, {sf.strat}, {sf.link1}, {sf.acct}, {sf.pl}, {sf.start},
                   {sf.date}, {sf.dur}, {sf.shares}, {sf.mktval}, {sf.targ}, {sf.targdiff},
                   {sf.stoploss}, {sf.sldiff}, {sf.rr}, {sf.realrr}, {sf.maxloss}, {sf.mstkval},
                   {sf.mstknote}, {sf.explain}, {sf.notes}, clean
            FROM trade_sum Where date = ?''', (daDate, ))
        tsums = tsums.fetchall()
        if not tsums:
            return None
        return tsums


    def renameKeys(self, d):
        '''Rename the sa names in a dict to the SumReqFields as used every where else'''
        sf = self.sf
        dbnames = ['start', 'link1', 'date', 'name', 'account',
                   'pnl', 'strategy', 'duration', 'shares', 'mktval', 'target',
                   'targdiff', 'stoploss', 'sldiff', 'rr', 'realrr', 'maxloss',
                   'mstkval', 'mstknote', 'explain', 'notes', ]
        sfnames = [sf.start, sf.link1, sf.date, sf.name, sf.acct,
                   sf.pl, sf.strat, sf.dur, sf.shares, sf.mktval, sf.targ,
                   sf.targdiff, sf.stoploss, sf.sldiff, sf.rr, sf.realrr, sf.maxloss,
                   sf.mstkval, sf.mstknote, sf.explain, sf.notes, ]
        for dbn, sfn in zip(dbnames, sfnames):
            if dbn in d:
                d[sfn] = d.pop(dbn)
            else:
                print(f'There is no {dbn}')
        return d

    def getTradeSummariesSA(self, daDate):
        '''
        Get the TradeSummaries as list of dict, each element is a transaction from the trade.
        Combine info from the related tables into TradeSummaries. Also, create and return the
        entries object. The entries object is used place the entry markers in trade charts.
        
         A trade begins with a purchase or sale from 0 shares and ends with 0 shares.
        Exceptions may be overnight trades in which either the beginning or end transaction
        is not (yet) associated with this trade. Associated data in trade summaries include
        user input and analysis including associated chart files. (located in the file system)
        '''
        sf = self.sf

        daDate = self.formatDate(daDate)
        tsums = self.getTradeSumByDateSA(daDate)
        if not tsums:
            return dict(), None

        tradeSummary = dict()
        entriesd = dict()
        for i, ts in enumerate(tsums):
            # Get list of trades from trade_sum relationship and create the entries list and
            # place the entry info in tsd
            # ModelBase.session.expunge(ts)
            entries = list()

            tsd = ts.__dict__.copy()
            tsd = self.renameKeys(tsd)
            if '_sa_instance_state' in tsd:
                del tsd['_sa_instance_state']
            ts_id = ts.id
            key = str(i + 1) + ' ' + tsd[sf.name]

            # Get list of charts from trade_sum relationship
            sumCharts = self.tcrud.getCharts(ts.id)
            for schart in sumCharts:
                chart = 'chart' + str(schart.slot)
                if not schart.name:
                    continue
                if not schart.path:
                    path = getDirectory(ts.date)
                    schart.path = os.path.join(path, 'out/')
                name = os.path.join(schart.path, schart.name)
                start = pd.Timestamp(schart.start)
                end = pd.Timestamp(schart.end)
                tsd[chart] = name
                tsd[chart + 'Start'] = start
                tsd[chart + 'End'] = end
                tsd[chart + 'Interval'] = schart.interval

            
            sumTrades = self.tcrud.getTradesByTsid(ts.id)
            for i in range(0, 8):
                ii = str(i + 1)
                if i < len(sumTrades):
                    strade = sumTrades[i]
                    BS = 'B' if strade.qty >= 0 else 'S'
                    time = pd.Timestamp(strade.datetime)
                    entry = [strade.price, '', BS, time]
                    entries.append(entry)
                    # 9 is OC, 5 is price
                    if strade.oc.find('O') > -1:
                        tsd['Entry' + ii] = strade.price
                        tsd['Exit' + ii] = ''
                    else:
                        tsd['Exit' + ii] = strade.price
                        tsd['Entry' + ii] = ''

                    tsd['Time' + ii] = time
                    tsd['EShare' + ii] = strade.qty
                    diff = None
                    if isinstance(strade.average, float):
                        diff = strade.price - strade.average
                    tsd['Diff' + ii] = diff
                    tsd['PL' + ii] = strade.pnl if strade.pnl is not None else ''
                    tsd['Avg' + ii] = strade.average
                else:
                    tsd['Exit' + ii] = ''
                    tsd['Entry' + ii] = ''
                    tsd['Time' + ii] = ''
                    tsd['EShare' + ii] = ''
                    tsd['Diff' + ii] = ''
                    tsd['PL' + ii] = ''
                    tsd['Avg' + ii] = ''

            tdf = pd.DataFrame(data=[tsd.values()], columns=tsd.keys())
            entriesd[key] = entries
            tradeSummary[key] = tdf
        return tradeSummary, entriesd


    def getStatement(self, day, account='all'):
        '''
        Get the trades from a single day. This is the default and corresponds tradeSummaries
        with numbered trades from a single day. Create a DataFrame with minimal columns, Format
        Date and Time and add Side
        :day: A date string or timestamp. The statement day
        :account: Leave blank to get all accounts. Fill in to get a single account.
        :return: DataFrame.
        '''
        rc = self.rc
        day = pd.Timestamp(day)
        begin = day.strftime('%Y%m%d')
        end = day.strftime('%Y%m%d;99')
        trades = None
        df = self.tcrud.getStatementDf(begin, end, account)
        if not isinstance(df, pd.DataFrame):
            return pd.DataFrame()
        
        df = df.rename(columns={ 'datetime':rc.date, 'symb':rc.ticker, 'qty': rc.shares, 'balance': rc.bal,
                                 'price': rc.price, 'average': rc.avg, 'pnl':rc.PL, 'commission': rc.comm,
                                 'oc':rc.oc, 'Start':rc.start, 'date': rc.date, 'das': 'DAS',
                                 'ib': 'IB', 'account': rc.acct, 'trade_sum_id': 'tsid'})

        df[rc.time] = ''
        for i, row in df.iterrows():
            df.at[i, rc.time] = row[rc.date][9:11] + ':' + row[rc.date][11:13] + ':' + row[rc.date][13:15]
            if row[rc.shares] > 0:
                df.at[i, rc.side] = 'B'
            else:
                df.at[i, rc.side] = 'S'
        return df


    def getCoveredDays(self):
        '''
        :return: a list of dates representing a complete list of days in the db
        '''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cursor = cur.execute('''
            SELECT min(day), max(day) from ib_covered ORDER BY day''')
        days = cursor.fetchall()
        returnMe = list()
        current = days[0][0]
        last = days[0][-1]
        last = pd.Timestamp(last)
        delt = pd.Timedelta(days=1)
        current = pd.Timestamp(current)
        while current <= last:
            if current.weekday() < 5 and not self.tcrud.isHoliday(current):
                returnMe.append(current)
            current = current + delt
        return returnMe

    def getUncoveredDaysSA(self, account, beg='20180301', end=None, usecache=False):
        '''
        Get Market days between beg and end for which we are not covered by a statement saved to the db.

        Paramaters:
        :params account:
        :params beg:
        :params end:
        :params usecache: Use the default True is this is to be called repeatedly to check the same dates
                   within a loop.
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
            strbeg = beg.strftime('%Y%m%d')
            strend = end.strftime('%Y%m%d')
            days = self.tcrud.getCoveredDays(account, strbeg, strend)
            self.covered = [pd.Timestamp(x.day).date() for x in days]
        notcovered = []
        current = beg.date()
        delt = pd.Timedelta(days=1)
        while True:
            if current.weekday() > 4 or self.tcrud.isHoliday(current):
                pass
            elif current not in self.covered:
                notcovered.append(current)
            else:
                pass
            current = current + delt
            if current > end.date():
                break
        return notcovered

    def getUncoveredDays(self, account, beg='20180301', end=None, usecache=False):
        '''
        Get Market days between beg and end for which we are not covered by a statement saved to the db.

        Paramaters:
        :params account:
        :params beg:
        :params end:
        :params usecache: Use the default True is this is to be called repeatedly to check the same dates
                   within a loop.
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
            if current.weekday() > 4 or self.tcrud.isHoliday(current):
                pass
            elif current not in self.covered:
                notcovered.append(current)
            else:
                pass
            current = current + delt
            if current > end.date():
                break
        return notcovered


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
    db = StatementDB()
    d = pd.Timestamp('2020-08-13')
    db.reFigureAPL_SA(d, d)
    # x = db.getUncoveredDaysSA('TRIB5621', "20180101", "20201201")
    print()



def main():
    '''Tun some local code for devel'''
    x = StatementDB()
    daDate = '20190103'
    ts, entries = x.getTradeSummariesSA(daDate)

    print(ts.keys())
    print(ts.values())
    print(entries)


if __name__ == '__main__':
    # notmain()
    local()
    # main()
