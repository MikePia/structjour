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
Test the methods and functions in journal.xlimage.
Created on Feb 17, 2019

@author: Mike Petersen
'''
import datetime as dt
import os
import random
from unittest import TestCase
import unittest

# from PIL import Image as PILImage
# from PIL import ImageGrab
# from openpyxl.drawing.image import Image

from structjour.xlimage import XLImage


class TestXLImage(TestCase):
    '''
    Test the functions in methods in thetradeobject module. Created no tests for getAndResizeImage
    and getPilImage. By the time I have automated responses mocked out, very little of value would
    be tested.
    '''

    def __init__(self, *args, **kwargs):
        super(TestXLImage, self).__init__(*args, **kwargs)
        # global DD

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def test_getDefault(self):
        '''
        Test the method journal.xlimage.XLImage.getDefaultPILImage. Specifically test that it opens
        an image whether an image is specified or not. If not, the default image may not exist- fix
        that.
        '''
        img = r'C:\python\E\structjour\data\defaultImage.png'
        os.path.exists(img)

        xli = XLImage(img)

        im = xli.getDefaultPILImage()
        self.assertEqual(im.format.lower(), 'png')
        xli2 = XLImage()
        im2 = xli2.getDefaultPILImage()
        self.assertGreater(len(im2.format), 1)

    def test_adjustSizeByHeight(self):
        '''
       Test the method XLImage.adjustSizeByHeight
        '''
        xl = XLImage()
        random.seed(dt.datetime.now())

        pixDelta = 0.02
        # Test input tuple
        for dummy in range(10):
            insz = (random.randint(200, 2500), random.randint(200, 2500))
            w, h = xl.adjustSizeByHeight(insz)
            self.assertAlmostEqual(insz[0] / insz[1], w / h, delta=pixDelta)

        # Test Figuring by cell number
        for dummy in range(10):
            insz = (random.randint(200, 2500), random.randint(200, 2500))
            nc = (random.randint(15, 35))
            xl = XLImage(heightInCells=nc)
            w, h = xl.adjustSizeByHeight(insz)
            self.assertAlmostEqual(insz[0] / insz[1], w / h, delta=pixDelta)

        # test changing pixPerCell
        for dummy in range(10):
            insz = (random.randint(200, 2500), random.randint(200, 2500))
            ppc = (random.uniform(30, 35))
            nc = (random.randint(15, 35))
            xl = XLImage(heightInCells=nc, pixPerCell=ppc)
            w, h = xl.adjustSizeByHeight(insz)
            self.assertAlmostEqual(insz[0] / insz[1], w / h, delta=pixDelta)

    def test_getResizeName(self):
        '''Test method journal.xlimage.XLImage.getResizeName'''

        xli = XLImage()
        origname = 'FredsEmporium.potter'
        outdir = 'C:/python/E/structjour/out'
        name, dummy = xli.getResizeName(origname, outdir)
        outdir, newname = os.path.split(name)
        torig, dummy = os.path.splitext(origname)
        tnew, dummy = os.path.splitext(newname)
        self.assertEqual(torig, tnew)


def main():
    '''Run unittest locally'''
    unittest.main()


def notmain():
    '''run some local code'''
    t = TestXLImage()
    # t.test_getDefault()
    # t.test_AdjustSizeByHeight()
    t.test_getResizeName()


if __name__ == '__main__':
    # notmain()
    main()
