import os
import pickle
import re
import pandas as pd
from PyQt5.QtCore import QSettings

class WeGot:
    # Short Circuit Values
    MISSING_DAS_SAVED = 1
    MISSING_IB_SAVED = 2
    CONFLICTING_USER_INPUT = 3
    CONFLICTING_CHART_DATA = 4
    COMPLETED = 5
    ERROR = 6
    OK = 7

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
        dasInfile, ext = os.path.splitext(dasInfile)

        Year = '%Y'
        month = '%m'
        day = '%d'
        MONTH = '%B'
        DAY = '%A'
        das_inpathfile = scheme + 'trades.csv'
        outdirscheme = f'{scheme}out/'
        das_outfilescheme = outdirscheme + '.{dasInfile}{DAY}_{month}{day}.zst'

        # ibinfile, and any future infile that is represented with a glob in settings will be
        # translated in a method like getIbInput, getIbSaved, getIbXL
        # ib_outfilescheme = outdirscheme + '.{IBINFILE}{DAY}_{month}{day}.zst'
        xl_das_outfilescheme = outdirscheme + '{dasInfile}{DAY}_{month}{day}.xlsx'
        
        self.indirfrmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        self.das_infilefrmt = das_inpathfile.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
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
        Gets a list of IB Activity input files as a list. 
        :return: A list of file name or an empty list. (no pathnames)
        '''
        d = self.getIndir()
        if not d[0]:
            return []
        if not d[1] or not os.path.exists(d[1]):
            print(f'Cannot locate directory "{d[1]}".')
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

    def getIbSaved(self, ibinput):
        ibsaved = os.path.split(ibinput)
        ibsaved, ext = os.path.splitext(ibsaved[1])
        ibsaved = os.path.join(self.getOutdir()[1], f'.{ibsaved}.zst')
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
        xlout = os.path.join(outdir, flfname)
        retlist = list()
        
        flist = os.listdir(outdir)
        for fl in flist:
            if fl.startswith(flfname):
                if fl.endswith('.xlsx'):
                    retlist.append(fl)
            
        return retlist

    def loadDictionaries(self, ibsaved, dassaved, forceload=False):
        if self.ib_ts == None or forceload:
            with open(ibsaved, "rb") as f:
                test = pickle.load(f)
                if len(test) == 2:
                    print('Save is in the wrong format. Save and load it again to correct it')
                    (self.ib_ts, entries) = test
                    # self.ts = test
                elif len(test) != 3:
                    print('Something is wrong with this file')
                    return WeGot.ERROR
                    (self.ib_ts, entries, df) = test
            
            with open(dassaved, "rb") as f:
                test = pickle.load(f)
                if len(test) == 2:
                    print('Save is in the wrong format. Save and load it again to correct it')
                    (self.das_ts, entries) = test
                    # self.ts = test
                elif len(test) != 3:
                    print('Something is wrong with this file')
                    return WeGot.ERROR
                else:
                    (self.das_ts, entries, df) = test
        pass

    def compareDictionaries(self):
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
    bothlist = list()

    missinglist = list()
    while current < today:
        # print(current.weekday())
        if current.weekday() < 5:
            files = list()
        
            f = WeGot(current)

            dasname = f.getDASInput()            
            dasout = f.getSaved()
            if dasname[0] and not dasout[0]:
                return WeGot.MISSING_DAS_SAVED, None
            ibnames = f.getIbInput()
            ibout = f.getIbSaved(ibnames[0]) if ibnames else []
            if len(ibnames) > 1:
                raise ValueError('Here is one, how did that happen?', ibname[0])
            if ibnames and not ibout[0]:
                return WeGot.MISSING_IB_SAVED
            if dasname[0] and ibnames:
                if dasout[0] and ibout:
                    f.loadDictionaries(dasname[1], ibnames[0])
                    shortcircuit, key, dasdict, ibdict = f.compareDictionaries()
                    if shortcircuit != WeGot.OK:
                        return shortcircuit, key, dasdict, ibdict
            
                
        current = current + delt
    print('COMPLETED')
    # return flist
    return WeGot.COMPLETED, None, None, None


def notmain():
    b = pd.Timestamp('2018-10-25')
    # ll = reportDASExcelFiles(b)
    reportTwinSavedFiles(b)
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