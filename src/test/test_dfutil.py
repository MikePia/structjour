'''
Test the methods in th module journal.dfutil
Created on Jan 28, 2019

@author: Mike Petersen
'''
import unittest
import os
import types

from journal.pandasutil import InputDataFrame, ToCSV_Ticket as Ticket
from journal.dfutil import DataFrameUtil
import pandas as pd
from journal.tradeutil import ReqCol, FinReqCol  # , TradeUtil
from journalfiles import JournalFiles

#  pylint: disable=C0103


class Test_DfUtil(unittest.TestCase):
    '''
    Test the methods in ToCSV_Ticket
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(Test_DfUtil, self).__init__(*args, **kwargs)
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def testCheckReqColumnsWithReqColSuccess(self):
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
        vals = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']]
        apd = pd.DataFrame(vals)
        apd.columns = [['Its', 'the', 'end', 'of',
                        'the', 'world', 'as', 'we', 'know', 'it']]
        columns = ['Its', 'the', 'end', 'of', 'the',
                   'world', 'as', 'we', 'know', 'it', 'sofuckit']
#         DataFrameUtil.checkRequiredInputFields(apd, columns)

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

        try:
            DataFrameUtil.checkRequiredInputFields(apd, columns)
        except ValueError:
            pass
            self.assertTrue(True)
        except Exception as ex:
            msg = "Wrong exception was thrown" + ex
            self.fail(msg)
        else:
            self.fail("Failed to throw a Value Error Exception")

    def testCheckrequiredColumnsWithReqColFail(self):

        reqCol = ReqCol()
        finReqCol = FinReqCol()
        fail = pd.DataFrame(
            columns=['Time', 'Symb', 'Side', 'Price', 'Qty', 'Account'])
        rc = pd.DataFrame(columns=reqCol.columns)

        try:
            DataFrameUtil.checkRequiredInputFields(fail, reqCol.columns)
        except ValueError as ex:
            print(ex)
            self.assertTrue(True, ex)

        try:
            DataFrameUtil.checkRequiredInputFields(rc, finReqCol.columns)
        except ValueError as ex:
            self.assertTrue(True)

    def test_dfUtil_createDf(self):
        cols = pd.DataFrame(columns=['Its', 'the', 'end', 'of', 'the', 'world', 'as', 'we', 'know', 'it'])
        cols2 =['Its', 'the', 'end', 'of', 'the', 'world', 'as', 'we', 'know', 'it']
        numRow=9
        fill = ''

        x = DataFrameUtil.createDf(cols, numRow, fill)
        y = DataFrameUtil.createDf(cols2, numRow, fill)

        self.assertEqual (list(x.columns), list(y.columns))
        self.assertEqual (len(x), len(y))

        for xc, yc in zip(x.iloc[1], y.iloc[1]):
            self.assertEqual(xc, yc)
            self.assertEqual(xc, fill)

        fill = None
        y = DataFrameUtil.createDf(cols2, numRow, fill)
        for xc, yc in zip(x.iloc[1], y.iloc[1]):
            self.assertTrue(xc != yc)

            self.assertEqual(yc, fill)

    def test_dfUtil_addRow(self):
        cols2 = ['Its', 'the', 'end', 'of', 'the', 'world', 'as', 'we', 'know', 'it']
        numRow = 9
        fill = 'something silly'
        fill2 = 'sillier'

        y = DataFrameUtil.createDf(cols2, numRow, fill=fill)
        y = DataFrameUtil.addRows(y, numRow, fill=fill2)
        self.assertEqual(len(y), numRow*2)

        for i in range(numRow):
            for ii in y.iloc[i]:
                self.assertEqual(ii, fill)

        for i in range(numRow, numRow*2):
            for ii in y.iloc[i]:
                self.assertEqual(ii, fill2)



def main():
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

def notmain():
    t = Test_DfUtil()
    # t.test_dfUtil_createDf()
    t.test_dfUtil_addRow()

if __name__ == '__main__':
    '''Run some local code'''
    # notmain()
    main()