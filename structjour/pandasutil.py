'''
Created on Sep 2, 2018C

@author: Mike Petersen
'''
import sys, os
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

    def zeroPadTimeStr(self, dframe) :
        '''
        Guarantee that the time format xx:xx:xx
        Devel note: Currently accounts for only a single time format. Note that it is only a problem if the column formatted
        in the df as string. Date formats use numbers. And the only time I have encountered it as a string is when I have opened it in Excel and saved it.
        @test
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
        ''' Fix the shares sold to be negative values. 
        @testpu'''
        
        rc = ReqCol()
        
        for i, row in dframe.iterrows():
            if row[rc.side] != 'B' and row[rc.shares] > 0:
                dframe.at[i, rc.shares] = ((dframe.at[i, rc.shares]) * -1)
        return dframe
    
    def getListTickerDF(self, dframe) :
        '''
        Returns a python list of all tickers/account traded in todays input file.
        :param:dframe: The DataFrame with the days trades that includes the column tickCol (Symb by default and in DAS).
        :return: The list of tickers in the days trades represented by the DataFrame 
        '''
        rc = ReqCol()
        
        listOfTickers = list()
        for symb in dframe[rc.ticker].unique() :
            for acct in dframe[rc.acct][dframe[rc.ticker]==symb].unique()  :

#                 ldf = dframe[dframe[rc.ticker]==symb][dframe[rc.acct]==acct]
                ldf = dframe[dframe[rc.ticker]==symb]
                ldf = ldf[ldf[rc.acct]==acct]

                listOfTickers.append(ldf)
#         
#        This code is too interdependent. gtoOvernightTrade, figureOvernightTrades, askUser
#         and insertOvernightRow combined with the data
        return listOfTickers
    
    def getOvernightTrades(self, dframe) :
        ''' 
        Create the overnightTrade (aka swingTrade data structure) from the list of overnight holds. Overnight holds are inferred
            from an unbalanced number of shares. Until we ask the user, we won't know whether before or after or both. 
        :param:dframe: The Original unaltered input file with the days trades that includes the columns rc.ticker and rc.shares 
        :return:overnightTrades: The structure is a list of dict. The dict has the keys (ticker, shares, before, after, acct). 
                                        Elsewhere in the program the variable is referred to as swingTrade or swtrade.
            :ticker:                     The stock ticker
            :shares: :before: :after:    The accounting of overnight shares. At the end of this method, all shares
                                         are in shares. Don't have the info for before or after.
            :acct:                       The account for this transaction
        @testpu
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
    
    
    
    def askUser(self, shares, question) :
        '''
        Ask the user a question regarding how many shares they are holding.
        :params:shares: The number of shares outof balance. Its inserted into the question and
                        used as a default response.
        :return: The number response for the number of shares.
        '''
        while True :
            try :
                response = input(question)
                if len(response) < 1 :
                    response = shares
                else :
                    response = int(response)
            except Exception as ex:
                print(ex)
                print()
                print("please enter a number")
                response = 0
                continue
           
            return response
    
    def figureOvernightTransactions(self, dframe) :
        '''
        Determine how of the unbalanced shares were held before and after the days trade (as in the file).
        Get the raw data from getOvernightTrade then ask the user number of shares before and after.
        '''
        
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
                swingTrade[i]['after'] = self.askUser(swingTrade[i]['shares'], question)
                swingTrade[i]['shares'] = swingTrade[i]['shares'] - swingTrade[i]['after']
    
                if swingTrade[i]['shares'] != 0 :
    
                    question = '''There is now a prior unbalanced amount of shares of {0} amount 
                    of {1} in the account {2}. How many shares of {0} were you holding before? 
                    (Enter for {1}) '''.format(swingTrade[i]['ticker'], -swingTrade[i]['shares'], swingTrade[i]['acct'])
                    
#                     question = "How many shares of {0} were you holding before? (Enter for {1}".format(swingTrade[i]['ticker'], swingTrade[i]['shares'])
                    swingTrade[i]['before'] = self.askUser(swingTrade[i]['shares'], question)
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
                                    newldf.at[j, rc.side] = "HOLD-"
                                else :
                                    newldf.at[j, rc.side] = "HOLD+"
                                newldf.at[j, rc.price] = float(0.0)
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
                                ldf.at[j, rc.price] = float(0.0)
                                ldf.at[j, rc.shares] = trade['after']
                                ldf.at[j, rc.acct] = trade['acct']   #'ZeroSubstance'
                                ldf.at[j, rc.PL] = 0
            
            newdf = newdf.append(ldf, ignore_index = True, sort = False)
        return newdf
    
    
class ToCSV_Ticket(object):
    '''
    Take an input CSV file of all trade transactions and reduce the transactions to tickets. Use the 
    JournalFiles class as the single point of contact with  input and output.  When the new file is 
    created, alter the Journalfiles indir/infile to the new file
    :params:jf: The JournalFile Object. It has the input files we need.
    '''
    
    
    def __init__(self, jf) :
        self.jf = jf
        self.df = pd.read_csv(self.jf.inpathfile)
        rc = ReqCol()
        DataFrameUtil.checkRequiredInputFields(self.df, rc.columns)


    def _checkUniqueSIMTX(self):
        '''
        Check the SIM transactions for uniqueness within (ticker, time, account). I believe these are always 
        necessarily unique. I need to know if they are not.  If found,the program should fail or alert the 
        user and work around
        '''
        pass
        rc = ReqCol()
        dframe = self.df
         
        #HACK ALERT
        #This is guaranteed to cause some future problem
        # If Cloid has some Sim ids ('AUTO') the column must have some str elements. Without this
        # it throws a TypeError and a Future Warning about changing code. For DataFrame columns 
        # without any sim trades there are only floats. This is not guaranteed behavior, just obaserved
        # from my runs. And there there is some weirdness between numpy types and python regarding 
        # what type to return for this comparison--and it may change in the future.
