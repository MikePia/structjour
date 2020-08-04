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
Test the methods in th module journal.dfutil
Created on Jan 28, 2019

@author: Mike Petersen
'''
import unittest
import os

import pandas as pd

from structjour.dfutil import DataFrameUtil
from structjour.colz.finreqcol import FinReqCol
from structjour.definetrades import ReqCol

#  pylint: disable=C0103, W0703


class Test_DfUtil(unittest.TestCase):
    '''
    Test something
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(Test_DfUtil, self).__init__(*args, **kwargs)

    def setUp(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))

    def testCheckReqColumnsWithReqColSuccess(self):
        '''Test return values of DataFrameUtil.checkRequiredInputFields'''
        reqCol = ReqCol()
        finReqCol = FinReqCol()

        frc = pd.DataFrame(columns=finReqCol.columns)

        t1 = False
        t2 = False
        try:
            t1 = DataFrameUtil.checkRequiredInputFields(frc, finReqCol.columns)
            t2 = DataFrameUtil.checkRequiredInputFields(frc, reqCol.columns)

        except ValueError as ex:
            print(ex)
        self.assertTrue(t1)
        self.assertTrue(t2)

    def testCheckRequiredColumnsThrow(self):
        '''Test DataFrameUtil.checkRequredInputFields for raising exceptions'''
        vals = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']]
        apd = pd.DataFrame(vals)
        apd.columns = [['Its', 'the', 'end', 'of',
                        'the', 'world', 'as', 'we', 'know', 'it']]
        columns = ['Its', 'the', 'end', 'of', 'the',
                   'world', 'as', 'we', 'know', 'it', 'sofuckit']
        # DataFrameUtil.checkRequiredInputFields(apd, columns)

        try:
            DataFrameUtil.checkRequiredInputFields(apd, columns)

        except ValueError:
            pass
        except Exception as ex:
            msg = "{0}{1}".format("Unexpected exception. ", ex)
            self.fail(msg)

        else:
            self.fail("Failed to throw expected exception")

        vals = [[1, 2, 3, 4, 5, 6, 7, 8, 9], [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']]
        apd = pd.DataFrame(
            vals, columns=['Its', 'the', 'end', 'of', 'world', 'as', 'we', 'know', 'it'])

        gotve = False
        try:
            DataFrameUtil.checkRequiredInputFields(apd, columns)
        except ValueError:
            gotve = True
        except Exception as ex:
            msg = "Wrong exception was thrown" + ex
            self.fail(msg)
        finally:
            self.assertTrue(gotve, "Failed to throw a Value Error Exception")

    def testCheckrequiredColumnsWithReqColFail(self):
        '''Test method DataFrameUtil.checkRequiredInputFields'''

        reqCol = ReqCol()
        finReqCol = FinReqCol()
        fail = pd.DataFrame(
            columns=['Time', 'Symb', 'Side', 'Price', 'Qty', 'Account'])
        rc = pd.DataFrame(columns=reqCol.columns)

        gotve = False
        try:
            DataFrameUtil.checkRequiredInputFields(fail, reqCol.columns)
        except ValueError:
            gotve = True
        finally:
            self.assertTrue(gotve, "Failed to throw value error")

        gotve = False
        try:
            DataFrameUtil.checkRequiredInputFields(rc, finReqCol.columns)
        except ValueError:
            gotve = True
        finally:
            self.assertTrue(gotve, "Failed to throw a ValueError")

    def test_dfUtil_createDf(self):
        '''Test method DataFrameUtil.createDf'''
        cols = pd.DataFrame(columns=['Its', 'the', 'end', 'of', 'the', 'world',
                                     'as', 'we', 'know', 'it'])
        cols2 = ['Its', 'the', 'end', 'of', 'the', 'world', 'as', 'we', 'know', 'it']
        numRow = 9
        fill = ''

        x = DataFrameUtil.createDf(cols, numRow, fill)
        y = DataFrameUtil.createDf(cols2, numRow, fill)

        self.assertEqual(list(x.columns), list(y.columns))
        self.assertEqual(len(x), len(y))

        for xc, yc in zip(x.iloc[1], y.iloc[1]):
            self.assertEqual(xc, yc)
            self.assertEqual(xc, fill)

        fill = None
        y = DataFrameUtil.createDf(cols2, numRow, fill)
        for xc, yc in zip(x.iloc[1], y.iloc[1]):
            self.assertTrue(xc != yc)

            self.assertEqual(yc, fill)

    def test_dfUtil_addRow(self):
        '''Test method DataFrameUtil.addRows
        '''
        cols2 = ['Its', 'the', 'end', 'of', 'the', 'world', 'as', 'we', 'know', 'it']
        numRow = 9
        fill = 'something silly'
        fill2 = 'sillier'

        y = DataFrameUtil.createDf(cols2, numRow, fill=fill)
        y = DataFrameUtil.addRows(y, numRow, fill=fill2)
        self.assertEqual(len(y), numRow * 2)

        for i in range(numRow):
            for ii in y.iloc[i]:
                self.assertEqual(ii, fill)

        for i in range(numRow, numRow * 2):
            for ii in y.iloc[i]:
                self.assertEqual(ii, fill2)


def main():
    '''Run unittests cl style'''
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


def notmain():
    '''Run some local code'''
    t = Test_DfUtil()
    # t.test_dfUtil_createDf()
    t.test_dfUtil_addRow()


if __name__ == '__main__':
    # notmain()
    main()
