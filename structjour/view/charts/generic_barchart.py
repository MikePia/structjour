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

        x = range(len(self.chartData.neg))
        # d = pd.Timestamp(self.chartData.date)

        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.bar(x, self.chartData.neg, width=0.9, color='crimson')
        ax.bar(x, self.chartData.pos, width=0.9, color='limegreen')
        ax.set_xticks(x)
        ax.set_xticklabels(self.chartData.names)
        for label in ax.get_xticklabels():
            label.set_rotation(-45)
            label.set_fontsize(8)
        self.figure.subplots_adjust(bottom=.175)
        ax.set_title(self.chartData.title)
        self.draw()
