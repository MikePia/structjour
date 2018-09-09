import datetime, os, sys


class JournalFiles :
    '''
    Handles the location of directories to read from and to write to, and also the names of the
    files to read and write.
    '''

    # As the console version has no plan for release, not to worry too much about configuration
    def __init__(self, indir = None, outdir = None, theDate=None, infile='trades.csv', mydevel=False):
        '''
        Creates the required path and field names to run the program. Raises value error the inputfile
        cannot be located
        
        :param: indir:      The location of the input file (DAS Trades export). This is required. (except for development verions using mydevel = True)
        :param: outdir      The name of the output directory. By default, this will be indir/'out'. Structjour willalso place copied charts in this directory.
        :param: theDate:    The date of the transactions in the input file. (Currently DAS Pro Trades export file only)
        :param: infile:     The name of the input file. ('trades.csv' by default)
        :param: outfile:    The name of the outfile. Leave this blank to accept t
        
        '''
        if theDate :
            try:
                assert (type(theDate) is type(datetime.date.today() ))
            except Exception as ex :
                print("TheDate must be type datetime.date. Leave it blank to accept today's date", ex)
                sys.exit(-1)
            self.theDate = theDate
        else :
            self.theDate = datetime.date.today()

        self.root = os.getcwd()
        self.indir = indir if indir else os.path.join(self.root, 'data')
        self.outdir = outdir if outdir else os.path.join(self.root, 'out')
        self.infile = infile if infile else 'trades.csv'
        self.outfile = self.theDate.strftime("Trades_%A_%m%d.xlsx")
        
        if mydevel :
            self.setMyParams(indir, outdir, infile)
        else :
            self.inpathfile = os.path.join(self.indir, self.infile)
            self.outpathfile = os.path.join(self.outdir, self.outfile)
            
        self._checkPaths()
        
               

    def indir(self, indir=None):
        if indir :
            self.indir = indir
            self.inpathfile = os.path.join(self.indir, self.infile)
        return self.indir
    
    def outdir(self, outdir=None):
        if outdir :
            self.outdir = outdir
            self.outpathfile = os.path.join(self.outdir, self.outfile)
        return self.outdir

    def infile(self, infile=None):
        if infile :
            self.infile = infile
            self.inpathfile = os.path.join(self.indir, self.infile)
        return self.infile
    
    def outfile(self, outfile=None):
        if outfile :
            self.outfile = outfile
            self.outpathfile = os.path.join(self.outdir, self.outfile)
        return self.outfile
            
    

    def setMyParams(self, indir, outdir, infile):
        weekNo = str(self._whichWeek(self.theDate.month, self.theDate.day))
        self.indir = indir if indir else self.theDate.strftime(r"C:\trader\journal\_%m_%B\Week_" + weekNo + "\_%m%d_%A")
        self.inpathfile = os.path.join(self.indir, self.infile)
        
        self.outdir =  outdir if outdir else os.path.join(self.indir, 'out')
        self.outpathfile = os.path.join(self.outdir, self.outfile)
      
    def _whichWeek(self, month, testday, year=2018) :
        ''' Calculates which number work week a day is in '''
        #TODO Rework .... again .... use isoweek() for Mon-Sun week. Harder than it should have been.

        beginDate = datetime.date(year, month, 1)
        testDate = datetime.date(year, month, testday)
        idow = int(beginDate.strftime("%w"))
        
        
        #{ dayOfWeekOf1stDayOfMonth:DayOf1stMonday}
        dayOfFirstMonday= {  0:(2,1), 1:(1,1), 2:(7,2), 3:(6,2), 4:(5,2), 5:(4,2), 6:(3,1) }
        # aka (9 - idow) % 7 (if 0 then 7)
        
        fm = datetime.date(year, month, dayOfFirstMonday[idow][0])
        adjuster = 1 if fm.day < 4 else 2
        day = testDate.day
        week = ((day - fm.day)//7)  + adjuster
        week = 1 if week < 1 else week 
        return week   
        
    def mkOutdir (self):
        if not os.path.exists(self.outdir) :
            try :
                os.mkdir(self.outdir) 
            except FileNotFoundError as ex:
                print (ex)
                return False
        return True
    
    def _checkPaths(self):
        '''
        Check the value of self.inpathfile for existance and raise a ValueError if not
        '''
  
        if not os.path.exists(self.inpathfile) :
            print(os.path.realpath(self.inpathfile))
            if os.path.exists(os.path.join(self.root, self.infile)) :
                self.indir = self.root
                self.inpathfile = os.path.join(self.indir, self.infile)
            else :
                err = "Fatal error:{0}: input can't be located: {1}".format("JournalFiles._checkPaths", self.inpathfile)
                self._printValues()
                raise NameError (err)
        if not os.path.exists(self.outdir) :
            
            checkUpOne = os.path.split(self.outdir)[0]
            if len(checkUpOne) < 1 :
                checkUpOne = "."
            if not os.path.exists(checkUpOne) :
                #If the parent exists, Structjour will create the out directory when it comes to it. 
                # Otherwise, trash this puppy
                err = "Fatal error:{0} Neither output directory nor its parent can be located: {1}".format("JournalFiles._checkPaths", self.outputdir)
                self._printValues()
                raise NameError(err)
            
        
    def _printValues(self):
        '''Development helper'''
        print("indir:              " +self.indir)
        print("infile:             " +self.infile)
        print("inpathfile:         " +self.inpathfile)
        print()
        print("outdir:             " +self.outdir)
        print("outfile:            " +self.outfile)
        print("outpathfile:        " +self.outpathfile)
        print("theDate:            " + self.theDate.strftime("%A, %B %d, %y"))
         


