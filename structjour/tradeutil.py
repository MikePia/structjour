'''
Created on Sep 5, 2018

@author: Mike Petersen
'''
import sys, datetime, os
from PIL import Image as PILImage
from PIL import ImageGrab
from openpyxl.drawing.image import Image
# from tkinter.tix import Balloon

class FinReqCol(object) :
    '''
    Some sugar to take the strings out of all the client code. The identifying strings are managed here. To get
    a list of columns use the dictionary frc (frc.values())).
    '''
    def __init__(self, source = 'DAS') :
        
        if source != 'DAS' :
            print("Only DAS is implemented")
            raise(ValueError)

        frcvals = ['Tindex', 'Start', 'Time', 'Symb', 'Side', 'Price', 'Qty','Balance', 'Account', "P / L", 'Sum', 'Duration', 'Name']
        frckeys = ['tix', 'start', 'time', 'ticker', 'side', 'price', 'shares', 'bal', 'acct', 'PL', 'sum', 'dur', 'name']
        frc = dict(zip(frckeys, frcvals))

        self.tix = frc['tix']
        self.start = frc['start']
        self.time = frc['time']
        self.ticker = frc['ticker']
        self.side = frc['side']
        self.price = frc['price']
        self.shares = frc['shares']
        self.bal = frc['bal']
        self.acct = frc['acct']
        self.PL = frc['PL']
        self.sum = frc['sum']
        self.dur = frc['dur']
        self.name = frc['name']
        
        #provided for methods that need a list of columns (using e.g. frc.values())
        self.frc = frc
        self.columns = list(frc.values())

    def hello(self):
        print('hello FinReqCol', self.tix)
        
class ReqCol(object):
    '''The required columns of the input data'''
    
    
        
    def __init__(self, source="DAS"):
        '''Set the required columns in the import file.'''
        
        if source != 'DAS' :
            print("Only DAS is currently supported")
            raise(ValueError)
        
        rckeys = ['time', 'ticker', 'side', 'price', 'shares', 'acct', 'PL']
        rcvals = ['Time', 'Symb', 'Side', 'Price', 'Qty', 'Account', 'P / L']
        rc  = dict(zip(rckeys, rcvals))

        self.time = rc['time']
        self.ticker = rc['ticker']
        self.side = rc['side']
        self.price = rc['price']
        self.shares = rc['shares']
        self.acct = rc['acct']
        self.PL = rc['PL']

        self.rc = rc
        self.columns = list(rc.values())

