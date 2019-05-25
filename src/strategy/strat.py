# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

'''
Created on Oct 31, 2018

@author: Mike Petersen
'''
# pylint: disable = C0103

class TheStrategyObject(object):
    '''
    Handle information about trade strategies
    '''

    def __init__(self, newStrats=None, replace=False, LongShort=0):
        '''
        Constructor
        '''
        self.db = False
        stratlist = [['ORBU', 'ORBD'],
                     ['ABCD', 'Reverse ABCD'],
                     ['Bull Flag', 'Bear Flag'],
                     ['Fallen Angel'],
                     ['VWAP Support', 'VWAP Resistance'],
                     ['VWAP Reversal'],
                     ['VWAP False Breakout'],
                     ['VWAP MA trend'],
                     ['Robert HTG'],
                     ['booty'],
                     ['Other'],
                     ['Skip'],
                     ['Hanging Man Reversal']]
        stratlist2 = ['booty']
        strats = dict()
        strats['ORBU'] = ['Opening Range Breakout',
                          '''
Opening range has been a 5 minute range. But there is a trend at BBT to consider
shorter ORBS. The 2 minute is getting popular. This seems to be in response to
evolving trading practices. In any case, 2, 5, 15 minute orbs are momentum plays.
This is not a trend setup. Partial out, generally, sooner rather than later. If
the stock is in a larger trend, those are not part of the ORB setup. Still, after
partialing, keep in mind to let winners run, consider a stop at break even or a
range stop if it looks like a trend is developing.
1.  We need a stock in play. Watch the opening and find the 5 (or 2, 10, 15, 30) minute
    range. Notice the price action and volume and the ATR. The range should be
    less than the ATR. The price shoud be close enough to VWAP, below for short,
    above for long.
2.  Enter At the break of the opening range (long or short) for breakout trade.
3.  Or enter at a pullback from opening range. This creates a tighter stop but lacks
    the breakout confirmation.
4.  Stop on a break to the other side of VWAP-- or, if its a breakout entry, stop
    some amount the other side the breakout. Or if its a pullback entry, treat it
    as ABCD and stop the other side of C. Know which stop strategy you are using.
5.  Target the next important technical level. If there are none, look for
    weakness like a new 5 minute low.
''']

        strats['ABCD'] = ['ABCD',
                          '''
1.  We need a stock in play that is surging up (from A) reaching a significant
    new HOD (B). Watch to see if it goes higher or lower (Verify B level)
2.  The stock consolodates at a lower level. Verify that it finds support at
    a level between A and B, closer to B, that is level C. Use the 1 and 5
    minute charts to verify support at C.
3.  Enter the trade above C with an initial target (D) when it breaks B.
    The R:R should be favorable with an entrance closer to C than D.
    (Alternately, the entrance is a breakout entrance above D.)
4.  Sell remainder at technical level target or sign of weakness.

''']

        strats['Bull Flag'] = ['Bull Flag',
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
        strats['VWAP Support'] = ['VWAP Support',
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
''']

        strats['Robert HTG'] = ['15 Minute Reversal',
                                '''1. Strong 15 minute down trend that becomes extended from VWAP.
2. 1 minute MA to cross the 9 & 20. Price action above all 3 MA's
3. 5 minute bullish candle with higher high
4. 15 Minute - no new low and higher high, a reversal looking candle
5. Also look for prie acction extended from VWAP and a daily support level.
''']
        strats['booty'] = ['Booty Reversal Breakout',
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
5. Look for the 1 minute crossing of the 9MA over the 20MA sometime during or after the 15
     minute high. This will provide volume and momentum as traders who trade the one minute
     strategy pile on. With the longer view, you benefit from traders with different time foci.
6. Use the 1 minute chart to place your stop. This trade has momentum built into it. If the
momentum fails to happen, the short stop is probably correct. If the momentum does happen, ride to
next resistance.
''']

        strats['Hanging Man Reversal'] = ['Hanging Man Reversal',
                                          '''
A hanging man candle is found at the top of a trend on the 5 or 15 minute chart. The The body is
thin- doji like. The lower wick needs to be three times the length of the upper wick. Careful,
because this can indicate indeision and requires other factors to be a reversal. Look for
Resistance from
            moving averages
            daily levels
            bigger  trend tendenies (eg hourly, daily)
            bigger MA trends (eg the 200).
This strategy provides a good R2R but has a strong probablilty of stopping you out. If you believe
it marks a reversal then this is the strategy:
1. Enter at the candle after the hanging man as soon as it opens or below the body.
2. Stop is (max) at the high of the hanging man. But if it gets that high, the trade is not going
    your way. A tighter stop is recommended, the high of the previous candle or a substantial break
    above the body of the hanging man.
3. Take no partials until it breaks the low of the Hanging Man.
4. On your own after that but Ride the winners, Cut the losers.
''']

        self.s1 = stratlist
        self.s2 = stratlist2
        self.strats = strats

    def getStrat(self, index,  long=0):
        tso = TheStrategyObject()
        if len(tso.s1[index]) > 1:
            return tso.s1[index][long]
        else:
            return tso.s1[index][0]

    def getStratDesc(self, i):
        '''
        Retrieves the description of the strategy defined in
        self.s1[index] if it exists.
        '''
        if self.getStrat(i, 0) in self.strats.keys():
            return self.strats[self.getStrat(i, 0)][1]
        else:
            return None


# tso = TheStrategyObject()
# for i in range(len(tso.s1)):
#     print(tso.getStrat(i, 0))
#     desc = tso.getStratDesc(i)
#     if desc:
#         print(tso.getStratDesc(i))
