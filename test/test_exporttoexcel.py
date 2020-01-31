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
Test the methods in the module exporttoexcel

@created_on Feb 8, 2019

@author: Mike Petersen
'''
import os
import sys

from  unittest import TestCase
import unittest

from openpyxl import Workbook, load_workbook
import pandas as pd

from structjour.rtg import getRandGenTradeStuff

from structjour.journalfiles import JournalFiles

from structjour.dailysumforms import MistakeSummary
from structjour.layoutsheet import LayoutSheet
from structjour.thetradeobject import SumReqFields
from structjour.tradestyle import TradeFormat, c as tcell
from structjour.view.dailycontrol import DailyControl
from structjour.view.exportexcel import ExportToExcel

from PyQt5.QtTest import QTest
from PyQt5 import QtCore
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
from PyQt5 import QtWebEngineWidgets    # noqa F401
from PyQt5.QtWidgets import QApplication

# pylint: disable = C0103

app = QApplication(sys.argv)


class Test_ExportToExcel(TestCase):
    '''
    Test the ExportToExcel Object. Generally use this class for less elaborate setups and
    Test_ExportToExcel_MistakeData for more elaborate setups (Hyperinks and stuff requiring
    coordinated data)
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(Test_ExportToExcel, self).__init__(*args, **kwargs)


    def setUp(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))
        theDate = pd.Timestamp('2008-06-06')
        self.jf = JournalFiles(outdir='out/', theDate=theDate, mydevel=False, inputType='DAS')
        self.tradeS, self.ts, self.entries, self.imageNames, self.df, self.ldf = getRandGenTradeStuff()
        if os.path.exists(self.jf.outpathfile):
            os.remove(self.jf.outpathfile)


    def test_exportExcel(self):
        '''Using a random trade generator, test exportExcel creates a file'''

        t = ExportToExcel(self.ts, self.jf, self.df)
        t.exportExcel()

        self.assertTrue(os.path.exists(self.jf.outpathfile))

    def test_populateXLDailyNote(self):
        '''
        Test the method populateXLDailyNote. Specifically test after setting a note, calling the
        method the workbook contains the note as expected
        '''
        dc = DailyControl(self.jf.theDate)
        note = 'Ipsum solarium magus coffeum brewum'
        dc.setNote(note)
        
        t = ExportToExcel(self.ts, self.jf, self.df)
        wb = Workbook()
        ws = wb.active
        t.populateXLDailyNote(ws)
        t.saveXL(wb, self.jf)
        wb2 = load_workbook(self.jf.outpathfile)


        cell = (1, 6)
        cell = tcell(cell)
        val = wb2.active[cell].value
        self.assertEqual(note, val)         

    def test_populateXLDailySummaryForm(self):
        '''
        Test the method populateXLDailySummaryForm. Specifically test that given a specific anchor, 
        12 specific spots are written to by default. 
        '''
        NUMROWS = 6
        mstkAnchor = (3, 3)     # arbitrary
        mistake = MistakeSummary(numTrades=len(self.ldf), anchor=mstkAnchor)
        t = ExportToExcel(self.ts, self.jf, self.df)
        wb = Workbook()

        t.populateXLDailySummaryForm(mistake, wb.active, mstkAnchor)
        # t.saveXL(wb, self.jf)
        
        anchor = (mstkAnchor[0], mstkAnchor[1] + len(self.ldf) + 5)
        cell = tcell(mstkAnchor, anchor=anchor)
        for i in range(0, NUMROWS):
            cell = tcell((mstkAnchor[0], mstkAnchor[1] + i), anchor = anchor)
            cell2 = tcell((mstkAnchor[0]+1, mstkAnchor[1] + i), anchor = anchor)
            self.assertIsInstance(wb.active[cell].value, str)
            self.assertIsInstance(wb.active[cell2].value, str)

