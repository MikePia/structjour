'''
Created on Sep 2, 2018C

@author: Mike Petersen
'''
import sys
import pandas as pd

from structjour.tradeutil import ReqCol 

class DataFrameUtil(object):
    '''
    A group of utilities to work with data frames. Methods are class methods and can be used
    without regard to instance.
    '''


    def __init__(self, params):
        '''
        Constructor which may never be used. (but it could be)
        '''

    @classmethod
    def checkRequiredInputFields(cls, dframe, requiredFields) :
        '''
        Checks that dframe has the fields in the array requiredFields. Also checks that there are no duplicate fields
        Returns True on success. Raises a ValueError on failure.
        :param:dframe:          The DataFrame that is being checked.
        :param:requiredFields:  The fields that are required. 
        '''
        actualFields=dframe.columns
        if len(actualFields) != len(set(actualFields)) :
            err = 'Your DataFrame has duplicate columns'
            raise(ValueError(err))
        if set (requiredFields) <= (set (actualFields)) :
            return True
        else :
            err='Your DataFrame is missing some required fields:\n'
            err += str((set(requiredFields) - set(actualFields)))
            raise ValueError(err)
    
    
    #TODO Change this to create the DataFrame from an array of fields
    @classmethod
    def createDf(cls, dframe, numRow) :
        ''' 
        Creates a new DataFrame with  the length numRow. Each cell is filled with empty string 
        
        :param:dframe:            (Will be) ... An array of the labels to create columns.
        :param:requiredFields:    The number of empty rows to create. 
        :return:                   The new DataFrame objet
        '''
    
        ll=list()
        r=list()
        for i in range(len(dframe.columns)) :
            r.append('')
            
        for i in range(numRow) :
            ll.append(r)
        newdf= pd.DataFrame(ll, columns=dframe.columns)
    
        return newdf
    
    @classmethod
    def addRows(cls, dframe, numRow) :
        ''' 
        Adds numRow rows the the DataFrame object dframe'
        
        :param:dframe:            The DataFrame to increase in size 
        :param:requiredFields:    The number of empty rows to create. 
        :return:                   The new DataFrame objet
        '''
        
        newdf= cls.createDf(dframe, numRow)
        dframe = dframe.append(newdf, ignore_index=True, sort=False)
        
        return dframe

class InputDataFrame(object):
    '''Manipulation of the original import of the trade transactions. Abstract the label schema
    to a dictionary. Import from all soures is equalized here.'''
    def __init__(self, source="DAS"):
#         '''Set the required columns in the import file.'''
        if source != 'DAS' :
            print("Only DAS is currently supported")
            raise(ValueError)
#         self.reqCol={}
#         self.reqColKeys = ['time', 'ticker', 'side', 'price', 'shares', 'acct', 'PL']
#         self._DASColVal = ['Time', 'Symb', 'Side', 'Price', 'Qty', 'Account', 'P / L']
#         self.source=source
#         self._setup()

    def _checkUniqueSIMTX(self, dframe):
        '''Check the SIM transactions for uniqueness within (ticker, time, account). I believe these are always necessariy unique.
        I need to know if they are not.  If found,the program should fail or alert the user and work around
        '''
        rc = ReqCol()
        

        df =dframe[dframe['Cloid'] == "AUTO" ]
        tickerlist = list()
        for i, row in df.iterrows():
            tickerlist.append( (row[rc.time], row[rc.ticker], row[rc.acct]) )
    
            tickerset = set(tickerlist)
            try :
                assert(len(tickerset) == len (tickerlist) )
            except ValueError as ex :
                err = "Found a Sim ticket that is not unique. Alert the media.... (Now)"
                print("{0}{1}".format(err, ex))
                sys.exit(-1)

    def getListOfTicketDF(self, dframe):
        ''' 
        Take the standard trades.csv DataFrame and return transactsion for each ticket as a python list 
        of DataFrames. This is made more interesting by the SIM transactions which have no ticket ID (Cloid). 
        They are identified in DAS by 'AUTO.' We will give them one. Presumably one ticket per SIM transaction, 
        but check for uniqueness and fail it if it is ever not true.
        
        NOTE: This SIM ticket will most definitely
        not be found unique between different days
        if/when that is an issue, fixit.
        '''
        self._checkUniqueSIMTX(dframe)
        
        SIMdf =dframe[dframe['Cloid'] == "AUTO" ]
        for i, row in SIMdf.iterrows():
            tickName = "SIMTick_{0}".format(i)
            print(tickName)
            SIMdf.at[i, "Cloid"] = tickName
            
                
            
        listOfTickets = list()
        for ticketID in dframe.Cloid.unique():
            if ticketID == "AUTO" :
                continue
            t = dframe[dframe['Cloid'] == ticketID ]
            listOfTickets.append(t)
        
        
            
        #Add the altered sim tickets to the ptyhon list, One list element per ticket (in SIM -- each row wil be a DF)
        for simTkt in SIMdf.Cloid.unique():
            print(simTkt)
            t = SIMdf[SIMdf['Cloid'] == simTkt]
            listOfTickets.append(t)            
            
        
        return listOfTickets
        
    def zeroPadTimeStr(self, dframe) :
        '''
        Guarantee that the time format xx:xx:xx
        Devel note: Currently accounts for only a single time format. 
        '''
        
        rc = ReqCol()
