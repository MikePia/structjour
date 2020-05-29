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

@creation_date: April 1, 2020
'''
# import pandas as pd
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import matplotlib.ticker as ticker
from structjour.view.charts.chartbase import ChartBase
from structjour.view.charts.chartdatabase import BarchartData


class BarChart(ChartBase):
    '''
    A Qt embedded matplotlib barchart. Uses the __init__() of ChartBase.

    ChartBase.__init__() params:
    ----------------------------------------------------------------------------------
    :params chartData: A subclass of ChartDataBase. The data for this particular chart
    :params parent: QWidget parent class
    :params width: matplot lib figure.width
    :params height: matplot lib figure.height
    :params dpi: matplot lib figure.dpi
    '''

    def setChartData(self, chartData):
        assert isinstance(chartData, BarchartData)
        self.setChartData(chartData)

    def plot(self):
        self.chartData.getChartUserData()

        if self.chartData.cud['inNumSets'] >= 1:
            xdates = [x.strftime("%m/%d/%y  %H:%M") for x in self.chartData.labels]
        else:
            xdates = [x.strftime("%b %d, %Y") for x in self.chartData.labels]

        assert len(self.chartData.labels) == len(self.chartData.neg)
        # x = range(len(self.chartData.neg))
        # d = pd.Timestamp(self.chartData.date)

        width = min(2 + len(self.chartData.neg) * 3 / 8, 15)
        self.figure.set_figwidth(width, forward=True)
        self.figure.set_figheight(5, forward=True)
        self.axes.clear()

        self.axes.bar(xdates, self.chartData.neg, width=0.9, color='crimson')
        self.axes.bar(xdates, self.chartData.pos, width=0.9, color='limegreen')
        self.axes.set_xticks(xdates)

        self.axes.xaxis.set_major_locator(ticker.MaxNLocator(nbins='auto'))
        self.axes.xaxis.set_minor_locator(ticker.MaxNLocator(nbins='auto'))
        # self.axes.set_xticklabels(self.chartData.labels)
        for label in self.axes.get_xticklabels():
            label.set_rotation(-45)
            label.set_fontsize(8)

        fmt = '${x:,.0f}'
        tick = ticker.StrMethodFormatter(fmt)
        self.axes.yaxis.set_major_formatter(tick)
        self.axes.yaxis.grid()
        self.figure.subplots_adjust(bottom=.23)

        self.axes.set_title(self.chartData.title)
        self.draw()
