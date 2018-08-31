
# coding: utf-8

# ### Add a module that accesses strategies to help with the daily analysis. Should include descriptions of accepted strategies and personal strategies. Save the material in a sqllite db. Unspecified version for this one. Probably an elemental version of this in version 1. 
# ###### Morning ORB, ABCD, VWAP Reversal (Bull Flag and Fallen angel for low float).
# ###### Late Morning VWAP false break out and VWAP reversal
# ###### Mid-Day VWAP Moving Average Trend VWAP false breakout
# ###### Close VWAP MA Trend
# ### Prototype version will have the features of version 1 but run in Jupyter notebook.
# ### Version 1 will include the kind of wizard daily review with prompts to get the picture (videos in an unspecified version) and the stops, targets, explanation and analysis. The nature of those will change when this moves to a windowed app
# ### Version 2 is going to be the summary stuff.
# ### Version 2.5 will include archive saving of all the input of Trades from DAS (Datess may be an issue as DAS Trades window is time only (I think)

# In[1]:


from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
import pandas as pd


# In[2]:


import datetime, os, openpyxl
from PIL import Image as PILImage
from PIL import ImageGrab


# In[3]:


# This directory stuff is for my system only. I think its a good idea but I need 
# some input. In the end I think the directory naming, creation and organization will 
# have to be optional. Personally, I am going to include the monthly utility to create 
# the structure in this program.  The ability to configure it would be a nice feature.

# In[47]:


theDate=datetime.date.today()
# theDate = datetime.date(2018,8,29)


# In[48]:


inname = 'trades.csv'
outname = theDate.strftime("Trades_%A_%m%d.xlsx")
print (inname, outname)


# In[49]:


theDirectory = theDate.strftime(r"C:\trader\journal\_%m_%B\Week_5\_%m%d_%A")
outDir = os.path.join(theDirectory, 'out')
if not os.path.isdir(theDirectory) :
    print('oops')
    raise(NameError('theDirectory ' + theDirectory + ' is not found.'))
else :
    if not os.path.isdir(outDir) :
        print('creating directory ' + outDir )
        os.mkdir(outDir)




# In[50]:


infile=os.path.join(theDirectory, 'trades.csv')
if not os.path.exists(infile) :
    print('Input file: ' + infile + ' does not exist')


# In[51]:


devOutDir = os.path.join(os.getcwd(), 'out')
if not os.path.isdir(devOutDir) :
    os.mkdir(devOutDir)
devOutFile = os.path.join(devOutDir, outname)

outdir=os.path.join(theDirectory,'out')
outFile=os.path.join(outdir, outname)

trades = pd.read_csv(infile)

def checkRequiredInputFields(dframe) :
    RequiredFields = ['Time', 'Symb', 'Side', 'Price', 'Qty', 'P / L']
    ActualFields=dframe.columns
    if set (RequiredFields) <= (set (ActualFields)) :
        print("got it")
    else :
        err='You are missing some fields in your input file:\n'
        err += str((set(RequiredFields) - set(ActualFields)))
        raise ValueError(err)

def createDf(dframe, numRow) :
    ''' Creates a new DataFrame with  the length numRow. Each cell is filled with empty string '''

    ll=list()
    r=list()
    for i in range(len(dframe.columns)) :
        r.append('')
        
    for i in range(numRow) :
        ll.append(r)
    newdf= pd.DataFrame(ll, columns=dframe.columns)

    return newdf


# In[ ]:


def addRows(dframe, numRow) :
    newdf= createDf(dframe, numRow)
        
    
    dframe = dframe.append(newdf, ignore_index=True, sort=False)
    
    return dframe

    


# Make sure the hour string is 0 padded.  Should probably change these to data types. 

# Todo- This, and the duration, will get more complex with the IB report format. The 
# html report uses a long timedate format


def zeroPadTimeStr(dframe, timeHeading) :
    '''Guarantee that the time format xx:xx:xx'''
    

    for i, row in dframe.iterrows():
        tm = row[timeHeading]
        tms=tm.split(":")
        if int(len(tms[0]) < 2) :
            if tms[0].startswith("0") == False :
                tm= "0" + tm
                dframe.at[i, timeHeading] = tm
    return dframe
                


# Todo. Doctor an input csv file to include fractional numer of shares for testing. Make 
# it more modular by checking for 'HOLD'. It might be useful in a windowed version with 
# menus to do things seperately.