#         time = rc.time
        for i, row in dframe.iterrows():
            tm = row[rc.time]
            tms=tm.split(":")
            if int(len(tms[0]) < 2) :
                if tms[0].startswith("0") == False :
                    tm= "0" + tm
                    dframe.at[i, rc.time] = tm
        return dframe
    
    # Todo.  Doctor an input csv file to include fractional numer of shares for testing. 
    #        Make it more modular by checking for 'HOLD'. 
    #        It might be useful in a windowed version with menus to do things seperately.
    #        Currently relying on values of side as 'B' , 'S', 'SS' 
    def mkShortsNegative(self, dframe) :
        ''' Fix the shares sold to be negative values. '''
        
        rc = ReqCol()
        
        for i, row in dframe.iterrows():
            if row[rc.side] != 'B' and row[rc.shares] > 0:
                dframe.at[i, rc.shares] = ((dframe.at[i, rc.shares]) * -1)
        return dframe
    
    def getListTickerDF(self, dframe) :
        '''
        Returns a python list of all tickers/account traded in todays input file.
        :param:dframe: The DataFrame with the days trades that includes the column tickCol (Symb by default and in DAS).
        :param:tickCol: The required column that contains the ticker symbols
        :return: The list of tickers in the days trades represented by the DataFrame 
        '''
        rc = ReqCol()
        
        listOfTickers = list()
        for symb in dframe[rc.ticker].unique() :
            for acct in dframe[rc.acct][dframe[rc.ticker]==symb].unique()  :
                ldf = dframe[dframe[rc.ticker]==symb][dframe[rc.acct]==acct]
                listOfTickers.append(ldf)
#         
#         ldf_tick = list()
#         for ticker in dframe[rc.ticker].unique() :
#             ldf = dframe[dframe[rc.ticker] == ticker]
#             ldf_tick.append(ldf)
        return listOfTickers
    
    def getOvernightTrades(self, dframe) :
        ''' 
        :dep:getListTickerDF: Requires transactions from a single ticker in a single account.  
        :dep:mkShortsNegative: Qunatity of shares need to be positive for a buy and negative for a sell or short. 
        We will not know whether the overnight trade is before or after or both. 
        :param:dframe: The DataFrame with the days trades that includes the columns rc.ticker and rc.shares 
        :return:overnightTrades: The structure is a list of dict. The dict has the keys (ticker, shares, before, after, acct). 
                                Elsewhere in the program the variable is referred to as swingTrade or swtrade.
            :ticker:                     The stock ticker
            :shares: :before: :after:    The accounting of overnight shares. At the end of this method, all shares
                                         are in shares. Don't have the info for before or after.
            :acct:                       The account for this transaction
        '''
        rc = ReqCol()
        
        ldf_tick = self.getListTickerDF(dframe)
        overnightTrade = list()
        i = 0
        for ticker in ldf_tick :
            if ticker[rc.shares].sum() != 0 :
                overnightTrade.append(dict())
                overnightTrade[i]['ticker'] = ticker[rc.ticker].unique()[0]
                overnightTrade[i]['shares'] = ticker[rc.shares].sum()
                overnightTrade[i]['before'] = 0
                overnightTrade[i]['after'] = 0
                overnightTrade[i]['acct'] = ticker[rc.acct].unique()[0]
                i = i + 1
        return overnightTrade
    
    
    # Note that this does not yet include those shares that are held before the days trading 
    # began. Redo this to remake the list of data frames from the Symbols of Swing List then 
    # make a list of data frams that  excludes those then merge them together
    
    def askUser(self, swTradeItem, question) :
        while True :
            try :
                response = input(question)
                if len(response) < 1 :
                    response = swTradeItem['shares']
                else :
                    response = int(response)
            except Exception as ex:
                print(ex)
                print("please enter a number")
                response = 0
                continue
           
            return response
    
    def figureOvernightTransactions(self, dframe) :
        
        rc = ReqCol()

        swingTrade = self.getOvernightTrades(dframe)
        for i in range(len(swingTrade)) :
            tryAgain =  True
            while tryAgain == True :
    
                print(swingTrade[i])
                question= '''There is an unbalanced amount of shares of {0} in the amount of {1} 
                    in the account {2}. How many shares of {0} are you holding now? 
                    (Enter for {1}) '''.format(swingTrade[i]['ticker'], swingTrade[i]['shares'], swingTrade[i]['acct'])
    
