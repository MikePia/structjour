import pandas as pd

from journal.dfutil import DataFrameUtil 
from journal.tradeutil import  FinReqCol
# from withstyle.tradestyle import srf
# from tornado.test.web_test import ErrorHandlerXSRFTest


# Use to access columns in the (altered) input dataframe, known on this page as df. Use srf (SumReqFields instance) to access
# columns/data for the summary trade dataframe, known on this page as TheTrade.
frc = FinReqCol()

class   SumReqFields(object):
    '''
    Manage the required columns, cell location and namedStyle for the summary aka TheTradeObject and TheTradeStyle. 
    These columns are used in a DataFrame (aka TheTrade) that summarizes each single trade with a single row. This 
    summary information includes information from the user, target, stop, strategy, notes etc.
    '''

    def __init__(self):
        
        ''' rcvals are the actual column titles 
        rckeys are the abstracted names for use with all file types
        The abstraction provides code style consistency for this program (like ReqCol and FinReqCol)
            and a means to change the whole thing managed here alone'''
        # TODO (maybe) make these things pluggable to alow the creation of any shape and style by plugging in a module. Might possibe by
        #   plugging in tfcoumns and tfformulas alone, and leaving the rest
        rcvals = ['Name', 'Account', 'Strategy', 'Link1',
                  'P/LHead', 'P / L', 'StartHead', 'Start','DurHead', 'Duration', 'ShareHead', 'Shares', 'MktHead', 'MktVal',
                  'TargHead', 'Target', 'TargDiff', 'StopHead', 'StopLoss', 'SLDiff',  'RRHead', 'RR', 'MaxHead', 'MaxLoss', 
                  'MstkHead', 'MstkVal', 'MstkNote', 
                  
                  'EntryHead', 'Entry1', 'Entry2', 'Entry3', 'Entry4', 'Entry5', 'Entry6', 'Entry7', 'Entry8', 
                  'Exit1', 'Exit2', 'Exit3', 'Exit4', 'Exit5', 'Exit6', 'Exit7', 'Exit8',
                  'Time1', 'Time2', 'Time3', 'Time4', 'Time5', 'Time6', 'Time7', 'Time8',
                  'EShare1', 'EShare2', 'EShare3', 'EShare4', 'EShare5',  'EShare6', 'EShare7', 'EShare8', 
                  'Diff1', 'Diff2', 'Diff3', 'Diff4', 'Diff5', 'Diff6', 'Diff7', 'Diff8', 
                  'PL1', 'PL2', 'PL3', 'PL4', 'PL5', 'PL6', 'PL7', 'PL8',                    
                  'Explain', 'Notes'
                  ]
#         rcvals2 =[  'StratNote', 'Link5', 'Link6', ]
        
        rckeys = ['name', 'acct', 'strat', 'link1',
                  'plhead', 'pl', 'starthead', 'start','durhead', 'dur', 'sharehead', 'shares', 'mkthead', 'mktval',
                 'targhead', 'targ', 'targdiff', 'stophead', 'stoploss', 'sldiff',  'rrhead', 'rr', 'maxhead', 'maxloss', 
                 'mstkhead', 'mstkval', 'mstknote',
                  
                 'entryhead', 'entry1', 'entry2', 'entry3', 'entry4', 'entry5', 'entry6', 'entry7', 'entry8', 
                 'exit1', 'exit2', 'exit3', 'exit4', 'exit5', 'exit6', 'exit7', 'exit8',  
                 'time1', 'time2', 'time3', 'time4', 'time5',  'time6', 'time7', 'time8', 
                 'eshare1', 'eshare2', 'eshare3', 'eshare4', 'eshare5', 'eshare6', 'eshare7', 'eshare8', 
                 'diff1', 'diff2',  'diff3',  'diff4', 'diff5',  'diff6',  'diff7',  'diff8',
                  'pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'pl6', 'pl7', 'pl8', 
                  'explain', 'notes'
                  ]
