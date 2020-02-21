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
@author: Mike Petersen

@creation_date: 2019-01-17
'''
import datetime as dt
import os
import pickle
import types
import unittest

import pandas as pd

from PyQt5.QtCore import QSettings

from structjour.stock import mybarchart as bc

from structjour.stock import utilities as util
# pylint: disable = C0103


class PickleSettings:
    '''A utility to store and restore settings for use in testing. Be careful not to lose data.'''
    def __init__(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        self.settings = QSettings('zero_substance', 'structjour')
        self.apisettings = QSettings('zero_substance/stockapi', 'structjour')
        self.chartsettings = QSettings('zero_substance/chart', 'structjour')
        self.setkeys = []
        self.setvals = []
        self.apisetkeys = []
        self.apisetvals = []

        self.name = os.path.join(ddiirr, 'pickleset.zst')
        # print(self.name)

    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def tearDown(self):
        self.setUp()

    def initializeSettings(self):
        self.settings.clear()
        self.apisettings.clear()
        self.chartsettings.clear()

    def removePickle(self):
        if os.path.exists(self.name):
            os.remove(self.name)

    def initializeVars(self):
        self.setkeys = []
        self.setvals = []

        self.apisetkeys = []
        self.apisetvals = []

        self.chartkeys = []
        self.chartvals = []

    def storeSettings(self, replacePickle=False):
        if os.path.exists(self.name):
            if not replacePickle:
                return
        self.initializeVars()
        self.setkeys = self.settings.allKeys()
        for k in self.setkeys:
            self.setvals.append(self.settings.value(k))

        self.apisetkeys = self.apisettings.allKeys()
        for k in self.apisetkeys:
            self.apisetvals.append(self.apisettings.value(k))

        self.chartkeys = self.chartsettings.allKeys()
        for k in self.chartkeys:
            self.chartvals.append(self.chartsettings.value(k))

        setsnkeys = [self.setkeys, self.setvals, self.apisetkeys, self.apisetvals, self.chartkeys, self.chartvals]

        with open(self.name, "wb") as f:
            '''Cannot pickle qsettings objects- so we pickle a list'''
            pickle.dump((setsnkeys), f)

    def restoreSettings(self):
        if os.path.exists(self.name):
            with open(self.name, "rb") as f:
                setsnkeys = pickle.load(f)
                for k, v in zip(setsnkeys[0], setsnkeys[1]):
                    self.settings.setValue(k, v)

                for k2, v2 in zip(setsnkeys[2], setsnkeys[3]):
                    self.apisettings.setValue(k2, v2)

                for k2, v2 in zip(setsnkeys[4], setsnkeys[5]):
                    self.chartsettings.setValue(k2, v2)

            os.remove(self.name)
        else:
            print(f'No pickle found at {self.name}')


class TestUtilities(unittest.TestCase):
    '''Test functions in the stock.utilities module'''

    def __init__(self, *args, **kwargs):
        super(TestUtilities, self).__init__(*args, **kwargs)
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        self.p = os.path.realpath(ddiirr)

    def test_makeupEntries(self):
        '''
        Test the test utility makeupEntries. Specifically test that candle index matches the
        integer candle index, test the price lies within the range of the candle and test the
        entry time lies within candle interval.
        '''
        b = util.getPrevTuesWed(pd.Timestamp.today())
        start = pd.Timestamp(b.year, b.month, b.day, 9, 32, 45)
        end = pd.Timestamp(b.year, b.month, b.day, 11, 39, 46)
        interval = 5
        # print(start)
        x, df, maList = bc.getbc_intraday('SQ', start=start, end=end, minutes=interval, showUrl=True)

        entries = util.makeupEntries(df, 5)
        for e in entries:
            cx = e[3]
            candleindex = df.index[e[1]]
            delt = cx - candleindex
            assert delt.total_seconds() // 60 <= interval
            # self.assertEqual(df.index[e[1]], cx)
            high = df.iloc[e[1]].high
            low = df.iloc[e[1]].low
            price = e[0]
            self.assertGreaterEqual(price, low)
            self.assertLessEqual(price, high)

    def test_getLastWorkDay(self):
        '''run some local code'''
        now = dt.datetime.today()
        # fmt = "%a, %B %d"

        for i in range(7):
            d = now - dt.timedelta(i)
            dd = util.getLastWorkDay(d)

            # print(f'{d.strftime(fmt)} ... : ... {util.getLastWorkDay(d).strftime(fmt)}')
            self.assertTrue(dd.isoweekday() < 6)
            self.assertTrue(dd.isoweekday() > 0)

    def test_updateKey(self):
        t = PickleSettings()
        t.storeSettings()
        t.initializeSettings()
        settings = QSettings('zero_substance', 'structjour')
        # apiset = QSettings('zero_substance/stockapi', 'structjour')

        settings.setValue('journal', self.p)
        testdb = 'test_db.db'
        mk = util.ManageKeys(db=testdb, create=True)
        mk.updateKey('bc', 'Its the end of the world')
        mk.updateKey('av', 'as we know it')
        bck = mk.getKey('bc')
        avk = mk.getKey('av')
        self.assertTrue(bck == 'Its the end of the world')
        self.assertTrue(avk == 'as we know it')

        t.restoreSettings()
        # print(apiset.allKeys())
        # print(settings.allKeys())
        os.remove(testdb)

    def test_ibSettings(self):
        t = PickleSettings()
        t.storeSettings()
        t.initializeSettings()

        apiset = QSettings('zero_substance/stockapi', 'structjour')
        apiset.setValue('ibRealCb', True)
        apiset.setValue('ibPaperCb', False)
        ibs = util.IbSettings()
        defport = 7496
        defid = 7878
        defhost = '127.0.0.1'
        p = ibs.getIbSettings()
        self.assertEqual(defhost, p['host'])
        self.assertEqual(defid, p['id'])
        self.assertEqual(defport, p['port'])

        t.restoreSettings()
        # print(apiset.allKeys())


def notmain():
    '''Run some local code... Careful not to remove keys'''
    # p = PickleSettings()
    # p.storeSettings()
    # p.initializeSettings()
    # p.restoreSettings()
    t = TestUtilities()

    t.test_makeupEntries()
    # t.test_getLastWorkDay()
    # t.test_setDB()
    # t.test_updateKey()
    # t.test_ibSettings()
    # t = PickleSettings()
    # t.storeSettings()
    # t.initializeSettings()
    # t.restoreSettings()
    # t.removePickle()
    # t = PickleSettings()
    # t.storeSettings()
    # t.initializeSettings()
    # t.restoreSettings()


def main():
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


def localrun():
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
    notmain()
    # main()
