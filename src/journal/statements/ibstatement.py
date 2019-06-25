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
        self.begindate = None
        self.enddate = None
        self.inputType = None

    def parseTitle(self, t):
        '''
        The html title tag of the activity statement contains statement info. There are no specs to
        the structure of the thing. So on failure, raise exceptions. By trial and error, find the
        available formats. Especially multi day format must be different than this one. So just
        raise exceptions everywhere until comfortable that all cases are covered. 
        '''
        st = dict()

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

            self.begindate = pd.Timestamp(theDate)
            self.account = account
            self.statementname = sname

        except:
            raise ValueError('Failed to parse the statement date')

    def doctorHtmlTables(self, tabd):
        tabs = ['AccountInformation', 'OpenPositions', 'Transactions']
        for key in tabd:
            if key in ['OpenPositions', 'Transactions']:
                df = tabd[key]
                df = df[df['Symbol'].str.startswith('Total') == False]
                df = df.iloc[2:]
                tabd[key] = df.copy()
            elif key == 'AccountInformation':
                tabd[key].columns = ['Field Name', 'Field Value']
        return tabd

    def openIBStatementHtml(self, infile):
        if not os.path.exists(infile):
            return
        soup = BeautifulSoup(readit(infile), 'html.parser')
        tbldivs = soup.find_all("div", id=lambda x: x and x.startswith('tbl'))
        title = soup.find('title').text
        self.parseTitle(title)
        tables = dict()
        for tableTag in tbldivs:
            continueit = True
            tabKey = ''
            for key in ['tblAccountInformation', 'tblOpenPositions', 'tblTransactions']:
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
            print()
        if 'Transactions' not in tables.keys():
            # This should maybe be a dialog
            msg = 'The statment lacks a trades table; it has no information of interest.'
            print(msg)
            return dict()
        self.doctorHtmlTables(tables)
        return tables

    def openIBStatementCSV(self, infile):
        '''
        Identify a csv file as a type of IB Statement and send to the right place to open it
        '''
        if os.path.exists(infile):
            print('so far ...')
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
            return {'Trades': df}, {'Trades': 'Trades'}
        elif df.iloc[0][0] == 'Statement':
            # This is a multi table statement like a default statement
            self.inputType = 'ACTIVITY'
            return self.getTablesFromDefaultStatement(df)
        return None, None

    def getTablesFromDefaultStatement(self, df):
        '''
        From a default Activity statement csv, retrieve AccountInformation, OpenPositions, and
        Trades
        '''
        # df = pd.read_csv(infile, header=range(0,15))
        keys = df[0].unique()
        tables = dict()
        tablenames = list()
        for key in keys:
            if key not in ['Statement', 'Account Information', 'Open Positions', 'Short Open Positions', 'Long Open Positions', 'Trades']:
                continue

            tab = df[df[0] == key]
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
                        raise ValueError(
                            'A Programmer thing-- want to see it occur before I write code to handle it')
                    tables['OpenPositions'] = tables['OpenPositions'].append(
                        tab)
                    continue
                else:
                    key = 'OpenPositions'
            elif key == 'Trades':
                # We want the rows where DataDiscriminator=Trade
                tab = tab[tab['DataDiscriminator'].str.lower() == 'trade']
                tab = tab.rename(columns={'T. Price': 'Price', 'Comm/Fee': 'Commission'})
                tab['Account'] = self.account
                tab = tab.drop('DataDiscriminator', axis=1)
                tab = tab.rename(columns={'Code': 'Codes', 'Date/Time': 'DateTime'})

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
                else:
                    self.beginDate = test[0].strip()
                    self.endDate = test[1].strip()
                    self.beginDate = pd.Timestamp(self.beginDate)
                    self.endDate = pd.Timestamp(self.endDate)
            elif key == 'Account Information':
                self.account = tab[tab['Field Name'] == 'Account']['Field Value'].unique()[0]

                

            key = key.replace(' ', '')
            tables[key] = tab

            # tab.columns = currentcols
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
            begindate = df.iloc[0][4]
            self.begindate = pd.Timestamp(begindate)
            enddate = df.iloc[0][5]
            self.enddate = pd.Timestamp(enddate)

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
                        self.verifyAvailableCols(
                            currentcols, ourcols, tabid + names)
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
                    t = t.rename(columns={'OpenC/CloseIndicator': 'Codes'})

                    print()

                # Assign to dict and return
                tables[tabid] = t
                tablenames[tabid] = names
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
                         'Long Open Positions', 'Short Open Positions', 'Trades', 'FlexTrades']:
            return []
        if tabid == 'ACCT':
            return ['ClientAccountID', 'AccountAlias']

        if tabid in ['POST', 'Open Positions', 'OpenPositions']:
            return ['Symbol', 'Quantity']

        if tabid in ['Long Open Positions', 'Short Open Positions']:
            # DataDiscriminator is temporary to filter results
            return ['Symbol', 'Quantity', 'DataDiscriminator']

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
            return [ 'ClientAccountID', 'Symbol', 'Date/Time', 'Quantity', 'Price', 'Commission', 'Code', 'LevelOfDetail' ]


        ####### Activity Statement non flex #######
        if tabid == 'Statement':
            return ['Field Name', 'Field Value']

        if tabid.find('Positions') > -1:
            raise ValueError('Fix it!!!')

        # Trades= ['ClientAccountID', 'AccountAlias', 'Symbol', 'Conid', 'ListingExchange', 'TradeID', 'ReportDate', 'TradeDate',              'Date/Time',              'Buy/Sell', 'Quantity',  'Price',      'TransactionType',  'Commission',                          'Code',       'LevelOfDetail', ]

    def verifyAvailableCols(self, flxcols, ourcols, tabname):
        '''
        Check flxcols against ourcols, remove any cols in ourcols that are missing in flxcols and
        send a warning
        '''
        missingcols = set(ourcols) - set(flxcols)
        if missingcols:
            print(f'WARNING: {tabname} is missing the columns {missingcols}')
            for col in missingcols:
                ourcols.remove(col)
        return ourcols


class StatementDB:
    '''
    Methods to create and manage tables to store Activity Statements. Fields are exactly IB fields
    from activity flex query
    '''

    def __init__(self, db):
        '''Initialize and set the db location'''
        self.db = db

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
            print()
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

    #These are patterns, not necessariy file names
    flexTid = 'TradeFlexMonth.327778.csv'
    flexAid = 'ActivityFlexMonth.369463.csv'
    activityDaily = 'ActivityDaily.663710.csv'
    activityMonth = 'CSVMonthly.644225.csv'     # Search monthly with freq='MonthlyDir'
    dtr = 'DailyTradeReport.html'
    das = 'trades.csv'                          # Search verbatim with  searchParts=False

    f = dtr
    
    fs = findFilesSinceMonth('2019-01', f) 
    # for i in range(1,7):
    #     pat = f'{f[1]}.{f[0]}.{f[2]}'
    #     fs = findFilesInMonth(d, pat, True)
    print()
    for f in fs:
        print(f)

if __name__ == '__main__':
    notmain()
