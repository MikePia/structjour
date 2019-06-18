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
Re-implementing the ib csv statement stuff to get a general solution that can be stored in a db
@author: Mike Petersen
@creation_data: 06/15/19
'''

import math
import os
import sqlite3

from PyQt5.QtCore import QSettings
import numpy as np
import pandas as pd

from bs4 import BeautifulSoup
import urllib.request

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
        try:
            t, broker = t.split('-')
        except ValueError:
            raise ValueError('Failed to parse the statement date')
        
        broker = broker.strip()
        self.broker = broker
        t = t.strip()
        t = t.split(' ')
        if len(t) == 6:
            account = t[0]
            sname = ' '.join([t[1], t[2]])
            theDate = ' '.join([t[3], t[4], t[5]])
        elif len(t) == 5:
            account = t[0]
            sname =  t[1]
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
            df = df[0]    #.replace(np.nan, '')
            # tables[tableTag['id']] = df[0]
            tables[tabKey] = df
            print()
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
            #This is a flex activity statement with multiple tables
            self.inputType = "A_FLEX"
            return self.getTablesFromMultiFlex(df)

        elif df.iloc[0][0] =='ClientAccountID':
            # This is a single table file. Re read to get default column names from row 1
            df = pd.read_csv(infile)
            self.inputType = 'T_FLEX'
            return {'Trade' : df}, {'Trade' : 'Trade'}
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
            if key not in ['Statement', 'Account Information', 'Open Positions', 'Trades']:
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
                    tab = tab[tab[1] == 'Data']
                    tab = tab[cols].copy()
                    tables[key] = tab

                    break
                else:
                    print('do the same thing?')
                    tab.columns = currentcols
                    tab = tab[cols].copy()
                    tables[key] = tab
            # tab.columns = currentcols
        return tables, tablenames

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
            x = df[df[0] == 'BOS']


            tabids = x[1]
            for tabid in tabids:
                ourcols = ft.getColsByTabid(tabid)
                if not ourcols:
                    continue

                t = df[df[1] == tabid]
                names = t.iloc[0][2]

                t = t[t[0] != 'EOS']
                t = t[t[0] != 'BOS']

                # Get the columns as found in the FLEX file then edit the columns to our liking
                cols = list()
                currentcols = list(t.columns)
                for i, col in enumerate(t[t[0] == 'HEADER'].iloc[0]):
                    if col and isinstance(col, str):
                        if col in ['HEADER', tabid]:
                            continue
                        cols.append(col)
                        currentcols[i] = col
                    elif isinstance(col, float) and math.isnan(col):
                        t.columns = currentcols
                        t = t[t[1] == 'Data']
                        t = t[t[0] != 'HEADER']
                        t = t[ourcols].copy()
                        break
                    else:
                        msg = ''.join(['A Programmer thing: Probably do the same thing as the elif',
                                       'but I want to see why it occurs.'])
                        raise ValueError(msg)

                tables[tabid] = t
                tablenames[tabid] = names
        else:
            return None
        return tables, tablenames

    def getColsByTabid(self, tabid):
        '''
        Using the tableids from the Flex queries, we are interetsed in these tables only and in
        the columns we define here only. If that is incorrect, change it here. If table columns
        are not defined here, we won't save it.
        '''

        #######  From the Flex Activity statement #######
        if tabid not in ['ACCT', 'POST', 'TRNT']:
            return []
        if tabid == 'ACCT':
            return ['ClientAccountID', 'AccountAlias']

        if tabid == 'POST':
            return ['Symbol', 'Quantity', 'Side', 'LevelOfDetail']

        if tabid == 'TRNT':
            return ['ClientAccountID', 'AccountAlias', 'Symbol', 'Conid', 'ListingExchange', 
                    'TradeID', 'ReportDate', 'TradeDate', 'TradeTime', 'OrderTime', 'Buy/Sell',
                    'Quantity', 'TradePrice',  'TransactionType', 'IBCommission',
                    'Open/CloseIndicator', 'Notes/Codes', 'LevelOfDetail', ]

        ####### Activity Statement non flex #######
        if tabid == 'Statement':
            return ['Field Name', 'Field Value']

        if tabid == 'Open Positions':
            return ['Symbol', 'Quantity']

        # Trade= ['ClientAccountID', 'AccountAlias', 'Symbol', 'Conid', 'ListingExchange', 'TradeID', 'ReportDate', 'TradeDate',              'Date/Time',              'Buy/Sell', 'Quantity',  'Price',      'TransactionType',  'Commission',                          'Code',       'LevelOfDetail', ]

        if tabid == 'Trade':
            pass
            # The input fields differ. Here are the relavanat fields from the different input file types
            # AHTML= [                                   'Symbol',                                                                                'Date/Time',                          'Quantity', 'T. Price',                        'Comm/Fee',               'Code' ]

        if tabid == 'Trade':
            return ['ClientAccountID', 'AccountAlias', 'Symbol', 'Conid', 'ListingExchange',
                    'TradeID', 'ReportDate', 'TradeDate', 'Date/Time', 'Buy/Sell', 'TransactionType',
                    'Quantity', 'Price', 'Exchange',  
                    'Amount',   
                    'Commission',
                    'BrokerExecutionCommission', 'BrokerClearingCommission',
                    'ThirdPartyExecutionCommission', 'ThirdPartyClearingCommission',
                    'ThirdPartyRegulatoryCommission', 'OtherCommission', 'Code',
                    'LevelOfDetail']


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


def localstuff():
    basedir = 'C:/trader/journal/'
    settings = QSettings('zero_substance', 'structjour')
    scheme = settings.value('scheme')
    d = pd.Timestamp('2019-06-14')
    scheme = d.strftime(scheme.format(
        Year='%Y', month='%m', MONTH='%B', day='%d', DAY='%A'))
    daDir = os.path.join(basedir, scheme)
    fn = 'ActivityStatement.20190614.html'
    fn = os.path.join(daDir, fn)
    ibs = IbStatement()
    ibs = ibs.openIBStatementHtml(fn)


def notmain():
    '''Run some local code'''
    testdb = 'C:/python/minituts/test.sqlite'
    # ft = StatementDB(testdb)

    basedir = 'C:/trader/journal/'
    settings = QSettings('zero_substance', 'structjour')
    scheme = settings.value('scheme')
    d = pd.Timestamp('2019-06-14')
    scheme = d.strftime(scheme.format(
        Year='%Y', month='%m', MONTH='%B', day='%d', DAY='%A'))
    daDir = os.path.join(basedir, scheme)

    # fn = 'ActivityFlexMonth.csv'                # Activity flex Month
    # fn = 'TradeFlexMonth.csv'                 # Trade Flex Month (single table)
    fn = 'U2429974_20190614_20190614.csv'     # default Activity
    # fn = 'U2429974_U2429974_2018_2018_AS_Fv2_b05f9463b268e093e7a94039001e60f7.csv'
    # fn = os.path.join(basedir, fn)

    # fn = 'CSVMonthly.644225.201905.csv'
    # ddir = os.path.join(basedir, '_201905_May/')
    # fn = os.path.join(ddir, fn)
    #This is the ib given name of a default statement download
    fn = os.path.join(daDir, fn)

    ibs = IbStatement()

    tabs, names = ibs.openIBStatementCSV(fn)

    for key in tabs:
        print(key, len(list(tabs[key].columns)))

    # print(names['ACCT'])
    # tabname = names['ACCT'].lower().replace(' ', '_')

    # tabs['ACCT'].columns, tabname

    # ft.genericTbl(tabname, list(tabs['ACCT'].columns))

if __name__ == '__main__':
    # notmain()
    localstuff()