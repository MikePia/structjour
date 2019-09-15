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
Test the methods in the module layoutsheet

@created_on Feb 8, 2019

@author: Mike Petersen
'''

import datetime as dt
import os
from random import randint
from unittest import TestCase
import unittest
from unittest.mock import patch
from collections import deque

import numpy as np
import pandas as pd

from openpyxl import Workbook
from openpyxl import load_workbook

from PyQt5.QtCore import QSettings

from structjour.journalfiles import JournalFiles
from structjour.pandasutil import InputDataFrame
from structjour.statement import Statement_DAS
from structjour.colz.finreqcol import FinReqCol
from structjour.definetrades import DefineTrades
from structjour.layoutsheet import LayoutSheet
from structjour.dailysumforms import MistakeSummary
from structjour.tradestyle import TradeFormat, c as tcell
from structjour.thetradeobject import SumReqFields
########: disable = C0103, W0613, W0603, W0212, R0914
# pylint: disable = C0103, W0613, W0603, W0212, R0914


D = deque()


def mock_askUser(shares_unused, question_unused):
    '''
    Mock the specific askUser function that asks how many shares are currently owned or owned
    before trading today.
    '''
    global D
    x = D.popleft()
    # print("Returning from the mock ", x)
    return x


# Runs w/o error using discovery IFF its the first test to run. With mock, QTest, global data and 
# precarious data matching based on knowing too much, I am not going to take the time to fix it.
# Its deprecated code- will soon remove all evidence of the console version and the cosole
# interview. (It runs without error when run seperately)
@unittest.skip('fnka')
class TestLayoutSheet(TestCase):
    '''
    Run all of structjour with a collection of input files and test the outcome
    '''

    def __init__(self, *args, **kwargs):
        super(TestLayoutSheet, self).__init__(*args, **kwargs)

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

        settings = QSettings('zero_substance', 'structjour')
        settings.setValue('runtype', 'CONSOLE')

        self.dadata = deque(
            [[-4000], [3923, -750], [], [600, 241, 50], [-169],
             [], [0, -600], [], [0, 750, 50], [-600], [0, -200]])

        # Input test files can be added here. And place the test data in testdata.xlsx. Should add
        # files with potential difficulties
        self.infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
                        'trades.8.csv', 'trades.907.WithChangingHolds.csv',
                        'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
                        'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
                        'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv',
                        'trades190221.BHoldPreExit.csv']

        # self.tests = self.getTestData(r'C:\python\E\structjour\src\data')

    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def getTestData(self, indir):
        '''
        Open the csv file testdata and oraganze the data into a usable data structure. The file is
        necessarily populated by 'hand.' To add a file to test, copy it to the data dir and enter
        the information to test.
        :return data: List  containing the data to check against the output files.
        '''

        df = pd.read_excel(os.path.join(indir, 'testdata.xlsx'))

        l = len(df)
        data = list()

        data = list()
        for i, row in df.iterrows():
            entry = list()
            if not pd.isnull(df.at[i, 'Order']):
                entry.extend((row['Order'], row['NumTrades'], row['Name']))
                j = i
                trades = list()
                begginning = True
                while j < l and not pd.isnull(df.at[j, 'Ticker']):
                    # Check these specific trades
                    if not begginning:
                        if isinstance(df.at[j, 'Name'], str):
                            break

                    trades.append([df.at[j, 'Ticker'], df.at[j, 'Account'],
                                   df.at[j, 'Side'], df.at[j, 'Held'], df.at[j, 'Pos'], ])
                    begginning = False
                    j = j+1
                entry.append(trades)
                data.append(entry)
        return data

    @patch('structjour.pandasutil.askUser', side_effect=mock_askUser)
    def test_createImageLocation(self, unusedstub):
        '''Run structjour'''
        #Assert the initial entry location in imageLocation is figured by these factors
         # Assert all entries are figured by summarySize and len of the minittrade
        # Assert the minitable locations are offset by length of the minitrade tables +
                # ls.spacing, and the first entry in the Leftmost column starts with 'Trade'
                 # Assert third entry of imageLocation begins with 'Trade' and contains
                #       ['Long', 'Short']
                # Assert the 4th entry is a timestamp
                # Assert the 5th entry is a time delta
        global D


        for tdata, infile in zip(self.dadata, self.infiles):
            # :::::::::  Setup   ::::::::
            D = deque(tdata)
            # infile = 'trades.8.csv'
            # print(infile)
            indir = 'data/'
            mydevel = False
            jf = JournalFiles(indir=indir, infile=infile, mydevel=mydevel)

            trades, jf = Statement_DAS(jf).getTrades()
            trades, success = InputDataFrame().processInputFile(trades)
            inputlen, dframe, ldf = DefineTrades().processOutputDframe(trades)
            # ::::::::::: end setup :::::::::::::

            margin = 25
            spacing = 3
            ls = LayoutSheet(margin, inputlen, spacing=spacing)
            imageLocation, dframe = ls.imageData(dframe, ldf)


            for count, t in enumerate(imageLocation):
                if count == 0:
                    initialEntry = ls.inputlen + ls.topMargin + ls.spacing + len(ldf[0]) + 2
                    self.assertEqual(t[0], initialEntry)

                else:
                    nextloc = imageLocation[count-1][0] + len(ldf[count]) + ls.summarySize
                    self.assertEqual(t[0], nextloc)

                t_entry = t[0] - (spacing + len(ldf[count]))
                self.assertTrue(dframe.iloc[t_entry][0].startswith('Trade'))
                self.assertEqual(len(dframe.iloc[t_entry-1][0]), 0)
                self.assertTrue(t[2].startswith('Trade'))

                #
                # self.assertTrue(t[2].find('Long') > 0 or t[2].find('Short') > 0)
                self.assertTrue(isinstance(pd.Timestamp('2019-11-11 ' + t[3]), dt.datetime))
                self.assertTrue(isinstance(t[4], dt.timedelta))


    def test_createWorkbook(self):
        '''
        Test the method structjour.layoutsheet.LayoutSheet.createWorkbook
        '''

        df = pd.DataFrame(np.random.randint(0, 100, size=(100, 7)), columns=list('ABCDEFG'))
        # df
        margin = 25
        spacing = 3
        inputlen = len(df)
        ls = LayoutSheet(margin, inputlen, spacing=spacing)

        wb, ws, df = ls.createWorkbook(df)


        for row, (i, dfrow) in zip(ws, df.iterrows()):
            # We inserted the column headers in this row (ws starts with 1, not 0)
            if i + 1 == ls.topMargin:
                for ms, x in zip(row, df.columns):
                    self.assertEqual(x, ms.value)
            # everything else is verbatim
            else:
                for ms, x in zip(row, dfrow):
                    self.assertEqual(x, ms.value)


        wb.save("out/SCHNOrK.xlsx")

    def test_styleTop(self):
        '''
        Test the method layoutsheet.LayoutSheet.styleTop. This  will probably produce warnings from
        openpyxl as there is empty data when it makes the headers. No worries.
        Note that we are using a protected member of Worksheet ws._tables, so if it this fails, look
        at that. openpyxl does not provide a public attribute for tables.
        Note that knowing the quoteRange and noteRange is bad design. Eventually these two bits of
        design data should be abstracted to somewhere accessible by the user. (and testing too)
        '''
        quoteRange = [(1, 1), (13, 5)]
        noteRange = [(1, 6), (13, 24)]
        quoteStyle = 'normStyle'
        noteStyle = 'explain'
        margin = 25
        inputlen = 50   #len(df)

        wb = Workbook()
        ws = wb.active

        # Make sure the out dir exists
        if not os.path.exists("out/"):
            os.mkdir("out/")

        # Make sure the file we are about to create does not exist
        dispath = "out/SCHNOrK.xlsx"
        if os.path.exists(dispath):
            os.remove(dispath)

        # Create table header and data in the ws
        headers = ['Its', 'the', 'end', 'of', 'the', 'world', 'as', 'we',
                   'know', 'it.', 'Bout', 'Fn', 'Time!']
        for i in range(1, 14):
            ws[tcell((i, 25))] = headers[i-1]

        ls = LayoutSheet(margin, inputlen)
        for x in range(ls.topMargin+1, ls.inputlen + ls.topMargin+1):
            for xx in range(1, 14):
                ws[tcell((xx, x))] = randint(-1000, 10000)


        ls.styleTop(ws, 13, TradeFormat(wb))

        wb.save(dispath)

        wb2 = load_workbook(dispath)
        ws2 = wb2.active

        listOfMerged = list()
        listOfMerged.append(tcell((quoteRange[0])) + ':' +  tcell((quoteRange[1])))
        listOfMerged.append(tcell((noteRange[0])) + ':' +  tcell((noteRange[1])))
        for xx in ws2.merged_cells.ranges:
            # print (str(xx) in listOfMerged)
            self.assertTrue(str(xx) in listOfMerged)
        self.assertEqual(ws[tcell(quoteRange[0])].style, quoteStyle)
        self.assertEqual(ws[tcell(noteRange[0])].style, noteStyle)

        self.assertEqual(len(ws._tables), 1)


        begin = tcell((1, ls.topMargin))

        end = tcell((13, ls.topMargin + ls.inputlen))
        tabRange = f'{begin}:{end}'
        self.assertEqual(tabRange, ws._tables[0].ref)

        os.remove(dispath)

    def test_styleTopwithnothin(self):
        '''
        Test the method layoutsheet.LayoutSheet.styleTop. Test that it still works without
        table data. We still know too much about the method,. Note that we are using a protected
        member of Worksheet ws._tables
        '''
        quoteRange = [(1, 1), (13, 5)]
        noteRange = [(1, 6), (13, 24)]
        quoteStyle = 'normStyle'
        noteStyle = 'explain'
        margin = 25
        inputlen = 50   #len(df)

        wb = Workbook()
        ws = wb.active

        # Make sure the out dir exists
        if not os.path.exists("out/"):
            os.mkdir("out/")

        # Make sure the file we are about to create does not exist
        dispath = "out/SCHNOrK.xlsx"
        if os.path.exists(dispath):
            os.remove(dispath)

        ls = LayoutSheet(margin, inputlen)
        ls.styleTop(ws, 13, TradeFormat(wb))

        wb.save(dispath)

        wb2 = load_workbook(dispath)
        ws2 = wb2.active

        listOfMerged = list()
        listOfMerged.append(tcell((quoteRange[0])) + ':' +  tcell((quoteRange[1])))
        listOfMerged.append(tcell((noteRange[0])) + ':' +  tcell((noteRange[1])))
        for xx in ws2.merged_cells.ranges:
            # print (str(xx) in listOfMerged)
            self.assertIn(str(xx), listOfMerged)
        self.assertEqual(ws[tcell(quoteRange[0])].style, quoteStyle)
        self.assertEqual(ws[tcell(noteRange[0])].style, noteStyle)

        self.assertEqual(len(ws._tables), 1)


        begin = tcell((1, ls.topMargin))

        end = tcell((13, ls.topMargin + ls.inputlen))
        tabRange = f'{begin}:{end}'
        self.assertEqual(tabRange, ws._tables[0].ref)

        os.remove(dispath)


    @patch('structjour.xlimage.askUser', return_value='d')
    @patch('structjour.layoutsheet.askUser', return_value='n')
    @patch('structjour.pandasutil.askUser', side_effect=mock_askUser)
    def test_populateMistakeForm(self, unusedstub1, unusedstub2, unusedstub3):
        '''
        Test the method populateMistakeForm. The setup here is alost the entire module trade.py
        '''

        global D
        for tdata, infile in zip(self.dadata, self.infiles):
            # :::::::::  Setup   ::::::::
            D = deque(tdata)
            # :::::::::::::: SETUP ::::::::::::::
            # theDate = '2018-11-05'
            outdir = 'out/'
            indir = 'data/'
            mydevel = False
            jf = JournalFiles(infile=infile, outdir=outdir, indir=indir, mydevel=mydevel)

            trades, jf = Statement_DAS(jf).getTrades()
            trades, success = InputDataFrame().processInputFile(trades)
            inputlen, dframe, ldf = DefineTrades().processOutputDframe(trades)

            # Process the openpyxl excel object using the output file DataFrame. Insert
            # images and Trade Summaries.
            margin = 25

            # Create the space in dframe to add the summary information for each trade.
            # Then create the Workbook.
            ls = LayoutSheet(margin, inputlen)
            imageLocation, dframe = ls.imageData(dframe, ldf)
            wb, ws, dummy = ls.createWorkbook(dframe)

            tf = TradeFormat(wb)

            mstkAnchor = (len(dframe.columns) + 2, 1)
            mistake = MistakeSummary(numTrades=len(ldf), anchor=mstkAnchor)
            mistake.mstkSumStyle(ws, tf, mstkAnchor)

            tradeSummaries = ls.runSummaries(imageLocation, ldf, jf, ws, tf)

            # :::::::::::::: END SETUP ::::::::::::::
            ls.populateMistakeForm(tradeSummaries, mistake, ws, imageLocation)

            # Make sure the out dir exists
            if not os.path.exists("out/"):
                os.mkdir("out/")

            # Make sure the file we are about to create does not exist
            dispath = "out/SCHNOrK.xlsx"
            if os.path.exists(dispath):
                os.remove(dispath)
            wb.save(dispath)

            wb2 = load_workbook(dispath)
            ws2 = wb2.active

            frc = FinReqCol()

            # ragged iteration over mistakeFields and tradeSummaries.
            count = 0   # ragged iterator for tradeSummaries
            for key in mistake.mistakeFields:

                entry = mistake.mistakeFields[key]
                cell = entry[0][0] if isinstance(entry[0], list) else entry[0]
                cell = tcell(cell, anchor=mistake.anchor)
                if key.startswith('name'):
                    # Get the hyperlink target in mistakeform , parse the target and verify the
                    # hyperlinks point to each other
                    tsName = tradeSummaries[count][frc.name].unique()[0]
                    tsAcct = tradeSummaries[count][frc.acct].unique()[0]
                    targetcell = ws2[cell].hyperlink.target.split('!')[1]
                    originalcell = ws2[targetcell].hyperlink.target.split('!')[1]

                    # print(ws2[cell].value, '<--------', tsumName)
                    # print(ws2[cell].value, '<-------', tsumAccount)
                    # print(cell, '<------->', originalcell)
                    self.assertGreater(ws2[cell].value.find(tsName), -1)
                    self.assertGreater(ws2[cell].value.find(tsAcct), -1)
                    self.assertEqual(cell, originalcell)
                    count = count + 1


            # ::::::: tpl fields :::::::
            count = 0
            for key in mistake.mistakeFields:

                entry = mistake.mistakeFields[key]
                cell = entry[0][0] if isinstance(entry[0], list) else entry[0]
                cell = tcell(cell, anchor=mistake.anchor)
                if key.startswith('tpl'):
                    targetcell = ws2[cell].value[1:]
                    origval = tradeSummaries[count][frc.PL].unique()[0]
                    # print(ws2[targetcell].value, '<------->', origval )
                    if origval == 0:
                        self.assertIs(ws2[targetcell].value, None)
                    else:
                        self.assertAlmostEqual(ws2[targetcell].value, origval)
                    count = count + 1

                # These next two tests (for plx and mistakex) have no unique entries (without user
                # input or mock) Test for the static values and that plx entry is next to its header
                if key.startswith('pl'):
                    headval = 'Proceeds Lost'
                    targetcell = ws2[cell].value[1:]
                    headercell = 'A' + targetcell[1:]
                    # print(ws2[targetcell].value, '<------->', None)
                    # print(headercell, '------->', ws2[headercell].value)
                    self.assertTrue(ws2[targetcell].value is None)
                    self.assertEqual(ws2[headercell].value, headval)


    @patch('structjour.xlimage.askUser', return_value='d')
    @patch('structjour.layoutsheet.askUser', return_value='n')
    @patch('structjour.pandasutil.askUser', side_effect=mock_askUser)
    def test_populateDailySummaryForm(self, unusedstub1, unusedstub2, unusedstub3):
        '''
        Test the method populateMistakeForm. The setup here is alost the entire module trade.py
        The tested method puts in the trade PL and notes
        '''

        global D


        for tdata, infile in zip(self.dadata, self.infiles):
            # :::::::::  Setup   ::::::::
            D = deque(tdata)
            # :::::::::::::: SETUP ::::::::::::::
            # theDate = '2018-11-05'
            outdir = 'out/'
            indir = 'data/'
            mydevel = False
            jf = JournalFiles(infile=infile, outdir=outdir, indir=indir, mydevel=mydevel)
            print(jf.inpathfile)

            trades, jf = Statement_DAS(jf).getTrades()
            trades, success = InputDataFrame().processInputFile(trades)
            inputlen, dframe, ldf = DefineTrades().processOutputDframe(trades)

            # Process the openpyxl excel object using the output file DataFrame. Insert
            # images and Trade Summaries.
            margin = 25

            # Create the space in dframe to add the summary information for each trade.
            # Then create the Workbook.
            ls = LayoutSheet(margin, inputlen)
            imageLocation, dframe = ls.imageData(dframe, ldf)
            wb, ws, dummy = ls.createWorkbook(dframe)

            tf = TradeFormat(wb)

            mstkAnchor = (len(dframe.columns) + 2, 1)
            mistake = MistakeSummary(numTrades=len(ldf), anchor=mstkAnchor)
            # mistake.mstkSumStyle(ws, tf, mstkAnchor)
            mistake.dailySumStyle(ws, tf, mstkAnchor)
            tradeSummaries = ls.runSummaries(imageLocation, ldf, jf, ws, tf)

            # :::::::::::::: END SETUP ::::::::::::::
            # ls.populateMistakeForm(tradeSummaries, mistake, ws, imageLocation)
            ls.populateDailySummaryForm(tradeSummaries, mistake, ws, mstkAnchor)

            # Make sure the out dir exists
            if not os.path.exists("out/"):
                os.mkdir("out/")

            # Make sure the file we are about to create does not exist
            dispath = "out/SCHNOrK.xlsx"
            if os.path.exists(dispath):
                os.remove(dispath)

            wb.save(dispath)
            # print(infile, 'saved as', dispath)

            wb2 = load_workbook(dispath)
            ws2 = wb2.active

            # Live Total
            frc = FinReqCol()
            livetot = 0
            simtot = 0
            highest = 0
            lowest = 0
            numwins = 0
            numlosses = 0
            totwins = 0
            totloss = 0

            for trade in tradeSummaries:
                acct = trade[frc.acct].unique()[0]
                pl = trade[frc.PL].unique()[0]
                highest = pl if pl > highest else highest
                lowest = pl if pl < lowest else lowest
                if pl > 0:
                    numwins += 1
                    totwins += pl
                # Trades == 0 are figured in the loss column-- comissions and all
                else:
                    numlosses += 1
                    totloss += pl


                if acct == 'Live':
                    livetot += pl
                elif acct == 'SIM':
                    simtot += pl

            # print(livetot)
            # livetotcell = tcell(mistake.dailySummaryFields['livetot'][0], anchor=ls.DSFAnchor)
            # print(simtot)

            avgwin = 0 if numwins == 0 else totwins/numwins
            avgloss = 0 if numlosses == 0 else totloss/numlosses

            data = [['livetot', livetot], ['simtot', simtot], ['highest', highest],
                    ['lowest', lowest], ['avgwin', avgwin], ['avgloss', avgloss]]

            for s, d in data:
                cell = tcell(mistake.dailySummaryFields[s][0], anchor=ls.DSFAnchor)
                # msg = '{} {} {}'.format(s, d, ws2[cell].value)
                # print(msg)
                self.assertAlmostEqual(d, ws2[cell].value)  #, abs_tol=1e-7)


            data = ['livetotnote', 'simtotnote', 'highestnote', 'lowestnote',
                    'avgwinnote', 'avglossnote']
            for s in data:
                cell = tcell(mistake.dailySummaryFields[s][0][0], anchor=ls.DSFAnchor)
                val = ws2[cell].value
                self.assertIsInstance(val, str)

                self.assertGreater(len(val), 1)


    @patch('structjour.xlimage.askUser', return_value='d')
    @patch('structjour.layoutsheet.askUser', return_value='n')
    @patch('structjour.pandasutil.askUser', side_effect=mock_askUser)
    def test_runSummaries(self, unusedstub1, unusedstub2, unusedstub3):
        '''
        Test the method prunSummaries. The setup here is alost the entire module trade.py
        We run the standard set of infiles
        '''

        # global D
        # infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
        #         'trades.8.csv', 'trades.907.WithChangingHolds.csv',
        #         'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
        #         'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
        #         'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv',
        #         'trades190221.BHoldPreExit.csv']

        global D
        for tdata, infile in zip(self.dadata, self.infiles):
            # :::::::::  Setup   ::::::::

            D = deque(tdata)
            # :::::::::::::: SETUP ::::::::::::::
            # theDate = '2018-11-05'
            outdir = 'out/'
            indir = 'C:/python/E/structjour/data/'
            mydevel = False
            jf = JournalFiles(infile=infile, outdir=outdir, indir=indir, mydevel=mydevel)


            trades, jf = Statement_DAS(jf).getTrades()
            trades, success = InputDataFrame().processInputFile(trades)
            inputlen, dframe, ldf = DefineTrades().processOutputDframe(trades)

            # Process the openpyxl excel object using the output file DataFrame. Insert
            # images and Trade Summaries.
            margin = 25

            # Create the space in dframe to add the summary information for each trade.
            # Then create the Workbook.
            ls = LayoutSheet(margin, inputlen)
            imageLocation, dframe = ls.imageData(dframe, ldf)
            wb, ws, dummy = ls.createWorkbook(dframe)

            tf = TradeFormat(wb)

            mstkAnchor = (len(dframe.columns) + 2, 1)
            mistake = MistakeSummary(numTrades=len(ldf), anchor=mstkAnchor)
            mistake.mstkSumStyle(ws, tf, mstkAnchor)

            # :::::::::::::: END SETUP ::::::::::::::
            tradeSummaries = ls.runSummaries(imageLocation, ldf, jf, ws, tf)

            # Make sure the out dir exists
            if not os.path.exists("out/"):
                os.mkdir("out/")

            # Make sure the file we are about to create does not exist
            dispath = "out/SCHNOrK.xlsx"
            if os.path.exists(dispath):
                os.remove(dispath)
            wb.save(dispath)

            wb2 = load_workbook(dispath)
            ws2 = wb2.active


            srf = SumReqFields()
            for trade, loc in zip(tradeSummaries, imageLocation):
                anchor = (1, loc[0])
                for col in trade:
                    if col in['clean', 'Date'] or col.lower().startswith('chart'):
                        continue


                    # Get the cell
                    if isinstance(srf.tfcolumns[col][0], list):
                        cell = tcell(srf.tfcolumns[col][0][0], anchor=anchor)
                    else:
                        cell = tcell(srf.tfcolumns[col][0], anchor=anchor)

                    # Nicer to read
                    wsval = ws2[cell].value
                    tval = trade[col].unique()[0]

                    # Test Formulas (mostly skipping for now because its gnarly)
                    # Formulas in srf.tfformulas including the translation stuff

                    if col in srf.tfformulas.keys():
                        self.assertTrue(wsval.startswith('='))

                    # Test empty cells
                    elif not tval:
                        # print(wsval, '<------->', tval)
                        self.assertIs(wsval, None)

                    # Test floats
                    elif isinstance(tval, float):
                        # print(wsval, '<------->', tval)
                        self.assertAlmostEqual(wsval, tval)

                    # Time vals
                    elif isinstance(tval, (pd.Timestamp, dt.datetime, np.datetime64)):
                        wsval = pd.Timestamp(wsval)
                        tval = pd.Timestamp(tval)
                        self.assertGreaterEqual((wsval-tval).total_seconds(), -.01)
                        self.assertLessEqual((wsval-tval).total_seconds(), .01)


                    # Test everything else
                    else:
                        # print(wsval, '<------->', tval)
                        self.assertEqual(wsval, tval)


def notmain():
    '''Run some local code'''
        # pylint: disable = E1120
    ttt = TestLayoutSheet()
    ttt.test_createImageLocation()
    ttt.test_createWorkbook()
    ttt.test_styleTop()
    ttt.test_styleTopwithnothin()
    ttt.test_populateMistakeForm()
    ttt.test_populateDailySummaryForm()
    ttt.test_runSummaries()

def main():
    '''Run unittests cl style'''
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()




if __name__ == '__main__':
    notmain()
    # main()
