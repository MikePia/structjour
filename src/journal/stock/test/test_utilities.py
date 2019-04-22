'''
@author: Mike Petersen

@creation_date: 2019-01-17
'''
import datetime as dt
import types
import unittest

from journal.stock import utilities as util
# pylint: disable = C0103


class TestUtilities(unittest.TestCase):
    '''Test functions in the stock.utilities module'''

    def test_getLastWorkDay(self):
        '''run some local code'''
        now = dt.datetime.today()
        fmt = "%a, %B %d"
        # dd = now
        print()
        for i in range(7):
            d = now - dt.timedelta(i)
            dd = util.getLastWorkDay(d)

            print(f'{d.strftime(fmt)} ... : ... {util.getLastWorkDay(d).strftime(fmt)}')
            self.assertTrue(dd.isoweekday() < 6)
            self.assertTrue(dd.isoweekday() > 0)

def notmain():
    '''Run some local code'''
    t = TestUtilities()
    t.test_getLastWorkDay()

def main():
    '''
    test discovery is not working in vscode. Use this for debugging. Then run cl python -m unittest
    discovery
    '''
    f = TestUtilities()
    for name in dir(f):
        if name.startswith('test'):
            attr = getattr(f, name)
            if isinstance(attr, types.MethodType):
                attr()

if __name__ == '__main__':
    # notmain()
    main()
