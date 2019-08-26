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
Re- doing das Statemnet stuff to save the trades in the db and generally imporve it.

@author: Mike Petersen
@creation_data: 07/8/19
'''


# from pandas import DataFrame, read_csv
# import matplotlib.pyplot as plt
import math
import os

import numpy as np
import pandas as pd
from PyQt5.QtCore import QSettings

from journal.definetrades import FinReqCol, ReqCol
from journal.dfutil import DataFrameUtil
# from journal.dfutil import
from journal.statements import findfiles as ff
from journal.statements.findfiles import findFilesSinceMonth
from journal.statements.ibstatementdb import StatementDB

# pylint: disable=C0103



class DasStatement:
    '''
    Handles opening DAS export files from the trades and positions window and creating a df.
    Adds Balance, Average, OC and Date columns
    '''
    def __init__(self, infile, settings, theDate, positions='positions.csv', df=None):
        self.settings = settings
        self.theDate = theDate
        self.infile = infile
        self.infile2 = positions
        self.positions = positions
        rc = FinReqCol()
        self.rc = rc
        if not theDate:
            raise ValueError('Das input files require theDate parameter.')

        if isinstance(df, pd.DataFrame):
            self.df = df
        else:
            self.df = self.openDasFile()
        if not self.df.empty:
            DataFrameUtil.checkRequiredInputFields(self.df, ReqCol().columns)
            self.df = self.df[[rc.time, rc.ticker, rc.side, rc.price,
                               rc.shares, rc.acct, rc.PL, rc.date, 'Cloid']]
            self.df[rc.bal] = np.nan
            self.df[rc.avg] = np.nan
            self.df[rc.comm] = np.nan
            self.df[rc.oc] = ''

    def makeShortsNegative(self, df):
        ''' Fix the shares sold to be negative values.
        '''

        rc = ReqCol()

        for i, row in df.iterrows():
            if row[rc.side] != 'B' and row[rc.shares] > 0:
                df.at[i, rc.shares] = ((df.at[i, rc.shares]) * -1)
        return df

    def figureUnbalancedBAPL(self, ttdf):
        '''
        Figure Balance, Average, and PnL. DAS has a PL column but it often differs from the 
        calculations  (and from IB). 
        :ttdf: A dataframe of a single ticker/account, It includes 1 or 2 partial trades. It may
               also include 1 or more complete trades. We will try to deduce the averages by using
               the PL. If any trade lacks a (PL != 0), we can't figure out anything -- This happens
               most commonly on statements that open one day,  and close on a later day. DAS statements
               are generally one day only statements.
        '''
        # Going to write this as I locate the different cases for each case cumulative
        # Then plan to re-write after all case types are found.

        tdf = ttdf.copy()
        rc = FinReqCol()
        LONG = True
        SHORT = False
        side = LONG
        tdf.reset_index(drop=True, inplace=True)
        average = None
        # breakitup = False
        for i in range(len(tdf)):
            # Using this snaky iteration we go forwards to a point, backwards to the beginning
            # and forward to the end (to be successful and getting some  redundant results for
            # figureAPL, all we need is the  balance from the first trade in the tdf)  Let the
            # contortions begin

            # Need to find a PL ( a closer 'B') preceeded immediately by an opener ('A')
            #    Where A.price == B.average
            #       Note that any closer must be preceeded by an opener so find a
            #       (SHORT closer) -- look for a (SHORT opener)
            #           Criteria met when -- in forward iteration, we find any closer preceed by
            #           its oppositie side
            # If this fails return the original df
            # The 2 conditions of failure, I believe, (not sure about number 1 anymore)
            #   1) The first trade closes without a PL (ie PL==0) and no other tx in first trade
            #      has PL
            #   2) No PL found period
            # Result of failure is the trade is entered in the DB as is and will be found a
            #       badTrade in refigureBAPL But it will still be available for structjour and the
            #      (avoidatallcost) ask the user (positions) form
            if tdf.at[i, rc.PL] != 0:
                # This is a closer
                average = (tdf.at[i, rc.PL] / tdf.at[i, rc.shares]) + tdf.at[i, rc.price]
                tdf.at[i, rc.avg] = average
                tdf.at[i, rc.oc] = 'C'
                side = SHORT if tdf.at[i, rc.shares] > 0 else LONG
                if i == 0:
                    continue
                sides = tdf[tdf[rc.date] <= tdf.at[i, rc.date]][rc.side].unique()
                if (set(['B', 'S']) - set(sides)) and (set(['B', 'SS']) - set(sides)):
                    continue
                moreBackwards = False
                for j in range(i-1, -1, -1):
                    # Iterate backward to beginning trade of statement --- note that this test is
                    # not what it seems It tests that the this trade's and the following closer
                    # trade's  sides  have opposite buy/sell Don't believe that guarantees the two
                    # transactions are from the same trade if the trades are adjacent, we got
                    # something --  a closer demands a previous opener but don't think the bases
                    # are covered yet
                    if moreBackwards:
                        balance = balance - tdf.at[j+1, rc.shares]
                        tdf.at[j, rc.bal] = balance

                        if j == 0:
                            #maybe def updateBalance(self, balance)
                            balance = balance - tdf.at[j, rc.shares]

                            for k in range(len(tdf)):
                                balance = tdf.at[k, rc.shares] + balance
                                tdf.at[k, rc.bal] = balance
                            balance = tdf.iloc[0][rc.bal] - tdf.iloc[0][rc.shares]
                            ntdf, stdf = self.figureAPL(tdf, balance, 0)
                            return ntdf, stdf

                    elif (side == LONG and tdf.at[j, rc.shares] > 0) or (
                            side == SHORT and tdf.at[j, rc.shares] < 0):
                        # opener
                        # If the following row is a closer, then we share the average
                        if tdf.at[j+1, rc.oc] == 'C':
                            tdf.at[j, rc.oc] = 'O'
                            tdf.at[j, rc.avg] = average
                            # If the average==price, this is the trade opener (for our purposes)
                            # and we can now set all the balances
                            if math.isclose(tdf.at[j, rc.price], average, abs_tol=1e-5):
                                # Found a Trade beginning opener balance = quantity
                                balance = tdf.at[j, rc.shares]
                                tdf.at[j, rc.bal] = balance
                                if j == 0:
                                    # We could quit here
                                    # thurn turn the snake around --and exit at
                                    balance = 0
                                    for k in range(len(tdf)):
                                        # partially redundantly fill in balances
                                        balance = tdf.at[k, rc.shares] + balance
                                        tdf.at[k, rc.bal] = balance
                                    # breakitup = True
                                else:
                                    # Continue backwards iteration-- setting balance
                                    # then go forward from here
                                    moreBackwards = True
                                    continue
                                balance = tdf.iloc[0][rc.bal] - tdf.iloc[0][rc.shares]
                                ntdf, stdf = self.figureAPL(tdf, balance, 0)
                                return ntdf, stdf
        return ttdf, pd.DataFrame()

    def figureAPL(self, tdf, balance, prevBalance):
        '''
        Figure the average price and the PL. Although DAS has PL, it often does not match the
        figures -- or IB
        '''

        rc = self.rc

        ntdf = pd.DataFrame()
        stdf = pd.DataFrame()
        LONG = True
        SHORT = False
        side = LONG
        pastPrimo = False


        # Figure balance first -- send to swing trade if PL does not match
        for i, row in tdf.iterrows():
            quantity = row[rc.shares]
            prevBalance = balance
            balance = balance + row[rc.shares]
            tdf.at[i, rc.bal] = balance

            # Check for a flipped position. The flipper is figured like an Opener; the
            # average changes, and no PL is take.
            if pastPrimo and side == LONG and balance < 0:
                side = SHORT
            elif pastPrimo and side == SHORT and balance > 0:
                side = LONG

            # This the first trade Open; average == price and set the side-
            if not pastPrimo and balance == row[rc.shares]:

                pastPrimo = True
                average = row[rc.price]
                tdf.at[i, rc.avg] = average
                tdf.at[i, rc.oc] = 'O'
                side = SHORT if quantity < 0 else LONG

            # Openers -- adding to the trade. The average changes
            elif (pastPrimo and side and row[rc.shares] > 0) or (
                    pastPrimo and not side and row[rc.shares] < 0):

                newAverage = ((average * prevBalance) + (row[rc.shares] * row[rc.price])) / balance
                average = newAverage
                tdf.at[i, rc.avg] = average
                tdf.at[i, rc.oc] = 'O'

            # Closers, set Close, DAS has all PL--check that PL matches with our figured
            # average and balance, if not, abort this and send to SwingTrade
            elif pastPrimo:

                tdf.at[i, rc.avg] = average
                PLfig = (average - row['Price']) * quantity

                # If DAS is more than 50 cents off, send it ot swing Trades (which is not
                # implemented yet-- just adds it back to normal) Otherwise just fixit here
                if not math.isclose(row[rc.PL], PLfig, abs_tol=0.5):
                    print('Figured the PL differently than DAS')
                    if abs(row[rc.PL] - PLfig) > 2:
                        print("The figured PL is far from DAS's PLcalculated PL")
                tdf.at[i, rc.PL] = PLfig                
                tdf.at[i, rc.oc] = 'C'
                if balance == 0:
                    pastPrimo = False
            elif (row[rc.bal] or row[rc.bal] == 0) and not math.isnan(row[rc.bal]) and (
                    row[rc.avg] and not math.isnan(row[rc.bal])):
                average = row[rc.avg]
                balance = row[rc.bal]
                continue
            else:
                print('just want to place a break here and verify these are unfixable from here.')
                # if len(tdf) == 1:
                #     continue
                # else:
                    # raise ValueError('First trade(s) no bal/avg in the tdf and pastPrimo is False')
        ntdf = ntdf.append(tdf)
        return ntdf, stdf

    def figureBA_noPositions(self, df):
        '''
        This is called if the positions table is lacking to detemine if there is missing data
        for any equities traded today. This is not ideal. Using the positions table is ideal.
        For tickers with balanced shares, we cn figure the average based on PL and Shares. For
        tickers with unbalanced shares, call figureUnbalancedBAPL. For the rare case where
        '''
        rc = FinReqCol()
        ddf = df.copy()
        actKeys = ddf[rc.acct].unique()
        swingTrades = pd.DataFrame()
        newTrades = pd.DataFrame()
        for actKey in actKeys:
            act = ddf[ddf[rc.acct] == actKey]
            symKeys = act[rc.ticker].unique()
            for symKey in symKeys:
                tdf = act[act[rc.ticker] == symKey].copy()
                tdf.sort_values([rc.date], inplace=True)
                tdf.reset_index(drop=True, inplace=True)
                if tdf[rc.shares].sum() != 0:
                    nt, st = self.figureUnbalancedBAPL(tdf)
                    newTrades = newTrades.append(nt)
                    swingTrades = swingTrades.append(st)

                else:
                    prevBalance = 0
                    balance = 0
                    nt, st = self.figureAPL(tdf, balance, prevBalance)
                    newTrades = newTrades.append(nt)
                    swingTrades = swingTrades.append(st)

        newTrades.reset_index(drop=True, inplace=True)
        swingTrades.reset_index(drop=True, inplace=True)
        assert len(newTrades) + len(swingTrades) == len(df)
        return newTrades, swingTrades

    def askAboutSwingTrades(self, st):
        '''placeholder'''
        return st, True

    def figureBalance(self, df):
        '''
        The easy way (using positions.csv) and the hard way (no positions.csv). The hard way should
        occassionally fail and require user intervention via the qt positions form. Avoid that by
        all possible contorted means.
        '''

        rc = FinReqCol()

        # positions = pd.DataFrame(columns=reqcols)
        if self.positions and os.path.exists(self.positions):
            positions = pd.read_csv(self.positions)
            print(positions)
            reqcols = ['Symb', 'Account', 'Shares']
            currentcols = list(positions.columns)
            if not set(reqcols).issubset(set(currentcols)):
                print('WARNING: positions table is missing the following required columns.')
                print(set(reqcols) - set(currentcols))
                positions = pd.DataFrame(columns=reqcols)
            else:
                positions = positions[positions['Shares'] != 0]
                positions = positions[reqcols]

        else:
            df, swingTrades = self.figureBA_noPositions(df)
            if not swingTrades.empty:
                swingTrades, success = self.askAboutSwingTrades(swingTrades)
                if not success:
                    return pd.DataFrame()
                df = df.append(swingTrades)
                df = df.sort_values([rc.acct, rc.ticker, rc.date])
                df.reset_index(drop=True, inplace=True)
            return df
        rc = FinReqCol()
        newdf = pd.DataFrame()
        for acntKey in df[rc.acct].unique():
            acnt = df[df[rc.acct] == acntKey]
            for ticker in acnt[rc.ticker].unique():

                tdf = df[df[rc.ticker] == ticker]
                tdf = tdf.sort_values(rc.date, )
                offset = tdf[rc.shares].sum()
                holding = 0
                pos = positions[(positions['Account'] == acntKey)  & (positions['Symb'] == ticker)]
                if ticker in pos['Symb'].unique():
                    assert pos['Symb'].unique()[0] == ticker
                    holding = pos['Shares'].unique()[0]
                    offset = offset - holding
                balance = -offset

                # testMe = tdf.copy()
                tdf, st = self.figureAPL(tdf, balance, 0)
                assert tdf.iloc[-1][rc.bal] == holding
                newdf = newdf.append(tdf)

                if not st.empty:
                    st, success = self.askAboutSwingTrades(st)
                # if not success:
                #     return pd.DataFrame()
                newdf = newdf.append(st)
                newdf = newdf.sort_values([rc.acct, rc.ticker, rc.date])
                newdf.reset_index(drop=True, inplace=True)

        newdf = newdf.sort_values([rc.acct, rc.ticker, rc.date])
        newdf.reset_index(drop=True, inplace=True)
        return newdf

    def normify(self, df):
        '''
        Normalize the df to match other Trade DFs
        '''
        for i, row in df.iterrows():
            if (isinstance(row.Time, float) and math.isnan(row.Time)) or not row.Time:
                df.drop([i], inplace=True)
        return df

    def openDasFile(self):
        '''
        Open an DAS export file from the trades window
        '''
        rc = self.rc
        self.theDate = pd.Timestamp(self.theDate)
        if not os.path.exists(self.infile):
            self.infile = os.path.join(ff.getDirectory(self.theDate), self.infile)
            self.positions = os.path.join(ff.getDirectory(self.theDate), self.positions)
        if not os.path.exists(self.infile):
            print('File does not exist', self.infile)
            return pd.DataFrame()
        pos = os.path.split(self.infile)
        self.positions = os.path.join(pos[0], self.positions)
        # self.settings.setValue('dasInfile', self.infile)

        df = pd.DataFrame()
        if not os.path.exists(self.positions):
            pass
            # print('File does not exist', self.positions)
        else:
            self.settings.setValue('dasInfile2', self.positions)
        df = pd.read_csv(self.infile)

        df = self.normify(df)

        if 'Date' not in df.columns:
            df['Date'] = np.nan
            df = self.createDateField(df)
        df = self.makeShortsNegative(df)
        if 'P / L' in df.columns:
            df = df.rename(columns={'P / L': rc.PL})

        reqcol = [rc.time, rc.ticker, rc.side, rc.price, rc.shares, rc.acct,
                  rc.PL, rc.date, 'Cloid']
        actualcols = list(df.columns)
        missingcols = set(reqcol) - set(actualcols)

        if missingcols:
            print('statement is missing the required fields:', missingcols)
            return pd.DataFrame()

        df = df[reqcol].copy()

        return df

    def createDateField(self, df):
        '''Add a datefield to df that uses a Timestamp'''
        for i, row in df.iterrows():
            dd = self.theDate
            tt = pd.Timestamp(row.Time)
            daDate = pd.Timestamp(dd.year, dd.month, dd.day, tt.hour, tt.minute, tt.second)
            df.at[i, 'Date'] = daDate
        return df

    def setNewInfile(self, newinfile):
        scheme = self.settings.value('scheme').split('/')
        if len(scheme) > 1:
            d = self.theDate
            scheme = scheme[1].format(Year='%Y', MONTH='%B', month='%m', DAY='%A', day='%d')
            d = d.strftime(scheme)
            newinfile, ext = os.path.splitext(newinfile)
            newinfile = f'{newinfile}{d}{ext}'
        self.settings.setValue('infile', newinfile)
        newinfile = os.path.join(ff.getDirectory(self.theDate), newinfile)
        return newinfile

    def combineOrdersByTime(self, t):
        '''
        There are a few seperate orders for equities that share the same order time. These cannot
        have an assigned share balance because there is no way to assign the order of execution.
        Combine them to a single order here. This corresponds to the trader's intention, not the
        broker's execution. When found, both of these orders were charged commission despite having
        the same order time.
        '''
        rc  = self.rc
        newdf = pd.DataFrame()
        for account in t[rc.acct].unique():
            if not account:
                return t
            accountdf = t[t[rc.acct] == account]
            for symbol in accountdf[rc.ticker].unique():
                tickerdf = accountdf[accountdf[rc.ticker] == symbol]  
                for datetime in tickerdf['DateTime'].unique():
                    ticketdf = tickerdf[tickerdf['DateTime'] == datetime]
                    if len(ticketdf) > 1:
                        net = 0
                        # Need to combin price commission and shares.
                        firstindex = True
                        ixval = None
                        buy = ticketdf.iloc[0][rc.shares] > 0
                        for i, row in ticketdf.iterrows():
                            assert buy == (row[rc.shares] > 0)
                            if firstindex:
                                ixval = i
                                firstindex = False
                            net = net + (row[rc.shares] * row[rc.price])
                        price = net / ticketdf[rc.shares].sum()
                        ticketdf.at[ixval, rc.price] = price
                        ticketdf.at[ixval, rc.comm] = ticketdf[rc.comm].sum()
                        ticketdf.at[ixval, rc.shares] = ticketdf[rc.shares].sum()
                        newdf = newdf.append(ticketdf.loc[ixval])
                    else:
                        newdf = newdf.append(ticketdf)
        return newdf

    def getTrades(self, listdf=None):
        '''
        Create an alternate dataFrame by ticket. For large share sizes this may have dramatically
        fewer transactions.
        :params listdf: Normally leave blank. If used, listdf should be the be a list of DFs.
        :return: The DataFrame created version of the data.
        :side effects: Saves a csv file of all transactions as single ticket transactions to
                        the settings inpathfile
        '''
        # TODO: Add the date to the saved file name after we get the date sorted out.
        if self.df.empty:
            return self.df
        if not listdf:
            listdf = self.getListOfTicketDF()


        newdf = DataFrameUtil.createDf(listdf[0], 0)

        for tick in listdf:
            t = self.createSingleTicket(tick)
            newdf = newdf.append(t)

        for i, row in newdf.iterrows():
            newdf.at[i, 'DateTime'] = row[self.rc.date].strftime('%Y%m%d;%H%M%S')
        newdf = self.combineOrdersByTime(newdf)

        newinfile = self.setNewInfile("tradesByTicket.csv")
        newdf.to_csv(newinfile)
        self.settings.setValue('inpathfile', newinfile)
        newdf = self.figureBalance(newdf)
        # newdf['DateTime'] = ''
        ibdb = StatementDB(source='DAS')

        # TODO Horrible assumption is that the date is 'covered' when this statement could be
        # a partial day. I think we can't fill in any covered days from a DAS export unless
        # the user says so...maybe in the filesettings form
        ibdb.processStatement(newdf, 'U2429974', self.theDate, self.theDate)

        return newdf

    def createSingleTicket(self, tickTx):
        '''
        Create a single row ticket from a Dataframe with a list (1 or more) of Transactions.
        :prerequisites: tickTx needs to have 'len(unique()) == 1' for side, symb, account, and
                        cloid. That uniqueness is created in getListOfTicketDF() so use that to
                         create a list of ticktTX.
        :params tickTx: A DataFrame with transactions from a single ticket
        :return: A single row data frame with total shares and average price.
        '''

        rc = ReqCol()

        total = 0
        totalPL = 0
        for dummy, row in tickTx.iterrows():
            total = total + (row[rc.price] * row[rc.shares])
            totalPL = totalPL + row[rc.PL]

        totalShares = tickTx[rc.shares].sum()
        avgPrice = total / totalShares

        newdf = DataFrameUtil.createDf(tickTx, 0)

        oneRow = tickTx.sort_values([rc.time, rc.price]).head(1)
        newdf = newdf.append(oneRow)
        newdf.copy()

        newdf[rc.price] = avgPrice
        newdf[rc.shares] = totalShares
        newdf[rc.PL] = totalPL
        return newdf

    def getListOfTicketDF(self):
        '''
        From the standard DAS input trades export (trades.csv) DataFrame create a list of trades;
        list member is a DataFrame with all transactions from a single ticket. This is made more
        interesting by the SIM transactions. They have no ticket ID (Cloid). They
        are identified in DAS by 'AUTO.' We will give each an ID unique for this run. There is only,
        presumably one ticket per SIM transaction, but check for uniqueness and report. (Found one
        on 10/22/28 -- a SIM trade on SQ. Changed the code not to fail in the event of an identical
        transx.)
        :return: A list of DataFrames, each list member is one ticket with 1 or more transactions.
        '''
        rc = self.rc

        dframe = self.df
        # if len(dframe.Cloid.apply(lambda x: isinstance(x, str))) < 1 :
        # newdf = pd.DataFrame
        SIMdf = dframe[dframe['Cloid'] == "AUTO"]
        newdf = dframe[dframe['Cloid'] != "AUTO"]
        # Found a DAS export that had two trades with the same times--so we will combine them
        SIMdf.sort_values([rc.acct, rc.ticker, rc.time], inplace=True)
        i = 0
        for tickKey in SIMdf[rc.ticker].unique():
            ticker = SIMdf[SIMdf[rc.ticker] == tickKey].copy()
            for timeKey in ticker[rc.time].unique():
                ticket = ticker[ticker[rc.time] == timeKey].copy()
                tickName = "SIMTick_{0}".format(i)
                ticket["Cloid"] = tickName
                newdf = newdf.append(ticket)
                i = i + 1

        #For each unique ticket ID (akaCloid), create a DataFrame and add it to a list of DataFrames
        listOfTickets = list()
        for ticketID in newdf.Cloid.unique():
            # Retrieves all rows that match the ticketID
            t = newdf[newdf['Cloid'] == ticketID]
            listOfTickets.append(t)
        # Combine the two above into a python list of DataFrames

        # for simTkt in SIMdf.Cloid.unique():
        #     t = SIMdf[SIMdf['Cloid'] == simTkt]
        #     listOfTickets.append(t)

        return listOfTickets


def notmain():
    '''Run some local code'''
    d = "20190208"
    settings = QSettings('zero_substance', 'structjour')
    # fs = findFilesInDir(trades[1], trades[0], searchParts=False)
    fs = findFilesSinceMonth(d, 'trades.csv', searchParts=False, DAS=True)
    for f in fs:
        print(f[0])
        ds = DasStatement(f[0], settings, f[1])
        df = ds.getTrades()
        print(list(df.columns), len(df))
    # idf = InputDataFrame()
    # trades, success = idf.processInputFile(df, settings.value('theDate'))


def local():
    fn = "C:/journal/trader/_20181203_December/_1203_Monday/trades.csv"
    if not os.path.exists(fn):
        print('try again')
    theDate = '20180323'
    settings = QSettings('zero_substance', 'structjour')
    ds = DasStatement('trades.csv', settings, theDate)
    df = ds.getTrades()

if __name__ == '__main__':
    notmain()
    # local()
