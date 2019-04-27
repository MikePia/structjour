'''
Created on Apr 1, 2019

@author: Mike Petersen
'''


import os
import pickle
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QFileDialog, QMessageBox

import pandas as pd

from journal.pandasutil import InputDataFrame
from journal.statement import Statement_DAS as Ticket
from journal.statement import Statement_IBActivity
from journal.definetrades import DefineTrades
from journal.tradestyle import TradeFormat
from journal.dailysumforms import MistakeSummary
from journal.view.layoutforms import LayoutForms



from journalfiles import JournalFiles
from journal.view.sumcontrol import SumControl
from journal.view.summaryform import Ui_MainWindow


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


        # Defining this one connection here. Its different than all the others
        
        self.ui.goBtn.pressed.connect(self.runnit)
        self.ui.loadBtn.pressed.connect(self.loadit)

    def initialize(self):
        ### Might blitz thes lines if JournalFiles gets an overhaul. For ease of transaiton
        ### We keep JournalFiles till its allworks into the Qt run
        self.settings = self.sc.settings
        self.inputtype = self.settings.value('inputType')
        self.indir = self.sc.getDirectory()
        if self.inputtype == 'DAS':
            inkey = 'dasInfile'
        elif self.inputtype == 'IB_HTML':
            inkey = 'ibInfileName'
        if self.settings.value('outdirPolicy') == 'default':
            self.outdir = None
        else:
            self.outdir = self.settings.value('outdir')
        qd = self.settings.value('theDate')
        self.theDate = pd.Timestamp(qd.year(), qd.month(), qd.day())
        self.positions = self.settings.value('dasInfile2')

        ### end blitz
        self.infile = self.settings.value(inkey)
        self.inpathfile = self.ui.infileEdit.text()
        print(self.inpathfile)

    def loadit(self):
        print('gonna loadit gonna loadit')
        daDate = self.ui.dateEdit.date()
        self.settings.setValue('theDate', daDate)
        self.initialize()
        jf = JournalFiles(indir=self.indir, outdir=self.outdir,
                      theDate=self.theDate, infile=self.infile,
                      inputType = self.inputtype, infile2=self.positions,
                      mydevel=True)



        lf = LayoutForms(self.sc, jf)
        lf.loadSavedFile()
        

    def runnit(self):
        print('gonna runnit gonna runnit')
        self.initialize()
        jf = JournalFiles(indir=self.indir, outdir=self.outdir,
                      theDate=self.theDate, infile=self.infile,
                      inputType = self.inputtype, infile2=self.positions,
                      mydevel=True)

        if self.inputtype == 'IB_HTML':
            jf.inputType = 'IB_HTML'
            statement = Statement_IBActivity(jf)
            df = statement.getTrades_IBActivity(jf.inpathfile)
        elif  self.inputtype == 'DAS':
            tkt = Ticket(jf)
            df, jf = tkt.getTrades()
        # trades = pd.read_csv(jf.inpathfile)
        else:
            #Temporary
            print('Opening a non standard file name in DAS')
            tkt = Ticket(jf)
            df, jf = tkt.getTrades()

        idf = InputDataFrame()
        trades,  success = idf.processInputFile(df, jf.theDate, jf)
        if not success:
            return

        tu = DefineTrades(self.inputtype)
        inputlen, dframe, ldf = tu.processOutputDframe(trades)

        # Process the openpyxl excel object using the output file DataFrame. Insert
        # images and Trade Summaries.
        margin = 25

        lf = LayoutForms(self.sc, jf)
        tradeSummaries = lf.runSummaries(ldf)




        


if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    w = SumControl()
    # formUi = Ui_MainWindow()
    # formUi.setupUi(w)
    # sc = SumControl(formUi)
    rc = runController(w)
    w.show()
    sys.exit(app.exec_())
