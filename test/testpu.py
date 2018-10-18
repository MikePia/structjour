'''
Created on Sep 9, 2018

@author: Mike Petersen
'''
import unittest
import os
from structjour.pandasutil import DataFrameUtil, InputDataFrame, ToCSV_Ticket as Ticket
import pandas as pd
from structjour.tradeutil import ReqCol, FinReqCol  #, TradeUtil
# from structjour.xlimage import XLImage
from journalfiles import JournalFiles


class Test(unittest.TestCase):
    
    
    def testGetListOfTicketDF(self):
        rc = ReqCol()
        
        jf = JournalFiles(indir = '../data', infile='trades.910.tickets.csv', outdir = '../out/', mydevel = True)
        
#         idf = InputDataFrame()
        tkt = Ticket(jf)
#         tkt.setup()
        tktList = tkt.getListOfTicketDF()
        
        totalTX = 0
        for ticket in tktList :
            self.assertEqual(len(ticket[rc.side].unique()), 1, "There can only be one side, long or short, in a ticket")
            self.assertEqual(len(ticket[rc.ticker].unique()), 1,"There can only be one ticker in a ticket")
            self.assertEqual(len(ticket['Cloid'].unique()), 1, "There can be only one Cloid in a ticket")
            self.assertEqual(len(ticket[rc.acct].unique()),  1, "There can be only one account in a ticket")

            totalTX = totalTX + len(ticket)

        trades = pd.read_csv(jf.inpathfile)
        msg = "There is a discrepancy in number of transactions between the original and the tickets"
        self.assertEqual(len(trades), totalTX, msg)
        
    def testCreateSingleTicket(self):
        rc = ReqCol()
        jf=JournalFiles(indir=r"../data", infile = "trades.910.tickets.csv", outdir= r"../out")
        tkt = Ticket(jf)

        listTick = tkt.getListOfTicketDF()
        totalSharesForDay = 0
        for tick in listTick :
                
            singleTicket = tkt.createSingleTicket(tick)
            self.assertIsInstance(singleTicket, type(pd.DataFrame()), "Failed to create a DataFrame")
            self.assertEqual(len(singleTicket), 1, "Failed to create a single item ticket")
            self.assertLessEqual(singleTicket[rc.price].unique()[0], tick[rc.price].max())
            self.assertGreaterEqual(singleTicket[rc.price].unique()[0], tick[rc.price].min())
            
            totalSharesForDay = totalSharesForDay + tick[rc.shares].sum()

        dframe = pd.read_csv(jf.inpathfile)
        self.assertEquals(dframe[rc.shares].sum(), totalSharesForDay, "Failed to acount for all the shares transacted in the day")

    def testNewSingleTxPerTicket(self):
        rc = ReqCol()
        jf=JournalFiles(indir=r"../data", infile = "trades.910.tickets.csv", outdir= r"../out")
        origdframe = pd.read_csv(jf.inpathfile)
        originfile=jf.infile
        tkt = Ticket(jf)

#         listTick = tkt.getListOfTicketDF()
        newDF, jf = tkt.newDFSingleTxPerTicket()
        
        self.assertNotEqual(originfile, jf.infile)
        newdframe = pd.read_csv(jf.inpathfile)
        print ("Original len: {0}: Original sum: {1}.".format(len(origdframe),origdframe[rc.PL].sum()))
        print ("The new  len: {0}: The new sum:  {1}.".format(len(newdframe),newdframe[rc.PL].sum()))
        print ("The new  len: {0}: The new sum:  {1}.".format(len(newDF),newDF[rc.PL].sum()))
        self.assertAlmostEqual(origdframe[rc.PL].sum(), newdframe[rc.PL].sum(),places=10)
        self.assertAlmostEqual(newDF[rc.PL].sum(), newdframe[rc.PL].sum(),places=10)


    def testCheckRequiredColumnsThrow(self):
        vals=[[1,2,3,4,5,6,7,8,9,10],['a','b','c','d','e','f','g','h','i','j']]
        apd=pd.DataFrame(vals)
        apd.columns=[['Its', 'the', 'end', 'of', 'the', 'world', 'as', 'we', 'know','it']]
        columns=['Its', 'the', 'end', 'of', 'the', 'world', 'as', 'we', 'know','it','sofuckit']
