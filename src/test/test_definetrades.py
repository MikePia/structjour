'''
Test the methods in the module journal.definetrades

@created_on Feb 18, 2019

@author: Mike Petersen
'''
import os
import random
import types
from unittest import TestCase

import numpy as np
import pandas as pd

from journal.dfutil import DataFrameUtil
from journal.definetrades import DefineTrades, FinReqCol, ReqCol

# pylint: disable = C0103


def getSide():
    '''
    Get a random distribution of 'B', 'S', 'HOLD+', 'HOLD-'
    '''
    s = random.random()
    side = 'B'if s < .45 else 'S' if s < .9 else 'HOLD+' if s < .95 else 'HOLD-'
    return side

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

def getTicker():
    '''
    Get a random ticker symbol
    '''
    tickers = ['SQ', 'AAPL', 'TSLA', 'ROKU', 'NVDA', 'NUGT',
               'MSFT', 'CAG', 'ACRS', 'FRED']
    return tickers[random.randint(0,9)]


def randomTradeGenerator(tnum, earliest=pd.Timestamp('2019-01-01 09:30:00')):
    '''
    Creates a list of transacations to make up a trade. Uses columns for tradenum, start, time,
    side, qty and balance. The PL is not worked out to coincide with shares or price. Used to 
    test the mechanics of DefineTrades class.
    Each trade ends with a 0 balance. Side can be one of 'S', 'B', 'HOLD+', 'HOLD-','HOLD+B',
    'HOLD-B', The before holds are no different than 'B' or 'S'. The HOLDx afters have 0 qty
    and bal.
    :return list: Transactions making up a single trade as a list. [[start,time, side, qty, bal]]
    '''
    tradenum = 'Trade {}'.format(tnum)
    start = earliest
    nowtime = start
    numTrades = getNumTrades(maxt=10)
    trade = list()
    prevBal = 0
    long = True
    theSum = None
    duration = ''
    sumtotal = 0
    # account = getAccount()
    account = 'U000000'
    ticker = getTicker()

    for i in range(numTrades):
        nexttime = getRandomFuture(nowtime)
        pl = 0
        side = getSide()
        if i == 0:
            if side == 'S' or side.find('-') >= 0:
                long = False
        if long and side == 'S':
            pl = getPL()
        elif not long and side == 'B':
            pl = getPL()

        if side.startswith('HOLD'):
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
                trade.append([tradenum, start, nowtime, ticker, side, 0, 0, account, pl, theSum, duration])
                sumtotal = sumtotal + pl
                prevBal = 0
                break
        elif i == numTrades -1:
            side = 'S' if prevBal >= 0 else 'B'
            trade.append([tradenum, start, nowtime, ticker, side, -prevBal, 0,
                          account, pl, theSum, duration])
            sumtotal = sumtotal + pl
            prevBal = 0
            break
        else:

            qty = random.randint(1, 500)
            qty = -qty if side == 'S' else qty
            trade.append([tradenum, start, nowtime, ticker, side, qty, prevBal+qty,
                          account, pl, theSum, duration])
            sumtotal = sumtotal + pl
            prevBal = prevBal+qty

        nowtime = nexttime
    duration = nowtime - start
    trade[-1][10] = duration
    trade[-1][9] = sumtotal
    return trade



