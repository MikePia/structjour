from unittest import TestCase
from unittest.mock import patch
from foo import f2
from mock import patch
from collections import deque

import pandas as pd

from journal.pandasutil import InputDataFrame, ToCSV_Ticket as Ticket
from journal.tradeutil import ReqCol
from journalfiles import JournalFiles



D = deque()

class MyTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(MyTest, self).__init__(*args, **kwargs)
        global D

        self.D = D
        if not D or len(D) < 6:
            D.clear()

            D = deque(['', 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', ])




    def test_f2_2(self):
        for i in range(6):
            self.()

        print("after tests")



    @patch('journal.pandasutil.askUser')
    def walkit(self, mock_askUser):
        '''Run Structjour multiple times with test files'''
        from trade import run

        tests = [[1, 'trades.1116_messedUpTradeSummary10.csv',
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


        #Will give an arbitrary date to avoid name conflicts
        for count, infile in enumerate(self.infiles):
            # infile = 'trades.csv'
            outdir = 'out/'
            theDate = pd.Timestamp(2019, 1, count+1)
            print(theDate)
            indir = 'data/'
            mydevel = True
            # mock_askUser.
            #         some_func.return_value = (20, False)
            # num, stat = f2()
            # self.assertEqual((num, stat), (40, False))

            run(infile=infile, outdir=outdir, theDate=theDate, indir=indir, mydevel=mydevel)

            # for i in tests:
            #     print (i[0], i[1])
            if tests[count][2]:
                for j in tests[count][2]:
                    print(infile, tests[count][1])
                    print('     ', j)

            
            if count == 31:
                exit()


if __name__ == '__main__':
    # D.append(20)
    # D.append(30)
    # D.append(40)
    # D.append(50)
    # D.append(60)
    # D.append(70)
    t = MyTest()
    # for i in range(5):
    t.test_f2_2()