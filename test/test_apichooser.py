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
import numpy as np
import unittest
from structjour.stock import utilities as util

from structjour.stock.apichooser import APIChooser

from PyQt5.QtCore import QSettings


class TestAPIChooser(unittest.TestCase):

    def test_apiChooser(self):
        '''
        Test the method FinPlot.apiChooser for the same interface in each api
        '''
        apiset = QSettings('zero_substance/stockapi', 'structjour')
        chooser = APIChooser(apiset)
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
                print('Skipped {api} at {start} to {end} because...')
                for rule in result[1]:
                    print(rule)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
