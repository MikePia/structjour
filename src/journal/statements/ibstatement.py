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
from journal.statements.ibstatementdb import StatementDB

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


def getBaseDir(nothing=None):
    settings = QSettings('zero_substance', 'structjour')
    journal = settings.value('journal')
    return journal


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
        the structure of the thing. So on failure, raise exceptions.
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

            self.beginDate = pd.Timestamp(theDate).date()
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

            codes = ticker['Codes'].unique()
            for code in codes:
                parts = ticker[ticker['Codes'] == code]
                if code.find('P') > -1:
                    if len(parts) == 1:
                        x=3

                    else:
                        # print()
                        addme = []
                        curTotal = 0

                        for count, (i, row) in enumerate(parts.iterrows()):
                            share = int(row['Quantity'])
                            if curTotal == 0:
                                curTotal = share
                                addme.append(count)
                            else:
                                curTotal = curTotal - share
                        assert curTotal == 0
                        x=3
                        for x in addme:
                            newdf = newdf.append(parts.iloc[x])
                else:
                    newdf = newdf.append(parts)

        return newdf

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
                    ourcols, missingcols = self.verifyAvailableCols(list(df.columns), ourcols, 'tbl' + key)
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
            ibdb.processStatement(tables[tname], self.account, self.beginDate, self.endDate)
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
        df = df
        if df.iloc[0][0] == 'BOF'  or df.iloc[0][0] == 'HEADER':
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
            beg = pd.Timestamp(beg).date()
            end = fred.iloc[-1]['DateTime'][:8]
            end = pd.Timestamp(end).date()
            ibdb = StatementDB()
            ibdb.processStatement(df, self.account, beg, end)
            ### end db stuff ###

            return {'Trades': df}, {'Trades': 'Trades'}
        elif df.iloc[0][0] == 'Statement':
            # This is a multi table statement like a default statement
            self.inputType = 'ACTIVITY'
            return self.getTablesFromDefaultStatement(df)
        return dict(), dict()

    def unifyDateFormat(self, df):
        '''
        Ib sends back differnt formats from different files. All statement processing should call
        this method.
        '''
        df['DateTime'] = df['DateTime'].str.replace('-', '').str.replace(':', '').str.replace(',', ';').str.replace(' ', '')
        if df.any()[0]:
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
                print('\nMulti account statment not supported"')
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
                        ourcols, missingcols = self.verifyAvailableCols(currentcols, ourcols, key)
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
                    ourcols, missingcols = self.verifyAvailableCols(
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
                # but could affect recognition of partial executions. (Changed combinePartials to
                # avoid problem)
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
                    self.beginDate = pd.Timestamp(period).date()
                elif len(test) == 3:
                    # This is proably a date formatted 14-Jun-9
                    try:
                        self.beginDate = pd.Timestamp(period).date()
                    except ValueError:
                        print('Unrecognized date format in Statement', period)
                else:
                    self.beginDate = test[0].strip()
                    self.endDate = test[1].strip()
                    self.beginDate = pd.Timestamp(self.beginDate).date()
                    self.endDate = pd.Timestamp(self.endDate).date()
            elif key == 'Account Information':
                names = tab['Field Name'].unique()
                self.account = tab[tab['Field Name'] == 'Account']['Field Value'].unique()[0]

            key = key.replace(' ', '')
            if key == 'OpenPositions':
                d =  self.endDate if self.endDate else self.beginDate
                tab['Date'] = d.strftime('%Y%m%d')
                
            tables[key] = tab
            tablenames[key] = key

        if 'Trades' not in tables.keys():
            # This should maybe be a dialog
            msg = 'The statment lacks a trades table; it has no information of interest.'
            print(msg)
            return dict(), dict()

        if self.account == None:
            msg = '''This statement lacks an account number. Can't add it to the database'''
            print(msg)
            return dict(), dict()
        ibdb = StatementDB()
        openpos = None
        if 'OpenPositions' in tables.keys():
            openpos = tables['OpenPositions']
        ibdb.processStatement(tables['Trades'], self.account, self.beginDate, self.endDate, openpos)
        return tables, tablenames

    def combinePartials(self, t):
        '''
        In flex docs, the TRNT (Trades) table input might be in transacations instead of tickets
        identified by LevelOfDetail=EXECUTION without the summary rows identified by 
        LevelOfDetail=ORDERS. This is fixable by changing the Flex query to include ORDERS but we
        can recombine the rows back into tackets here.
        :t: Is a TRNT DataFrame. That is a Trades table from a CSV multi table doc in which TRNT
                 is the tableid.
        :assert: Tickets written at the exact same time are partials, identified by 
                 Notes/Codes == P (change name to Codes) and by having a single Symbol
        :prerequisite: Must have the columns ['Price', 'Commission', 'Quantity', 'LevelOfDetail', 'Codes']
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
                        # Need to figure the average price of the transactions and sum of quantity and commission
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

    def doctorFlexTRNTCols(self, t, missingcols):
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
        # 1
        if 'Date/Time' in t.columns:
            raise ValueError('wtf ib!?!, Maybe you should hire me to do this stuff.')
            # t = t.rename(columns={'Date/Time': 'DateTime'})
        elif 'DateTime' in t.columns:
            pass
        elif 'TradeDate' and 'TradeTime' in t.columns:
            t['DateTime'] = t['TradeDate'].map(str) + ';' + t['TradeTime']
            t = t.drop(['TradeDate', 'TradeTime'], axis=1)
        else:
            msg = '\n'.join(['''This Activity Flex statement is missing order time information. Please include the',
                               'Date/Time' column or ['TradeDate','TradeTime'] columns. '''])
            self.beginDate = None
            return pd.DataFrame(), msg

        # 2
        missingcols = set(missingcols) - set(['TradeDate', 'TradeTime', 'DateTime', 'Date/Time', 'IBOrderID'])
        if missingcols:
            msg = f'Statment is missing cols: {list(missingcols)}'
            return pd.DataFrame, msg
        # 5
        t = t.rename(columns={'TradePrice': 'Price', 'IBCommission': 'Commission', 'ClientAccountID': 'Account'})

        # 3
        t['Codes'] = ''
        for i, row in t.iterrows():
            OC = row['Open/CloseIndicator']
            P = row['Notes/Codes']
            if isinstance(OC, float):
                OC = ''
            if isinstance(P, str):
                if (OC.find('O') > -1 and P.find('O') > -1) or (OC.find('C') > -1 and P.find('C') > -1):
                    codes = P
                else:
                    codes = f'{OC};{P}'
            else:
                codes = OC
            t.at[i, 'Codes'] = codes
        t = t.drop(['Open/CloseIndicator', 'Notes/Codes'], axis=1)

        # 4
        # lod =  list(t['LevelOfDetail'].unique())
        lod = [x.lower() for x in list((t['LevelOfDetail'].unique()))]
        if 'order' in lod:
            t = t[t['LevelOfDetail'].str.lower() == 'order']
        elif 'execution' in lod:
            if not 'IBOrderId' in t.columns:
                self.beginDate = None
                msg = '\n'.join(['This Activity Flex statement Includes EXECUTION level data (aka partials) To combine the partial executions',
                               'into readable trades, the column "IBOrderID" must be included in the Flex Query Trades table. Alternately,',
                               'select the Orders Options.'])
                return pd.DataFrame(), msg

            t = t[t['LevelOfDetail'].str.lower() == 'execution']
            t = self.combinePartials(t)
        elif len(t) > 0:
            msg = '\n'.join(['This Activity Flex statement is missing partial execution data. Please include the Orders or Execution Options for',
                           'the Trades Table in your Activity flex statement. '])
            return pd.DataFrame(), msg

        t = self.unifyDateFormat(t)
        dcolumns, mcolumns = self.verifyAvailableCols(list(t.columns), ['LevelOfDetail', 'IBOrderID', 'TradeDate'], 'utility')
        t = t.drop(dcolumns, axis=1)
        return t, ''

    def getFrame(self, fid, df):
        x = df[df[0] == fid[0]]
        metadata = []
        ldf = []
        for i in range(0, len(x)):
            started = False
            # newdf = pd.DataFrame()
            data = []

            for j, row in df.iterrows():
                if row[0] == fid[0] and started == False:
                    md = [x for x in row if isinstance(x, str)]
                    metadata.append(md)
                    started = True
                    continue
                elif started == True and row[0] != fid[1]:
                    data.append(row.values)
                    # newdf = newdf.append(row)
                elif started:
                    newdf = pd.DataFrame(data=data, columns=df.columns)
                    ldf.append(newdf)
                    break
        
        return ldf, metadata

    def doctorFlexTables(self, tables, mcd):
        if 'TRNT' in tables.keys():
            missingcols = mcd['TRNT']
            tables['TRNT'], m = self.doctorFlexTRNTCols(tables['TRNT'], missingcols)
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
            d =  self.endDate if self.endDate else self.beginDate if self.beginDate else None
            if d == None:
                # Bit of a catch 22 in the processing produces unsure
                if 'TRNT' in tables.keys():
                    beginDate = tables['TRNT']['DateTime'].min()
                    endDate = tables['TRNT']['DateTime'].max()

            tables['POST']['Date'] = d.strftime('%Y%m%d')
            tables['POST'] = tables['POST'].rename(columns={'ClientAccountID': 'Account'})
        return tables, ''

    def getTablesFromMultiFlex(self, df):
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
            ibdb = StatementDB()
            positions = None
            if 'POST' in tables.keys():
                positions = tables['POST']
            ibdb.processStatement(tables['TRNT'], self.account, self.beginDate, self.endDate, positions)
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
        if tabid not in ['ACCT', 'POST', 'TRNT',  'Open Positions', 'OpenPositions',
                         'Long Open Positions', 'Short Open Positions', 'Trades', 'FlexTrades',
                         'tblTrades', 'tblTransactions', 'tblOpenPositions',
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
        # It seems some statements use DateTime and others Date/Time. (not sure)  Baby sit it with an exception to try to find out.
        if tabid == 'TRNT':
            return ['ClientAccountID', 'Symbol', 'TradeDate', 'TradeTime','Date/Time', 'DateTime', 'Quantity', 'TradePrice', 'IBCommission', 'Open/CloseIndicator', 'Notes/Codes', 'LevelOfDetail', 'IBOrderID']

        if tabid == 'Trades':
            return ['Symbol', 'Date/Time', 'Quantity', 'T. Price', 'Comm/Fee', 'Code', 'DataDiscriminator']

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
    d = pd.Timestamp('2019-06-01')
    files = dict()
    # files['annual'] = ['_2018_2018.csv', getBaseDir]

    # files['stuff'] = ['N.csv', getDirectory]
    # files['flexTid'] = ['TradeFlexMonth.327778.csv', getDirectory]
    # files['flexTid'] = ['TradeFlexMonth.csv', getDirectory]
    # files['flexAid'] = ['ActivityFlexMonth.369463.csv', getDirectory]
    files['flexAid'] = ['ActivityFlexMonth.csv', getDirectory]
    # files['activityDaily'] = ['ActivityDaily.663710.csv', getDirectory]
    # files['U242'] = ['U242.csv', getDirectory]
    # files['activityMonth'] = ['CSVMonthly.644225.csv', getMonthDir]
    # files['dtr'] = ['DailyTradeReport.html', getDirectory]
    # files['act'] = ['ActivityStatement.html', getDirectory]
    # files['atrade'] = ['trades.643495.html', getDirectory]

    das = 'trades.csv'                          # Search verbatim with searchParts=False
                                                # TODO How to reconcile IB versus DAS input?

    sp = True
    for key in files:
        # fs = findFilesInDir(files[key][1](d), files[key][0], searchParts=sp)
        fs = findFilesSinceMonth(d, files[key][0])
        for f in fs:
            ibs = IbStatement()
            x = ibs.openIBStatement(f)
            if x[0]:
                print()
                for key in x[0]:
                    print (key, list(x[0][key].columns), len(x[0][key]))
                

            if x[1] and not x[0]:
                msg = f'\nStatement {f} \n{x[1]}'
                print(msg)
        print()

if __name__ == '__main__':
    # notmain()
    localStuff()
