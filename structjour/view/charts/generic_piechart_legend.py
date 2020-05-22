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
A bar chart to show pnl from trades

@author: Mike Petersen

@creation_date: April 21, 2020
'''
from structjour.view.charts.chartbase import ChartBase


def autopct_generator(limit):
    def inner_autopct(pct):
        return ('%.2f%%' % pct) if pct > limit else ''
    return inner_autopct


class Piechart(ChartBase):
    '''
    A Qt embedded matplotlib piechart. Uses the __init__() of ChartBase.

    ChartBase.__init__() params:
    ----------------------------------------------------------------------------------
    :params chartData: A subclass of ChartDataBase. The data for this particular chart
    :params parent: QWidget parent class
    :params width: matplot lib figure.width
    :params height: matplot lib figure.height
    :params dpi: matplot lib figure.dpi
    '''

    def plot(self):
        self.chartData.getChartUserData()
        self.axes.clear()
        patches, text1, text2 = self.axes.pie(self.chartData.data, labels=self.chartData.labels, autopct=autopct_generator(3), shadow=True, startangle=45)

        ncol = 1
        if len(self.chartData.legendLabels) > 15:
            ncol = len(self.chartData.legendLabels) // 10
        self.axes.legend(patches, zip(self.chartData.legendLabels, self.chartData.legendData), loc='center right', bbox_to_anchor=(-0.1, 1.), fontsize=8, ncol=ncol)
        self.axes.set_title(self.chartData.title)
        self.draw()
