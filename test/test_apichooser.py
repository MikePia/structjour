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
Choose which API intraday call to get chart data based on rules
@author: Mike Petersen

@creation_date: 3/3/20
'''

import datetime as dt
import logging
import numpy as np
import pandas as pd
import unittest
from structjour.stock import utilities as util

from structjour.stock.apichooser import APIChooser

from PyQt5.QtCore import QSettings


class TestAPIChooser(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestAPIChooser, self).__init__(*args, **kwargs)
        self.apiset = QSettings('zero_substance/stockapi', 'structjour')

    def test_apiChooser(self):
        '''
        Test the method FinPlot.apiChooser for the same interface in each api
        '''
        chooser = APIChooser(self.apiset)
        biz = util.getLastWorkDay()
        start = dt.datetime(biz.year, biz.month, biz.day, 12, 30)
        end = dt.datetime(biz.year, biz.month, biz.day, 16, 1)
        minutes = 1
        apis = chooser.preferences
        symbol = 'SQ'
        for api in apis:
            chooser.api = api
            result = chooser.apiChooserList(start, end, api)
            if result[0]:
                dummy, df, maDict = chooser.apiChooser()(symbol, start=start, end=end,
                                            minutes=minutes, showUrl=True)
                self.assertEqual(len(df.columns), 5,
                                 f"Failed to retrieve data with the {chooser.api} api.")
                self.assertTrue(isinstance(df.index[0], dt.datetime),
                                f'Failed to set index to datetime in {chooser.api} api')
                cols = ['open', 'high', 'low', 'close', 'volume']
                for col in cols:
                    # print(col, type(df[col][0]), isinstance(df[col][0], (np.float, np.integer)))
                    self.assertTrue(col in df.columns)
                    self.assertTrue(isinstance(
                        df[col][0], (np.float, np.integer)))

                # This call should retrieve data within 1 bar of the requested start and finish.
                # Idiosyncracies of the APIs vary as to inclusion of first and last time index
                delt = df.index[0] - \
                    start if df.index[0] > start else start - df.index[0]
                self.assertLessEqual(delt.seconds, minutes * 60)

                # print('Retrieved {} candles from {} to {} for {}'.format(
                #     len(df), df.index[0], df.index[-1], symbol))
                # print()
            else:
                print(f'Skipped {api} at {start} to {end} because...')
                for rule in result[1]:
                    print(rule)

    @unittest.SkipTest
    def test_apiChooserLimitReached(self):
        '''
        This is designed to hit the limits of the apis. Do not want to run this with
        tests most of the time. Just fiddle with the orprefs and the REPEATS and watch the result
        '''
        REPEATS = 15
        orprefs = ['av']
        symbol = 'AAPL'
        minutes = 1
        d = util.getPrevTuesWed(pd.Timestamp.now())
        start = pd.Timestamp(d.strftime("%Y%m%d " + '09:36:42'))
        end = pd.Timestamp(d.strftime("%Y%m%d " + '09:38:53'))
        chooser = APIChooser(self.apiset, orprefs=orprefs)
        for i in range(REPEATS):
            chooser.apiChooserList(start, end)
            if chooser.api:
                intraday = chooser.apiChooser()
                meta, df, ma = intraday(symbol, start, end, minutes)
                if not df.empty:
                    print(i + 1, ' ', end='')
                else:
                    print()
                    print(meta)
                    print()
            else:
                print()
                print('Call number', i)
                for rule in chooser.violatedRules:
                    print(rule)

    def test_get_intraday(self):
        '''
        Test that it rolls over when there are 2 members of APIPrefs and the
        first one fails. Note that this will fail if one of the APIS has exhausted
        its limit today (or fails some other rule)
        SO ... if this test follows extensive testing of APIS
        '''
        # First exhaust the 1 minute quota of AlphaVantage
        avonly = APIChooser(self.apiset, orprefs=['av'])
        d = util.getPrevTuesWed(pd.Timestamp.now())
        symbol = 'TSLA'
        start = pd.Timestamp(d.strftime("%Y%m%d " + '09:36:42'))
        end = pd.Timestamp(d.strftime("%Y%m%d " + '10:38:53'))
        minutes = 5

        for i in range(20):
            meta, df, ma = avonly.get_intraday(symbol, start, end, minutes)
            if df.empty:
                break

        # Now create new APIChoosers and test that the call rolls over
        for token in ['bc', 'fh']:
            chooser = APIChooser(self.apiset, orprefs=['av', token])
            meta, df, ma = chooser.get_intraday(symbol, start, end, minutes)
            if df.empty:
                logging.info(meta)
            msg = f"Failed to retrieve data from {token}. This could be normal operation or not. Its an http call."
            self.assertTrue(not df.empty, msg)


def notmain():
    t = TestAPIChooser()
    # t.test_apiChooserLimitReached()
    t.test_get_intraday()


def main():
    unittest.main()


if __name__ == '__main__':
    notmain()
    # main()
