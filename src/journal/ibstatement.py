import csv
import math
import sys
import os
# import ssl

from pandas import DataFrame, read_csv
# import matplotlib.pyplot as plt
import pandas as pd

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup, __version__ as bs4v

from journal.definetrades import ReqCol

print ('Python version ' + sys.version)
print('Pandas version ' + pd.__version__)
print('Beautiful Soup ' + bs4v)

def readit(url):
    data = ''
    if url.lower().startswith('http:'):
        data = urllib.request.urlopen(url).read()
    else:
        assert os.path.exists(url)
        with open(url) as f:
            data = f.read()
    return data

def getCSVData(csvfile):
    maxcols=0
    row0=None
    inlist=[]
    with open(csvfile, 'r') as cf :
        cread = csv.reader(cf)
        for row in cread:
            inlist.append(row)
            maxcols = len(row) if len(row) > maxcols else maxcols
    return inlist, maxcols

def getId_IbCvs(df):
    
    account = ''
    startnow=False
    for i, row in df.iterrows():
        if df.iloc[i][0] == 'Account Information':
            # print(df.iloc[i][2], df.iloc[i][3])
            if df.iloc[i][2] == 'Account':
                account = df.iloc[i][3]
                break
    return account

def dayPl(df):
    daypl = 0.0
    commission = 0.0
    # df = fred[0].copy()
    df['PL'] = 0.0
    # df['Realized P/L'] = df['Realized P/L'].astype(float)
    # df['Comm/Fee'] = df['Comm/Fee'].astype(float)
    for i, row in df.iterrows():
        if floatValue(row['Realized P/L'], includezero=True)[0]:
            assert floatValue(row['Comm/Fee'], includezero=True)[0]
            df.at[i, 'Realized P/L'] = float(df.at[i, 'Realized P/L'])
            df.at[i, 'Comm/Fee'] = float(df.at[i, 'Comm/Fee'])
            if not row['Symbol'].lower().startswith('total'):
                daypl = daypl + df.at[i, 'Realized P/L']
                commission = commission + df.at[i, 'Comm/Fee']
                # if 'P' in row['Code']:
                recordProfit = 'Sum P&L' if 'C' in row['Code'] else ''
                if recordProfit:
                    daypl = daypl - commission
                    # print('{:3}   {:10}   {}   {} = {}'.format(i, row['Realized P/L'], row['Symbol'], recordProfit, daypl))
                    df.at[i, 'PL'] = daypl
                    daypl = 0.0
                    commission = 0.0
                    # pl = 0
                # else:
                    # print('{:3}   {:10}   {}'.format(i, row['Realized P/L'], row['Symbol']))

    return df

def getId_IBActivity(soup):
    tbldivs = soup.find("div", id=lambda x: x and x.startswith('tblAccountInformation'))
    tbldivs.get('id')
    tableTag = tbldivs.find("table")
    tableTag
    
    df = pd.read_html(str(tableTag))
    account = ''
    for i, row in df[0].iterrows():
        if (row[0] == 'Account'):
            account = row[1]
    return account


def floatValue(test, includezero=False):
    try:
        addme = float(test)
    except ValueError:
        return False, 0
    if math.isnan(addme):
        return False, 0
    if not includezero and addme == 0:
        return False, 0
    return True, addme


def filterTrades_IBActivity(df):
    newtrades = pd.DataFrame()
    for i, row in df.iterrows():
        addme, tval = floatValue(row['T. Price'])
        dblchk, bval = floatValue(row['Basis'])
        if addme and dblchk and not row['Symbol'].lower().startswith('total'):
            newtrades = newtrades.append(row)

    return newtrades


def normColumns_IBActivity(df):
    '''
    The so called norm will have to become the new norm. 
    This particular method is similar enough between CSV, Daily, and Activity to combine the 3 into one
    '''
    
    rc = ReqCol()
    
    df = df[['Date/Time', 'Symbol', 'T. Price', 'Quantity', 'Account',  'Proceeds', 'PL', 'Code']].copy()
    # df['PL'] = 0
    df['Date'] = df['Date/Time']
    df[rc.side] = ''
    df.Quantity = df.Quantity.astype(int)
    df['T. Price'] = df['T. Price'].astype(float)
    df['Proceeds'] = df['Proceeds'].astype(float)
    df['Code'] = df['Code'].astype(str)


    for i, row in df.iterrows():
        # df.at[i, 'Date'] = df.at[i, 'Date'][:10]
        cleandate = pd.Timestamp(df.at[i, 'Date'])
        df.at[i, 'Date'] = cleandate.strftime('%Y-%m-%d %H:%M:%S')
        df.at[i, 'Date/Time'] = df.at[i, 'Date/Time'][12:]
        code = df.at[i, 'Code'].split(';')


        
        if df.at[i, 'Quantity'] < 0:
            df.at[i, rc.side] = 'S'
        else:
            df.at[i, rc.side] = 'B'

        for c in code:
            if c in ['O', 'C']:
                df.at[i, 'Code'] = c
                continue

    

    df = df.rename(columns={'Date/Time': rc.time, 'Symbol': rc.ticker, 'T. Price': rc.price,
                                    'Quantity': rc.shares, 'Account': rc.acct, 'Code': 'O/C', 'PL': rc.PL})
    return df

