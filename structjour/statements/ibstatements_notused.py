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
Unused methods that I am unwilling to trash entirely:

@author: Mike Petersen
@creation_data: 01/30/20

'''

import logging
import math
import os
import urllib.request

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from structjour.colz.finreqcol import FinReqCol
from structjour.dfutil import DataFrameUtil
from structjour.statements.ibstatementdb import StatementDB

# pylint: disable = C0103


def readit(url):
    '''Copied this from statement.py. I think this will be its home-- '''
    data = ''
    if url.lower().startswith('http:'):
        data = urllib.request.urlopen(url).read()
    else:
        assert os.path.exists(url)
        with open(url) as f:
            data = f.read()
    return data


class IbStatement_deprecated:
    '''
    Hold the column names for tables in Flex Queries. The names are a subset of the possible
    columns.
    '''

    # Not sure there is a difference between T_FLEX and TRADE
    # Going to attempt to treat CSV and Html version of activity statements the same once
    # the initial dataframes are created. For the subset of 3-4 tables we view, should be possible.
    I_TYPES = ["A_FLEX", "T_FLEX", "ACTIVITY", "TRADE"]
    def __init__(self, db=None):

        self.account = None
        self.statementname = None
        self.beginDate = None
        self.endDate = None
        self.inputType = None
        self.broker = None
        self.db = db
        self.rc = FinReqCol()

    def parseTitle(self, t):
        '''
        The html title tag of the activity statement contains statement info. There are no specs to
        the structure of the thing. So on failure, raise exceptions then fix it.
        '''
        result = t.split('-')
        if len(result) == 2:

            t = result[0]
            broker = result[1].strip()
        elif len(result) == 3:
            t = result[0]
            endDate = result[1].strip()
            broker = result[2].strip()
            try:
                self.endDate = pd.Timestamp(endDate).date()
            except ValueError:
                raise ValueError('Failed to parse the statement date:', t)

        # broker = broker.strip()
        self.broker = broker
        t = t.strip()
        t = t.split(' ')

        # The different lengths accout for Statement titles with different numbers of words, 1,
        # 2, or 3
        if len(t) == 7:
            account = t[0]
            sname = ''.join([t[1], t[2], t[3]])
            theDate = ' '.join([t[4], t[5], t[6]])
        elif len(t) == 6:
            account = t[0]
            sname = ' '.join([t[1], t[2]])
            theDate = ' '.join([t[3], t[4], t[5]])
        elif len(t) == 5:
            account = t[0]
            sname = t[1]
            theDate = ' '.join([t[2], t[3], t[4]])
        else:
            raise ValueError('Failed to parse the statement date')

        try:

            self.beginDate = pd.Timestamp(theDate).date()
            self.account = account
            self.statementname = sname

        except Exception:
            raise ValueError('Failed to parse the statement date')

    # Conversion stuff
    def combinePartialsHtml(self, df):
        '''
        Combine the partial entries in a trades table. The Html refers to the origin of the table.
        This is really more of a removing the details than combining them. This is a table without
        a DataDiscriminator or LevelOfDetail column. The Partials were identified in html with
        css and js and the user identifies them with expanding thingys. So woopdy do for that. The
        discriminator now is equal[DateTime, Codes, Symbol](Codes must include a P). The first of
        the bunch (with the javascript expanding thingy) has the summary Quantity, 'the rest' add
        up to the first. Filter out 'the rest.'
        '''
        newdf = pd.DataFrame()
        hasPartials = False
        rc = self.rc
        tickers = df[rc.ticker].unique()
        for tickerKey in tickers:
            if tickerKey.lower().startswith('closed') or tickerKey.lower().startswith('wash sale'):
                hasPartials = True
        if not hasPartials:
            return df

        for tickerKey in df[rc.ticker].unique():
            ticker = df[df[rc.ticker] == tickerKey]
            if len(tickerKey) > 6:
                # This is probably not a ticker assert to verify
                for code in ticker[rc.oc].unique():
                    assert code.find('O') == -1
                    assert code.find('C') == -1
                    assert code.find('P') == -1
                continue

            codes = ticker[rc.oc].unique()
            for code in codes:
                parts = ticker[ticker[rc.oc] == code]
                if code.find('P') > -1:
                    if len(parts) == 1:
                        pass

                    else:
                        addme = []
                        curTotal = 0

                        for count, (i, row) in enumerate(parts.iterrows()):
                            share = int(row[rc.shares])
                            if curTotal == 0:
                                curTotal = share
                                addme.append(count)
                            else:
                                curTotal = curTotal - share
                        assert curTotal == 0
                        x = 3
                        for x in addme:
                            newdf = newdf.append(parts.iloc[x])
                else:
                    newdf = newdf.append(parts)

        return newdf

    def doctorHtmlTables(self, tabd):
        '''
        Fix the idiosyncracies in the tables from an html IB Statement
        '''
        rc = self.rc
        keys = list(tabd.keys())
        for key in keys:
            if key in ['OpenPositions', 'Transactions', 'Trades', 'LongOpenPositions',
                       'ShortOpenPositions']:
                df = tabd[key]
                df = df[df['Symbol'].str.startswith('Total') is False]
                df = df.iloc[2:]
                # Using 'tbl' prefix to identify the html specific table
                ourcols = self.getColsByTabid('tbl' + key)
                if ourcols:
                    ourcols, missingcols = self.verifyAvailableCols(list(df.columns), ourcols,
                                                                    'tbl' + key)
                    df = df[ourcols]
                if key == 'Trades':
                    df = df.rename(columns={'Symbol': rc.ticker, 'Quantity': rc.shares, 'Acct ID': rc.acct, 'Trade Date/Time': 'DateTime',
                                            'Comm': rc.comm})
                    df = self.unifyDateFormat(df)
                    df = self.combineOrdersByTime(df)

                if key == 'Transactions':
                    df = df.rename(columns={'Symbol': rc.ticker, 'Date/Time': 'DateTime',
                                            'T. Price': rc.price, 'Comm/Fee': rc.comm,
                                            'Code': rc.oc, 'Quantity': rc.shares})

                    df[rc.acct] = self.account
                    df = self.fixNumericTypes(df)
                    df = self.combinePartialsHtml(df)
                    df = self.unifyDateFormat(df)
                    df = self.combineOrdersByTime(df)
                    key = 'Trades'
                else:
                    # small cringe
                    df = self.fixNumericTypes(df)
                tabd[key] = df.copy()

            elif key == 'AccountInformation':
                tabd[key].columns = ['Field Name', 'Field Value']

            if key in ['LongOpenPositions', 'ShortOpenPositions']:
                t = tabd[key]

                if tabd[key]['Mult'].dtype == np.float:
                    t = tabd[key][tabd[key]['Mult'] == 1]
                else:
                    t = tabd[key][tabd[key]['Mult'] == '1']

                if 'OpenPositions' in tabd.keys():
                    tabd['OpenPositions'] = tabd['OpenPositions'].append(t)
                else:
                    tabd['OpenPositions'] = t.copy()
                del tabd[key]
        if self.beginDate:
            if not self.endDate:
                self.endDate = self.beginDate
        else:
            if 'Trades' in tabd.keys():
                beg = tabd['Trades']['DateTime'].min()
                end = tabd['Trades']['DateTime'].max()
                try:
                    self.beginDate = pd.Timestamp(beg).date()
                    self.endDate = pd.Timestamp(end).date()
                except ValueError:
                    logging.warning('Failed to get date from trades file')
            assert self.beginDate
            assert self.endDate
        if 'Transactions' in tabd.keys():
            del tabd['Transactions']

        if 'OpenPositions' in tabd.keys() and self.endDate:
            tabd['OpenPositions']['Date'] = self.endDate.strftime("%Y%m%d")
            tabd['OpenPositions']['Account'] = self.account

        return tabd

    def openIBStatementHtml(self, infile):
        '''
        Open an IB Statement in html form
        '''
        if not os.path.exists(infile):
            return
        soup = BeautifulSoup(readit(infile), 'html.parser')
        tbldivs = soup.find_all("div", id=lambda x: x and x.startswith('tbl'))
        title = soup.find('title').text
        self.parseTitle(title)
        tables = dict()
        tablenames = dict()
        for tableTag in tbldivs:
            continueit = True
            tabKey = ''
            for key in ['tblAccountInformation', 'tblOpenPositions', 'tblLongOpenPositions',
                        'tblShortOpenPositions', 'tblTransactions', 'tblTrades']:
                if tableTag['id'].startswith(key):
                    continueit = False
                    tabKey = key[3:]
                    break
            if continueit:
                continue

            tab = tableTag.find("table")
            if not tab:
                continue
            df = pd.read_html(str(tab))
            assert len(df) == 1
            df = df[0]  # .replace(np.nan, '')
            tables[tabKey] = df
        if 'Transactions' not in tables.keys() and 'Trades' not in tables.keys():
            msg = 'The statment lacks a trades table.'
            return dict(), msg
        self.doctorHtmlTables(tables)

        posTab = None
        if 'OpenPositions' in tables.keys():
            posTab = tables['OpenPositions']
            tables['Trades'] = self.figureBAPL(tables['Trades'], posTab)

            ibdb = StatementDB(source='IB', db=self.db)
            ibdb.processStatement(tables['Trades'], self.account, self.beginDate, self.endDate, openPos=posTab)
            for key in tables:
                tablenames[key] = key
            tablenames[tabKey] = tabKey
            return tables, tablenames
        return dict(), 'This statement lacks any overnight information.'

    # Conversion stuff
    def combinePartialsFlexTrade(self, t):
        '''
        The necessity of a new method to handle this is annoying...BUT gdmit, The Open/Close info
        is not in any of the available fields. Instead, a less rigorous system is used based on
        OrderID
        '''
        lod = t['LevelOfDetail'].unique()
        if len(lod) > 1:
            assert ValueError('I need to see this')
        if lod[0].lower() != 'execution':
            assert ValueError('I need to see this')

        t = t[t['LevelOfDetail'].str.lower() == 'execution']
        newdf = pd.DataFrame()
        for tickerKey in t['Symbol'].unique():
            ticker = t[t['Symbol'] == tickerKey]
            # ##### New Code
            ticketKeys = ticker['OrderID'].unique()
            for ticketKey in ticketKeys:
                ticket = ticker[ticker['OrderID'] == ticketKey]
                if len(ticket) > 1:
                    codes = ticket['Codes']
                    for code in codes:
                        assert code.find('P') > -1

                    thisticket = DataFrameUtil.createDf(ticket.columns, 1)
                    net = 0.0
                    # Need to figure the average price of the transactions and sum of quantity
                    # and commission
                    for i, row in ticket.iterrows():
                        net = net + (float(row['Price']) * int(row['Quantity']))
                    for col in list(thisticket.columns):
                        if col not in ['Quantity', 'Price', 'Commission']:
                            thisticket[col] = ticket[col].unique()[0]
                    thisticket['Quantity'] = ticket['Quantity'].map(int).sum()
                    thisticket['Commission'] = ticket['Commission'].map(float).sum()
                    thisticket['Price'] = net / ticket['Quantity'].map(int).sum()
                    newdf = newdf.append(thisticket)

                else:
                    newdf = newdf.append(ticket)
        return newdf

    def cheatForBAPL(self, t):
        '''
        Check the db to find at least one trade for each ticker that matches a trade in t and get
        the balance. Then set the balance for that ticker
        :return: Either a df that includes balance for all trades or an empty
        '''
        # TODO This is the third of three methods that do similar things. Its a bit complex and
        # is bound to produce errors. Eventually, this method, figureBAPL and figureAPL should be
        # combined or at least share code.

        rc = self.rc
        ibdb = StatementDB(db=self.db, source='IB')
        t[rc.bal] = np.nan
        t[rc.avg] = np.nan
        t[rc.PL] = np.nan
        newdf = pd.DataFrame()
        for ticker in t[rc.ticker].unique():

            LONG = True
            SHORT = False

            tdf = t[t[rc.ticker] == ticker]
            tdf = tdf.sort_values(['DateTime'])
            tdf.reset_index(drop=True, inplace=True)
            for i, row in tdf.iterrows():
                x = ibdb.findTrades(row['DateTime'], row[rc.ticker], row[rc.price], row[rc.shares], row[rc.acct])
                # Its possible this can return more than one trade, if it does, note that they share
                # everything but balance
                if x:
                    tdf.at[i, rc.bal] = x[0][3]
                    break
            started = False
            balance = 0
            for i, row in tdf.iterrows():
                if not math.isnan(tdf.at[i, rc.bal]):
                    started = True
                    balance = row[rc.bal]
                elif started:
                    balance = row[rc.shares] + balance
            offset = balance
            if started:
                pastPrimo = False
                side = LONG
                balance = offset
                for i, row in tdf.iterrows():
                    quantity = row[rc.shares]
                    if pastPrimo and side == LONG and balance < 0:
                        side = SHORT
                    elif pastPrimo and side == SHORT and balance > 0:
                        side = LONG

                    prevBalance = balance

                    tdf.at[i, rc.bal] = row[rc.shares] + balance
                    balance = tdf.at[i, rc.bal]

                    # This the first trade Open; average == price and set the side-
                    if not pastPrimo and balance == row[rc.shares]:

                        pastPrimo = True
                        average = row[rc.price]
                        tdf.at[i, rc.avg] = average
                        side = LONG if row[rc.shares] >= 0 else SHORT

                    # Here are openers -- adding to the trade; average changes
                    # newAverage = ((prevAverage * prevBalance) + (quantity * price)) / balance
                    elif (pastPrimo and side is LONG and quantity >= 0) or (
                          pastPrimo and side is SHORT and quantity < 0):
                        newAverage = ((average * prevBalance) + (quantity * row[rc.price])) / balance
                        average = newAverage
                        tdf.at[i, rc.avg] = average

                    # Here are closers; PL is figured and check for trade ending
                    elif pastPrimo:
                        # Close Tx, P/L is figured on CLOSING transactions only
                        tdf.at[i, rc.avg] = average
                        tdf.at[i, rc.PL] = (average - row[rc.price]) * quantity
                        if balance == 0:
                            pastPrimo = False
                    else:
                        # This should be a first trade for this statmenet/Symbol. Could be Open or
                        # Close. We are lacking the previous balance so cannot reliably figure the
                        # average.
                        # logging.debug(f'''There is a  trade for {row[rc.ticker]} that lacks a transaction in this statement''')
                        pass

                newdf = newdf.append(tdf)
            else:
                # If the balance for any trade is not found, return empty.
                return pd.DataFrame()
        return newdf

    def openTradeFlexCSV(self, infile):
        '''
        Open a Trade flex statement csv file. This is a single table file. The headers are in the
        top row so just reading it with read_csv will collect them. This table is missing the
        Open/Close data.
        '''
        df = pd.read_csv(infile)
        self.inputType = 'T_FLEX'
        rc = self.rc

        # This one table file has no tableid
        currentcols = list(df.columns)
        ourcols = self.getColsByTabid('FlexTrades')
        ourcols, missingcols = self.verifyAvailableCols(currentcols, ourcols, 'DailyTrades')
        df = df[ourcols].copy()
        df = df.rename(columns={'Date/Time': 'DateTime', 'Code': 'Codes',
                                'ClientAccountID': 'Account'})

        lod = df['LevelOfDetail'].str.lower().unique()
        if 'order' in lod:
            pass
        elif 'execution' in lod:
            if 'OrderID' in missingcols:
                msg = 'This table contains transaction level data but lacks OrderID.'
                return dict(), msg
            else:
                # df = df.rename(columns={'OrderID': 'IBOrderID'})
                df = self.combinePartialsFlexTrade(df)
        else:
            # TODO 2019-07-03 if this never trips, blitz the statmement for just in case
            raise ValueError("If this trips, detemine if the data is savlagable")
        # if len(df) < 1:
        if df.empty:
            msg = 'This statement has no trades.'
            return dict(), msg

        # The Codes col acks the OpenClose codes so were done with it.
        df = df.drop(['LevelOfDetail', 'Codes'], axis=1)
        df = self.unifyDateFormat(df)
        self.account = df['Account'].unique()[0]

        beg = df['DateTime'].min()
        end = df['DateTime'].max()
        assert beg
        assert end
        try:
            self.beginDate = pd.Timestamp(beg).date()
            self.endDate = pd.Timestamp(end).date()
        except ValueError:
            msg = f'Unknown date format error: {beg}, {end}'
            return dict(), dict()
        df = df.rename(columns={'Symbol': rc.ticker, 'Quantity': rc.shares})
        x = self.cheatForBAPL(df)
        if not x.empty:
            ibdb = StatementDB(db=self.db, source='IB')
            ibdb.processStatement(x, self.account, self.beginDate, self.endDate)
            df = x.copy()
            return {'Trades': df}, {'Trades': 'Trades'}

        return {'Trades': df}, {'Trades': 'Trades'}
