# 
# Note that the interview stuff will be taken care of during the image insertion allowing the user to do all the 
# review of a tradeafter viewing the chart. The interview stuff will include: 1. strategy  2. brief strategy note  
# 3. target  4. stop loss  5. description of trade.  6. Notes and analysis of the trade

# On Second thought, the strategy note, trade explanation and analysis will be left to do in excel. The Gui Version 
# of structjour will implement that part of the review. Otherwise I would have to include some facility for entering 
# multiple sentences in the console app.  Not that difficult but not that helpful when it can be done in Excel wilh 
# all the visuals present.

import pandas as pd
import datetime
# from journalfiles import JournalFiles
from structjour.pandasutil import DataFrameUtil 
# InputDataFrame, ToCSV_Ticket as Ticket
from structjour.tradeutil import  FinReqCol
# XLImage, TradeUtil

# Use to access columns in the (altered) input dataframe, known on this page as df. Use srf (SumReqFields instance) to access
# columns/data for the summary trade dataframe, known on this page as TheTrade.
frc = FinReqCol()

class SumReqFields(object):
    '''Manage the required columns, cell location and namedStyle for the summary aka TheTradeObject and TheTradeStyle'''

    def __init__(self):
        rcvals =['Name', 'Account', 'P / L', 'Start', 'Duration', 'Strategy', 'StratNote', 'Shares', 'MktVal', 
                 'Link1', 'Link2', 'Link3', 'Link4', 'Link5', 'Link6', 
                 'EntryHead', 'Entry1', 'Entry2', 'Entry3', 'Entry4', 'Entry5', 
                 'ExitHead', 'Exit1', 'Exit2', 'Exit3', 'Exit4', 'Exit5', 
                 'TargHead', 'Target', 'TargDiff', 
                 'StopHead', 'StopLoss', 'SLDiff', 
                 'RRHead', 'RR', 'MaxHead', 'MaxLoss', 'Explain', 'Notes']
        
        rckeys = ['name', 'acct', 'PL', 'start', 'dur', 'strat', 'stratnote', 'shares', 'mktval', 
                  'link1', 'link2', 'link3', 'link4', 'link5', 'link6',
                  'entryhead', 'entry1', 'entry2', 'entry3', 'entry4', 'entry5',
                  'exithead', 'exit1', 'exit2', 'exit3', 'exit4', 'exit5',
                  'targhead', 'targ', 'targdiff',
                  'stophead', 'stoploss', 'sldiff',
                  'rrhead', 'rr', 'maxhead', 'maxloss', 'explain', 'notes']
        
        
        # This includes all the locations that are likely to have data associated with them.  Blank cells are added to tfcolumns  Each of these are added as 
        # attributes Unnecessarily as but it should reduce errors to use attributes instead of strings
        rc = dict(zip(rckeys, rcvals))
        
        # The user should generally use these as dot accessors to get the columns names. <soapbox> I am against strings as the primary navigation
        # in a programming language. Leave that to SQL in VB or html. A level of abstraction is safer. rc.name rather than rc['Name']
        # Dictionary type is for programmers/implementation, not users/interface. </soapbox>
       
        self.name     = rc['name']
        self.acct     = rc['acct']
        self.PL       = rc['PL']
        self.start    = rc['start']
        self.dur      = rc['dur']
        self.strat    = rc['strat']
        self.stratnote= rc['stratnote']
        self.shares   = rc['shares']
        self.mktval   = rc['mktval']
        self.link1    = rc['link1']
        self.link2    = rc['link2']
        self.link3    = rc['link3']
        self.link4    = rc['link4']
        self.link5    = rc['link5']
        self.link6    = rc['link6']
        self.entryhead= rc['entryhead']
        self.entry1   = rc['entry1']
        self.entry2   = rc['entry2']
        self.entry3   = rc['entry3']
        self.entry4   = rc['entry4']
        self.entry5   = rc['entry5']
        self.exithead = rc['exithead']
        self.exit1    = rc['exit1']
        self.exit2    = rc['exit2']
        self.exit3    = rc['exit3']
        self.exit4    = rc['exit4']
        self.exit5    = rc['exit5']
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
        self.explain  = rc['explain']
        self.notes    = rc['notes']
        
        self.rc = rc
        self.columns = rc.values()
        
        
        #The cell called 'normxx' are not in any other place This will be used to set the style for each cell/merged group of the TradeObject in excell. They ar not in rckeys 
        
        self.tfcolumns = { 
            self.name     : [[(1, 1), (3, 2)],'titleStyle'],
            self.acct      : [[(4 ,1), (6, 2)],'titleStyle'],
            self.PL       : [[(7, 1), (9, 2)],'titleStyle'],
            self.start    : [[(1, 3), (3, 4)],'titleStyle'],
            self.dur      : [[(4, 3), (6, 4)],'titleStyle'],
            self.strat    : [[(7, 3), (9, 4)],'titleStyle'],
            self.stratnote: [[(7, 5), (9, 6)],'titleStyleStratNotes'],
            self.shares   : [[(7, 7), (9, 8)],'titleStyle'],
            self.mktval   : [[(7, 9), (9, 10)],'titleStyle'],
            self.link1    : [[(7, 11),(9, 12)],'titleStyleLink'],
            self.link2    : [[(7, 13),(9, 14)],'titleStyleLink'],
            self.link3    : [[(7, 15),(9, 16)],'titleStyleLink'],
            self.link4    : [[(7, 17),(9, 18)],'titleStyleLink'],
            self.link5    : [[(7, 19),(9, 20)],'titleStyleLink'],
            self.link6    : [[(7, 21),(9, 22)],'titleStyleLink'],
            self.entryhead: [(1, 5),'normStyle'],
            self.entry1   : [(2, 5),'normStyle'],
            self.entry2   : [(3, 5),'normStyle'],
            self.entry3   : [(4, 5),'normStyle'],
            self.entry4   : [(5, 5),'normStyle'],
            self.entry5   : [(6, 5),'normStyle'],
            self.exithead : [(1, 6),'normStyle'],
            self.exit1    : [(2, 6),'normStyle'],
            self.exit2    : [(3, 6),'normStyle'],
            self.exit3    : [(4, 6),'normStyle'],
            self.exit4    : [(5, 6),'normStyle'],
            self.exit5    : [(6, 6),'normStyle'],
            self.targhead : [(1, 7),'normStyle'],
            self.targ     : [(2, 7),'normStyle'],
            self.targdiff : [(3, 7),'normStyle'],
            "norm47"      : [(4, 7),'normStyle'],
            "norm57"      : [(5, 7),'normStyle'],
            "norm67"      : [(6, 7),'normStyle'],          
            self.stophead : [(1, 8),'normStyle'],
            self.stoploss : [(2, 8),'normStyle'],
            self.sldiff   : [(3, 8),'normStyle'],
            "norm48"      : [(4, 8),'normStyle'],
            "norm58"      : [(5, 8),'normStyle'],
            "norm68"      : [(6, 8),'normStyle'],
            self.rrhead   : [(1, 9),'normStyle'],
            self.rr       : [(2, 9),'normStyleRR'],
            "norm39"      : [(3, 9),'normStyle'],
            "norm49"      : [(4, 9),'normStyle'],
            "norm59"      : [(5, 9),'normStyle'],
            "norm69"      : [(6, 9),'normStyle'],
            self.maxhead  : [(1, 10),'normStyle'],
            self.maxloss  : [(2, 10),'normStyle'],
            "norm310"     : [(3, 10),'normStyle'],
            "norm410"     : [(4, 10),'normStyle'],
            "norm510"     : [(5, 10),'normStyle'],
            "norm610"     : [(6, 10),'normStyle'],

            self.explain  : [[(1,11), (6,16)],'noteStyle'],
            self.notes    : [[(1,17), (6,22)],'noteStyle']
    
                     }
            #TODO get a list of namd styles and verify that all of these strings are on the list. Come up with a mechanism to make this configurable by the user
        
