'''
Created on Oct 31, 2018

@author: Mike Petersen
'''

class TheStrategyObject(object):
    '''
    Handle information about trade strategies
    '''


    def __init__(self, newStrats = None, replace=False, LongShort=0):
        '''
        Constructor
        '''
        self.db = False
        stratlist = [['ORBU', 'ORBD'], 
                        ['ABCD', 'Reverse ABCD'], 
                        ['Bull Flag', 'Bear Flag'], 
                        ['Fallen Angel'],
                        ['VWAP Support', 'VWAP Resistance']
                        ['VWAP Reversal'], 
                        ['VWAP False Breakout'],  
                        ['VWAP MA trend'], 
                        ['15 Minute Reversal'], 
                        ['booty'], 
                        ['Other'], 
                        ['Skip']]
        stratlist2 = ['booty']
        strats = dict()
        strats['ORBU'] = ['Opening Range Breakout', \
'''
1.  We need a stock in play. Watch the opening and find the 5 (or longer) minute 
    range. Notice the price action and volume and the ATR. The range should be 
    less than the ATR. The price shoud be close enough to VWAP, below for short, 
    above for long.
2.  At the break of the opening range, make the entrance (long or short). 
3.  Stop on a break to the other side of VWAP.
4.  Target the next important technical level. If there are none, look for 
    weakness like a new 5 minute low. 
''']

        strats['ABCD'] = ['ABCD', \
'''
1.  We need a stock in play that is surging up (from A) reaching a significant 
    new HOD (B). Watch to see if it goes higher or lower (Verify B level) 
2.  The stock consolodates at a lower level. Verify that it finds support at 
    a level between A and B, closer to B, that is level C. Use the 1 and 5
    minute charts to verify support at C.
3.  Enter the trade above C with an initial target (D) when it breaks B.
    The R:R should be favorable with an entrance closer to C than D. 
    (Alternately, the entrance is a breakout entrance above D.) 
    Take partial profit at D, move stop to B/E. (Aternately add more)
4.  Sell remainder at technical level target or sign of weakness.

''']

        strats['Bull Flag'] = ['Bull Flag', \
'''
This is essentially a low float ABCD but the strategy is not the same. It 
generally moves faster and requires more finnesse. Insist on more confirmation 
of the trend, specifically enter at the breakout point(at D) and only if the 
volume is increasing and R:R remains favorable. Get out while its still running.

1.  Stock is found surging from watchlist, tip or scanner. It must consolodate
    lower. Wait! Determine share size, entry, stop and exit strategy based on the
    point of support in consolodation its high point and higher targets.
2.  Entry is the break of its high in the Bull flag with INCREASING VOLUME. 
    Without increasing volume, this is not a Bull Flag strategy. Upward momentum
    must be found on both 1 and 5 minute charts. Perfect entry is the close of
    1 and 5 minute green candles. At this entry point, it is crucial to maintain 
    a favorable R:R based on price action.
3.  This is a momentum trade. Take some profit early. Any technical level is a 
    good opportunity. After taking profit, move stop loss to break even or better.
4.  Sell remainder at target or signs of weakness and sellers taking control. 
    Generally, consider getting out while its still running without trying to 
    get the top.
''']
        strats['VWAP Support'] = ['VWAP Support', \
'''
Andrew gives examples of this strategy but does not summarize it with concise
rules. Its more of a principle than an event. This principle is reliable, easy
to spot, and easy to determine a sensible stop, but it supplies no target. It 
can happen any time of the day but 10:15 to 11:30, when the institutional buyers 
and sellers first come to a consensus for the day, is a likely time.

1.  A stock approaches VWAP and bounces. Look for VWAP support to be verified by 
    two consecutive 5 minute candles. Many other alternative strong support patterns 
    may be found including multiple bounces, a strong decisive V pattern, or a 
    consolodation. Consider both a long and short entry after a consolodation.
    Also consider it may consolodate for the rest of the day.
2.  Enter at the end of the second 5 minute candle that verifies the VWAP support.
3.  The bounce and VWAP support suggest institutions and others have taken an 
    interest in this stock and the price action will move away from VWAP. The
    initiall move away from VWAP is reliable but the pattern does not suggest what 
    will happen next or how much price motion will occur. It could be a 6 cent 
    motion or the beginning of a whole point move. After moving, be wary of a 
    return to VWAP 4.  
4.  Determine the closest target, the likely strength of the move, a good R:R 
    based on a stop over the VWAP and the closest target. The stop could be a 5 
    minute close over the VWAP or 10 cents over the VWAP or a close technical 
    level over the VWAP.
'''

        strats['15 Minute Reversal'] = ['15 Minute Reversal', \
'''
1. We need a strong 15 minute trend that becomes very extended from VWAP.
2. The down trend needs to be followed by a 15 minute reversal candle.
3. The reversal needs a second 15 minute candle that breaks in the opposite direction.
4. There must be a coinciding 5 minute break
5. There must be a coinciding 1 minute ma crossing, usually the 9ma over the 20.
6. Choose one of the above to be entry with the crossing as final confirmation
7. Keep the stop tight. If it doesn't turn out its confirmed quickly. Huge RR. 1:4 or better.
''']
        strats['booty'] = ['Booty Reversal Breakout' , \
'''
A down to up reversal
1. Stock has sold off for a very long time. This is knife catching at its most cogent.
     Stock will have sold off for hours. Maybe bleeding for the whole day.
2. The down trend is interrupted by a White 15 minute candle.
3. The down trend is halted and a consolodiation begins.
     There may be a ceiling of resistance with higher lows (pennant looking thing) 
     There may be a failure to go lower over several candles.
4. The consolodation ends with a 15 minute breaking high and some increasing volume.
     Look for coinciding 5 minute high.
     You can enter at the 5 minute high(s) or the 15 minute high.
5. Look for the 1 minute crossing sometime during or after the 15 minute high. 
     This will provide volume and momentum as traders who trade the one minute strategy pile on.
     With the longer view, you benefit from traders with different time foci.
6. Use the 1 minute chart to place your stop. This trade has momentum built into it. If the momentum fails
     to happen, the short stop is probably correct. If the momentum does happen, ride to next resistance.
''']


        self.s1=stratlist
        self.s2=stratlist2
        self.strats=strats

    def getStrat(self, index,  long=0) :
        tso=TheStrategyObject()
        if len(tso.s1[index]) > 1:
            return tso.s1[index][long]
        else :
            return tso.s1[index][0]
    
    def getStratDesc(self, index):
        '''
        Retrieves the description of the strategy defined in 
        self.s1[index] if it exists.
        '''
        if self.getStrat(i, 0) in self.strats.keys() :
            return self.strats[self.getStrat(i,0)][1]
        else :
            return None

tso = TheStrategyObject()
for i in range (len(tso.s1)) :
    print(tso.getStrat(i,0))
    desc = tso.getStratDesc(i)
    if desc :
        print (tso.getStratDesc(i))
