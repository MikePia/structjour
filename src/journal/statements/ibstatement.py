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
Re-implementing the ib statement stuff to get a general solution that can be stored in a db
@author: Mike Petersen
@creation_data: 06/15/19
'''

import math
import os
import sqlite3

from PyQt5.QtCore import QSettings, QDate, QDateTime
import numpy as np
import pandas as pd

from bs4 import BeautifulSoup
import urllib.request

from journal.stock.utilities import qtime2pd
from journal.dfutil import DataFrameUtil

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


def getMonthDir(daDate=None):
    settings = QSettings('zero_substance', 'structjour')
    if daDate:
        d = daDate
    else:
        d = settings.value('theDate')

    scheme = settings.value('scheme')
    journal = settings.value('journal')
    if not scheme or not journal:
        return None
    scheme = scheme.split('/')[0]

    if isinstance(d, (QDate, QDateTime)):
        d = qtime2pd(d)
    Year = d.year
    month = d.strftime('%m')
    MONTH = d.strftime('%B')
    day = d.strftime('%d')
    DAY = d.strftime('%A')
    try:
        schemeFmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
    except KeyError:
        return None
    inpath = os.path.join(journal, schemeFmt)
    return inpath


def getDirectory(daDate=None):
    settings = QSettings('zero_substance', 'structjour')
    if daDate:
        d = daDate
    else:
        d = settings.value('theDate')

    scheme = settings.value('scheme')
    journal = settings.value('journal')
    if not scheme or not journal:
        return None
    # scheme = scheme.split('/')[0]

    if isinstance(d, (QDate, QDateTime)):
        d = qtime2pd(d)
    Year = d.year
    month = d.strftime('%m')
    MONTH = d.strftime('%B')
    day = d.strftime('%d')
    DAY = d.strftime('%A')
    try:
        schemeFmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
    except KeyError:
        return None
    inpath = os.path.join(journal, schemeFmt)
    return inpath

class IbStatement:
    '''
    Hold the column names for tables in Flex Queries. The names are a subset of the possible
    columns.
    '''

    # Not sure there is a difference between T_FLEX and TRADE
    # Going to attempt to treat CSV and Html version of activity statements the same once
    # the initial dataframes are created. For the subset of 3-4 tables we view, should be possible.
    I_TYPES = ["A_FLEX", "T_FLEX", "ACTIVITY", "TRADE"]
    def __init__(self):

        self.account = None
        self.statementname = None
        self.beginDate = None
        self.endDate = None
        self.inputType = None
        self.broker = None

    def parseTitle(self, t):
        '''
        The html title tag of the activity statement contains statement info. There are no specs to
        the structure of the thing. So on failure, raise exceptions. By trial and error, find the
        available formats. Especially multi day format must be different than this one. So just
        raise exceptions everywhere until comfortable that all cases are covered. 
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
                endDate = pd.Timestamp(endDate)
                self.endDate = endDate
            except ValueError('Failed to parse the statement date'):
                raise

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

            self.beginDate = pd.Timestamp(theDate)
            self.account = account
            self.statementname = sname

        except:
            raise ValueError('Failed to parse the statement date')
    def combinePartialsHtml(self, df):
        '''
        Combine the partial entries in a trades table. The Html refers to the origin of the table.
        This is a table without a DataDiscriminator or LevelOfDetail column. The Partials were
        identified in html with classes and the user identifies them with expanding thingys. So 
        woopdy do for that. The discriminator now is equal[DateTime, Codes, Symbol](Codes must
        include a P). The first of the bunch has the summary Quantity, 'the rest' add to the first.
        Filter out 'the rest.'
        '''
        newdf = pd.DataFrame()
        hasPartials = False
        tickers = df['Symbol'].unique()
        for tickerKey in tickers:
            if tickerKey.lower().startswith('closed') or tickerKey.lower().startswith('wash sale'):
                hasPartials = True
        if not hasPartials:
            return df
                
        for tickerKey in df['Symbol'].unique():
            ticker = df[df['Symbol'] == tickerKey]
            if len(tickerKey) > 6:
                # This is probably not a ticker assert to verify
                for code in ticker['Codes'].unique():
                    assert code.find('O') == -1
                    assert code.find('C') == -1
                    assert code.find('P') == -1
                continue


            ####### new code #####
            # aticker = ticker
            codes = ticker['Codes'].unique()
            for code in codes:
                parts = ticker[ticker['Codes'] == code]
                if code.find('P') > -1:
                    if len(parts) == 1:
                        # ASSUMPTION. If there is only one partial, this is a summary row and
                        # the detail rows are excluded by IB
                         
                        # raise ValueError('How to deal with singe partial entries????')
                        print()
                        print(f'''1)    {parts.iloc[0][['Symbol', 'DateTime', 'Quantity', 'Codes']].values}''')
                        x=3

                    else:
                        print()
                        addme = []
                        curTotal = 0

                        for count, (i, row) in enumerate(parts.iterrows()):
                            share = int(row['Quantity'])
                            if curTotal == 0:
                                curTotal = share
                                addme.append(count)
                            else:
                                curTotal = curTotal - share
                            print(f'{count})   ', row[['Symbol', 'DateTime', 'Quantity', 'Codes']].values)
                        assert curTotal == 0
                        print('Summary(s) in row(s)', addme)
                        x=3
                        # for code in trade['Codes'].unique():
                        #     assert code.find('O') > -1 or code.find('C') > -1
                        for x in addme:
                            newdf = newdf.append(parts.iloc[x])
                else:
                    newdf = newdf.append(parts)

        return newdf



            ####### Old code #####
            #  for timeKey in  ticker['DateTime'].unique():
            #     trade = ticker[ticker['DateTime'] == timeKey]
            #     if len(trade) > 1:
            #         codes = trade['Codes'].unique()
            #         # I am not sure they all have to share the same code but it makes sense
            #         assert len(codes) == 1
            #         assert codes[0].find('P') > -1
            #         totQuantity = trade.iloc[0]['Quantity']
            #         try:
            #             totQuantity = int(totQuantity)
            #             tot = 0
            #             for qty in trade['Quantity']:
            #                 tot = tot + int(qty)
            #             if tot != 2 * totQuantity:
            #                 print('Bad value. The old system is going to add a phantom trade:::::::::')
            #                 raise TypeError('Stop here')
                    
            #         except ValueError:
            #             print("Badly formatted or missing data html in Trades table for partial.")
            #             return None
            #     for code in trade['Codes'].unique():
            #         assert code.find('O') > -1 or code.find('C') > -1
            #     newdf = newdf.append(trade.iloc[0])

    def doctorHtmlTables(self, tabd):
        tabs = ['AccountInformation', 'OpenPositions', 'Transactions', 'Trades',
                'LongOpenPositions', 'ShortOpenPositions']
        keys = list(tabd.keys())
        for key in keys:
           

            if key in ['OpenPositions', 'Transactions', 'Trades', 'LongOpenPositions', 'ShortOpenPositions']:
                df = tabd[key]
                df = df[df['Symbol'].str.startswith('Total') == False]
                df = df.iloc[2:]
                # Using 'tbl' prefix to identify the html specific table
                ourcols = self.getColsByTabid('tbl' + key)
                if ourcols:
                    ourcols = self.verifyAvailableCols(list(df.columns), ourcols, 'tbl' + key)
                    df = df[ourcols]
                if key == 'Trades':
                    df = df.rename(columns={'Acct ID': 'Account', 'Trade Date/Time': 'DateTime',
                                   'Comm': 'Commission'})
                    df = self.unifyDateFormat(df)
                if key == 'Transactions':
                    df = df.rename(columns={'Date/Time': 'DateTime', 'T. Price': 'Price',
                                   'Comm/Fee': 'Commission', 'Code': 'Codes'})
                    
                    df['Account'] = self.account
                    df = self.combinePartialsHtml(df)
                    df = self.unifyDateFormat(df)
                tabd[key] = df.copy()

            elif key == 'AccountInformation':
                tabd[key].columns = ['Field Name', 'Field Value']
            
            if key in ['LongOpenPositions', 'ShortOpenPositions']:
                t = tabd[key]

                t = tabd[key][tabd[key]['Mult'] == '1']

                if 'OpenPositions' in tabd.keys():
                    tabd['OpenPositions'] = tabd['OpenPositions'].append(t)
                else:
                    tabd['OpenPositions'] = t.copy()
                del tabd[key]
        return tabd

    def openIBStatementHtml(self, infile):
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
            for key in ['tblAccountInformation', 'tblOpenPositions', 'tblLongOpenPositions', 'tblShortOpenPositions', 'tblTransactions', 'tblTrades']:
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
            # tables[tableTag['id']] = df[0]
            tables[tabKey] = df
        if 'Transactions' not in tables.keys() and 'Trades' not in tables.keys():
            # This should maybe be a dialog
            msg = 'The statment lacks a trades table; it has no information of interest.'
            print(msg)
            return dict(), dict()
        self.doctorHtmlTables(tables)
        tname = ''
        if 'Trades' in tables.keys():
            tname = 'Trades'
        elif 'Transactions' in tables.keys():
            tname = 'Transactions'
        
        if tname:
            ibdb = StatementDB()
            ibdb.processStatement(tables[tname], self.beginDate, self.endDate)
        else:
            raise ValueError('This code should not have come here')
        for key in tables:
            tablenames[key] = key
        tablenames[tabKey] = tabKey
        return tables, tablenames

    def openIBStatement(self, infile):
        if os.path.splitext(infile)[1] == '.csv':
            return self.openIBStatementCSV(infile)
        elif os.path.splitext(infile)[1] == '.html':
            return self.openIBStatementHtml(infile)
        else:
            print('Only htm or csv files are recognized')
        
    def openIBStatementCSV(self, infile):
        '''
        Identify a csv file as a type of IB Statement and send to the right place to open it
        '''
        df = pd.read_csv(infile, names=[x for x in range(0, 100)])
        # for s in df[0]:
        #     print(s)
        df = df
        if df.iloc[0][0] == 'BOF':
            # This is a flex activity statement with multiple tables
            self.inputType = "A_FLEX"
            return self.getTablesFromMultiFlex(df)

        elif df.iloc[0][0] == 'ClientAccountID':
            # This is a single table file. Re read to get default column names from row 1
            # This table is missing the Open/Close data. Its probably in transacations,
            # identified by LevelOfDetail=EXECUTION
            df = pd.read_csv(infile)
            self.inputType = 'T_FLEX'

            # This one table file has no tableid
            ourcols = self.getColsByTabid('FlexTrades')
            currentcols = list(df.columns)
            self.verifyAvailableCols(currentcols, ourcols, 'DailyTrades')
            df = df[ourcols].copy()
            df = df.rename(columns={'Date/Time': 'DateTime', 'Code': 'Codes'})
            df = self.combinePartials(df)
            df = df.rename(columns={'ClientAccountID': 'Account'})

            # The Codes col acks the OpenClose codes so were done with it.
            df = df.drop(['LevelOfDetail', 'Codes'], axis=1)
            df = self.unifyDateFormat(df)

            ### db stuff ###
            fred = df.copy()
            fred.sort_values('DateTime', ascending=True, inplace=True)
            beg = fred.iloc[0]['DateTime'][:8]
            end = fred.iloc[-1]['DateTime'][:8]
            ibdb = StatementDB()
            ibdb.processStatement(df, beg, end)
            ### end db stuff ###

            return {'Trades': df}, {'Trades': 'Trades'}
        elif df.iloc[0][0] == 'Statement':
            # This is a multi table statement like a default statement
            self.inputType = 'ACTIVITY'
            return self.getTablesFromDefaultStatement(df)
        return None, None

    def unifyDateFormat(self, df):
        '''
        Ib sends back differnt formats from different files. All statement processing should call
        this method.
        '''
        df['DateTime'] = df['DateTime'].str.replace('-', '').str.replace(':', '').str.replace(',', ';').str.replace(' ', '')
        assert len(df.iloc[0]['DateTime']) == 15
        return df

    def getTablesFromDefaultStatement(self, df):
        '''
        From a default Activity statement csv, retrieve AccountInformation, OpenPositions, and
        Trades
        '''
        # df = pd.read_csv(infile, header=range(0,15))
        keys = df[0].unique()
        tables = dict()
        tablenames = dict()
        for key in keys:
            if key not in ['Statement', 'Account Information', 'Open Positions', 'Short Open Positions', 'Long Open Positions', 'Trades']:
                continue

            tab = df[df[0] == key]
            headers = tab[tab[1] == 'Header']
            if len(headers) > 1:
                print('Multi account statment not supported"')
                return dict(), dict()
            assert tab.iloc[0][1] == 'Header'
            currentcols = list(tab.columns)
            cols = list()

            for i, col in enumerate(tab.iloc[0]):
                if isinstance(col, str):
                    if col == key or col == 'Header':
                        continue
                    cols.append(col)
                    currentcols[i] = col
                    # tab = tab.rename({headers: col})
                elif isinstance(col, float) and math.isnan(col):
                    tab.columns = currentcols
                    tab = tab[tab[1].str.lower() == 'data']
                    tab = tab[cols].copy()
                    ourcols = self.getColsByTabid(key)
                    if ourcols:
                        ourcols = self.verifyAvailableCols(currentcols, ourcols, key)
                        tab = tab[ourcols].copy()

                    break
                else:
                    print('do the same thing?')
                    tab.columns = currentcols
                    tab = tab[cols].copy()
            if key in ['Long Open Positions', 'Short Open Positions']:
                tab = tab[tab['DataDiscriminator'].str.lower() == 'summary']
                key = 'OpenPositions'
                ourcols = self.getColsByTabid(key)
                if ourcols:
                    ourcols = self.verifyAvailableCols(
                        list(tab.columns), ourcols, key)
                    tab = tab[ourcols].copy()

                if 'OpenPositions' in tables.keys():
                    if not (set(tables['OpenPositions'].columns) == set(tab.columns)):
                        msg = 'A Programmer thing-- see it occur before I write code'
                        raise ValueError(msg)
                            
                    tables['OpenPositions'] = tables['OpenPositions'].append(tab)
                    tablenames['OpenPositions'] = 'OpenPositions'
                    continue
                else:
                    key = 'OpenPositions'
            elif key == 'Trades':
                # We want the rows where DataDiscriminator=Trade or Order. The info is nearly
                # identical and redundant. Some statements include both but some only include
                # Order. The occasional slight differences (in time) will not affect trade review.
                # I have seen none that include Trade, but not Order rows. 
                if 'Trades' in tablenames.keys():
                    raise ValueError('Statement type Not Supported: Satement has Trades table for two accounts.')
                tab = tab[tab['DataDiscriminator'].str.lower() == 'order']
                tab = tab.rename(columns={'T. Price': 'Price', 'Comm/Fee': 'Commission'})
                tab['Account'] = self.account
                tab = tab.drop('DataDiscriminator', axis=1)
                tab = tab.rename(columns={'Code': 'Codes', 'Date/Time': 'DateTime'})
                tab = self.unifyDateFormat(tab)

            elif key == 'Statement':
                # This bugs me. It is too dependent on the file to be formatted precisely as
                # expected and expectations based only on observation. There are no specs for layout
                # Another argument to insist on flex queries only- they have specs.  When this raises
                # exceptions ...
                self.broker = tab[tab['Field Name'] == 'BrokerName']['Field Value'].unique()[0]
                self.statementname = tab[tab['Field Name'] == 'Title']['Field Value'].unique()[0]
                self.statementname = tab[tab['Field Name'] == 'Title']['Field Value'].unique()[0]
                period = tab[tab['Field Name'] == 'Period']['Field Value'].unique()[0]
                test = period.split('-')
                if len(test) == 1:
                    self.beginDate = pd.Timestamp(period)
                elif len(test) == 3:
                    # This is proably a date formatted 14-Jun-9
                    try:
                        self.beginDate = pd.Timestamp(period)
                    except ValueError:
                        print('Unrecognized date format in Statement', period)
                else:
                
                
                    self.beginDate = test[0].strip()
                    self.endDate = test[1].strip()
                    self.beginDate = pd.Timestamp(self.beginDate)
                    self.endDate = pd.Timestamp(self.endDate)
            elif key == 'Account Information':
                names = tab['Field Name'].unique()
                if 'Account' in names:
                    self.account = tab[tab['Field Name'] == 'Account']['Field Value'].unique()[0]
                elif 'Segment' in names:
                    # This is a multi account statement
                    self.account = tab[tab['Field Name'] == 'Segment']['Field Value'].unique()[0]

                

            key = key.replace(' ', '')
            tables[key] = tab
            tablenames[key] = key


            # tab.columns = currentcols

        if 'Trades' not in tables.keys():
            # This should maybe be a dialog
            msg = 'The statment lacks a trades table; it has no information of interest.'
            print(msg)
            return dict(), dict()

        ibdb = StatementDB()
        ibdb.processStatement(tables['Trades'], self.beginDate, self.endDate)
        return tables, tablenames

    def combinePartials(self, t):
        '''
        In flex docs, the TRNT (Trades) table input is in transacations. This is identified by
        LevelOfDetail=EXECUTION and by a lack of LevelOfDetail="ORDER." Why did they leave out
        the summary here, but not in other statement docs? .... Here we re-combine the tx rows
        into tickets
        :t: Is a TRNT DataFrame. That is a Trades table from a CSV multi table doc in which TRNT
                 is the tableid.
        :assert: Tickets written at the exact same time are partials, identified by 
                 Notes/Codes == P (change name to Codes) and by having a single Symbol
        :prerequisite: Must have the columns ['Price', 'Commission', 'Quantity', 'LevelOfDetail', 'Codes']
        '''
        for lod in t['LevelOfDetail'].unique():
            if lod.lower() == 'order':
                t = t[t['LevelOfDetail'].str.lower() == lod]
                orderfound = True
                return t

        t = t[t['LevelOfDetail'].str.lower() == 'execution']
        newtickets = pd.DataFrame()
        for ticker in t['Symbol'].unique():
            tickers = t[t['Symbol'] == ticker]
            for ttime in tickers['DateTime'].unique():
                ticket = tickers[tickers['DateTime'] == ttime]

                l = len(ticket)
                if l > 1:
                    for i, row in ticket.iterrows():
                        code = row['Codes']
                        assert code.find('P') > -1

                    ticket = ticket.replace(np.nan, '')
                    
                    thisticket = DataFrameUtil.createDf( ticket.columns, 1)
                    net = 0.0

                    # Need to figure the average price of the transactions and sum of quantity and commission
                    for i, row in ticket.iterrows():
                        net = net + (float(row['Price']) * int(row['Quantity']))
                    for col in list(thisticket.columns):
                        if col not in ['Quantity', 'Price', 'IBCommission']:
                            thisticket[col] = ticket[col].unique()[0]
                    thisticket['Quantity'] = ticket['Quantity'].map(int).sum()
                    thisticket['Commission'] = ticket['Commission'].map(float).sum()
                    thisticket['Price'] = net / ticket['Quantity'].map(int).sum()
                    newtickets = newtickets.append(thisticket)

                else:
                    newtickets = newtickets.append(ticket)
        return newtickets

    def getTablesFromMultiFlex(self, df):
        '''
        :code notes:
        navigation values = [BOF,EOF,BOA,EOA,BOS,EOS,HEADER,DATA] They occur in column one
        The imported columns names are clunky: col 1 is named 'BOF' col 2 is named the {account#}
        (e.g. 'U1234567')
        column 2 navigation is accountid (sames as the column heading [1]) or {tableid} which will
        identify all the rows in a table (i.e df[df.account==tableid] where account is column 2)
        There is probably a way to identify this csv structure using heirarchical multilevel
        indexes. If discovered replace this hacky version.
        The trick here is to extract the tables into pandas, get the headers, replace the active
        fields and truncate all the other fields (that lack headers and data)

        '''
        ft = IbStatement()
        # df = pd.read_csv(infile)

        tables = dict()
        tablenames = dict()
        if df.iloc[0][0] == 'BOF':
            # The data in the top (BOF) line is not part of a table. We need begin and end.
            self.account = df.iloc[0][1]
            self.statementname = df.iloc[0][2]
            # numtables = df.columns[3]
            beginDate = df.iloc[0][4]
            self.beginDate = pd.Timestamp(beginDate)
            endDate = df.iloc[0][5]
            self.endDate = pd.Timestamp(endDate)

            # Retrieve the rows for all BeginOfSection markers, TableIDs are in the second column
            x = df[df[0] == 'BOS']

            tabids = x[1]
            for tabid in tabids:
                ourcols = ft.getColsByTabid(tabid)
                if not ourcols:
                    continue

                # Create a DataFrame for tabid, Remove marker rows EOS and BOS,
                # get the header columns, then remove the header row
                t = df[df[1] == tabid]
                names = t.iloc[0][2]

                t = t[t[0] != 'EOS']
                t = t[t[0] != 'BOS']

                # Get the headers as found in the FLEX file (index is numbers),
                cols = list()
                currentcols = list(t.columns)
                for i, col in enumerate(t[t[0] == 'HEADER'].iloc[0]):
                    if col and isinstance(col, str):
                        if col in ['HEADER', tabid]:
                            continue

                        # Selectively replace list of index names with headers
                        cols.append(col)
                        currentcols[i] = col

                    # This signals the end of the columns in our index list. better indicator(?)
                    elif isinstance(col, float) and math.isnan(col):
                        # Replace the index, remove non 'Data' rows and the 'HEADER' row,  Filter with our columns
                        self.verifyAvailableCols(currentcols, ourcols, tabid + names)
                        t.columns = currentcols
                        t = t[t[0].str.lower() == 'data']
                        t = t[t[0].str.lower() != 'header']
                        t = t[ourcols].copy()
                        break
                    else:
                        # Could this also signal the end of the columns? (never been triggered)
                        msg = ''.join(['A Programmer thing: Probably do the same thing as the elif',
                                       'but I want to see why it occurs.'])
                        raise ValueError(msg)
                if tabid == 'TRNT':
                    # NOTES: I am wary of LevelOfDetail. EXECUTION is transactions, not tickets.
                    # Docs say LevelOfDetail could include ORDERS but mine don't and I can find
                    # no way to choose to get that information. Other statements include both
                    # kinds of info. Lacking more precise info, refigure everything... Look for
                    # orders (which may never exist) and failing to find it, combine partials into
                    # tickets (like it is everywhere else and an order is a ticket.) The big
                    # weakness is that LevelOfDetail=Orders may never get tested by real data input
                    # until someone's statement tests it.
                    t['DateTime'] = t['TradeDate'].map(str) + ';' + t['TradeTime']

                    t = t.rename(columns={'TradePrice': 'Price', 'IBCommission': 'Commission', })

                    # Weirdness -- combined cols 
                    t = t.rename(columns={'ClientAccountID': 'Account', 'Notes/Codes': 'Codes'})
                    t = self.combinePartials(t)

                        
                    t = t.drop(['TradeDate', 'TradeTime', 'Codes', 'LevelOfDetail'], axis=1)
                    t = t.rename(columns={'Open/CloseIndicator': 'Codes'})
                    t = self.unifyDateFormat(t)

                # Assign to dict and return
                tables[tabid] = t
                tablenames[tabid] = names
            ibdb = StatementDB()
            ibdb.processStatement(tables['TRNT'], self.beginDate, self.endDate)
        else:
            return None
        return tables, tablenames

    def getColsByTabid(self, tabid):
        '''
        Using the tableids from the Flex queries and other Statements, we are interetsed in these
        tables only and in the columns we define here only. 
        The column headers are a subset as found in the input files. 
        Functionally TRNT and Trades and tblTransactions are the same but IB returns different
        column names in 
            flex(TRNT) 
            csv Activity Statements(Trades)
            html Activity statements (Transactions)
        Fixing the differences is not done here.
        '''

        # Trades not implemented -- still figuring the place to reconcile the different fields.
        #######  From the Flex Activity statement #######
        if tabid not in ['ACCT', 'POST', 'TRNT',  'Open Positions', 'OpenPositions',
                         'Long Open Positions', 'Short Open Positions', 'Trades', 'FlexTrades',
                         'tblTrades', 'tblTransactions', 'tblOpenPositions',
                         'tblLongOpenPositions', 'tblShortOpenPositions']:
            return []
        if tabid == 'ACCT':
            return ['ClientAccountID', 'AccountAlias']

        if tabid in ['POST', 'Open Positions', 'OpenPositions', 'tblOpenPositions']:
            return ['Symbol', 'Quantity']

        if tabid in ['Long Open Positions', 'Short Open Positions']:
            # DataDiscriminator is temporary to filter results
            return ['Symbol', 'Quantity', 'DataDiscriminator']

        if tabid in ['tblLongOpenPositions', 'tblShortOpenPositions']:
            # Not a great data discriminator (Mult=='1')
            return ['Symbol', 'Quantity', 'Mult']


        # Trades table from fllex csv
        if tabid == 'TRNT':
            # I have not seen statements that use LevelOfDetail for anything but EXECUTION, but it
            # must be used sometime. Should filter by EXECUTION
            return ['ClientAccountID', 'Symbol', 'TradeDate', 'TradeTime', 'Quantity', 'TradePrice', 'IBCommission',  'Open/CloseIndicator', 'Notes/Codes', 'LevelOfDetail']

        if tabid == 'Trades':
            # return [ 'Symbol', 'TradeDate', 'Date/Time', 'Quantity', 'Price', 'Commission', 'Code']
            return ['Symbol', 'Date/Time', 'Quantity', 'T. Price', 'Comm/Fee', 'Code', 'DataDiscriminator']
            # [ 'Asset Category', 'Currency', 'Exchange', 'C. Price', 'Proceeds', 'Basis', 'Realized P/L' 'MTM P/L' ]


        if tabid == 'FlexTrades':
            return ['ClientAccountID', 'Symbol', 'Date/Time', 'Quantity', 'Price', 'Commission', 'Code', 'LevelOfDetail' ]

        if tabid == 'tblTrades':
            return ['Acct ID', 'Symbol', 'Trade Date/Time', 'Quantity', 'Price', 'Comm' ]

        if tabid == 'tblTransactions':
            return ['Symbol', 'Date/Time', 'Quantity', 'T. Price',  'Comm/Fee',       'Code'    ]


        ####### Activity Statement non flex #######
        if tabid == 'Statement':
            return ['Field Name', 'Field Value']

        if tabid.find('Positions') > -1:
            raise ValueError('Fix it!!!')

        raise ValueError('What did we not catch?')

        # Trades= ['ClientAccountID', 'AccountAlias', 'Symbol', 'Conid', 'ListingExchange', 'TradeID', 'ReportDate', 'TradeDate',              'Date/Time',              'Buy/Sell', 'Quantity',  'Price',      'TransactionType',  'Commission',                          'Code',       'LevelOfDetail', ]

    def verifyAvailableCols(self, flxcols, ourcols, tabname):
        '''
        Check flxcols against ourcols, remove any cols in ourcols that are missing in flxcols and
        send a warning
        '''
        missingcols = set(ourcols) - set(flxcols)
        if missingcols:
            msg = f'ERROR: {tabname} is missing the columns {missingcols}'
            raise ValueError(msg)
            for col in missingcols:
                ourcols.remove(col)
        return ourcols