#                 question = " How many shares of {0} are you holding now? (Enter for {1})".format ( swingTrade[i]['ticker'], swingTrade[i]['shares'] )
                swingTrade[i]['after'] = self.askUser(swingTrade[i], question)
                swingTrade[i]['shares'] = swingTrade[i]['shares'] - swingTrade[i]['after']
    
                if swingTrade[i]['shares'] != 0 :
    
                    question = '''There is now a prior unbalanced amount of shares of {0} amount 
                    of {1} in the account {2}. How many shares of {0} were you holding before? 
                    (Enter for {1}) '''.format(swingTrade[i]['ticker'], -swingTrade[i]['shares'], swingTrade[i]['acct'])
                    
#                     question = "How many shares of {0} were you holding before? (Enter for {1}".format(swingTrade[i]['ticker'], swingTrade[i]['shares'])
                    swingTrade[i]['before'] = self.askUser(swingTrade[i], question)
                    swingTrade[i]['shares'] = swingTrade[i]['shares'] - swingTrade[i]['before']
    
                if swingTrade[i]['shares']== 0 :
                    print("That works.")
                    tryAgain = False
                else :
                    print()
                    print("There are {1} unaccounted for shares in {0}".format(swingTrade[i]['ticker'], swingTrade[i]['shares']))
                    print()
                    print("That does not add up. Starting over ...")
                    print()
                    print ("Prior to reset version ", i, swingTrade)
                    swingTrade[i] = self.getOvernightTrades(dframe)[i]
                    print ("reset version ", i, swingTrade)
        return swingTrade
    
    def insertOvernightRow(self, dframe, swTrade) :
        
        rc = ReqCol()
        
        newdf = DataFrameUtil.createDf(dframe, 0)
        
        
        for ldf in self.getListTickerDF(dframe) :
#             print(ldf[rc.ticker].unique()[0], ldf[rc.acct].unique()[0])
            for trade in swTrade :
                if trade['ticker'] == ldf[rc.ticker].unique()[0] and trade['acct'] == ldf[rc.acct].unique()[0]:
                    print ("Got {0} with the balance {1}, before {2} and after {3} in {4}". format (trade['ticker'], 
                                                                                             trade['shares'],
                                                                                             trade['before'],
                                                                                             trade['after'],
                                                                                             trade['acct']))
                    
                    #insert a non transaction HOLD row before transactions of the same ticker
                    if trade['before'] != 0 :
                        newldf = DataFrameUtil.createDf(dframe, 1)
                        print("length:   ", len(newldf))
                        for j, row in newldf.iterrows():
    
                            if j == len(newldf) -1 :
                                print("Though this seems unnecessary it will make it more uniform ")
                                newldf.at[j, rc.time] = '00:00:01'
                                newldf.at[j, rc.ticker] = trade['ticker']
                                if trade['before'] > 0 :
                                    newldf.at[j, rc.side] = "HOLD+"
                                else :
                                    newldf.at[j, rc.side] = "HOLD-"
                                newldf.at[j, rc.price] = 0
                                newldf.at[j, rc.shares] = trade['before']
                                newldf.at[j, rc.acct] = trade['acct']    #ZeroSubstance'
                                newldf.at[j, rc.PL] = 0
                                
                                ldf = newldf.append(ldf, ignore_index = True)
                            break #This should be unnecessary as newldf should always be the length of 1 here
                        
                    # Insert a non-transaction HOLD row after transactions from the same ticker    
                    if trade['after'] != 0 :
                        print("Are we good?")
                        ldf = DataFrameUtil.addRows(ldf, 1)
            
                        for j, row in ldf.iterrows():
    
                            if j == len(ldf) -1 :
                                ldf.at[j, rc.time] = '23:59:59'
                                ldf.at[j, rc.ticker] = trade['ticker']

                                if trade['after']> 0 :
                                    ldf.at[j, rc.side] = "HOLD+"
                                else :
                                    ldf.at[j, rc.side] = "HOLD-"
                                ldf.at[j, rc.price] = 0
                                ldf.at[j, rc.shares] = trade['after']
                                ldf.at[j, rc.acct] = trade['acct']   #'ZeroSubstance'
                                ldf.at[j, rc.PL] = 0
            
            newdf = newdf.append(ldf, ignore_index = True, sort = False)
        return newdf
    
print('hello dataframe')