def normColumns_IbCsv(df):
    '''
    The so called norm will have to become the new norm. 
    This particular method is similar enough between CSV, Daily, and Activity to combine the 3 into one
    '''
    
    rc = ReqCol()
    
    df = df[['Date/Time', 'Symbol', 'T. Price', 'Quantity', 'Account',  'Proceeds', 'PL', 'Code']].copy()
    # df['PL'] = 0
    df['Date'] = df['Date/Time']
    df[rc.side] = ''
    df.Quantity = df.Quantity.astype(int)
    df['T. Price'] = df['T. Price'].astype(float)
    df['Proceeds'] = df['Proceeds'].astype(float)
    df['Code'] = df['Code'].astype(str)


    for i, row in df.iterrows():
        # df.at[i, 'Date'] = df.at[i, 'Date'][:10]
        df.at[i, 'Date/Time'] = df.at[i, 'Date/Time'][12:]
        code = df.at[i, 'Code'].split(';')


        
        if df.at[i, 'Quantity'] < 0:
            df.at[i, rc.side] = 'S'
        else:
            df.at[i, rc.side] = 'B'

        for c in code:
            if c in ['O', 'C']:
                df.at[i, 'Code'] = c
                continue

    

    df = df.rename(columns={'Date/Time': rc.time, 'Symbol': rc.ticker, 'T. Price': rc.price,
                                    'Quantity': rc.shares, 'Account': rc.acct, 'Code': 'O/C', 'PL': rc.PL})
    return df


def getTrades_IBActivity(url):
    '''
    Get trades from an IB statement that has a Transactions table and an Account Information table
    '''
    soup = BeautifulSoup(readit(url), 'html.parser')
    tbldivs = soup.find_all("div", id=lambda x: x and x.startswith('tblTransactions'))
    account = getId_IBActivity(soup)

    assert len(tbldivs) == 1

    tableTag = tbldivs[0].find("table")
    df = pd.read_html(str(tableTag))
    assert len(df) == 1
    
    df = dayPl(df[0])

    df = filterTrades_IBActivity(df)
    df['Account'] = account
    df = normColumns_IBActivity(df)

    return df

def getTrades_csv(infile):
    '''
    This file may contain many tables and eventually we should retrieve all of them.
    We need the Trades table. There at least two possible tables with a Trades heading.
    And then we need to filter out non-table rows like total, subtotal, washsale and others
    So we get this noodly approach instead of the cool pandas descriptive approach.
    '''
    # Get the max col length and data to import to DataFrame
    data, maxcol = getCSVData(infile)
    collist = [str(x) for x in range(maxcol) ]
    df = pd.DataFrame(data=data, columns=collist)
    
    id = getId_IbCvs(df)
    
    # Locat the correct Trades table. The other Trades table is a summary of Financial intstruments used.
    startnow = False
    data = []
    cols=[]

    for i, row in df.iterrows():
        # This identifies the header row for the our table, save them to cols, and start accumulating table data
        if df.iloc[i][0] == 'Trades' and 'Asset Category' in list(row):
            cols = list(row)
            startnow = True
            continue

        # Filter out the orders from the totals, subtotals and other stuff
        if df.iloc[i][0] == 'Trades' and startnow and df.iloc[i][1] == 'Data' and df.iloc[i][2] == 'Order':
            # print(df.iloc[i][0], df.iloc[i][1], row[0])
            # print(list(row))
            data.append(list(row))

    # newtrades
    newtrades = pd.DataFrame(data=data, columns=cols)
    newtrades = dayPl(newtrades)
    newtrades['Account'] = id
    newtrades = normColumns_IbCsv(newtrades)
    return newtrades


def runActivity():
    # url = 'http://localhost/DailyTradeReport.20180914.html'
    # filen= 'C:/xampp/htdocs/DailyTradeReport.20180914.html'
    indir = 'C:/trader/journal/_201903_March/_0301_Friday/'
    # infile = 'DailyTradeReport.20190301.html'


    infile= 'ActivityStatement.20190301.html'
    inpathfile = os.path.join(indir, infile)
    # print(inpathfile)
    assert os.path.exists(inpathfile)

    df = getTrades_IBActivity(inpathfile)
    return df

def runCSV():
    # infile="U2429974_20180913_20180913.csv"
    indir = r'C:/trader/journal/_201903_March/_0301_Friday/'
    infile=r"U2429974_20190301_20190301.csv"
    inpathfile = os.path.join(indir, infile)
    assert os.path.exists(inpathfile)

    df = getTrades_csv(inpathfile)
    return df



def main():
    df = runCSV()
    print(df)
    df = runActivity()
    print(df)

    # df = filter_IBWebTradesTable(df[0])
    # print(df)

if __name__ == '__main__':
    main()