'''
Created on Nov 5, 2018

@author: Mike Petersen
'''
import unittest
from journalfiles import JournalFiles
from journal.pandasutil import InputDataFrame, ToCSV_Ticket as Ticket
from journal.tradeutil import TradeUtil
from journal.thetradeobject import TheTradeObject,  SumReqFields




    # Global   
grf = SumReqFields()
class Test(unittest.TestCase):


    def testSumReqFields(self):
        '''
        This class is just data. The only thing that can go wrong is to let it get 
        out of sync which is very difficult to auto test. The real test is to visually 
        verify the output above.  
        '''
        srf = SumReqFields()
        for k in srf.rc.keys():
            value=srf.rc[k]
            address=srf.tfcolumns[value][0]
            

            print ("{0:12} {1:10} {2}  ".format(k, value, address))
        print(self.testSumReqFields.__doc__)
        self.assertEqual(len(srf.columns), len(srf.rc.keys()), "This cannot fail! FLW")
#         print(srf.getStyles())
        self.assertIn("normStyle", srf.getStyles())
        self.assertIn("explain", srf.getStyles())
        self.assertIn("normalNumberTopRight", srf.getStyles())
        self.assertIn("normalSubLeft", srf.getStyles())
     
    def setupForTheTradeObject(self):
        jf=JournalFiles(mydevel=True,infile="trades.8.csv", indir="../data/", outdir="../out/")
        
        tkt = Ticket(jf)
        trades, jf =tkt.newDFSingleTxPerTicket()
        
        idf = InputDataFrame()
        trades = idf.processInputFile(trades)
        
        tu = TradeUtil()
        (dummy_len, dummy_df, ldf) = tu.processOutputDframe(trades)

        tto=TheTradeObject(ldf[1], True)
        return tto
        
    def testTheTradeObjectSetName(self):
        
        tto=self.setupForTheTradeObject()
        
        tto._TheTradeObject__setName()
        tto._TheTradeObject__setName()
        self.assertEqual(tto.TheTrade[grf.name].unique()[0], "SQ Long", "Failed to set the name correctly")
        
    def testTheTradeObjectSetAcct(self):
        tto=self.setupForTheTradeObject()
        tto._TheTradeObject__setAcct()
        self.assertEqual(tto.TheTrade[grf.acct].unique()[0], "SIM", "Failed to set the account correctly")
    
    def testTheTradeObjectSetSum(self):
        tto=self.setupForTheTradeObject()
        tto._TheTradeObject__setSum()
        self.assertEqual(tto.TheTrade[grf.pl].unique()[0], -16.5, "Failed to set p/l correctly")
        
    def testTheTradeObjectSetStart(self):
        tto=self.setupForTheTradeObject()
        tto._TheTradeObject__setStart()
        self.assertEqual(tto.TheTrade[grf.start].unique()[0], "09:37:05", "Failed to set start time correctly")
        
    def testTheTradeObjectSetDur(self):
        tto=self.setupForTheTradeObject()
        tto._TheTradeObject__setDur()
        self.assertEqual(tto.TheTrade[grf.dur].unique()[0], "0 hours 1:40", "Failed to set duration time correctly")
        
    def testTheTradeObjectSetStrategy(self):
        '''Skipping because I don't do mock...(yet) The mechanics are the same for all of theses anyway'''
        
    def testTheTradeObjectSetShares(self):
        tto=self.setupForTheTradeObject()
        tto._TheTradeObject__setShares()
        self.assertEqual(tto.TheTrade[grf.shares].unique()[0], "300 shares", "Failed to set position correctly")
        shares=tto.getShares()
        self.assertEqual(shares, 300, "Failed to set position correctly")
        
    def testTheTradeObjectSetMarketValue(self):
        tto=self.setupForTheTradeObject()
        tto._TheTradeObject__setMarketValue()
        self.assertEqual(tto.TheTrade[grf.mktval].unique()[0], 22398, "Failed to set position correctly")
        
    def testTheTradeObjectSetHeaders(self):
        tto=self.setupForTheTradeObject()
        tto._TheTradeObject__setHeaders()

        self.assertEqual(tto.TheTrade[grf.plhead].unique()[0],  "P/L"              , "Failed to set head correctly") 
        self.assertEqual(tto.TheTrade[grf.starthead].unique()[0],  "Start"            , "Failed to set head correctly") 
        self.assertEqual(tto.TheTrade[grf.durhead] .unique()[0],  "Dur"              , "Failed to set head correctly") 
        self.assertEqual(tto.TheTrade[grf.sharehead].unique()[0],  "Pos"              , "Failed to set head correctly") 
        self.assertEqual(tto.TheTrade[grf.mkthead] .unique()[0],  "Mkt"              , "Failed to set head correctly") 
        self.assertEqual(tto.TheTrade[grf.entryhead].unique()[0],  'Entries and Exits', "Failed to set head correctly") 
        self.assertEqual(tto.TheTrade[grf.targhead].unique()[0],  'Target'           , "Failed to set head correctly") 
        self.assertEqual(tto.TheTrade[grf.stophead].unique()[0],  'Stop'             , "Failed to set head correctly") 
        self.assertEqual(tto.TheTrade[grf.rrhead].unique()[0],  'R:R'              , "Failed to set head correctly") 
        self.assertEqual(tto.TheTrade[grf.maxhead].unique()[0],  'Max Loss'         , "Failed to set head correctly") 
        self.assertEqual(tto.TheTrade[grf.mstkhead].unique()[0],  "Proceeds Lost"    , "Failed to set head correctly") 
        
 
    def testTheTradeObjectSetEntries(self):
        tto=self.setupForTheTradeObject()
        tto._TheTradeObject__setEntries()
        tto.TheTrade[['Entry1', 'Exit2', 'Exit3', 'PL2', 'PL3', 'PL4']]
        self.assertEqual(tto.TheTrade[grf.entry1].unique()[0], 74.66, "Failed to set entry correctly")
        self.assertEqual(tto.TheTrade[grf.exit2].unique()[0], 74.77, "Failed to set exit correctly")
        self.assertEqual(tto.TheTrade[grf.exit3].unique()[0], 74.55, "Failed to set exit correctly")
        self.assertEqual(tto.TheTrade[grf.pl2].unique()[0], 8.25, "Failed to set pl correctly")
        self.assertEqual(tto.TheTrade[grf.pl3].unique()[0], -24.75, "Failed to set pl correctly")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()