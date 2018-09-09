'''
Created on Sep 8, 2018

@author: Mike Petersen
'''
import unittest
from structjour.tradeutil import XLImage


class Test(unittest.TestCase):


    def testXLImageAdjustSize(self):
        xl = XLImage()
        x = xl.adjustSizeByHeight((2024,1050), 200)
        print(x)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testXLImageAdjustSize']
    unittest.main()