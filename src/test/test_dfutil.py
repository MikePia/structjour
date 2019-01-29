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
