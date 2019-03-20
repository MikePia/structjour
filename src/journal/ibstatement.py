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

### Using the html report as above might be the best approach. Using beautifulSoup, its easy to extract the needed table. The csv files don't have that metadata. Nevertheless, here is the csv version read into pandas.  Goig to havet tp use the csv tables as the metadata is variable depending on how you opened the document.

# def filterTrades_IBActivity(df):
#     newtrades = pd.DataFrame()
#     for i, row in df.iterrows():
#         print('testing', row['Quantity'], type(row['Quantity']))
#         if not math.isnan(row['Quantity']):
#             if not math.isnan(row['Basis']):
#                 newtrades = newtrades.append(row)
#     return newtrades

def floatValue(test):
    try:
        addme = float(test)
    except ValueError:
        return False, 0
    if math.isnan(addme) or addme == 0:
        return False, 0
    return True, addme

### Using the html report as above might be the best approach. Using beautifulSoup, its easy to extract the needed table. The csv files don't have that metadata. Nevertheless, here is the csv version read into pandas.  Goig to havet tp use the csv tables as the metadata is variable depending on how you opened the document.

def filterTrades_IBActivity(df):
    newtrades = pd.DataFrame()
    for i, row in df.iterrows():
        addme, tval = floatValue(row['T. Price'])
        dblchk, bval = floatValue(row['Basis'])
        if addme and dblchk and not row['Symbol'].lower().startswith('total'):
            newtrades = newtrades.append(row)

    return newtrades

# def filter_IBWebTradesTable(df):

#     newtrades = pd.DataFrame()
#     for i, row in df.iterrows():
#         if not math.isnan(row['Quantity']):
#             newtrades = newtrades.append(row)
#     return newtrades

def filter_IBWebTradesTable(df):

    newtrades = pd.DataFrame()
    for i, row in df.iterrows():
        addme, tval = floatValue(row['Quantity'])
        dblchk, bval = floatValue(row['Price'])
        trplchk, bval = floatValue(row['Proceeds'])
        
        
        if addme and dblchk and trplchk and not row[0].lower().startswith('total'):
            newtrades = newtrades.append(row)
    return newtrades

# def normColumns_IbCsv(df):
def normColumns_IBActivity(df):
    '''
    The so called norm will have to become the new norm. 
    This particular method is similar enough between CSV, Daily, and Activity to combine the 3 into one
    '''
    
    rc = ReqCol()
    
    df = df[['Date/Time', 'Symbol', 'T. Price', 'Quantity', 'Account',  'Proceeds', 'Code']].copy()
    df['PL'] = 0
    df['Date'] = df['Date/Time']
    df[rc.side] = ''
    df.Quantity = df.Quantity.astype(int)
    df['T. Price'] = df['T. Price'].astype(float)
    df['Proceeds'] = df['Proceeds'].astype(float)
    df['Code'] = df['Code'].astype(str)


    for i, row in df.iterrows():
        df.at[i, 'Date'] = df.at[i, 'Date'][:10]
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
    
    df = df[['Date/Time', 'Symbol', 'T. Price', 'Quantity', 'Account',  'Proceeds', 'Code']].copy()
    df['PL'] = 0
    df['Date'] = df['Date/Time']
    df[rc.side] = ''
    df.Quantity = df.Quantity.astype(int)
    df['T. Price'] = df['T. Price'].astype(float)
    df['Proceeds'] = df['Proceeds'].astype(float)
    df['Code'] = df['Code'].astype(str)


    for i, row in df.iterrows():
        df.at[i, 'Date'] = df.at[i, 'Date'][:10]
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


# For some reason, these tables do not include O/C in the displayed codes. The Activity statement does 
# as does the CSV statement
def normColumns_IBWeb(df):
#     df = df[['Trade Date/Time', 'Symbol', 'Type', 'Price', 'Quantity', 'Acct ID', 'Proceeds']].copy()
    rc = ReqCol()
    
    df = df[['Trade Date/Time', 'Symbol', 'Type', 'Price', 'Quantity', 'Acct ID', 'Proceeds', 'Code']].copy()
    df['PL'] = 0
    df['Date'] = df['Trade Date/Time']
    df[rc.side] = ''
    df['Proceeds'] = df['Proceeds'].astype(float)
    df['Code'] = df['Code'].astype(str)
    df['Price'] = df['Price'].astype(float)
    df['Quantity'] = df['Quantity'].astype(int)
    
    for i, row in df.iterrows():
        df.at[i, 'Date'] = df.at[i, 'Date'][:10]
        df.at[i, 'Trade Date/Time'] = df.at[i, 'Trade Date/Time'][12:]
        code = df.at[i, 'Code'].split(';')
        
        if df.at[i, 'Quantity'] < 0:
            df.at[i, rc.side] = 'S'
        else:
            df.at[i, rc.side] = 'B'

        setc=False
        for c in code:
            
            if c in ['O', 'C']:
                df.at[i, 'Code'] = c
                setc=True
                continue
        if not setc:
            df.at[i, 'Code'] = ''
        
    
    df = df.rename(columns={'Trade Date/Time': rc.time, 'Symbol': rc.ticker, 'Type': rc.side,
                            'Quantity': rc.shares, 'Acct ID': rc.acct, 'Code': 'O/C', 'PL': rc.PL})
    return df



def getTrades_IBActivity(url):
    '''
    Get trades from an IB statement that has a Transactions table and an Account Information table
    '''
    soup = BeautifulSoup(readit(url), 'html.parser')
    tbldivs = soup.find_all("div", id=lambda x: x and x.startswith('tblTransactions'))
    account = getId_IBActivity(soup)

    assert len(tbldivs) == 1
    # print(tbldivs[0].get('id'))

    tbldivs[0]

    tableTag = tbldivs[0].find("table")
    df = pd.read_html(str(tableTag))
    assert len(df) == 1
    
    df = filterTrades_IBActivity(df[0])
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
    newtrades['Account'] = id
    newtrades = normColumns_IbCsv(newtrades)
    return newtrades

def getTrades_IBDaily(url, rcols):
    # print(url)
    
    soup = BeautifulSoup(readit(url), 'html.parser')
    divTag = soup.find("div", {"id" : "tblTradesBody"})
    if not divTag:
        return pd.DataFrame()
    tableTag = divTag.find("table")
    df = pd.read_html(str(tableTag))
    if len(df) != 1:
        print('Failed to get 1 unique table ... try a different approach')
        return pd.DataFrame()
    # print(df[0].columns)
    for col in rcols:
        if not col in df[0].columns:
            print('Looks like the wrong table')
            return pd.DataFrame()
    df = filter_IBWebTradesTable(df[0])
    df = normColumns_IBWeb(df)
    
    return df

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

def runDaily():
    indir = 'C:/trader/journal/_201903_March/_0301_Friday/'
    infile = 'DailyTradeReport.20190301.html'

    inpathfile = os.path.join(indir, infile)
    assert os.path.exists(inpathfile)

    # These are the columns expected in the Daily Trades table from the web statement. There 
    # are differences from the Activity Web and CSV Statement.
    rcols = ['Acct ID', 'Symbol', 'Trade Date/Time', 'Settle Date', 'Exchange',
            'Type', 'Quantity', 'Price', 'Proceeds', 'Comm', 'Fee', 'Code']
    df = getTrades_IBDaily(inpathfile, rcols)
    return df


def main():
    df = runDaily()
    # df = filter_IBWebTradesTable(df[0])
    print(df)

if __name__ == '__main__':
    main()