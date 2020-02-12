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
First try at trade summary using a grid Layout

author: Mike Petersen

created: September 1, 2018
'''

import os
import datetime as dt

import numpy as np
import pandas as pd

from PyQt5.QtCore import QSettings

from structjour.colz.finreqcol import FinReqCol
from structjour.dfutil import DataFrameUtil
from structjour.stock.graphstuff import FinPlot

# pylint: disable=C0103


# Use to access columns in the (altered) input dataframe, known on this page as df.
# Use sf (SumReqFields instance) to access
# columns/data for the summary trade dataframe, known on this page as TheTrade.
frc = FinReqCol()



class SumReqFields:
    '''
    Manage the required columns, cell location and namedStyle for the summary aka TheTradeObject
    and TheTradeStyle. There are three types of data represented here.
    :attribute self.rc (The data): The data is held in the locations represented by self.rc and the
        associatied dict keys. The keys can be of course accessed as strings or as attributes such
        as self.name. The latter should be used to maintain portable input files. This data will be
        placed in the workbooks in the trade summaries. The rc columns are used in a DataFrame (aka
        TheTrade) that summarizes each single trade with a single row. This summary information
        includes information from the user, target, stop, strategy, notes, saved images etc.
    :attribute self.tfcolumns (The style): This the the tradeformat excel form. The form can be 
        re-shaped by changing this data structure. These will style workbook in the trade summaries
    :attribute self.tfformulas (hybrid data): These entries will override the rc data. The entries
        represent excel formulas. Most formulas require a mapping of cells done just after the cell
        styling.

    :
    NOTES on self.tfcolumns and tfformulas(Summary trade form):
    tfcolumns, short for tradeFormatColumns, specifically defines the trade summary form.
    Each named dict entry contains its location in relation to the anchor at the top left
    and a named style for that cell or group of merged cells. Merged locations have a
    list of two tuples (e.g. self.name) Single cells contain a single tuple (e.g.
    self.targhead).  To add a style to the TradeSummary, define the NamedStyle in
    journal.tradestyle.TradeFormat. Follow the pattern of the others. Then place the name
    in tfcolumns with the others. Excel cell formulas (tfformulas) are created seperately and
    usually require cell translation, done just after the style creation usually. If no cell
    translation is required, the workbook insertion can be handled as a regular rc entry.

    :Expanding to include trade_sum db columns
    '''

    def __init__(self):
        ''' rcvals are the actual column titles
        rckeys are the abstracted names for use with all file types
        The abstraction provides code style consistency (like ReqCol and FinReqCol)
            and a means to change the whole thing managed here alone'''
        # TODO (maybe) make these things pluggable to alow the creation of any shape and style by
        # plugging in a module. Might possibe by plugging in tfcoumns and tfformulas alone, and
        # leaving the rest
        # pylint: disable = C0301
        rcvals = ['Name', 'Account', 'Strategy', 'Link1',
                  'P/LHead', 'PnL', 'StartHead', 'Start', 'DurHead', 'Duration', 'ShareHead', 'Shares', 'MktHead', 'MktVal',
                  'TargHead', 'Target', 'TargDiff', 'StopHead', 'StopLoss', 'SLDiff', 'RRHead', 'RR', 'MaxHead', 'MaxLoss',
                  'MstkHead', 'MstkVal', 'MstkNote',

                  'EntryHead', 'Entry1', 'Entry2', 'Entry3', 'Entry4', 'Entry5', 'Entry6', 'Entry7', 'Entry8',
                  'Exit1', 'Exit2', 'Exit3', 'Exit4', 'Exit5', 'Exit6', 'Exit7', 'Exit8',
                  'Time1', 'Time2', 'Time3', 'Time4', 'Time5', 'Time6', 'Time7', 'Time8',
                  'EShare1', 'EShare2', 'EShare3', 'EShare4', 'EShare5', 'EShare6', 'EShare7', 'EShare8',
                  'Diff1', 'Diff2', 'Diff3', 'Diff4', 'Diff5', 'Diff6', 'Diff7', 'Diff8',
                  'PL1', 'PL2', 'PL3', 'PL4', 'PL5', 'PL6', 'PL7', 'PL8',
                  'Explain', 'Notes', 'Date', 'Clean', 'id'
                  ]

        rckeys = ['name', 'acct', 'strat', 'link1',
                  'plhead', 'pl', 'starthead', 'start', 'durhead', 'dur', 'sharehead', 'shares', 'mkthead', 'mktval',
                  'targhead', 'targ', 'targdiff', 'stophead', 'stoploss', 'sldiff', 'rrhead', 'rr', 'maxhead', 'maxloss',
                  'mstkhead', 'mstkval', 'mstknote',

                  'entryhead', 'entry1', 'entry2', 'entry3', 'entry4', 'entry5', 'entry6', 'entry7', 'entry8',
                  'exit1', 'exit2', 'exit3', 'exit4', 'exit5', 'exit6', 'exit7', 'exit8',
                  'time1', 'time2', 'time3', 'time4', 'time5', 'time6', 'time7', 'time8',
                  'eshare1', 'eshare2', 'eshare3', 'eshare4', 'eshare5', 'eshare6', 'eshare7', 'eshare8',
                  'diff1', 'diff2', 'diff3', 'diff4', 'diff5', 'diff6', 'diff7', 'diff8',
                  'pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'pl6', 'pl7', 'pl8',
                  'explain', 'notes', 'date', 'clean', 'id'
                  ]

        dbvals = ['Name', 'Account', 'Strategy', 'Link1', 'PnL', 'Start', 'Duration', 'Shares',
                 'MktVal', 'Target', 'TargDiff', 'StopLoss', 'SLDiff', 'RR', 'MaxLoss', 'MstkVal',
                 'MstkNote', 'Explain', 'Notes', 'Date', 'id']

        dbkeys = ['name', 'acct', 'strat', 'link1', 'pl', 'start', 'dur', 'shares',
        'mktval', 'targ', 'targdiff', 'stoploss', 'sldiff', 'rr', 'maxloss', 'mstkval',
        'mstknote', 'explain', 'notes', 'date', 'id']

        self.tcols = dict(zip(dbkeys, dbvals))


        # This includes all the locations that are likely to have data associated with them.
        # Blank cells are added to tfcolumns. Tese have style, but no data. Each of the data
        # entries are added as attributes to maintain programming abstraction, minimize future
        # change.
        rc = dict(zip(rckeys, rcvals))

        # #Suggested way to address the columns for the TheTrade DataFrame.
        self.name = rc['name']
        self.acct = rc['acct']
        self.strat = rc['strat']
        self.link1 = rc['link1']

        self.plhead = rc['plhead']
        self.pl = rc['pl']

        self.starthead = rc['starthead']
        self.start = rc['start']

        self.durhead = rc['durhead']
        self.dur = rc['dur']

        self.sharehead = rc['sharehead']
        self.shares = rc['shares']

        self.mkthead = rc['mkthead']
        self.mktval = rc['mktval']

        self.targhead = rc['targhead']
        self.targ = rc['targ']
        self.targdiff = rc['targdiff']

        self.stophead = rc['stophead']
        self.stoploss = rc['stoploss']
        self.sldiff = rc['sldiff']

        self.rrhead = rc['rrhead']
        self.rr = rc['rr']

        self.maxhead = rc['maxhead']
        self.maxloss = rc['maxloss']

        self.mstkhead = rc['mstkhead']
        self.mstkval = rc['mstkval']
        self.mstknote = rc['mstknote']

        self.entryhead = rc['entryhead']
        self.entry1 = rc['entry1']
        self.entry2 = rc['entry2']
        self.entry3 = rc['entry3']
        self.entry4 = rc['entry4']
        self.entry5 = rc['entry5']
        self.entry6 = rc['entry6']
        self.entry7 = rc['entry7']
        self.entry8 = rc['entry8']

        self.exit1 = rc['exit1']
        self.exit2 = rc['exit2']
        self.exit3 = rc['exit3']
        self.exit4 = rc['exit4']
        self.exit5 = rc['exit5']
        self.exit6 = rc['exit6']
        self.exit7 = rc['exit7']
        self.exit8 = rc['exit8']

        self.time1 = rc['time1']
        self.time2 = rc['time2']
        self.time3 = rc['time3']
        self.time4 = rc['time4']
        self.time5 = rc['time5']
        self.time6 = rc['time6']
        self.time7 = rc['time7']
        self.time8 = rc['time8']

        self.eshare1 = rc['eshare1']
        self.eshare2 = rc['eshare2']
        self.eshare3 = rc['eshare3']
        self.eshare4 = rc['eshare4']
        self.eshare5 = rc['eshare5']
        self.eshare6 = rc['eshare6']
        self.eshare7 = rc['eshare7']
        self.eshare8 = rc['eshare8']

        self.diff1 = rc['diff1']
        self.diff2 = rc['diff2']
        self.diff3 = rc['diff3']
        self.diff4 = rc['diff4']
        self.diff5 = rc['diff5']
        self.diff6 = rc['diff6']
        self.diff7 = rc['diff7']
        self.diff8 = rc['diff8']

        self.pl1 = rc['pl1']
        self.pl2 = rc['pl2']
        self.pl3 = rc['pl3']
        self.pl4 = rc['pl4']
        self.pl5 = rc['pl5']
        self.pl6 = rc['pl6']
        self.pl7 = rc['pl7']
        self.pl8 = rc['pl8']

        self.explain = rc['explain']
        self.notes = rc['notes']
        self.date = rc['date']
        self.clean = rc['clean']
        self.id = rc['id']

        self.rc = rc
        self.columns = rc.values()

        self.tfcolumns = {
            self.name: [[(1, 1), (3, 2)], 'titleStyle'],
            self.acct: [[(4, 1), (6, 2)], 'titleStyle'],
            self.strat: [[(7, 1), (9, 2)], 'titleStyle'],
            self.link1: [[(10, 1), (12, 2)], 'linkStyle'],

            self.plhead: [[(1, 3), (1, 4)], 'titleLeft'],
            self.pl: [[(2, 3), (3, 4)], 'titleNumberRight'],
            self.starthead: [[(1, 5), (1, 6)], 'titleLeft'],
            self.start: [[(2, 5), (3, 6)], 'titleRight'],
            self.durhead: [[(1, 7), (1, 8)], 'titleLeft'],
            self.dur: [[(2, 7), (3, 8)], 'titleRight'],
            self.sharehead: [[(1, 9), (1, 10)], 'titleLeft'],
            self.shares: [[(2, 9), (3, 10)], 'titleRight'],
            self.mkthead: [[(1, 11), (1, 12)], 'titleLeft'],
            self.mktval: [[(2, 11), (3, 12)], 'titleNumberRight'],

            self.targhead: [(1, 13), 'normStyle'],
            self.targ: [(2, 13), 'normalNumber'],
            self.targdiff: [(3, 13), 'normStyle'],
            self.stophead: [(1, 14), 'normStyle'],
            self.stoploss: [(2, 14), 'normStyle'],
            self.sldiff: [(3, 14), 'normStyle'],
            self.rrhead: [(1, 15), 'normStyle'],
            self.rr: [(2, 15), 'normalFraction'],
            "ex1": [(3, 15), 'normStyle'],
            self.maxhead: [(1, 16), 'normStyle'],
            self.maxloss: [(2, 16), 'normStyle'],
            "ex2": [(3, 16), 'normStyle'],

            self.mstkhead: [[(1, 17), (1, 18)], 'normStyle'],
            self.mstkval: [[(2, 17), (3, 18)], 'titleNumberRight'],
            self.mstknote: [[(1, 19), (3, 20)], 'finalNoteStyle'],
            self.entryhead: [[(4, 3), (4, 8)], 'normStyle'],

            self.entry1: [(5, 3), 'normalNumberTopLeft'],
            self.entry2: [(6, 3), 'normalNumberTop'],
            self.entry3: [(7, 3), 'normalNumberTop'],
            self.entry4: [(8, 3), 'normalNumberTop'],
            self.entry5: [(9, 3), 'normalNumberTop'],
            self.entry6: [(10, 3), 'normalNumberTop'],
            self.entry7: [(11, 3), 'normalNumberTop'],
            self.entry8: [(12, 3), 'normalNumberTopRight'],

            self.exit1: [(5, 4), 'normalNumberLeft'],
            self.exit2: [(6, 4), 'normalNumberInside'],
            self.exit3: [(7, 4), 'normalNumberInside'],
            self.exit4: [(8, 4), 'normalNumberInside'],
            self.exit5: [(9, 4), 'normalNumberInside'],
            self.exit6: [(10, 4), 'normalNumberInside'],
            self.exit7: [(11, 4), 'normalNumberInside'],
            self.exit8: [(12, 4), 'normalNumberRight'],

            self.time1: [(5, 5), 'timeSubLeft'],
            self.time2: [(6, 5), 'timeSub'],
            self.time3: [(7, 5), 'timeSub'],
            self.time4: [(8, 5), 'timeSub'],
            self.time5: [(9, 5), 'timeSub'],
            self.time6: [(10, 5), 'timeSub'],
            self.time7: [(11, 5), 'timeSub'],
            self.time8: [(12, 5), 'timeSubRight'],

            self.eshare1:  [(5, 6), 'normalSubLeft'],
            self.eshare2:  [(6, 6), 'normalSub'],
            self.eshare3:  [(7, 6), 'normalSub'],
            self.eshare4:  [(8, 6), 'normalSub'],
            self.eshare5:  [(9, 6), 'normalSub'],
            self.eshare6:  [(10, 6), 'normalSub'],
            self.eshare7:  [(11, 6), 'normalSub'],
            self.eshare8:  [(12, 6), 'normalSubRight'],

            self.diff1:  [(5, 7), 'normalSubLeft'],
            self.diff2:  [(6, 7), 'normalSub'],
            self.diff3:  [(7, 7), 'normalSub'],
            self.diff4:  [(8, 7), 'normalSub'],
            self.diff5:  [(9, 7), 'normalSub'],
            self.diff6:  [(10, 7), 'normalSub'],
            self.diff7:  [(11, 7), 'normalSub'],
            self.diff8:  [(12, 7), 'normalSubRight'],

            self.pl1:  [(5, 8), 'normalSubNumberBottomLeft'],
            self.pl2:  [(6, 8), 'normalSubNumberBottom'],
            self.pl3:  [(7, 8), 'normalSubNumberBottom'],
            self.pl4:  [(8, 8), 'normalSubNumberBottom'],
            self.pl5:  [(9, 8), 'normalSubNumberBottom'],
            self.pl6:  [(10, 8), 'normalSubNumberBottom'],
            self.pl7:  [(11, 8), 'normalSubNumberBottom'],
            self.pl8:  [(12, 8), 'normalSubNumberBottomRight'],

            self.explain: [[(4, 9), (12, 14)], 'explain'],
            self.notes: [[(4, 15), (12, 20)], 'noteStyle']
        }

        # Set up the excel formulas for the trade summaries. The ones for Mistake Summary are in
        # their class
        # In this dict, the values are a list in which the first entry is the formula itsef
        # with format specifiers {} for the referenced addresses. For example, '={0}-{1}' will
        # translate to something like '=D145-D143' The rest of the list is the location of the
        # cells within the trade summary form (untranslated) at A1. Translate the
        # cell addresses then use format to replace the specifiers from summary data in the
        # openpyxl worksheet object for each trade.
        self.tfformulas = dict()
        self.tfformulas[self.targdiff] = ["={0}-{1}",
                                          self.tfcolumns[self.targ][0],
                                          self.tfcolumns[self.entry1][0]
                                          ]
        self.tfformulas[self.sldiff] = ["={0}-{1}",
                                        self.tfcolumns[self.stoploss][0],
                                        self.tfcolumns[self.entry1][0]
                                        ]
        self.tfformulas[self.rr] = ["=ABS({0}/{1})",
                                    self.tfcolumns[self.sldiff][0],
                                    self.tfcolumns[self.targdiff][0]
                                    ]
        self.tfformulas[self.maxloss] = ['=(LEFT({0},SEARCH(" ",{1},1)))*{2}',
                                         self.tfcolumns[self.shares][0][0],
                                         self.tfcolumns[self.shares][0][0],
                                         self.tfcolumns[self.sldiff][0]
                                         ]

        self.rc = rc
        self.columns = rc.values()

    def getStyles(self):
        '''Retrieves a list of the style names from tfcolumns'''
        _styles = []
        for v in list(self.tfcolumns.values()):
            _styles.append(v[1])

        df = pd.DataFrame(_styles, columns=['st'])
        return df['st'].unique()

    def maxcol(self):
        '''
        Maxcol() method will get the maximum column for the current TradeSummaries form as it is
        translated from column A.
        :return maxcol: As an int
        '''
        locs = [self.tfcolumns[x][0] for x in self.tfcolumns]
        maxcol = 1
        for loc in locs:
            if isinstance(loc, list):
                if loc[1][0] > maxcol:
                    maxcol = loc[1][0]
            elif loc[0] > maxcol:
                maxcol = loc[0]
        return maxcol

    def maxrow(self):
        '''
        Maxrow() method will get the maximum row for the current TradeSummaries form as it is
        translated from row 1.
        :return maxrow: As an int
        '''
        locs = [self.tfcolumns[x][0] for x in self.tfcolumns]
        maxrow = 1
        for loc in locs:
            if isinstance(loc, list):
                if loc[1][1] > maxrow:
                    maxrow = loc[1][1]
            elif loc[1] > maxrow:
                maxrow = loc[1]
        return maxrow


# global variable for use in this module
sf = SumReqFields()


class TheTradeObject:
    '''
    Note that this is called when opening a trade from a statment. 
    Create the flattened version of a trade summary, that is, take the multiple transactions included
    in the trade_sum table and flatten the info to one row for use in the Qt/excel/whatever form.
    Manages
    :PreRequisite: The original DtaFrame need be transformed where partial trades are combined into
    tickets and are combined into a list of dataframes (ldf), one list per trade. This includes the
    work of DefineTrades.processDBTrades().
    '''

    def __init__(self, df, interview, sf):
        '''
        Create a dataframe that includes all the summary material for review. Some
        of this data comes from the program and some of it comes from the user. The
        user will determine which parts to fill out from a couple of options.
        :params:df: A DataFrame that includes the transactions, or tickets,
            from a singel trade.
        '''

        self.interview = interview
        col = list(sf.tfcolumns.keys())
        col.append('Date')
        TheTrade = pd.DataFrame(columns=col)
        TheTrade = DataFrameUtil.addRows(TheTrade, 1)
        self.sf = sf

        ix = df.index[-1]
        ix0 = df.index[0]

        # TODO This list should be retrieved from TheStrategyObject
        strats = ['ORB', 'ABCD', 'VWAP Reversal', 'Bull Flag', 'Fallen Angel',
                  'VWAP False Breakout', 'VWAP Reversal', '15 Minute Reversal',
                  'VWAP MA trend', 'Other', 'Skip']
        side = df.loc[ix0][frc.side]
        self.df = df
        self.TheTrade = TheTrade
        self.ix = ix
        self.ix0 = ix0
        self.strats = strats
        self.side = side
        self.shares = 0
        self.chartSlot1 = None
        self.chartSlot2 = None
        self.chartSlot3 = None
        self.settings = QSettings('zero_substance', 'structjour')

    def runSummary(self, imageName):
        '''
        Populate a DataFrame (self.TheTrade) with all the trade summary information, one row per
        trade. The information will then populate the the openpyxl / excel Trade Summary. The user
        interview for target stoploss, and strategy happen in their respective methods.
        '''
        self.__setName()
        self.__setAcct()
        self.__setSum()
        self.__setStart()
        self.__setDur()
        self.__setMarketValue()

        self.__setShares()
        self.__setHeaders()
        self.__setExplainNotes()
        self.__blandSpaceInMstkNote()
        ret = self.__setEntries(imageName)

        # Add a column to manage the Qt mistake stuff
        self.TheTrade['clean'] = True
        return ret

    def getName(self):
        ''' Get df.Name column'''
        return self.TheTrade[self.sf.name]

    def __setName(self):
        self.TheTrade[self.sf.name] = self.df.loc[self.ix][sf.name]
        return self.TheTrade

    def __setAcct(self):
        self.TheTrade[self.sf.acct] = 'Live' if self.df.loc[self.ix][sf.acct].startswith(
            'U') else 'SIM'
        return self.TheTrade

    def __setSum(self):
        self.TheTrade[self.sf.pl] = self.df.loc[self.ix][frc.sum]
        return self.TheTrade

    def __setStart(self):
        self.TheTrade[self.sf.start] = self.df.loc[self.ix][sf.start]
        self.TheTrade[self.sf.date] = self.df.loc[self.ix][sf.date]
        return self.TheTrade

    # HACK ALERT The duration came out as an empty string on an older file so I added the
    # babysitting for empty strings
    def __setDur(self):
        '''
        Sets the duration delta to a nicely formatted string for humans. Return just the number of
        days if its 1 or more. Otherwise return something like: 1 hour, 4:34
        :raise: A couple of assertions could raise AssertionError. (Temporary for development)
        '''

        time = self.df.loc[self.ix][sf.dur]
        if isinstance(time, str):
            dur = time

        else:
            # programmer babysitter, remove after several months of success (3/12/19) Its here
            # because changes to this method exposed the possibility of untested error.

            assert isinstance(time, dt.timedelta)
            time = pd.Timedelta(time)
            assert time.components.days >= 0
            if time.components.days > 0:
                d = time.components.days
                dur = str(d) + ' days' if d > 1 else str(d) + \
                    ' day' if d == 1 else ''
                return dur
            h = time.components.hours
            m = time.components.minutes
            s = time.components.seconds

            dur = str(h) + ' hours, ' if h > 1 else str(h) + \
                ' hour, ' if h == 1 else ''
            dur += str(m) + ':' + str(s)
        self.TheTrade[self.sf.dur] = dur
        return self.TheTrade

    def getSharesDB(self):
        '''
        The DB statement has gotten rid of the 'Hold' entries. Determining a value for 
        how many shares a trade has to be re thought
        '''
        sf = self.sf
        ocs = self.df[frc.oc].unique()
        opens = list()
        Long = True if (self.df.iloc[0][frc.oc].find('O') >= 0 and (self.df.iloc[0][frc.shares] > 0)) or (
                        self.df.iloc[0][frc.oc].find('C') >= 0 and (self.df.iloc[0][frc.shares] < 0)) else False

        for oc in ocs:
            if oc.find('O') >= 0:
                if Long:
                    self.shares = self.shares = self.df[frc.bal].max()
                else:
                    self.shares = self.df[frc.bal].min()
                return self.shares

        self.shares = -self.df.iloc[0][frc.shares]
        return self.shares



    def getShares(self):
        '''
        Utility to get the number of shares in this Trade. Each TradeObject object represents a
        single trade, or the part of a trade that happens on one day, with at least 1 
        transaction/ticket. 
        '''
        if self.settings.value('inputType') == 'DB':
            return self.getSharesDB()
        elif self.shares == 0:
            if self.side.startswith("B") or self.side.startswith("HOLD+"):
                self.shares = self.df[frc.bal].max()
            else:
                self.shares = self.df[frc.bal].min()
        return self.shares

    def __setShares(self):
        self.TheTrade.Shares = "{0} shares".format(self.getShares())
        return self.TheTrade

    def __setMarketValue(self):
        mkt = self.getShares() * self.df.loc[self.ix0][frc.price]
        self.TheTrade.MktVal = mkt
        return self.TheTrade

    def __setHeaders(self):
        self.TheTrade[self.sf.plhead] = "P/L"
        self.TheTrade[self.sf.starthead] = "Start"
        self.TheTrade[self.sf.durhead] = "Dur"
        self.TheTrade[self.sf.sharehead] = "Pos"
        self.TheTrade[self.sf.mkthead] = "Mkt"
        self.TheTrade[self.sf.entryhead] = 'Entries and Exits'
        self.TheTrade[self.sf.targhead] = 'Target'
        self.TheTrade[self.sf.stophead] = 'Stop'
        self.TheTrade[self.sf.rrhead] = 'R:R'
        self.TheTrade[self.sf.maxhead] = 'Max Loss'
        self.TheTrade[self.sf.mstkhead] = "Proceeds Lost"
        return self.TheTrade[[self.sf.entryhead, self.sf.targhead, self.sf.stophead,
                              self.sf.rrhead, self.sf.maxhead]]

    def __setEntriesDB(self, imageName):
        Long = True if (self.df.iloc[0][frc.oc].find('O') >= 0 and (self.df.iloc[0][frc.shares] > 0)) or (
                        self.df.iloc[0][frc.oc].find('C') >= 0 and (self.df.iloc[0][frc.shares] < 0)) else False

        entries = list()
        fpentries = list()
        # exits = list()
        long = False
        entry1 = 0
        count = 0

        for i, row in self.df.iterrows():
            # ix0 is the index of the first row in df (df is a dataframe holding one trade in at
            # least 1 row (1 row per ticket)
            diff = 0

            tm = pd.Timestamp(row[frc.time])
            d = pd.Timestamp(row[frc.date])
            dtime = pd.Timestamp(d.year, d.month, d.day, tm.hour, tm.minute, tm.second)
            price = row[frc.price]
            shares = row[frc.shares]
            average = row[frc.avg]
            if average:
                if count == 0:
                    entry1 = price
                    average1 = average
                    diff = average1-price
                else:
                    diff = average1 - price

            fpentries.append([price, 'deprecated', row[frc.side], dtime])
            


            # Entry Price
            col = 'Entry' + str(count+1) if row[frc.oc].find('O') >= 0 else 'Exit' + str(count+1)
            self.TheTrade[col] = price

            # Entry Time
            col = "Time" + str(count+1)
            # self.TheTrade[col] = pd.Timestamp(price[1])
            self.TheTrade[col] = dtime


            # Entry Shares
            col = "EShare" + str(count+1)
            self.TheTrade[col] = shares

            # Entry P/L
            col = "PL" + str(count+1)
            self.TheTrade[col] = row[frc.PL]

            # Entry diff
            col = "Diff" + str(count+1)
            self.TheTrade[col] = diff
            count += 1
        self.entries = fpentries
        
        if imageName:
            start = self.df.iloc[0][frc.date]
            end = self.df.iloc[-1][frc.date]
            self.setChartDataDefault(start, end, imageName)
        return self.TheTrade
        

    def __setEntries(self, imageName=None):
        '''
        This method places data into the trade summary from entries, exits, time of transaction,
        number of shares, and the difference between price of this transaction and the 1st entry
        (or over night hold entry).  This method also creates the entries object (will be dict
        eventually) and saves it, not in the dataFrame but as self.entries to be gathered into
        a dict using parallel keys to lf.ts.
        '''
        if self.settings.value('inputType') == 'DB':
            return self.__setEntriesDB(imageName)
        entries = list()
        fpentries = list()
        # exits = list()
        long = False
        entry1 = 0
        count = 0
        exitPrice = 0
        partEntryPrice = 0

        # If the first trade side is 'B' or HOLD+ we are long
        sideat0 = self.df.loc[self.ix0][frc.side]
        if sideat0.startswith('B') or sideat0.lower().startswith('hold+'):
            long = True

        # Set the first entry price aka entry1 and place it in df. This method needs a test!
        if self.df.loc[self.ix0][frc.price] == 0:
            for i, row in self.df.iterrows():
                if long and count and row[frc.side].startswith('S'):
                    exitPrice = exitPrice + \
                        abs(row[frc.price] * row[frc.shares])
                elif count:
                    partEntryPrice = partEntryPrice + \
                        abs(row[frc.price] * row[frc.shares])
                count = count + 1
            if isinstance(self.df.loc[self.ix][frc.sum], str):
                entryPrice = exitPrice
            else:
                entryPrice = exitPrice - self.df.loc[self.ix][frc.sum]
            tmpentry = (entryPrice - partEntryPrice)
            tmpshares = self.df.loc[self.ix0][frc.shares]
            if entryPrice == 0 or tmpshares == 0:
                entry1 = 0
            else:
                entry1 = tmpentry / tmpshares
            # entry1 = (entryPrice - partEntryPrice) / \
            #     self.df.loc[self.ix0][frc.shares]
            self.df.at[self.ix0, frc.price] = entry1

        for i, row in self.df.iterrows():
            # ix0 is the index of the first row in df (df is a dataframe holding one trade in at
            # least 1 row (1 row per ticket)
            diff = 0

            tm = pd.Timestamp(row[frc.time])
            d = pd.Timestamp(row[sf.date])
            dtime = pd.Timestamp(d.year, d.month, d.day, tm.hour, tm.minute, tm.second)
            price = row[frc.price]
            shares = row[frc.shares]
            if count == 0:
                entry1 = price
            else:
                diff = price - entry1

            fpentries.append([price, 'deprecated', row[frc.side], dtime])

            if long:
                    # entries.append(price, cindex, L_or_S,  dtime)
                if (row[frc.side]).startswith('B') or (row[frc.side]).lower().startswith("hold+"):
                    entries.append([price, dtime, shares, 0, diff, "Entry"])
                else:
                    entries.append([price, dtime, shares, row[sf.pl], diff, "Exit"])
            else:
                if (row[frc.side]).startswith('B'):
                    entries.append([price, dtime, shares, row[sf.pl], diff, "Exit"])
                else:
                    entries.append([price, dtime, shares, 0, diff, "Entry"])
            count = count + 1

        # Store this bit seperately for use in chart creation. Avoid having to re-constitute the details. We will
        # add these to a dictionary in LayoutForms using the same key as lf.ts
        self.entries = fpentries

        if len(entries) > 8:
            more = len(entries) - 8
            self.TheTrade[self.sf.pl8] = "Plus {} more.".format(more)
            # If this triggered check that the input file processed into tickets.
            # If not, there are probably fewer ticketts than it appears-- check for repeated
            # time entries
        for i, price in zip(range(len(entries)), entries):

            # Entry Price
            col = "Entry" + str(i+1) if price[5] == "Entry" else "Exit" + str(i+1)
            self.TheTrade[col] = price[0]

            # Entry Time
            col = "Time" + str(i+1)
            self.TheTrade[col] = pd.Timestamp(price[1])

            # Entry Shares
            col = "EShare" + str(i+1)
            self.TheTrade[col] = price[2]

            # Entry P/L
            col = "PL" + str(i+1)
            self.TheTrade[col] = price[3]

            # Entry diff
            col = "Diff" + str(i+1)
            self.TheTrade[col] = price[4]
        imageName = imageName if imageName else ''
        start = entries[0][1]
        end = entries[-1][1]
        self.setChartDataDefault(start, end, imageName)
        return self.TheTrade

    def setChartDataDefault(self, start, end, imageName):
        '''Set up default times and intervals for charts'''
        # start = entries[0][1]
        # end = entries[-1][1]
        defaultIntervals = [1, 5, 15]
        fp = FinPlot()
        for i, di in enumerate(defaultIntervals):
            if imageName:
                iName, ext = os.path.splitext(imageName)
                iName = '{}_{:02d}min{}'.format(iName, di, ext)
            else:
                iName = ''
            begin, finish = fp.setTimeFrame(start, end, di)

            self.TheTrade['chart'+ str(i+1)] = iName
            self.TheTrade['chart'+ str(i+1) + 'Start'] = begin
            self.TheTrade['chart'+ str(i+1) + 'End'] = finish
            self.TheTrade['chart'+ str(i+1) + 'Interval'] = di

        if self.df.loc[self.ix0][frc.side].lower().startswith('hold'):
            return self.TheTrade

        return self.TheTrade

    def __blandSpaceInMstkNote(self):
        pass
        # self.TheTrade[self.sf.mstknote] = "Final note"

    def __setExplainNotes(self):
        # self.TheTrade[self.sf.explain] = "Technical description of the trade"
        # self.TheTrade[self.sf.notes] = "Evaluation of the trade"
        pass

def imageData(ldf):
    '''
    Create generic image names, one for each trade. The start and dur are the first and last
    entries. This is called in the inital loading of a file. More specific names will be used
    for created charts.
    :ldf: A list of DataFrames slices from the input dataframe, each includes the transactions
            for a single trade.
    :return: A list of the generic images, one per trade.
    '''

    frq = FinReqCol()
    imageNames = list()
    for tdf in ldf:
        tindex = tdf[frq.tix].unique()[-1].replace(' ', '')
        name = tdf[frq.name].unique()[-1].replace(' ', '_')
        begin = pd.Timestamp(tdf[frq.start].unique()[-1]).strftime('%H%M%S')
        dur = pd.Timedelta(tdf[frq.dur].unique()[-1]).__str__().replace(':', '').replace(' ', '_')

        imageName = '{0}_{1}_{2}_{3}.{4}'.format(tindex, name, begin, dur, 'png')
        imageName = imageName.replace(':', '')
        imageNames.append(imageName)
    return imageNames

def setTradeSummaryHeaders(ts):
    '''
    A utility created to add the header fields for the tto object as stored in
    the DB trade_sum table. Stuff the blank fields ex1 and ex2 so they are styled 
    '''
    sf = SumReqFields()
    newts = dict()
    for key in ts:
        trade = ts[key]
        trade[sf.plhead] = "P/L"
        trade[sf.starthead] = "Start"
        trade[sf.durhead] = "Dur"
        trade[sf.sharehead] = "Pos"
        trade[sf.mkthead] = "Mkt"
        trade[sf.entryhead] = 'Entries and Exits'
        trade[sf.targhead] = 'Target'
        trade[sf.stophead] = 'Stop'
        trade[sf.rrhead] = 'R:R'
        trade[sf.maxhead] = 'Max Loss'
        trade[sf.mstkhead] = "Proceeds Lost"
        trade['ex1'] = ''
        trade['ex2'] = ''
        # newts[key] = trade
    return ts

def runSummaries(ldf):
    '''
    This script creates the tto object for each trade in the input file and appends it to a
    list It also creates a generic name for assoiated images. That name will be altered for
    speific images that may be created via the stock api or added by the user. Finally the
    sript creates the tradeList key and adds it to the tradeList widget. The key is used to
    retrieve the tto data from the tradeList widget currentText selection.
    :params ldf: A list of DataFrames. Each df is a complete trade from initial purchace or
                hold to 0 shares or hold.
    '''

    tradeSummaries = list()

    sf = SumReqFields()
    initialImageNames = imageData(ldf)
    assert len(ldf) == len(initialImageNames)
    # self.sc.ui.tradeList.clear()
    ts = dict()
    entries = dict()
    for i, (imageName, tdf) in enumerate(zip(initialImageNames, ldf)):

        tto = TheTradeObject(tdf, False, sf)
        tto.runSummary(imageName)
        tradeSummaries.append(tto.TheTrade)
        tkey = f'{i+1} {tto.TheTrade[sf.name].unique()[0]}'
        ts[tkey] = tto.TheTrade
        entries[tkey] = tto.entries
        # self.sc.ui.tradeList.addItem(tkey)

    # self.tradeSummaries = tradeSummaries
    return tradeSummaries, ts, entries, initialImageNames

def notmain():
    '''Run some local code'''
    sf = SumReqFields()



if __name__ == '__main__':
    notmain()
