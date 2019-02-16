'''
@author: Mike Petersen
Top level module currently.
'''

# from PyQt5.QtWidgets import QApplication

from journalfiles import JournalFiles
from journal.pandasutil import InputDataFrame, ToCSV_Ticket as Ticket
from journal.tradeutil import TradeUtil
from journal.layoutsheet import LayoutSheet
from journal.tradestyle import TradeFormat
from journal.mstksum import MistakeSummary
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
    trades = idf.processInputFile(trades)

    tu = TradeUtil()
    inputlen, dframe, ldf = tu.processOutputDframe(trades)

    # Process the openpyxl excel object using the output file DataFrame. Insert
    # images and Trade Summaries.
    sumSize = 25
    margin = 25

    # Create the space in dframe to add the summary information for each trade.
    # Then create the Workbook.
    ls = LayoutSheet(sumSize, margin, inputlen)
    imageLocation, dframe = ls.createImageLocation(dframe, ldf)
    wb, ws, nt = ls.createWorkbook(dframe)

    tf = TradeFormat(wb)
    ls.styleTop(ws, len(nt.columns), tf)
    assert len(ldf) == len(imageLocation)

    mstkAnchor = (len(dframe.columns) + 2, 1)
    mistake = MistakeSummary(numTrades=len(ldf), anchor=mstkAnchor)
    mistake.mstkSumStyle(ws, tf, mstkAnchor)
    mistake.dailySumStyle(ws, tf, ldf, mstkAnchor)

    tradeSummaries = ls.createSummaries(imageLocation, ldf, jf, ws, tf)
    # app = QApplication(sys.argv)
    # qtf = QtForm()
    # qtf.fillForm(tradeSummaries[2])
    # app.exec_()

    ls.createMistakeForm(tradeSummaries, mistake, ws, imageLocation)
    ls.createDailySummaryForm(tradeSummaries, mistake, ws, mstkAnchor)

    ls.save(wb, jf)
    print("done")
    return jf


if __name__ == '__main__':
    inf = None
    outd = 'out/'
    # theD = '2019-02-08'
    theD = None
    ind = None
    mydev = True
    run(infile=inf, outdir=outd, theDate=theD, indir=ind, mydevel=mydev)
