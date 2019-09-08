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


import os
import sys

import pandas as pd
from PyQt5.QtCore import QDate, QDateTime
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QStyleFactory, QMessageBox, QInputDialog, QLineEdit

from journal.definetrades import DefineTrades, FinReqCol
from journal.pandasutil import InputDataFrame
from journal.statements.dasstatement import DasStatement
from journal.statements.findfiles import checkDateDir
from journal.statements.ibstatementdb import StatementDB
from journal.statements.ibstatement import IbStatement
from journal.statements.statement import getStatementType
from journal.statement import Statement_DAS as Ticket
from journal.statement import Statement_IBActivity
from journal.stock.utilities import pd2qtime
from journal.view.layoutforms import LayoutForms
from journal.view.sumcontrol import SumControl, qtime2pd
from journal.journalfiles import JournalFiles

# pylint: disable = C0103


def getDate(msg):
    while True:
        text, okPressed = QInputDialog.getText(None, "Get text", msg, QLineEdit.Normal, "")
        if okPressed and text != '':
            if text.lower().startswith('q'):
                return None
            try:
                text = pd.Timestamp(text)
                return text
            except ValueError:
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

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../../'))


        self.initialize()

        self.ui.goBtn.pressed.connect(self.runnit)
        self.ui.loadBtn.pressed.connect(self.loadit)

    def initialize(self):
        '''
        Initialize the inputs and outs
        '''
        ### Might blitz thes lines if JournalFiles gets an overhaul. For ease of transaiton
        ### We keep JournalFiles till its allworks into the Qt run
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

        ### end blitz
        self.infile = self.settings.value(inkey)
        self.inpathfile = self.ui.infileEdit.text()
        print(self.inpathfile)

    def loadit(self):
        '''
        Load saved objects
        '''
        inputType = self.settings.value('inputType')
            
        daDate = self.ui.dateEdit.date()
        daDate = qtime2pd(daDate)
        self.settings.setValue('theDate', daDate)
        self.initialize()

        if not self.indir:
            print('What file is supposed to load?')
            return
        jf = JournalFiles(indir=self.indir, outdir=self.outdir, theDate=self.theDate,
                          infile=self.infile, inputType=self.inputtype, infile2=self.positions,
                          mydevel=True)
        

        lf = LayoutForms(self.sc, jf, None)
        lf.loadSavedFile(inputType, daDate)
        if lf.df is None:
            print('Did not load up correctly. Try pressing Go, Load, Save')

    def runDBInput(self, daDate, jf):
        statement = StatementDB()

        daDate = qtime2pd(daDate)

        rc = FinReqCol()
        df = statement.getStatement(daDate)
        if df.empty:
            return False

        tu = DefineTrades(self.inputtype)
        inputlen, dframe, ldf = tu.processDBTrades(df)
        lf = LayoutForms(self.sc, jf, dframe)
        lf.pickleitnow()
        tradeSummaries = lf.runTtoSummaries(ldf)
        ts = lf.ts
        statement.addTradeSummaries(tradeSummaries, ldf)
        # ts = statement.loadDBSummaries(ts)
        return True


    def runnitDB(self):
        '''
        Load an initial input file and process it.
        '''
        print('gonna runnitDB gonna runnitDB')
        self.initialize()
        if not self.indir:
            print('What file is supposed to load?')
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
            x = statement.openIBStatement(jf.inpathfile)
        elif self.inputtype == 'DAS':
            theDate = self.settings.value('theDate')
            ds = DasStatement(jf.infile, self.settings, theDate)
            df = ds.getTrades()

 
    def runnit(self):
        '''
        Load an initial input file and process it.
        '''
        self.initialize()
        if not self.indir:
            print('What file is supposed to load?')
            return
        jf = JournalFiles(indir=self.indir, outdir=self.outdir, theDate=self.theDate,
                          infile=self.infile, inputType=self.inputtype, infile2=self.positions,
                          mydevel=True)
        if self.inputtype == 'DB':
            self.runDBInput(self.theDate, jf)
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
            msgbx.setIconPixmap(QPixmap("images/ZSLogo.png"));
            msgbx.setText(msg)
            msgbx.exec()
            return
        self.inputtype = inputType

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
            msgbx.setIconPixmap(QPixmap("images/ZSLogo.png"));
            msgbx.setText(msg)
            msgbx.exec()
            return
        elif  self.inputtype == 'DAS':
            x = checkDateDir(jf.inpathfile)
            if not x:
                msg = "<h3>The date for this DAS statement is not clear</h3>"
                msg += "<div>Please enter the date for this statement</div>"
                msg += f'<div><strong>{jf.inpathfile}</strong></div>'
                msg +=  '<div>(YYYYMMDD) ex: 20190113</div>'
                theDate = getDate(msg)
                if theDate:
                    self.settings.setValue('theDate', theDate)
                    self.sc.ui.dateEdit.setDate(pd2qtime(theDate, qdate=True))
                else:
                    return
            ds = DasStatement(jf.infile, self.settings, self.theDate)
            df = ds.getTrades()
            self.runDBInput(self.theDate, jf)
            return
            try:
                tkt = Ticket(jf)
            except ValueError as ex:
                msg = '<h3>The input file has caused a ValueError:</h3><ul> '
                msg = msg + '<div><strong>' + ex.__str__() + '</strong></div>'
                msg = msg + '<div>Did you export the trades window?</div>'
                msg = msg + '<div>If so, please configure the table in DAS to have the necessary fields and re-export it.</div>'
                msgbx = QMessageBox()
                msgbx.setIconPixmap(QPixmap("images/ZSLogo.png"));
                msgbx.setText(msg)
                msgbx.exec()
                return

            df, jf = tkt.getTrades()
        # trades = pd.read_csv(jf.inpathfile)
        else:
            #Temporary
            print('Opening a non standard file name in DAS')
            tkt = Ticket(jf)
            df, jf = tkt.getTrades()

        print('check for multiday')

        idf = InputDataFrame()
        trades, success = idf.processInputFile(df, jf.theDate, jf)
        if not success:
            return

        tu = DefineTrades(self.inputtype)
        inputlen, dframe, ldf = tu.processOutputDframe(trades)
        self.inputlen = inputlen

        # images and Trade Summaries.
        margin = 25

        lf = LayoutForms(self.sc, jf, dframe)
        lf.pickleitnow()
        tradeSummaries = lf.runTtoSummaries(ldf)
        # self.ldf = ldf
        # self.dframe = dframe


def main():
    ddiirr = os.path.dirname(__file__)

    # Paths used in summaryform.ui rely on cwd .
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    s = QStyleFactory.create('Fusion')
    app.setStyle(s)
    w = SumControl()
    rc = runController(w)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()    