class StatementDB:
    '''
    Methods to create and manage tables to store Activity Statements. Fields are exactly IB fields
    from activity flex query
    '''

    def __init__(self, db=None):
        '''Initialize and set the db location'''
        settings = QSettings('zero_substance', 'structjour')
        jdir = settings.value('journal')
        if not db:
            db = 'structjour_test.db'
        self.db = os.path.join(jdir, db)
        self.createTradeTables()

        self.holidays = [ 
                        ['New Year’s Day', '2018-01-01', '2019-01-01', '2020-01-01', '2121-01-01', '2022-01-01', '2023-01-01'],
                        ['Martin Luther King, Jr. Day', '2018-01-15', '2019-01-21', '2020-01-20', '2021-01-18', '2022-01-17', '2023-01-16'],
                        ['Washington’s Birthday', '2018-02-19', '2019-02-18',	'2020-02-17', '2021-02-21', '2022-02-21', '2023-02-20'],
                        ['Good Friday', '', '2019-04-19', '2020-04-10', '2021-04-02', '2022-04-15', '2023-04-07'],
                        ['Memorial Day', '2018-05-28', '2019-05-27', '2020-05-25', '2021-05-31', '2022-05-30', '2023-05-29'],
                        ['Independence Day', '2018-07-04', '2019-07-04', '2020-07-04', '2021-07-04', '2022-07-04', '2023-07-04'],
                        ['Labor Day', '2018-09-03', '2019-09-02', '2020-09-07', '2021-09-06', '2022-09-05', '2023-09-04'], 
                        ['Thanksgiving Day', '2018-11-22', '2019-11-28', '2020-11-26', '2021-11-25', '2022-11-24', '2023-11-23'], 
                        ['Christmas Day', '2018-12-25', '2019-12-25', '2020-12-25', '2021-12-25', '2022-12-25', '2023-12-25']
        ]
        self.popHol()

    

    def account(self):
        '''Create account table'''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE if not exists account_information (
            id	INTEGER PRIMARY KEY AUTOINCREMENT,
            ClientAccountID TEXT, 
            AccountAlias TEXT);''')
        conn.commit()

    def createTradeTables(self):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE if not exists ib_trades (
                id	INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol	TEXT NOT NULL,
                datetime	TEXT NOT NULL,
                quantity	INTEGER NOT NULL,
                price	NUMERIC NOT NULL,
                commission	NUMERIC,
                codes	TEXT,
                account	TEXT);''')

        cur.execute('''
            CREATE TABLE if not exists ib_covered (
                day	TEXT,
                covered	TEXT NOT NULL DEFAULT "false",
                PRIMARY KEY(day))''')

        cur.execute('''
            CREATE TABLE if not exists holidays(
                day TEXT,
                name TEXT)''')
        conn.commit()

    def findTrade(self, row, cur):
        cursor = cur.execute('''
            SELECT * from ib_trades where datetime = ?
            AND symbol = ?
            AND quantity = ?
            AND account = ?
            ''',
            (row['DateTime'], row['Symbol'], row['Quantity'], row['Account']))
        x = cursor.fetchall()
        if x:
            if len(x) !=1:
                print('Duplicates ? ', row['Symbol'], row['DateTime'])
            print('. ', end='')
            return True
        print('Adding a trade', row['Symbol'], row['DateTime'])
        return False




    def insertTrade(self, row, cur):
        '''Insert a trade. Commit not included'''
        if self.findTrade(row, cur):
            return
        if 'Codes' in row.keys():
            codes = row['Codes']
        else:
            codes = ''
        cur.execute('''
            INSERT INTO ib_trades (symbol, datetime, quantity, price, commission, codes, account)
            VALUES(?,?, ?, ?, ?, ?, ?)''',
            (row['Symbol'], row['DateTime'], row['Quantity'], row['Price'], row['Commission'],
            codes, row['Account']))

    def processStatement(self, tdf, begin, end,  openPos=None):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        for i, row in tdf.iterrows():
            self.insertTrade(row, cur)
        conn.commit()

    def popHol(self):
        '''
        Populat the holidays table.
        '''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        didsomething = False
        for i in range(1, 6):
            for year in self.holidays:
                cur.execute('''SELECT * from holidays where day = ?''', (year[i],))
                cursor = cur.fetchone()
                if not cursor:
                    didsomething = True
                    cur.execute('''INSERT INTO holidays (day, name)
                        VALUES(?,?)''', (year[i], year[0]))
        if didsomething:
            conn.commit()


    def genericTbl(self, tabname, fields):
        '''
        Create a table with an id plus all the fields in fields as TEXT
        '''
        tabname = tabname.lower().replace(' ', '_').replace(';', '')
        query = f'''
            CREATE TABLE if not exists {tabname} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,'''
        for field in fields:
            query = query + f'''
                {field} TEXT,'''

            print(query)
        query = query[:-1]
        query = query + ')'
        print(query)
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()


