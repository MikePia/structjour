'''
Created on Sep 5, 2018

@author: Mike Petersen
'''
import sys, datetime
# from journal.pandasutil import DataFrameUtil
from journal.dfutil import DataFrameUtil
# import str

# from tkinter.tix import Balloon

class FinReqCol(object) :
    '''
    Intended to serve as the adapter class for multiple input files. FinReqCol manages the column names fot 
    the output file. It includes some of the input columns and additional columns  to identify seprate trades and sorting.
    The columns we add are tix, start, bal, sum, dur, and name
    :SeeAlso: journal.thetradeobject.SumReqFields
    '''
    def __init__(self, source = 'DAS') :
        
        if source != 'DAS' :
            print("Only DAS is implemented")
            raise(ValueError)


        # frcvals are the actual column titles (to be abstracted when we add new input files)
        # frckeys are the abstracted names for use with all file types
        frcvals = ['Tindex', 'Start', 'Time', 'Symb', 'Side', 'Price', 'Qty','Balance', 'Account', "P / L", 'Sum', 'Duration', 'Name']
        frckeys = ['tix', 'start', 'time', 'ticker', 'side', 'price', 'shares', 'bal', 'acct', 'PL', 'sum', 'dur', 'name']
        frc = dict(zip(frckeys, frcvals))

        #Suggested way to address the columns for the main output DataFrame. 
        self.tix = frc['tix']
        self.start = frc['start']
        self.time = frc['time']
        self.ticker = frc['ticker']
        self.side = frc['side']
        self.price = frc['price']
        self.shares = frc['shares']
        self.bal = frc['bal']
        self.acct = frc['acct']
        self.PL = frc['PL']
        self.sum = frc['sum']
        self.dur = frc['dur']
        self.name = frc['name']
        
        #provided for methods that need a list of columns (using e.g. frc.values())
        self.frc = frc
        self.columns = list(frc.values())

        
class ReqCol(object):
    '''
    Intended as an adapter class for multiple input types. ReqCol are the columns for the original input file
    All of these are required.
    '''
    
    
        
    def __init__(self, source="DAS"):
        '''Set the required columns in the import file.'''
        
        if source != 'DAS' :
            print("Only DAS is currently supported")
            raise(ValueError)
        
        # rcvals are the actual column titles (to be abstracted when we add new input files)
        # rckeys are the abstracted names for use with all file types
        rckeys = ['time', 'ticker', 'side', 'price', 'shares', 'acct', 'PL']
        rcvals = ['Time', 'Symb', 'Side', 'Price', 'Qty', 'Account', 'P / L']
        rc  = dict(zip(rckeys, rcvals))

        #Suggested way to address the columns for the main input DataFrame. 
        self.time = rc['time']
        self.ticker = rc['ticker']
        self.side = rc['side']
        self.price = rc['price']
        self.shares = rc['shares']
        self.acct = rc['acct']
        self.PL = rc['PL']

        self.rc = rc
        self.columns = list(rc.values())


      
class TradeUtil(object):
    '''
    TradeUtil moves the data from DataFrame to a formatted excel format object. It will compose a Trade class that will 
    encapsulate a trade including each transaction, and all the user input (target price, stop price, strategy, 
    explanation, extended notes and short notes. A data structure will be used to format this information in a way
    that makes review of the trade the prime concern using an openpyxl excel object.
    '''

    def __init__(self, source='DAS'):
        '''
        Constructor
        '''
        self._frc = FinReqCol(source)
        
    def processOutputDframe(self, trades):
        finalReqCol = FinReqCol()

        #Process the output file DataFrame
        trades = self.addFinReqCol(trades)
        newTrades = trades[finalReqCol.columns]
        newTrades.copy()
        nt = newTrades.sort_values([finalReqCol.ticker,finalReqCol.acct,  finalReqCol.time])
        nt = self.writeShareBalance(nt)
        nt = self.addStartTime(nt)
        nt = nt.sort_values([finalReqCol.start, finalReqCol.acct, finalReqCol.time])
        nt = self.addTradeIndex(nt)
        nt = self.addTradePL(nt)
        nt = self.addTradeDuration(nt)
        nt = self.addTradeName(nt)
        nt = DataFrameUtil.addRows(nt,2)
        nt = self.addSummaryPL(nt)
        ldf= self.getTradeList(nt)         # ldf is a list of DataFrames, one per trade

        inputlen = len(nt)              # Get the length of the input file in order to style it in the Workbook
        dframe = DataFrameUtil.addRows(nt, 2)
        return inputlen, dframe, ldf

    def writeShareBalance(self, dframe) :
        prevBal = 0
        c = self._frc
        
        for i, dummy_row in dframe.iterrows():
            qty = (dframe.at[i, c.shares])
