'''
A couple plot methods driven by a chosen live data source. The charts available will be
single day minute charts (1,5, 10 min etc)
@author: Mike Petersen

@creation_date: 1/13/19
'''
import datetime as dt
import os
import random
import re

import pandas as pd

import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import markers, style
from matplotlib.ticker import FuncFormatter
from mpl_finance import candlestick_ohlc

from PyQt5.QtCore import QSettings

from journal.stock import myalphavantage as mav
from journal.stock import mybarchart as bc
from journal.stock import myib as ib
from journal.stock import myiex as iex
from journal.stock.utilities import getMASettings

# pylint: disable = C0103, W0603

FILL = 2


def dummyName(fp, symb, tradenum, begin, end, outdir='out'):
    '''
    This is a method function for use in developement. It will probably move up in the
        heirarchy to the inclusive program. Instructive to see all the elements that need
        go into this name.
    :params fp: FinPlot
    :params base: figure name icluding file type
    :params tradenum: An int or string indicating the trade number for the reporting period.
    :params symb: The stock ticker
    :params begin: Time date object or time string for the beginning of the chart
    :params end: End time date object or time string for the end of the chart
    :return: A string name
    :raise ValueError: If tradenum cannot be cnverted to a string representation of an int.
    :raise ValueError: If either begin or end are not time objects or strings.
    '''
    global FILL

    try:
        int(tradenum)
        tradenum = str(tradenum).zfill(FILL)
    except ValueError:
        raise ValueError(
            "Unable to convert tradenum to string representation of an int")

    try:
        begin = pd.Timestamp(begin)
    except ValueError:
        raise ValueError(
            f'(begin {begin}) cannot be converted to a datetime object')

    try:
        end = pd.Timestamp(end)
    except ValueError:
        raise ValueError(
            f'(end {end}) cannot be converted to a datetime object')
    begin = begin.strftime(fp.format)
    end = end.strftime(fp.format)
    name = f'{fp.base}{tradenum}_{symb}_{begin}_{end}_{fp.api}{fp.ftype}'

    name = os.path.join(outdir, name)

    return name


