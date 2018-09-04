'''
Created on Sep 2, 2018

@author: Mike Petersen
'''
import pandas as pd


class DataFrameUtil(object):
    '''
    A group of utilities to work with data frames. Methods are class methods and can be used
    without regard to instance.
    '''


    def __init__(self, params):
        '''
        Constructor
        '''

    @classmethod
    def checkRequiredInputFields(cls, dframe, requiredFields) :
        '''
        Checks that dframe has the fields in the array requiredFields. Succeeds silently. Raises a ValueError on failure.
        :param:dframe:          The DataFrame tha is being checked.
        :param:requiredFields:  The fields that are required. 
        '''

        actualFields=dframe.columns
        if set (requiredFields) <= (set (actualFields)) :
            print("got it")
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
        '''Set the required columns in the import file.'''
        self.reqCol={}
        self.reqColKeys = ['time', 'ticker', 'side', 'price', 'shares', 'acct', 'PL']
        self._DASColVal = ['Time', 'Symb', 'Side', 'Price', 'Qty', 'Account', 'P / L']
        self.source=source
        self._setup()
        
    
    def _setup (self):
        if self.source == 'DAS' :
            k=self._DASColVal
        
        self.reqCol = dict(zip(self.reqColKeys, k))
    
    def zeroPadTimeStr(self, dframe) :
        '''
        Guarantee that the time format xx:xx:xx
        Devel note: Currently accounts for only a single time format. 
        '''
        time = self.reqCol['time']
        for i, row in dframe.iterrows():
            tm = row[time]
            tms=tm.split(":")
            if int(len(tms[0]) < 2) :
                if tms[0].startswith("0") == False :
                    tm= "0" + tm
                    dframe.at[i, time] = tm
        return dframe
    
                


    # Todo.  Doctor an input csv file to include fractional numer of shares for testing. 
    #        Make it more modular by checking for 'HOLD'. 
    #        It might be useful in a windowed version with menus to do things seperately.
    #        Currently relying on values of side as 'B' , 'S', 'SS' 
    def mkShortsNegative(self, dframe) :
        ''' Fix the shares sold to be negative values. '''
        
        side = self.reqCol['side']
        shares = self.reqCol['shares']
        
        for i, row in dframe.iterrows():
            if row[side] != 'B' and row[shares] > 0:
                dframe.at[i, shares] = ((dframe.at[i, shares]) * -1)
        return dframe
    
    def getListTickerDF(self, dframe) :
        '''
        Returns a python list of all tickers traded in todays input file.
        :param:dframe: The DataFrame with the days trades that includes the column tickCol (Symb by default and in DAS).
        :param:tickCol: The required column that contains the ticker symbols
        :return: The list of tickers in the days trades represented by the DataFrame 
        '''
    
        tickerCol=self.reqCol['ticker']
        
        ldf_tick = list()
        for ticker in dframe[tickerCol].unique() :
            ldf = dframe[dframe[tickerCol] == ticker]
            ldf_tick.append(ldf)
        return ldf_tick
    
    def getOvernightTrades(self, dframe) :
        ''' 
        Returns a python list (Symb, Qty, 0, 0) of the tickers traded today that have positions from before the market,
        opened, or from after the trades file was exported or both. 
        :param:dframe: The DataFrame with the days trades that includes the columns tickCol and qtyCol 
        (Symb and Qty by default and in DAS).
        :param:tickCol: The required column that contains the ticker symbols
        :param:qtyCol: The required column that contains the quantity of shares in each transaction
        :return: A list of lists with the ticker and quantity of tickers with positions outside todays transactions. 
        '''
        tickCol = self.reqCol['ticker']
        shares = self.reqCol['shares']
        
        ldf_tick = self. getListTickerDF(dframe)
        overnightTrade = list()
        i = 0
        for ticker in ldf_tick :
            if ticker[shares].sum() != 0 :
                overnightTrade.append(dict())
                overnightTrade[i]['ticker'] = ticker[tickCol].unique()[0]
                overnightTrade[i]['shares'] = ticker[shares].sum()
                overnightTrade[i]['before'] = 0
                overnightTrade[i]['after'] = 0
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
        swingTrade = self.getOvernightTrades(dframe)
        for i in range(len(swingTrade)) :
            tryAgain =  True
            while tryAgain == True :
    
                print(swingTrade[i])
                print ("There is an unbalanced amount of shares of {0} in the amount of {1}".format(
                    swingTrade[i]['ticker'], swingTrade[i]['shares']))
    
                question = "How many shares of {0} are you holding now? (Enter for {1})".format(swingTrade[i]['ticker'], swingTrade[i]['shares'])
                swingTrade[i]['after'] = self.askUser(swingTrade[i], question)
                swingTrade[i]['shares'] = swingTrade[i]['shares'] - swingTrade[i]['after']
    
                if swingTrade[i]['shares'] != 0 :
    
                    statement = "There is now a prior unbalanced amount of shares of {0} in the amount of {1}"
                    print(statement.format(swingTrade[i]['ticker'], swingTrade[i]['shares']))
                    question = "How many shares of {0} were you holding before? (Enter for {1}".format(swingTrade[i]['ticker'], swingTrade[i]['shares'])
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
        newdf = DataFrameUtil.createDf(dframe, 0)
        
        for ldf in self.getListTickerDF(dframe) :
            for i in range(len(swTrade)) :
                if swTrade[i]['ticker'] == ldf.Symb.unique()[0] :
                    print ("Got {0} with the balance {1}, before {2} and after {3}". format (swTrade[i]['ticker'], 
                                                                                             swTrade[i]['shares'],
                                                                                             swTrade[i]['before'],
                                                                                             swTrade[i]['after']))
                    
                    #insert a non transaction HOLD row before transactions of the same ticker
                    if swTrade[i]['before'] != 0 :
                        newldf = DataFrameUtil.createDf(dframe, 1)
                        print("length:   ", len(newldf))
                        for j, row in newldf.iterrows():
    
                            if j == len(newldf) -1 :
                                print("Though this seems unnecessary it will make it more uniform ")
                                newldf.at[j, self.reqCol['time']] = '00:00:01'
                                newldf.at[j, self.reqCol['ticker']] = swTrade[i]['ticker']
                                if swTrade[i]['before'] > 0 :
                                    newldf.at[j, self.reqCol['side']] = "HOLD+"
                                else :
                                    newldf.at[j, self.reqCol['side']] = "HOLD-"
                                newldf.at[j, self.reqCol['price']] = 0
                                newldf.at[j, self.reqCol['shares']] = swTrade[i]['before']
                                newldf.at[j, self.reqCol['acct']] = 'ZeroSubstance'
                                newldf.at[j, self.reqCol['PL']] = 0
                                
                                ldf = newldf.append(ldf, ignore_index = True)
                            break #This should be unnecessary as newldf should always be the length of 1 here
                        
                    # Insert a non-transaction HOLD row after transactions from the same ticker    
                    if swTrade[i]['after'] != 0 :
                        print("Are we good?")
                        ldf = DataFrameUtil.addRows(ldf, 1)
            
                        for j, row in ldf.iterrows():
    
                            if j == len(ldf) -1 :
                                ldf.at[j, self.reqCol['time']] = '23:59:59'
                                ldf.at[j, self.reqCol['ticker']] = swTrade[i]['ticker']

                                if swTrade[i]['after']> 0 :
                                    ldf.at[j, self.reqCol['side']] = "HOLD+"
                                else :
                                    ldf.at[j, self.reqCol['side']] = "HOLD-"
                                ldf.at[j, self.reqCol['price']] = 0
                                ldf.at[j, self.reqCol['shares']] = swTrade[i]['after']
                                ldf.at[j, self.reqCol['acct']] = 'ZeroSubstance'
                                ldf.at[j, self.reqCol['PL']] = 0
            
            newdf = newdf.append(ldf, ignore_index = True, sort = False)
        return newdf
    
        
    
print('hello dataframe')