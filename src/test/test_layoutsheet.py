'''
Test the methods in the module layoutsheet

@created_on Feb 8, 2019

@author: Mike Petersen
'''
import os
from unittest import TestCase
from unittest.mock import patch
from collections import deque

import pandas as pd

from journalfiles import JournalFiles
from journal.pandasutil import InputDataFrame
from journal.tradeutil import TradeUtil
from journal.layoutsheet import LayoutSheet
# pylint: disable = C0103


D = deque()


def mock_askUser(dummy, dummy2):
    '''
    Mock the specific askUser function that asks how many shares are currently owned or owned
    before trading today.
    '''
    global D
    x = D.popleft()
    # print("Returning from the mock ", x)
    return x


class TestLayoutSheet(TestCase):
    '''
    Run all of structjour with a collection of input files and test the outcome
    '''

    def __init__(self, *args, **kwargs):
        super(TestLayoutSheet, self).__init__(*args, **kwargs)

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

        self.dadata = deque(
            [[-4000], [3923, -750], [], [600, 241, 50], [-169],
             [], [0, -600], [], [0, 750, 50], [-600], ])

        # Input test files can be added here. And place the test data in testdata.xlsx. Should add
        # files with potential difficulties
        self.infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
                        'trades.8.csv', 'trades.907.WithChangingHolds.csv',
                        'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
                        'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
                        'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv']

        # self.tests = self.getTestData(r'C:\python\E\structjour\src\data')

    def getTestData(self, indir):
        '''
        Open the csv file testdata and oraganze the data into a usable data structure. The file is
        necessarily populated by 'hand.' To add a file to test, copy it to the data dir and enter
        the information to test.
        :return data: List  containing the data to check against the output files.
        '''

        df = pd.read_excel(os.path.join(indir, 'testdata.xlsx'))

        l = len(df)
        # print(l)
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

    @patch('journal.pandasutil.askUser', side_effect=mock_askUser)
    def test_createImageLocation(self, unusedstub):
        '''Run structjour'''
        global D

        # :::::::::; Setup   ::::::::
        for tdata, infile in zip(self.dadata, self.infiles):
            D = deque(tdata)
            # infile = 'trades.8.csv'
            indir = 'data/'
            mydevel = False
            jf = JournalFiles(indir=indir, infile=infile, mydevel=mydevel)

            trades = pd.read_csv(jf.inpathfile)

            idf = InputDataFrame()
            trades = idf.processInputFile(trades)

            tu = TradeUtil()
            inputlen, dframe, ldf = tu.processOutputDframe(trades)
            # ::::::::::: end setup :::::::::::::

            sumSize = 25
            margin = 25
            spacing = 3
            ls = LayoutSheet(sumSize, margin, inputlen, spacing=spacing)
            imageLocation, dframe = ls.createImageLocation(dframe, ldf)

            #Where does the 2 come from ?
            import datetime as dt

            for count, t in enumerate(imageLocation):
                if count == 0:

                    #Assert the initial entry location in imageLocation is figured by these factors
                    initialEntry = ls.inputlen + ls.topMargin + \
                        ls.spacing + len(ldf[0]) + 2
                    self.assertEqual(t[0], initialEntry)

                else:
                    # Assert all entries are figured by summarySize and len of the minittrade
                    self.assertEqual(t[0], imageLocation[count-1]
                                     [0] + len(ldf[count]) + ls.summarySize)

                # Assert the minitable locations are offset by length of the minitrade tables +
                # ls.spacing, and the first entry in the Leftmost column starts with 'Trade'
                t_entry = t[0] - (spacing + len(ldf[count]))
                self.assertTrue(dframe.iloc[t_entry][0].startswith('Trade'))
                self.assertEqual(len(dframe.iloc[t_entry-1][0]), 0)

                # Assert third entry of imageLocation begins with 'Trade' and contains 
                #       ['Long', 'Short']
                # Assert the 4th entry is a timestamp
                # Assert the 5th entry is a time delta
                self.assertTrue(t[2].startswith('Trade'))
                self.assertTrue(t[2].find('Long') >
                                0 or t[2].find('Short') > 0)
                self.assertTrue(isinstance(pd.Timestamp(
                    '2019-11-11 ' + t[3]), dt.datetime))
                self.assertTrue(isinstance(t[4], dt.timedelta))

            print('Done', infile)





if __name__ == '__main__':
    # pylint: disable = E1120
    ttt = TestLayoutSheet()
    ttt.test_createImageLocation()
