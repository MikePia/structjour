'''
@author: Mike Petersen

@creation_date: 2018-12-23
'''

import datetime as dt
import random
import unittest
import pandas as pd
import types

from journal.stock import myib as ib
from journal.stock import utilities as util
# pylint: disable = C0103


class TestMyib(unittest.TestCase):
    '''
    Test methods and functions in the myib module
    This will currently retrive only market hours data. It will match the other APIs. But we 
    can and should accomodate after hours data even with API chooser.
    '''

    def test_ni(self):
        '''
        Test the function ni. The purpose of ni is to format the interval paramete correctly'''
        # print(ib.ni(13))
        tests = [(False, ('1 min', 1, 1)),
                 (False, ('2 mins', 2, 2)),
                 (False, ('3 mins', 3, 3)),
                 (True,  ('1 min', 1, 4)),
                 (False, ('5 mins', 5, 5)),
                 (True,  ('1 min', 1, 6)),
                 (True,  ('1 min', 1, 7)),
                 (True,  ('1 min', 1, 8)),
                 (True,  ('1 min', 1, 9)),
                 (False, ('10 mins', 10, 10)),
                 (True, ('1 min', 1, 11)),
                 (True, ('1 min', 1, 12)),
                 (True, ('1 min', 1, 13)),
                 (True, ('1 min', 1, 14)),
                 (False, ('15 mins', 15, 15)),
                 (True, ('1 min', 1, 16)), 
                 (False, ('20 mins', 20, 20)),
                 (True, ('1 min', 1, 21)),
                 (False, ('30 mins', 30, 30)),
                 (True, ('1 min', 1, 31)),
                 (False, ('1 hour', 60, 60)),
                 (True, ('1 min', 1, 180))]

        for x in tests:
            self.assertEqual(ib.ni(x[1][2]), x)

    def test_getib_intraday(self):
        '''
        This will provide time based failures on market holidays. If you are woking on a holiday,
        it serves you right :)
        '''
        msg = '''
            
            IB is not connected. To continue connect IB Gateway. 
            'test_getib_intraday cannont runMyib cannot run.
            '''
        if not ib.isConnected():
            msg = '''
            
            IB is not connected. To continue connect IB Gateway. 
            'test_getib_intraday cannont runMyib cannot run.
            '''
            print(msg)
            return

        self.assertTrue(ib.isConnected(), msg)

        biz = util.getLastWorkDay()
        bizMorn = dt.datetime(biz.year, biz.month, biz.day, 7, 0)
        bizAft = dt.datetime(biz.year, biz.month, biz.day, 16, 1)
        bef = util.getLastWorkDay(bizMorn - dt.timedelta(1))
        befAft = dt.datetime(bef.year, bef.month, bef.day, 16, 1)
        specificStart = dt.datetime(biz.year, biz.month, biz.day, 9, 37)
        specificEnd = dt.datetime(biz.year, biz.month, biz.day, 11, 37)
        longBef = util.getLastWorkDay(bizMorn - dt.timedelta(10))

        dateArray = [(bizMorn, bizAft),
                     (bizMorn, None),
                     (bef, befAft),
                     (specificStart, specificEnd),
                     (befAft, None),
                     (longBef, None),
                     (None, None)
                    ]

        for start, end in dateArray:
            minutes = random.randint(1,10)

            # Each of these should get results every time,beginning times are either before 9:31 or
            # between 9:30 (short days won't produce failures)
            l, df = ib.getib_intraday("SQ", start=start, end=end,
                                            minutes=minutes, showUrl=True)
            if l == 0:
                continue

            print("Requested...", start, end)
            print("Received ...", df.index[0], df.index[-1])
            print("     ", l)
            if not start:
                start = df.index[0]

            self.assertGreater(l, 0)
            delt = int((df.index[1] - df.index[0]).total_seconds()/60)
            self.assertEqual(delt, minutes)


            # If the requested start time is before 9:30, start should be 9:30
            d = df.index[0]
            expected = dt.datetime(d.year, d.month, d.day, 9, 30)

            # With resampled data, the alignment could be up to a candle interval away
            if start < expected:
                delt = expected - d if expected > d else d - expected
                self.assertLessEqual(delt.total_seconds(), minutes * 60)
            else:
                # The start should be within the amount of the candle length
                # if d != start:
                delt = pd.Timedelta(minutes=minutes)
                delt2 = d - start if d > start else start - d
                self.assertLessEqual(delt2, delt)


def notmain():
    '''Run some local code'''
    t = TestMyib()
    # t.test_ni()
    t.test_getib_intraday()

def main():
    '''
    test discovery is not working in vscode. Use this for debugging. Then run cl python -m unittest
    discovery
    '''
    f = TestMyib()
    for name in dir(f):
        if name.startswith('test'):
            attr = getattr(f, name)
            if isinstance(attr, types.MethodType):
                attr()


if __name__ == '__main__':
    # notmain()
    main()
