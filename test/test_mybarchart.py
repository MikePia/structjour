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

@creation_date: 2019-01-14
'''

import datetime as dt
import unittest
import pandas as pd

from structjour.stock import mybarchart as bc
from structjour.stock import utilities as util
# import inspect
# from itertools import ifilter
# pylint: disable = C0103
# pylint: disable = R0914
# pylint: disable = C0111


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


class TestMybarchart(unittest.TestCase):
    '''
    Test functions in module bybarchart
    '''

    def test_getbc_intraday(self):
        '''
        This API will not retrieve todays data until 15 minutes after close. It may not retrieve
        all of yesterday till after close today
        '''

        # def test_getbc_intraday(self):
        now = dt.datetime.today()
        nowbiz = util.getLastWorkDay()          # We want to retrieve a day with data for testing here
        bizclose = pd.Timestamp(nowbiz.year, nowbiz.month, nowbiz.day, 16, 0)
        tomorrow = now + dt.timedelta(1)
        y = now - dt.timedelta(1)
        ymorn = dt.datetime(y.year, y.month, y.day, 7, 30)
        yaft = dt.datetime(y.year, y.month, y.day, 17, 30)
        ymorn = getPrevTuesWed(ymorn)
        yaft = getPrevTuesWed(yaft)
        beginDay = dt.datetime(now.year, now.month, now.day, 9, 30)
        endDay = dt.datetime(now.year, now.month, now.day, 16, 0)

        # These should all retrieve the same data. unless the day is today before 4:30. No start
        # date and today trigger a 1day query
        # for the most current biz day (which may be yesterday if its before 16:30 on Tuesday)
        dateArray = [(None, None),
                     (beginDay, None),
                     (None, endDay),
                     (beginDay, endDay),
                     (None, tomorrow),
                     (ymorn, yaft),
                     (None, yaft),
                     (ymorn, None)]  # Same as both None

        dateArray2 = [(ymorn, None), (ymorn, yaft)]

        # These should retrive 0 results with no Exception
        dateArray3 = [(None, yaft), (tomorrow, None)]

        # edays=list()
        interval = 5
        for start, end in dateArray:
            x, df, maList = bc.getbc_intraday('SQ', start=start, end=end, showUrl=True)
            if x['code'] == 666:
                print('Abandon all hope of retrieving barchart data today.\n',
                      'You have run out of free queries until midnight')
                return

            if not start or start.date() == now.date():
                # Retrieveing todays will retrieve butkis until the magictime
                mt = util.getLastWorkDay()

                # 4:45 EST = 2:45 MST
                magictime = pd.Timestamp(mt.year, mt.month, mt.day, 14, 45)
                if now < magictime:
                    msg = 'This query should be empty because barchart does not retrieve todays'
                    msg += 'data till after close. If its not empty, either we are in the cracks.'
                    msg += '(wait a minute), or something is wrong (probably with the code).'
                    self.assertTrue(df.empty, msg)
                    continue

            else:
                self.assertGreater(len(df), 0)

            # Given start == None, barchart returns data from previous weekday (holidays ignored)
            now = pd.Timestamp.today()
            if not start and not df.empty:
                start = df.index[0]

                if now.isoweekday() > 5:
                    self.assertLess(df.index[0].isoweekday(), 6, "Is it a holiday? Go party now!")
            if not start:
                start = now
            if start and end and start > end or start > bizclose:
                assert df.empty
                continue

            s = pd.Timestamp(start.year, start.month, start.day, 9, 29)
            e = pd.Timestamp(start.year, start.month, start.day, 16, 1)
            if start > s and start < e:
                self.assertEqual(df.index[0], start)

            msg = f'\nInput: {end} \nTest:  <> {e} \nIndex{df.index[-1]}'
            # print(msg)
            # Very internal noodly but barchart last index is always the next to the last time aka end - interval
            if end and end > s and end < e:
                # end2 = end - pd.Timedelta(minutes=interval)
                msg = f'\nInput: {end} \nTest:  {e} \nIndex: {df.index[-1]}'
                delt = df.index[-1] - end if df.index[-1] > end else end - df.index[-1]

                self.assertLessEqual(int(delt.total_seconds()), interval * 60)
                # self.assertEqual(df.index[-1], end2, msg)

        for start, end in dateArray2:
            x, df, maList = bc.getbc_intraday('SQ', start=start, end=end)
            self.assertGreater(len(df), 0)

        for start, end in dateArray3:
            x, df, maList = bc.getbc_intraday('SQ', start=start, end=end)
            # print(df)
            # print(len(df.index))
            print(x['message'])
            self.assertEqual(len(df), 0)

    def test_getbc_intraday_interval(self):
        '''Test the candle intvarls by subtracting strings processed into times'''
        intervals = [2, 6, 60, 15]
        start = getPrevTuesWed(pd.Timestamp.today().date())
        for interval in intervals:
            dummy, df, maList = bc.getbc_intraday("SQ", start=start, minutes=interval)
            if len(df) < 1:
                print('Failed to retrieve data from barchart:', start)
                continue

            # of a time string ---
            min0 = df.index[0]
            min1 = df.index[1]

            self.assertEqual((min1 - min0).total_seconds(), interval * 60)


def main():
    # not_main()
    unittest.main()


def notmain():
    '''Run some local stuff'''
    f = TestMybarchart()
    # f.test_getbc_intraday()
    f.test_getbc_intraday_interval()
    # f.test_getbc_intraday_interval()


if __name__ == '__main__':
    main()
    # notmain()
