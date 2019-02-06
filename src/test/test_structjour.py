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
    print("Returning from the mock ", x)
    return x


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
        if not DD or len(D) < 10:
            DD.clear()

            # These are user inputs, each row corresponding to each infile.
            DD = deque(
                [[-4000], [3923, -750], [], [600, 241, 50], [-169],
                 [], [0, -600], [], [0, 750, 50], [-600], ])

        # Input test files can be added here.  Should add files that should fail in another list
        self.infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
                        'trades.8.csv', 'trades.907.WithChangingHolds.csv',
                        'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
                        'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
                        'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv']

        self.tests = [[['PCG', 'Sim', 'Short', 'After', 4000]],
                      [['MU', 'Sim', 'Short', 'After', 750],
                       ['IZEA', 'SIM', 'Long', 'After', 3923]],
                      [],
                      [['MU', 'Live', 'Long', 'After', 50],
                       ['AMD', 'Sim', 'Long', 'After', 600],
                       ['FIVE', 'Live', 'Long', 'After', 241] ],
                      [['PCG', 'Live', 'Short', 'After', 169]],
                      [],
                      [['AMD', 'Sim', 'Long', 'Before', 600]],
                      [],
                      [['MU', 'Sim', 'Short', 'Before', 750],
                       ['TSLA', 'Sim', 'Long', 'After', 50]],
                     [['AMD', 'Live', 'Short', 'After', 600]]]

    @patch('journal.xlimage.askUser', return_value='q')
    @patch('journal.layoutsheet.askUser', return_value='n')
    @patch('journal.pandasutil.askUser', side_effect=mock_askUser)
    def test_run(self, unusedstub, unused2, unused3):
        '''Run structjour beginning to end.'''
        global D
        global DD
        for count, (fred, infile) in enumerate(zip(DD, self.infiles)):
            D = deque(fred)
            outdir = 'out/'
            theDate = pd.Timestamp(2019, 1, count+1)
            print(theDate)
            indir = 'data/'
            mydevel = True
            print(infile)
            jf = run(infile=infile, outdir=outdir,
                     theDate=theDate, indir=indir, mydevel=mydevel)

        print("after tests")


if __name__ == '__main__':
    # pylint: disable = E1120
    t = TestStructjour()
    t.test_run()
