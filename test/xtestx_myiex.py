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

@creation_date: 2018-12-23
'''

import datetime as dt
import types
import unittest
import pandas as pd

from structjour.stock import myiex as iex
# import inspect
# from itertools import ifilter
# pylint: disable = C0103
# pylint: disable = R0914


def getPrevTuesWed(td):
    '''
    Utility method to get a probable market open day prior to td. The least likely
    closed days are Tuesday and Wednesday. This will occassionally return  a closed
    day but wtf.
    :params td: A Datetime object
    '''
    deltdays = 7
    if td.weekday() == 0:
        deltdays = 5
    elif td.weekday() < 3:
        deltdays = 0
    elif td.weekday() < 5:
        deltdays = 2
    else:
        deltdays = 4
    before = td - dt.timedelta(deltdays)
    return before


class TestMyiex(unittest.TestCase):
    '''Test functions in module myiex'''

    def test_getiex_intraday(self):
        now = dt.datetime.today()
        tomorrow= now + dt.timedelta(1)
        now=getPrevTuesWed(now)
        beginDay = dt.datetime(now.year, now.month, now.day, 9,29)
        endDay = dt.datetime(now.year, now.month, now.day, 16,1)
        
        dateArray = [(None, None),
                     (beginDay, None),
                     (beginDay, endDay)]
        for start, end in dateArray:
            x, df, noma = iex.getiex_intraday('SQ', start=start, end=end)
            self.assertGreater(len(df), 0)


        # These dates should return no results
        dateArray = [(None, beginDay),
                     (endDay, None),
                     (tomorrow, None )]
        for start, end in dateArray:
            x, df, noma = iex.getiex_intraday('SQ', start=start, end=end)
            self.assertEqual(len(df), 0)

        # Test date formats
        startstamp = pd.Timestamp(beginDay)
        endstamp = pd.Timestamp(endDay)
        startstring = beginDay.strftime("%Y%m%d %H%M")
        endstring = endDay.strftime("%Y-%m-%d %H:%M")
        dateArray = [(startstamp, endstamp),
                     (startstring, endstring),
                     (startstamp, endstring),
                     (startstring, endstamp),
                     (startstamp, endstring)]

        for start, end in dateArray:
            lendf, df, noma = iex.getiex_intraday('SQ', start=start, end=end)
            self.assertGreater(len(df), 0)

    def test_getiex_intraday_interval(self):
        '''Test the candle intvarls by subtracting strings processed into times'''
        intervals = [2, 6, 60, 15]
        for interval in intervals:
            x, df, noma = iex.getiex_intraday("SQ", minutes=interval)

            min0 = df.index[0]
            min1 = df.index[1]
            delt = min1 - min0
            interval_actual = delt.seconds//60
            self.assertEqual(interval_actual, interval)

    def test_get_trading_chart(self):
        '''
        Test it returns value for stocks that exist and raises Exception
        for stocks that don't exist
        '''
        df = iex.get_trading_chart("AAPL")

        self.assertGreater(len(df), 0)

        self.assertRaises(Exception, iex.get_trading_chart, "SNOORK")

    def test_get_trading_chart_dates(self):
        '''Test that it correctly retrieves the right times and date as requested. Also the index should be a Timestamp'''
        b = getPrevTuesWed(dt.datetime.today())
        start = b.strftime("%Y%m%d 09:32")
        # start = "09:32"
        end = b.strftime("%Y%m%d 15:59")
        df = iex.get_trading_chart("SQ", start, end)

        start = pd.Timestamp(start)
        end = pd.Timestamp(end)
        startday = pd.Timestamp(start.strftime("%Y%m%d"))
        actualdate = pd.Timestamp(df.iloc[0]['date'])
        self.assertEqual(actualdate, startday)
        msg1 = f"Was the market open on at {start}"
        msg2 = f"Was the market open on between {start} at {end}"
        self.assertEqual(df.index[0], start, msg=msg1)
        self.assertEqual(df.index[-1], end, msg=msg2)

    def test_get_trading_chart_interval(self):
        '''Test the candle intvarls by subtracting strings processed into times'''
        intervals = [6, 60, 15, 9, 4]
        for interval in intervals:
            df = iex.get_trading_chart("SQ", minutes=interval)

            min0 = df.index[0]
            min1 = df.index[1]
            delt = min1-min0
            interval_actual = delt.seconds//60
            self.assertEqual(interval_actual, interval)

    def test_get_trading_chart_filt(self):
        df = iex.get_trading_chart("SQ", filt='default')
        msg=str(df.columns)
        self.assertEqual(len(df.columns), 5, msg)
        self.assertTrue('open' in df.columns)
        self.assertTrue('high' in df.columns)
        self.assertTrue('low' in df.columns)
        self.assertTrue('close' in df.columns)
        self.assertTrue('volume' in df.columns)

        df = iex.get_trading_chart("SQ", filt='open, marketOpen, average')
        self.assertEqual(len(df.columns), 3)
        self.assertTrue('open' in df.columns)
        self.assertTrue('marketOpen' in df.columns)
        self.assertTrue('average' in df.columns)

        df = iex.get_trading_chart("SQ")
        self.assertTrue('changeOverTime' in df.columns)

    def test_get_historical_chart(self):
        '''Test we got about 5 years of data within about 1 week leeway'''
        '''Test we got about 5 years of data within about 1 week leeway'''
        df = iex.get_historical_chart("AAPL")

        today = pd.Timestamp.today()
        firstd = df.index[0]
        delt = today - firstd

        self.assertGreater(delt.days, 1819, f'Should have retrieved 5 years of data. Received {delt.days} days')
        self.assertLess(delt.days, 1832, f'Should have retrieved 5 years of data. Received {delt.days} days')

        lastd = df.index[-1]
        delt = today-lastd

        # Assert we got data at least to 4 days ago (account for 4 day weekends etc)
        self.assertLess(delt.days, 4, f'Most recent date ({lastd}) was more than 4 days ago')

    def test_get_historical_chart_start(self):
        '''Checking the correct start and end dates given open market days for start and end'''
        #Test dates are all days the market was open
        dateArray = [(dt.datetime(2017, 3, 3), dt.datetime(2017, 11, 10)),
                    (dt.datetime(2016, 12, 27), dt.datetime(2017, 2, 3)),
                    (('2018-06-08 00:00:00'), ('2019-01-10 00:00:00'))]

        for start, end in dateArray:
            df = iex.get_historical_chart("TEAM", start, end)
            start= pd.Timestamp(start)
            end = pd.Timestamp(end)

            actualStart = df.index[0]
            actualEnd = df.index[-1]
            
            self.assertEqual(actualStart, start, f"Was the market open on {start}?")
            self.assertEqual(actualEnd, end, f"Was the market open on {end}?")

        #Test dates are all days the market was closed
        dateArray = [(dt.datetime(2017, 3, 5), dt.datetime(2017, 11, 5)),
                    (dt.datetime(2016, 12, 24), dt.datetime(2017, 2, 5)),
                    (('2018-06-10 00:00:00'), ('2019-01-13 00:00:00'))]

        for start, end in dateArray:
            df = iex.get_historical_chart("TEAM", start, end)
            start= pd.Timestamp(start)
            end = pd.Timestamp(end)

            astart = df.index[0]
            aend = df.index[-1]
            deltstart = astart - start if astart > start else start - astart
            deltend =   aend - end if aend > end else end - aend
            self.assertLess(deltstart.days, 4)
            self.assertLess(deltend.days, 4)

            self.assertNotEqual(actualStart, start)
            self.assertNotEqual(actualEnd, end)

def main():
    '''test discovery is not working in vscode. Use this for debugging. Then run cl python -m unittest discovery'''
    f = TestMyiex()
    for name in dir(f):
        if name.startswith('test'):
            attr = getattr(f, name)
            if isinstance(attr, type(f.test_get_trading_chart)):
                attr()

def notmain():
    f = TestMyiex()
    # f.test_get_trading_chart_filt()
    # f.test_getiex_intraday()
    f.test_getiex_intraday_interval()

if __name__ == '__main__':
    main()
    # notmain() 

    