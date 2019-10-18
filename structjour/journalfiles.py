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
@author Mike Petersen
'''
import datetime as dt
import os
import sys
import numpy as np
import pandas as pd

from PyQt5.QtCore import QSettings

from structjour import time as mkmonth
# pylint: disable=C0103, R0913




class JournalFiles:
    '''
    Handles the location of directories to read from and to write to, and also the names of the
    files to read and write.
    '''

    inputTypeDict = {'das': 'DAS', 'ib': 'IB_HTML', 'ib_cvs': 'IB_CVS', 'db': 'DB'}

    # As the console version has no plan for release, not to worry too much about configuration
    def __init__(self, indir=None, outdir=None, theDate=None, infile='trades.csv', inputType='DAS',
                 infile2='positions.csv', mydevel=False):
        '''
        Creates the required path and field names to run the program. Raises value error if the
        input file cannot be located. If mydevel is True, the default locations change.

        :params indir:      The location of the input file. Defaut is (cwd)/data. 
        :params outdir      The name of the output directory. Default is (indir)/out. 
        :params theDate:    A Datetime object or timestamp of the date of the transactions in the
                            input file. Will be used if the input file lacks dates. Defaults to 
                            today.
        :params infile:     The name of the input file. Defaults to 'trades.csv'.
        :params inputType:  One of  DAS, IB_HTML, or IB_CVS. Either IB input file should be an
                            activity statement with the tables: Trades, Open Positions and Account
                            Information.
        :params infile2:    This is the positions file. Required for DAS Trader Pro only and only
                            if positions are held before or after this input file's trades. If
                            missing, the program will ask for the information. Defaults to
                            'positions.csv'     
        :raise ValueError:  If theDate is not a valid time.
        :raise NameError:   If the infile is not located.
        '''
        self.settings = QSettings('zero_substance', 'structjour')
        if theDate:
            try:
                theDate = pd.Timestamp(theDate)
                assert isinstance(theDate, dt.datetime)

            except ValueError as ex:
                msg = f"\n\nTheDate ({theDate}) must be a valid timestamp or string.\n"
                msg += "Leave it blank to accept today's date\n" 
                msg += ex.__str__() + "\n" 
                print(msg)
                raise ValueError(msg)
                    
            theDate = theDate
        else:
            theDate = dt.date.today()

        assert inputType in JournalFiles.inputTypeDict.values()
        self.inputType = inputType
        self.settings.setValue('inputType', self.inputType)
        self.theDate = theDate
        self.monthformat = "_%Y%m_%B" #TODO abstract the formats from scheme setting in a utility method
        self.dayformat = "_%m%d_%A"
        self.root = os.getcwd()
        self.indir = indir if indir else os.path.join(self.root, 'data/')
        self.outdir = outdir if outdir else os.path.join(self.root, 'out/')
        self.infile = infile if infile else 'trades.csv'
        self.infile2 = infile2
        self.inpathfile2 = None
        self.outfile = os.path.splitext(self.infile)[0] +  self.theDate.strftime("%A_%m%d.xlsx")

        if not mydevel:
            self.inpathfile = os.path.join(self.indir, self.infile)
            self.outpathfile = os.path.join(self.outdir, self.outfile)
            if self.infile2:
                self.inpathfile2 = os.path.join(self.indir, self.infile2)

        else:
            self.setMyParams(indir, outdir)
        if self.inpathfile2 and not os.path.exists(self.inpathfile2):
            # Fail or succeed quietly here
            self.infile2 = None
            self.inpathfile2 = None
        
        try:
            self._checkPaths()
        except NameError as ex:
            print('Directory ERROR', ex)
            print()

    def setMyParams(self, indir, outdir):
        '''
        Set the file names for MyDevel. By default this uses a directory structure that we created:
                        By default indir is at (journal)/_01_January/Week_4/_0125_Friday
                        Configurable by the infile parameter for JournalFiles
        :params indir:  Location of the input file. If None, set to MyDevel params
        :params outdir: Location to write the output file. If None set to indir/out
        :params infile: The name of the input file.
        '''
        path="C:/trader/journal/" + self.monthformat + '/' + self.dayformat
        path = self.theDate.strftime(path)
        self.indir = indir if indir else os.path.realpath(path)
        self.inpathfile = os.path.join(self.indir, self.infile)
        if self.infile2:
            self.inpathfile2 = os.path.join(self.indir, self.infile2)

        self.outdir = outdir if outdir else os.path.join(self.indir, 'out')
        self.outpathfile = os.path.join(self.outdir, self.outfile)

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
        Check the value of self.inpathfile, self.inpathfile2 (if the entry exists), and self.outdir 
        for existance. Note that this is called by __init__
        :raise NameError: If not DB and inpathfile, inpathfile2 (if given) or outdir do not exist.
        '''
        if self.inputType != 'DB' and not os.path.exists(self.inpathfile):
            print(os.path.realpath(self.inpathfile))
            if os.path.exists(os.path.join(self.root, self.infile)):
                self.indir = self.root
                self.inpathfile = os.path.join(self.indir, self.infile)
            else:
                err = "Fatal error:{0}: input can't be located: {1}".format(
                    "JournalFiles._checkPaths", self.inpathfile)
                self.printValues()
                raise NameError(err)

        if self.inputType != 'DB' and self.inpathfile2 and not os.path.exists(self.inpathfile2):
            err = "Fatal error:{0}: input can't be located: {1}".format(
                    "JournalFiles._checkPaths", self.inpathfile2)
            self.printValues()
            raise NameError(err)

        if not os.path.exists(self.indir):
            print('fixme')
        

        if self.inputType == 'DB':
            
            if not os.path.exists(self.outdir):
                if not os.path.exists(self.indir):
                    monthdir = os.path.join(self.indir, '..')
                    monthdir = os.path.abspath(monthdir)
                    if not os.path.exists(monthdir):
                        msg = f'''The folder {monthdir} does not exist. Structjour must create the
                        folder in order to continue. Creating the directories now.'''
                        print(msg)
                        journal = self.settings.value('journal')
                        if os.path.exists(journal):
                            scheme = self.settings.value('scheme')
                            ix = scheme.find('/')
                            if ix < 0:
                                ix = scheme.find('\\')
                            if ix < 0:
                                raise NameError('Please set the journal directory. Go to the file settings dialog.')
                            dayScheme = scheme[ix+1:]
                            dayScheme = dayScheme.format(DAY='%A', month='%m', day='%d')
                            scheme = scheme[:ix]
                            monthdir = os.path.join(journal, scheme)
                            monthdir = self.theDate.strftime(monthdir.format(Year='%Y', month='%m', MONTH='%B'))
                            mkmonth.createDirs(self.theDate, monthdir, frmt=dayScheme)
                            return
                    # TODO Decide whether to put qt dialog here.
                    raise NameError('Please set the journal directory. Go to the file settings dialog.')
            

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
        if self.inpathfile2:
            print("inpathfile2:        " + self.inpathfile2)
        print()
        print("outdir:             " + self.outdir)
        print("outfile:            " + self.outfile)
        print("outpathfile:        " + self.outpathfile)
        print("theDate:            " + self.theDate.strftime("%A, %B %d, %y"))


def notmain():
    ''' Run some local code'''
    # jf = JournalFiles()


if __name__ == '__main__':
    notmain()
