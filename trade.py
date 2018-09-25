import datetime, os


from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.utils.dataframe import dataframe_to_rows

from journalfiles import JournalFiles
import pandas as pd
from structjour.pandasutil import DataFrameUtil, InputDataFrame, ToCSV_Ticket as Ticket
from structjour.tradeutil import ReqCol, FinReqCol, XLImage, TradeUtil
from withstyle.thetradeobject import SumReqFields, TheTradeObject
from withstyle.tradestyle import TradeFormat
#TradeUtil, FinReqCol, ReqCol, 

# jf = JournalFiles(indir= "C:\trader\journal\_08_August\Week_5\_0831_Friday",mydevel=True)

# jf= JournalFiles(indir =r'C:\trader\journal\_09_September\Week_1\_0904_Tuesday', infile='trades1.csv', mydevel=True)
# jf = JournalFiles(theDate=datetime.date(2018, 9,6), outdir = 'out', mydevel=True)
# jf = JournalFiles(indir='data', infile='TradesWithHolds.csv', outdir = "out", mydevel=True)
# jf = JournalFiles(theDate = datetime.date(2018, 9, 7), outdir = 'out', mydevel = True)
# jf = JournalFiles(theDate=datetime.date(2018,9,11), mydevel = True)
jf=JournalFiles(outdir='out/', mydevel=True)
jf._printValues()
        
tkt = Ticket(jf)

tu = TradeUtil()
trades, jf =tkt.newDFSingleTxPerTicket()
# trades = pd.read_csv(jf.inpathfile)

idf = InputDataFrame()
reqCol = ReqCol()
finalReqCol = FinReqCol()

DataFrameUtil.checkRequiredInputFields(trades, reqCol.columns)
trades = idf.zeroPadTimeStr(trades)
trades = trades.sort_values([reqCol.acct, reqCol.ticker, reqCol.time])
trades = idf.mkShortsNegative(trades)
swingTrade = idf.getOvernightTrades(trades)
swingTrade = idf.figureOvernightTransactions(trades)
trades = idf.insertOvernightRow(trades,swingTrade)

trades = tu.addFinReqCol(trades)
newTrades = trades[finalReqCol.columns]
newTrades.copy()
nt = newTrades.sort_values([finalReqCol.ticker,finalReqCol.acct,  finalReqCol.time])
nt = tu.writeShareBalance(nt)
nt = tu.addStartTime(nt)
nt = nt.sort_values([finalReqCol.start, finalReqCol.acct, finalReqCol.time])
nt = tu.addTradeIndex(nt)
nt = tu.addTradePL(nt)
nt = tu.addTradeDuration(nt)
nt = tu.addTradeName(nt)
nt=DataFrameUtil.addRows(nt,1)
nt = tu.addSummaryPL(nt)
    
ldf=tu.getTradeList(nt)

dframe = DataFrameUtil.addRows(nt, 2)


# entries = list()
# exits= list()
# for tdf in ldf:
#     longOrShort = tu.getLongOrShort(tdf)
#     
#     ent = tdf[tdf.Side == 'B']
#     ext = tdf[tdf.Side.str.startswith('S')]
#     entries.append(ent)
#     exits.append(ext)
#     print(tu.getLongOrShort(tdf))
#         
#     break
# 
# for tdf in ldf:
#     print (tdf.Tindex.unique()[0].replace(' ','') + '.jpeg')
# 
# print(ldf[0].Tindex.unique()[0])
# print (ldf[0].Name.unique()[-1])
# print(ldf[0].Start.unique()[0])

print (ldf[0].Duration.unique()[-1])

topMargin = 10
newdf = DataFrameUtil.createDf(dframe,  topMargin)
insertsize = 25
dframe = newdf.append(dframe, ignore_index = True)

#Add rows and append each trade, leaving space for an image. Create a list of names and rows numbers 
# to place images within the excel file.
imageLocation = list()
for tdf in ldf :
    imageName='{0}_{1}_{2}_{3}.jpeg'.format (tdf[finalReqCol.tix].unique()[-1].replace(' ',''), 
           tdf[finalReqCol.name].unique()[-1].replace(' ','-'),
           tdf[finalReqCol.start].unique()[-1],
           tdf[finalReqCol.dur].unique()[-1])

    # TODO handle empty string in the tdf
    imageLocation.append([len(tdf) + len(dframe) + 2, 
                          tdf.Tindex.unique()[0].replace(' ', '') + '.jpeg',
                          imageName,
                          tdf.Start.unique()[-1],
                        tdf.Duration.unique()[-1]])
    print(len(tdf) + len(dframe) + 2)

    dframe = dframe.append(tdf, ignore_index = True)
    dframe = DataFrameUtil.addRows(dframe, insertsize)
    print(len(dframe))

nt = dframe

wb = Workbook()
ws = wb.active

for r in dataframe_to_rows(nt, index=False, header=False):
    ws.append(r)


for name, cell  in zip(nt.columns, ws[topMargin]) :
    cell.value = name




XL = XLImage()

srf = SumReqFields()
tradeSummaries = list()
tf = TradeFormat(wb)
assert (len(ldf) == len(imageLocation))
     
response = input("Would you like to enter strategy names, targets and stops?")
interview = True if response.lower().startswith('y') else False
for loc, tdf in zip(imageLocation, ldf) :
#     print('Copy an image into the clipboard for {0} beginning {1}, and lasting {2}'.format(loc[1], loc[2], loc[3]))
    img = XL.getAndResizeImage(loc[2], jf.outdir)
    cellname = 'J' + str(loc[0])
    ws.add_image(img, cellname)
    
    #Put together the summary info and interview the trader
    tto=TheTradeObject(tdf, interview)
    tto.runSummary()
    tradeSummaries.append(tto)
    
    #Place the format shapes/styles in the worksheet
    tf.formatTrade(ws, anchor=(1, loc[0]))
    
print("Done with interview")


jf.mkOutdir() 
saveName=jf.outpathfile
count=1
while True :
    try :
        wb.save(saveName)
    except PermissionError as ex :
        print(ex)
        print("Failed to create file {0}.{1}".format(saveName, ex))
        print("Images from the clipboard were saved  in {0}".format(jf.outdir))
        (nm, ext) = os.path.splitext(jf.outpathfile)
        saveName = "{0}({1}){2}".format(nm,count,ext)
        print("Will try to save as {0}".format(saveName))
        count=count+1
        if count==6:
            print("Giving up. PermissionError")
            raise (PermissionError("Failed to create file {0}".format(saveName)))
        continue
    except Exception as ex:
        print (ex)
    break
print("Done!")
