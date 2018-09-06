import datetime, os

from PIL import Image as PILImage
from PIL import ImageGrab
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.utils.dataframe import dataframe_to_rows

from journalfiles import JournalFiles
import pandas as pd
from structjour.pandasutil import DataFrameUtil, InputDataFrame


# TODO Add a module that accesses strategies to help with the daily analysis. Should include descriptions of accepted strategies 
# and personal strategies. Save the material in a sqllite db. Unspecified version for this one. Probably an elemental version of 
# this in version 1. 
#     Morning ORB, ABCD, VWAP Reversal (Bull Flag and Fallen angel for low float).
#     Late Morning VWAP false break out and VWAP reversal
#     Mid-Day VWAP Moving Average Trend VWAP false breakout
#     Close VWAP MA Trend
# Version 0 will be console app and include prompts for required input and the stops, targets, explanation and analysis. 
# The nature of those will change when this moves to a windowed app
# TODOVersion 1 will have a gui and can include videos 
# Version 2 is going to be the summary stuff.
# Version 2.5 will include archive saving of all the input of Trades from DAS (Datess may be an issue as DAS Trades window is time only (I think)
# Make sure the hour string is 0 padded.  Should probably change these to data types. 
# jf = JournalFiles(indir= "C:\trader\journal\_08_August\Week_5\_0831_Friday",mydevel=True)



def writeShareBalance(dframe) :
    prevBal = 0
    for i, row in dframe.iterrows():
        qty = (dframe.at[i,'Qty'])
        if row['Side'].startswith("HOLD") :
            print("got it at ", qty)
            qty = qty * -1
        newBalance = qty + prevBal

        dframe.at[i,'Balance'] = newBalance 
        prevBal = newBalance    
    return nt

def addStartTime(dframe) :
    newTrade = True
    for i, row in dframe.iterrows():
#         print(i, row['Time'])
        if newTrade :
            if row['Side'].startswith('HOLD') and i < len(dframe):
                
                oldTime = dframe.at[i+1, 'Time']
#                 print("     :Index: {0},  Side: {1}, Time{2}, setting {3}".format(i, row['Side'], row['Time'], oldTime))
                dframe.at[i, 'Start'] = oldTime

            else :
                oldTime = dframe.at[i, 'Time']
#                 print("     :Index: {0},  Side: {1}, Time{2}, setting {3}".format(i, row['Side'], row['Time'], oldTime))
                dframe.at[i, 'Start'] = oldTime
                
                
            newTrade = False
        else :
#             print("      Finally :Index: {0},  Side: {1}, Time{2}, setting {3}".format(i, row['Side'], row['Time'], oldTime))
            dframe.at[i, 'Start'] = oldTime
        if row['Balance'] == 0 :
#             print("       setting newTrade")
            newTrade = True
    return dframe
        
def addTradeIndex(dframe) :

    TCount = 1
    prevEndTrade = -1

    for i, row in dframe.iterrows():
        if len(row['Symb']) < 1 :
            break
        tradeIndex = "Trade " + str(TCount)
        if prevEndTrade == 0:
            TCount = TCount + 1
            prevEndTrade = -1
        tradeIndex = "Trade " + str(TCount)
        dframe.at[i,'Tindex'] = tradeIndex 
        if row['Balance'] == 0 :
            prevEndTrade = 0
    numTrades = TCount
    print(numTrades)        
    return dframe
# This will blow up from wrong types if there is some kind of anomaly. The blank rows in 
# Sum col are str and the filled rows are float. Don't fix it until it blows up. (or you 
# need change this 'now' to production code for some reason) That way we have some case to fix.

def addTradePL (dframe) :
    tradeTotal = 0.0
    for i, row in dframe.iterrows():
        if row['Balance'] != 0 :
            tradeTotal = tradeTotal + row['P / L']
        else :
            sumtotal = tradeTotal + row['P / L']
            dframe.at[i, 'Sum'] = sumtotal
            tradeTotal = 0
    return dframe

def addTradeDuration(dframe) :
    
    tradeTotal = 0.0
    for i, row in dframe.iterrows():
        if row['Balance'] == 0 :
            timeEnd = row['Time']
            timeStart = row['Start']
            end=timeEnd.split(":")
            start=timeStart.split(":")
            diff = datetime.datetime(1,1,1,int(end[0]), int(end[1]), int(end[2])) - datetime.datetime(1,1,1,int(start[0]), int(start[1]), int(start[2]))
            dframe.at[i,'Duration'] = diff
    return dframe


# In[ ]:


def addTradeName(dframe) :
    for i, row in dframe.iterrows():
        longShort = " Long"
        if row['Balance'] == 0 :
            if row['Side'] == 'B' :
                longShort = " Short"
            dframe.at[i, 'Name'] = row['Symb'] + longShort
    return dframe

