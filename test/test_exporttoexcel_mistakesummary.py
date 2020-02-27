# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading

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
Test the methods in the module exporttoexcel_mistakesummary

@created_on Feb 27, 2019

@author: Mike Petersen
'''
import os
import sys
import unittest
from unittest import TestCase

from PyQt5.QtCore import QSettings
from PyQt5 import QtCore
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
from PyQt5 import QtWebEngineWidgets    # noqa:  F401
from PyQt5 import QtWidgets

from structjour.dailysumforms import MistakeSummary
from structjour.definetrades import DefineTrades
from structjour.journalfiles import JournalFiles
from structjour.layoutsheet import LayoutSheet

from structjour.rtgAgain import RTG
from structjour.statements.ibstatement import IbStatement
from structjour.statements.ibstatementdb import StatementDB
from structjour.statements.statement import getStatementType
from structjour.statements.dasstatement import DasStatement
from structjour.stock.utilities import clearTables
from structjour.thetradeobject import SumReqFields
from structjour.tradestyle import TradeFormat, c as tcell
from structjour.view.exportexcel import ExportToExcel
from structjour.view.layoutforms import LayoutForms
from structjour.view.sumcontrol import SumControl

app = QtWidgets.qApp = QtWidgets.QApplication(sys.argv)

class Test_ExportToExcel_MistakeData(TestCase):
    '''
    Test the forms data. Elaborate setup. Kind of eloborate tests. It Aint TDD
    '''

    infile = ''
    theDate = ''
    lf = None
    jf = None
    dframe = None
    ldf = None

    rtg = None
    db = ''
    outdir = ''
    sc = None
    rtg = None
    db = ''
    outdir = ''
    sc = None

    @classmethod
    def setUpClass(cls):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

        outdir = 'test/out'
        cls.outdir = os.path.realpath(outdir)
        cls.db = 'data/testdb.sqlite'
        cls.db = os.path.realpath(cls.db)
        if os.path.exists(cls.db):
            clearTables(cls.db)

        cls.rtg = RTG(db=cls.db)
        # cls.dates = ['20200203 09:30', '20200204 07:30', '20200205 09:35', '20200206 11:40', '20200207 10:39']
        cls.theDate = '20200207 10:39'
        cls.infile = cls.rtg.saveSomeTestFiles([cls.theDate], cls.outdir)[0]

        settings = QSettings('zero_substance', 'structjour')
        # for i, name in enumerate(cls.infiles):
        name = os.path.join(cls.outdir, cls.infile)
        x, inputType = getStatementType(name)
        if inputType == 'DAS':
            ds = DasStatement(name, settings, cls.theDate)
            ds.getTrades(testFileLoc=cls.outdir, testdb=cls.db)
        elif inputType == "IB_CSV":
            ibs = IbStatement(db=cls.db)
            ibs.openIBStatement(name)
        else:
            raise ValueError(f'Unsupported File type: {inputType}')

        statement = StatementDB(db=cls.db)
        df = statement.getStatement(cls.theDate)
        dtrade = DefineTrades(inputType)
        dframe, cls.ldf = dtrade.processDBTrades(df)

        cls.jf = JournalFiles(indir=cls.outdir, outdir=outdir, theDate=cls.theDate, infile=name)
        cls.sc = SumControl()
        lf = LayoutForms(cls.sc, cls.jf, dframe)
        lf.runTtoSummaries(cls.ldf)

        # Setup mistake note fields to test
        cls.note = 'Ground control to Major Tom'

        for i, key in enumerate(lf.ts):
            tto = lf.ts[key]
            notex = cls.note + str(i + 1)
            tto['MstkNote'] = notex

        # Setup a couple images to add
        imdir = 'images/'
        img1 = os.path.join(imdir, 'fractal-art-fractals.jpg')
        img2 = os.path.join(imdir, 'psych.jpg')
        assert os.path.exists(img1)
        assert os.path.exists(img2)
        for key in lf.ts:
            tto = lf.ts[key]['chart1'] = img1
            tto = lf.ts[key]['chart2'] = img2

        t = ExportToExcel(lf.ts, cls.jf, df)
        imageNames = t.getImageNamesFromTS()
        cls.imageLocation, dframe = t.layoutExcelData(t.df, cls.ldf, imageNames)
        assert len(cls.ldf) == len(cls.imageLocation)

        # Create an openpyxl wb from the dataframe
        ls = LayoutSheet(t.topMargin, len(t.df))
        cls.wb, ws, nt = ls.createWorkbook(dframe)

        # Place both forms 2 cells to the right of the main table
        mstkAnchor = (len(dframe.columns) + 2, 1)
        cls.mistake = MistakeSummary(numTrades=len(cls.ldf), anchor=mstkAnchor)
        cls.t = t
        cls.a = mstkAnchor

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
            n = 'name' + str(i + 1)
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
            tpl = 'tpl' + str(i + 1)
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
            m = 'mistake' + str(i + 1)
            note = self.note + str(i + 1)
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
            sumcell = tcell((1, loc[0][0][1]))
            aboveSumCell = tcell((1, loc[0][0][1] - 1))
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

    Test_ExportToExcel_MistakeData.setUpClass()
    t = Test_ExportToExcel_MistakeData()
    # t.test_populateXLMistakeForm_hyperlinks()
    # t.test_populateXLMistakeForm_correctTradePL()
    # t.test_populateXLMistakeForm_noteLinks()
    # t.test_placeImagesAndSumStyles()
    t.test_populateXLDailyFormulas()


if __name__ == '__main__':
    # notmain()
    main()
