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
Chart to show pnls of trades or groups of trades

@author: Mike Petersen

@creation_date: May 27, 2020
'''
from structjour.view.charts.chartdatabase import BarchartData
from structjour.models.trademodels import TradeSum
from structjour.models.meta import ModelBase


class MultiTradeProfit_BarchartData(BarchartData):
    def __init__(self, cud, limit=20, grouptrades=1):
        '''
        Arguments will summarize the user selections
        '''
        super().__init__(cud)

        self.limit = limit

    def getChartUserData(self):
        if self.chartInitialized is False:
            self.chartInitialized = True
            return
        ModelBase.connect(new_session=True)
        self.query = ModelBase.session.query(TradeSum).order_by(TradeSum.date.asc(), TradeSum.start.asc())
        self.runFilters()
        # self.query = self.query.all()

        # self.query = self.query.limit(self.limit)
        accounts = self.cud['accounts'] if self.cud['accounts'] else 'All'
        if self.cud['inNumSets'] > 0:
            pnls, dates = self.getProfitInNumGroups(self.query.all(), self.cud['inNumSets'])
            self.title = f'Trades in groups of {self.cud["inNumSets"]} trades in {accounts} accounts'
        elif self.cud['inTimeGroups'] is not None:
            pnls, dates = self.groupByTime(self.query.all(), self.cud['inTimeGroups'])
            self.title = f'Trades: {self.cud["titleBit"]} in {accounts} accounts'

        self.labels = dates
        self.data = pnls
        self.getFormatGraphArray()
