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
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from structjour.models.trademodels import TradeSum


class Canvas(FigureCanvas):
    def __init__(self, daDate, account, parent=None, width=5, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.daDate = daDate
        self.account = account

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        self.plot()

    def getFormatGraphArray(self, arr):
        neg = [round(x, 2) if isinstance(x, (float, int)) and x < 0 else 0 for x in arr]
        pos = [round(x, 2) if isinstance(x, (float, int)) and x >= 0 else 0 for x in arr]
        return neg, pos

    def plot(self):
        names, profits = TradeSum.getNamesAndProfits(self.daDate)

        neg, pos = self.getFormatGraphArray(profits[self.account])
        x = range(len(neg))
        d = pd.Timestamp(self.daDate)
        title = f'Profits in {self.account} account on {d.strftime("%B %d, %Y")}'

        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.bar(x, neg, width=0.9, color='crimson')
        ax.bar(x, pos, width=0.9, color='limegreen')
        ax.set_xticks(x)
        ax.set_xticklabels(names[self.account])
        for label in ax.get_xticklabels():
            label.set_rotation(-45)
            label.set_fontsize(8)
        self.figure.subplots_adjust(bottom=.2)
        ax.set_title(title)
        self.draw()
