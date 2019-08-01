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
from PyQt5.QtWidgets import QApplication, QStyleFactory, QMessageBox

from journal.definetrades import DefineTrades, FinReqCol
from journal.pandasutil import InputDataFrame
from journal.statements.ibstatementdb import StatementDB
from journal.statement import Statement_DAS as Ticket
from journal.statement import Statement_IBActivity
from journal.view.layoutforms import LayoutForms
from journal.view.sumcontrol import SumControl, qtime2pd
from journalfiles import JournalFiles

# pylint: disable = C0103


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
        self.settings.setValue('theDate', daDate)
        self.initialize()

        if not self.indir:
            print('What file is supposed to load?')
            return
        jf = JournalFiles(indir=self.indir, outdir=self.outdir, theDate=self.theDate,
                          infile=self.infile, inputType=self.inputtype, infile2=self.positions,
                          mydevel=True)
        if inputType == 'DB':
            self.runDBInput(daDate, jf)
            return

        lf = LayoutForms(self.sc, jf, None)
        lf.loadSavedFile()
        if lf.df is None:
            print('Did not load up correctly. Try pressing Go, Load, Save')

    def runDBInput(self, daDate, jf):
        statement = StatementDB()

        daDate = qtime2pd(daDate)

        rc = FinReqCol()
        data = statement.getStatement(daDate)
        columns = [rc.ticker, rc.date, rc.shares, rc.bal, rc.price, rc.avg, rc.PL, rc.acct, rc.oc, 'id', rc.comm]
        df = pd.DataFrame(data=data, columns=columns)
        df[rc.time] = ''
        for i, row in df.iterrows():
            df.at[i, rc.time] = row[rc.date][9:11] + ':' + row[rc.date][11:13] + ':' + row[rc.date][13:15]
        # df[rc.time] = df[rc.time].map(str) + df[rc.date][:6]
        df[rc.date] = pd.to_datetime(df[rc.date], format='%Y%m%d;%H%M%S')


        tu = DefineTrades(self.inputtype)
        # inputlen, dframe, ldf = tu.processOutputDframe(df)
        inputlen, dframe, ldf = tu.processDBTrades(df)
        # self.inputlen = inputlen

        # images and Trade Summaries.
        # margin = 25

        lf = LayoutForms(self.sc, jf, dframe)
        lf.pickleitnow()
        tradeSummaries = lf.runTtoSummaries(ldf)


    def runnit(self):
        '''
        Load an initial input file and process it.
        '''
        print('gonna runnit gonna runnit')
        self.initialize()
        if not self.indir:
            print('What file is supposed to load?')
            return
        jf = JournalFiles(indir=self.indir, outdir=self.outdir, theDate=self.theDate,
                          infile=self.infile, inputType=self.inputtype, infile2=self.positions,
                          mydevel=True)

        if self.inputtype == 'IB_HTML':
            jf.inputType = 'IB_HTML'
            statement = Statement_IBActivity(jf)
            df = statement.getTrades_IBActivity(jf.inpathfile)
        elif  self.inputtype == 'DAS':
            try:
                tkt = Ticket(jf)
            except ValueError as ex:
                msg = '<h3>The input file has caused a ValueError:</h3><ul> '
                msg = msg + '<div><strong>' + ex.__str__() + '</strong></div>'
                msg = msg + '<div>Did you export the trades window?</div>'
                msg = msg + '<div>If so, please configure the table in DAS to have the necessary fields and re-export it.</div>'
                msgbx = QMessageBox()
                msgbx.setIconPixmap(QPixmap("../../images/ZSLogo.png"));
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



if __name__ == '__main__':
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