class FinPlot:
    '''
    Plot stock charts using single day minute interval charts
    '''

    def __init__(self, mplstyle='dark_background'):

        self.apiset = QSettings('zero_substance/stockapi', 'structjour')
        self.chartSet = QSettings('zero_substance/chart', 'structjour')
        self.style = self.chartSet.value('chart')
        self.style = None if self.style == 'No style' else self.style
        self.gridlines = self.getGridLines()
        self.markercolorup = self.chartSet.value('markercolorup', 'g')
        self.markercolordown = self.chartSet.value('markercolordown', 'r')
        self.interactive = self.chartSet.value('interactive', False, bool)
        self.legend = self.chartSet.value('showlegend', False, bool)

        # Pieces of the file name for the next FinPlot graph, format and base should rarely change.
        p = self.apiset.value('APIPref')
        if p:
            p = p.replace(' ', '')
            self.preferences = p.split(',')
        else:
            self.preferences = ['ib', 'bc', 'av', 'iex']
        self.api = self.preferences[0]

        self.ftype = '.png'
        self.format = "%H%M"
        self.base = 'trade'
        self.adjust = dict()
        self.setadjust()

        # data structure [entry, cande, minutes, tix]
        # entry price, nth candle, interval time index value
        # Currently using the candle index instead of the time index
        self.entries = []
        self.exits = []

    def getGridLines(self):
        y = self.chartSet.value('gridh', False, bool)
        x = self.chartSet.value('gridv', False, bool)
        val = (True, 'both') if x and y else (True,'x') if x else (True,'y') if y else (None, None)
        return val

    def volFormat(self, vol, pos):
        if vol < 1000:
            return vol
        elif vol < 1000000:
            vol = vol/1000
            vol = '{:0.1f}K'.format(vol)
            return vol
        elif vol < 1000000000:
            vol = vol/1000000
            vol = '{:0.1f}M'.format(vol)
            return vol
        elif vol < 1000000000000:
            vol = vol/1000000000
            vol = '{:0.1f}B'.format(vol)
            return vol
        else:
            vol = vol/1000000000000
            vol = '{:0.1f}Tr'.format(vol)
            return vol

    def setticks(self, interval, numcand):
        '''utility for Formatter'''
        major = []
        if interval == 10:
            major = [0, 20, 40]
        elif interval < 3:
            major = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
            if numcand > 60:
                major = [0, 15, 30, 45]
        elif interval < 10:
            major = [0, 15, 30, 45]
        elif interval < 20:
            major = [0, 30]
        else:
            major = [0]
        return major

    def matchFont(self, nm, default='arial$'):
        '''
        Retrieve font names from matplotlib matching the regex term nm. Search is not case dependent
        :params nm: The regex search parameter. To remove the font variants try adding $,
            e.g. 'arial$'
        :params default: A default font to return
        :return: A list of matching fonts or the default font if nm has no match
        '''
        nm = nm.lower()
        retList = []
        g = list({f.name for f in fm.fontManager.ttflist})
        g.sort()
        for gg in g:
            if re.search(nm, gg.lower()):
                retList.append(gg)
        if not retList:
            retList = (self.matchFont(default))
        return retList

    def apiChooserList(self, start, end, api=None):
        '''
        Given the current list of apis as av, bc, iex, and ib, determine if the given api will
            likely return data for the given times.
        :params start: A datetime object or time stamp indicating the intended start of the chart.
        :params end: A datetime object or time stamp indicating the intended end of the chart.
        :params api: Param must be one of mab, bc, iex, or ib. If given, the return value in
            (api, x, x)[0] will reflect the bool result of the api
        :return: (bool, rulesviolated, suggestedStocks) The first entry is only valid if api is
            an argument.

        '''
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)
        n = pd.Timestamp.now() + dt.timedelta(0, 60*120)        # Adding 2 hours for NY time

        violatedRules = []
        suggestedApis = self.preferences
        # nopen = dt.datetime(n.year, n.month, n.day, 9, 30)
        nclose = dt.datetime(n.year, n.month, n.day, 16, 30)

        # Rule 1 Barchart will not return todays data till 16:30
        # Rule 1a Barchart will not return yesterdays data after 12 till 1630
        tradeday = pd.Timestamp(start.year, start.month, start.day)
        todayday = pd.Timestamp(n.year, n.month, n.day)
        yday = todayday - pd.Timedelta(days=1)
        y = pd.Timestamp(yday.year, yday.month, yday.day, 11, 59)
        if tradeday == todayday and n < nclose and 'bc' in suggestedApis:
            suggestedApis.remove('bc')
            violatedRules.append(
                'Barchart free data will not return todays data till 16:30')
        if tradeday == yday and end > y and n < nclose and 'bc' in suggestedApis:
            suggestedApis.remove('bc')
            violatedRules.append(
                'Barchart free data will not yesterdays data after 12 till today at  16:30')

        # Rule 2 No support any charts greater than 7 days prior till today
        if n > start:
            delt = n - start
            if delt.days > 6 and 'av' in suggestedApis:
                suggestedApis.remove('av')
                lastday = n-pd.Timedelta(days=6)
                violatedRules.append('AlphaVantage data before {} is unavailable.'.format(
                    lastday.strftime("%b %d")))

        # Rule 3 Don't call ib if its not connected
        if 'ib' in suggestedApis and not ib.isConnected():
            suggestedApis.remove('ib')
            violatedRules.append('IBAPI is not connected.')

        # Rule 4 No data is available for the future
        if start > n:
            suggestedApis = []
            violatedRules.append('No data is available for the future.')

        api = api in suggestedApis if api else False

        return(api, violatedRules, suggestedApis)

    def apiChooser(self):
        '''
        Get a data method
        '''
        # self.api = api
        if self.api == 'bc':
            # retrieves previous biz day until about 16:30
            return bc.getbc_intraday
        if self.api == 'av':
            return mav.getmav_intraday
        if self.api == 'ib':
            return ib.getib_intraday
        if self.api == 'iex':
            return iex.getiex_intraday

        return None

    def setTimeFrame(self, begin, end, interval):
        '''
        Set the amount of time before the first transaction and after the last transaction
        to include in the chart. This may include some trend examination in the future.
        For now just add some time based on the time of day and the candle interval
        :params begin: A datetime object or time string for the first transaction time.
        :params end: A datetime object or time string for the last transaction time.
        :params interval: The candle length.
        return: A tuple (begin, end) for the suggested chart begin and end times.
        '''
        begin = pd.Timestamp(begin)
        end = pd.Timestamp(end)
        beginday = pd.Timestamp(begin.year, begin.month, begin.day, 0, 0)
        endday = pd.Timestamp(end.year, end.month, end.day, 23, 59)
        xtime = 0
        if interval < 5:
            xtime = 20
        elif interval < 7:
            xtime = 40
        elif interval < 20:
            xtime = 60
        else:
            xtime = 180
        begin = begin - dt.timedelta(0, xtime*60)
        end = end + dt.timedelta(0, xtime*60)

        # If beginning is before 10:15-- show the opening
        mopen = dt.datetime(beginday.year, beginday.month, beginday.day, 9, 30)
        orbu = dt.datetime(beginday.year, beginday.month, beginday.day, 10, 15)
        mclose = dt.datetime(endday.year, endday.month, endday.day, 16, 0)

        begin = mopen if begin <= orbu else begin
        end = mclose if end >= mclose else end

        # Trim pre and post market times  XXXX Leave
        # begin = mopen if mopen > begin else begin
        # end = mclose if mclose < end else end

        return begin, end

    def setadjust(self, left=.04, bottom=.14, top=.96, right=.89):
        '''
        Adjust the margins of the graph. Use self.interactive=True to find the correct settings
        '''
        self.adjust['left'] = left
        self.adjust['right'] = right
        self.adjust['top'] = top
        self.adjust['bottom'] = bottom

    def graph_candlestick(self, symbol, start=None, end=None, minutes=1,
                          dtFormat="%H:%M", save='trade'):
        '''
        Currently this will retrieve the data using apiChooser. Set self.preferences to limit
            acceptible apis. To place tx markers, set (or clear) fp.entries and fp.exits prior
            to calling
        :params symbol: The stock ticker
        :params start: A datetime object or time string for the begining of the graph. The day must
                    be within the last 7 days. This may change in the future.
        :params end: A datetime object or time string for the end of a graph. Defaults to whatever
                    the call gets.
        :params dtFormat: a strftime formt to display the dates on the x axis of the chart
        :parmas st: The matplot lib style for style.use(st). If fp.randomStyle is set,
                    it overrides.
        '''

        start = pd.Timestamp(start)
        end = pd.Timestamp(end)
        if self.style:
            style.use(self.style)

        ################ Prepare data ##############
        # Get the data and prepare the DtaFrames from some stock api
        meta, df, maDict = (self.apiChooser())(
            symbol, start=start, end=end, minutes=minutes)
        if df.empty:
            if not isinstance(meta, int):
                self.apiset.setValue('errorCode', str(meta['code']))
                self.apiset.setValue('errorMessage', meta['message'])
            return None
        df['date'] = df.index

        df['date'] = df['date'].map(mdates.date2num)

        df_ohlc = df[['date', 'open', 'high', 'low', 'close']]
        df_volume = df[['date', 'volume']]
        ################ End Prepare data ##############
        ####### PLOT and Graph #######
        colup = self.chartSet.value('colorup', 'g')
        coldown = self.chartSet.value('colordown', 'r')
        ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
        ax1.grid(b=self.gridlines[0], which='major', axis=self.gridlines[1])

        ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1,
                               colspan=1, sharex=ax1)
        fig = plt.gcf()
        fig.subplots_adjust(hspace=0)

        # candle width is a percentage of a day
        width = (minutes*35)/(3600 * 24)
        candlestick_ohlc(ax1, df_ohlc.values, width, colorup=colup, colordown=coldown, alpha=.99)

        for date, volume, dopen, close in zip(df_volume.date.values, df_volume.volume.values,
                                              df_ohlc.open.values, df_ohlc.close.values):
            color = colup if close > dopen else 'k' if close == dopen else coldown
            ax2.bar(date, volume, width, color=color)
        ####### END PLOT and Graph #######
        ####### ENTRY MARKER STUFF #######
        markersize = self.chartSet.value('markersize', 90)
        edgec = self.chartSet.value('markeredgecolor', '#000000')
        alpha = float(self.chartSet.value('markeralpha', 0.5))
        for entry in self.entries:
            e = entry[3]
            if entry[1] < 0 or entry[1] > (len(df_ohlc)-1):
                continue
            x = df_ohlc.index[entry[1]]
            y = entry[0]
            if entry[2] == 'B':
                facec = self.chartSet.value('markercolorup', 'g')
                mark = '^'
            else:
                facec = self.chartSet.value('markercolordown', 'r')
                mark = 'v'
            l = ax1.scatter(x, y, color=facec, marker=markers.MarkerStyle(
                marker=mark, fillstyle='full'), s=markersize, zorder=10)
            l.set_edgecolor(edgec)
            l.set_alpha(alpha)
        ####### END MARKER STUFF #######
        ##### TICKS-and ANNOTATIONS #####

        ax1.yaxis.tick_right()
        ax2.yaxis.tick_right()
        # ax1.grid(True, axis='y')

        plt.setp(ax1.get_xticklabels(), visible=False)
        for label in ax2.xaxis.get_ticklabels():
            label.set_rotation(-45)
            label.set_fontsize(8)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter(dtFormat))
        ax2.yaxis.set_major_formatter(FuncFormatter(self.volFormat))
        plt.locator_params(axis='y', tight=True, nbins=2)

        numcand = ((end-start).total_seconds()/60)//minutes
        ax2.xaxis.set_major_locator(mdates.MinuteLocator(
            byminute=self.setticks(minutes, numcand)))

        idx = int(len(df_ohlc.date)*.39)

        ax1.annotate(f'{symbol} {minutes} minute', (df_ohlc.date[idx], df_ohlc.low.max()),
                     xytext=(0.4, 0.85), textcoords='axes fraction', alpha=0.35, size=16)
        ##### END TICKS-and ANNOTATIONS #####
        ####### ma, ema and vwap #######
        MA1 = 9
        MA2 = 20
        MA3 = 50
        MA4 = 200
        MA5 = 'vwap'
        if maDict:
            maSetDict = getMASettings()
            for ma in maSetDict[0]:
                if not ma in maDict.keys():
                    continue
                ax1.plot(df_ohlc.date, maDict[ma], lw=1, color=maSetDict[0][ma][1], label=f'{ma}MA')
            if 'vwap' in maDict.keys():
                ax1.plot(df_ohlc.date, maDict['vwap'], lw=1, color=maSetDict[1][0][1], label='VWAP')
        if self.legend:
            leg = ax1.legend()
            leg.get_frame().set_alpha(0.35)
        ##### Adjust margins and frame
        top = df_ohlc.high.max()
        bottom = df_ohlc.low.min()
        margin=(top-bottom) * .08
        ax1.set_ylim(bottom=bottom-margin, top=top+(margin*2))

        ad = self.adjust
        plt.subplots_adjust(left=ad['left'], bottom=ad['bottom'], right=ad['right'],
                            top=ad['top'], wspace=0.2, hspace=0)

        if self.chartSet.value('interactive', False, bool):
            # plt.savefig('out/figure_1.png')
            plt.show()
        count = 1
        saveorig = save
        while os.path.exists(save):
            s, ext = os.path.splitext(saveorig)
            save = '{}({}){}'.format(s, count, ext)
            count = count + 1

        fig.savefig(save)
        return save


def localRun():
    '''Just running through the paces'''

    # tdy = dt.datetime.today()

    fp = FinPlot()
    # odate = dt.datetime(2019, 1, 19, 9, 40)
    # cdate = dt.datetime(2019, 1, 19, 16, 30)
    # interval = 60


if __name__ == '__main__':
    localRun()