#         if len(dframe.Cloid.apply(lambda x: isinstance(x, str))) < 1 :
        
        doSomething = False
        for t in dframe['Cloid'] :
            if isinstance(t, str) :
                doSomething = True
                break
        if not doSomething :
            return



        df =dframe[dframe['Cloid'] == "AUTO" ]
    
        tickerlist = list()
        for i, row in df.iterrows():
            tickerlist.append( (row[rc.time], row[rc.ticker], row[rc.acct]) )
     
            tickerset = set(tickerlist)
            try :
                assert(len(tickerset) == len (tickerlist) )
            except ValueError as ex :
                err = "Found a Sim ticket that is not unique. This should not be possible. Please send the csv file to the deveoper"
                print("{0}{1}".format(err, ex))
                sys.exit(-1)
    
    def createSingleTicket(self, tickTx):
        '''
        Create a single row ticket from a Dataframe with a list of Transactions.
        :prerequisites: tickTx needs to have 'unique() == 1' for side, symb, account, and cloid. That uniqueness is tested in 
                        getListOfTicketDF() so use that to create a list of ticktTX  
        :param:tickTx: A DataFrame with transactions from a single ticket
        :return: A single row data frame with total shares and average price.
        '''
        
        rc=ReqCol()
    
        total =0
        totalPL = 0
        for i, row in tickTx.iterrows():
            total = total + (row[rc.price] * row[rc.shares])
            totalPL = totalPL + row[rc.PL]
    
        totalShares = tickTx[rc.shares].sum()
        avgPrice = total /  totalShares
        
        newDf = DataFrameUtil.createDf(tickTx, 0)
    
        oneRow = tickTx.sort_values([rc.time, rc.price]).head(1)
        newDf = newDf.append(oneRow)
        newDf.copy()
    
        newDf[rc.price]=avgPrice
        newDf[rc.shares]=totalShares
        newDf[rc.PL] = totalPL
        return newDf        
        
    def getListOfTicketDF(self):
        ''' 
        Take the standard trades.csv DataFrame and return transactsion for each ticket as a python list 
        of DataFrames. This is made more interesting by the SIM transactions which have no ticket ID (Cloid). 
        They are identified in DAS by 'AUTO.' We will give them an ID unique for this run. There is only, 
        presumably one ticket per SIM transaction, but check for uniqueness and fail it if it is ever not true
        :return: The penultimate step, returns a list of DataFrames, 1 row per ticket.
        
        HACK ALERT: This got real ugly when I sent in a trades.csv without any sim trades.  The import alters
        the type. Without no Sim included, they are all floats. With at least one Sim transaction, they are 
        str. But that is not guaranteed.
        
        
        NOTE: This SIM ticket will most definitely
        not be found unique between different days
        if/when that is an issue, fixit.
        '''
        
        dframe = self.df
        self._checkUniqueSIMTX()
        
        doSomething = False
        for t in dframe['Cloid'] :
            if isinstance(t, str) :
                doSomething = True
                break
        
        
        #Get the SIM transactions from the origainal DataFtame. Change the Cloid from Auto to SIMTick__XX
        if doSomething:
            SIMdf =dframe[dframe['Cloid'] == "AUTO" ]
            for i, row in SIMdf.iterrows():
                tickName = "SIMTick_{0}".format(i)
                SIMdf.at[i, "Cloid"] = tickName
        
        #For each unique ticket ID (akaCloid), create a DataFrame and add it to a list of DataFrames    
        listOfTickets = list()
        for ticketID in dframe.Cloid.unique():
            if ticketID == "AUTO" :
                continue
            t = dframe[dframe['Cloid'] == ticketID ]
            listOfTickets.append(t)
        print("before last loop {0}".format(len(listOfTickets)))
        # Combine the two above into a python list of DataFrames
        
        if doSomething :
            for simTkt in SIMdf.Cloid.unique():
                t = SIMdf[SIMdf['Cloid'] == simTkt]
                listOfTickets.append(t)            
        print("after last loop {0}".format(len(listOfTickets)))
            
        return listOfTickets
    
    def newDFSingleTxPerTicket(self, listDf=None):
        '''
        Create an alternate csv file using the single tx per ticket DataFrames we created.
        :param:listDf: Normally leave blank. If used, listDf should be the return value from getListOfTicketDF.
        :param:jf: A JournalFiles object as this new CSV file needs to be written into the outdir.
        :return: The DataFrame created version of the data.
        :sideeffects: Saves a csv file of all transactions as single ticket transactions to jf.inpathfile
        '''
        rc = ReqCol()
        if not listDf :
            listDf = self.getListOfTicketDF()

        DataFrameUtil.checkRequiredInputFields(listDf[0], rc.columns)
        
        newDF = DataFrameUtil.createDf(listDf[0], 0)
        
        
        for tick in listDf :
            t = self.createSingleTicket(tick)
            newDF = newDF.append(t)
            
        outfile="tradesByTicket.csv"
        opf = os.path.join(self.jf.indir, outfile)
        newDF.to_csv(opf)
        self.jf.resetInfile(outfile)
        
        return newDF, self.jf
    
# print('hello dataframe')