#         rckeys2 = ['stratnote', 'link5', 'link6']
        
        
        # This includes all the locations that are likely to have data associated with them.  Blank cells are added to tfcolumns  Each of these are added as 
        # attributes Unnecessarily as but it should reduce errors to use attributes instead of strings
        rc = dict(zip(rckeys, rcvals))
        
        
         
        # #Suggested way to address the columns for the TheTrade DataFrame. 
        self.name     = rc['name']                    
        self.acct     = rc['acct']                 
        self.strat    = rc['strat']     
        self.link1    = rc['link1']     
        
        self.plhead   = rc['plhead']    
        self.pl       = rc['pl']                   
        self.starthead= rc['starthead'] 
        self.start    = rc['start']           
        self.durhead  = rc['durhead']
        self.dur      = rc['dur'] 
        self.sharehead= rc['sharehead']
        self.shares   = rc['shares'] 
        self.mkthead  = rc['mkthead']
        self.mktval   = rc['mktval'] 
        
        self.targhead = rc['targhead']  
        self.targ     = rc['targ']      
        self.targdiff = rc['targdiff']  
        self.stophead = rc['stophead']  
        self.stoploss = rc['stoploss']  
        self.sldiff   = rc['sldiff']    
        self.rrhead   = rc['rrhead']    
        self.rr       = rc['rr']        
        self.maxhead  = rc['maxhead']   
        self.maxloss  = rc['maxloss']   
        
        
        
        self.mstkhead = rc['mstkhead']
        self.mstkval  = rc['mstkval']
        self.mstknote = rc['mstknote']
        self.entryhead= rc['entryhead']
        self.entry1   = rc['entry1']   
        self.entry2   = rc['entry2']   
        self.entry3   = rc['entry3']   
        self.entry4   = rc['entry4']   
        self.entry5   = rc['entry5']   
        self.entry6   = rc['entry6']
        self.entry7   = rc['entry7']
        self.entry8   = rc['entry8']   
        
        self.exit1    = rc['exit1']    
        self.exit2    = rc['exit2']    
        self.exit3    = rc['exit3']    
        self.exit4    = rc['exit4']    
        self.exit5    = rc['exit5']    
        self.exit6    = rc['exit6']    
        self.exit7    = rc['exit7']    
        self.exit8    = rc['exit8']    
        
        self.time1 =  rc['time1']             
        self.time2 =  rc['time2']
        self.time3 =  rc['time3']
        self.time4 =  rc['time4']
        self.time5 =  rc['time5']
        self.time6 =  rc['time6']
        self.time7 =  rc['time7']
        self.time8 =  rc['time8']    
        
        self.eshare1= rc['eshare1']  
        self.eshare2= rc['eshare2'] 
        self.eshare3= rc['eshare3'] 
        self.eshare4= rc['eshare4'] 
        self.eshare5= rc['eshare5'] 
        self.eshare6= rc['eshare6'] 
        self.eshare7= rc['eshare7'] 
        self.eshare8= rc['eshare8'] 
        
        self.diff1  = rc['diff1']
        self.diff2  = rc['diff2']
        self.diff3  = rc['diff3']
        self.diff4  = rc['diff4']
        self.diff5  = rc['diff5']
        self.diff6  = rc['diff6']
        self.diff7  = rc['diff7']
        self.diff8  = rc['diff8']
        
        self.pl1  = rc['pl1']
        self.pl2  = rc['pl2']
        self.pl3  = rc['pl3']
        self.pl4  = rc['pl4']
        self.pl5  = rc['pl5']
        self.pl6  = rc['pl6']
        self.pl7  = rc['pl7']
        self.pl8  = rc['pl8']
        
        self.explain  = rc['explain']  
        self.notes    = rc['notes']    
         
        self.rc = rc
        self.columns = rc.values()
         
         
        # To add a style to the TradeSummary, define the NamedStyle in withstyle.tradestyle.TradeFormat. Follow the pattern of the
        # others. Then place the name here with its cell location (anchor at (1,1)) and its associated data column in TheTrade DataFrame