# global variable for use in this module    
srf=SumReqFields()
class TheTradeObject(object):
    '''Summarize one trade at a time'''


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
        self.TheTrade[srf.PL]=self.df.loc[self.ix][frc.sum]
        return self.TheTrade

    def __setStart(self):
        self.TheTrade[srf.start]=self.df.loc[self.ix][frc.start]
        return self.TheTrade

    def __setDur(self):
        time = self.df.loc[self.ix][frc.dur]
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
        self.TheTrade[srf.entryhead] = 'Entries'
        self.TheTrade[srf.exithead] = 'Exits'
        self.TheTrade[srf.targhead] = 'Target'
        self.TheTrade[srf.stophead] = 'Stop'
        self.TheTrade[srf.rrhead] = 'R:R'
        self.TheTrade[srf.maxhead] = 'Max Loss'
        return self.TheTrade[[srf.entryhead, srf.exithead, srf.targhead, srf.stophead, srf.rrhead, srf.maxhead]]
  
    def __setEntries(self):
        B=list()
        S=list()
        
        for i, row in self.df.iterrows() :
            if(row[frc.side]).startswith('B') :
                B.append(row[frc.price])
            else :
                S.append(row[frc.price])
    
        if len(B) > 5 :
            more = len(B) - 5
            self.TheTrade.Entry5 =  "Plus {} more.".format(more)
        for i, price in zip(range (len(B)), B) :
            col = "Entry" + str(i+1)
            self.TheTrade[col] = price
    

        if len(S) > 5 :
            more = len(S) - 5
            self.TheTrade.Exits5 =  "Plus {} more.".format(more)
        for i, price in zip(range (len(S)), S) :
            col = "Exit" + str(i+1)
            self.TheTrade[col] = price
        return self.TheTrade
    #[[srf.entryhead, srf.entry1, srf.entry2, srf.entry3, srf.entry4, srf.entry5, 
    #                          srf.exithead, srf.exit1, srf.exit2, srf.exit3, srf.exit4, srf.exit5]]
    
    def __setTarget(self) :
        target = 0
        while True:
            try :
                targ = input("What was your target? ")
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
        
        # If this is a trade with a privious holding, the diff in price of the target has no meaning
        if self.df.loc[self.ix0][frc.side].lower().startswith('hold') :
            return

        diff = target - self.TheTrade[srf.entry1]
        self.TheTrade[srf.targdiff] = diff
        return self.TheTrade

    def __setStop(self) :
        stop = 0
        while True:
            try :
                stop = input("What was your Stop Loss? ")
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

        self.TheTrade[srf.sldiff] = stop - self.TheTrade[srf.entry1]
        return self.TheTrade
    
    def __setMaxLoss(self):
        #TODO write some tests that check for unknown types in the SLDiff col. Then fix this to handle them.
        
        self.TheTrade.MaxLoss = self.TheTrade.SLDiff * self.__getShares()
        return self.TheTrade

    def __setRiskReward(self):
        #Write some tests that check for unknown types and then handle them here
                
        self.TheTrade.RR = self.TheTrade.StopLoss / self.TheTrade.Target
        return self.TheTrade
        