class Test_ExportToExcel_MistakeData(TestCase):
    '''
    Test the forms data. Elaborate setup. Kind of eloborate tests. It Aint TDD
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(Test_ExportToExcel_MistakeData, self).__init__(*args, **kwargs)


    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))
        
        theDate = pd.Timestamp('2008-06-06')
        self.jf = JournalFiles(outdir='out/', theDate=theDate, mydevel=False, inputType='DAS')
        self.tradeS, self.ts, self.entries, self.imageNames, self.df, self.ldf = getRandGenTradeStuff()
        if os.path.exists(self.jf.outpathfile):
            os.remove(self.jf.outpathfile)

        # Setup mistake note fields to test
        note = 'Ground control to Major Tom'

        for i, key in enumerate(self.ts):
            tto = self.ts[key]
            notex = note + str(i+1)
            tto['MstkNote'] = notex

        # Setup a couple images to add 
        imdir = 'images/'
        img1 = os.path.join(imdir, 'fractal-art-fractals.jpg')
        img2 = os.path.join(imdir, 'psych.jpg')
        assert os.path.exists(img1)
        assert os.path.exists(img2)
        for key in self.ts:
            tto = self.ts[key]['chart1'] = img1
            tto = self.ts[key]['chart2'] = img2




        t = ExportToExcel(self.ts, self.jf, self.df)
        imageNames = t.getImageNamesFromTS()
        imageLocation, dframe = t.layoutExcelData(t.df, self.ldf, imageNames)
        assert len(self.ldf) == len(imageLocation)

        # Create an openpyxl wb from the dataframe
        ls = LayoutSheet(t.topMargin, len(t.df))
        wb, ws, nt = ls.createWorkbook(dframe)

        #Place both forms 2 cells to the right of the main table
        mstkAnchor = (len(dframe.columns) + 2, 1) 
        mistake = MistakeSummary(numTrades=len(self.ldf), anchor=mstkAnchor)
        self.imageLocation = imageLocation
        self.mistake = mistake
        self.wb = wb
        self.t = t
        self.a = mstkAnchor
        self.note = note

    def test_populateXLMistakeForm_hyperlinks(self):
        '''
        Test the method populateXLMistakeForm has set up correct hyperlinks to the daily summary
        forms. 
        '''
        ws = self.wb.active
        iloc = self.imageLocation
        self.t.populateXLDailyFormulas(iloc, ws)
        self.t.populateXLMistakeForm(self.mistake, ws, iloc)
        # self.t.saveXL(self.wb, self.jf)

        # cell = tcell(self.mistake.mistakeFields['tpl1'][0])
        for i in range(len(self.ldf)):
            n = 'name' + str(i+1)
            cell = tcell(self.mistake.mistakeFields[n][0][0], anchor=self.a)
            self.assertIsNotNone(ws[cell].hyperlink)
            link = ws[cell].hyperlink.target.split('!')[1]
            self.assertIsNotNone(ws[link].hyperlink)
            link2 = ws[link].hyperlink.target.split('!')[1]
            self.assertEqual(cell, link2)
        # print(ws[cell].value)

    def test_populateXLMistakeForm_correctTradePL(self):
        '''This method knows way too much, but how else to deal with excel and test formula results...'''
        ws = self.wb.active
        iloc = self.imageLocation
        self.t.populateXLDailyFormulas(iloc, ws)
        self.t.populateXLMistakeForm(self.mistake, ws, iloc)
        # self.t.saveXL(self.wb, self.jf)

        # Here we will get the values that the simple formulas point to and test that the trade pl matches
        for i in range(len(self.ldf)):
            tpl = 'tpl' + str(i+1)
            cell = tcell(self.mistake.mistakeFields[tpl][0], anchor=self.a)
            vallink = ws[cell].value.replace('=', '')
            val = ws[vallink].value
            try:
                val = float(val)
            except ValueError:
                print(val)
                if val == '':
                    val = 0.0
                else:
                    raise ValueError('Unexpected value for a currency amount.', type(val), val)
            self.assertIsInstance(val, float, val)
            origval = float(self.ldf[i].iloc[-1].Sum)
            self.assertAlmostEqual(val, origval)

    def test_populateXLMistakeForm_noteLinks(self):
        '''
        This method knows way too much, but how else to deal with excel and test formula results...
        Test that when data is included for the mistake note in ts, that data is linked with a 
        simple formula (e.g. '=X98') in the mistake summary form
        '''
        ws = self.wb.active
        iloc = self.imageLocation
        self.t.populateXLDailyFormulas(iloc, ws)
        self.t.populateXLMistakeForm(self.mistake, ws, iloc)
        # self.t.saveXL(self.wb, self.jf)

        # Here we will get the values that the simple formulas point to and test that the note is what we wrote
        for i in range(len(self.ldf)):
            m = 'mistake' + str(i+1)
            note = self.note + str(i+1)
            cell = tcell(self.mistake.mistakeFields[m][0][0], anchor=self.a)
            vallink = ws[cell].value.replace('=', '')
            val = ws[vallink].value
            self.assertEqual(val, note)

    def test_placeImagesAndSumStyles(self):
        '''
        At a loss for how to test image placement---the image is in a zip, the links are not in
        the worksheet. Openpyxl does not get the image info from load_workbook. While these asserts
        are not satisfactory, they will probably fail if something has gone wrong with the insert
        locations for images and the SumStyle forms.
        '''
        tf = TradeFormat(self.wb)
        ws = self.wb.active
        self.mistake.mstkSumStyle(ws, tf, self.a)
        self.mistake.dailySumStyle(ws, tf, self.a)

        self.t.placeImagesAndSumStyles(self.imageLocation, ws, tf)
        # self.t.saveXL(self.wb, self.jf)

        for loc in self.imageLocation:
            sumcell=tcell((1, loc[0][0][1]))
            aboveSumCell = tcell((1, loc[0][0][1]-1))
            self.assertEqual(ws[sumcell].style, 'titleStyle', sumcell)
            self.assertEqual(ws[aboveSumCell].style, 'Normal', aboveSumCell)
            for iloc, fn in zip(loc[0], loc[1]):
                imgcell = tcell(iloc)
                sumcell = tcell((1, iloc[1]))

                self.assertIsNotNone(ws[imgcell].value)

    def test_populateXLDailyFormulas(self):
        '''
        Test populateXLDailyFormulas. Specifically test that the value written to the
        ws is a formula (it begins with =).
        '''
        srf = SumReqFields()
        self.t.populateXLDailyFormulas
        self.t.populateXLDailyFormulas(self.imageLocation, self.wb.active)
        # self.t.saveXL(self.wb, self.jf)
        ws = self.wb.active

        # Get the anchor from imageLocation, Get the form coord from tfcolumns using a key
        # common to tfcolumns and tfformulas
        for loc in self.imageLocation:
            anchor = (1, loc[0][0][1])
            for key in srf.tfformulas:
                cell = srf.tfcolumns[key][0]
                if isinstance(cell, list):
                    cell = cell[0]
                valcell = tcell(cell, anchor=anchor)
                # print(ws[valcell].value)
                self.assertEqual(ws[valcell].value.find('='), 0)

def main():
    unittest.main()


def notmain():

    t = Test_ExportToExcel()
    t.setUp()
    t.test_exportExcel()

if __name__ == '__main__':
    # notmain()
    main()