class TestDefineTrades(TestCase):
    '''
    Run all of structjour with a collection of input files and test the outcome
    '''

    def __init__(self, *args, **kwargs):
        super(TestDefineTrades, self).__init__(*args, **kwargs)

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def test_addFinReqCol(self):
        '''
        Test the method journal.definetrades.DefineTrades.addFinReqCol
        '''
        rc = ReqCol()
        frc = FinReqCol()

        df = pd.DataFrame(np.random.randint(0, 1000, size=(10, len(rc.columns))),
                          columns=rc.columns)
        dtrades = DefineTrades()
        df = dtrades.addFinReqCol(df)
        for x in frc.columns:
            self.assertIn(x, df.columns)
        self.assertGreaterEqual(len(df.columns), len(frc.columns))

    def test_writeShareBalance(self):
        '''
        Test the method writeShareBalance. Send some randomly generated trades side and qty and
        test the share balance that returns
        '''

        trades = list()
        for i in range(10):
            t = randomTradeGenerator(i+1)
            trades.extend(t)
            # print(len(trades))
            # print (t)

        frc = FinReqCol()
        df = pd.DataFrame(data=trades, columns=[frc.tix, frc.start, frc.time, frc.ticker, frc.side, frc.shares,
                                                frc.bal, frc.acct, frc.PL, frc.sum, frc.dur])
        df2 = df.copy()
        df2[frc.bal] = None
        dtrades = DefineTrades()
        df3 = dtrades.writeShareBalance(df2)
        for i in range(len(df3)):
            self.assertEqual(df3.iloc[i][frc.bal], df.iloc[i][frc.bal])
            # print('{:-20}     {}'.format(df3.iloc[i][frc.bal], df.iloc[i][frc.bal]))


    def test_addStartTime(self):
        '''
        Test the method DefineTrades.addStartTime. Send some randomly generated trades excluding
        the start field and then test the results for the start field.
        '''
        trades = list()
        start = pd.Timestamp('2019-01-01 09:30:00')
        for i in range(4):
            t = randomTradeGenerator(i+1, earliest=start)
            trades.extend(t)
            start = getRandomFuture(start)
            # print(len(trades))
            # for tt in t:
            #     print(tt[0], tt[1],tt[2], tt[3])

        frc = FinReqCol()
        df = pd.DataFrame(data=trades, columns=[frc.tix, frc.start, frc.time, frc.ticker, frc.side, frc.shares,
                                                frc.bal, frc.acct, frc.PL, frc.sum, frc.dur])
        df2 = df.copy()
        df2[frc.start] = None
        dtrades = DefineTrades()
        df3 = dtrades.addStartTime(df2)
        for i in range(len(df3)):
            # if df3.iloc[i][frc.start] != df.iloc[i][frc.start]:
            if df3.iloc[i][frc.start] != df.iloc[i][frc.start]:
                print(df3)
                print(df)
                # print(':::::::::; HERE IS ONE ::::::"')
            # print(df3.iloc[i][frc.tix], df3.iloc[i][frc.start], '-----   :   ----',
            # df.iloc[i][frc.tix], df.iloc[i][frc.start])
            self.assertEqual(df3.iloc[i][frc.start], df.iloc[i][frc.start])
            # print('{}                  {}'.format(df3.iloc[i][frc.start], df.iloc[i][frc.start]))



    def test_addTradeIndex(self):
        '''
        Test the method writeShareBalance. Send some randomly generated trades side and qty and
        test the share balance that returns
        '''

        trades = list()
        for i in range(10):
            t = randomTradeGenerator(i+1)
            trades.extend(t)
            # print(len(trades))
            # print (t)

        frc = FinReqCol()
        df = pd.DataFrame(data=trades, columns=[frc.tix, frc.start, frc.time, frc.ticker, frc.side, frc.shares,
                                                frc.bal, frc.acct, frc.PL, frc.sum, frc.dur])
        df2 = df.copy()
        df2[frc.tix] = ''
        dtrades = DefineTrades()
        df3 = dtrades.addTradeIndex(df2)
        for i in range(len(df3)):
            self.assertEqual(df3.iloc[i][frc.tix], df.iloc[i][frc.tix])
            # print((df3.iloc[i][frc.tix], df.iloc[i][frc.tix]))


    def test_addTradePL(self):
        '''
        Test the method DefineTrades.addStartTime. Send some randomly generated trades excluding
        the start field and then test the results for the start field.
        '''
        trades = list()
        start = pd.Timestamp('2019-01-01 09:30:00')
        for i in range(4):
            t = randomTradeGenerator(i+1, earliest=start)
            trades.extend(t)
            start = getRandomFuture(start)
            # print(len(trades))
            # for tt in t:
            #     print(tt[0], tt[4],tt[8], tt[9])

        frc = FinReqCol()
        df = pd.DataFrame(data=trades, columns=[frc.tix, frc.start, frc.time, frc.ticker, frc.side, frc.shares,
                                                frc.bal, frc.acct, frc.PL, frc.sum, frc.dur])
        df.fillna(value=0.0, inplace=True)
        df2 = df.copy()
        df2[frc.sum] = 0.0
        dtrades = DefineTrades()
        df3 = dtrades.addTradePL(df2)

        for i in range(len(df3)):
            # print(df.iloc[i][frc.sum], '------>  <-------',  df3.iloc[i][frc.sum] )
            msg = '{} is not {}'.format(df.iloc[i][frc.sum], df3.iloc[i][frc.sum])
            self.assertAlmostEqual(df.iloc[i][frc.sum],  df3.iloc[i][frc.sum], msg)


    def test_addTradeDuration(self):
        '''
        Test the method DefineTrades.addStartTime. Send some randomly generated trades excluding
        the start field and then test the results for the start field.
        '''
        trades = list()
        start = pd.Timestamp('2019-01-01 09:30:00')
        for i in range(4):
            t = randomTradeGenerator(i+1, earliest=start)
            trades.extend(t)
            start = getRandomFuture(start)
            # print(len(trades))
            # for tt in t:
            #     print(tt[0], tt[1],tt[2], tt[8])

        frc = FinReqCol()
        df = pd.DataFrame(data=trades, columns=[frc.tix, frc.start, frc.time, frc.ticker, frc.side, frc.shares,
                                                frc.bal, frc.acct, frc.PL, frc.sum, frc.dur])
        df2 = df.copy()
        df2[frc.start] = None
        dtrades = DefineTrades()
        df3 = dtrades.addStartTime(df2)
        for i in range(len(df3)):
            if pd.isnull(df.iloc[i][frc.dur]):
                self.assertTrue(pd.isnull(df3.iloc[i][frc.dur]))
            else:
                self.assertEqual(df3.iloc[i][frc.dur], df.iloc[i][frc.dur])

    def test_addSummaryPL(self):
        '''
        Test the method DefineTrades.addStartTime. Send some randomly generated trades excluding
        the start field and then test the results for the start field.
        '''
        trades = list()
        start = pd.Timestamp('2019-01-01 09:30:00')
        for i in range(4):
            t = randomTradeGenerator(i+1, earliest=start)
            trades.extend(t)
            start = getRandomFuture(start)
            # print(len(trades))
            # for tt in t:
            #     print(tt[0], tt[3],tt[6])


        frc = FinReqCol()
        df = pd.DataFrame(data=trades, columns=[frc.tix, frc.start, frc.time, frc.ticker, frc.side, frc.shares,
                                                frc.bal, frc.acct, frc.PL, frc.sum, frc.dur])
        summaryPL = df[frc.PL].sum()

        df2 = df.copy()
        df2[frc.start] = None
        dtrades = DefineTrades()
        df2 = DataFrameUtil.addRows(df2, 2)
        df3 = dtrades.addSummaryPL(df2)
        # print(summaryPL, df3.iloc[-1][frc.sum])

        self.assertAlmostEqual(summaryPL, df3.iloc[-1][frc.sum])
        self.assertAlmostEqual(summaryPL, df3.iloc[-2][frc.PL])

def notmain():
    '''Run some local code'''
    t = TestDefineTrades()
    # t.test_addStartTime()
    # t.test_addTradeIndex()
    # t.test_addTradeDuration()
    t.test_addTradePL()
    # t.test_addSummaryPL()


def main():
    '''
    Test discovery is not working in vscode. Use this for debugging.
    Then run cl python -m unittest discovery
    '''
    f = TestDefineTrades()
    for name in dir(f):
        if name.startswith('test'):
            attr = getattr(f, name)

            if isinstance(attr, types.MethodType):
                attr()

if __name__ == '__main__':
    # main()
    notmain()
