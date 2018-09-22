# 
# Note that the interview stuff will be taken care of during the image insertion allowing the user to do all the 
# review of a tradeafter viewing the chart. The interview stuff will include: 1. strategy  2. brief strategy note  
# 3. target  4. stop loss  5. description of trade.  6. Notes and analysis of the trade

# On Second thought, the strategy note, trade explanation and analysis will be left to do in excel. The Gui Version 
# of structjour will implement that part of the review. Otherwise I would have to include some facility for entering 
# multiple sentences in the console app.  Not that difficult but not that helpful when it can be done in Excel wilh 
# all the visuals present.

import pandas as pd
import datetime.timedelta
# from journalfiles import JournalFiles
from structjour.pandasutil import DataFrameUtil 
# InputDataFrame, ToCSV_Ticket as Ticket
from structjour.tradeutil import  FinReqCol
# XLImage, TradeUtil

frc = FinReqCol()

class TheTradeObject(object):
    '''Summarize one trade at a time'''

    def __init__(self, df):
        '''
        Create a dataframe that includes all the summary material for review. Some of this data comes from the program
        and some of it comes from the user. The user will determine which parts to fill out from a couple of options.
        :params:df: A DataFrame that includes the transactions, or tickets, from a singel trade.
        '''
        
        tfcolumns = { 
            frc.name   : [(1, 1), (3, 2 )],
            frc.acct   : [(4 ,1), (6, 2)],
            frc.PL     : [(7, 1), (9, 2)],
            frc.start  : [(1, 3), (3, 4)],
            frc.dur    : [(4, 3), (6, 4)],
            "Strategy" : [(7, 3), (9, 4)],
            "StratNote": [(7, 5), (9, 6)],
            "Shares"   : [(7, 7), (9, 8)],
            "MktVal"   : [(7, 9), (9, 10)],
            "Link1"    : [(7, 11),(9, 12)],
            "Link2"    : [(7, 13),(9, 14)],
            "Link3"    : [(7, 15),(9, 16)],
            "Link4"    : [(7, 17),(9, 18)],
            "Link5"    : [(7, 19),(9, 20)],
            "Link6"    : [(7, 21),(9, 22)],
            "EntriesHeader": (1, 5),
            "Entries1"     : (2, 5),
            "Entries2"     : (3, 5),
            "Entries3"     : (4, 5),
            "Entries4"     : (5, 5),
            "Entries5"     : (6, 5),
            "ExitsHeader"  : (1, 6),
            "Exits1"       : (2, 6),
            "Exits2"       : (3, 6),
            "Exits3"       : (4, 6),
            "Exits4"       : (5, 6),
            "Exits5"       : (6, 6),
            "TargHead"     : (1, 7),
            "Target"       : (2, 7),
            "TargDiff"     : (3, 7),
            "StopHead"     : (1, 8),
            "StopLoss"     : (2, 8),
            "SLDiff"       : (3, 8),
            "RRHead"       : (1, 9),
            "RR"           : (2, 9),
            "MaxHead"      : (1, 10),
            "MaxLoss"      : (2, 10),
            "Explain"  : [(1,11), (6,16)],
            "Notes"    : [(1,17), (2,22)]
    
                     }
        TheTrade = pd.DataFrame(columns=tfcolumns.keys())
        TheTrade = DataFrameUtil.addRows(TheTrade, 1)

        ix = df.index[-1]
        ix0 = df.index[0]

        
        #TODO This list should be retrieved from TheStrategyObject
        strats = ["ORB", "ABCD", "VWAP Reversal", "Bull Flag", "Fallen ANgel",
          "VWAP False Breakout", "VWAP Reversal", "15 Minute Reversal",
          "VWAP MA trend", "Other", "Skip"]
        side = df.loc[ix0][frc.side]
        self.df = df
        self.TheTrade = TheTrade
        self.ix = ix
        self.ix0 = ix0
        self.strats = strats
        self.side = side
        self.shares = 0
        
    def _setName(self):
        self.TheTrade[frc.name]=self.df.loc[self.ix][frc.name]

    def _setAcct(self):
        self.TheTrade[frc.acct]="Live" if self.df.loc[self.ix][frc.acct].startswith("U") else "SIM"

    def _setSum(self):
        self.TheTrade[frc.PL]=self.df.loc[self.ix][frc.sum]

    def _setStart(self):
        self.TheTrade[frc.start]=self.df.loc[self.ix][frc.start]

    def _setDur(self):
        time = self.df.loc[self.ix][frc.dur]
        duration = "{0} hours {1}:{2}".format(time.seconds // 3600, time.seconds // 60, time.seconds % 60)
        self.TheTrade[frc.dur]=duration

    def getStrategy(self) :

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

    def _setStrategy(self):
        reply = self.getStrategy()
    

        if reply == 9 :
            response = input("What do you want to call the strategy?")
            self.TheTrade.Strategy = response
        elif reply == 10 :
            pass
        elif reply > -1 and reply < len(self.strats):
            self.TheTrade.Strategy=self.strats[reply]
        else :
            print("WTF?  reply out of bounds. 'reply' = {0}".format( reply))
            raise ValueError
        
    def _getShares(self):
        if self.shares == 0 :
            if self.side.startswith("B"):
                self.shares = self.df[frc.bal].max()
            else :
                self.shares = self.df[frc.bal].min()
        return self.shares
        
        
    def _setShares(self):
        self.TheTrade.Shares = "{0} shares".format(self._getShares())
        
    def _setMarketValue(self):
        mkt = self._getShares() * self.df.loc[self.ix0][frc.price]
        self.TheTrade.MktVal   = mkt

    def _setHeaders(self):
        self.TheTrade['EntriesHeader'] = "Entries"
        self.TheTrade['ExitsHeader'] = "Exits"
        self.TheTrade.TargHead = "Target"
        self.TheTrade.StopHead = "Stop"
        self.TheTrade.RRHead = "R:R"
        self.TheTrade.MaxHead = "Max Loss"

    
    
    def _setEntries(self):
        B=list()
        S=list()
        
        for i, row in self.df.iterrows() :
            if(row[frc.side]).startswith('B') :
                B.append(row[frc.price])
            else :
                S.append(row[frc.price])
    
        if len(B) > 5 :
            more = len(B) - 5
            self.TheTrade.Entries5 =  "Plus {} more.".format(more)
        for i, price in zip(range (len(B)), B) :
            col = "Entries" + str(i+1)
            self.TheTrade[col] = price
    

        if len(S) > 5 :
            more = len(S) - 5
            self.TheTrade.Exits5 =  "Plus {} more.".format(more)
        for i, price in zip(range (len(S)), S) :
            col = "Exits" + str(i+1)
            self.TheTrade[col] = price
    
    def _setTarget(self) :
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
        self.TheTrade.Target = target
        self.TheTrade.TargDiff = target - self.TheTrade.Entries1

    def _setStop(self) :
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
        self.TheTrade.StopLoss = stop
        self.TheTrade.SLDiff = stop - self.TheTrade.Entries1
    
    def _setMaxLoss(self):
        #TODO write some tests that check for unknown types in the SLDiff col. Then fix this to handle them.
        
        self.TheTrade.MaxLoss = self.TheTrade.SLDiff * self._getShares()

    def _getRiskReward(self):
        #Write some tests that check for unknown types and then handle them here
                
        self.TheTrade.RR = self.TheTrade.StopLoss / self.TheTrade.Target
        












