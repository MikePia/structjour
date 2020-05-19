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

from structjour.view.charts.chartbase import ChartBase
from structjour.view.charts.chartdatabase import BarchartData


class BarChart(ChartBase):
    '''
    A Qt embedded matplotlib barchart. Uses the __init__() of ChartBase.
    The first argument to the constructor must be a type BarChartData, a
    subclass of ChartDataBase
    '''

    def setChartData(self, chartData):
        assert isinstance(chartData, BarchartData)
        self.setChartData(chartData)

    def plot(self):
        self.chartData.getChartUserData()

        x = range(len(self.chartData.neg))
        # d = pd.Timestamp(self.chartData.date)

        width = min(2 + len(self.chartData.neg) * 3 / 8, 15)
        print("Width:", width)
        # plt.rcParams['figure.figsize'] = (width, 5)
        self.figure.set_figwidth(width, forward=True)
        self.figure.set_figheight(5, forward=True)
        # self.figure.set_figwidth(15)
        # ax = self.figure.add_subplot(111)
        self.axes.clear()
        self.axes.bar(x, self.chartData.neg, width=0.9, color='crimson')
        self.axes.bar(x, self.chartData.pos, width=0.9, color='limegreen')
        self.axes.set_xticks(x)
        self.axes.set_xticklabels(self.chartData.names)
        for label in self.axes.get_xticklabels():
            label.set_rotation(-45)
            label.set_fontsize(8)
        self.figure.subplots_adjust(bottom=.175)

        self.axes.set_title(self.chartData.title)
        self.draw()