def mkShortsNegative(dframe, side, qty) :
    ''' Fix the shares sold to be negative values. Currently assuming DAS values 'B', 'S', 'SS' for 'Side'. 
    '''
    for i, row in dframe.iterrows():
        if row[side] != 'B' and row[qty] > 0:
            dframe.at[i, qty] = ((dframe.at[i, qty]) * -1)
    return dframe


# def getListTickerDF(df) will take a dataframe that includes tickers in column 'Symb' and 
# returns a python list of DataFrames , 1 for each ticker.

def getListTickerDF(dframe, tickCol = 'Symb') :
    ldf_tick = list()
    for ticker in dframe[tickCol].unique() :
        ldf = dframe[dframe[tickCol] == ticker]
        ldf_tick.append(ldf)
    return ldf_tick

def getOvernightTrades(dframe, tickCol='Symb', qtyCol='Qty') :
    ''' getOvernightTrades(dframe) takes the DataFrame and returns a list of lists 
        (symb, qty) of trades that have overnight shares. '''
    
    ldf_tick = getListTickerDF(dframe, tickCol)
    overnightTrade = list()
    for ticker in ldf_tick :
        if ticker[qtyCol].sum() != 0 :
            overnightTrade.append([ticker[tickCol].unique()[0], ticker[qtyCol].sum(), 0, 0])
    return overnightTrade


# Note that this does not yet include those shares that are held before the days trading 
# began. Redo this to remake the list of data frames from the Symbols of Swing List then 
# make a list of data frams that  excludes those then merge them together

def askUser(st, question, ix, default) :
    while True :
        try :
            response = input(question)
            if len(response) < 1 :
                response = default
            else :
                response = int(response)
        except Exception as ex:
            print(ex)
            print("please enter a number")
            continue
       
        st[ix] = response
        return st

def figureOvernightTransactions() :
    swingTrade = getOvernightTrades(trades)
    for i in range(len(swingTrade)) :
        tryAgain =  True
        while tryAgain == True :

            xticker = 0      #Candy coaters
            xbalance = 1
            xbefore = 2
            xafter = 3
            print(swingTrade[i])
            print ("There is an unbalanced amount of shares of {0} in the amount of {1}".format(swingTrade[i][xticker], swingTrade[i][xbalance]))

            question = "How many shares of {0} are you holding now? (Enter for {1})".format(swingTrade[i][xticker], swingTrade[i][xbalance])
            swingTrade[i] = askUser(swingTrade[i], question, xafter, swingTrade[i][xbalance])

            if swingTrade[i][xafter] != swingTrade[i][xbalance]:

                difference = swingTrade[i][xbalance] - swingTrade[i][xafter]
                statement = "There is now a prior unbalanced amount of shares of {0} in the amount of {1}"
                print(statement.format(swingTrade[i][xticker], difference))
                question = "How many shares of {0} were you holding before?".format(swingTrade[i][xticker])
                swingTrade[i] = askUser(swingTrade[i], question, xbefore, difference)

            unaccounted = swingTrade[i][xbefore] + swingTrade[i][xafter] - swingTrade[i][xbalance]
            if unaccounted == 0 :
                print("That works.")
                tryAgain = False
            else :
                print()
                print("There are {1} unaccounted for shares in {0}".format(swingTrade[i][xticker], unaccounted))
                print()
                print("That does not add up. Starting over ...")
                print()
                print ("Prior to reset version ", i, swingTrade)
                swingTrade[i] = getOvernightTrades(trades)[i]
                print ("reset version ", i, swingTrade)
    return swingTrade

def insertOvernightRowold(dframe, swingTrade, time='Time', symbol='Symb', side='Side', price='Price', qty='Qty', acct="Account", PL='P / L') :
    newdf = createDf(trades, 0)
    for ldf in getListTickerDF(dframe) :
        found=False
        for ticker, balance, before, after in swingTrade:
            if ticker == ldf.Symb.unique()[0] :
#                 print ("Got {0} with the balance {1}". format (ticker, balance))
                found = True
                ldf = addRows(ldf, 1)
                for i, row in ldf.iterrows():

                    if i == len(ldf) -1 :
                        ldf.at[i, time] = '23:59:59'
                        ldf.at[i, symbol] = ticker
                        if balance > 0 :
                            ldf.at[i, side] = "HOLD+"
                        else :
                            ldf.at[i, side] = "HOLD-"
                        ldf.at[i, price] = 0
                        ldf.at[i, qty] = after
                        ldf.at[i, acct] = 'ZeroSubstance'
                        ldf.at[i, PL] = 0
        newdf = newdf.append(ldf, ignore_index = True)
    return newdf

