import os
import re
import pandas as pd

from PyQt5.QtCore import QSettings

from journal.discipline.disciplined import getTradeSummary, getTradeTable

# pylint: disable = C0103

class manageSavedStuff:
    '''
    Manage the qt saves and the excel exports. Load one from the other
    '''

    def __init__(self, settings):
        self.settings = settings
        self.basedir = self.settings.value('journal')
        self.dasInfile = self.settings.value('dasInfile')
        self.ibInfile = self.settings.value('ibInfile')

        Year = '%Y'
        month = '%m'
        MONTH = '%B'
        day = '%d'
        DAY = '%A'
        scheme = self.settings.value('scheme')
        self.frmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)

    def getIbInfiles(self,  indir):
        '''
        '''
        sglob = self.ibInfile

        rgx = re.sub('{\*}', '.*', sglob)
        rgx = rgx + '$'
        d = indir

        # What should turn red here????
        if not d or not os.path.exists(d):
            print(f'Cannot locate directory "{d}".')
            return None
        fs = list()
        for f in os.listdir(d):
            x = re.search((rgx), f)
            if x:
                fs.append(x.string)
        if len(fs) > 1:
            msg = '<h3>You have matched multiple files:</h3><ul> '
        
        return fs

    def getSaveName(self, infile, theDate):
        '''
        Get the save name for infile. The format is taken from sumcontrol.getSaveName and needs to
        remain in sync.
        '''
        savename = f'''.{infile}{theDate.strftime('%A_%m%d')}.zst'''
        return savename

    def loadXlFileAsTS(self, sumList):

        ldfs = list()
        dframes = list()
        dailynotes = list()
        for key in sumList:
            outdirfrmt = self.frmt + 'out/'
            outdir = key.strftime(outdirfrmt)
            outdir = os.path.join(self.basedir, outdir)
            for objs in sumList[key]:
                for xlfile in objs[1]:
                    # print(xlfile)
                    if not objs[2]:
                        print('load it up', key)
                        for xl in objs[1]:
                            xlname = os.path.join(outdir, xl)
                            ldf = getTradeSummary(xlname, key)
                            ldfs.append(ldf)
                            dframe = getTradeTable(xlname, key)
                            dframes.append(dframe)
                            print()
                # print(key.strftime('%m-%d'), objs)
        return ldfs

        print()
        print()

    def gatherDailySumList(self, begin):
        '''
        Gets a dictionary of all input file and all saved files associated with each input file
        :begin: Earliest input file day
        '''
        if not  os.path.exists(self.basedir):
            return
        os.chdir(self.basedir)
        # prefix=prefix

        now = pd.Timestamp.today()
        theDate = begin
        delt = pd.Timedelta(days=1)

        sumfiles = dict()

        while now >= theDate:
            indir=theDate.strftime(self.frmt)
            infiles = list()
            indir = os.path.join(self.basedir, indir)
            filesfordate = list()
            if os.path.exists(indir):
                fnames = os.listdir(indir)
                infiles.extend(self.getIbInfiles(indir))
                if self.dasInfile in fnames:
                    infiles.append(self.dasInfile)

                for inf in infiles:

                    # dirname = theDate.strftime('_%Y%m_%B/_%m%d_%A/out/')
                    dirname = os.path.join(indir, 'out/')
                    outdir = os.path.join(self.basedir, dirname)
                    xlfiles = []
                    if os.path.exists(outdir):
                        os.chdir(outdir)
                        fnames = os.listdir()
                        inf = os.path.splitext(inf)[0]
                        savedfile = self.getSaveName(inf, theDate)
                        for f in fnames:
                            if f.startswith(inf) and  f.endswith('.xlsx'):
                                xlfiles.append(f)
                        if not savedfile in fnames:
                            savedfile = ''
                    filesfordate.append([inf, xlfiles, savedfile])    
            sumfiles[theDate] = filesfordate
            theDate = theDate+delt
        return sumfiles

def main():
    settings = QSettings('zero_substance', 'structjour')
    begin = pd.Timestamp('2018-10-25')

    t = manageSavedStuff(settings)
    l = t.gatherDailySumList(begin)
    ldfs = t.loadXlFileAsTS(l)
    # df = get
    print(l)
    print()

# os.listdir()

if __name__ == '__main__':
    main()