'''
Populate the Qt forms

Created on April 14, 2019

@author: Mike Petersen
'''

import datetime as dt
import numpy as np

import pandas as pd
from journal.definetrades import FinReqCol
from journal.thetradeobject import TheTradeObject, SumReqFields
# from journal.view.sumcontrol import SumControl
# pylint: disable=C0103

class LayoutForms:
    '''
    Run theTradeObject summariew to get the tto DataFrame and populate
    the trade form for each trade
    '''
    def __init__(self, sc):
        self.ts = dict()
        rc = SumReqFields()
        self.timeFormat = '%H:%M:%S'


        self.sc = sc
        

        #Widget Dictionary
        wd = dict()
        wd[rc.name] = sc.ui.title
        wd[rc.acct] = sc.ui.account
        wd[rc.strat] = sc.ui.strategy
        wd[rc.link1] = sc.ui.link
        wd[rc.pl] = sc.ui.pl
        wd[rc.start] = sc.ui.start
        wd[rc.dur] = sc.ui.dur
        wd[rc.shares] = sc.ui.pos
        wd[rc.mktval] = sc.ui.mkt
        wd[rc.targ] = sc.ui.targ
        wd[rc.targdiff] = sc.ui.targDiff
        wd[rc.stoploss] = sc.ui.stop
        wd[rc.sldiff] = sc.ui.stopDiff
        wd[rc.rr] = sc.ui.rr
        wd[rc.maxloss] = sc.ui.maxLoss
        wd[rc.mstkval] = sc.ui.lost
        wd[rc.mstknote] = sc.ui.sumNote
        wd[rc.entry1] = sc.ui.entry1
        wd[rc.entry2] = sc.ui.entry2
        wd[rc.entry3] = sc.ui.entry3
        wd[rc.entry4] = sc.ui.entry4
        wd[rc.entry5] = sc.ui.entry5
        wd[rc.entry6] = sc.ui.entry6
        wd[rc.entry7] = sc.ui.entry7
        wd[rc.entry8] = sc.ui.entry8
        wd[rc.exit1] = sc.ui.exit1
        wd[rc.exit2] = sc.ui.exit2
        wd[rc.exit3] = sc.ui.exit3
        wd[rc.exit4] = sc.ui.exit4
        wd[rc.exit5] = sc.ui.exit5
        wd[rc.exit6] = sc.ui.exit6
        wd[rc.exit7] = sc.ui.exit7
        wd[rc.exit8] = sc.ui.exit8
        wd[rc.time1] = sc.ui.time1
        wd[rc.time2] = sc.ui.time2
        wd[rc.time3] = sc.ui.time3
        wd[rc.time4] = sc.ui.time4
        wd[rc.time5] = sc.ui.time5
        wd[rc.time6] = sc.ui.time6
        wd[rc.time7] = sc.ui.time7
        wd[rc.time8] = sc.ui.time8
        wd[rc.eshare1] = sc.ui.share1
        wd[rc.eshare2] = sc.ui.share2
        wd[rc.eshare3] = sc.ui.share3
        wd[rc.eshare4] = sc.ui.share4
        wd[rc.eshare5] = sc.ui.share5
        wd[rc.eshare6] = sc.ui.share6
        wd[rc.eshare7] = sc.ui.share7
        wd[rc.eshare8] = sc.ui.share8
        wd[rc.diff1] = sc.ui.diff1
        wd[rc.diff2] = sc.ui.diff2
        wd[rc.diff3] = sc.ui.diff3
        wd[rc.diff4] = sc.ui.diff4
        wd[rc.diff5] = sc.ui.diff5
        wd[rc.diff6] = sc.ui.diff6
        wd[rc.diff7] = sc.ui.diff7
        wd[rc.diff8] = sc.ui.diff8
        wd[rc.pl1] = sc.ui.pl1
        wd[rc.pl2] = sc.ui.pl2
        wd[rc.pl3] = sc.ui.pl3
        wd[rc.pl4] = sc.ui.pl4
        wd[rc.pl5] = sc.ui.pl5
        wd[rc.pl6] = sc.ui.pl6
        wd[rc.pl7] = sc.ui.pl7
        wd[rc.pl8] = sc.ui.pl8
        wd[rc.explain] = sc.ui.explain
        wd[rc.notes] = sc.ui.notes

        self.rc = rc
        self.wd = wd
        self.sc.loadLayoutForms(self)

    def imageData(self, ldf):
        frq = FinReqCol()
        imageNames = list()
        for tdf in ldf:
            imageName = '{0}_{1}_{2}_{3}.{4}'.format(tdf[frq.tix].unique()[-1].replace(' ', ''),
                                                     tdf[frq.name].unique()[-1].replace(' ', '-'),
                                                     tdf[frq.start].unique()[-1],
                                                     tdf[frq.dur].unique()[-1], 'unused')
            imageNames.append(imageName)
        return imageNames


    def runSummaries(self, imageNames, ldf):
    
        tradeSummaries = list()

        srf = SumReqFields()

        for count, (loc, tdf) in enumerate(zip(imageNames, ldf)):

            tto = TheTradeObject(tdf, False, srf)
            tto.runSummary()
            tradeSummaries.append(tto.TheTrade)
            for key in self.wd.keys():
                print(key, tto.TheTrade[key].unique()[0])
            tkey = f'{count+1} {tto.TheTrade[srf.name].unique()[0]}'
            self.ts[tkey] = tto.TheTrade
            self.sc.ui.tradeList.addItem(tkey)

            

        self.tradeSummaries = tradeSummaries
        return tradeSummaries

    def populateTradeSumForms(self, key):
        tto = self.ts[key]
        for wkey in self.wd.keys():
            daVal = tto[wkey].unique()[0]
            if isinstance(daVal, (np.floating, float)):
                daVal = '{:.02f}'.format(daVal)
            elif isinstance(daVal, (np.integer, int)):
                daVal = '{}'.format(daVal)
            elif isinstance(daVal, (pd.Timestamp, dt.datetime, np.datetime64)):
                daVal = pd.Timestamp(daVal)
                daVal = daVal.strftime(self.timeFormat)
            self.wd[wkey].setText(daVal)

            print(wkey)
            self.setChartTimes(self, key)

    def setChartTimes(self, key):
        tto = self.ts[key]
        for i in range(1, 8):
            print(tto['Time' + str(i)])
            daVal = tto['Time' + str(i)]
            start = pd.Timestamp(tto['Time1'])
            if isinstance(daVal, (pd.Timestamp, dt.datetime, np.datetime64)):
                daVal = pd.Timestamp(daVal)
                end = daVal
            
            
        print()

    def reloadTimes(self, key):
        tto = self.ts[key]
        twidgets = [self.sc.ui.time1, self.sc.ui.time2, self.sc.ui.time3, self.sc.ui.time4,
                    self.sc.ui.time5, self.sc.ui.time6, self.sc.ui.time7, self.sc.ui.time8]
        for i, widg in enumerate(twidgets):
            daVal = tto['Time' + str(i+1)].unique()[0]
            if isinstance(daVal, (pd.Timestamp, dt.datetime, np.datetime64)):
                daVal = pd.Timestamp(daVal)
                daVal = daVal.strftime(self.timeFormat)
            widg.setText(daVal)

        print(tto['Time1'], type(tto['Time1']))
        # self.sc.ui.time1
        print()

    def setTargVals(self, key, targ, diff, rr):

        rc = self.rc
        print(key, targ, diff, rr)
        tto = self.ts[key]
        tto[rc.targ] = targ
        tto[rc.targdiff] = diff
        if rr:
            tto[rc.rr] = rr
        print()

    def setStopVals(self, key, stop, diff, rr, maxloss):

        rc = self.rc
        print(key, stop, diff, rr)
        tto = self.ts[key]
        tto[rc.stoploss] = stop
        tto[rc.sldiff] = diff
        if rr:
            tto[rc.rr] = rr
        maxloss = 0.0 if not maxloss else maxloss
        tto[rc.maxloss] = maxloss
        
        lost = 0.0
        note = ''
        clean = tto['clean'].unique()[0]
        name = tto[rc.name].unique()[0]
        pl = tto[rc.pl].unique()[0]
        if maxloss and clean:
            if 'long' in name and diff >= 0:
                return lost, note, clean
            if 'short' in name and diff <= maxloss:
                return lost, note, clean
            assert maxloss < 0
            if maxloss > pl:
                lost = maxloss - pl
                tto[rc.mstkval] = lost
                note = 'Loss exceeds max loss!'
                tto[rc.mstknote] = note
        return (lost, note, clean)
    
    def setClean(self, key, b):
        '''
        Set DataFrame theTrade col clean to b
        :params key: The current trade name is the key found in the tradeList Combo box
        :params b: bool
        ''' 
        self.ts[key]['clean'] = b

    def setMstkVals(self, key, val, note):
        '''
        Set DataFrame theTrade cols values for the two mistake widgets
        :params key: The current trade name is the key found in the tradeList Combo box
        :params val: Float, The value for the 'lost' widget
        :params note: The value for the sumNotes widget
        '''
        self.ts[key][self.rc.mstkval] = val
        self.ts[key][self.rc.mstknote] = note

    def setExplain(self, key, val):
        '''
        Set DataFrame theTrade col explain to val
        :params key: The current trade name is the key found in the tradeList Combo box
        :params val: The value for the explain widget
        '''
        self.ts[key][self.rc.explain] = val

    def setNotes(self, key, val):
        '''
        Set DataFrame theTrade col notes to val
        :params key: The current trade name is the key found in the tradeList Combo box
        :params val: The value for the notes widget
        '''
        self.ts[key][self.rc.notes] = val

    def getImageName(self, key, wloc,  uinfo):

         tto = self.ts[key]
         rc = self.rc
        #  print(rc.tix, rc.name, rc.start, rc.dur)
        #  imageName = '{0}_{1}_{2}_{3}.{4}'.format(tdf[frq.tix].unique()[-1].replace(' ', ''),
        #                                              tdf[frq.name].unique()[-1].replace(' ', '-'),
        #                                              tdf[frq.start].unique()[-1],
        #                                              tdf[frq.dur].unique()[-1], ft)
