'''
Test the functions in module journal.time
Created on Feb 10, 2019

@author: Mike Petersen
'''
import unittest
import os
import datetime as dt
from shutil import rmtree

import pandas as pd

from journal.time import getFirstWeekday, createDirs
# pylint: disable = C0103


class Test_time(unittest.TestCase):
    '''
    Test the functions in the module journal.time. Specifically test the noninteractive version for
    the return values
    '''

    def __init__(self, *args, **kwargs):
        super(Test_time, self).__init__(*args, **kwargs)

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def test_createDirs(self):
        '''
        Test the function time.createDirs. Specifically test that it creates the specified
        directory and the subdirectories. Test that it throws ValueError if theDir already 
        exists. Test that cwd is the same before calling the function and after.
        '''
        cwd = os.getcwd()
        outdir = 'out/'
        msg = "Test test_createDirs is improperly set up"
        self.assertTrue(os.path.exists(outdir), msg)

        sandbox = os.path.join(outdir, 'SCHWANSTEIN')
        sandbox = os.path.abspath(sandbox)
        if os.path.exists(sandbox):
            rmtree(sandbox, ignore_errors=True)
            self.assertFalse(os.path.exists(sandbox), "The error here is in the test_createDirs")
            # os.removedirs(sandbox)

        theDate = dt.datetime(2019,1,1)
        wasThrown = False
        createDirs(theDate, sandbox)
        try:
            createDirs(theDate, sandbox)
        except ValueError:
            wasThrown = True
        finally:
            self.assertTrue(wasThrown)
        

        
        while True:
            if theDate.isoweekday() < 6:
                break
            theDate = theDate + dt.timedelta(days=1)
        self.assertTrue(os.path.exists(sandbox))
        
        cwd2 = os.getcwd()
        self.assertEqual(cwd, cwd2)
        if os.path.exists(sandbox):
            rmtree(sandbox)





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
    # t.test_getFirstWeekday()
    t.test_createDirs()


if __name__ == '__main__':
    notmain()