def insertOvernightRow(dframe, st, time='Time', symbol='Symb', side='Side', price='Price', qty='Qty', acct="Account", PL='P / L') :
    newdf = createDf(trades, 0)
    
    for ldf in getListTickerDF(dframe) :
        found=False
        for ticker, balance, before, after in swingTrade:
            if ticker == ldf.Symb.unique()[0] :
                print ("Got {0} with the balance {1}, before {2} and after {3}". format (ticker, balance, before, after))
                if before != 0 :
                    newldf = createDf(trades, 1)
                    print("length:   ", len(newldf))
                    for i, row in newldf.iterrows():

                        if i == len(newldf) -1 :
                            print("Though this seems unnecessary it will make it more uniform ")
                            newldf.at[i, time] = '00:00:01'
                            newldf.at[i, symbol] = ticker
                            if before > 0 :
                                newldf.at[i, side] = "HOLD+"
                            else :
                                newldf.at[i, side] = "HOLD-"
                            newldf.at[i, price] = 0
                            newldf.at[i, qty] = before
                            newldf.at[i, acct] = 'ZeroSubstance'
                            newldf.at[i, PL] = 0
                            
                            ldf = newldf.append(ldf, ignore_index = True)
                        break #This should be unnecessary as newldf should always be the length of 1 here
                if after != 0 :
                    print("Are we good?")
                    ldf = addRows(ldf, 1)
        
                    for i, row in ldf.iterrows():

                        if i == len(ldf) -1 :
                            ldf.at[i, time] = '23:59:59'
                            ldf.at[i, symbol] = ticker
                            if balance > 0 :
                                ldf.at[i, side] = "HOLD+"
                            else :
                                ldf.at[i, side] = "HOLD-"
                            ldf.at[i, price] = 0
                            ldf.at[i, qty] = after
                            ldf.at[i, acct] = 'ZeroSubstance'
                            ldf.at[i, PL] = 0
        
        newdf = newdf.append(ldf, ignore_index = True, sort = False)
    return newdf

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
                return null
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

# In[ ]:


checkRequiredInputFields(trades)
trades = zeroPadTimeStr(trades, 'Time')
trades = trades.sort_values(['Symb', 'Time'])
trades = mkShortsNegative(trades, 'Side', 'Qty')
swingTrade = getOvernightTrades(trades)
swingTrade = figureOvernightTransactions()
listdf = insertOvernightRow(trades, swingTrade)
lbls = ['Tindex', 'Start', 'Time', 'Symb', 'Side', 'Price', 'Qty','Balance', 'Account', "P / L", 'Sum', 'Duration', 'Name']

for l in lbls :
    if l not in listdf.columns :
        listdf[l] = ''

# trades.columns
newTrades = listdf[lbls]
newTrades.copy()
nt = newTrades.sort_values(['Symb', 'Time'])
nt = writeShareBalance(nt)
nt = addStartTime(nt)
nt = nt.sort_values(['Start', 'Time'])
nt = addTradeIndex(nt)
nt = addTradePL(nt)
nt = addTradeDuration(nt)
nt = addTradeName(nt)
nt=addRows(nt,1)
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

dframe = addRows(dframe, 2)
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


# The Dataframe grabshere rely far too much on proper placement by this program. This is no 
# longer DataFrame like data. At this point, the trades will be encapsulated in objects.

# In[ ]:imageLocation = list()
newdf = createDf(dframe,  10)
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
    dframe = addRows(dframe, insertsize)
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
        img = openpyxl.drawing.image.Image(resizeName)
        cellname = 'E' + str(loc[0])
        ws.add_image(img, cellname)
        print(cellname)
            
            
    except IOError as e :
        print("An exception occured '%s'" % e)

for c in ws[10]:
    print(c.value)

wb.save('out/diditwork.xlsx')


# tdir='C:\\trader\\journal\\_08_August\\Week_4\\_0821_Tuesday\\'
# tdir = "out"
# outfile=tdir+ name
# nt.to_csv(outfile)

# nt.to_excel(outFile, index=False)


