'''
Created on Sep 8, 2018

@author: Mike Petersen
'''
import unittest
from journal.xlimage import XLImage
import random
from datetime import datetime

class Test(unittest.TestCase):


    def testXLImageAdjustSize(self):
        '''The size tuple is required to be ints. The rounding discrepencay will be worse with smaller numbers.
        :var:pixDelta:  Adjusts for float math rounding to a final int result. The delta here should be enough and 
                        is a very small distance in pixels.
        '''
        xl = XLImage()
        random.seed(datetime.now())
        
        pixDelta = 0.02
        #Test input tuple
        for i in range(10) :
            insz=(random.randint(200,2500),random.randint(200,2500))
            w,h   = xl.adjustSizeByHeight(insz)
            self.assertAlmostEqual(insz[0]/insz[1], w/h, delta=pixDelta)      
        #TestChanging heights
        for i in range(10) :
            insz=(random.randint(200,2500),random.randint(200,2500))
            nh=(random.randint(200,700))
            w,h   = xl.adjustSizeByHeight(insz, newHeight=nh)
            self.assertAlmostEqual(insz[0]/insz[1], w/h, delta=pixDelta)      
            self.assertEqual(h, nh)
        #Test Figuring by cell number
        for i in range(10) :
            insz=(random.randint(200,2500),random.randint(200,2500))
            nc=(random.randint(15,35))
            w,h   = xl.adjustSizeByHeight(insz, numCells=nc)
            self.assertAlmostEqual(insz[0]/insz[1], w/h, delta=pixDelta)      
        #test changing pixPerCell
        for i in range(10) :
            insz=(random.randint(200,2500),random.randint(200,2500))
            ppc=(random.uniform(30,35))
            nc=(random.randint(15,35))
            w,h   = xl.adjustSizeByHeight(insz, numCells=nc, pixPerCell=ppc)
            self.assertAlmostEqual(insz[0]/insz[1], w/h, delta=pixDelta)  
            
        
           
             
    
         



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testXLImageAdjustSize']
    unittest.main()