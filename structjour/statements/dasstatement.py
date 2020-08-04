# Structjour -- a daily trade review helper
# Copyright (C) 2020 Zero Substance Trading
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
@creation_date: 07/8/19
'''


# from pandas import DataFrame, read_csv
# import matplotlib.pyplot as plt
import logging
import math
import os

import numpy as np
import pandas as pd
from PyQt5.QtCore import QSettings

from structjour.colz.finreqcol import FinReqCol
from structjour.definetrades import ReqCol
from structjour.dfutil import DataFrameUtil
# from structjour.dfutil import
from structjour.statements import findfiles as ff
from structjour.statements.findfiles import findFilesSinceMonth
from structjour.statements.ibstatementdb import StatementDB
from structjour.utilities.util import isNumeric


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
        self.rc = FinReqCol()
        rc = self.rc
        if not theDate:
            raise ValueError('Das input files require theDate parameter.')

        if isinstance(df, pd.DataFrame):
            self.df = df
        else:
            self.df = self.openDasFile(defaultPositions=False)
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
        tdf.reset_index(drop=True, inplace=True)

        # breakitup = False
        if self.setSomeAverages(rc, tdf):
            if self.findOpenSetBalance(rc, tdf):
                return tdf, pd.DataFrame()
            else:
                return self.hypotheticalBalance(rc, tdf)

        # Failed to set the balance. Marking tdf as swing trade for the dreaded askuser.
        return pd.DataFrame(), tdf

    def setSomeAverages(self, rc, tdf):
        '''
        This is going to find closers (trades with a PL) and set the average and oc. If the trade
        before the closer is an opener, set its average and oc too. This will fail to set break
        even closers.
        '''
        setsome = False
        for i in range(len(tdf)):
            if tdf.at[i, rc.PL] != 0:
                average = (tdf.at[i, rc.PL] / tdf.at[i, rc.shares]) + tdf.at[i, rc.price]
                tdf.at[i, rc.avg] = average
                tdf.at[i, rc.oc] = 'C'
                setsome = True
                if i > 0 and tdf.at[i, rc.shares] * tdf.at[i - 1, rc.shares] < 0:
                    tdf.at[i - 1, rc.avg] = average
                    tdf.at[i - 1, rc.oc] = 'O'

        return setsome

    def findOpenSetBalance(self, rc, tdf):
        '''
        This is for unbalanced trades, that is a  (ticker/account) set that has sum(qty) != 0
        Prerequisite is there is at least one trade that has Average filled in. Search for an
        average = price. If found set all balances
        '''
        balance = 0
        foundOpen = False
        for i, row in tdf.iterrows():
            if isNumeric(row[rc.avg]) and math.isclose(row[rc.avg], row[rc.price], abs_tol=1e-3):
                balance = row[rc.shares] - tdf.at[tdf.index[0], rc.shares]
                foundOpen = True
                break
        if foundOpen:
            for i, row in tdf.iterrows():
                balance += row[rc.shares]
                tdf.at[i, rc.bal] = balance
            return True

        return False

    def hypotheticalBalance(self, rc, tdf):
        logging.warning('''Structjour has found an overnight transaction and cannot determine the
        share balance. It may soon open a dialogue to ask you, dear DAS user, how many shares
        were owned at the start of the day. The best way to avoid this is to export your DAS
        positions window on days that include overnight transactions.''')
        logging.warning('''Please be aware that structjour will attempt to find likely balance points but
        there is a possiblilty for error. Success or failure will not affect the reported PnL but failure
        will probably munge transactions together from different trades for this ticker.''')
        offsets = [-tdf.at[0, rc.shares], 0, tdf.at[0, rc.shares], -tdf[rc.shares].sum()]
        print(offsets)
        hypotheticalSuccess = []
        for i, offset in enumerate(offsets):
            success, t = self.testHypotheticalBalance(rc, tdf, offset)
            if success:
                hypotheticalSuccess.append(t)
        if len(hypotheticalSuccess) == 1:
            return hypotheticalSuccess[0], pd.DataFrame()
        elif len(hypotheticalSuccess) > 1:
            print('What next from this unlikely result?')
        return pd.DataFrame(), tdf

    def testHypotheticalBalance(self, rc, tdf, offset):
        t = tdf.copy()
        prevBalance = offset
        prevAverage = -1

        foundPotentialOpener = False
        foundPotentialCloser = False
        figureTheEarlierStuff = -1
        beginNewTrade = False
        long = True
        for i, row in t.iterrows():
            if beginNewTrade:
                beginNewTrade = False
                t.at[i, rc.oc] = 'O'

            balance = prevBalance + t.at[i, rc.shares]
            t.at[i, rc.bal] = balance
            if prevBalance == 0:
                if len(t.at[i, rc.oc]) > 0:
                    if t.at[i, rc.oc] != 'O':
                        return False, None
                else:
                    t.at[i, rc.oc] = 'O'
                average = row[rc.price]
                if isNumeric(row[rc.PL]) and row[rc.PL] != 0:
                    return False, None
                if isNumeric(row[rc.avg]) and not math.isclose(row[rc.avg], average, abs_tol=0.005):
                    return False, None
                if not foundPotentialOpener:
                    figureTheEarlierStuff = i
                t.at[i, rc.avg] = average
                foundPotentialOpener = True
                if row[rc.shares] < 0:
                    long = False
                prevBalance = balance
                prevAverage = average

            elif foundPotentialOpener:
                if (long and row[rc.shares] > 0) or (not long and row[rc.shares] < 0):
                    # isNumeric(row[rc.avg])
                    figuredAverage = ((prevBalance * prevAverage) + (row[rc.shares] * row[rc.price])) / balance
                    if isNumeric(row[rc.avg]):
                        if not math.isclose(row[rc.avg], figuredAverage, abs_tol=0.005):
                            return False, None
                        else:
                            average = figuredAverage
                    else:
                        t.at[rc.avg] = figuredAverage
                        average = figuredAverage
                else:
                    # This transaction should have been correctly identified in previous methods
                    if row[rc.oc] != 'C' or not isNumeric(row[rc.avg]) or row[rc.avg] <= 0:
                        return False, None
                    if not math.isclose(row[rc.avg], t.at[i - 1, rc.avg], abs_tol=0.005):
                        return False, None

                    print('take care of the closer')
                if balance == 0:
                    foundPotentialCloser = True
                    beginNewTrade = True
                prevBalance = balance
                prevAverage = average
            elif balance == 0 and not foundPotentialCloser:
                foundPotentialCloser = True
                prevBalance = balance
                t.at[i, rc.oc] = 'C'
                figureTheEarlierStuff = i
                if isNumeric(row[rc.PL]):
                    average = (row[rc.PL] / row[rc.shares]) + row[rc.price]
                    if isNumeric(row[rc.avg]) and row[rc.avg] > 0 and not math.isclose(average, row[rc.avg], abs_tol=0.005):
                        return False, None
                    beginNewTrade = True
            elif isNumeric(row[rc.PL]) and row[rc.PL] != 0:
                # An opener cannot have a pnl
                if (prevBalance < 0 and row[rc.shares] < 0) or (prevBalance > 0 and row[rc.shares] > 0):
                    return False, None
                prevBalance = balance
            else:
                prevBalance = balance

        if figureTheEarlierStuff > 0:
            i = figureTheEarlierStuff
            # Check the previous trade
            if t.at[i - 1, rc.oc] == 'C':
                if t.at[i, rc.shares] * t.at[i - 1, rc.shares] < 0 or (
                        not math.isclose((-t.at[i - 1, rc.PL] / t.at[i - 1, rc.shares]) + t.at[i - 1, rc.avg], t.at[i - 1, rc.price], abs_tol=0.005)):
                    return False, None
            else:
                if self.checkEverythinInTdf(rc, t):
                    return True, t
                print('There are still more possibilities here')

        return (foundPotentialCloser or foundPotentialOpener), t

    def checkEverythinInTdf(self, rc, t):
        '''
        Check average, balance, and oc that they all exist in harmony. Make no changes. Return
        False if anything is not right.
        TODO: Temporary- return False if trade is flipped
        '''
        for i, row in t.iterrows():
            long = True
            if row[rc.oc] not in ['O', 'C'] or not isNumeric(row[rc.bal]) or not isNumeric(row[rc.avg]) or row[rc.avg] <= 0:
                return False
            if i == 0:
                if (row[rc.oc] == 'O' and row[rc.shares] < 0) or (row[rc.oc] == 'C' and row[rc.shares] > 0):
                    long = False
            if (long and row[rc.bal] < 0) or (not long and row[rc.bal] > 0):
                # Flipped trade. Raise programming exception to see this in action
                logging.error('Might be a flipped trade. Programming note to check it out.')
                return False
            if row[rc.oc] == 'C':
                average = (row[rc.PL] / row[rc.shares]) + row[rc.price]
                if not math.isclose(average, row[rc.avg], abs_tol=0.005):
                    return False
                if (long and row[rc.shares] > 0) or (not long and row[rc.shares] < 0):
                    return False
            else:
                if i == 0:
                    # Somehow the average and balance are already set.
                    logging.error('''Programming error. How did this trade get here? It should not have been possible to figure the balance''')
                else:
                    pAvg, pBal, pr, qty, bal, avg = t.at[i - 1, rc.avg], t.at[i - 1, rc.bal], row[rc.price], row[rc.shares], row[rc.bal], row[rc.avg]
                    figAvg = ((pAvg * pBal) + (pr * qty)) / bal
                    if not math.isclose(avg, figAvg, abs_tol=0.005):
                        return False
                if (long and row[rc.shares] < 0) or (not long and row[rc.shares] > 0):
                    return False
        return True

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

            # This the first trade in this tdf. If there is no prevBal its an Open, average == price and set the side-
            # If there is a prevBalance, long if its > 0. Average can be set at the first trade with a PL != 0
            #   If there is no trade where no PL != 0. We don't know. The DB stuff will find it a bad trade and
            #       try to figure it.
            if not pastPrimo and balance == row[rc.shares]:

                pastPrimo = True
                average = row[rc.price]
                tdf.at[i, rc.avg] = average
                tdf.at[i, rc.oc] = 'O'
                side = SHORT if quantity < 0 else LONG

            elif not pastPrimo:
                # An overnight trade (or at least a trade without its opener)
                if row[rc.PL] != 0:
                    side = LONG if prevBalance > 0 else SHORT
                    # check for a flipper
                    if prevBalance * balance < 0:
                        side = not side
                    # programming assert to look for accuracy 02/16/20.
                    # This is a closing trade so the shares need be opposite the side
                    try:
                        if row[rc.shares] < 0:
                            assert side
                        else:
                            assert not side
                    except AssertionError:
                        logging.error('Failed to determine the side correctly')

                    pl, qty, price = row[rc.PL], row[rc.shares], row[rc.price]

                    average = (pl + (qty * price)) / qty
                    tdf.at[i, rc.avg] = average

                    tdf.at[i, rc.oc] = 'C'
                    prevBalance = balance
                    pastPrimo = True

                else:
                    # Required algo is unique
                    # TODO not to be left in place
                    print('now for something completely different')
                    assert False, f"Programming assert in serach of a statement to use in testing; {row[rc.date]}"

            # Openers -- adding to the trade. The average changes
            elif (pastPrimo and side and row[rc.shares] > 0) or (
                    pastPrimo and not side and row[rc.shares] < 0):

                average = ((average * prevBalance) + (row[rc.shares] * row[rc.price])) / balance
                tdf.at[i, rc.avg] = average
                tdf.at[i, rc.oc] = 'O'

            # Closers, set Close, DAS has all PL--check that PL matches with our figured
            # average and balance, if not, use DAS PL, leave the rest and log the error
            elif pastPrimo:

                tdf.at[i, rc.avg] = average
                PLfig = (average - row['Price']) * quantity
                tdf.at[i, rc.PL] = PLfig

                # If DAS is more than 50 cents off, use DAS PL and log error
                # Otherwise stick with our figures. (Thinking here is if its that far off,
                # I have missed something)
                if not math.isclose(row[rc.PL], PLfig, abs_tol=0.5):
                    if abs(row[rc.PL] - PLfig) > 2:
                        logging.error(f"{row[rc.ticker]}: {row[rc.acct]}: {row[rc.date]}, The figured PL is far from DAS's calculated PL")
                        tdf.at[i, rc.PL] = row[rc.PL]

                tdf.at[i, rc.oc] = 'C'
                if balance == 0:
                    pastPrimo = False
            elif (row[rc.bal] or row[rc.bal] == 0) and not math.isnan(row[rc.bal]) and (
                    row[rc.avg] and not math.isnan(row[rc.bal])):
                average = row[rc.avg]
                balance = row[rc.bal]
                continue

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
        swingTrades = pd.DataFrame()
        newTrades = pd.DataFrame()
        for actKey in ddf[rc.acct].unique():
            act = ddf[ddf[rc.acct] == actKey]
            for symKey in act[rc.ticker].unique():
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
            logging.info(f'The DAS positions file: {self.positions}')
            reqcols = ['Symb', 'Account', 'Shares']
            currentcols = list(positions.columns)
            if not set(reqcols).issubset(set(currentcols)):
                logging.warning('positions table is missing the following required columns.')
                logging.warning(f'{set(reqcols) - set(currentcols)}')
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

                tdf = acnt[acnt[rc.ticker] == ticker]
                tdf = tdf.sort_values(rc.date, )
                offset = tdf[rc.shares].sum()
                holding = 0
                pos = positions[(positions[rc.acct] == acntKey) & (positions[rc.ticker] == ticker)]
                if ticker in pos[rc.ticker].unique():
                    assert pos[rc.ticker].unique()[0] == ticker
                    holding = pos["Shares"].unique()[0]
                    offset = offset - holding
                elif tdf[rc.shares].sum() != 0:
                    offset = tdf[rc.shares].sum()

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

    def openDasFile(self, defaultPositions=True):
        '''
        Open an DAS export file from the trades window
        :params defaultPositions: If True, look for a file named {self.positions} (TODO add the date)
        in the same directory as self.infile. If found, set it as the positions file for this date.
        '''
        rc = self.rc
        self.theDate = pd.Timestamp(self.theDate)
        if not os.path.exists(self.infile):
            self.infile = os.path.normpath(os.path.join(ff.getDirectory(self.theDate), self.infile))
            self.positions = os.path.normpath(os.path.join(ff.getDirectory(self.theDate), self.positions))
        if not os.path.exists(self.infile):
            logging.warning(f'File does not exist: {self.infile}')
            return pd.DataFrame()
        if defaultPositions:
            pos = os.path.split(self.infile)
            self.positions = os.path.join(pos[0], self.positions)
            # self.settings.setValue('dasInfile', self.infile)

            if not os.path.exists(self.positions):
                pass
            else:
                self.settings.setValue('dasInfile2', self.positions)
        df = pd.DataFrame()
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
            logging.warning(f'statement is missing the required fields: {missingcols}')
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
        rc = self.rc
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

    def getTrades(self, listdf=None, testFileLoc=None, testdb=None):
        '''
        Create an alternate dataFrame by ticket. For large share sizes this may have dramatically
        fewer transactions.
        :params listdf: Normally leave blank. If used, listdf should be the be a list of DFs.
        :params testFileLoc: Override the location to place the file.
        :params testdb: Override the database to use
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
            d = pd.Timestamp(row[self.rc.date])
            newdf.at[i, 'DateTime'] = d.strftime('%Y%m%d;%H%M%S')
        newdf = self.combineOrdersByTime(newdf)
        newinfile = "tradesByTicket.csv"
        if not testFileLoc:
            newinfile = self.setNewInfile(newinfile)
        else:
            newinfile = os.path.join(testFileLoc, newinfile)
        newdf.to_csv(newinfile)
        self.settings.setValue('inpathfile', newinfile)
        newdf = self.figureBalance(newdf)
        # newdf['DateTime'] = ''
        ibdb = StatementDB(source='DAS', db=testdb)

        # TODO Note that the date is 'covered' in the DB if a statement is processed. That leaves
        # the possibility that the user exported a partial day. The trades should be added if/when
        # a statement is processed with additional trades. I believe it works but find a way to test
        # it -- maybe an altered DAS export with trades deleted.
        account = self.settings.value('account')
        if not account:
            account = ''
        ibdb.processStatement(newdf, account, self.theDate, self.theDate)

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

        dframe = dframe.astype({'Cloid': str})
        SIMdf = dframe[dframe['Cloid'] == "AUTO"].copy()
        newdf = dframe[dframe['Cloid'] != "AUTO"].copy()
        # Found a DAS export that had two trades with the same times--so we will combine them
        SIMdf.sort_values([rc.acct, rc.ticker, rc.time], inplace=True)
        i = 0
        for tickKey in SIMdf[rc.ticker].unique():
            ticker = SIMdf[SIMdf[rc.ticker] == tickKey].copy()
            for timeKey in ticker[rc.time].unique():
                ticket = ticker[ticker[rc.time] == timeKey].copy()
                ticket["Cloid"] = f"SIMTick_{i}"
                newdf = newdf.append(ticket)
                i = i + 1

        # For each unique ticket ID (akaCloid), create a DataFrame and add it to a list of DataFrames
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


def local():
    fn = "C:/journal/trader/_20181203_December/_1203_Monday/trades.csv"
    if not os.path.exists(fn):
        print('try again')
    theDate = '20180323'
    settings = QSettings('zero_substance', 'structjour')
    ds = DasStatement('trades.csv', settings, theDate)
    ds.getTrades()


if __name__ == '__main__':
    notmain()
    # local()
