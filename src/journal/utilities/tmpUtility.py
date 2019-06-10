import os
import pandas as pd
from PyQt5.QtCore import QSettings

class WeGot:
    def __init__(self, daDate):
        self.d = daDate
        self.basedir = 'C:/trader/journal/'
        os.chdir(self.basedir)

        settings = QSettings('zero_substance', 'structjour')
        scheme =settings.value('scheme')
        Year = '%Y'
        month = '%m'
        day = '%d'
        hour = '%H'
        minute = '%M'
        second = '%S'
        MONTH = '%B'
        DAY = '%A'
        inpathfile = scheme + 'trades.csv'
        outdirscheme = f'{scheme}out/'
        qtoutfilescheme = outdirscheme + '.trades{DAY}_{month}{day}.zst'
        xloutfilescheme = outdirscheme + 'trades{DAY}_{month}{day}.xlsx'
        
        self.infilefrmt = inpathfile.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        self.outdirfrmt = outdirscheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        self.qtoutfilefrmt = qtoutfilescheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        self.xloutfilefrmt = xloutfilescheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
    def getDASInput(self):
        infile = os.path.join(self.basedir, self.d.strftime(self.infilefrmt))
        return os.path.exists(infile), infile
        

    def getOutdir(self):
        outdir = os.path.join(self.basedir, self.d.strftime(self.outdirfrmt))
        return os.path.exists(outdir), outdir
    
    def getSaved(self):
        saved = os.path.join(self.basedir, self.d.strftime(self.qtoutfilefrmt))
        return os.path.exists(saved), saved
    
    def getXl(self):
        b, daDir = self.getOutdir()
        xl = os.path.join(self.basedir, self.d.strftime(self.xloutfilefrmt))
        base, flfname = os.path.split(xl)
        flfname, ext = os.path.splitext(flfname)
        retlist = list()
        if b:
            flist = os.listdir(daDir)
            for fl in flist:
                if fl.startswith(flfname):
                    retlist.append(fl)
            
        return retlist

def reportExcelFiles(begin):
    today = pd.Timestamp.today()
    delt = pd.Timedelta(days=1)
    current = begin
    flist = list()
    while current < today:
        # print(current.weekday())
        if current.weekday() < 5:
            files = list()
        
#             print(current.strftime('%A, %B %d, %Y'))
            
            f = WeGot(current)
            
            b, name = f.getDASInput()
            if b:
                files.append(name)
                xls = f.getXl()
                files.append(xls)
                if not xls:
                    print('process', name)
                    flist.append(files)
                    return flist
                
        current = current + delt
        flist.append(files)
    print('COMPLETED')
    return flist


if __name__ == '__main__':
    b = pd.Timestamp('2018-10-01')
    reportExcelFiles(b)