#         ex1="ex1"
        self.tfcolumns = { 
            self.name     : [[(1, 1), (3, 2)], 'titleStyle'],
            self.acct     : [[(4, 1), (6, 2)], 'titleStyle'],
            self.strat    : [[(7, 1), (9, 2)], 'titleStyle'],         
            self.link1    : [[(10, 1),(12,2)], 'linkStyle'],
            
            self.plhead   : [[(1, 3), (1, 4)], 'titleLeft'],      
            self.pl       : [[(2, 3), (3, 4)], 'titleNumberRight'],
            self.starthead: [[(1, 5), (1, 6)], 'titleLeft'],     
            self.start    : [[(2, 5), (3, 6)], 'titleRight'],
            self.durhead  : [[(1, 7), (1, 8)], 'titleLeft'],      
            self.dur      : [[(2, 7), (3, 8)], 'titleRight'],
            self.sharehead: [[(1, 9), (1, 10)], 'titleLeft'],     
            self.shares   : [[(2, 9), (3, 10)], 'titleRight'],        
            self.mkthead  : [[(1, 11), (1, 12)], 'titleLeft'],     
            self.mktval   : [[(2, 11), (3, 12)], 'titleNumberRight'], 
            
            self.targhead : [(1,13), 'normStyle'],
            self.targ     : [(2,13), 'normalNumber'],
            self.targdiff : [(3,13), 'normStyle'],
            self.stophead : [(1,14), 'normStyle'],      
            self.stoploss : [(2,14), 'normStyle'],
            self.sldiff   : [(3,14), 'normStyle'],
            self.rrhead   : [(1,15), 'normStyle'],
            self.rr       : [(2,15), 'normalFraction'],
            "ex1"           : [(3,15), 'normStyle'],
            self.maxhead  : [(1,16), 'normStyle'],
            self.maxloss  : [(2,16), 'normStyle'],
            "ex2"         : [(3,16), 'normStyle'],
            
            self.mstkhead : [[(1, 17), (1,18)], 'normStyle'],
            self.mstkval  : [[(2, 17), (3, 18)], 'titleNumberRight' ],
            self.mstknote : [[(1, 19), (3, 20)], 'finalNoteStyle'], 
            self.entryhead: [[(4, 3), (4, 8)], 'normStyle'],
            
            self.entry1   : [(5,3), 'normalNumberTopLeft'],
            self.entry2   : [(6,3), 'normalNumberTop'],
            self.entry3   : [(7,3), 'normalNumberTop'],
            self.entry4   : [(8,3), 'normalNumberTop'],
            self.entry5   : [(9,3), 'normalNumberTop'],
            self.entry6   : [(10,3), 'normalNumberTop'],
            self.entry7   : [(11,3), 'normalNumberTop'],
            self.entry8   : [(12,3), 'normalNumberTopRight'],
            
            self.exit1    : [(5, 4),  'normalNumberLeft'],    
            self.exit2    : [(6, 4),  'normalNumberInside'],             
            self.exit3    : [(7, 4),  'normalNumberInside'],             
            self.exit4    : [(8, 4),  'normalNumberInside'],             
            self.exit5    : [(9, 4),  'normalNumberInside'],
            self.exit6    : [(10,4),  'normalNumberInside'],
            self.exit7    : [(11,4),  'normalNumberInside'],
            self.exit8    : [(12,4),  'normalNumberRight'],             
            
            self.time1 : [(5, 5),  'normalSubLeft'],          
            self.time2 : [(6, 5),  'normalSub'],              
            self.time3 : [(7, 5),  'normalSub'],              
            self.time4 : [(8, 5),  'normalSub'],              
            self.time5 : [(9, 5),  'normalSub'],
            self.time6 : [(10,5), 'normalSub'],
            self.time7 : [(11,5), 'normalSub'],
            self.time8 : [(12,5), 'normalSubRight'],              
            
            self.eshare1:  [(5, 6), 'normalSubLeft'],          
            self.eshare2:  [(6, 6), 'normalSub'],              
            self.eshare3:  [(7, 6), 'normalSub'],              
            self.eshare4:  [(8, 6), 'normalSub'],              
            self.eshare5:  [(9, 6), 'normalSub'],
            self.eshare6:  [(10,6), 'normalSub'],
            self.eshare7:  [(11,6), 'normalSub'],
            self.eshare8:  [(12,6), 'normalSubRight'],
            
            self.diff1  :  [(5, 7),  'normalSubLeft'],
            self.diff2  :  [(6, 7),  'normalSub'],
            self.diff3  :  [(7, 7),  'normalSub'],
            self.diff4  :  [(8, 7),  'normalSub'],
            self.diff5  :  [(9, 7),  'normalSub'],
            self.diff6  :  [(10,7),  'normalSub'],
            self.diff7  :  [(11,7),  'normalSub'],
            self.diff8  :  [(12,7),  'normalSubRight'],     
            
            self.pl1  :  [(5, 8),  'normalSubNumberBottomLeft'],
            self.pl2  :  [(6, 8),  'normalSubNumberBottom'],
            self.pl3  :  [(7, 8),  'normalSubNumberBottom'],
            self.pl4  :  [(8, 8),  'normalSubNumberBottom'],
            self.pl5  :  [(9, 8),  'normalSubNumberBottom'],
            self.pl6  :  [(10,8),  'normalSubNumberBottom'],
            self.pl7  :  [(11,8),  'normalSubNumberBottom'],
            self.pl8  :  [(12,8),  'normalSubNumberBottomRight'],           
            
            self.explain  : [[(4, 9), (12, 14)], 'explain'],
            self.notes    : [[(4, 15), (12, 20)], 'noteStyle']
            }
        
        # Set up the excel formulas for the trade summaries. The ones for Mistake Summary are in 
        # their class
        # In this dict, the values are a list in which the first entry is the formula itsef
        # with format specifiers {} for the referenced addresses. The rest of the list is the location
        # of the cells within the trade summary form at A1. To fill this in translate the cell addresses
        # and replace the specifiers.
        self.tfformulas = dict()
        self.tfformulas[self.targdiff] = ["={0}-{1}", 
                                          self.tfcolumns[self.targ][0], 
                                          self.tfcolumns[self.entry1][0]
                                          ]
        self.tfformulas[self.sldiff] = ["={0}-{1}", 
                                          self.tfcolumns[self.stoploss][0], 
                                          self.tfcolumns[self.entry1][0]
                                          ]
        self.tfformulas[self.rr] = ["=ABS({0}/{1})", 
                                          self.tfcolumns[self.sldiff][0], 
                                          self.tfcolumns[self.targdiff][0]
                                          ]
        self.tfformulas[self.maxloss] = ['=(LEFT({0},SEARCH(" ",{1},1)))*{2}', 
                                          self.tfcolumns[self.shares][0][0], 
                                          self.tfcolumns[self.shares][0][0],
                                          self.tfcolumns[self.sldiff][0]
                                          ]
         
             
                           
        self.rc = rc  
        self.columns = rc.values()
         
    def getStyles(self):
        '''Retrieves a list of the style names from tfcolumns'''
        _styles = []
        for v in list(self.tfcolumns.values()) :
            _styles.append(v[1])
        
        df = pd.DataFrame(_styles, columns=['st'])
        return df['st'].unique()
    
    



            #TODO get a list of namd styles and verify that all of these strings are on the list. Come up with a mechanism to make this configurable by the user
        