#             if row[c.side].startswith("HOLD") :
# #                 print("got it at ", qty)
#                 qty = qty * -1
            newBalance = qty + prevBal
    
            dframe.at[i, c.bal] = newBalance 
            prevBal = newBalance    
        return dframe
    
    def addStartTime(self, dframe) :
        
        c = self._frc

        newTrade = True
        for i, row in dframe.iterrows():
            if newTrade :
                if row[c.side].startswith('HOLD') and i < len(dframe):
                    
                    oldTime = dframe.at[i+1, c.time]
    #                 print("     :Index: {0},  Side: {1}, Time{2}, setting {3}".format(i, row['Side'], row['Time'], oldTime))
                    dframe.at[i, c.start] = oldTime
    
                else :
                    oldTime = dframe.at[i, c.time]
                    dframe.at[i, c.start] = oldTime
                    
                newTrade = False
            else :
    #             print("      Finally :Index: {0},  Side: {1}, Time{2}, setting {3}".format(i, row['Side'], row['Time'], oldTime))
                dframe.at[i, c.start] = oldTime
            if row[c.bal] == 0 :
                newTrade = True
        return dframe
   
    def addTradeIndex(self, dframe) :
        '''
        Labels and numbers the trades by populating the TIndex column. 'Trade 1' for example includes the transactions 
        between the initial purchase or short of a stock and its subsequent 0 position. (If the stock is held overnight, 
        non-transaction rows have been inserted to account for todays' activities.)
        '''
        
        c = self._frc

        TCount = 1
        prevEndTrade = -1
    
        for i, row in dframe.iterrows():
            if len(row[c.ticker]) < 1 :
                break
            tradeIndex = "Trade " + str(TCount)
            if prevEndTrade == 0:
                TCount = TCount + 1
                prevEndTrade = -1
            tradeIndex = "Trade " + str(TCount)
            dframe.at[i,c.tix] = tradeIndex 
            if row[c.bal] == 0 :
                prevEndTrade = 0
        return dframe
    
    def addTradePL (self, dframe) :
        ''' Add a trade summary P/L. That is total the transaction P/L and write a summary P/L for the trade in the c.sum column '''

        c = self._frc        

        tradeTotal = 0.0
        for i, row in dframe.iterrows():
            if row[c.bal] != 0 :
                tradeTotal = tradeTotal + row[c.PL]
            else :
                sumtotal = tradeTotal + row[c.PL]
                dframe.at[i, c.sum] = sumtotal
                tradeTotal = 0
        return dframe
    
    def addTradeDuration(self, dframe) :
        ''' Get a time delta beween the time of the first and last transaction. Place it in the c.dur column'''
        
        c = self._frc

        for i, row in dframe.iterrows():
            if row[c.bal] == 0 :
                timeEnd = row[c.time]
                timeStart = row[c.start]
                end=timeEnd.split(":")
                start=timeStart.split(":")
                diff = datetime.datetime(1,1,1,int(end[0]), int(end[1]), int(end[2])) - datetime.datetime(1,1,1,int(start[0]), int(start[1]), int(start[2]))
                dframe.at[i, c.dur] = diff
        return dframe
    
    def addTradeName(self, dframe) :
        '''Create a name for this trade like 'AMD Short'. Place it in the c.name column'''
            
        c= self._frc
        
        for i, row in dframe.iterrows():
            longShort = " Long"
            if row[c.bal] == 0 :
                if row[c.side] == 'B' :
                    longShort = " Short"
                dframe.at[i, c.name] = row[c.ticker] + longShort
        return dframe
    
    def addSummaryPL(self, dframe) :
        ''' 
        Create a summary of the P/L for the day, place it in new row. 
        Sum up the transactions in c.PL for Live and Sim Seperately.
        We rely on the account number starting with 'U' or 'TR' to determine
        live or SIM. These two columns should add to the same amount. '''
        # TODO sum up the seperate accounts and make a new labeled entry for each account
        # Note that .sum() should work on this but it failed when I tried it.
        c = self._frc
        
        count=0
        tot=0.0
        tot2 = 0.0
        totLive = 0.0
        totSim = 0.0
        for i, row in dframe.iterrows():
            count=count+1
            if count < len(dframe)-1 :
                tot=tot+row[c.PL]
                if row[c.bal] == 0 :
                    tot2 = tot2 + row[c.sum]
                    if row[c.acct].startswith('TR') :
                        totSim = totSim + row[c.sum]
                    else :
                        assert(row[c.acct].startswith('U'))
                        totLive = totLive + row[c.sum]
                # if count == len(dframe) -2 :
                #     lastCol = row[c.PL]
       
            elif count == len(dframe) -1 :
                dframe.at[i, c.PL] = tot
                dframe.at[i, c.sum] = totSim
            else :
                assert (count == len(dframe))
                dframe.at[i, c.sum] = totLive
    
    
        return dframe
    
    def getLongOrShort(self, dframe) :
        # dframe contains the transactions of a single trade.  Single trade ends when the balance 
        # of shares is 0
        # Return value is a string 'Long' or 'Short'
        tsx = dframe[dframe.Balance == 0]
    
        
        if len(tsx) != 1 :
            return None
        if str(tsx.Side) == 'B' or str(tsx.Side) == 'Hold-':
            return 'Short'    
        else :
            return 'Long'
   
    def getTradeList (self, dframe) :
        '''
        Creates a python list of DataFrames for each trade. It relies on addTradeIndex successfully creating the 
        trade index in the format Trade 1, Trade 2 etc.
        :param:dframe: A dataframe with the column Tindex filled in.
        '''
        # Now  we are going to add each trade and insert space to put in pictures with circles and 
        #arrows and paragraph on the back of each one to be used as evidence against you in a court 
        # of law (or court of bb opionion)
#         insertsize=25
    #     dframe = nt
        c = self._frc   
        try :
            if not dframe[c.tix].unique()[0].startswith('Trade') :
                raise(NameError("Cannot make a trade list. You must first create the TIndex column using addTradeIndex()."))
        except NameError as ex :
            print(ex, 'Bye!')
            sys.exit(-1)

        ldf = list()
        count = 1
        while True :
            tradeStr = "Trade " + str(count)
            count = count + 1
            tdf = dframe[dframe.Tindex == tradeStr]
            if len(tdf) > 0 :
                ldf.append(tdf)
            else :
                break
#         print("Got {0} trades".format(len(ldf)))
        return ldf
    
    def addFinReqCol (self, dframe) :
        c = self._frc  
        for l in c.columns :
            if l not in dframe.columns :
                dframe[l] = ''
        return dframe