class XLImage(object):
    
    
    
    def adjustSizeByHeight(self, sz, newHeight=425, numCells=0, pixPerCell = 20.238095238095237) :
        ''' 
        Adjust size to keep the aspect ratio the same as determined by newHeight
        :param:sz: A tuple of ints in the form (width, height).
        :param:newHeight: The height in pixels of the image as place in the excel doc. The default number is
                            based on 21 unaltered excel cells on my machine.
        :param:numCells: An alternate way to determine the height based on how many excel rows for the height.
                            This value will override newHeight. The number of pixels is unscientifically determined 
                            (by me) to be about 20.24.
        :param:pixPerCell: The aproximate number of pixels per excel row.  Because this is determined by issues
                            beyond our control, it will have to be configurable in user settings     
        '''
        w,h = sz
        if numCells > 0:
            newHeight = numCells * pixPerCell
        newWidth = newHeight * w/h
        nw=int(newWidth)
        nh=int(newHeight)
        return(nw, nh)    
    
    
    def getPilImageFromClipboard(self, msg) :
        '''
        Use the PIL library to get an image from the clipboard. The ImageGrab.grabclibboard() works on
        Windows and MAC only. On failure to get an image, give the user 4 more tries or the user can opt out by
        entering 'q'.
        :param:msg: This is communication to the user of what to copy into the clipboard. It should be something
                    'Copy the chart for MU long at 9:35 for 2 minutes.
        :return:     The image in as a PIL object or None
        '''
        
        for i in range (5) :
            msg = "{0} {1}".format(msg, "Are you ready? (q to skip image) ")
            response = input(msg)
            if response.lower().startswith('y') : 
                im = ImageGrab.grabclipboard()
                if im is None :
                    print("Failed to get an image. Please select and copy an image (or press 'q')")
                else :
                    return im
            else :
                if response.lower().startswith('q') :
                    return None
        print("Moving on")
        return None
    
    
    
    
    def getAndResizeImage (self, name, outdir) :
        '''
        A script to run the image manipulation in structjour. Request a clipboard copy of an image. 
        Resze it to newSize height. Save it with a new name. Return the name. Hackiness lives until 
        I figure how to create a proper openpyxl Image object from a PIL Image object that doesn't 
        make the Workbook puke. (Saving the image is kind of a nice touch as long as the name has
        enough information to make the file useful ... like (Trade1_TWTR-Short_930-3min.jpeg)
        :param:name: An original name. We mark it up with _resize, save it, and return the new name.
        :param:outdir: The location to save the images.
        :return: The pathname of the image we save.
        '''
        
        try :
            if not os.path.exists(outdir) :
                os.mkdir(outdir)
            msg = '''
            Copy an image to the clipboard using snip for {0}
            '''.format(name)
            pilImage = self.getPilImageFromClipboard(msg) 
            newSize = self.adjustSizeByHeight(pilImage.size)
            pilImage = pilImage.resize(newSize, PILImage.ANTIALIAS)
            
            
            resizeName, ext = self.getResizeName(name, outdir)
            pilImage.save(resizeName, ext)
            img = Image(resizeName)
                
        except IOError as e :
            print("An exception occured '%s'" % e)
            if img :
                return img
            return None
    
    
        return img    
    
    
    
    def getResizeName(self, orig, outdir) :
        '''
        Munge up a pathfile name by inserting _resize onto the name. Do minimal checking that it has some extension.
        Using openpyxl and PIL, they may have more stringent requirements. PIL, for example, fails if you try to save with 
        the extension .jpg. But its perfectly happy with .jpeg
        :param:orig: The original pathfile name.
        :outdir:outdir: The location to save to.
        :return: A tuple(newFileName, extension)
        '''
        
        orig = orig.replace(":", "-")
        x=os.path.splitext(orig)
        if (len (x[1]) < 4 ) :
            print("please provide an image name with an image extension in its name. e.g 'png', jpg', etc")
        newName = x[0] + '_resize'
        if 'jpg' in x[1].lower() :
            newName += '.jpeg'
        else :
            newName += x[1]
        newName = os.path.join(os.path.normpath(outdir), newName)
        return (newName, os.path.splitext(newName)[1][1:])
      
class TradeUtil(object):
    '''
    TradeUtil moves the data from DataFrame to a formatted excel format object. It will compose a Trade class that will 
    encapsulate a trade including each transaction, and all the user input (target price, stop price, strategy, 
    explanation, extended notes and short notes. A data structure will be used to format this information in a way
    that makes review of the trade the prime concern using an openpyxl excel object.
    '''



    def __init__(self, source='DAS'):
        '''
        Constructor
        '''
        self._frc = FinReqCol(source)
                
            
    def writeShareBalance(self, dframe) :
        prevBal = 0
        c = self._frc
        
        for i, row in dframe.iterrows():
            qty = (dframe.at[i, c.shares])
            if row[c.side].startswith("HOLD") :
