import os
from unittest import TestCase
from unittest.mock import patch
from foo import f2
from mock import patch
from collections import deque
DD = deque()
D = deque()

class MyTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(MyTest, self).__init__(*args, **kwargs)
        global DD

        self.DD = DD
        if not DD or len(D) < 10:
            DD.clear()


            ddiirr = os.path.dirname(__file__)
            os.chdir(os.path.realpath(ddiirr + '/../'))

            # Input test files can be added here.  Should add files that should fail in another list
            self.infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
                            'trades.8.csv', 'trades.907.WithChangingHolds.csv',
                            'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
                            'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
                            'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv']

            # These are user inputs, each row corresponding to each infile. 
            DD = deque(
                       [
                        ['', 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        ['', '', 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        ['n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        ['', '', '', 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        ['', 'n','q', 'q', 'q', 'q', 'q', 'q'],
                        ['n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        ['0', '', '', 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        ['n', 'q'],
                        ['0', '', '', '', 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q'],
                        ['', 'n', 'q', 'q', 'q', 'q', 'q', 'q', 'q', 'q'], 
                       ]
                        )




    def test_f2_2(self):
        global D
        global DD
        for i in range(6):
            D = deque(DD.popleft())
            self.f2_2()

        print("after tests")



    @patch('foo.f1')
    def f2_2(self, some_func):
        global D
        while len(D) >= 2:
            some_func.return_value = (D.popleft(), False)
            num, stat = f2()
            # self.assertEqual((num, stat), (40, False))
            print(num, stat)


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