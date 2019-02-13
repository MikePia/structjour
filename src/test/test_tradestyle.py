'''
Test the methods and functions in journal.tradestyle
@created_on Feb 12, 2019

@author: Mike Petersen
'''
import os
from unittest import TestCase

from openpyxl import load_workbook
from openpyxl import Workbook

from journal.tradestyle import TradeFormat, c



# pylint: disable = C0103, W0613, W0603


class TestTradeFormat(TestCase):
    '''
    Test the methods in journal.tradestyle.TradeFormat and also the functions in the module.
    '''

    def __init__(self, *args, **kwargs):
        super(TestTradeFormat, self).__init__(*args, **kwargs)

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def test_TradeFormat(self):
        '''
        Test the object formation and the cration of the styles in __init__ for the Workbook. 
        Specifically test that the named styles are created in the workbook and are still there
        when you close it and open it.
        '''

        wb = Workbook()
        ws = wb.active
        tf = TradeFormat(wb)
        styleList = list(tf.styles.keys())
        if not os.path.exists("out/"):
            os.mkdir("out/")

        dispath = "out/SCHNOrK.xlsx"
        if os.path.exists(dispath):
            os.remove(dispath)

        for i, key in enumerate(styleList):
            #     print(key, c((1, i+1)))
            ws[c((1, i+1))] = key
            ws[c((1, i+1))].style = tf.styles[key]
        wb.save(dispath)

        wb2 = load_workbook(dispath)
        ws2 = wb2.active

        for i, key in enumerate(styleList):
            #     print(key,ws2[c((1, i+1))].style )
            self.assertEqual(key, ws2[c((1, i+1))].style)
        # print('Done')



def notmain():
    t = TestTradeFormat()
    t.test_TradeFormat()
()
if __name__ == '__main__':
    notmain()