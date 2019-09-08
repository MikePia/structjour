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
@author: Mike Petersen
Top level module currently.
'''
# from PyQt5.QtWidgets import QApplication
import os
from PyQt5.QtCore import QSettings

from journal.journalfiles import JournalFiles
from journal.pandasutil import InputDataFrame
from journal.statement import Statement_DAS as Ticket
from journal.statement import Statement_IBActivity
from journal.definetrades import DefineTrades
from journal.layoutsheet import LayoutSheet
from journal.tradestyle import TradeFormat
from journal.dailysumforms import MistakeSummary
# from journal.qtform import QtForm
# pylint: disable=C0103

# jf = JournalFiles(theDate=dt.date(2019, 1, 25), mydevel=True)


def run(infile='trades.csv', outdir=None, theDate=None, indir=None, infile2=None, mydevel=True):
    '''
    Run structjour. Temporary picker for input type based on filename. If infile has 'activity' in
    it and ends in .html, then its IB Activity Statement web page (as a file on this system)
    :params infile: Name of the input file. Default trades.csv--a DAS export from the trades window.
                    If infile contains the string 'trades', input type is set to DAS.
                    If infile contains the string 'activity', input type is set to IB Activity.
                    Default will try DAS
    :params outdir: Location to write the output file.
    :params theDate: The date of this input file. If trades lack a Date, this date be the trade date.
    :params indir: Location of the input file.
    :parmas infile2: Name of the DAS positions file. Will default to indir/positions.csv  
    :params mydevel: If True, use a specific file structure and let structjour create it. All can 
                     be overriden by using the specific parameters above.
    '''
    settings = QSettings('zero_substance', 'structjour')
    settings.setValue('runType', 'CONSOLE')
    #  indir=None, outdir=None, theDate=None, infile='trades.csv', mydevel=False
    jf = JournalFiles(indir=indir, outdir=outdir,
                      theDate=theDate, infile=infile, infile2=infile2, mydevel=mydevel)

    name, ext = os.path.splitext(jf.infile.lower())
    if name.find('activity') > -1 and ext == '.html':
        jf.inputType = 'IB_HTML'
        statement = Statement_IBActivity(jf)
        df = statement.getTrades_IBActivity(jf.inpathfile)
    elif  name.find('trades') > -1 and ext == '.csv':
        # This could be an IB CSV--so this is temporary-- when I enable some sort of IB CSV, will
        # probably do some kind of class heirarchy here for statements. 
        tkt = Ticket(jf)
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
        print('Failed. Between you and me, I think its a programming error')
        return jf

    tu = DefineTrades()
    inputlen, dframe, ldf = tu.processOutputDframe(trades)

    # Process the openpyxl excel object using the output file DataFrame. Insert
    # images and Trade Summaries.
    margin = 25

    # Create the space in dframe to add the summary information for each trade.
    # Then create the Workbook.
    ls = LayoutSheet(margin, inputlen)
    imageLocation, dframe = ls.imageData(dframe, ldf)
    wb, ws, nt = ls.createWorkbook(dframe)

    tf = TradeFormat(wb)
    ls.styleTop(ws, len(nt.columns), tf)
    assert len(ldf) == len(imageLocation)

    mstkAnchor = (len(dframe.columns) + 2, 1)
    mistake = MistakeSummary(numTrades=len(ldf), anchor=mstkAnchor)
    mistake.mstkSumStyle(ws, tf, mstkAnchor)
    mistake.dailySumStyle(ws, tf, mstkAnchor)

    tradeSummaries = ls.runSummaries(imageLocation, ldf, jf, ws, tf)
    # app = QApplication(sys.argv)
    # qtf = QtForm()
    # qtf.fillForm(tradeSummaries[1])
    # app.exec_()

    ls.populateMistakeForm(tradeSummaries, mistake, ws, imageLocation)
    ls.populateDailySummaryForm(tradeSummaries, mistake, ws, mstkAnchor)

    ls.save(wb, jf)
    print("Processing complete. Saved {}".format(jf.outpathfile))
    return jf


if __name__ == '__main__':
    theD = '2019-02-13'
    # inf = 'trades.1116_messedUpTradeSummary10.csv'
    # inf = 'ActivityStatement.20190321.html'
    # theD = None
    outd = 'out/'
    inf = None
    positions = 'None'
    ind = None
    mydev = True
    run(infile=inf, outdir=outd, theDate=theD, indir=ind, infile2=positions, mydevel=mydev)
