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
Opens an ib statement and, if possible, stores the trades in the db. The thing that prevents db
placement is lack of balance info-- overnight trades without a positions table. This occurs in
single table statements that have only the trades table. For custom Activity statements, its a
setup choice at the IB website.

In most cases, its is probably possible to figure out the balance by querying the trades in the
db. The code to do that is not there yet.
@author: Mike Petersen
@creation_data: 07/8/19
'''

import math
import os
import urllib.request

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from structjour.colz.finreqcol import FinReqCol
from structjour.dfutil import DataFrameUtil
from structjour.statements.findfiles import getDirectory, findFilesSinceMonth, findFilesInDir, getBaseDir
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



class IbStatement:
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

    def figureBAPL(self, tt, tos):
        '''
        Figure Balance, Average price and PL
        '''
        rc = self.rc
        tt[rc.bal] = np.nan
        tt[rc.avg] = np.nan
        tt[rc.PL] = np.nan
        newdf = pd.DataFrame()

        for acct in tt[rc.acct].unique():
            accounts = tt[tt[rc.acct] == acct]
        
            for ticker in accounts[rc.ticker].unique():

                LONG = True
                SHORT = False

                tdf = tt[tt[rc.ticker] == ticker]
                tdf = tdf.sort_values(['DateTime'])
                tdf.reset_index(drop=True, inplace=True)
                offset = tdf[rc.shares].sum()
                holding = 0
                if ticker in tos['Symbol'].unique():
                    oset = tos[tos['Symbol'] == ticker]
                    holding = int(oset['Quantity'].unique()[0])
                    offset = offset - holding
                balance = -offset

                #Discriminator for first opening transaction
                # TODO account for account in tos
                primo = False
                side = LONG
                
                # Figure Balance first -- adjust offset for overnight
                for i, row in tdf.iterrows():
                    quantity = row[rc.shares]
                    prevBalance = balance
                    balance = balance + quantity
                    tdf.at[i, rc.bal] = balance

                    # Check for a flipped position. The flipper is figured like Opener; the average
                    # changes, and no PL is taken 
                    if primo and side == LONG and balance < 0:
                        side = SHORT
                    elif primo and side == SHORT and balance > 0:
                        side = LONG

                    # This the first trade Open; average == price and set the side- 
                    if not primo and balance == row[rc.shares]:
                        
                        primo = True
                        average = row[rc.price]
                        tdf.at[i, rc.avg] = average
                        side = LONG if row[rc.shares] >= 0 else SHORT

                    # Here are openers -- adding to the trade; average changes
                    # newAverage = ((prevAverage * prevBalance) + (quantity * price)) / balance
                    elif (primo and side is LONG and quantity >= 0) or (
                        primo and side is SHORT and quantity < 0):
                        newAverage = ((average * prevBalance) + (quantity * row[rc.price])) / balance
                        average = newAverage
                        tdf.at[i, rc.avg] = average

                    # Here are closers; PL is figured and check for trade ending
                    elif primo:
                        # Close Tx, P/L is figured on CLOSING transactions only
                        tdf.at[i, rc.avg] = average
                        tdf.at[i, rc.PL] = (average - row[rc.price]) * quantity
                        if balance == 0:
                            primo = False
                    else:
                        # This should be the first trades for this statmenet/Symbol. 
                        # We are lacking the previous average so cannot reliably figure the
                        # average or PL. (IB uses Cost basis accounting and their PL may be wrong
                        #  for our purposes)
                        # print(f'''There is a trade for {row[rc.ticker]} that lacks a tx.''')
                        pass


                assert tdf.iloc[-1][rc.bal] == holding
                newdf = newdf.append(tdf)
        newdf = newdf.sort_values([rc.acct, rc.ticker, 'DateTime'])
        newdf.reset_index(drop=True, inplace=True)
        return newdf

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

        except:
            raise ValueError('Failed to parse the statement date')

    #Conversion stuff
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
                df = df[df['Symbol'].str.startswith('Total') == False]
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
                    print('Failed to get date from trades file')
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

    def openIBStatement(self, infile):
        '''
        Open an IB Statement in either csv or html form
        '''
        if os.path.splitext(infile)[1] == '.csv':
            return self.openIBStatementCSV(infile)
        # elif os.path.splitext(infile)[1] == '.html':
        #     return self.openIBStatementHtml(infile)
        else:
            # msg = 'Only htm or csv files are recognized'
            msg = 'Only csv files are currently supported'
            return dict(), msg

    def openIBStatementCSV(self, infile):
        '''
        Identify a csv file as a type of IB Statement and send to the right place to open it
        '''
        df = pd.read_csv(infile, names=[x for x in range(0, 100)])
        # df = df
        if df.iloc[0][0] == 'BOF'  or df.iloc[0][0] == 'HEADER':
            # This is a flex activity statement with multiple tables
            self.inputType = "A_FLEX"
            return self.openActivityFlexCSV(df)

        elif df.iloc[0][0] == 'ClientAccountID':
            return dict(), "Unsupported file type. Lacks all overnight information."
            # return self.openTradeFlexCSV(infile)

        elif df.iloc[0][0] == 'Statement':
            # This is a multi table statement like a default statement
            self.inputType = 'ACTIVITY'
            return self.getTablesFromDefaultStatement(df)
        return dict(), dict()

    def fixNumericTypes(self, t):
        rc = self.rc
        if 'Quantity' in t.columns and t['Quantity'].any():
            if isinstance(t['Quantity'].iloc[0], str):
                t['Quantity'] = t['Quantity'].str.replace(',', '')
            t['Quantity'] = pd.to_numeric(t['Quantity'], errors='coerce')
        elif rc.shares in t.columns and t[rc.shares].any():
            if isinstance(t[rc.shares].iloc[0], str):
                t[rc.shares] = t[rc.shares].str.replace(',', '')
            t[rc.shares] = pd.to_numeric(t[rc.shares], errors='coerce')
        if rc.price in t.columns:
            t[rc.price] = pd.to_numeric(t[rc.price], errors='coerce')
        if rc.comm in t.columns:
            t[rc.comm] = pd.to_numeric(t[rc.comm], errors='coerce')
        return t

    def unifyDateFormat(self, df):
        '''
        Ib sends back differnt formats from different files. All statement processing should call
        this method.
        '''
        df['DateTime'] = df['DateTime'].str.replace('-', '').str.replace(
            ':', '').str.replace(',', ';').str.replace(' ', '')
        if df.any()[0]:
            assert len(df.iloc[0]['DateTime']) == 15
        return df

    def parseDefaultCSVPeriod(self, period):
        '''
        The printed perod at the top of the staement comes in at least 3 formats. I have found no
        specs. If this fails, the program will set covered dates by the min and max trade dates.
        '''
        try:
            test = period.split('-')
            if len(test) == 1:
                # Expecting a full date like January 25, 2019
                self.beginDate = pd.Timestamp(period).date()
            elif len(test) == 3:
                # Expecting 14-Jun-9 or 2019-01-03
                self.beginDate = pd.Timestamp(period).date()
            else:
                # Expecting a range like January 1, 2019 - January 31, 2019
                self.beginDate = test[0].strip()
                self.endDate = test[1].strip()
                self.beginDate = pd.Timestamp(self.beginDate).date()
                self.endDate = pd.Timestamp(self.endDate).date()
        except ValueError:
            msg = f'Failed to parse the statement date period: {period}'
            print(msg)

    def combinePartialsDefaultCSV(self, t):
        if 'order' in t['DataDiscriminator'].str.lower().unique():
            t = t[t['DataDiscriminator'].str.lower() == 'order'].copy()
        elif 'execution' in t['DataDiscriminator'].str.lower():
            # TODO
            raise ValueError('Need to implement combine partials for the default statement')
        elif 'trade' in t['DataDiscriminator'].str.lower():
            raise ValueError('Need to either implement a cludge or disable the statement')

        t = self.fixNumericTypes(t)

        return self.combineOrdersByTime(t)

    def doctorDefaultCSVStatement(self, tables, mcd):
        '''
        Fix up the idiosyncracies in the tables from a default csv statement'''
        # for key in tables:
        rc = self.rc
        if 'Statement' in tables.keys():
            t = tables['Statement']
            self.broker = t[t['Field Name'] == 'BrokerName']['Field Value'].unique()[0]
            self.statementname = t[t['Field Name'] == 'Title']['Field Value'].unique()[0]
            period = t[t['Field Name'] == 'Period']['Field Value'].unique()[0]
            self.parseDefaultCSVPeriod(period)
            tables['Statement'] = t

        if 'AccountInformation' in tables.keys():
            self.account = tables['AccountInformation'].iloc[1][1]
            test = self.account.split(' ')
            if len(test) > 1:
                self.account = test[0]

        if 'OpenPositions' in tables.keys():
            d = self.endDate if self.endDate else self.beginDate
            t = tables['OpenPositions']
            t['Date'] = d.strftime('%Y%m%d')
            if 'ClientAccountID' in mcd['OpenPositions']:
                if self.account:
                    t['Account'] = self.account
            else:
                t = t.rename(
                    columns={'ClientAccountID': 'Account'})
            t['Quantity'] = t['Quantity'].str.replace(',', '')
            t['Quantity'] = pd.to_numeric(t['Quantity'], errors='coerce')
            tables['OpenPositions'] = t
        if 'Trades' in tables.keys():
            t = tables['Trades']
            t = t.rename(columns={'T. Price': rc.price, 'Comm/Fee': rc.comm, 'Symbol': rc.ticker,
                                  'Code': rc.oc, 'Date/Time': 'DateTime', 'Quantity': rc.shares})
            t[rc.acct] = self.account
            t = self.unifyDateFormat(t)
            t = self.combinePartialsDefaultCSV(t)

            t = t.drop('DataDiscriminator', axis=1)

            tables['Trades'] = t
        return tables

    def getTablesFromDefaultStatement(self, df):
        '''
        From a default Activity statement csv, retrieve AccountInformation, OpenPositions, and
        Trades
        '''
        # df = pd.read_csv(infile, header=range(0,15))
        keys = df[0].unique()
        tables = dict()
        tablenames = dict()
        mcd = dict()
        for key in keys:
            if key not in ['Statement', 'Account Information', 'Open Positions',
                           'Short Open Positions', 'Long Open Positions', 'Trades']:
                continue

            t = df[df[0] == key]
            headers = t[t[1].str.lower() == 'header']
            if len(headers) > 1:
                msg = f'This statement has {len(headers)} {key} tables.'
                msg = msg + '\nMulti account statment not supported.'
                return dict(), msg
            assert t.iloc[0][1].lower() == 'header'
            currentcols = list(t.columns)
            headers = headers.iloc[0]
            t = t[t[1].str.lower() == 'data']
            assert len(currentcols) == len(headers)
            t.columns = headers
            ourcols = self.getColsByTabid(key)
            ourcols, missingcols = self.verifyAvailableCols(headers, ourcols, key)
            if not ourcols:
                continue
            t = t[ourcols]

            if key in ['Long Open Positions', 'Short Open Positions']:
                t = t[t['DataDiscriminator'].str.lower() == 'summary']
                key = 'OpenPositions'
                ourcols = self.getColsByTabid(key)
                if ourcols:
                    ourcols, missingcols = self.verifyAvailableCols(
                        list(t.columns), ourcols, key)
                    t = t[ourcols].copy()

                if 'OpenPositions' in tables.keys():
                    if not set(tables['OpenPositions'].columns) == set(t.columns):
                        msg = 'A Programmer thing-- see it occur before I write code'
                        raise ValueError(msg)

                    tables['OpenPositions'] = tables['OpenPositions'].append(t)
                    tablenames['OpenPositions'] = 'OpenPositions'
                    continue
                else:
                    key = 'OpenPositions'

            key = key.replace(' ', '')
            mcd[key] = missingcols
            tables[key] = t
            tablenames[key] = key

        tables = self.doctorDefaultCSVStatement(tables, mcd)
        if 'Trades' not in tables.keys():
            # This should maybe be a dialog
            msg = 'The statment lacks a trades table'
            return dict(), msg

        if self.account is None:
            msg = '''This statement lacks an account number. Can't add it to the database'''
            return dict(), msg
        ibdb = StatementDB(self.db, source='IB')
        openpos = None
        if 'OpenPositions' in tables.keys():
            openpos = tables['OpenPositions']
            tables['Trades'] = self.figureBAPL(tables['Trades'], tables['OpenPositions'])
            # Here we need to combine with cheatForBAPL to accomodate statements with no
            # OpenPositions
            ibdb.processStatement(tables['Trades'], self.account, self.beginDate, self.endDate,
                                  openPos=openpos)
        return tables, tablenames

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
        ibdb = StatementDB(source='IB')
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
                        # print(f'''There is a  trade for {row[rc.ticker]} that lacks a transaction in this statement''')
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
            ibdb = StatementDB(source='IB')
            ibdb.processStatement(x, self.account, self.beginDate, self.endDate)
            df = x.copy()
            return {'Trades': df}, {'Trades': 'Trades'}

        # print("Trades are not added to the database")
        return {'Trades': df}, {'Trades': 'Trades'}

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

    def combinePartialsFlexCSV(self, t):
        '''
        In flex Statements, the TRNT (Trades) table input might be in transacations instead of
        tickets identified by LevelOfDetail=EXECUTION without the summary rows identified by
        LevelOfDetail=ORDERS. This is fixable (in both Activity statements and Trade statements)
        by changing Options to inclue Orders. If we have Executions only, we need to recombine
        the partials as identified by IBOrderID. If we also lack that column, blitz the sucker.
        Its not that hard to get a new statment.
        New wrinkle. There are some orders that have the same datetime making any sort by time void
        and leaving the balance up to chance which is first. While these might be different orders
        by IB, the trader ordered them as a single ticket- and we will combine them.
        :t: Is a TRNT DataFrame. That is a Trades table from a CSV multi table doc in which TRNT
                 is the tableid.
        :assert: Tickets written at the exact same time are partials, identified by
                 Notes/Codes == P (change name to Codes) and by having a single Symbol
        :prerequisite: Must have the columns
                        ['Price', 'Commission', 'Quantity', 'LevelOfDetail', 'Codes']
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
            ##### New Code
            codes = ticker['Codes'].unique()
            for code in codes:
                if isinstance(code, float):
                # if math.isnan(code):
                    continue
                parts = ticker[ticker['Codes'] == code]
                ticketKeys = parts['IBOrderID'].unique()
                for ticketKey in ticketKeys:
                    ticket = parts[parts['IBOrderID'] == ticketKey]
                    if len(ticket) > 1:
                        thisticket = DataFrameUtil.createDf(ticket.columns, 1)
                        net = 0.0
                        # Need to figure the average price of the transactions and sum of
                        # quantity and commission
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

    def doctorActivityFlexTrades(self, t, missingcols):
        '''
        Deal with idiosyncracies;
        set uniform format in the Activity Flex Trades table (tableid = TRNT)
            1) Some statements' TRNT table include TradeDate and TradeTime seperately. Others may
               have the combined DateTime. And, maybe, some statements use Date/Time
            2) The missing possibly required fields are provided in missingcols
            3) Combine Open/CloseIndicator and Notes/Codes into Codes-- required if we need to
               combine partials
            4) LevelOfDetail may include ORDER and/or  EXECTION. We want the ORDER info but if
               we have only EXECUTION, combine the partials. One or the other is required.
            5) Set uniform columns names and date format.
        '''
        rc = self.rc
        # 1
        if 'Date/Time' in t.columns:
            raise ValueError('wtf ib!?!, Maybe you should hire me to do this stuff.')
            # t = t.rename(columns={'Date/Time': 'DateTime'})
        elif 'DateTime' in t.columns:
            pass
        elif 'TradeDate' and 'TradeTime' in t.columns:
            # The Time string in *some* IB statements lacks a beginning '0' for 9:30 etc. 
            for i, row in t.iterrows():
                if len(row['TradeTime']) == 5:
                    t.at[i, 'TradeTime'] = '0' + row['TradeTime']

            t['DateTime'] = t['TradeDate'].map(str) + ';' + t['TradeTime']
            t = t.drop(['TradeDate', 'TradeTime'], axis=1)
        else:
            msg = '\n'.join(['''This Activity Flex statement is missing order'
                               'time information. Please include the',
                               'Date/Time' column or ['TradeDate','TradeTime'] columns. '''])
            self.beginDate = None
            return pd.DataFrame(), msg

        # 2
        missingcols = set(missingcols) - set(['TradeDate', 'TradeTime', 'DateTime', 'Date/Time',
                                              'IBOrderID'])
        if missingcols:
            msg = f'Statment is missing cols: {list(missingcols)}'
            return pd.DataFrame, msg
        # 5
        t = t.rename(columns={'TradePrice': 'Price', 'IBCommission': 'Commission',
                              'ClientAccountID': 'Account'})

        # 3
        t['Codes'] = ''
        for i, row in t.iterrows():
            OC = row['Open/CloseIndicator']
            P = row['Notes/Codes']
            if isinstance(OC, float):
                OC = ''
            if isinstance(P, str):
                if (OC.find('O') > -1 and P.find('O') > -1) or (
                        OC.find('C') > -1 and P.find('C') > -1):
                    codes = P
                else:
                    codes = f'{OC};{P}'
            else:
                codes = OC
            t.at[i, 'Codes'] = codes
        t = t.drop(['Open/CloseIndicator', 'Notes/Codes'], axis=1)

        # 4
        t = self.fixNumericTypes(t)
        lod = [x.lower() for x in list((t['LevelOfDetail'].unique()))]
        if 'order' in lod:
            t = t[t['LevelOfDetail'].str.lower() == 'order']
        elif 'execution' in lod:
            if not 'IBOrderID' in t.columns:
                self.beginDate = None
                msg = '\n'.join(['This Activity Flex statement Includes EXECUTION level data'
                                 '(aka partials) To combine the partial executions',
                                 'into readable trades, the column "IBOrderID" must be included'
                                 'in the Flex Query Trades table. Alternately,',
                                 'select the Orders Options.'])
                return pd.DataFrame(), msg
            t = t[t['LevelOfDetail'].str.lower() == 'execution']



            t = self.combinePartialsFlexCSV(t)
        elif len(t) > 0:
            msg = '\n'.join(['This Activity Flex statement is missing partial execution data.'
                             'Please include the Orders or Execution Options for',
                             'the Trades Table in your Activity flex statement. '])
            return pd.DataFrame(), msg
        t = t.rename(columns={'Symbol': rc.ticker, 'Quantity': rc.shares, 'Codes': rc.oc})
        t = self.combineOrdersByTime(t)

        t = self.unifyDateFormat(t)
        dcolumns, mcolumns = self.verifyAvailableCols(
            list(t.columns), ['LevelOfDetail', 'IBOrderID', 'TradeDate'], 'utility')
        t = t.drop(dcolumns, axis=1)
        ###### Set all the right names here

        return t, ''

    def getFrame(self, fid, df):
        '''
        Retrieve the rows between (fid[0], fid[1]) in df
        :fid: A section identifier like ('BOF', 'EOF')
        '''
        x = df[df[0] == fid[0]]
        metadata = []
        ldf = []
        for i in range(0, len(x)):
            started = False
            # newdf = pd.DataFrame()
            data = []

            for j, row in df.iterrows():
                if row[0] == fid[0] and not started:
                    md = [x for x in row if isinstance(x, str)]
                    metadata.append(md)
                    started = True
                    continue
                elif started and row[0] != fid[1]:
                    data.append(row.values)
                    # newdf = newdf.append(row)
                elif started:
                    newdf = pd.DataFrame(data=data, columns=df.columns)
                    ldf.append(newdf)
                    break
        return ldf, metadata

    def doctorFlexTables(self, tables, mcd):
        '''
        Fix up the idiosyncracies in the tables in from an Activity Flex Statement
        '''
        if 'TRNT' in tables.keys():
            missingcols = mcd['TRNT']
            tables['TRNT'], m = self.doctorActivityFlexTrades(tables['TRNT'], missingcols)
            # A statement with no trades and a beginDate can update the ib_covered table. But w/o
            # the date or Trades, this statement has no use.
            if tables['TRNT'].empty and not self.beginDate:
                m = m + '\nThis statement has no trades and no begin or end date.'
                return dict(), m
        if 'ACCT' in tables.keys():
            tables['ACCT'] = tables['ACCT'].rename(columns={'ClientAccountID': 'Account'})
            self.account = tables['ACCT']['Account'].values[0]
        if 'POST' in tables.keys():
            # If the statement lacks date metadata, the next best thing is the the first and last
            # dates for trades
            d = self.endDate if self.endDate else self.beginDate if self.beginDate else None
            if d is None:
                # Bit of a catch 22 in the processing produces unsure  ???
                if 'TRNT' in tables.keys():
                    beginDate = tables['TRNT']['DateTime'].min()
                    endDate = tables['TRNT']['DateTime'].max()

            tables['POST']['Date'] = d.strftime('%Y%m%d')
            tables['POST'] = tables['POST'].rename(columns={'ClientAccountID': 'Account'})
        return tables, ''

    def openActivityFlexCSV(self, df):
        '''
        This will process a flex activity statement with headers and with or without  metadata. The
        metadata rows are itendified with BOF BOA BOS columns.
        Setting up to process multiple accounts but the table names are still messed up
        Raise error if multiple accounts are sent in for now
        '''

        tables = dict()
        tablenames = dict()
        mcd = dict()
        accounts = []
        ldf, filemetadata = self.getFrame(('BOF', 'EOF'), df)
        accountsmetadata = []
        if ldf and isinstance(ldf[0], pd.DataFrame):
            accounts, accountsmetadata = self.getFrame(('BOA', 'EOA'), ldf[0])
            if len(accounts) > 1:
                raise ValueError('Multiple accounts is not enabled for Ib Statement parsing')
            filemetadata = filemetadata[0]
            accountsmetadata = accountsmetadata[0]
        else:
            accounts.append(df)
        for dfa in accounts:
            if filemetadata:
                # self.account = filemetadata[1]
                self.statementname = filemetadata[2]
                beginDate = filemetadata[4]
                self.beginDate = pd.Timestamp(beginDate).date()
                endDate = filemetadata[5]
                self.endDate = pd.Timestamp(endDate).date()
            if accountsmetadata:
                self.account = accountsmetadata[1]

            tabids = dfa[1].unique()
            for tabid in tabids:
                t = dfa[dfa[1] == tabid]
                if 'BOS' in t[0].unique():
                    tab, tabmetadata = self.getFrame(('BOS', 'EOS'), t)
                    assert len(tab) == 1
                    assert len(tabmetadata) == 1
                    t = tab[0]
                    tabmetadata = tabmetadata[0]
                currentcols = list(t.columns)
                headers = list(t[t[0] == 'HEADER'].iloc[0])
                t = t[t[0] == 'DATA']
                assert len(currentcols) == len(headers)
                t.columns = headers
                ourcols = self.getColsByTabid(tabid)
                ourcols, missingcols = self.verifyAvailableCols(headers, ourcols, tabid)
                if not  ourcols:
                    continue
                t = t[ourcols]
                mcd[tabid] = missingcols

                # Assign to dict and return
                tables[tabid] = t.copy()
                tablenames[tabid] = tabid
            tables, msg = self.doctorFlexTables(tables, mcd)
            if not len(tables.keys()):
                # TODO When enabling multi accounts-- fix this to not return
                return tables, msg
            ibdb = StatementDB(source='IB')
            positions = None
            if 'POST' in tables.keys():
                positions = tables['POST']
                tables['TRNT'] = self.figureBAPL(tables['TRNT'], positions)
            ibdb.processStatement(tables['TRNT'], self.account, self.beginDate, self.endDate,
                                  openPos=positions)
        return tables, tablenames

    def getColsByTabid(self, tabid):
        '''
        Using the tableids from the Flex queries and other Statements, we are interetsed in these
        tables only and in the columns we define here only.
        The column headers are a subset as found in the input files. returns different
        column names in
            flex(TRNT)
            csv Activity Statements(Trades)
            html Activity statements (Transactions)
        Fixing the differences is not done here. From here we need the original names. If the names
        change (from IB), this process should catch it and raise an error.
        '''
        if tabid not in ['ACCT', 'POST', 'TRNT', 'Open Positions', 'OpenPositions', 'Statement',
                         'Account Information', 'Long Open Positions', 'Short Open Positions',
                         'Trades', 'FlexTrades', 'tblTrades', 'tblTransactions', 'tblOpenPositions',
                         'tblLongOpenPositions', 'tblShortOpenPositions']:
            return []
        if tabid == 'ACCT':
            return ['ClientAccountID', 'AccountAlias']

        if tabid in ['POST', 'Open Positions', 'OpenPositions', 'tblOpenPositions']:
            return ['ClientAccountID', 'Symbol', 'Quantity']


        if tabid in ['Long Open Positions', 'Short Open Positions']:
            # DataDiscriminator is temporary to filter results
            return ['ClientAccountID', 'Symbol', 'Quantity', 'DataDiscriminator']

        if tabid in ['tblLongOpenPositions', 'tblShortOpenPositions']:
            # Not a great data discriminator (Mult=='1')
            return ['ClientAccountID', 'Symbol', 'Quantity', 'Mult']

        # Trades table from fllex csv
        # It seems some statements use DateTime and others Date/Time. (not sure)  Baby sit it
        # with an exception to try to find out.
        if tabid == 'TRNT':
            return ['ClientAccountID', 'Symbol', 'TradeDate', 'TradeTime', 'Date/Time', 'DateTime',
                    'Quantity', 'TradePrice', 'IBCommission', 'Open/CloseIndicator', 'Notes/Codes',
                    'LevelOfDetail', 'IBOrderID']

        if tabid == 'Trades':
            return ['Symbol', 'Date/Time', 'Quantity', 'T. Price', 'Comm/Fee', 'Code',
                    'DataDiscriminator']

        if tabid == 'FlexTrades':
            return ['ClientAccountID', 'Symbol', 'Date/Time', 'Quantity', 'Price', 'Commission',
                    'Code', 'LevelOfDetail', 'OrderID']

        if tabid == 'tblTrades':
            return ['Acct ID', 'Symbol', 'Trade Date/Time', 'Quantity', 'Price', 'Comm']

        if tabid == 'tblTransactions':
            return ['Symbol', 'Date/Time', 'Quantity', 'T. Price', 'Comm/Fee', 'Code']

        ####### Activity Statement non flex #######
        if tabid in ['Statement', 'Account Information']:
            return ['Field Name', 'Field Value']

        if tabid.find('Positions') > -1:
            raise ValueError('Fix it!!!')

        raise ValueError('What did we not catch?')

    def verifyAvailableCols(self, flxcols, ourcols, tabname):
        '''
        Check flxcols against ourcols, remove any cols in ourcols that are missing in flxcols and
        send a warning
        :return: ourcols are the requested cols that exist, missing is complement
        '''
        missingcols = set(ourcols) - set(flxcols)
        if missingcols:
            for col in missingcols:
                ourcols.remove(col)
        return ourcols, missingcols


def notmain():
    ''' Run local stuff'''
    t = StatementDB(source='IB')
    t.popHol()

def localStuff():
    '''Run local stuff'''
    d = pd.Timestamp('2019-06-01')
    files = dict()
    # files['annual'] = ['U242.csv', getBaseDir]

    # files['stuff'] = ['U2.csv', getDirectory]
    # files['stuff'] = ['FlexMonth.csv', getDirectory]
    # files['flexAid'] = ['ActivityFlexMonth.369463.csv', getDirectory]
    # files['flexAid'] = ['ActivityFlexMonth.csv', getDirectory]
    # files['flexTid'] = ['TradeFlexMonth.csv', getDirectory]
    # files['activityDaily'] = ['ActivityDaily.663710.csv', getDirectory]
    # files['U242'] = ['U242.csv', getDirectory]
    files['csvtrades'] = ['644223.csv', getDirectory]
    # files['multi'] = ['MULTI', getDirectory]
    # files['activityMonth'] = ['CSVMonthly.644225.csv', getDirectory]
    # files['dtr'] = ['DailyTradeReport.html', getDirectory]
    # files['act'] = ['ActivityStatement.html', getDirectory]
    # files['atrade'] = ['trades.643495.html', getDirectory]

    das = 'trades.csv'                          # Search verbatim with searchParts=False
                                                # TODO How to reconcile IB versus DAS input?

    badfiles = []
    goodfiles = []
    for filekey in files:
        # fs = findFilesInDir(files[filekey][1](d), files[filekey][0], searchParts=True)
        fs = findFilesSinceMonth(d, files[filekey][0])
        for f in fs:
            ibs = IbStatement()
            x = ibs.openIBStatement(f)
            if x[0]:
                goodfiles.append(f)
                print("GOOD", f)
                # for key in x[0]:
                #     print(key, list(x[0][key].columns), len(x[0][key]))


            if x[1] and not x[0]:
                badfiles.append([f, x[1]])
                print("\nBAD", f, '\n', x[1])
            #     msg = f'\nStatement {f} \n{x[1]}'
            #     print(msg)
        # print()

if __name__ == '__main__':
    # notmain()
    localStuff()