# global variable for use in this module    
srf=SumReqFields()
class TheTradeObject(object):
    '''
    Manages the creation of the Trade Summary objects from the the output DataFrame. 
    Summarize one trade at a time on a single row of a DataFrame and include user input
    like stop, target, and trade strategy 
    :PreRequisite: The original DtaFrame must be transformed into the output DataFrame 
        in which trades are represented in tickets and are seperated and labeled. 
    '''


    def __init__(self, df, interview):
        '''
        Create a dataframe that includes all the summary material for review. Some 
        of this data comes from the program and some of it comes from the user. The 
        user will determine which parts to fill out from a couple of options. 
        :params:df: A DataFrame that includes the transactions, or tickets, 
            from a singel trade.
        '''
        
        
        self.interview = interview
        col=srf.tfcolumns.keys()
        TheTrade = pd.DataFrame(columns=col)
        TheTrade = DataFrameUtil.addRows(TheTrade, 1)

        ix = df.index[-1]
        ix0 = df.index[0]

        
        #TODO This list should be retrieved from TheStrategyObject
        strats = ['ORB', 'ABCD', 'VWAP Reversal', 'Bull Flag', 'Fallen Angel',
          'VWAP False Breakout', 'VWAP Reversal', '15 Minute Reversal',
          'VWAP MA trend', 'Other', 'Skip']
        side = df.loc[ix0][frc.side]
        self.df = df
        self.TheTrade = TheTrade
        self.ix = ix
        self.ix0 = ix0
        self.strats = strats
        self.side = side
        self.shares = 0
        
    def runSummary(self):
        '''
        Populate a DataFrome (self.TheTrade) with all the trade summary information, one row per trade.
        The information will then populate the the openpyxl / excel Trade Summary. The user interview for
        target stoploss, and strategy happen in their respective methods.
        '''
        self.__setName()
        self.__setAcct()
        self.__setSum()
        self.__setStart()
        self.__setDur()
        self.__setMarketValue()
        
        self.__setShares()
        self.__setHeaders()
        self.__setExplainNotes()
        self.__blandSpaceInMstkNote()
        ret = self.__setEntries()
        
        print("Side = ", self.df.loc[self.ix0][frc.side])
        if self.interview == True :
            self.__setStrategy()     
            self.__setTarget()       
            self.__setStop()         
            self.__setMaxLoss()
            ret = self.__setRiskReward()
            self.__setStopLossMistake()
        return ret
    

    def getName(self):
        return self.TheTrade[srf.name]
        
    def __setName(self):
        self.TheTrade[srf.name]=self.df.loc[self.ix][frc.name]
        return self.TheTrade

    def __setAcct(self):
        self.TheTrade[srf.acct]='Live' if self.df.loc[self.ix][frc.acct].startswith('U') else 'SIM'
        return self.TheTrade

    def __setSum(self):
        self.TheTrade[srf.pl]=self.df.loc[self.ix][frc.sum]
        return self.TheTrade
    def __setStart(self):
        self.TheTrade[srf.start]=self.df.loc[self.ix][frc.start]
        return self.TheTrade

    # HACK ALERT The duration came out as an empty string on an older file so I added the babysitting for empty strings
    def __setDur(self):
        
        time = self.df.loc[self.ix][frc.dur]
        if isinstance(time, str ) :
            if len(time) < 1 :
                return
            else :
                duration = time
 
        else :
            duration = "{0} hours {1}:{2}".format(time.seconds // 3600, time.seconds // 60, time.seconds % 60)
        self.TheTrade[srf.dur]=duration
        return self.TheTrade

    def __getStrategy(self) :

        s="What was the strategy?" 
    
        for i, strat in zip(range(1, len(self.strats)+1), self.strats) :
            s = "{0}\n     {1}. {2}".format(s, i, strat)
    
        s = s + "\n"

        while True:
            try :
                reply = input(s)
                ireply = int(reply)
                if ireply < 1 or ireply > len(self.strats) :
                    raise ValueError
                break
            except ValueError:
                print("Please enter a number between 1 and {0}".format(len(self.strats)))
                continue
        return ireply -1

    def __setStrategy(self):
        reply = self.__getStrategy()
    

        if reply == 9 :
            response = input("What do you want to call the strategy?")
            self.TheTrade[srf.strat] = response
        elif reply == 10 :
            pass
        elif reply > -1 and reply < len(self.strats):
            self.TheTrade[srf.strat] =self.strats[reply]
        else :
            print("WTF?  reply out of bounds. 'reply' = {0}".format( reply))
            raise ValueError
        return self.TheTrade
        
    def getShares(self):
        #TODO Rethink this for HOLDs
        if self.shares == 0 :
            if self.side.startswith("B") or self.side.startswith("HOLD+") :
                self.shares = self.df[frc.bal].max()
            else :
                self.shares = self.df[frc.bal].min()
        return self.shares
            
    def __setShares(self):
        self.TheTrade.Shares = "{0} shares".format(self.getShares())
        return self.TheTrade
        
    def __setMarketValue(self):
        mkt = self.getShares() * self.df.loc[self.ix0][frc.price]
        self.TheTrade.MktVal   = mkt
        return self.TheTrade

    def __setHeaders(self):
        self.TheTrade[srf.plhead]    = "P/L"
        self.TheTrade[srf.starthead] = "Start"
        self.TheTrade[srf.durhead  ] = "Dur"
        self.TheTrade[srf.sharehead] = "Pos"
        self.TheTrade[srf.mkthead]   = "Mkt"
        self.TheTrade[srf.entryhead] = 'Entries and Exits'
        self.TheTrade[srf.targhead]  = 'Target'
        self.TheTrade[srf.stophead]  = 'Stop'
        self.TheTrade[srf.rrhead]    = 'R:R'
        self.TheTrade[srf.maxhead]   = 'Max Loss'
        self.TheTrade[srf.mstkhead]  = "Proceeds Lost"
        return self.TheTrade[[srf.entryhead, srf.targhead, srf.stophead, srf.rrhead, srf.maxhead]]
  
    def __setEntries(self):
        '''
        This method places in the trade summary form the entries, exits, time of 
        transaction, number of shares, and the difference between price of this 
        transaction and the 1st entry (or over night hold entry).  The strategy I 
        adopted for overnight hold is not ideal. Keep brainstorming for alternitives. 
        The logic tree to make entries/exits is convoluted.
        '''
        entries=list()
        exits=list()
        #TODO Fix the hold entry
#         if self.df.loc[self.ix0][frc.side].lower().startswith('hold') :
        long = False            
        entry1=0
        count=0
        exitPrice = 0
        partEntryPrice = 0
        if self.df.loc[self.ix0][frc.side].startswith('B') or self.df.loc[self.ix0][frc.side].lower().startswith('hold+') :
            long = True
        if self.df.loc[self.ix0][frc.price] == 0 :
            for i, row in self.df.iterrows() :
                if long and count and row[frc.side].startswith('S') :
                    exitPrice = exitPrice + abs(row[frc.price] * row[frc.shares])
                elif count :
                    partEntryPrice = partEntryPrice + abs(row[frc.price] * row[frc.shares])
                count = count + 1
            entryPrice=exitPrice - self.df.loc[self.ix][frc.sum]
            entry1 = (entryPrice - partEntryPrice)/self.df.loc[self.ix0][frc.shares]
            self.df.loc[self.ix0][frc.price] = entry1

            
        for i, row in self.df.iterrows() :
            #ix0 is the index of the first row in df -- a dataframe holding one trade in at least rows (1 row per ticket)
            # if self.df.loc[self.ix0][frc.side].startswith('B') or self.df.loc[self.ix0][frc.side].lower().startswith('hold+') :
            #     long = True
            diff=0
            if count == 0:
                entry1 = row[frc.price] 
            else :
                diff =  row[frc.price] -entry1
                
            if long :
                if (row[frc.side]).startswith('B') or (row[frc.side]).lower().startswith("hold+"):
                   
                    entries.append(
                        [row[frc.price],
                        row[frc.time], 
                        row[frc.shares],
                        0, 
                        diff, 
                        "Entry"])
                else :
                    entries.append([
                        row[frc.price], 
                        row[frc.time], 
                        row[frc.shares], 
                        row[frc.PL], 
                        diff, 
                        "Exit"])
            else :
                if (row[frc.side]).startswith('B') :
                    entries.append([
                        row[frc.price], 
                        row[frc.time], 
                        row[frc.shares], 
                        row[frc.PL], 
                        diff, 
                        "Exit"])
                else :
                    entries.append([
                        row[frc.price],
                        row[frc.time], 
                        row[frc.shares], 
                        0, diff, 
                        "Entry"])
            count = count + 1

        #TODO This is broken because we display only 8 combined entries plus exits
        if len(entries) > 8 :
            more = len(entries) - 8
            self.TheTrade[srf.pl8] =  "Plus {} more.".format(more)
        for i, price in zip(range (len(entries)), entries) :
            
            #Entry Price
            if price[5] == "Entry" :
                col = "Entry" + str(i+1)
            else :
                col = "Exit" + str(i+1)
            self.TheTrade[col] = price[0]

            #Entry Time
            col="Time" + str(i+1)
            self.TheTrade[col] = price[1]
    
            #Entry Shares
            col= "EShare" + str(i+1)
            self.TheTrade[col] = price[2]
            
            #Entry P/L
            col= "PL" + str(i+1)
            self.TheTrade[col] = price[3]
            
            #Entry diff
            col= "Diff" + str(i+1)
            self.TheTrade[col] = price[4]
        return self.TheTrade

    
    def __setTarget(self) :
        '''Interview the user for the target. targdiff is handled as a formula elsewhere'''
        target = 0
        shares = self.TheTrade[srf.shares].unique()[0]
        try :
            p= float(self.TheTrade[srf.entry1])
            p=f'{p:.3f}'
        except :
            question = '''
            Your position was {0}.
            What was your target?
                 '''.format(shares)
        else :
            side = self.TheTrade[srf.name].unique()[0].split()[1].lower()
            
            question = '''
                Your entry was {0} at {1}.
                your position was {2}.
                What was your target?.
                     '''.format(side, p, shares)
        while True:
            try :
                
                
                targ = input(question)
                if targ.lower().startswith('q') :
                    target = 0
                    break
                target = float(targ)
            except ValueError :
                print('''
                Please enter a number or 'q' to skip
                ''')
                target = 0
                
                continue
            break
        
        pd.to_numeric(self.TheTrade[srf.targ] , errors='coerce')
        self.TheTrade[srf.targ] = target
        
        # TODO update--Unecessary? If this is a trade with a previous holding, 
        # Planning to change the target diff to a formula-- add formulas to tfcolumns
        if self.df.loc[self.ix0][frc.side].lower().startswith('hold') :
            return
        
        # Although we will use an excel formula, place it in the df for our use.
        diff = target - self.TheTrade[srf.entry1]
        self.TheTrade[srf.targdiff] = diff

        return self.TheTrade

    def __setStop(self) :
        '''Interview the user and git the stoploss. sldiff is handled elsewhere as an excel formula.'''
        stop = 0
        
        shares = self.TheTrade[srf.shares].unique()[0]
        try :
            p= float(self.TheTrade[srf.entry1])
            p=f'{p:.3f}'
        except :
            question = '''
            Your position was {0}.
            What was your stop?
                 '''.format(shares)
        else :
            side = self.TheTrade[srf.name].unique()[0].split()[1].lower()
            question = '''
                Your entry was {0} at {1}.
                your position was {2}.
                What was your stop?.
                     '''.format(side, p, shares)
        
        while True:
            try :
                stop = input(question)
                if stop.lower().startswith('q') :
                    stop = 0
                    break
                stop = float(stop)
            except ValueError :
                print('''
                Please enter a number or 'q' to skip
                ''')
                continue
            break
        
        self.TheTrade[srf.stoploss] = stop
        
        # If this is a trade with a privious holding, the diff in price of the stophas no meaning
        if self.df.loc[self.ix0][frc.side].lower().startswith('hold') :
            return

        # Although we will use an excel formula, place it in the df for our use.
        self.TheTrade[srf.sldiff] = stop - self.TheTrade[srf.entry1]
        return self.TheTrade
    
    def __setMaxLoss(self):
        # Although we will use an excel formula, place it in the df for our use.
        self.TheTrade.MaxLoss = self.TheTrade.SLDiff * self.getShares()
        return self.TheTrade

    def __setRiskReward(self):
        #Handled as an excel formula elsewhere
                
#         self.TheTrade.RR = self.TheTrade.StopLoss / self.TheTrade.Target
        return self.TheTrade
    
    def __setStopLossMistake(self):
        '''
        If the amount lost from a trade exceeds the Max Loss, post the difference in mstkval and fill in mstknote. Note that
        this is not done with a formula because the space can be used for any mistake and should be filled in by the 
        user if, for example, the its sold before a target and the trade never approached the stoploss.
        '''
        if isinstance(self.TheTrade[srf.maxloss].unique()[0], str) :
            # There is no entry in entry1 so maxLoss has no meaning here.
            return
        if self.TheTrade[srf.pl].unique()[0] < 0 :
            if abs(self.TheTrade[srf.pl].unique()[0]) > abs(self.TheTrade[srf.maxloss].unique()[0]) :
                self.TheTrade[srf.mstkval] = abs(self.TheTrade[srf.maxloss].unique()[0]) - abs(self.TheTrade[srf.pl].unique()[0])
                self.TheTrade[srf.mstknote] = "Exceeded Stop Loss!"

    def __blandSpaceInMstkNote(self):
        self.TheTrade[srf.mstknote] = "Final note"
                
    def __setExplainNotes(self) :
        self.TheTrade[srf.explain] = "Technical description of the trade"
        self.TheTrade[srf.notes] = "Evaluation of the trade"