def findFilesInDir(direct, fn, searchParts):
    '''
    Find the files in direct that match fn, either exactly or including the same parts.
    :direct: The directory to search
    :fn: A filename or file pattern with parts seperated by '.' 
    :freq: Either DaiyDir or MonthlyDir. DailyDir will search the daily directories and MonthlyDir
            will search the Monthly directories.
    :searchParts: If False, search for the precise filename. If True search parts seperated by
            '.' and ending with the same extension 
    '''
    files = os.listdir(direct)
    found=[]
    if searchParts:
        fn, ext = os.path.splitext(fn)
        for f in files:
            parts = fn.split('.')
            countparts=0
            for part in parts:
                if f.find(part) > -1:
                    countparts = countparts + 1
                    if countparts == len(parts) and f.endswith(ext):
                        found.append(os.path.join(direct, f))
                else:
                    break
    else:
        for f in files:
            if fn == f:
                found.append(os.path.join(direct, f))
        
    return found

def findFilesInMonth(daDate, fn, searchParts):
    '''
    Match the file in the given month that contain the name fn
    :fn: A filename of file pattern with parts seperated by '.' 
    :searchParts: If False, search for the precise filename. If True search parts seperated by
            '.' and ending with the same extension 

    '''

    m = daDate
    m = pd.Timestamp(m)
    m = pd.Timestamp(m.year, m.month, 1)
    delt = pd.Timedelta(days=1)
    current = m
    files = []
    while True:
        currentMonth = current.month
        theDir = getDirectory(current)

        if current.weekday() > 4:
            current = current + delt
            continue
        
        addme=[]
        if os.path.exists(theDir):
            addme = findFilesInDir(theDir, fn, searchParts)
        if addme:
            files.extend(addme)
    
            
        current = current + delt
        if current.month != currentMonth:
            break
    return files

