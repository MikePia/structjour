'''
@author Mike Petersen
'''
import datetime as dt
import os
import sys
import pandas as pd
# pylint: disable=C0103, R0913


def whichWeek(d):
    '''
    Get the week number of the trade where week 1 begins in the first workweek and
    increments every Monday
    :params d: The datetime object or time string to use.
    :return: An int week number
    '''
#     d = pd.Timestamp.today()

    beginDate = dt.datetime(d.year, d.month, 1)
    d = pd.Timestamp(d)
    week = 1
    while beginDate.isoweekday() != 1:
        beginDate = beginDate + dt.timedelta(1)
    if d < beginDate:
        return d, week
    if beginDate.day > 3:
        week = 2
    while beginDate.day < d.day:
        beginDate = beginDate + dt.timedelta(1)
        if beginDate.isoweekday() == 1:
            week = week + 1
    return week


class JournalFiles:
    '''
    Handles the location of directories to read from and to write to, and also the names of the
    files to read and write.
    '''

    # As the console version has no plan for release, not to worry too much about configuration
    def __init__(self, indir=None, outdir=None, theDate=None, infile='trades.csv', mydevel=False):
        '''
        Creates the required path and field names to run the program. Raises value error
        the inputfile cannot be located

        :params indir:      The location of the input file (DAS Trades export). If MyDevel is not
                            set, it defaults to (cwd)/data
        :params outdir      The name of the output directory. By default, this will be
                            cwd/'out'. MyDevel places it at (indir)/out Structjour will also place
                            charts in this directory.
        :params theDate:    A Datetime object or timestamp representing the date of the
                            transactions in the input file. Defaults to today if not set.
        :params infile:     The name of the input file. ('trades.csv' by default)
        :raise ValueError:  If theDate is not a valid time.
        :raise NameError:   If the input file is not located.
        '''
        if theDate:
            try:
                theDate = pd.Timestamp(theDate)
                assert isinstance(theDate, type(dt.date.today()))

            except AssertionError as ex:
                print(
                    "TheDate must be type datetime.date. Leave it blank to accept today's date", ex)
                sys.exit(-1)
            self.theDate = theDate
        else:
            self.theDate = dt.date.today()

        self.root = os.getcwd()
        self.indir = indir if indir else os.path.join(self.root, 'data')
        self.outdir = outdir if outdir else os.path.join(self.root, 'out')
        self.infile = infile if infile else 'trades.csv'
        self.outfile = os.path.splitext(self.infile)[0] +  self.theDate.strftime("%A_%m%d.xlsx")

        if mydevel:
            self.setMyParams(indir, outdir)
        else:
            self.inpathfile = os.path.join(self.indir, self.infile)
            self.outpathfile = os.path.join(self.outdir, self.outfile)

        self._checkPaths()

    # TODO: add a journalroot variable and write it to db or pickle or something and expand
    # MyDevel to a general file structure for all users and fix that ffnn hard coded path
    def setMyParams(self, indir, outdir):
        '''
        Set the file names for MyDevel. By default this uses a directory structure that we created:
                        By default indir is at (journal)/_01_January/Week_4/_0125_Friday
                        Configurable by the infile parameter for JournalFiles
        :params indir:  Location of the input file. If None, set to MyDevel params
        :params outdir: Location to write the output file. If None set to indir/out
        :params infile: The name of the input file.
        '''
        weekNo = str(whichWeek(self.theDate))
        self.indir = indir if indir else self.theDate.strftime(
            r"C:\trader\journal\_%m_%B\Week_" + weekNo + r"\_%m%d_%A")
        self.inpathfile = os.path.join(self.indir, self.infile)

        self.outdir = outdir if outdir else os.path.join(self.indir, 'out')
        self.outpathfile = os.path.join(self.outdir, self.outfile)

    # def _whichWeek(self, month, testday, year=2019):
    #     '''
    #     Calculates which number work week a day is in. Weeks end on Friday. This is
    #     for the naming scheme directory structure.
    #     '''

    #     d = self.theDate

    #     beginDate = dt.date(d.year, d.month, 1)
    #     testDate = dt.date(d.year, d.month, d.day)
    #     idow = int(beginDate.strftime("%w"))

    #     #{ dayOfWeekOf1stDayOfMonth:DayOf1stMonday}
    #     dayOfFirstMonday = {0: (2, 1), 1: (1, 1), 2: (
    #         7, 2), 3: (6, 2), 4: (5, 2), 5: (4, 2), 6: (3, 1)}
    #     # aka (9 - idow) % 7 (if 0 then 7)

    #     fm = dt.date(year, month, dayOfFirstMonday[idow][0])
    #     adjuster = 1 if fm.day < 4 else 2
    #     day = testDate.day
    #     week = ((day - fm.day)//7) + adjuster
    #     week = 1 if week < 1 else week
        # return week



    def mkOutdir(self):
        '''
        Create the directory self.outdir. Allows a Permission exception to stop the program.
        :return: True if successful or False if not.
        '''
        if not os.path.exists(self.outdir):
            try:
                os.mkdir(self.outdir)
            except FileNotFoundError as ex:
                print(ex)
                return False
        return True

    def _checkPaths(self):
        '''
        Check the value of self.inpathfile and self.outdir for existance. Note that this is
        called by __init__
        :raise ValueError: If inpathfile or outdir do not exist.
        '''
        if not os.path.exists(self.inpathfile):
            print(os.path.realpath(self.inpathfile))
            if os.path.exists(os.path.join(self.root, self.infile)):
                self.indir = self.root
                self.inpathfile = os.path.join(self.indir, self.infile)
            else:
                err = "Fatal error:{0}: input can't be located: {1}".format(
                    "JournalFiles._checkPaths", self.inpathfile)
                self.printValues()
                raise NameError(err)
        if not os.path.exists(self.outdir):

            checkUpOne = os.path.split(self.outdir)[0]
            if not checkUpOne:
                checkUpOne = "."
            if not os.path.exists(checkUpOne):
                # If neither outdir not its parent exists, trash this puppy.
                # If the parent exists, we can create outdir when needed
                err = "Fatal error:{0} Output directory cannot be located: {1}".format(
                    "JournalFiles._checkPaths", self.outdir)
                self.printValues()
                raise NameError(err)

    def resetInfile(self, infile):
        '''
        Reset the name of the input file. Note that this is used after processing an original input
                        file (governed by individual transactions) to a file governed by tickets.
                        There is currently no other anticipated reason to use this method.
        :params infile: The file to set as infile
        :raise NameError: If either inpathfile or outdir is not found.
        '''

        self.infile = infile
        inpathfile = os.path.join(self.indir, self.infile)
        self.inpathfile = inpathfile
        self._checkPaths()

    def printValues(self):
        '''Development helper'''
        print("indir:              " + self.indir)
        print("infile:             " + self.infile)
        print("inpathfile:         " + self.inpathfile)
        print()
        print("outdir:             " + self.outdir)
        print("outfile:            " + self.outfile)
        print("outpathfile:        " + self.outpathfile)
        print("theDate:            " + self.theDate.strftime("%A, %B %d, %y"))


def notmain():
    ''' Run some local code'''
    # jf = JournalFiles()
    for i in range(1, 13):
        dd = pd.Timestamp(2019, i, 7)
        whichWeek(dd)                # pylint: disable = W0212


if __name__ == '__main__':
    notmain()
