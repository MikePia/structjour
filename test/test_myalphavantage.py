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
Test code for myalphavantage module.
@author: Mike Petersen
@creation_date: 1/15/19
'''
import datetime as dt
import unittest
from time import time, sleep

import pandas as pd

from structjour.stock import myalphavantage as mav
from structjour.stock import utilities as util


class TestMyalphavantage(unittest.TestCase):
    '''Test methods and functions from the modulemyalphavantage'''

    def test_getmav_intraday(self, count=None):
        '''
        This will provide time based failures on market holidays. If you are woking on a holiday,
        it serves you right :)
        '''
        if count is None:
            count = [0]
        # It seems alphavantage no longer provides realtime quotes for free. Coverage for todya (8/24/20)
        # started sometime between 6-10:30 eastern
        # They seem to provide quotes from the previous day to the the previous week
        yesterday = dt.datetime.today() - dt.timedelta(1)
        biz = util.getLastWorkDay(yesterday)
        bizMorn = dt.datetime(biz.year, biz.month, biz.day, 7, 0)
        bizAft = dt.datetime(biz.year, biz.month, biz.day, 16, 1)
        bef = util.getLastWorkDay(bizMorn - dt.timedelta(1))
        befAft = dt.datetime(bef.year, bef.month, bef.day, 16, 1)
        specificStart = dt.datetime(biz.year, biz.month, biz.day, 9, 37)
        specificEnd = dt.datetime(biz.year, biz.month, biz.day, 11, 37)
        longBef = util.getLastWorkDay(bizMorn - dt.timedelta(10))
        # longBefAft = dt.datetime(longBef.year, longBef.month, longBef.day, 16, 1)

        # dateArray = [(biz, bizAft), (biz, None), (None, bizAft) ]
        minutes = 2

        dateArray = [
                    (bizMorn, bizAft),
                     (bizMorn, None),
                     (bef, befAft),
                     (specificStart, specificEnd),
                     (befAft, None),
                     (longBef, None)]
        # dateArray2 = [(bizAft, None)]
        # now = pd.Timestamp.today()

        # Prevent more than 5 calls per minute, sleep after 5 for the remainder
        nextt = time() + 80
        for start, end in dateArray:

            # Each of these should get results every time,beginning times are either before 9:31 or
            # between 9:30 (short days won't produce failures)
            dummy, df, maDict = mav.getmav_intraday("SQ", start=start, end=end,
                                            minutes=minutes, showUrl=True, key=None)

            # print("Requested...", start, end)
            # print("Received ...", df.index[0], df.index[-1])
            # print("     ", len(df))
            if df is None:
                continue
            self.assertGreater(len(df), 0, f'Failed witha args {start} and {end}')

            if not start and not end:
                # This will retrieve the full set available. It should cover 5 days data. 
                #  We will just test that the results cover 4 days and ends on the last biz day.
                # We are at the mercy of AV-- if they change, this should fail. (that's good)
                # !!! They did change and are not advertising what the new rules are
                lt = df.index[-1]
                self.assertGreater((lt - df.index[0]).days, 3)
                lastDay = dt.datetime(lt.year, lt.month, lt.day)
                bizDay = pd.Timestamp(biz.year, biz.month, biz.day)
                # TODO: Figure out what the new service is and make a more precise test. Specifically, when do they
                # start returning todays stuff?
                # self.assertEqual(lastDay, bizDay)
                start = df.index[0]

            # If the requested start time is before 9:31, start should be 9:31
            d = df.index[0]
            expected = dt.datetime(d.year, d.month, d.day, 9, 30)
            if start < expected:
                self.assertEqual(d, expected)
            else:
                # The start should be within the amount of the candle length
                # if d != start:
                delt = pd.Timedelta(minutes=minutes)
                delt2 = d - start if d > start else start - d
                self.assertLessEqual(delt2, delt)

            # Could add some tests for what happens when request is for today during market hours

            if count[0] % 5 == 4:
                # After 5 calls, sleep. 5 calls per minute is the max for the free API
                newnextt = nextt - time()
                nx = max(int(newnextt), 80)
                print(f'''Waiting for {nx} seconds. 5 calls per minute max
                       from AVantage free API''')
                if newnextt < 0:
                    # It took a minute plus to get through those 5 calls- reset for the next 5
                    nextt = time() + 80
                    count[0] += 1
                    continue
                nextt = newnextt
                sleep(nextt)

            count[0] += 1

    def test_ni(self):
        '''
        Test the utility for mav
        '''
        results = [
            (True, ('1min', 1, 3)),
            (True, ('30min', 30, 45)),
            (True, ('60min', 60, 112)),
            (True, ('5min', 5, 11)),
            (False, ('1min', 1, 1)),
            (False, ('30min', 30, 30)),
        ]
        for r in results:
            res = mav.ni(r[1][2])
            self.assertEqual(res, r)

        res = mav.ni(-42)
        self.assertEqual(res, (False, ('1min', 1, 1)))

        res = mav.ni(450)
        self.assertEqual(res, (False, ('60min', 60, 60)))


def main():
    '''test discovery is not working in vscode. Use this for debugging. Then run cl python -m unittest discovery'''
    unittest.main()

def notmain():
    '''Run some local code for dev'''
    m = TestMyalphavantage()
    m.test_getmav_intraday()
    
    # count = [0]
    # for i in range(40):
    #     print('==================', i, '===================')
    #     m.test_getmav_intraday(count)
    # # m.test_ni()


if __name__ == '__main__':
    notmain()
    # main()