def findFilesSinceMonth(daDate, fn, freq='DailyDir', searchParts=True):
    '''
    Collect the all files since daDate in the journal directory that match fn
    :fn: A filename or file pattern with parts seperated by '.' 
    :freq: Either DaiyDir or MonthlyDir. DailyDir will search the daily directories and MonthlyDir
            will search the Monthly directories.
    :searchParts: If False, search for the precise filename. If True search parts seperated by
            '.' and ending with the same extension 
    '''
    assert freq in ['DailyDir', 'MonthlyDir']
    daDate = pd.Timestamp(daDate)
    now = pd.Timestamp.today()
    thisMonth = pd.Timestamp(now.year, now.month, 1)
    current = pd.Timestamp(daDate.year, daDate.month, 1)
    files = []
    addme = []
    while current <= thisMonth:
        if freq == 'DailyDir':
            addme = findFilesInMonth(current, fn, searchParts)
        else:
            addme = findFilesInDir(getMonthDir(current), fn, searchParts)
        if addme:
            files.extend(addme)
        month = current.month
        if month == 12:
            current = pd.Timestamp(current.year+1, 1, 1)
        else:
            current = pd.Timestamp(current.year, month+1, 1)
    return files
        



def notmain():
    t = StatementDB()
    t.popHol()
    

