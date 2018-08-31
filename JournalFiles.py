import datetime, os

class JournalFiles :
    '''
    Handles the location of directories to read from and to write to, and also the names of the
    files to read and write.
    '''

    # As the console version has no plan for release, not to worry too much about configuration
    def __init__(self, indir = None, outdir = None, theDate=None, infile='trades.csv', outfile=None, mydevel=False):
        '''
        Creates the required path and field names to run the program. Raises value error if missing indir or outdir
        
        :param: indir:      The location of the input file (DAS Trades export). This is required. (except for development verions using mydevel = True)
        :param: outdir      The name of the output directory. By default, this will be indir/'out'. Structjour willalso place copied charts in this directory.
        :param: theDate:    The date of the transactions in the input file. (Currently DAS Pro Trades export file only)
        :param: infile:     The name of the input file. ('trades.csv' by default)
        :param: outfile:    The name of the outfile. Leave this blank to accept the generated file name.
        :param: mydevel:    My file locations. 
        
        '''
        if theDate :
            self.theDate = theDate
        else :
            self.theDate = datetime.date.today()

        if indir : 
            self.indir = indir
        else :
            self.indir = None
        
        if outdir : 
            self.outdir = outdir
        else :
            self.outdir = None
            
        if not infile :
            infile = 'trades.csv'
        if not outfile :
            outfile = self.theDate.strftime("Trades_%A_%m%d.xlsx")

        if mydevel :
            self.setMyParams()

        if not self.indir :
            err = "Missing requied arguments: indir. Raising ValueError Exception."
            raise ValueError(err)
        else: 
            if os.path.exists(self.indir) :
                out = os.path.join(self.indir, 'out')
                try :
                    os.mkdir(out)
                    self.outdir = out
                except FileExistsError :
                    pass
                except Exception as ex:
                    print("Error occured while trying to create directory {0}". format(out))
                    quit()
        
           
        self.infile = infile
        self.inpathfile = os.path.join(self.indir, infile)
        self.outfile = outfile
        self.outpathfile = os.path.join(self.outdir, outfile) 
        self.devOutDir = os.path.join(os.getcwd(), 'out')
        if not os.path.isdir(self.devOutDir) :
            try :
                os.mkdir(self.devOutDir)
            except Exception as ex:
                print(ex)
                quit()
        
            
        # indir, outdir
        

    def requiredFields(self):
        '''Checks for required fields in the constructor call'''
        missingFields = list()
        if not self.indir :
            missingFields.append(self.indir)
        if not self.outdir:
            missingFields.append('self.outdir')

        
    def theDate(self, theDate=None):
        if theDate :
            self.theDate = theDate

        return self.theDate

    def indir(self, indir=None):
        if indir :
            self.indir = indir
        return self.indir
    
    def outdir(self, outdir=None):
        if outdir :
            self.outdir = outdir

    def setMyParams(self):
        weekNo = str(self._whichWeek(self.theDate.month, self.theDate.day))
        self.indir = self.theDate.strftime(r"C:\trader\journal\_%m_%B\Week_" + weekNo + "\_%m%d_%A")
        self.outdir = os.path.join(self.indir, 'out')
      
    def _whichWeek(self, month, testday, year=2018) :
        ''' Calculates which number work week a day is in '''

        beginDate = datetime.date(year, month, 1)
        testDate = datetime.date(year, month, testday)
        idow = int(beginDate.strftime("%w"))
        if idow == 1 :
            firstMonday = datetime.date(year, month, 1)
        else :
            firstMonday = datetime.date(year, month, 9 - idow)

        td = testDate.day
        diff = td - firstMonday.day
        week = (diff // 7) + 2
        return(week)


jf = JournalFiles(theDate = datetime.date.today(), mydevel = True)
print ("indir:", jf.indir)
print("infile", jf.infile)
print ("inpathfilename: ",jf.inpathfile)
print("outfile", jf.outfile)
print("outpathfilename", jf.outpathfile)
print ("outdir", jf.outdir)
print ("devOutDir", jf. devOutDir)
