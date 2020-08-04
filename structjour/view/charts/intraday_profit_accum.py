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
A a filled line graph to show accumulating intraday profit

@author: Mike Petersen

@creation_date: April 1, 2020
'''
# import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
from pandas.plotting import register_matplotlib_converters

# from structjour.models.trademodels import TradeSum


class Canvas(FigureCanvas):
    '''
    Create a intraday profit chart showing accumulating profit.
    '''
    def __init__(self, df, account, parent=None, width=5, height=5, dpi=100):
        '''
        :params df: A DataFrame columns [date, pnl]. The pnl column should be the intraday
        accumulation of pnl
        :params account: The account name for use in the chart title
        '''
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # self.daDate = daDate
        self.account = account
        self.df = df

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        self.plot()

    def plot(self):
        register_matplotlib_converters()
        d = self.df.iloc[0]['date']
        # d = pd.Timestamp(self.daDate)
        title = f'Accumulating profit: {self.account}, {d.strftime("%B %d, %Y")}'

        ax = self.figure.add_subplot(111)
        ax.clear()
        xdates = [x.strftime("%H:%M:%S") for x in self.df['date']]
        ax.plot(xdates, self.df['pnl'], color='#666666', linestyle='--', label="accumulating pnl")
        ax.fill_between(xdates, self.df['pnl'], 0, where=(self.df['pnl'] > 0), color='chartreuse', alpha=0.25)
        ax.fill_between(xdates, self.df['pnl'], 0, where=(self.df['pnl'] <= 0), color='red', alpha=0.25)
        
        ax.legend()
        
        ax.set_xlabel('Time of day')
        ax.set_ylabel('$ USD')
        self.figure.tight_layout()
        # ax.set_xticks(x)
        # ax.set_xticklabels(names[self.account])
        for label in ax.get_xticklabels():
            label.set_rotation(-45)
            label.set_fontsize(8)

        fmt = '${x:,.0f}'
        tick = ticker.StrMethodFormatter(fmt)
        ax.yaxis.set_major_formatter(tick)
        self.figure.subplots_adjust(top=.9, bottom=.25)
        ax.set_title(title)
        self.draw()
