'''
@author: Mike Petersen
Top level module currently.
'''
import sys
from PyQt5.QtWidgets import QApplication

from journalfiles import JournalFiles
from journal.pandasutil import InputDataFrame, ToCSV_Ticket as Ticket
from journal.definetrades import DefineTrades
from journal.layoutsheet import LayoutSheet
from journal.tradestyle import TradeFormat
from journal.dailysumforms import MistakeSummary
from journal.qtform import QtForm
# pylint: disable=C0103

# jf = JournalFiles(theDate=dt.date(2019, 1, 25), mydevel=True)


def run(infile='trades.csv', outdir=None, theDate=None, indir=None, mydevel=True):
    '''Run structjour'''
    #  indir=None, outdir=None, theDate=None, infile='trades.csv', mydevel=False
    jf = JournalFiles(indir=indir, outdir=outdir,
                      theDate=theDate, infile=infile, mydevel=mydevel)

    tkt = Ticket(jf)
    trades, jf = tkt.newDFSingleTxPerTicket()
    # trades = pd.read_csv(jf.inpathfile)

    idf = InputDataFrame()
    trades = idf.processInputFile(trades, jf.theDate)

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
    theD = '2019-03-01'
    outd = 'out/'
    inf = None
    outd = None
    theD = None
    ind = None
    mydev = True
    run(infile=inf, outdir=outd, theDate=theD, indir=ind, mydevel=mydev)
