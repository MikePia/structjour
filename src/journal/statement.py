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
from journal.dfutil import DataFrameUtil

print ('Python version ' + sys.version)
print('Pandas version ' + pd.__version__)
print('Beautiful Soup ' + bs4v)


class Statement_DAS(object):
    '''
    Take an input CSV file of all trade transactions and reduce the transactions to tickets. Use the
    JournalFiles class as the single point of contact with  input and output.  When the new file is
    created, alter the Journalfiles indir/infile to the new file
    :params:jf: The JournalFile Object. It has the input files we need.
    '''

    def __init__(self, jf, df=None):
        self.jf = jf
        if not isinstance(df, pd.DataFrame):
            self.df = pd.read_csv(self.jf.inpathfile)
        else:
            self.df = df
        if 'Date' not in self.df.columns:
            self.df['Date'] = jf.theDate
        rc = ReqCol()
        DataFrameUtil.checkRequiredInputFields(self.df, rc.columns)

    def _checkUniqueSIMTX(self):
        '''
        Check the SIM transactions for uniqueness within (ticker, time, account). I believe these
        are always necessarily unique. I need to know if they are not.  If found,the program
        should fail or alert the user and work around
        '''
        rc = ReqCol()
        dframe = self.df

        #HACK ALERT
        #This is guaranteed to cause some future problem
        # If Cloid has some Sim ids ('AUTO') the column must have some str elements. Without this
        # it throws a TypeError and a Future Warning about changing code. For DataFrame columns
        # without any sim trades there are only floats. This is not guaranteed behavior, just
        # observed from my runs. And there there is some weirdness between numpy types and python
        # regarding what type to return for this comparison--and it may change in the future.
        # if len(dframe.Cloid.apply(lambda x: isinstance(x, str))) < 1 :

        doSomething = False
        for t in dframe['Cloid']:
            if isinstance(t, str):
                doSomething = True
                break
        if not doSomething:
            return

        df = dframe[dframe['Cloid'] == "AUTO"]

        tickerlist = list()
        for dummy, row in df.iterrows():
            tickerlist.append((row[rc.time], row[rc.ticker], row[rc.acct]))

            tickerset = set(tickerlist)
            if len(tickerset) != len(tickerlist):
                # print("\nFound a Sim ticket that is not unique.
                # This should not be possible (but it happens).{}".format(tickerlist[-1]))
                return

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
        Take the standard trades.csv DataFrame a list in which each list member is a DataFrame that
        contains the transactions that create a single ticket.
        This is made more interesting by the SIM transactions. They have no ticket ID (Cloid). They
        are identified in DAS by 'AUTO.' We will give them an ID unique for this run. There is only,
        presumably one ticket per SIM transaction, but check for uniqueness and report. (Found one
        on 10/22/28 -- a SIM trade on SQ. Changed the code not to fail in the event of an identical
        transx.)
        :return: A list of DataFrames, each list member is one ticket with 1 or more transactions.

        PROGRAMMING NOTE: This SIM ticket will most definitely not be found unique between different
        days Use the 10/22/28 input file in a test and fix it.
        '''

        dframe = self.df
        self._checkUniqueSIMTX()

        doSomething = False
        for t in dframe['Cloid']:
            if isinstance(t, str):
                doSomething = True
                break

        # Get the SIM transactions from the origainal DataFtame.
        # Change the Cloid from Auto to SIMTick__XX
        if doSomething:
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

        if doSomething:
            for simTkt in SIMdf.Cloid.unique():
                t = SIMdf[SIMdf['Cloid'] == simTkt]
                listOfTickets.append(t)

        return listOfTickets


    def getPositions(self):
        if not self.jf.infile2:
            return ''
        df = pd.read_csv(self.jf.inpathfile2)
        reqcol = ['Symb', 'Account', 'Shares', 'Avgcost', 'Unrealized']
        df = df[reqcol].copy()
        newtrades = pd.DataFrame()
        for i, row in df.iterrows():
            addme, tval = floatValue(row['Avgcost'])
            dblchk, tval = floatValue(row['Shares'])
            if addme and dblchk: 
                newtrades = newtrades.append(row)

        return newtrades


    def getTrades(self, listDf=None):
        '''
        Create an alternate dataFrame by ticket. For large share sizes this may have dramatically
        fewer transactions. 
        :params listDf: Normally leave blank. If used, listDf should be the be a list of DFs.
        :params jf: A JournalFiles object as this new CSV file needs to be written into the outdir.
        :return: The DataFrame created version of the data.
        :side effects: Saves a csv file of all transactions as single ticket transactions to
                        jf.inpathfile
        '''
        # TODO: Add the date to the saved file name after we get the date sorted out.
        rc = ReqCol()
        if not listDf:
            listDf = self.getListOfTicketDF()
        DataFrameUtil.checkRequiredInputFields(listDf[0], rc.columns)

        newDF = DataFrameUtil.createDf(listDf[0], 0)

        for tick in listDf:
            t = self.createSingleTicket(tick)
            newDF = newDF.append(t)

        outfile = "tradesByTicket.csv"
        opf = os.path.join(self.jf.indir, outfile)
        newDF.to_csv(opf)
        self.jf.resetInfile(outfile)

        return newDF, self.jf

class Statement_IBActivity:

    def __init__(self, jf):
        self.jf = jf
    
    def getUnbal_IBActivity(self, url=None, soup=None):
        '''
        Get unbalanced positions IB Activity statement. The statement must have a Trades table 
        and an Open Positions table. The return value is a list of stocks that were bought or sold
        in this statement and their current position. Other positions, not traded today, are left out.
        :params url: File location of the Activity Statement as an html doc
        :return: List of [symbol, bal] indicating the number of shares that are held as of the 
        time of the statement
        '''
        if url:
            soup = BeautifulSoup(readit(url), 'html.parser')
        positions = self.getPositions(None, soup)
        tbldivs = soup.find_all("div", id=lambda x: x and x.startswith('tblTransactions'))
        account = getId_IBActivity(soup)
        assert len(tbldivs) == 1
        tableTag = tbldivs[0].find("table")
        df = pd.read_html(str(tableTag))
        assert len(df) == 1
        df = filterTrades_IBActivity(df[0])
        curPositions = list()
        for s in df.Symbol.unique():
            if s in positions.Symbol.unique():
                daybal = float(positions[positions.Symbol == s].Quantity)
            else:
                daybal = 0
            if daybal != 0:
                curPositions.append([s, daybal])
        
        return curPositions

    
    def getDate_IBActivity(self, url, soup=None):
        '''
        Get the date from tblNAV aka 'Net Asset Value table'    '''
        soup = BeautifulSoup(readit(url), 'html.parser')
        navdivs = soup.find_all("div", id=lambda x: x and x.startswith('tblNAV'))
        assert len(navdivs) == 1
        navTag = navdivs[0].find('table')
        ndf = pd.read_html(str(navTag))
        assert len(ndf) == 1
        d = ndf[0].iloc[0][2]
        try:
            d = pd.Timestamp(d)
            'Activity Statements come after after hours'
            d = pd.Timestamp(d.year, d.month, d.day, 18, 0, 0)
        except ValueError:
            
            raise ValueError(
                '''Failed to retrieve date from IB Activity Statement.
                Statement must include the tables 
                    Trades, 
                    Open Positions
                    Account Information
                    Net Asset Value (for the date)
                ''')
            
        return d



    def getId_IBActivity(self, soup = None, url=None):
        if url:
            soup = BeautifulSoup(readit(url), 'html.parser')
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

    def getPositions(self, soup=None):
        '''
        Get open positions from the IB statement. Will retrieve a tabel with three columns:
        Symb, Shares and Account
        '''
        if soup == None:
            soup = BeautifulSoup(readit(self.jf.inpathfile), 'html.parser')
        tbldivs = soup.find_all("div", id=lambda x: x and x.startswith('tblOpenPositions'))
        account = self.getId_IBActivity(soup)

        assert len(tbldivs) == 1

        tableTag = tbldivs[0].find("table")
        df = pd.read_html(str(tableTag))
        assert len(df) == 1
        newtrades = pd.DataFrame()
        for i, row in df[0].iterrows():
            addme, tval = floatValue(row['Quantity'])
            if addme: 
                newtrades = newtrades.append(row)

        if not newtrades.empty:
            newtrades = newtrades[['Symbol', 'Quantity']].copy()
            newtrades['Account'] = account
            newtrades = newtrades.rename(columns={'Symbol': 'Symb', 'Quantity': 'Shares'})
        return newtrades



    def filterTrades_IBActivity(self, df):
        newtrades = pd.DataFrame()
        for i, row in df.iterrows():
            addme, tval = floatValue(row['T. Price'])
            dblchk, bval = floatValue(row['Basis'])
            if addme and dblchk and not row['Symbol'].lower().startswith('total'):
                newtrades = newtrades.append(row)

        return newtrades


    def normColumns_IBActivity(self, df):
        '''
        The so called norm will have to become the new norm. 
        This particular method is similar enough between CSV, Daily, and Activity to combine the 3 into one
        '''

        rc = ReqCol()
        if 'PL' not in df.columns:
            df['PL'] = 0
        df = df[['Date/Time', 'Symbol', 'T. Price', 'Quantity', 'Account',  'Proceeds', 'PL', 'Code']].copy()

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


    def figurePL_IBActivity(self, df, soup=None, url=None):
        df = df.copy()
        df['bal'] = 0
        df['PL'] = 0.0
        df['avg'] = 0.0
        df['mkt'] = 0.0
        # df = df[['Symbol', 'Date/Time', 'Quantity', 'bal', 'T. Price', 'Comm/Fee', 'Realized P/L', 'PL', 'avg', 'Code', 'Proceeds', 'mkt' ]].copy()

        newtrade = pd.DataFrame(columns = df.columns)
        # unbal = self.getUnbal_IBActivity(soup=soup, url=url)
        for s in df['Symbol'].unique():
            tdf = df[(df.Symbol == s)].copy()
            bal = costSum = comSum = total = 0.0

            firsttrade = True
            avg = 0
            for count, (i, row) in enumerate(tdf.iterrows()):
                PL = 0.0
                symb, qty, price, comm,  rpl, code = list(row[['Symbol',  'Quantity', 'T. Price', 'Comm/Fee', 'Realized P/L', 'Code',]])
                
                try:
                    qty = int(qty) if qty else 0
                    price = float(price) if price else 0.0
                    rpl = float(rpl) if rpl else 0.0
                    comm = float(comm) if comm else 0.0

                except ValueError:
                    msg = f'Bad Value in {row} found in {__file__}'
                    raise ValueError(msg)
                    
                comSum = comSum + comm

                if tdf.iloc[0].Code == 'C':
                    if row['Code'] == 'C':
                        mkt = qty * price
                        PL = rpl - comSum

                if tdf.iloc[0].Code == 'O':


                    bal = bal + qty
                    mkt = qty * price
                    costSum = costSum + mkt
                    if firsttrade:
                        avg = price
                    if code == 'O':
                        if bal != 0:
                            avg = costSum/bal
                    elif code == 'C':
                        PL = (avg - price) * qty
                        total = total + PL


                tdf.at[i, 'bal'] = bal
                tdf.at[i, 'PL'] = PL
                tdf.at[i, 'avg'] = avg
                tdf.at[i, 'mkt'] = mkt

                newtrade = newtrade.append(tdf.loc[i])

                firsttrade = False


        return newtrade


    def getTrades_IBActivity(self, url):
        '''
        Get trades from an IB statement that has a Transactions table and an Account Information table
        '''
        soup = BeautifulSoup(readit(url), 'html.parser')
        tbldivs = soup.find_all("div", id=lambda x: x and x.startswith('tblTransactions'))
        account = self.getId_IBActivity(soup)

        assert len(tbldivs) == 1

        tableTag = tbldivs[0].find("table")
        df = pd.read_html(str(tableTag))
        assert len(df) == 1


        df = self.filterTrades_IBActivity(df[0])
        df['Account'] = account
        print('fkna')
        df = self.figurePL_IBActivity(df, soup=soup)
        df = self.normColumns_IBActivity(df)

        return df


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