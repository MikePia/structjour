'''
Created on Oct 18, 2018

@author: Mike Petersen
'''
import os
import sqlite3

from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo

# from inspiration.inspire import Inspire
from inspiration.inspire import Inspire
from journal.dfutil import DataFrameUtil
from journal.tradeutil import FinReqCol
from journal.xlimage import XLImage
from withstyle.tradestyle import c as tcell
from withstyle.tradestyle import style_range
from withstyle.thetradeobject import TheTradeObject, SumReqFields 



class LayoutSheet(object):
    '''
    Contains methods to layout the material on the excel page. Uses both pandas and openpyxl depending on
    how far in the program.  Generally the program progresses from pandas to openpyxl 
    '''


    def __init__(self, summarySize, topMargin, inputlen):
        '''
        Constructor
        :params:summarySize: The number of rows for each trade summary
        :params:frq: The FinReqCol object
        '''
        self.summarySize = summarySize
        self.topMargin = topMargin
        self.inputlen = inputlen
        
    def createImageLocation(self, df, ldf) :
        '''
        Debated what object to place this in. We are creating the shape of the excel document by adding rows
        to place the trade summaries and images, but we are doing it in a DataFrame and using  a list of 
        DataFrames, so it belongs here.
        Additionally creating the ImageLocation data structure to navigate the new space.
        '''
        #Add rows and append each trade, leaving space for an image. Create a list of names and row numbers 
        # to place images within the excel file (imageLocation data structure).
        
        frq = FinReqCol()
        newdf = DataFrameUtil.createDf(df,  self.topMargin)
    
        df = newdf.append(df, ignore_index = True)
        
        imageLocation = list()
        count=0
        for tdf in ldf :
            imageName='{0}_{1}_{2}_{3}.jpeg'.format (tdf[frq.tix].unique()[-1].replace(' ',''), 
               tdf[frq.name].unique()[-1].replace(' ','-'),
               tdf[frq.start].unique()[-1],
               tdf[frq.dur].unique()[-1])
            imageLocation.append([len(tdf) + len(df) + 3, 
                              tdf.Tindex.unique()[0].replace(' ', '') + '.jpeg',
                              imageName,
                              tdf.Start.unique()[-1],
                            tdf.Duration.unique()[-1]])
            print(count, imageName, len(imageLocation), len(tdf) + len(df) + 3)
            count = count + 1
            
            df = df.append(tdf, ignore_index = True)
            df = DataFrameUtil.addRows(df, self.summarySize)
        return imageLocation, df
 
    def createWorkbook(self, dframe) :
        nt = dframe
        # def 
        wb = Workbook()
        ws = wb.active
    
        for r in dataframe_to_rows(nt, index=False, header=False):
            ws.append(r)
    
        for name, cell  in zip(nt.columns, ws[self.topMargin]) :
            cell.value = name
        return wb, ws, nt
    
    
    def styleTop(self, ws, nt, tf) :
        ##Style the table, and the top paragraph.  Add and style the inspire quote. Create the SummaryMistake form (populate it below in a loop)
        tblRng= "{0}:{1}".format(tcell((1,self.topMargin)), tcell((len(nt.columns),self.topMargin + self.inputlen)))
        tab = Table(displayName="Table1", ref=tblRng)
        style = TableStyleInfo(name="TableStyleMedium1", showFirstColumn=False,
                               showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        tab.tableStyleInfo = style
    
        ws.add_table(tab)
        
        # A1:M5 inspire quote
        tf.mergeStuff(ws, (1,1), (13,5))
        ws["A1"].style = tf.styles["normStyle"]
        style_range(ws, "A1:M5", border=tf.styles["normStyle"].border)
        inspire = Inspire()
        ws["A1"] = inspire.getrandom().replace("\t", "        ")
        
        # A6:M24 introductory notes
        tf.mergeStuff(ws, (1,6), (13,24))
        ws["A6"].style = tf.styles["explain"]
        style_range(ws, "A6:M24", border=tf.styles["explain"].border)
        
        
        
        
        
        
        
        
    def createSummaries(self, imageLocation, ldf, jf, ws, tf) :
        tradeSummaries = list()
        XL = XLImage()
        srf = SumReqFields()
        
        response = input("Would you like to enter strategy names, targets and stops?     ")
        interview = True if response.lower().startswith('y') else False

        for loc, tdf in zip(imageLocation, ldf) :
            #     print('Copy an image into the clipboard for {0} beginning {1}, and lasting {2}'.format(loc[1], loc[2], loc[3]))
        
            
            img = XL.getAndResizeImage(loc[2], jf.outdir)
            
            #This is the location to place the chart on the page. Its kind of hidden in the deep recesses here.
            cellname = 'M' + str(loc[0])
            ws.add_image(img, cellname)
    
            #Put together the trade summary info for each trade and interview the trader
            tto=TheTradeObject(tdf, interview)
            tto.runSummary()
            tradeSummaries.append(tto.TheTrade)
    
            #Place the format shapes/styles in the worksheet
            tf.formatTrade(ws, anchor=(1, loc[0]))
    
            #populate the trade information
            for key in srf.tfcolumns.keys()  :
                cell = srf.tfcolumns[key][0]
                if isinstance(cell, list) :
                    cell = cell[0]
                tradeval = tto.TheTrade[key].unique()[0]
            #     print ("{0:10} \t{3} \t{1:}\t{2} ".format(key, cell, tradeval, tcell(cell, anchor=(1, loc[0]))))
    
    
                # Put some formulas in each trade Summary
                if key in srf.tfformulas :
    
                    anchor=(1,loc[0])
                    formula=srf.tfformulas[key][0]
                    args=[]
                    for c in srf.tfformulas[key][1:] :
                        args.append(tcell(c, anchor=anchor))
                    tradeval = formula.format(*args)
    
                if not tradeval :
                    continue
                ws[tcell(cell, anchor=(1, loc[0]))] = tradeval
                
        print("Done with interview")
        return tradeSummaries
            
    def createMistakeForm(self, tradeSummaries, mistake, ws, imageLocation) :
        '''
        Populate the mistake summaries form. Many entries are simple excel formulas found in 
        the dict mistake. Here we translate the cell addresses and populate the worksheet.
        :params:tradeSummaries: A dataframe containing the the trade summaries info, one line per trade.
        :parmas:mistake: A dataframe containing the info to populate the mistake summary.
        :params:ws: The openpyxl worksheet object.
        :imageLocation: A list containing the locations in the worksheet for each of the trades in tradeSummaries.
        '''
        
        # Populate the name fields
        for i in range(len(tradeSummaries)):
            key="name" + str(i+1)
            cell = mistake.mistakeFields[key][0][0]
            cell = tcell(cell, anchor=mistake.anchor)
            ts=tradeSummaries[i]
            s="{0} {1} {2}".format(i+1, ts.Name.unique()[0], ts.Account.unique()[0])
        #     print(s)
            ws[cell] = s
    
        # Populate the pl (loss) fields and the mistake fields. These are all simple formulas.   
        tokens=["pl", "mistake"]
        for token in tokens :
            for i in range(len(tradeSummaries)):
                key=token + str(i+1)
                if isinstance(mistake.mistakeFields[key][0], list) :
                    cell = mistake.mistakeFields[key][0][0]
                else :
                    cell = cell = mistake.mistakeFields[key][0]
                cell = tcell(cell, anchor=mistake.anchor)
            #     print(cell)
                formula = mistake.formulas[key][0]
                targetcell = mistake.formulas[key][1]
                targetcell = tcell(targetcell, anchor=(1, imageLocation[i][0]))
                formula = formula.format(targetcell)
    
                print("ws[{0}]='{1}'".format(cell,formula))
                ws[cell]=formula
                
    def save(self, wb, jf):
        #Write the file
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

                