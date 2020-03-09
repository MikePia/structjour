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
@author: Mike Petersen

@creation_date: 2019-01-17
'''
import datetime as dt
import os
import random
import unittest

import pandas as pd

from structjour.stock import utilities as util
if util.checkForIbapi():
    from structjour.stock import myib as ib
from structjour.stock.graphstuff import FinPlot, dummyName
# from structjour.stock.apichooser import APIChooser
from PyQt5.QtCore import QSettings


# pylint: disable = C0103


def getTicker():
    '''
    Get a random ticker symbol
    '''
    tickers = ['SQ', 'AAPL', 'TSLA', 'ROKU', 'NVDA', 'NUGT',
               'MSFT', 'CAG', 'ACRS', 'WORK', 'NFLX', 'MU', 'AAPL']
    return tickers[random.randint(0, 12)]


class TestGraphstuff(unittest.TestCase):
    '''
    Test functions and methods in the graphstuff module
    '''

    def __init__(self, *args, **kwargs):
        super(TestGraphstuff, self).__init__(*args, **kwargs)
        self.apiset = QSettings('zero_substance/stockapi', 'structjour')

    def setUp(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def test_dummyName(self):
        '''
        Testing method dummyName in the graphstuff module. This is temporary- it will move.
        '''
        fp = FinPlot()
        tradenum = 3
        symbol = 'AAPL'
        begin = '2019-01-20 08:30'
        end = '2019-01-20 15:15'
        n = dummyName(fp, symbol, tradenum, begin, end)
        self.assertTrue(n.find(fp.api) > 0)
        self.assertTrue(n.find(symbol) > 0)
        self.assertTrue(n.endswith(fp.ftype))
        self.assertTrue(n.find(fp.base) > 0,
                        "Check that outdir was sent to dummyName")

        # pylint: disable = W0104
        try:
            # Finding the assertRaises not reliable
            n = None
            tradenum = 'three'  # bad value
            n = dummyName(fp, symbol, tradenum, begin, end)
            self.assertTrue(n is None, 'Failed to raise ValueError')
        except ValueError:
            pass     # success

        try:
            n is None
            tradenum = 4
            begin = '1019091212:13'  # bad timestamp
            n = dummyName(fp, symbol, tradenum, begin, end)
            self.assertTrue(n is None, 'Failed to raise ValueError')
        except ValueError:
            pass

        try:
            n is None
            begin = '2019-01-20 08:30'
            end = '2019012015:15'  # bad timestamp
            n = dummyName(fp, symbol, tradenum, begin, end)
            self.assertTrue(n is None, 'Failed to raise ValueError')
        except ValueError:
            pass

    def makeupEntries(self, symbol, start, end, minutes, fp):
        if not ib.isConnected():
            # print()
            # print("ib gateway is not connected.")
            # print()
            return

        meta, df, maDict = ib.getib_intraday(symbol, start, end, minutes)
        entries = []
        exits = []
        for i in range(random.randint(2, 9)):
            if len(df) < 2:
                break
            candle = random.randint(0, len(df) - 1)
            high = df.iloc[candle].high
            low = df.iloc[candle].low
            entry = ((high - low) * random.random()) + low
            x = int(minutes * 60 * random.random())
            tix = df.index[candle]
            tix = tix + pd.Timedelta(seconds=x)

            if random.random() < .35:
                entries.append([entry, candle, minutes, tix])
            else:
                exits.append([entry, candle, minutes, tix])
        fp.entries = entries
        fp.exits = exits

    # # @unittest.skipUnless(util.checkForIbapi(), 'Requires ibapi to run')
    # def test_graph_candlestick(self):
    #     '''
    #     Test the FinPlot.graph_candlestick method. Currently requires ibapi and is too complex to
    #     be an effective test. Redo it
    #     '''
    #     fp = FinPlot()
    #     # fp.interactive = True
    #     fp.randomStyle = True

    #     # trades = [
    #     #     ['AAPL', 1, '2019-01-18 08:31', '2019-01-18 09:38', 1],
    #     #     ['AMD', 2, '2019-01-18 08:32', '2019-01-18 09:41', 1],
    #     #     ['NFLX', 3, '2019-01-18 09:39', '2019-01-18 09:46', 1],
    #     #     ['NFLX', 4, '2019-01-18 09:47', '2019-01-18 09:51', 1]]

    #     d = util.getPrevTuesWed(pd.Timestamp.now())
    #     # d = pd.Timestamp('2019-02-25')
    #     times = [['08:31', '09:38'],
    #              ['08:32', '09:41'],
    #              ['09:39', '12:46'],
    #              ['09:47', '13:51']]

    #     tickers = []
    #     for i in range(4):
    #         tickers.append(getTicker())

    #     trades = []
    #     for count, (tick, time) in enumerate(zip(tickers, times)):
    #         start = d.strftime('%Y-%m-%d ') + time[0]
    #         end = d.strftime('%Y-%m-%d ') + time[1]
    #         trades.append([tick, count + 1, start, end, 1])
    #         # print (trades[-1])
    #     for trade in trades:
    #         start, end = fp.setTimeFrame(trade[2], trade[3], trade[4])
    #         chooser = APIChooser(self.apiset)
    #         (dummy, rules, apilist) = chooser.apiChooserList(trade[2], trade[3])
    #         print(f'{apilist}/n{rules}')
    #         minutes = 2
    #         self.makeupEntries(trade[0], start, end, minutes, fp)
    #         chooser = APIChooser(self.apiset)

    #         name = fp.graph_candlestick(trade[0], chooser, start, end, minutes=minutes, save=dummyName(fp, ))
    #         cwd = os.getcwd()
    #         if name:

    #             msg = 'error creating ' + name + " IN ", cwd
    #             self.assertTrue(os.path.exists(name), msg)
    #         else:
    #             print('Failed to get data', fp.api)

    def test_setTimeFrame(self):
        '''
        setTimeFrame will require usage to figure out the right settings. Its purpose is to frame
        the chart with enough time before and after the transactions to give perspective to the
        trade. Ideally, it will include some intelligence with trending information and evaluation
        of the highs and lows within the day. The point here is this method is not done.
        '''
        fp = FinPlot()
        early = dt.datetime(2019, 1, 19, 0, 0)
        late = dt.datetime(2019, 1, 19, 23, 55)
        odate = dt.datetime(2019, 1, 19, 9, 40)
        cdate = dt.datetime(2019, 1, 19, 16, 30)
        opening = dt.datetime(2019, 1, 19, 9, 30)
        closing = dt.datetime(2019, 1, 19, 16, 00)
        interval = 1
        interval2 = 60
        # tests dependent on interval -- setting to 1
        for i in range(1, 10):
            begin1, end1 = fp.setTimeFrame(odate, cdate, interval)
            begin2, end2 = fp.setTimeFrame(odate, cdate, interval2)
            begin3, end3 = fp.setTimeFrame(early, late, interval)
            if odate < opening:
                self.assertEqual(begin1, opening)
                self.assertEqual(begin2, opening)
            else:
                delt = odate - begin1
                delt2 = odate - begin2
                self.assertLess(delt.seconds, 3600)
                self.assertLess(delt2.seconds, 3600 * 3.51)
            if early < opening:
                self.assertEqual(begin3, opening)
            if late > closing:
                self.assertEqual(end3, closing)
            mins = 40
            odate = odate + dt.timedelta(0, mins * 60)
            cdate = cdate - dt.timedelta(0, mins * 60)
            early = early + dt.timedelta(0, mins * 60)
            late = late - dt.timedelta(0, mins * 60)


def main():
    '''
    test discovery is not working in vscode. Use this for debugging. Then run cl python -m unittest
    discovery
    '''
    unittest.main()
    # f = TestGraphstuff()
    # for name in dir(f):
    #     if name.startswith('test'):
    #         attr = getattr(f, name)
    #         if isinstance(attr, types.MethodType):
    #             attr()


def notmain():
    '''
    Local run stuff for dev
    '''
    t = TestGraphstuff()
    t.test_apiChooser()
    # t.test_dummyName()
    # t.test_graph_candlestick()
    # print(getLastWorkDay(dt.datetime(2019, 1, 22)))
    # t.test_setTimeFrame()


if __name__ == '__main__':
    # notmain()
    main()
