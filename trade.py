import datetime, os


# from openpyxl import Workbook
# from openpyxl.drawing.image import Image
# from openpyxl.utils.dataframe import dataframe_to_rows
# from openpyxl.worksheet.table import Table, TableStyleInfo

from journalfiles import JournalFiles
from journal.pandasutil import InputDataFrame, ToCSV_Ticket as Ticket
from journal.dfutil import DataFrameUtil
from journal.tradeutil import ReqCol, FinReqCol, TradeUtil
from journal.xlimage import XLImage
from withstyle.layoutsheet import LayoutSheet
from withstyle.thetradeobject import SumReqFields 
# , TheTradeObject
from withstyle.tradestyle import TradeFormat
# from withstyle.tradestyle import c as tcell
from withstyle.mstksum import MistakeSummary

# jf = JournalFiles(indir= "C:\trader\journal\_08_August\Week_5\_0831_Friday",mydevel=True)

# jf= JournalFiles(indir =r'C:\trader\journal\_09_September\Week_1\_0904_Tuesday', infile='trades1.csv', mydevel=True)
# jf = JournalFiles(theDate=datetime.date(2018, 9,6), outdir = 'out', mydevel=True)
# jf = JournalFiles(indir='data', infile='TradesWithHolds.csv', outdir = "out", mydevel=True)
# jf = JournalFiles(theDate = datetime.date(2018, 10, 1), outdir = 'out/', mydevel = True)
jf=JournalFiles(infile="trades2.csv", outdir="out/", mydevel=True)
# jf = JournalFiles(mydevel = True)
jf._printValues()
        
tkt = Ticket(jf)

tu = TradeUtil()
trades, jf =tkt.newDFSingleTxPerTicket()
# trades = pd.read_csv(jf.inpathfile)

idf = InputDataFrame()
trades = idf.processInputFile(trades)

inputlen, dframe, ldf = tu.processOutputDframe(trades)





#Process the openpyxl excel object using the output file DataFrame. Insert images and Trade Summaries.
sumSize = 25
margin=25

# Create the space in dframe to add the summary information for each trade. Then create the Workbook.
ls = LayoutSheet(sumSize,margin, inputlen)
imageLocation, dframe = ls.createImageLocation(dframe, ldf)
wb, ws, nt =ls.createWorkbook(dframe)
ls.styleTop(ws, nt)

XL = XLImage()
srf = SumReqFields()
tradeSummaries = list()
tf = TradeFormat(wb)
assert (len(ldf) == len(imageLocation))
mstkAnchor = (len(dframe.columns) + 2, 1)
mistake = MistakeSummary(numTrades=len(ldf), anchor=mstkAnchor)
mistake.mstkSumStyle(ws, tf, mstkAnchor)
     
response = input("Would you like to enter strategy names, targets and stops?")
interview = True if response.lower().startswith('y') else False

tradeSummaries = ls.createSummaries(imageLocation, ldf, XL, jf, interview, srf, ws, tradeSummaries, tf)

    

ls.createMistakeForm(tradeSummaries, mistake, ws, imageLocation)    
    
ls.save(wb, jf)