def localStuff():
    # Tricky stuff -- triggered by 'atrade' from 3/28. Partials with different times. They exist,
    # and tht file has no good discriminator. In fact if the times are not guaranteed, none of
    # those files have guaranteed discriminators for partials. Have to go through a bucnch ofem
    # and try to use the codes and  share totals. 
    d = pd.Timestamp('2018-09-13')
    files = dict()
    files['flexTid'] = ['TradeFlexMonth.327778.csv', getDirectory]
    files['flexAid'] = ['ActivityFlexMonth.369463.csv', getDirectory]
    files['activityDaily'] = ['ActivityDaily.663710.csv', getDirectory]
    files['U242'] = ['U2429974.csv', getDirectory]
    files['activityMonth'] = ['CSVMonthly.644225.csv', getMonthDir]
    files['dtr'] = ['DailyTradeReport.html', getDirectory]
    files['act'] = ['ActivityStatement.html', getDirectory]
    files['atrade'] = ['trades.643495.html', getDirectory]

    das = 'trades.csv'                          # Search verbatim with searchParts=False
                                                # TODO How to reconcile IB versus DAS input?

    sp = True
    for key in files:
        # fs = findFilesInDir(files[key][1](d), files[key][0], searchParts=sp)
        fs = findFilesSinceMonth(d, files[key][0])
        for f in fs:
            ibs = IbStatement()
            x = ibs.openIBStatement(f)

if __name__ == '__main__':
    # notmain()
    localStuff()