#         DataFrameUtil.checkRequiredInputFields(apd, columns)

        try :
            DataFrameUtil.checkRequiredInputFields(apd, columns)
 
        except ValueError:
            pass
        except Exception as ex:
            msg = "{0}{1}".format("Unexpected exception. ", ex)
            self.fail(msg)
             
        else :
            self.fail("Failed to throw expected exception")     
            
        vals=[[1,2,3,4,5,6,7,8,9],['a','b','c','d','e','f','g','h','i']]
        apd=pd.DataFrame(vals, columns=['Its', 'the', 'end', 'of', 'world', 'as', 'we', 'know','it'])
        
        try :
            DataFrameUtil.checkRequiredInputFields(apd, columns)
        except ValueError :
            self.assertTrue(True)
            return
        self.assertFalse(False, "Should have thrown exception")
        

    def testCheckrequiredColumnsWithReqColFail(self):
        
        reqCol = ReqCol()
        finReqCol = FinReqCol()
        fail=pd.DataFrame(columns=['Time', 'Symb', 'Side', 'Price', 'Qty', 'Account'])
        rc=pd.DataFrame(columns=reqCol.columns)
        
        try :
            DataFrameUtil.checkRequiredInputFields(fail, reqCol.columns)
        except ValueError as ex:
            print(ex)
            self.assertTrue(True, ex)
        
        try :
            DataFrameUtil.checkRequiredInputFields(rc, finReqCol.columns)
        except ValueError as ex:
            self.assertTrue(True)
            
    def testCheckReqColumnsWithReqColSuccess(self):
        reqCol = ReqCol()
        finReqCol = FinReqCol()
        
        frc=pd.DataFrame(columns=finReqCol.columns)
        
        t1=False
        t2=False
        try :
            t1=DataFrameUtil.checkRequiredInputFields(frc, finReqCol.columns)
            t2=DataFrameUtil.checkRequiredInputFields(frc, reqCol.columns)
         
        except ValueError as ex:
            print(ex)
        self.assertTrue(t1)
        self.assertTrue(t2)         
        
    def testZeroPad(self) :
        '''
        Both this method and the tested method are extremely dependent on extra outside circumstances. For example
        This method depends on the transactions to begin between 9 and 10 as recorded by DAS. (A purchase at 8 will 
        cause this test to fail) Right now I have only one case to test ('data/TradesExcelEdited.csv')so wtf, leave 
        it till I have a test case.
        '''
        infile=r"../data/trades.8.ExcelEdited.csv"
        if not os.path.exists(infile) :
            err="Test is improperly setup. {0}".format(infile)
            self.assertTrue(False, err)
            return
        t = pd.read_csv(infile)
        numof0s = len(t['Time'][t['Time'].str.startswith('0')])
        numof9s = len(t['Time'][t['Time'].str.startswith('9')])
        self.assertTrue(numof0s == 0)
        self.assertGreater(numof9s, 0)
        
        
        idf = InputDataFrame()
        t = idf.zeroPadTimeStr(t)
        
        numof0s = len(t['Time'][t['Time'].str.startswith('0')])
        
        self.assertEquals(numof9s, numof0s)
        
        
    def testMkShortNegative (self) :
        rc=ReqCol()
        side=['B', 'S', 'S', 'SS', 'B', 'B']
        mult=[1, -1, -1, -1, 1, 1]
        shares=[100,200,300,400,500,600]
        testSet=list(zip(side,shares))

        
        apd=pd.DataFrame(testSet, columns=[rc.side, rc.shares])
        
        for i in range (6):
            self.assertEqual(apd[rc.shares][i], shares[i])
            
        idf = InputDataFrame()
        apd = idf.mkShortsNegative(apd)
        for i in range(6) :
            self.assertEqual ( apd[rc.shares][i], shares[i] * mult[i])

    def testGetListTickerDF(self) :
    
        rc = ReqCol()

        tickers=[ 'MU', 'MU', 'MU', 
                 'TWTR', 'TWTR', 'TWTR', 'TWTR', 'TWTR', 'TWTR', 
                 'AAPL', 'AAPL', 'AAPL', 'AAPL', 'AAPL', 'AAPL', 'AAPL',
                 'MU', 'MU', 'MU' ]
        U1="U12345"
        U2="TR12345"
        accounts= [ U1, U1, U1, 
                   U1, U1, U1, U2, U2, U2, 
                   U2, U1, U2, U2, U1, U1, U1, 
                   U2, U2, U2 ]

        testSet=list(zip(tickers,accounts))
    
        apd = pd.DataFrame(testSet, columns=[rc.ticker, rc.acct])
        apd
    
        ipd=InputDataFrame()
        listDf=ipd.getListTickerDF(apd)
        
        #A dataframe for each ticker in both accounts 
        self.assertEquals(len(listDf), 6)
        for df in listDf :
            self.assertEquals(len(df[rc.ticker].unique()), 1)
            self.assertEqual (len(df[rc.acct].unique()), 1)
            
    def testGetOvernightTrades(self):
        '''
        Check this with real data that is checked by hand. Add to the list whenever there is a new input file with overnight trades.
        '''
    
        indir=r"../data"
        infile = "trades.8.WithBothHolds.csv"
        infile2="trades.907.WithChangingHolds.csv"
#         infile3="TradesWithHolds.csv"          #skipping-- edited by Excel
    
        data = [
            (infile, [('MU','paper',750),('TSLA','paper',50)]),
            (infile2, [('AMD','paper',600),('FIVE','real',241),('MU','real',50)]),
            ]

        for infile, tradeList in data:
            inpathfile = os.path.normpath(os.path.join(indir, infile))
            if not os.path.exists(inpathfile) : 
                err="Test is improperly setup. {0}".format(infile)
                self.assertTrue(False, err)
                return
                
            dframe = pd.read_csv(inpathfile)
            idf = InputDataFrame()
            dframe = idf.mkShortsNegative(dframe)
        
    
            st = idf.getOvernightTrades(dframe)
#             found = list()
            for t in st :
                l = (t['ticker'], 'real' if t['acct'].startswith("U") else 'paper', t['shares'])
#                 if l in tradeList :
                err = "Failed to find {0} in {1}".format(l, infile)
                self.assertIn(l, tradeList, err)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCheckRequiredColumns']
    unittest.main()