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
Created on Apr 1, 2019

@author: Mike Petersen
'''

import logging
import os
import sys

import pandas as pd
from PyQt5.QtCore import QDate, QDateTime, QSettings
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QStyleFactory, QMessageBox, QInputDialog, QLineEdit

from structjour.definetrades import DefineTrades
from structjour.statements.dasstatement import DasStatement
from structjour.statements.findfiles import checkDateDir
from structjour.statements.ibstatementdb import StatementDB
from structjour.statements.ibstatement import IbStatement
from structjour.statements.statement import getStatementType
from structjour.stock.utilities import pd2qtime
from structjour.view.layoutforms import LayoutForms
from structjour.view.sumcontrol import SumControl
from structjour.stock.utilities import qtime2pd
from structjour.journalfiles import JournalFiles
# pylint: disable = C0103, C0301


def getDate(msg):
    '''
    QInputDialog to get the date
    '''
    while True:
        text, okPressed = QInputDialog.getText(None, "Get text", msg, QLineEdit.Normal, "")
        if okPressed and text != '':
            if text.lower().startswith('q'):
                return None
            try:
                text = pd.Timestamp(text)
                return text
            except ValueError as ex:
                logging.error(ex)
                continue
        else:
            break
    return None


class runController:
    '''
    Programming notes-- minimize the use of the ui (self.ui). Instead create high level
    interface in sc as needed.
    :Settings-keys: ['theDate', 'setToday', scheme', 'journal', 'dasInfile', 'dasInfile2',
                     'ibInfile', outdir, 'interval', inputType]
    '''
    def __init__(self, sc):
        self.sc = sc
        self.ui = self.sc.ui

        self.initialize()
        self.inputtype = None

        self.ui.goBtn.pressed.connect(self.runnit)
        self.ui.loadBtn.pressed.connect(self.loadit)
        self.loadedDate = None

    def initialize(self):
        '''
        Initialize the inputs and outs
        '''
        # Might blitz thes lines if JournalFiles gets an overhaul. For ease of transaiton
        # We keep JournalFiles till its allworks into the Qt run
        self.settings = self.sc.settings
        self.inputtype = self.settings.value('inputType')
        self.indir = self.sc.getDirectory()
        inkey = ''
        if self.inputtype == 'DAS':
            inkey = 'dasInfile'
        elif self.inputtype == 'IB_HTML':
            inkey = 'ibInfileName'
        if self.settings.value('outdirPolicy') == 'default':
            self.outdir = None
        else:
            self.outdir = self.settings.value('outdir')
        theDate = self.settings.value('theDate', pd.Timestamp.today())
        if theDate and isinstance(theDate, (QDate, QDateTime)):
            theDate = qtime2pd(theDate)
        self.theDate = theDate
        self.positions = self.settings.value('dasInfile2')

        # end blitz
        self.infile = self.settings.value(inkey)
        self.inpathfile = self.ui.infileEdit.text()
        self.sc.setWindowTitle(self.sc.baseWindowTitle)

    def loadit(self):
        '''
        Load saved objects
        '''
        # oldDate = self.loadedDate
        # t = self.sc.windowTitle()
        # if t[-1] == '*':
        #     self.saveTradesQuestion(oldDate)

        daDate = self.ui.dateEdit.date()
        daDate = qtime2pd(daDate)
        self.loadedDate = daDate
        self.settings.setValue('theDate', daDate)
        self.initialize()

        if not self.indir:
            logging.info('No file to load?')
            return
        jf = JournalFiles(indir=self.indir, outdir=self.outdir, theDate=self.theDate,
                          infile=self.infile, inputType=self.inputtype, infile2=self.positions,
                          mydevel=True)

        lf = LayoutForms(self.sc, jf, None)
        lf.loadTradesFromDB(daDate)

    def runDBInput(self, daDate, jf):
        '''
        Get the trades from daDate in the DB and process the trades
        '''
        statement = StatementDB()

        daDate = qtime2pd(daDate)

        df = statement.getStatement(daDate)
        if df.empty:
            return False

        tu = DefineTrades(self.inputtype)
        dframe, ldf = tu.processDBTrades(df)
        lf = LayoutForms(self.sc, jf, dframe)
        lf.pickleitnow()
        tradeSummaries = lf.runTtoSummaries(ldf)
        # ts = lf.ts
        statement.addTradeSummaries(tradeSummaries, ldf)
        return True

    def runnitDB(self):
        '''
        Load an initial input file and process it.
        '''
        
        logging.info('did this go to the right file?')
        self.initialize()
        if not self.indir:
            logging.info('No file to load?')
            return
        jf = JournalFiles(indir=self.indir, outdir=self.outdir, theDate=self.theDate,
                          infile=self.infile, inputType=self.inputtype, infile2=self.positions,
                          mydevel=True)
        local = os.path.normpath(self.ui.infileEdit.text())
        if os.path.normpath(jf.inpathfile) != local:
            if os.path.exists(local):
                d, jf.infile = os.path.split(local)
                jf.inpathfile = local

        if self.inputtype == 'IB_HTML':
            jf.inputType = 'IB_HTML'
            statement = IbStatement()
            statement.openIBStatement(jf.inpathfile)
        elif self.inputtype == 'DAS':
            theDate = self.settings.value('theDate')
            ds = DasStatement(jf.infile, self.settings, theDate)
            ds.getTrades()

    def runnit(self):
        '''
        Load an initial input file and process it.
        '''
        # t = self.sc.windowTitle()
        # if t[-1] == '*':
        #     self.saveTradesQuestion()
        self.initialize()
        if not self.indir:
            logging.info('No file to load?')
            return
        jf = JournalFiles(indir=self.indir, outdir=self.outdir, theDate=self.theDate,
                          infile=self.infile, inputType=self.inputtype, infile2=self.positions,
                          mydevel=True)
        if self.inputtype == 'DB':
            self.runDBInput(self.theDate, jf)

            windowTitle = f'{self.sc.baseWindowTitle}: {self.sc.ui.infileEdit.text()}: no user data'
            self.sc.setWindowTitle(windowTitle)
            return
        local = os.path.normpath(self.ui.infileEdit.text())
        if os.path.normpath(jf.inpathfile) != local:
            if os.path.exists(local):
                d, jf.infile = os.path.split(local)
                jf.inpathfile = local

        x, inputType = getStatementType(jf.inpathfile)
        if not inputType:
            msg = f'<h3>No trades found. File does not appear to be a statement</h3><ul> '
            msg += f'<div><strong>{jf.inpathfile}</strong></div>'
            msgbx = QMessageBox()
            msgbx.setIconPixmap(QPixmap("structjour/images/ZSLogo.png"))
            msgbx.setText(msg)
            msgbx.exec()
            return
        self.inputtype = inputType

        windowTitle = self.sc.baseWindowTitle + ': ' + self.sc.ui.infileEdit.text() + ': no user data'
        self.sc.setWindowTitle(windowTitle)

        if self.inputtype == 'IB_HTML' or self.inputtype == 'IB_CSV':
            jf.inputType = self.inputtype
            ibs = IbStatement()
            x = ibs.openIBStatement(jf.inpathfile)
            msg = ''
            if x[0]:
                tkey = 'Trades' if 'Trades' in x[0].keys() else 'TRNT' if 'TRNT' in x[0].keys() else None
                if not tkey:
                    raise ValueError(f'Error in processing statemnt {jf.inpathfile}')
                numtickets = len(x[0][tkey])
                gotToday = self.runDBInput(self.theDate, jf)

                if gotToday:
                    return
                else:
                    msg = f'<h3>No trades found on date {self.theDate.date()}</h3><ul> '
                    msg += f'<div><strong>{jf.inpathfile}</strong></div>'
                    msg += f'<div>Found {numtickets} tickets. They are now in DB</div>'
                    msg += f'<div>{list(x[1].keys())}</div>'

            else:
                msg = f'<h3>No trades recorded from the file:</h3><ul> '
                msg = msg + f'<div><strong>{jf.inpathfile}</strong></div>'
                msg = msg + f'<div>{x[1]}</div>'
            msgbx = QMessageBox()
            msgbx.setIconPixmap(QPixmap("structjour/images/ZSLogo.png"))
            msgbx.setText(msg)
            msgbx.exec()
            return
        elif self.inputtype == 'DAS':
            x = checkDateDir(jf.inpathfile)
            if not x:
                msg = "<h3>The date for this DAS statement is not clear</h3>"
                msg += "<div>Please enter the date for this statement</div>"
                msg += f'<div><strong>{jf.inpathfile}</strong></div>'
                msg += '<div>(YYYYMMDD) ex: 20190113</div>'
                theDate = getDate(msg)
                if theDate:
                    self.settings.setValue('theDate', theDate)
                    self.sc.ui.dateEdit.setDate(pd2qtime(theDate, qdate=True))
                else:
                    return
            ds = DasStatement(jf.infile, self.settings, self.theDate)
            ds.getTrades()
            self.runDBInput(self.theDate, jf)
            return
        else:
            msg = '<h3>Unrecognized input:</h3><ul> '
            msgbx = QMessageBox()
            msgbx.setIconPixmap(QPixmap("structjour/images/ZSLogo.png"))
            msgbx.setText(msg)
            msgbx.exec()
            return

    def saveTradesQuestion(self, oldDate):
        msgBox = QMessageBox()
        msgBox.setIconPixmap(QPixmap("structjour/images/ZSLogo.png"))
        name = self.sc.ui.tradeList.currentText()  # + oldDate.
        msgBox.setText(f"User data for {name}  on {oldDate.strftime('%A %B %d')} has been modified.")
        msgBox.setInformativeText("Do you want to commit your changes?")
        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Save)
        ret = msgBox.exec()
        
        if ret == QMessageBox.Save:
            self.sc.saveTradeObject(oldDate)


def setuplog():
    # basicConfig args level, filename, filemode, format
    settings = QSettings('zero_substance', 'structjour')
    level = settings.value('logfile_level', 'Debug')
    lvls = {'Debug': logging.DEBUG,
            'Info': logging.INFO,
            'Warning': logging.WARNING,
            'Error': logging.ERROR,
            'Critical': logging.CRITICAL
            }
    logfile = settings.value('logfile', 'app.log')
    level = lvls[level]
    filename = logfile
    filemode = 'a'
    datefmt = '%Y/%m/%d %H:%M:%S'
    format = '%(asctime)s  - %(levelname)s - %(funcName)s - %(message)s'
    logging.basicConfig(level=level, filename=filename, filemode=filemode, format=format, datefmt=datefmt)


def main():
    '''Run some local code'''
    setuplog()
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    os.chdir(os.path.realpath('../../'))
    app = QApplication(sys.argv)
    s = QStyleFactory.create('Fusion')
    app.setStyle(s)
    w = SumControl()
    rw = runController(w)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