# Note that .sum() should work on this but it failed when I tried it.
def addSummaryPL(dframe) :
    
    count=0
    tot=0.0
    tot2 = 0.0
    for i, row in dframe.iterrows():
        count=count+1
        if count < len(dframe) :
            tot=tot+row['P / L']
            if row['Balance'] == 0 :
 
                tot2 = tot2 + row['Sum']
            if count == len(dframe) -1 :
                lastCol = row['P / L']

                print("Last col?", row['P / L'])
   
        else :
            dframe.at[i, 'P / L'] = tot
            dframe.at[i, 'Sum'] = tot2

    if lastCol > 0:

        print('''
        Some shares are unaccounted for. Please send the original csv file to the developer in 
        order to fix ths issue in the software. Please remove the account number  or change its value
        to anything else.
        ''')
    return dframe

# Adjust size to keep the aspect ration
# The actual version should calculate the height based
# no the number of cells between entries. That 
# will be a number chosen by the user (with constraints) 
# pixels per cell height is about 20.238095238095237
# The default size (425) is height about 21 unaltered excel cells

def adjustSizeByHeight(sz, newHeight=425) :
    w,h = sz
    newWidth = int((newHeight/h) * w)
    newheight = int(newHeight)
    return(newWidth, newHeight)

def getPilImageFromClipboard() :
    for i in range (5) :
        response = input("Are you ready? ")
        if response.lower().startswith('y') : 
            im = ImageGrab.grabclipboard()
            if im is None :
                print("Failed to get an image. Please select and copy an image")
            else :
                return im
        else :
            if response.lower().startswith('q') :
                return None
    print("Moving on")


# orig: an image file name
# Returns a tuple(newFileName, extension)
#     changes jpg to jpeg to appease PIL.save()

def getResizeName(orig) :
    x=os.path.splitext(orig)
    if (len (x[1]) < 4 ) :
        print("please provide an image name with an image extension in its name. e.g 'png', jpg', etc")
    newName = x[0] + '_resize'
    if 'jpg' in x[1].lower() :
        newName += '.jpeg'
    else :
        newName += x[1]
    newName = os.path.join(jf.outdir, newName)
    return (newName, os.path.splitext(newName)[1][1:])

# dframe contains the transactions of a single trade.  Single trade ends when the balance 
# of shares is 0
# Return value is a string 'Long' or 'Short'
def getLongOrShort(dframe) :
    tsx = dframe[dframe.Balance == 0]

    
    if len(tsx) != 1 :
        return None
    if str(tsx.Side) == 'B' or str(tsx.Side) == 'Hold-':
        return 'Short'    
    else :
        return 'Long'
    
# dframe contains the transactions of a single trade.  longOrShort needs to be a str 'Long' 
# or 'Short'. Will raise an exception if they are not Returns a tuple of dataFrames 
# (entries, exits)-- not ready for prime time
# def getEntriesAndExits(dframe,longOrShort) :
#     if longOrShort.lower() not in ['long', 'short'] :
#         #Programming error if we are here
#         raise NameError('getEntriesAndExits requires a parameter of either Long or Short. 
#             %s is not acceptible' % longOrShort)
#         return None
#     f_ent, f_ext = ('B', 'S') if longOrShort == 'Long' else ('S', 'B')
#     ent = tdf[tdf.Side.str.startswith(f_ent)]
#     ext = tdf[tdf.Side.str.startswith(f_ext)]
#     return ent, ext
# getEntriesAndExits(tdf, 'Short')[0]
finalReqCol = ['Tindex', 'Start', 'Time', 'Symb', 'Side', 'Price', 'Qty','Balance', 'Account', "P / L", 'Sum', 'Duration', 'Name']

# jf= JournalFiles(indir =r'C:\trader\journal\_09_September\Week_1\_0904_Tuesday', infile='trades1.csv', mydevel=True)
jf = JournalFiles(theDate=datetime.date(2018, 9,4), mydevel=True)
# jf = JournalFiles(indir='data', infile='TradesWithHolds.csv', outdir = "out", mydevel=True)

trades = pd.read_csv(jf.inpathfile)

idf = InputDataFrame()

reqCol = idf.reqCol.values()

DataFrameUtil.checkRequiredInputFields(trades, reqCol)

trades = idf.zeroPadTimeStr(trades)
trades = trades.sort_values(['Symb', 'Time'])
trades = idf.mkShortsNegative(trades)

swingTrade = idf.getOvernightTrades(trades)

swingTrade = idf.figureOvernightTransactions(trades)
listdf = idf.insertOvernightRow(trades, swingTrade)


for l in finalReqCol :
    if l not in listdf.columns :
        listdf[l] = ''

# trades.columns
newTrades = listdf[finalReqCol]
newTrades.copy()
nt = newTrades.sort_values(['Symb', 'Time'])
nt = writeShareBalance(nt)
nt = addStartTime(nt)
nt = nt.sort_values(['Start', 'Time'])
nt = addTradeIndex(nt)
nt = addTradePL(nt)
nt = addTradeDuration(nt)
nt = addTradeName(nt)
nt=DataFrameUtil.addRows(nt,1)
nt = addSummaryPL(nt)

