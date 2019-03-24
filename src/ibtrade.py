'''
@author: Mike Petersen
Top level module currently.
'''
import sys
from PyQt5.QtWidgets import QApplication

from journalfiles import JournalFiles
from journal.pandasutil import InputDataFrame
from journal.statement import Statement as Ticket
from journal.definetrades import DefineTrades
from journal.layoutsheet import LayoutSheet
from journal.tradestyle import TradeFormat
from journal.dailysumforms import MistakeSummary
from journal.qtform import QtForm
from journal.statement import getTrades_IBActivity
# pylint: disable=C0103

# jf = JournalFiles(theDate=dt.date(2019, 1, 25), mydevel=True)


def run(infile='trades.csv', outdir=None, theDate=None, indir=None, infile2=None, mydevel=True):
    '''Run structjour'''
    #  indir=None, outdir=None, theDate=None, infile='trades.csv', mydevel=False
    jf = JournalFiles(indir=indir, outdir=outdir,
                      theDate=theDate, infile=infile, mydevel=mydevel)

    df = getTrades_IBActivity(jf.inpathfile)

    tkt = Ticket(jf, df)

    # trades, jf = tkt.newDFSingleTxPerTicket()
    # trades = pd.read_csv(jf.inpathfile)
    trades = df

    idf = InputDataFrame()
    trades = idf.processInputFile(trades)

    tu = DefineTrades()
    inputlen, dframe, ldf = tu.processOutputDframe(trades)

    # Process the openpyxl excel object using the output file DataFrame. Insert
    # images and Trade Summaries.
    margin = 25

    # Create the space in dframe to add the summary information for each trade.
    # Then create the Workbook.
    ls = LayoutSheet(margin, inputlen)
    imageLocation, dframe = ls.createImageLocation(dframe, ldf)
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
    theD = '2019-03-21'
    outd = 'out/'
    inf1 ='ActivityStatement.20190321.html'
    inf2 ='trades.643495.20190321.html'
    inf2 ='CSVTrades.644223.20190321.csv'
    inf = inf1
    # outd = None
    # theD = None
    ind = None
    mydev = True
    run(infile=inf1, outdir=outd, theDate=theD, indir=ind, infile2=None, mydevel=mydev)
