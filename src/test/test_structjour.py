'''
Integration test of structjour. Especially tests on Overnight holds. I plan to bareak the current
behavior but not before this version is tested more completely.

@created_on Feb 2, 2019

@author: Mike Petersen
'''
import os
from unittest import TestCase
from unittest.mock import patch
from collections import deque
import re

import pandas as pd


from trade import run
# pylint: disable = C0103, W0603, W0613


DD = deque()
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


def findTrade(df, t):
    '''
    Locate the trade represented by t in the dataFrame.
    :params df: A dataFrame of the output data as found in the upper portion of the output file.
    :params t: Data of a trade as presented in testdata.csv.
    '''

    # iterate through each trade as a dataFrame dfx
    for i in range(12):
        s = "Trade " + str(i+1)
        dfx = df[df['Tindex'] == s]

        # pick out trades with the symbol
        # print(dfx)
        # print()
        if dfx.symb.unique()[0] == t[0].strip():

            wegood = False
            if t[2].lower().strip().startswith('short'):
                #  and [m.group] 'HOLD-' in list(dfx.side):
                li = list(dfx.side)
                regex = re.compile('HOLD-*')
                if [m.group(0) for l in li for m in [regex.search(l)] if m]:
                    amnt = float(-t[4])
                    wegood = True
            elif t[2].lower().strip().startswith('long'):
                li = list(dfx.side)
                regex = re.compile('HOLD-*')
                if [m.group(0) for l in li for m in [regex.search(l)] if m]:

                    # print(dfx.account.unique()[0], 'long')
                    amnt = float(t[4])
                    wegood = True
            if wegood:
                if(t[3].lower().strip().startswith('after') and
                   dfx.iloc[-1].side.startswith('HOLD') and
                   float(dfx.iloc[-2].bal) == amnt):
                    return dfx
                if(t[3].lower().strip().startswith('before') and
                   dfx.iloc[0].side.startswith('HOLD') and
                   float(dfx.iloc[0].bal) == amnt):
                    return dfx
    return pd.DataFrame()




class TestStructjour(TestCase):
    '''
    Run all of structjour with a collection of input files and test the outcome
    '''

    def __init__(self, *args, **kwargs):
        super(TestStructjour, self).__init__(*args, **kwargs)
        global DD

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

        self.DD = DD
        if not DD or len(D) < 11:
            DD.clear()

            # These are overnight hold shares. They are mocked user input here in mock_askUser.
            # Each list corresponds to each infile.
            DD = deque(
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

        self.getTestData(r'C:\python\E\structjour\src\data')


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
        self.tests = data


    @patch('journal.xlimage.askUser', return_value='d')
    @patch('journal.layoutsheet.askUser', return_value='n')
    @patch('journal.pandasutil.askUser', side_effect=mock_askUser)
    def test_run(self, unusedstub, unused2, unused3):
        '''Run structjour beginning to end.'''
        global D
        global DD
        for count, (fred, infile, d) in enumerate(zip(DD, self.infiles, self.tests)):
            D = deque(fred)
            outdir = 'out/'
            theDate = pd.Timestamp(2019, 1, count+1)
            # print(theDate, infile)
            indir = 'data/'
            mydevel = True
            jf = run(infile=infile, outdir=outdir, theDate=theDate, indir=indir,
                     infile2=None, mydevel=mydevel)
            # print(jf.outpathfile)
            # print()

            # # The testdata file is found in the indir (data directory) along with the trades
            # input files we just ran
            # Now, however, we will test the output files found in the outdir (out dir). Those are
            # human files. We demonstrate far too much knowledge of their idosyncracies here,
            #  ...

            trades = list()
            indir = jf.outdir
            f = jf.outpathfile
            # fpname = os.path.join(indir, f)
            numTrades = int(d[1])
            df = pd.read_excel(f)
            # l = len(df)

            begin = False
            finalNum = 0
            for dummy, row in df.iterrows():
                if row[0] == 'Tindex':
                    begin = True
                    continue
                elif begin and isinstance(row[0], str) and row[0].startswith('Trade'):
                    r = [row[0], row[1], row[2], row[3], row[4], row[5],
                         row[6], row[7], row[8], row[9], row[10], row[11], row[12]]
                    trades.append(r)
                    num = row[0].split(' ')[1]
                    # print(num)
                    finalNum = int(num)
                elif begin:
                    break
            self.assertEqual(finalNum, numTrades)
            columns = ['Tindex', 'start', 'time', 'symb', 'side', 'price',
                       'qty', 'bal', 'account', 'pl', 'sum', 'dur', 'name']
            fdf = pd.DataFrame(data=trades, columns=columns)
            trades = []

        #     print(d[3][0])
            for dd in d[3]:
                #         print(dd)
                x = findTrade(fdf, dd)
                self.assertGreater(len(x), 0)
                # print('passed')


if __name__ == '__main__':
    # pylint: disable = E1120
    ttt = TestStructjour()
    ttt.test_run()
