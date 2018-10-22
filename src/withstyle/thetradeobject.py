import pandas as pd
from journal.dfutil import DataFrameUtil 
from journal.tradeutil import  FinReqCol


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
        
        # rcvals are the actual column titles 
        # rckeys are the abstracted names for use with all file types
        #While placing these here are not really necessary, it provides code style consistency with the use of ReqCol and FinReqCol
        rcvals = ['Name', 'Account', 'Strategy','P/LHead', 'P / L', 'StartHead', 'Start','DurHead', 'Duration', 'ShareHead', 'Shares', 'MktHead', 'MktVal',
                  'TargHead', 'Target', 'TargDiff', 'StopHead', 'StopLoss', 'SLDiff',  'RRHead', 'RR', 'MaxHead', 'MaxLoss', 'MstkHead', 'MstkVal', 'MstkNote', 'Link1',
                 'EntryHead', 'Entry1', 'Entry2', 'Entry3', 'Entry4', 'Entry5', 'EntTime1',  'EntTime2',  'EntTime3',  'EntTime4',  'EntTime5', 
                 'EntShare1', 'EntShare2', 'EntShare3', 'EntShare4', 'EntShare5', 'EntAvg1', 'EntAvg2',  'EntAvg3', 'EntAvg4', 'EntAvg5',   
                 
                 'ExitHead', 'Exit1', 'Exit2', 'Exit3', 'Exit4', 'Exit5', 'ExtTime1', 'ExtTime2', 'ExtTime3', 'ExtTime4', 'ExtTime5',
                 'ExtShare1', 'ExtShare2', 'ExtShare3', 'ExtShare4', 'ExtShare5', 'ExtPL1', 'ExtPL2', 'ExtPL3', 'ExtPL4', 'ExtPL5',   
                 'Explain', 'Notes'
                  ]
