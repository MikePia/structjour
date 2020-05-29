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
An instance class to create a pie chart

@author: Mike Petersen

@creation_date: May 29, 2020
'''

from structjour.view.charts.chartdatabase import PiechartLegendData
from structjour.models.trademodels import TradeSum


class StrategyPercentages_PiechartData(PiechartLegendData):
    '''
    An instance class for a pie chart
    '''
    def getChartUserData(self):
        self.query = TradeSum.getDistinctStratsQuery()
        self.runFilters()
        strats = self.stratquery.all()
        total = sum([x[1] for x in strats if x[0] != ''])
        # threshhold is a percentage of the total. 1% in this case
        threshold = total * .03

        self.labels = [x[0] if x[1] > threshold else '' for x in strats if x[0] is not None]
        self.legendLabels = [x[0] for x in strats if x[0] is not None]
        self.data = [x[1] for x in strats if x[0] is not None]
        self.legendData = ['{:0.2f}%'.format(x * 100 / sum(self.data)) for x in self.data]
        self.title = "Strategies used"
        if self.cud['strategies2']:
            self.title += " (excluding no strategy)"
        len(self.labels), len(self.data), len(self.legendLabels), len(self.legendData)


def doStuff():
    cdb = StrategyPercentages_PiechartData({})
    cdb.getChartUserData()


if __name__ == '__main__':
    doStuff()
