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
Utilities to synchronize, update, and manage saved objects in the structjour directotry structure
Created on June 6, 2019

@author: Mike Petersen
'''



import math
import os
import pickle
import re
import pandas as pd
from PyQt5.QtCore import QSettings

# pylint: disable = C0103, C0303, C0301, W0612, W0201
class WeGot:
    '''Manage the saved objects we got'''
    # Short Circuit Values
    OK = 0
    MISSING_DAS_SAVED = 1
    MISSING_IB_SAVED = 2
    CONFLICTING_USER_INPUT = 3
    CONFLICTING_CHART_DATA = 4
    ERROR = 5
    COMPLETED = 6

    ERROR_MULTIPLE_IB = 'Error: Multiple Ib Activity Statements'
    ERROR_DATA_CONFLICT = 'Error: Both trades have data for the this field'
    ERROR_DAS_TRADE_DATA = 'Error: Cannot convert DAS trade data. Please reload file. Press Go, Load, Save'
    ERROR_IB_TRADE_DATA = 'Error: Cannot convert IB trade data. Please reload file. Press Go, Load, Save'

    '''Use the settings for scheme and journal combined with self.date, find the various files for structjour'''
    def __init__(self, daDate):
        self.d = daDate
        self.basedir = 'C:/trader/journal/'
        os.chdir(self.basedir)

        settings = QSettings('zero_substance', 'structjour')
        scheme = settings.value('scheme')
        # IBINFILE = settings.value('ibInfile')
        # IBINFILE, ext = os.path.splitext(IBINFILE)
        dasInfile = settings.value('dasInfile')
        das_inpathfile_scheme = scheme + dasInfile
        dasInfile, ext = os.path.splitext(dasInfile)

        Year = '%Y'
        month = '%m'
        day = '%d'
        MONTH = '%B'
        DAY = '%A'
        outdirscheme = f'{scheme}out/'
        self.ofs = '{DAY}_{month}{day}'
        das_outfilescheme = outdirscheme + '.{dasInfile}' + self.ofs + '.zst'

        # ibinfile, and any future infile that is represented with a glob in settings will be
        # translated in a method like getIbInput, getIbSaved, getIbXL
        # ib_outfilescheme = outdirscheme + '.{IBINFILE}{DAY}_{month}{day}.zst'
        xl_das_outfilescheme = outdirscheme + '{dasInfile}' + self.ofs + '.xlsx'

        self.indirfrmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        self.das_infilefrmt = das_inpathfile_scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        self.outdirfrmt = outdirscheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        self.das_outfilefrmt = das_outfilescheme.format(dasInfile=dasInfile, Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        # self.ib_outfilefrmt = ib_outfilescheme.format(IBINFILE=IBINFILE, Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        self.xl_das_outfilefrmt = xl_das_outfilescheme.format(dasInfile=dasInfile, Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        self.settings = settings

        self.das_ts = None
        self.ib_ts = None

    def getIndir(self):
        '''Get the indir/ based on self.d'''
        indir = os.path.join(self.basedir, self.d.strftime(self.indirfrmt))
        return os.path.exists(indir), indir

    def getIbInput(self):
        '''
        Gets a list of IB Activity based on the glob in settings, returns a list.
        :return: A list of file name or an empty list. (no pathnames)
        '''
        d = self.getIndir()
        if not d[0]:
            # print(f'Cannot locate directory "{d[1]}".')
            return []

        sglob = self.settings.value('ibInfile')
        rgx = re.sub('{\\*}', '.*', sglob)
        rgx = rgx + '$'


        fs = list()
        for f in os.listdir(d[1]):
            x = re.search((rgx), f)
            if x:
                fs.append(x.string)

        return fs

    def getDASInput(self):
        '''Get the indir/dasInfile based on self.d'''
        infile = os.path.join(self.basedir, self.d.strftime(self.das_infilefrmt))
        return os.path.exists(infile), infile

    def getOutdir(self):
        '''Get the outdir based on self.d'''
        outdir = os.path.join(self.basedir, self.d.strftime(self.outdirfrmt))
        return os.path.exists(outdir), outdir

    def getSaved(self):
        '''Get the savedname based on self.d and return a tuplet (b, saved) where b is a bool for
        the existence of the file'''
        saved = os.path.join(self.basedir, self.d.strftime(self.das_outfilefrmt))
        return os.path.exists(saved), saved

    def getIbSaved(self, ibinput, current):
        '''Get the pickled object from the ib statement input'''
        ibsaved = os.path.split(ibinput)
        ibsaved, ext = os.path.splitext(ibsaved[1])
        ibsaved = ''.join(['.', ibsaved, self.ofs, '.zst'])

        day = '%d'
        month = '%m'
        DAY = '%A'
        ibsaved = ibsaved.format(DAY=DAY, month=month, day=day)
        ibsaved = current.strftime(ibsaved)
        ibsaved = os.path.join(self.getOutdir()[1], ibsaved)
        return os.path.exists(ibsaved), ibsaved

    def get_DAS_XL(self):
        '''Get a list of existing excel output files for DAS input files'''
        b, daDir = self.getOutdir()
        xl = os.path.join(self.basedir, self.d.strftime(self.xl_das_outfilefrmt))
        base, flfname = os.path.split(xl)
        flfname, ext = os.path.splitext(flfname)
        retlist = list()
        if b:
            flist = os.listdir(daDir)
            for fl in flist:
                if fl.startswith(flfname):
                    retlist.append(fl)
        return retlist

    def get_IB_XL(self, ibinput):
        '''
        Get a list of existing excel output files for IB input files. Will include XL files with
        'copy numbers' like {filename}(1).xlsx
        '''
        b, outdir = self.getOutdir()
        if not b:
            return []
        flfname, ext = os.path.splitext(ibinput)
        # xlout = os.path.join(outdir, flfname)
        retlist = list()

        flist = os.listdir(outdir)
        for fl in flist:
            if fl.startswith(flfname):
                if fl.endswith('.xlsx'):
                    retlist.append(fl)

        return retlist

    def getKeymap(self):
        '''Create and return a keymap between the two ts dictionaries'''
        keymap = list()
        for key in self.das_ts:
            if self.das_ts[key]['Account'].unique()[0] == 'Live':
                # daskeys.append(key)
                for ibkey in self.ib_ts:
                    dastrade = self.das_ts[key]
                    ibtrade = self.ib_ts[ibkey]
                    print(dastrade['Entry1'].unique()[0], '<-----*----->', ibtrade['Entry1'].unique()[0])
                    if math.isclose(dastrade['Entry1'].unique()[0], ibtrade['Entry1'], abs_tol=1e-7):
                        if dastrade['Time1'].unique()[0] == ibtrade['Time1'].unique()[0]:
                            if dastrade['Shares'].unique()[0] == ibtrade['Shares'].unique()[0]:
                                keymap.append([key, ibkey])
                                break
                print(keymap)
        if len(keymap) != len(self.ib_ts.keys()):
            return []
        return keymap


        # print(dastrade['P / L'].unique()[0], '<-----*----->', ibtrade['P / L'].unique()[0])
        # print(dastrade['Duration'].unique()[0], '<-----*----->', ibtrade['Duration'].unique()[0])
        # print(dastrade['Time1'].unique()[0], '<-----*----->', ibtrade['Time1'].unique()[0])
        # print(dastrade['Time2'].unique()[0], '<-----*----->', ibtrade['Time2'].unique()[0])
        # print()



    def loadDictionaries(self, dassaved, ibsaved, forceload=False):
        '''Upload the ts dictionary from DAS and IB'''
        if not self.ib_ts or forceload:
            with open(ibsaved, "rb") as f:
                test = pickle.load(f)
                if len(test) != 3:
                    print('Something is wrong with this file')
                    return WeGot.ERROR, WeGot.ERROR_IB_TRADE_DATA
                (self.ib_ts, self.ib_entries, self.ib_df) = test

            with open(dassaved, "rb") as f:
                test = pickle.load(f)
                if len(test) != 3:
                    print('Something is wrong with this file')
                    return WeGot.ERROR, WeGot.ERROR_DAS_TRADE_DATA
                (self.das_ts, self.das_entries, self.das_df) = test
        return [WeGot.OK]

    def saveDictionaries(self, dassaved, ibsaved):
        '''picklem'''
        with open(dassaved, 'wb') as f:
            pickle.dump((self.das_ts, self.das_entries, self.das_df), f)

        with open(ibsaved, 'wb') as f:
            pickle.dump((self.ib_ts, self.ib_entries, self.ib_df), f)


    def syncField(self, t1, t2, key):
        '''Update a field of user data in one dict from the other'''
        SUCCESS = 1
        FAIL = 0
        val1 = t1[key].unique()[0]
        val2 = t2[key].unique()[0]
        if val1 and not val2:
            t2[key] = t1[key]
        elif val2 and not val1:
            t1[key] = t2[key]
        elif not val1 and not val2:
            pass
        elif val1 and val2 and val1 != val2:
            print('Requires human decision')
            return FAIL, key
        print()
        return SUCCESS, key

    def syncCharts(self, t1, t2):
        '''
        If a chart exists, leave it alone. Only sync  when a chart exists in one
        object and not in the other.
        '''
        for c in ['chart1', 'chart2', 'chart3']:
            c1 = t1[c].unique()[0]
            c2 = t2[c].unique()[0]

            if os.path.exists(c1) and not os.path.exists(c2):
                t2[c] = t1[c]
                t2[c+'Start'] = t1[c+'Start']
                t2[c+'End'] = t1[c+'End']
                t2[c+'Interval'] = t1[c+'Interval']

            elif os.path.exists(c2) and not os.path.exists(c1):
                t1[c] = t2[c]
                t1[c+'Start'] = t2[c+'Start']
                t1[c+'End'] = t2[c+'End']
                t1[c+'Interval'] = t2[c+'Interval']


    def compareDictionaries(self):
        '''
        Compare the user data in the two trade dictionaries, Update one if one is empty
        '''
        keymap = self.getKeymap()
        for daskey, ibkey in keymap:
            dastrade = self.das_ts[daskey]
            ibtrade = self.ib_ts[ibkey]
            userdata = ['Target', 'StopLoss', 'MstkVal', 'MstkNote', 'Explain', 'Notes']
            for key in userdata:
                success, userdatakey = self.syncField(dastrade, ibtrade, key)
                if not success:
                    return WeGot.CONFLICTING_USER_INPUT, self.das_ts, self.ib_ts

                print(dastrade[key].unique()[0], ibtrade[key].unique()[0])
            self.syncCharts(dastrade, ibtrade)
        return WeGot.OK, None, None, None

def reportDASExcelFiles(begin):
    '''
    Report existing DAS input files that lack an Excel export beginning with begin until today.
    Short circuit with the first one found.
    '''
    today = pd.Timestamp.today()
    delt = pd.Timedelta(days=1)
    current = begin
    flist = list()
    while current < today:
        # print(current.weekday())
        if current.weekday() < 5:
            files = list()

            f = WeGot(current)

            b, name = f.getDASInput()
            if b:
                files.append(name)
                xls = f.get_DAS_XL()
                files.append(xls)
                if not xls:
                    print('process', name)
                    flist.append(files)
                    return flist

        current = current + delt
        flist.append(files)
    print('COMPLETED')
    return flist

def reportIBExcelFiles(begin):
    '''
    Report existing IB input files that lack an Excel export beginning with begin until today.
    Short circuit with the first one found.
    '''
    today = pd.Timestamp.today()
    delt = pd.Timedelta(days=1)
    current = begin
    flist = list()
    missinglist = list()
    while current < today:
        # print(current.weekday())
        if current.weekday() < 5:
            files = list()

            f = WeGot(current)

            names = f.getIbInput()
            if names:
                for n in names:
                    files.append(n)
                    xls = f.get_IB_XL(n)
                    files.append(xls)
                    if not xls:
                        print('Lack excel file for', n)
                        missinglist.append(os.path.join(f.getIndir()[1], n))
                        # Short circuit
                        # return []
                    else:
                        flist.append([n, files])

        current = current + delt
    print('COMPLETED')
    # return flist
    return missinglist

def reportTwinSavedFiles(begin):
    '''
    Report existing DAS and IB input files that lack outputfiles

    :Programming notes: After locating twin saves, open the ts dict and the chart dict. Determine
    if the same live trades are saved and create a correspondence map like [[Trade 1, Trade 9],
    [Trade2, Trade 2]]. If the trades are different, move on quitly and report when the process is
    complete. (This could happen) Then determine which has saved user data, including:

    target, stop, mistakeval, mistakenote, explain, analysis, strategy, (link).

    Also from the pickled item get the chart data and update it the same way.

    If only one has any one item, copy it to the other, if both have stuff, report and short
    circuit.

    Also report if the P/L is different beyond fees. Difference of more than ~ (shares * 2 * .0075)
    But keep don't copy this info between objects

    Divide the duties in a way that this code can be used in structjour. Specifically, add
    a dialog window that leads the user through the process and informs when data cannot be merged
    because the input is different. The dialog could load up each pair or just display at each
    short circuit. [choose b]

    Provide additional short circuits for any missing saved files

    Run the whole thing here before placing in structjour by calling it with a script that, at each
    short circuit, starts it again with the next date (won't run all of the code, but gets the
    larger outline.)
    '''

    today = pd.Timestamp.today()
    delt = pd.Timedelta(days=1)
    current = begin

    while current < today:
        # print(current.weekday())
        if current.weekday() < 5:
            f = WeGot(current)

            dasname = f.getDASInput()
            dasout = f.getSaved()
            if dasname[0] and not dasout[0]:
                return WeGot.MISSING_DAS_SAVED, current, dasout[1]
            ibnames = f.getIbInput()
            ibout = f.getIbSaved(ibnames[0], current) if ibnames else [False, '']
            if len(ibnames) > 1:
                # short circuit missing saved file
                return WeGot.ERROR, current, WeGot.ERROR_MULTIPLE_IB, ibnames
                # raise ValueError('Here is one, how did that happen?', ibnames[0])
            if ibnames and not ibout[0]:
                # short circuit missing saved file
                return WeGot.MISSING_IB_SAVED, current, ibout[1]
            if dasname[0] and ibnames:
                if dasout[0] and ibout[0]:
                    results = f.loadDictionaries(dasout[1], ibout[1])
                    if results[0] != WeGot.OK:
                        # short circuit bad dictionary data, reload
                        return results[0], current, results[1], None
                    results = f.compareDictionaries()
                    if results[0] != WeGot.OK:
                        # short circuit data conflict, user choose in gui
                        return (results[0], current, WeGot.ERROR_DATA_CONFLICT,
                                results[1], results[2])
                f.saveDictionaries(dasout[1], ibout[1])
            # else:
            #     print('What now')

        current = current + delt
    print('COMPLETED')
    # return flist
    return WeGot.COMPLETED, None, None, None


def getCSVStatements(dirname):
    'Retrieves files formatted {account}_{yyyymmdd}_{yyyymmdd}.csv The dates are begin and end dates'

    daDir = os.listdir(dirname)
    files = []
    for fn in daDir:
        print(fn)
        s = fn.split('_')
        if not len(s) == 3:
            continue


        s, d1, d2 = s
        d2, ext = os.path.splitext(d2)
        pat = 'U[\d]{7,7}'
        r = re.findall(pat, fn)
        if not r:
            continue

        try:
            beg = pd.Timestamp(d1)
            end = pd.Timestamp(d2)
        except ValueError:
            print('try another')
            continue

        files.append(fn)
    return

def somethingelse():
    '''run some local stuff'''
    basedir = 'C:/trader/journal/'
    settings = QSettings('zero_substance', 'structjour')
    scheme = settings.value('scheme')
    d = pd.Timestamp('2019-06-13')
    scheme = d.strftime(scheme.format(Year='%Y', month='%m', MONTH='%B', day='%d', DAY='%A'))

    daDir = os.path.join(basedir, scheme)

    getCSVStatements(daDir)


def notmain():
    ''' Run local code'''
    b = pd.Timestamp('2019-02-12')
    delt = pd.Timedelta(days=1)
    # ll = reportDASExcelFiles(b)

    while True:
        result = reportTwinSavedFiles(b)
        if result[0] == WeGot.MISSING_IB_SAVED:
            print('Process ib file for ', result[1].strftime('%m-%d'))
        if result[0] == WeGot.ERROR:
            print(result[1].strftime('%m-%d'), result[2], result[3])
            break
        if result[0] == WeGot.COMPLETED:
            break
        b = result[1] + delt

    print()
    # for l in ll:
    #     if l:
            # print(l)
    # print(reportIBExcelFiles(b))
    # w = WeGot(b)
    # print(w.getIbInput())

if __name__ == '__main__':
    # b = pd.Timestamp('2018-10-01')
    # reportIBExcelFiles(b)
    notmain()
    # somethingelse()
