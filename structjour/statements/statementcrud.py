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
sqlalchemy models for trade tables

@author: Mike Petersen
@creation_date: August 14, 2020

Implement the db methods from StatementDB using SA -- 
    Planning to change it a bit to make it more independent. That will require some changes outside this file.
'''
import pandas as pd
from structjour.models.meta import ModelBase
from structjour.models.trademodels import Trade, TradeSum, Charts
from structjour.models.coveredmodel import Covered

from structjour.colz.finreqcol import FinReqCol
from structjour.thetradeobject import SumReqFields

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMessageBox

def formatDate(daDate, frmt='%Y%m%d'):
    daDate = pd.Timestamp(daDate)
    return daDate.strftime(frmt)

def formatTime(daTime, frmt='%H:%M:%S'):
    daTime = pd.Timestamp(daTime)
    return  daTime.strftime(frmt)

def getFloat(val):
    if not isinstance(val, (float)):
        try:
            val = float(val)
        except:
            return 0.0
    return val

class TradeCrud:
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

        self.rc = FinReqCol()
        self.sf = SumReqFields()
        self.createTable()

    def createTable(self):
        ModelBase.connect(new_session=True)
        ModelBase.createAll()

    def insertTradeSummary(self, trade):
        '''
        Create a new record from the trade object
        :params trade: DataFrame that uses the column names defined in SumReqFields
        '''
        sf = self.sf
        rc = self.rc
        # tcols = sf.tcols
        newts = dict()
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        tradesum = TradeSum()


        tradesum.name = trade[sf.name].unique()[0]
        tradesum.strategy = trade[sf.strat].unique()[0]
        tradesum.link1 = trade[sf.link1].unique()[0]
        tradesum.account = trade[sf.acct].unique()[0]
        tradesum.pnl = trade[sf.pl].unique()[0]
        tradesum.start = formatTime(trade[sf.start].unique()[0])
        tradesum.date = formatDate(trade[sf.date].unique()[0])
        tradesum.duration = trade[sf.dur].unique()[0]
        tradesum.shares = trade[sf.shares].unique()[0]
        tradesum.mktval = getFloat(trade[sf.mktval].unique()[0])
        tradesum.target = getFloat(trade[sf.targ].unique()[0])
        tradesum.targdiff = getFloat(trade[sf.targdiff].unique()[0])
        tradesum.stoploss = getFloat(trade[sf.stoploss].unique()[0])
        tradesum.sldiff = getFloat(trade[sf.sldiff].unique()[0])
        tradesum.rr = trade[sf.rr].unique()[0]
        tradesum.realrr = trade[sf.realrr].unique()[0]
        tradesum.maxloss = getFloat(trade[sf.maxloss].unique()[0])
        tradesum.mstkval = getFloat(trade[sf.mstkval].unique()[0])
        tradesum.mstknote = trade[sf.mstknote].unique()[0]
        tradesum.explain = trade[sf.explain].unique()[0]
        tradesum.notes = trade[sf.notes].unique()[0]
        tradesum.clean = ''
        session.add(tradesum)
        session.commit()
        return tradesum

    def updateTradeSummary(self, trade):
        '''
        Update the user fields in trade_sum. 
        :params trade: DataFrame that uses the column names defined in SumReqFields
        '''
        sf = self.sf
        rc = self.rc
        # tcols = sf.tcols
        newts = dict()
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        tradesum = self.findTradeSummary(trade[sf.date].unique()[0], trade[sf.start].unique()[0])
        trade[sf.id] = tradesum.id
        if not tradesum:
            return None
        tradesum.strategy = trade[sf.strat].unique()[0]
        tradesum.link1 = trade[sf.link1].unique()[0]

        tradesum.mktval = getFloat(trade[sf.mktval].unique()[0])
        tradesum.target = getFloat(trade[sf.targ].unique()[0])
        tradesum.targdiff = getFloat(trade[sf.targdiff].unique()[0])
        tradesum.stoploss = getFloat(trade[sf.stoploss].unique()[0])
        tradesum.sldiff = getFloat(trade[sf.sldiff].unique()[0])
        tradesum.rr = trade[sf.rr].unique()[0]
        tradesum.realrr = trade[sf.realrr].unique()[0]
        tradesum.maxloss = getFloat(trade[sf.maxloss].unique()[0])
        tradesum.mstkval = getFloat(trade[sf.mstkval].unique()[0])
        tradesum.mstknote = trade[sf.mstknote].unique()[0]
        tradesum.explain = trade[sf.explain].unique()[0]
        tradesum.notes = trade[sf.notes].unique()[0]
        tradesum.clean = trade[sf.clean].unique()[0]
        session.add(tradesum)
        session.commit()
        return tradesum

    def getTradeSumByDate(self, daDate):
        sf = self.sf
        tsums = TradeSum.findByTime(formatDate(daDate))
        if not tsums:
            return None
        return tsums

    def getTradeSumById(self, tsid):
        return TradeSum.getById(tsid)

    def findTradeSummary(self, date, start):
        '''
        A helper method for addTradeSummariesSA and updateTradeSummaries
        Get a single trade summary record by date and time
        :date: A Date string or Timestamp for the date to find.
        :start: A Time string or Timestamp for the time to find
        :return: The found record as a tuple or False
        '''
        
        x = TradeSum.findByTime(formatDate(date), formatTime(start))
        if x:
            if len(x) > 1:
                logging.error(f'multiple trade summaries found with date:{date}, start: {start}')
            return x[0]

        return False

    def updateChart(self, tsid, chart, slot):
        Charts.updateChart(tsid, chart, slot)

    def getStatementDf(self, begin, end, account):
        q = Trade.getStatementQuery(begin, end, account)
        df = pd.read_sql(q.statement, con=ModelBase.session.bind)
        print()
        return df

    def updateEntries(self, tsid, tids):
        if isinstance(tids, pd.DataFrame):
            tids = list(tids.id)
        elif isinstance(tids, int):
            tids = [tids]
        elif not isinstance(tids, list):
            raise ValueError(f'arg typ of tids: {type(tids)} requires more programming')
        Trade.addTradesToSum(tsid, tids)

    def getEntryTrades(self, tsid):
        return TradeSum.getEntryTrades(tsid)

    def findTrade(self, datetime, symbol, quantity, account):
        # Looking for a duplicate trade
        t = Trade.findTrade(datetime, symbol, quantity, account)
        return t if t else False

    def insertTrade(self, row, oc, source, new_session=False):
        '''
        Verify before calling, check findTrade for duplicates and if found,
        assign trade argument  (to update pnl, avg, balance and oc)
        :params row: pd.Series
        :params oc: The Open/Close code
        :params source: Currently DAS or IB
        '''
        if new_session:
            ModelBase.connect(new_session=True)
        session = ModelBase.session
        das, ib = ('DAS', None) if source == 'DAS' else (None, 'IB')

        trade = Trade(
            symb = row['Symb'],
            datetime = row['DateTime'],
            qty = row['Qty'],
            balance = row['Balance'],
            price = row['Price'],
            average = row['Average'],
            pnl = row['PnL'],
            commission = row['Commission'],
            oc = oc,
            das =  das,
            ib = ib,
            account = row['Account']
            # trade_sum_id=Column(Integer, ForeignKey('trade_sum.id'))
        )
        session.add(trade)
        return True

    def isDateCovered(self, account, d):
        return Covered.isDateCovered(account, d)

    def insertCovered(self, account, d):
        Covered.insertCovered(account, d)


def dostuff():
    t = TradeCrud()
    print(t.findTradeSummary('20190103', "10:54:46"))

if __name__ == '__main__':
    dostuff()


# if isinstance(df, pd.DataFrame):
#             self.df = df
#         else:
#             self.df = self.openDasFile(defaultPositions=False)
#         if not self.df.empty:
#             DataFrameUtil.checkRequiredInputFields(self.df, ReqCol().columns)
#             self.df = self.df[[rc.time, rc.ticker, rc.side, rc.price,
#                                rc.shares, rc.acct, rc.PL, rc.date, 'Cloid']]
#             self.df[rc.bal] = np.nan
#             self.df[rc.avg] = np.nan
#             self.df[rc.comm] = np.nan
#             self.df[rc.oc] = ''
