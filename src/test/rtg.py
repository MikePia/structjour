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
Random Trade Generator to for testing

@created_on Mar 31, 2019

@author: Mike Petersen
'''


import math
from math import isclose
import random
from unittest import TestCase

import pandas as pd

# pylint: disable = C0103

def getSide(firsttrade=False):
    '''
    Get a random distribution of 'B', 'S', 'HOLD+', 'HOLD-'. Set the probabilities here.
    HOLDs provide the weirdest exceptions. They should be relatively likely for tests.
    '''
    s = random.random()
    if firsttrade:
        side = 'B'if s < .30 else 'S' if s < .6 else 'HOLD+B' if s < .8 else 'HOLD-B'
    else:
        side = 'B'if s < .35 else 'S' if s < .7 else 'HOLD+' if s < .85 else 'HOLD-'
    return side

def getAccount():
    '''
    Get a randoms account real or sim
    '''
    real = 'U000000'
    sim = 'TRIB0000'
    percentReal = .75
    r = random.random()
    acct = real if r < percentReal else sim
    return acct

def getNumTrades(maxt=8):
    '''
    Return a number between 2 and 8 by default
    '''
    t = random.randint(2, maxt)
    return t

def getRandomFuture(earliest=pd.Timestamp('2019-01-01 09:30:00')):
    '''
    Get a time that is in the future a random amount of seconds from earliset
    '''
    rsec = random.randint(45, 1500)
    nextt = earliest + pd.Timedelta(seconds=rsec)
    return nextt

def getPL():
    '''
    Get a random dollar amount
    '''
    amnt = random.random()
    upordown = random.random()
    upordown = 1 if upordown > .4 else -1
    multiplier = random.randint(2, 200)
    return amnt * upordown * multiplier

def getTicker(exclude=None):
    '''
    Get a random ticker symbol
    '''
    tickers = ['SQ', 'AAPL', 'TSLA', 'ROKU', 'NVDA', 'NUGT', 'MSFT', 'CAG', 'ACRS', 'FRED', 'PCG',
               'AMD', 'GE', 'NIO', 'AMRN', 'FIVE', 'BABA', 'BPTH', 'Z', ]
    tick = tickers[random.randint(0, len(tickers)-1)]
    if exclude and tick in exclude:
        if not set(tickers).difference(set(exclude)):
            # We could make up some random letters here if this ever ....-- or include more
            raise ValueError("You have excluded every stock in the method")
        return getTicker(exclude=exclude)
    return tick

def floatValue(test, includezero=False):
    try:
        addme = float(test)
    except ValueError:
        return False, 0
    if math.isnan(addme):
        return False, 0
    if not includezero and addme == 0:
        return False, 0
    return True, addme

def randomTradeGenerator2(tnum, earliest=pd.Timestamp('2019-01-01 09:30:00'),
                          pdbool=False, exclude=None):
    '''
    Creates a list of transacations to make up a trade. Uses columns for tradenum, start, time,
    side, qty and balance. The PL is not worked out to coincide with shares or price; will work
    that out after working out how IB handles PL, qty and split transactions for flipped positions.
    Each trade ends with a 0 balance. Side can be one of 'S', 'B', 'HOLD+', 'HOLD-','HOLD+B',
    'HOLD-B', The HOLD{-,+} afters have 0 qty/bal, HOLD{-,+}B befores are openers so have no PL.
    There are ways this can create impossible trades if you aggregated these. Specifically
    stocks of the same Symb/Account that have trades with overlapping times will sort as a single.
    This cannont happen from one broker in reality. Before HOLDs can mess up by sorting to give
    consecutive HOLDSxB with messed up balances. To prevent problems add each stock in the
    generated statement to exclude parameter. (have not implemented Symb/Accnt combo).

    :parmas tnum: Number used for TradeX the trade number index
    :params earliest: Transaction progress in time with earliest as the easliest possible trade
                       except for before HOLDs.
    :params pdbool: Setting to True will cause the return to be a DataFrame instead of an array.
    :params exclude: A list of symbols to exclude as candidates for this trade
    :return pd.DataFrame:  DataFrame or list of transactions making up a single trade.
    '''
    tradenum = 'Trade {}'.format(tnum)
    earliest = pd.Timestamp(earliest)
    latest = earliest
    start = earliest
    nowtime = start
    numTrades = getNumTrades(maxt=10)
    trade = list()
    prevBal = 0
    long = True
    theSum = None
    duration = ''
    sumtotal = 0
    account = getAccount()
    # account = 'U000000'
    ticker = getTicker(exclude=exclude)

    twoholds = True
    for i in range(numTrades):
        firsttrade = True if i == 0 else False
        nexttime = getRandomFuture(nowtime)
        latest = nexttime
        pl = 0
        side = getSide(firsttrade=firsttrade)
        if firsttrade:
            if side == 'S' or side.find('-') >= 0:
                long = False
            if side.startswith('HOLD'):
                n = nowtime
                nowtime = pd.Timestamp(n.year, n.month, n.day, 0, 0, 1)
                start = nexttime
        # Prevent a trade to consist only of two HOLDs with no transaction
        elif twoholds:
            if side.startswith('HOLD'):
                side = 'S' if side.find('-') > -1 else 'B'
            twoholds = False
        if long and side == 'S':
            pl = getPL()
        elif not long and side == 'B':
            pl = getPL()

        if side.startswith('HOLD') and not firsttrade:
            n = nowtime
            nowtime = pd.Timestamp(n.year, n.month, n.day, 23, 59, 59)
            if i == 0:
                qty = random.randint(1, 500)
                if side == 'HOLD-':
                    qty = -qty
                start = nexttime
                trade.append([tradenum, start, nowtime, ticker, side+'B', qty, qty,
                              account, pl, theSum, duration])
                sumtotal = sumtotal + pl
                prevBal = qty
            else:
                qty = -qty if side == 'S' else qty
                trade.append([tradenum, start, nowtime, ticker, side, 0, 0,
                              account, pl, theSum, duration])
                sumtotal = sumtotal + pl
                prevBal = 0
                # nowtime = nexttime
                break
        elif i == numTrades -1:
            side = 'S' if prevBal >= 0 else 'B'
            pl = getPL() # if not side.startswith('HOLD') else 0
            trade.append([tradenum, start, nowtime, ticker, side, -prevBal, 0,
                          account, pl, theSum, duration])
            sumtotal = sumtotal + pl
            prevBal = 0
            break
        else:

            qty = random.randint(1, 500)
            qty = -qty if (side == 'S' or side == 'HOLD-B') else qty

            trade.append([tradenum, start, nowtime, ticker, side, qty, prevBal+qty,
                          account, pl, theSum, duration])
            sumtotal = sumtotal + pl
            prevBal = prevBal+qty
            if prevBal == 0:
                #We are coincidentally at 0 balance. Trade is over. Must be a hotkey mistake ;-)
                # print(':::::::::: Trade over. Random hot key error :::::::')
                break

        nowtime = nexttime
    duration = nowtime - start
    trade[-1][10] = duration
    trade[-1][9] = sumtotal
    if pdbool:
        trade = pd.DataFrame(data=trade, columns=['Tindex', 'Start', 'Time', 'Symb', 'Side', 'Qty',
                                                  'Balance', 'Account', 'P / L', 'Sum', 'Duration'])
        if not isclose(trade['P / L'].sum(), trade.loc[trade.index[-1]].Sum, abs_tol=1e-7):
            print(trade['P / L'].sum(), ' != ', trade.loc[trade.index[-1]].Sum)
            print()
        
    return trade, latest

class Test_RandomTradeGen(TestCase):
    '''
    Run all of structjour with a collection of input files and test the outcome. These
    are tests of a utility for testing. Not part of the main testing suite. Some of the other
    tests will run similar code with these tests.
    '''

    def __init__(self, *args, **kwargs):
        super(Test_RandomTradeGen, self).__init__(*args, **kwargs)

    def test_randomTradeGenerator(self):
        '''
        Test the randomtradeGenerator. Demonstrates how to aggregate trades and tests the output.
        Specifically test that each trade increments Time forward and ends with a 0 balance.
        :Usage: To conglomerate trades use the exclude parameter and reset the index of the
        conglomerated file. EVentually alter this and test the dates to limits and multiple days
        '''
        earliest = pd.Timestamp('2018-06-06 09:30:00')
        delt = pd.Timedelta(minutes=1)
        df = pd.DataFrame()
        exclude = []
        numTrades = 4     # Number of trades to aggregate into single statement
        for i in range(numTrades):
            tdf, earliest = randomTradeGenerator2(i+1, earliest=earliest,
                                                  pdbool=True, exclude=exclude)
            exclude.append(tdf.iloc[0].Symb)
            df = df.append(tdf)
            earliest = earliest + delt
            lastd = None
            thisd = None
            xl = tdf.index[-1]
            for j, row in tdf.iterrows():
                if j != xl:
                    self.assertNotEqual(tdf.at[j, 'Balance'], 0)
                else:
                    self.assertEqual(tdf.at[j, 'Balance'], 0)
                thisd = row.Time
                if lastd:
                    if lastd > thisd:
                        print(thisd, lastd, thisd-lastd, thisd > lastd)
                        print('SSSSSTTTTTOOOOOPPPPP NNNNNOOOOOWWWWWW ')
                        print(df)
                        self.assertGreater(thisd, lastd)

                lastd = thisd

            # df.reset_index(drop=True, inplace=True)
            # df = df.sort_values(['Symb', 'Account', 'Time'])
            # print(df)




def notmain():
    '''Run some local code'''
    for i in range(5000):
        randomTradeGenerator2(5, pdbool=True)

if __name__ == '__main__':
    notmain()
