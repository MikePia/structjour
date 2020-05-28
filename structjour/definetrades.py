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
Created on Sep 5, 2018

@author: Mike Petersen
'''
import logging
import sys
# import datetime
import pandas as pd

from structjour.colz.finreqcol import FinReqCol
from structjour.dfutil import DataFrameUtil
from structjour.statements.ibstatementdb import StatementDB
from structjour.utilities.util import isNumeric


class ReqCol(object):
    '''
    Intended as an adapter class for multiple input types. ReqCol are the columns for the original
    input file All of these are required.
    '''

    def __init__(self, source="DAS"):
        '''Set the required columns in the import file.'''

        if source != 'DAS':
            logging.error("Only DAS is currently supported")
            raise ValueError

        # rcvals are the actual column titles (to be abstracted when we add new input files)
        # rckeys are the abstracted names for use with all file types
        rckeys = ['time', 'ticker', 'side', 'price', 'shares', 'acct', 'PL', 'date']
        rcvals = ['Time', 'Symb', 'Side', 'Price', 'Qty', 'Account', 'PnL', 'Date']
        rc = dict(zip(rckeys, rcvals))

        # Suggested way to address the columns for the main input DataFrame.
        self.time = rc['time']
        self.ticker = rc['ticker']
        self.side = rc['side']
        self.price = rc['price']
        self.shares = rc['shares']
        self.acct = rc['acct']
        self.PL = rc['PL']
        self.date = rc['date']

        self.rc = rc
        self.columns = list(rc.values())


class DefineTrades(object):
    '''
    DefineTrades moves the data from transaction centric to trade centric with a collection of
    transactions make a single trade. The dataframe representing a trade will have multiple
    transactions and added columns for time, share balance for each trade, duration and user info
    like stop loss, target and analasys.
    '''

    def __init__(self, source='DAS'):
        '''
        Constructor
        Note: source is not used by this class. Argument could be probably be removed.
        '''
        self.source = source
        assert self.source in ['DAS', 'IB_HTML', 'IB_CSV', 'DB']

        self._frc = FinReqCol(source)

    def appendCols(self, rccols):
        '''
        HACK ALERT:  adding columns to the the 'final' list of cols. Not ready to add these cols
        to FinReqCol
        '''
        cols = ['id', 'DAS', 'IB', 'tsid']
        for c in cols:
            if c not in rccols:
                rccols.append(c)
        return rccols

    def processDBTrades(self, trades):
        '''
        Run the methods to create the new DataFrame and fill in the data for the new trade-
        centric (as opposed to transaction-centric, trades may contain multiple transactgions) DataFrame.
        '''
        rc = self._frc

        # Process the output file DataFrame
        trades = self.addFinReqCol(trades)
        rccolumns = rc.columns.copy()
        rccolumns = self.appendCols(rccolumns)

        newTrades = trades[rccolumns]
        newTrades.copy()
        nt = newTrades.sort_values([rc.ticker, rc.acct, rc.date])
        # nt = self.writeShareBalance(nt)
        nt = self.addStartTimeDB(nt)
        # nt.Date = pd.to_datetime(nt.Date)
        nt = nt.sort_values([rc.start, rc.ticker, rc.acct, rc.date, rc.time], ascending=True)
        nt = self.addTradeIndex(nt)
        nt = self.addTradePL(nt)
        nt = self.addTradeDurationDB(nt)
        nt = self.addTradeNameDB(nt)
        ldf, nt = self.postProcessingDB(self.getTradeList(nt))
        nt = DataFrameUtil.addRows(nt, 2)
        nt = self.addSummaryPL(nt)

        dframe = DataFrameUtil.addRows(nt, 2)
        return dframe, ldf

    def addStartTimeDB(self, dframe):
        '''
        Add the start time to the new column labeled Start or frc.start. Each transaction whthin a
        trade will share a start time.
        :params dframe: The output df to place the data
        :return dframe: The same dframe but with the new start data.
        '''

        rc = self._frc

        newTrade = True
        oldsymb = ''
        oldaccnt = ''
        for i, row in dframe.iterrows():

            if row[rc.ticker] != oldsymb or row[rc.acct] != oldaccnt or row[rc.shares] == row[rc.bal]:
                newTrade = True
            oldsymb = row[rc.ticker]
            oldaccnt = row[rc.acct]

            if newTrade:
                newTrade = True if isNumeric(row[rc.bal]) and row[rc.bal] == 0 else False
                oldTime = dframe.at[i, rc.time]
                dframe.at[i, rc.start] = oldTime

            else:
                dframe.at[i, rc.start] = oldTime
            if row[rc.bal] == 0:
                newTrade = True
        return dframe

    def addTradeIndex(self, dframe):
        '''
        Labels and numbers the trades by populating the TIndex column. 'Trade 1' for example includes the transactions
        between the initial purchase or short of a stock and its subsequent 0 position. (If the stock is held overnight,
        non-transaction rows have been inserted to account for todays' activities.)
        '''

        rc = self._frc

        TCount = 0
        prevEndTrade = True
        prevTicker = ''
        prevAccount = ''

        for i, row in dframe.iterrows():
            if len(row[rc.ticker]) < 1:
                break
            if prevEndTrade or prevTicker != row[rc.ticker] or prevAccount != row[rc.acct]:
                TCount += 1
            tradeIndex = "Trade " + str(TCount)
            dframe.at[i, rc.tix] = tradeIndex

            prevEndTrade = False
            prevTicker = row[rc.ticker]
            prevAccount = row[rc.acct]
            # tradeIndex = "Trade " + str(TCount)
            if row[rc.bal] == 0:
                prevEndTrade = True
        return dframe

    def addTradePL(self, dframe):
        '''
        Add a trade summary P/L. That is total the transaction P/L and write a summary P/L for the
        trade in the c.sum column '''
        rc = self._frc
        newtrade = pd.DataFrame()
        for tindex in dframe[rc.tix].unique():
            t = dframe[dframe[rc.tix] == tindex]
            ixs = t.index
            sum = t[rc.PL].sum()
            t.at[ixs[-1], rc.sum] = sum
            newtrade = newtrade.append(t)
        return newtrade

    def addTradeDurationDB(self, dframe):
        '''
        Get a time delta beween the time of the first and last transaction. Place it in the
        c.dur column on the last transaction of the trade'''

        c = self._frc
        ldf = self.getTradeList(dframe)
        newdf = pd.DataFrame()
        for tdf in ldf:
            assert len(tdf[c.start].unique() == 1)
            ixs = tdf.index
            timeEnd = pd.Timestamp(tdf.at[ixs[-1], c.time])
            timeStart = pd.Timestamp(tdf.at[ixs[-1], c.start])
            dur = timeEnd - timeStart
            tdf.at[ixs[-1], c.dur] = dur
            # dur = tdf.at[ixs[-1], c.time] - tdf.at[ixs[-1], c.start]
            newdf = newdf.append(tdf)

        return newdf

    def addTradeNameDB(self, dframe):
        '''
        Create a name for this trade like 'AMD Short'. Place it in the c.name column.  This
        could still be a flipped position. The test is based on its last transaction.
        '''

        rc = self._frc
        newtrade = pd.DataFrame()
        for tindex in dframe[rc.tix].unique():
            t = dframe[dframe[rc.tix] == tindex]
            ixs = t.index
            side = ''
            if (t.iloc[-1][rc.oc].find('O') >= 0 and t.iloc[-1][rc.shares] > 0) or (
                    t.iloc[-1][rc.oc].find('C') >= 0 and t.iloc[-1][rc.shares] < 0):
                side = ' Long'
            else:
                side = ' Short'
            name = t[rc.ticker].unique()[0]
            name += side
            t.at[ixs[-1], rc.name] = name
            newtrade = newtrade.append(t)
        return newtrade

    def addSummaryPL(self, df):
        '''
        Create a summaries of live, sim and total P/L for the day and place it in new rows.
        Total and sim total go in the first blank row under PL and sum
        Live total in lower blank row under sum. Note that the accounts are identified 'IB' style
        and will break when new brokers are added.  Uxxxxxxxx is live, TRxxxxxx is sim. When new
        brokers are added do something else.
        :prerequisites: 2 blank rows added at the bottom of the df
        :raise AssertionError: If blank lines are not in df.
        '''
        rc = self._frc
        df.reset_index(drop=True, inplace=True)
        df[rc.PL] = pd.to_numeric(df[rc.PL], errors='coerce')

        ixs = df[df[rc.ticker] == ''].index
        assert len(ixs) > 1
        total = df[rc.PL].sum()
        for acnt in df[rc.acct].unique():
            acnttotal = df[df[rc.acct] == acnt][rc.PL].sum()
            if acnt.startswith('U'):
                df.at[ixs[1], rc.sum] = acnttotal
            elif acnt.startswith('TR'):
                df.at[ixs[0], rc.sum] = acnttotal

        df.at[ixs[0], rc.PL] = total
        return df

    def getTradeList(self, dframe):
        '''
        Creates a python list of DataFrames for each trade. It relies on addTradeIndex successfully creating the
        trade index in the format Trade 1, Trade 2 etc.
        :param:dframe: A dataframe with the column Tindex filled in.
        '''
        c = self._frc
        try:
            if not dframe[c.tix].unique()[0].startswith('Trade'):
                raise(NameError(
                    "Cannot make a trade list. Call addTradeIndex() before."))
        except NameError as ex:
            logging.error(ex)
            sys.exit(-1)

        ldf = list()
        for i, tindex in enumerate(list(dframe['Tindex'].unique())):
            tdf = dframe[dframe.Tindex == tindex]
            ldf.append(tdf)
        return ldf

    def fixTsid(self, tdf):
        if len(tdf['tsid'].unique()) > 1:
            therightone = list()

            for id in tdf['tsid'].unique():
                if isNumeric(id):
                    therightone.append(id)
            if len(therightone) > 1:
                # This could be a place for user input...There are confused ids here
                # The question is what trade do these transactions belong to.
                raise ValueError('Programmers exception: Something needs to be done here')
            elif len(therightone) == 1:
                ibdb = StatementDB()
                for i, row in tdf.iterrows():
                    tdf.at[i, 'tsid'] = therightone[0]
                    ibdb.updateTSID(row['id'], therightone[0])
                # If one of the vals was nan, the column became float
                tdf = tdf.astype({'tsid': int})
                # Update the db
        return tdf

    def postProcessingDB(self, ldf):
        '''
        A few items that need fixing up. Locate and name flipped positions and overnight holds and
        change the name appropriately. Look for trades that lack a tsid (foreign key) and fix
        :params ldf: A ist of DataFrames, each DataFrame represents a trade defined by the initial
                     purchase or short of a stock, and all transactions until the transaction which
                     returns the share balance to 0.
        :return (ldf, nt): The updated versions of the list of DataFrames, and the updated single
                      DataFrame.
        '''
        rc = self._frc
        dframe = pd.DataFrame()
        for tdf in ldf:
            x0 = tdf.index[0]
            xl = tdf.index[-1]
            if tdf.at[x0, rc.bal] != tdf.at[x0, rc.shares] or tdf.at[xl, rc.bal] != 0:
                tdf.at[xl, rc.name] = tdf.at[xl, rc.name] + " OVERNIGHT"

            if tdf.at[x0, rc.bal] != 0:
                firstrow = True
                for i, row in tdf.iterrows():
                    # Cant fix anythintg if the balance is not set
                    if row[rc.bal] is None:
                        break
                    if firstrow:
                        side = True if row[rc.bal] > 0 else False
                        firstrow = False
                    elif row[rc.bal] != 0 and (row[rc.bal] >= 0) != side:
                        tdf.at[xl, rc.name] = tdf.at[xl, rc.name] + " FLIPPED"
                        break
            else:
                assert len(tdf) == 1
            if len(tdf['tsid'].unique()) > 1 or not isNumeric(tdf['tsid'].unique()[0]):
                tdf = self.fixTsid(tdf)

            dframe = dframe.append(tdf)
        return ldf, dframe

    def addFinReqCol(self, dframe):
        '''
        Add the columns from FinReqCol that are not already in dframe.
        :params dframe: The original DataFrame with the columns of the input file and including at
                         least all of the columns in ReqCol.columns
        :return dframe: A DataFrame that includes at least all of the columns in FinReqCol.columns
        '''
        c = self._frc
        for l in c.columns:
            if l not in dframe.columns:
                dframe[l] = ''
        return dframe