#                 print("got it at ", qty)
                qty = qty * -1
            newBalance = qty + prevBal
    
            dframe.at[i, c.bal] = newBalance 
            prevBal = newBalance    
        return dframe
    
    def addStartTime(self, dframe) :
        
        c = self._frc

        newTrade = True
        for i, row in dframe.iterrows():
            if newTrade :
                if row[c.side].startswith('HOLD') and i < len(dframe):
                    
                    oldTime = dframe.at[i+1, c.time]
    #                 print("     :Index: {0},  Side: {1}, Time{2}, setting {3}".format(i, row['Side'], row['Time'], oldTime))
                    dframe.at[i, c.start] = oldTime
    
                else :
                    oldTime = dframe.at[i, c.time]
                    dframe.at[i, c.start] = oldTime
                    
                    
                newTrade = False
            else :
    #             print("      Finally :Index: {0},  Side: {1}, Time{2}, setting {3}".format(i, row['Side'], row['Time'], oldTime))
                dframe.at[i, c.start] = oldTime
            if row[c.bal] == 0 :
                newTrade = True
        return dframe
   
    def addTradeIndex(self, dframe) :
        
        c = self._frc

        TCount = 1
        prevEndTrade = -1
    
        for i, row in dframe.iterrows():
            if len(row[c.ticker]) < 1 :
                break
            tradeIndex = "Trade " + str(TCount)
            if prevEndTrade == 0:
                TCount = TCount + 1
                prevEndTrade = -1
            tradeIndex = "Trade " + str(TCount)
            dframe.at[i,c.tix] = tradeIndex 
            if row[c.bal] == 0 :
                prevEndTrade = 0
        numTrades = TCount
        print(numTrades)        
        return dframe
    # This will blow up from wrong types if there is some kind of anomaly. The blank rows in 
    # Sum col are str and the filled rows are float. Don't fix it until it blows up. (or you 
    # need change this 'now' to production code for some reason) That way we have some case to fix.
    
    def addTradePL (self, dframe) :

        c = self._frc        

        tradeTotal = 0.0
        for i, row in dframe.iterrows():
            if row[c.bal] != 0 :
                tradeTotal = tradeTotal + row[c.PL]
            else :
                sumtotal = tradeTotal + row[c.PL]
                dframe.at[i, c.sum] = sumtotal
                tradeTotal = 0
        return dframe
    
    def addTradeDuration(self, dframe) :
        
        c = self._frc

        for i, row in dframe.iterrows():
            if row[c.bal] == 0 :
                timeEnd = row[c.time]
                timeStart = row[c.start]
                end=timeEnd.split(":")
                start=timeStart.split(":")
                diff = datetime.datetime(1,1,1,int(end[0]), int(end[1]), int(end[2])) - datetime.datetime(1,1,1,int(start[0]), int(start[1]), int(start[2]))
                dframe.at[i, c.dur] = diff
        return dframe
    
    
    # In[ ]:
    
        
    
    def addTradeName(self, dframe) :
        
        c= self._frc
        
        for i, row in dframe.iterrows():
            longShort = " Long"
            if row[c.bal] == 0 :
                if row[c.side] == 'B' :
                    longShort = " Short"
                dframe.at[i, c.name] = row[c.ticker] + longShort
        return dframe
    
    # Note that .sum() should work on this but it failed when I tried it.
    def addSummaryPL(self, dframe) :
        
        c = self._frc
        
        count=0
        tot=0.0
        tot2 = 0.0
        for i, row in dframe.iterrows():
            count=count+1
            if count < len(dframe) :
                tot=tot+row[c.PL]
                if row[c.bal] == 0 :
     
                    tot2 = tot2 + row[c.sum]
                if count == len(dframe) -1 :
                    lastCol = row[c.PL]
    
                    print("Last col?", row[c.PL])
       
            else :
                dframe.at[i, c.PL] = tot
                dframe.at[i, c.sum] = tot2
    
        if lastCol > 0:
    
            print('''
            Some shares are unaccounted for. Please send the original csv file to the developer in 
            order to fix ths issue in the software. Please remove the account number  or change its value
            to anything else.
            ''')
        return dframe
    
   
    # dframe contains the transactions of a single trade.  Single trade ends when the balance 
    # of shares is 0
    # Return value is a string 'Long' or 'Short'
    def getLongOrShort(self, dframe) :
        tsx = dframe[dframe.Balance == 0]
    
        
        if len(tsx) != 1 :
            return None
        if str(tsx.Side) == 'B' or str(tsx.Side) == 'Hold-':
            return 'Short'    
        else :
            return 'Long'

   
    def getTradeList (self, dframe) :
        '''
        Creates a python list of DataFrames for each trade. It relies on addTradeIndex successfully creating the 
        trade index in the format Trade 1, Trade 2 etc.
        :param:dframe: A dataframe with the column Tindex filled in.
        '''
        # Now  we are going to add each trade and insert space to put in pictures with circles and 
        #arrows and paragraph on the back of each one to be used as evidence against you in a court 
        # of law (or court of bb opionion)
#         insertsize=25
    #     dframe = nt
        c = self._frc   
        try :
            if not dframe[c.tix].unique()[0].startswith('Trade') :
                raise(NameError("Cannot make a trade list. You must first create the TIndex column using addTradeIndex()."))
        except NameError as ex :
            print(ex, 'Bye!')
            sys.exit(-1)

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
        print("Got {0} trades".format(len(ldf)))
        return ldf
    
        
    def addFinReqCol (self, dframe) :
        c = self._frc  
        for l in c.columns :
            if l not in dframe.columns :
                dframe[l] = ''
        return dframe
    
   
        
        
