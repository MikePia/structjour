'''
@author: Mike Petersen
Top level module currently.
'''
# from PyQt5.QtWidgets import QApplication

from journalfiles import JournalFiles
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
    '''Run structjour'''
    #  indir=None, outdir=None, theDate=None, infile='trades.csv', mydevel=False
    jf = JournalFiles(indir=indir, outdir=outdir,
                      theDate=theDate, infile=infile, infile2=infile2, mydevel=mydevel)

    # tkt = Ticket(jf)
    # trades, jf = tkt.getTrades()
    # trades = pd.read_csv(jf.inpathfile)
    statement = Statement_IBActivity()
    df = statement.getTrades_IBActivity(jf.inpathfile)

    idf = InputDataFrame()
    trades = idf.processInputFile(df, jf.theDate, jf)

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
    # theD = None
    inf = None
    inf = 'ActivityStatement.20190321.html'
    # outd = None
    # positions = 'positions.csv'
    positions = None
    ind = None
    mydev = True
    run(infile=inf, outdir=outd, theDate=theD, indir=ind, infile2=positions, mydevel=mydev)