#         rcvals2 =[  'StratNote', 'Link5', 'Link6', ]
        
        rckeys = ['name', 'acct', 'strat','plhead', 'pl', 'starthead', 'start','durhead', 'dur', 'sharehead', 'shares', 'mkthead', 'mktval',
                 'targhead', 'targ', 'targdiff', 'stophead', 'stoploss', 'sldiff',  'rrhead', 'rr', 'maxhead', 'maxloss', 'mstkhead', 'mstkval', 'mstknote', 'link1', 
                 'entryhead', 'entry1', 'entry2', 'entry3', 'entry4', 'entry5', 'enttime1',  'enttime2',  'enttime3',  'enttime4',  'enttime5', 
                 'entshare1', 'entshare2', 'entshare3', 'entshare4', 'entshare5', 'entavg1', 'entavg2',  'entavg3', 'entavg4', 'entavg5',   
                 
                 'exithead', 'exit1', 'exit2', 'exit3', 'exit4', 'exit5', 'exttime1', 'exttime2', 'exttime3', 'exttime4', 'exttime5',
                 'extshare1', 'extshare2', 'extshare3', 'extshare4', 'extshare5', 'extpl1', 'extpl2', 'extpl3', 'extpl4', 'extpl5',   
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
        self.link1    = rc['link1']     
        self.entryhead= rc['entryhead']
        self.entry1   = rc['entry1']   
        self.entry2   = rc['entry2']   
        self.entry3   = rc['entry3']   
        self.entry4   = rc['entry4']   
        self.entry5   = rc['entry5']   
        self.enttime1 = rc['enttime1']             
        self.enttime2 = rc['enttime2']
        self.enttime3 = rc['enttime3']
        self.enttime4 = rc['enttime4']
        self.enttime5 = rc['enttime5']             
        self.entshare1=rc['entshare1']  
        self.entshare2= rc['entshare2'] 
        self.entshare3= rc['entshare3'] 
        self.entshare4= rc['entshare4'] 
        self.entshare5= rc['entshare5'] 
        self.entavg1  = rc['entavg1'] 
        self.entavg2  = rc['entavg2'] 
        self.entavg3  = rc['entavg3'] 
        self.entavg4  = rc['entavg4'] 
        self.entavg5  = rc['entavg5'] 
        self.exithead = rc['exithead'] 
        self.exit1    = rc['exit1']    
        self.exit2    = rc['exit2']    
        self.exit3    = rc['exit3']    
        self.exit4    = rc['exit4']    
        self.exit5    = rc['exit5']    
        self.exttime1 = rc['exttime1'] 
        self.exttime2 = rc['exttime2'] 
        self.exttime3 = rc['exttime3'] 
        self.exttime4 = rc['exttime4'] 
        self.exttime5 = rc['exttime5']  
        self.extshare1= rc['extshare1'] 
        self.extshare2= rc['extshare2'] 
        self.extshare3= rc['extshare3'] 
        self.extshare4= rc['extshare4'] 
        self.extshare5= rc['extshare5'] 
        self.extpl1   = rc['extpl1']   
        self.extpl2   = rc['extpl2']   
        self.extpl3   = rc['extpl3']   
        self.extpl4   = rc['extpl4']   
        self.extpl5   = rc['extpl5']   
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
            self.plhead   : [[(7, 3), (7, 4)], 'titleLeft'],      
            self.pl       : [[(8, 3), (9, 4)], 'titleNumberRight'],
            self.starthead: [[(7, 5), (7, 6)], 'titleLeft'],     
            self.start    : [[(8, 5), (9, 6)], 'titleRight'],
            self.durhead  : [[(7, 7), (7, 8)], 'titleLeft'],      
            self.dur      : [[(8, 7), (9, 8)], 'titleRight'],
            self.sharehead: [[(7, 9), (7, 10)], 'titleLeft'],     
            self.shares   : [[(8, 9), (9, 10)], 'titleRight'],        
            self.mkthead  : [[(7, 11), (7, 12)], 'titleLeft'],     
            self.mktval   : [[(8, 11), (9, 12)], 'titleNumberRight'], 
            self.targhead : [(7,13), 'normStyle'],
            self.targ     : [(8,13), 'normalNumber'],
            self.targdiff : [(9,13), 'normStyle'],
            self.stophead : [(7,14), 'normStyle'],      
            self.stoploss : [(8,14), 'normStyle'],
            self.sldiff   : [(9,14), 'normStyle'],
            self.rrhead   : [(7,15), 'normStyle'],
            self.rr       : [(8,15), 'normalFraction'],
            "ex1"           : [(9,15), 'normStyle'],
            self.maxhead  : [(7,16), 'normStyle'],
            self.maxloss  : [(8,16), 'normStyle'],
            "ex2"         : [(9,16), 'normStyle'],
            self.mstkhead : [[(7, 17), (7,18)], 'normStyle'],
            self.mstkval  : [[(8, 17), (9, 18)], 'titleNumberRight' ],
            self.mstknote : [[(7, 19), (9, 20)], 'normStyle'], 
            self.link1    : [[(7, 21), (9, 22)], 'linkStyle'],
            self.entryhead: [[(1, 3), (1, 6)], 'normStyle'],
            self.entry1   : [(2,3), 'normalNumberTopLeft'],
            self.entry2   : [(3,3), 'normalNumberTop'],
            self.entry3   : [(4,3), 'normalNumberTop'],
            self.entry4   : [(5,3), 'normalNumberTop'],
            self.entry5   : [(6,3), 'normalNumberTop'],
            self.enttime1 : [(2,4), 'normalSubLeft'],
            self.enttime2 : [(3,4), 'normalSub'],
            self.enttime3 : [(4,4), 'normalSub'],
            self.enttime4 : [(5,4), 'normalSub'],
            self.enttime5 : [(6,4), 'normalSub'],
            self.entshare1: [(2,5), 'normalSubLeft'],
            self.entshare2: [(3,5), 'normalSub'],
            self.entshare3: [(4,5), 'normalSub'],
            self.entshare4: [(5,5), 'normalSub'],
            self.entshare5: [(6,5), 'normalSubRight'],
            self.entavg1  : [(2,6), 'normalSubNumberBottomLeft'],
            self.entavg2  : [(3,6), 'normalNumberBottom'],
            self.entavg3  : [(4,6), 'normalNumberBottom'],
            self.entavg4  : [(5,6), 'normalNumberBottom'],
            self.entavg5  : [(6,6), 'normalSubNumberBottomRight'],
            self.exithead : [[(1, 7), (1, 10)], 'normStyle'],     
            self.exit1    : [(2,7), 'normalNumberTopLeft'],    
            self.exit2    : [(3,7), 'normalNumberTop'],             
            self.exit3    : [(4,7), 'normalNumberTop'],             
            self.exit4    : [(5,7), 'normalNumberTop'],             
            self.exit5    : [(6,7), 'normalNumberTop'],             
            self.exttime1 : [(2,8), 'normalSubLeft'],          
            self.exttime2 : [(3,8), 'normalSub'],              
            self.exttime3 : [(4,8), 'normalSub'],              
            self.exttime4 : [(5,8), 'normalSub'],              
            self.exttime5 : [(6,8), 'normalSub'],              
            self.extshare1: [(2,9), 'normalSubLeft'],          
            self.extshare2: [(3,9), 'normalSub'],              
            self.extshare3: [(4,9), 'normalSub'],              
            self.extshare4: [(5,9), 'normalSub'],              
            self.extshare5: [(6,9), 'normalSubRight'],         
            self.extpl1   : [(2,10), 'normalSubNumberBottomLeft'], 
            self.extpl2   : [(3,10), 'normalNumberBottom'],     
            self.extpl3   : [(4,10), 'normalNumberBottom'],     
            self.extpl4   : [(5,10), 'normalNumberBottom'],     
            self.extpl5   : [(6,10), 'normalSubNumberBottomRight'],
#             "ex3"         : [(1,11), 'normStyle'],
#             "ex4"         : [(2,11), 'normStyle'],
#             "ex5"         : [(3,11), 'normStyle'],
#             "ex6"         : [(4,11), 'normStyle'],
#             "ex7"         : [(5,11), 'normStyle'],
#             "ex8"         : [(6,11), 'normStyle'],
#             "ex9"         : [(1,12), 'normStyle'],
#             "ex10"        : [(2,12), 'normStyle'],
#             "ex911"       : [(3,12), 'normStyle'],
#             "ex12"        : [(4,12), 'normStyle'],
#             "ex13"        : [(5,12), 'normStyle'],
#             "ex14"        : [(6,12), 'normStyle'],
            self.explain  : [[(1, 11), (6, 16)], 'explain'],
            self.notes    : [[(1, 17), (6, 22)], 'noteStyle']
            }
        self.tfformulas = dict()
        self.tfformulas[self.targdiff] = ["={0}-{1}", 
                                          self.tfcolumns[self.targ][0], 
                                          self.tfcolumns[self.entry1][0]
                                          ]
        self.tfformulas[self.sldiff] = ["={0}-{1}", 
                                          self.tfcolumns[self.stoploss][0], 
                                          self.tfcolumns[self.entry1][0]
                                          ]
        self.tfformulas[self.rr] = ["={0}/{1}", 
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
    Summarize one trade at a time on a single row of a DataFramme. 
    :PreRequisite: The original DtaFrame must be transformed into the output DataFrame in which trades are represented in tickets and 
                    are seperated and labeled. 
    '''


    def __init__(self, df, interview):
        '''
        Create a dataframe that includes all the summary material for review. Some of this data comes from the program
        and some of it comes from the user. The user will determine which parts to fill out from a couple of options.
        :params:df: A DataFrame that includes the transactions, or tickets, from a singel trade.
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
        
    def __getShares(self):
        #TODO Rethink this for HOLDs
        if self.shares == 0 :
            if self.side.startswith("B"):
                self.shares = self.df[frc.bal].max()
            else :
                self.shares = self.df[frc.bal].min()
        return self.shares
            
    def __setShares(self):
        self.TheTrade.Shares = "{0} shares".format(self.__getShares())
        return self.TheTrade
        
    def __setMarketValue(self):
        mkt = self.__getShares() * self.df.loc[self.ix0][frc.price]
        self.TheTrade.MktVal   = mkt
        return self.TheTrade

    def __setHeaders(self):
        self.TheTrade[srf.plhead] = "P/L"
        self.TheTrade[srf.starthead] = "Start"
        self.TheTrade[srf.durhead  ] = "Dur"
        self.TheTrade[srf.sharehead] = "Pos"
        self.TheTrade[srf.mkthead]   = "Mkt"
        self.TheTrade[srf.entryhead] = 'Entries'
        self.TheTrade[srf.exithead] = 'Exits'
        self.TheTrade[srf.targhead] = 'Target'
        self.TheTrade[srf.stophead] = 'Stop'
        self.TheTrade[srf.rrhead] = 'R:R'
        self.TheTrade[srf.maxhead] = 'Max Loss'
        self.TheTrade[srf.mstkhead] = "Proceeds Lost"
        return self.TheTrade[[srf.entryhead, srf.exithead, srf.targhead, srf.stophead, srf.rrhead, srf.maxhead]]
  
    def __setEntries(self):
        entries=list()
        exits=list()
        #TODO Fix the hold entry
#         if self.df.loc[self.ix0][frc.side].lower().startswith('hold') :
        long = False            

        for i, row in self.df.iterrows() :
            if self.df.loc[self.ix0][frc.side].startswith('B') or self.df.loc[self.ix0][frc.side].lower().startswith('hold+') :
                long = True
            
            if long :
                if (row[frc.side]).startswith('B') :
                    entries.append([row[frc.price],row[frc.time], row[frc.shares],34.56])
                else :
                    exits.append([row[frc.price], row[frc.time], row[frc.shares], row[frc.PL]])
            else :
                if (row[frc.side]).startswith('B') :
                    exits.append([row[frc.price], row[frc.time], row[frc.shares], row[frc.PL]])
                else :
                    entries.append([row[frc.price],row[frc.time], row[frc.shares],34.56])

        if len(entries) > 5 :
            more = len(entries) - 5
            self.TheTrade.Entry5 =  "Plus {} more.".format(more)
        for i, price in zip(range (len(entries)), entries) :
            col = "Entry" + str(i+1)
            self.TheTrade[col] = price[0]

            col="EntTime" + str(i+1)
            self.TheTrade[col] = price[1]
    
            col= "EntShare" + str(i+1)
            self.TheTrade[col] = price[2]
            
            col= "EntAvg" + str(i+1)
            self.TheTrade[col] = price[3]


        if len(exits) > 5 :
            more = len(exits) - 5
            self.TheTrade.Exits5 =  "Plus {} more.".format(more)
        for i, price in zip(range (len(exits)), exits) :
            col = "Exit" + str(i+1)
            self.TheTrade[col] = price[0]
            
            col="ExtTime" + str(i+1)
            self.TheTrade[col] = price[1]
    
            col= "ExtShare" + str(i+1)
            self.TheTrade[col] = price[2]
            
            col= "ExtPL" + str(i+1)
            self.TheTrade[col] = price[3]
            
            
            
        return self.TheTrade
    
    def __setTarget(self) :
        '''Interview the user for the target. targdiff is handled as a formula elsewhere'''
        target = 0
        
        try :
            p= float(self.TheTrade[srf.entry1])
            p=f'{p:.3f}'
        except :
            question = '''
            What was your target?
                 '''
        else :
            question = '''
                Your entry was {0}.
                What was your target?.
                     '''.format(p)
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
        
        # If this is a trade with a privious holding, 
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
        try :
            p= float(self.TheTrade[srf.entry1])
            p=f'{p:.3f}'
        except :
            question = '''
            What was your stop?
                 '''
        else :
            question = '''
                Your entry was {0}.
                What was your stop?.
                     '''.format(p)
        
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
        self.TheTrade.MaxLoss = self.TheTrade.SLDiff * self.__getShares()
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
        if self.TheTrade[srf.pl].unique()[0] < 0 :
    
            if abs(self.TheTrade[srf.pl].unique()[0]) > abs(self.TheTrade[srf.maxloss].unique()[0]) :
                self.TheTrade[srf.mstkval] = abs(self.TheTrade[srf.maxloss].unique()[0]) - abs(self.TheTrade[srf.pl].unique()[0])
                self.TheTrade[srf.mstknote] = "Exceeded Stop Loss!"


    







