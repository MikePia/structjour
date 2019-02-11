'''
Test the functions in module journal.time
Created on Feb 10, 2019

@author: Mike Petersen
'''
import unittest
import os
import datetime as dt

import pandas as pd

from journal.time import getFirstWeekday
# pylint: disable = C0103


class Test_time(unittest.TestCase):
    '''
    Test the functions in the module journal.time. Specifically test the noninteractive version for
    the return values'''

    def __init__(self, *args, **kwargs):
        super(Test_time, self).__init__(*args, **kwargs)

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def test_getFirstWeekday(self):
        '''Test the function time.getFirstWeekday.'''
        theDir = os.getcwd()
        theDate = pd.Timestamp('2019-06-15')
        test2019 = [[0, 0], [2, 1], [5, 1], [5, 1], [1, 1], [3, 1], [1, 3],
                    [1, 1], [4, 1], [1, 2], [2, 1], [5, 1], [1, 2]]

        for month in range(1, 13):
            theDate = dt.datetime(2019, month, 15)
            dd, theDir = getFirstWeekday(theMonth=theDate, theDir=theDir)
            self.assertEqual(dd.isoweekday(), test2019[month][0])
            self.assertEqual(dd.day, test2019[month][1])
            self.assertTrue(os.path.exists(theDir))
        throw = False
        try:
            getFirstWeekday("notadate", theDir)
        except ValueError:
            throw = True
        except Exception:
            pass
            # self.assertTrue(test2019[0][0] == 1, "Failed to throw a ValueError")
        finally:
            if not throw:
                self.assertTrue(test2019[0][0] == 1, "Failed to throw a ValueError")
def notmain():
    '''Run some local code'''
    t = Test_time()
    t.test_getFirstWeekday()


if __name__ == '__main__':
    notmain()