# Request a clipboard copy of an image. Resze it to newSize height. Save it with a new name. 
# Return the name. Hackiness lives
# until I figure how to create a proper openpyxl Image object from a PIL Image object that 
# doesn't make the Workbook puke.
def getAndResizeImage (newSize) :
    try :
#         pilImage= PILImage.open(imgName)
        pilImage = getPilImageFromClipboard() 
        newSize = adjustSizeByHeight(pilImage.size)
        pilImage = pilImage.resize(newSize, PILImage.ANTIALIAS)
        resizeName, ext = getResizeName(imgName)
        pilImage.save(resizeName, ext)

    except IOError as e :
        print("An exception occured '%s'" % e)
    return resizeName

# Now  we are going to add each trade and insert space to put in pictures with circles and 
#arrows and paragraph on the back of each one to be used as evidence against you in a court 
# of law (or court of bb opionion)
insertsize=25
dframe = nt
ldf = list()
count = 1
while True :
    tradeStr = "Trade " + str(count)
    count = count + 1
    tdf = dframe[dframe.Tindex == tradeStr]
    if len(tdf) > 0 :
        ldf.append(tdf)
    else :
        break
len(ldf)

dframe = DataFrameUtil.addRows(dframe, 2)
# TODO The Hold is not operating correctly. This method is writen like I intend it to 
# function

entries = list()
exits= list()
for tdf in ldf:
    longOrShort = getLongOrShort(tdf)
    
    ent = tdf[tdf.Side == 'B']
    ext = tdf[tdf.Side.str.startswith('S')]
    entries.append(ent)
    exits.append(ext)
    print(getLongOrShort(tdf))
        
    break

for tdf in ldf:
    print (tdf.Tindex.unique()[0].replace(' ','') + '.jpeg')

s = 'Trade 1'.replace(" ", "") + '.jpeg'
s

print(ldf[0].Tindex.unique()[0])
print (ldf[0].Name.unique()[-1])
print(ldf[0].Start.unique()[0])
print (ldf[0].Duration.unique()[-1])


# The Dataframe grabs here rely far too much on proper placement by this program. This is no 
# longer DataFrame like data manipulation. The manipulation is far too specific to the
# processing. At this point, the trades should be encapsulated in objects.

# In[ ]:imageLocation = list()
newdf = DataFrameUtil.createDf(dframe,  10)
topMargin = 10
dframe = newdf.append(dframe, ignore_index = True)
imageLocation = list()
for tdf in ldf :

    # TODO handle empty string in the tdf
    imageLocation.append([len(tdf) + len(dframe) + 2, 
                          tdf.Tindex.unique()[0].replace(' ', '') + '.jpeg',
                          tdf.Name.unique()[-1],
                          tdf.Start.unique()[-1],
                        tdf.Duration.unique()[-1]])
    print(len(tdf) + len(dframe) + 2)

    dframe = dframe.append(tdf, ignore_index = True)
    dframe = DataFrameUtil.addRows(dframe, insertsize)
    print(count, ": ", len(dframe))

len(dframe)

for x in imageLocation :
    print(x)

# for tdf in ldf :
#     dframe = dframe.append(tdf, ignore_index = True)
#     dframe = addRows(dframe, insertsize)
#     print(count, ": ", len(dframe))
    
nt = dframe
# TODO - Catch Permission Denied exception and inform the user


wb = Workbook()
ws = wb.active

for r in dataframe_to_rows(nt, index=False, header=False):
    ws.append(r)


# In[ ]:


for name, cell  in zip(nt.columns, ws[topMargin]) :
    cell.value = name

for c in ws[10] :
    print (c.value)

for i in imageLocation :
    print('Copy an image into the clipboard for {0} beginning {1}, and lasting {2}'.format(i[2], i[3], i[4]))

imgName = 'tempImage.jpg'
for loc in imageLocation :
    try :
        pilImage = getPilImageFromClipboard() 
        newSize = adjustSizeByHeight(pilImage.size)
        pilImage = pilImage.resize(newSize, PILImage.ANTIALIAS)
        print('Copy an image into the clipboard for {0} beginning {1}, and lasting {2}'.format(loc[1], loc[2], loc[3]))
        resizeName, ext = getResizeName(loc[1])
        print (resizeName)
        pilImage.save(resizeName, ext)
        img = Image(resizeName)
        cellname = 'E' + str(loc[0])
        ws.add_image(img, cellname)
        print(cellname)
            
            
    except IOError as e :
        print("An exception occured '%s'" % e)

for c in ws[10]:
    print(c.value)

jf.mkOutdir() 
try :
    wb.save(jf.outpathfile)
except Exception as ex :
    print(ex)
    print("Failed to create file {0}".format(jf.outpathfile))
    print("Created images were saved in {0}".format(jf.outdir))

# tdir='C:\\trader\\journal\\_08_August\\Week_4\\_0821_Tuesday\\'
# tdir = "out"
# outfile=tdir+ name
# nt.to_csv(outfile)

# nt.to_excel(outFile, index=False)


