# Structjour -- a daily trade review helper
# Copyright (C) 2020 Zero Substance Trading
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
Chart to show pnls of trades or groups of trades

@author: Mike Petersen

@creation_date: May 29, 2020
'''
from structjour.view.charts.chartdatabase import BarchartData
from structjour.models.trademodels import TradeSum
# from structjour.models.meta import ModelBase


class StrategyAverage_BarchartData(BarchartData):
    def __init__(self, cud):
        '''
        Arguments will summarize the user selections
        '''
        super().__init__(cud)
        self.autolocate = False
        self.rotation = -90

    def getChartUserData(self):
        '''
        Getting an array of queries will allow the devel of digging down into each candle
        '''
        stratQueries = TradeSum.getDistinctStratAvgPnlQuery()
        self.alldata = []
        self.labels = []
        count = 0
        for i, (strat, squery) in enumerate(stratQueries):

            stratQueries[i][1] = self.runFiltersOnQuery(squery).all()

            if len(stratQueries[i][1]) == 0: continue

            self.alldata.append([stratQueries[i][0]])
            self.alldata[count].append(sum([x.pnl if isinstance(x.pnl, (float, int)) else 0 for x in stratQueries[i][1]]) / len(stratQueries[i][1]))
            count += 1

        self.alldata.sort(reverse=True, key=lambda x: x[1])
        # self.query = self.query.all()

        self.labels = [x[0] for x in self.alldata]
        self.data = [x[1] for x in self.alldata]
        self.title = f'Average PnL per Strategy in {self.cud["accounts"]} accounts'
        self.getFormatGraphArray()


if __name__ == '__main__':
    sab = StrategyAverage_BarchartData({})
    sab.getChartUserData()
    print()
