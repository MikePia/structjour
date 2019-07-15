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
import pandas as pd
import numpy as np


from journal.definetrades import ReqCol, FinReqCol
# from journal.dfutil import 
from journal.statements import findfiles as ff
from journal.dfutil import DataFrameUtil
from journal.pandasutil import InputDataFrame


# pylint: disable=C0103


from PyQt5.QtCore import QSettings

class DasStatement:
    def __init__(self, infile, settings, theDate, positions='positions.csv', df=None):
        self.settings = settings
        self.theDate = theDate
        self.infile = infile
        self.infile2 = positions
        self.positions = positions
        rc = FinReqCol()
        
        if isinstance(df, pd.DataFrame):
            self.df = df
        else:
            self.df = self.openDasFile()
        if not self.df.empty:
            DataFrameUtil.checkRequiredInputFields(self.df, ReqCol().columns)
            self.df = self.df[[rc.time, rc.ticker, rc.side, rc.price, rc.shares, rc.acct, rc.PL, rc.date, 'Cloid']]
            self.df[rc.bal] = np.nan
            self.df[rc.avg] = np.nan
            self.df[rc.oc] = ''

    def makeShortsNegative(self, df):
        ''' Fix the shares sold to be negative values.
        '''

        rc = ReqCol()

        for i, row in df.iterrows():
            if row[rc.side] != 'B' and row[rc.shares] > 0:
                df.at[i, rc.shares] = ((df.at[i, rc.shares]) * -1)
        return df

    def askUser(self, df):
        pass

    def figureUnbalancedBAPL(self, tdf):
        # Going to write this as I locate the different cases for each case cumulative
        # Then plan to re-write after all case types are found.
        rc = FinReqCol()
        LONG = True
        SHORT = False
        side = LONG
        tdf.reset_index(drop=True, inplace=True)
        foundPrimo = False
        success = False
        for i in range(len(tdf)):
            if tdf.at[i, rc.PL] != 0:
                # This is a closer
                average = (tdf.at[i, rc.PL] / tdf.at[i, rc.shares]) + tdf.at[i, rc.price]
                tdf.at[i, rc.avg] = average
                tdf.at[i, rc.oc] = 'C'
                side = SHORT if tdf.at[i, rc.shares] > 0 else LONG
                for j in range(i-1, -1, -1):
                    # Iterate backward to beginning trade of statement
                    if (side == LONG and tdf.at[j, rc.shares] > 0) or (
                        side == SHORT and tdf.at[j, rc.shares] < 0):
                        # opener
                        tdf.at[j, rc.oc] = 'O'
                        if tdf.at[j+1, rc.oc] == 'C':
                            tdf.at[j, rc.avg] = average
                            if math.isclose(tdf.at[j, rc.price], average, abs_tol=1e-5):
                                # I believe this means this is the opening trade and the unbalanced amount
                                # is held after and not before
                                assert j == 0
                                foundPrimo = True
                                balance = 0
                                for k in range(len(tdf)):
                                    balance = tdf.at[k, rc.shares] + balance
                                    tdf.at[k, rc.bal] = balance
                                    success = True
                    
        return tdf, success





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
                # Signifacant items to figure approach
                # 1) unbalanced shares -- Call figureUnbalancedBAPL
                # 2) Balanced shares in which the PL does not add up right -- 
                #    Call figureUnBalancedBAPL
                # 3) Balanced share in which the PL does add up but the Balance is wrong. (I don't
                #    think I have a single example of this or a way to detect it. In this case the
                #    average will = the price of the first trade but the share balance will differ.
                #    Plan9=Accept/ignore the error and catch it in the database entries. Neither
                #    PL nor daily review is affected
                # 4) For any tickers that figureUnbalancedBAPL fails, call askUserAboutPosition
                # 3) Everything else can be figured out here.
                tdf = act[act[rc.ticker] == symKey]
                tdf.sort_values([rc.date], inplace=True)
                if tdf[rc.shares].sum() != 0:
                    tdfx, success = self.figureUnbalancedBAPL(tdf)
                    if success:
                        newTrades = newTrades.append(tdfx)
                    else:
                        swingTrades = swingTrades.append(tdf)
                    break

                pastPrimo = False
                prevBalance = 0
                balance = 0

                LONG = True
                SHORT = False
                side = LONG

                # Figure balance first -- send to swing trade if PL does not match
                for i, row in tdf.iterrows():
                    prevBalance = balance
                    balance = balance + row[rc.shares]
                    tdf.at[i, rc.bal] = balance

                    # Check for a flipped position. The flipper is figured like Opener; the average
                    # changes, and no PL is taken 
                    if pastPrimo and side == LONG and balance < 0:
                        side = SHORT
                    elif pastPrimo and side == SHORT and balance > 0:
                        side = LONG

                    # This is the first transaction of a trade
                    # Set the side, set Open and avg == price 
                    if not pastPrimo and balance == row[rc.shares]:
                        if row[rc.shares] < 0:
                            side = SHORT
                        average = row[rc.price]
                        pastPrimo = True
                        tdf.at[i, rc.oc] = 'O'
                        tdf.at[i, rc.avg] = average

                    # Openers -- adding to the trade. The average changes
                    elif (pastPrimo and side and row[rc.shares] > 0) or (
                          pastPrimo and not side and row[rc.shares] < 0):
                        # Opening trade
                        tdf.at[i, rc.oc] = 'O'
                        average = ((average * prevBalance) + (row[rc.shares] * row[rc.price])) / balance
                        tdf.at[i, rc.avg] = average

                    # Closers, set Close, check that PL matches, if not send to SwingTrade
                    elif pastPrimo:
                        # Closing trade
                        tdf.at[i, rc.avg] = average
                        avgFig = (average - row['Price']) * row[rc.shares]
                        if not math.isclose(row[rc.PL], avgFig, abs_tol=1e-5):
                            swingTrades = swingTrades.append(tdf)
                            break
                            # raise ValueError('That  is a lot of exceptions for code fixin')
                        tdf.at[i, rc.oc] = 'C'
                        if balance == 0:
                            pastPrimo = False
                    else:
                        # Should be catching swing trades with the PL check in the closers excep
                        # for the ultra rare thing which I will have to painstakingly, with several
                        # fake statements, trigger in a system test
                        raise ValueError('Do not think this ever happens.... So what happened???')
                newTrades = newTrades.append(tdf)
        newTrades.reset_index(drop=True, inplace=True)
        swingTrades.reset_index(drop=True, inplace=True)
        return newTrades, swingTrades
                
    def askAboutSwingTrades(self, st):
        return st, False

    def figureBalance(self, df):

        rc = FinReqCol()

        reqcols = ['Symb', 'Account', 'Avgcost', 'Unrealized']
        positions = pd.DataFrame(columns=reqcols)
        if self.positions and os.path.exists(self.positions):
            positions = pd.read_csv(self.positions)
            print(positions)
            positions = positions[positions['Shares'] != 0]
            currentcols = list(positions.columns)
            if not set(reqcols).issubset(set(currentcols)):
                print('WARNING: positions table is missing the following required columns.')
                print(set(reqcols) - set(currentcols))
                positions = pd.DataFrame(columns=reqcols)
            else:
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
                LONG = True
                SHORT = False

                tdf = df[df[rc.ticker] == ticker]
                tdf = tdf.sort_values(rc.date, )

                # A closer may have 0 PL-- can't assume these are all of them
                balance = tdf[rc.PL].sum()
                if balance == 0:
                    balance = balance + tdf[rc.qty]
                    tdf[rc.bal] = balance
                print()
                newdf = newdf.append(tdf)
        return newdf
                



    def openDasFile(self):
        self.theDate = pd.Timestamp(self.theDate)
        self.infile = os.path.join(ff.getDirectory(self.theDate), self.infile)
        self.positions = os.path.join(ff.getDirectory(self.theDate), self.positions)
        print()
        print(self.infile)
        if not os.path.exists(self.infile):
            print('File does not exist', self.infile)
            return pd.DataFrame()
        self.settings.setValue('dasInfile', self.infile)

        print(self.positions)
        df = pd.DataFrame()
        if not os.path.exists(self.positions):
            print('File does not exist', self.positions)
        else:
            self.settings.setValue('dasInfile2', self.positions)
        df = pd.read_csv(self.infile)

        if 'Date' not in df.columns:
            df['Date'] = np.nan
            df = self.createDateField(df)
        df = self.makeShortsNegative(df)
        return df

    def createDateField(self, df):
        for i, row in df.iterrows():
            dd = self.theDate
            tt = pd.Timestamp(row.Time)
            daDate = pd.Timestamp(dd.year, dd.month, dd.day, tt.hour, tt.minute, tt.second)
            df.at[i, 'Date'] = daDate
        return df

    def getTrades(self, listDf=None):
        '''
        Create an alternate dataFrame by ticket. For large share sizes this may have dramatically
        fewer transactions. 
        :params listDf: Normally leave blank. If used, listDf should be the be a list of DFs.
        :return: The DataFrame created version of the data.
        :side effects: Saves a csv file of all transactions as single ticket transactions to
                        the settings inpathfile
        '''
        # TODO: Add the date to the saved file name after we get the date sorted out.
        if not listDf:
            listDf = self.getListOfTicketDF()

        newDF = DataFrameUtil.createDf(listDf[0], 0)

        for tick in listDf:
            t = self.createSingleTicket(tick)
            newDF = newDF.append(t)

        newinfile = "tradesByTicket.csv"
        newopf = os.path.join(ff.getDirectory(self.theDate), newinfile)
        newDF.to_csv(newopf)
        self.settings.setValue('infile', newinfile)
        self.settings.setValue('inpathfile', newopf)
        newDF = self.figureBalance(newDF)

        return newDF

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

        newDf = DataFrameUtil.createDf(tickTx, 0)

        oneRow = tickTx.sort_values([rc.time, rc.price]).head(1)
        newDf = newDf.append(oneRow)
        newDf.copy()

        newDf[rc.price] = avgPrice
        newDf[rc.shares] = totalShares
        newDf[rc.PL] = totalPL
        return newDf

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

        dframe = self.df
        # if len(dframe.Cloid.apply(lambda x: isinstance(x, str))) < 1 :
        SIMdf = dframe[dframe['Cloid'] == "AUTO"]
        for i, dummy in SIMdf.iterrows():
            tickName = "SIMTick_{0}".format(i)
            SIMdf.at[i, "Cloid"] = tickName

        #For each unique ticket ID (akaCloid), create a DataFrame and add it to a list of DataFrames
        listOfTickets = list()
        for ticketID in dframe.Cloid.unique():
            if ticketID == "AUTO":
                continue
            # Retrieves all rows that match the ticketID
            t = dframe[dframe['Cloid'] == ticketID]
            listOfTickets.append(t)
        # Combine the two above into a python list of DataFrames

        for simTkt in SIMdf.Cloid.unique():
            t = SIMdf[SIMdf['Cloid'] == simTkt]
            listOfTickets.append(t)

        return listOfTickets


def notmain():
    d = "20190709"
    infile = 'trades.csv'
    settings = QSettings('zero_substance', 'structjour')
    ds = DasStatement(infile, settings, d)
    df = ds.getTrades()
    idf = InputDataFrame()
    trades, success = idf.processInputFile(df, settings.value('theDate'))


if __name__ == '__main__':
    notmain()

