import os
from unittest import TestCase
from unittest.mock import patch
from foo import f2
# from unittest.mock import patch
from collections import deque

import pandas as pd

from journal.pandasutil import InputDataFrame, ToCSV_Ticket as Ticket
from journal.tradeutil import ReqCol
from journalfiles import JournalFiles
from journal.layoutsheet import LayoutSheet
from trade import run




DD = deque()
D = deque()


def mock_askUser(shares, question):
    global D
    x = D.popleft()
    print("Returning from the mock ", x)
    return x

class MyTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(MyTest, self).__init__(*args, **kwargs)
        global DD

        self.DD = DD
        if not DD or len(D) < 10:
            DD.clear()


            

            # These are user inputs, each row corresponding to each infile. 
            DD = deque(
                       [
                        [-4000, 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        [3923, -750, 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        ['n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        [600, 241, 50, 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        [-169, 'n','q', 'q', 'q', 'q', 'q', 'q'],
                        ['n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        [0, -600, 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        ['n', 'q'],
                        [0, 750, 50, 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        [-600, 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'], 
                       ]
                        )
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

        # Input test files can be added here.  Should add files that should fail in another list
        self.infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
                        'trades.8.csv', 'trades.907.WithChangingHolds.csv',
                        'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
                        'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
                        'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv']

        self.tests = [[1, 'trades.1116_messedUpTradeSummary10.csv',
                  [['PCG', 'Sim', 'Short', 'After', 4000]]],
                 [2, 'trades.8.WithHolds.csv',
                  [['MU', 'Sim', 'Short', 'After', 750],
                   ['IZEA', 'SIM', 'Long', 'After', 3923]]],
                 [3, 'trades.8.csv', []],
                 [4, 'trades.907.WithChangingHolds.csv',
                  [['MU', 'Live', 'Long', 'After', 50],
                   ['AMD', 'Sim', 'Long', 'After', 600],
                   ['FIVE', 'Live', 'Long', 'After', 241]]],
                 [5, 'trades_190117_HoldError.csv',
                  [['PCG', 'Live', 'Short', 'After', 169]]],
                 [6, 'trades.8.ExcelEdited.csv', []],
                 [7, 'trades.910.tickets.csv',
                  [['AMD', 'Sim', 'Long', 'Before', 600]]],
                 [8, 'trades_tuesday_1121_DivBy0_bug.csv', []],
                 [9, 'trades.8.WithBothHolds.csv',
                  [['MU', 'Sim', 'Short', 'Before', 750],
                   ['TSLA', 'Sim', 'Long', 'After', 50]]],
                 [10, 'trades1105HoldShortEnd.csv',
                  [['AMD', 'Live', 'Short', 'After', 600]]]]



    @patch('journal.xlimage.askUser', return_value='q')
    @patch('journal.layoutsheet.askUser', return_value='n')
    @patch('journal.pandasutil.askUser', side_effect=mock_askUser)
    def test_f2_2(self, unusedstub, unused2, unused3):
        global D
        global DD
        for count, (fred, infile) in enumerate(zip(DD, self.infiles)):
            D = deque(fred)
            outdir = 'out/'
            theDate = pd.Timestamp(2019, 1, count+1)
            print(theDate)
            indir = 'data/'
            mydevel = True

            run(infile=infile, outdir=outdir, theDate=theDate, indir=indir, mydevel=mydevel)
        print("after tests")


if __name__ == '__main__':
    t = MyTest()
    t.test_f2_2()