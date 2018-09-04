'''
Created on Aug 30, 2018

@author: Mike Petersen
'''
import unittest
import datetime
import os
from journalfiles import JournalFiles
from structjour.pandasutil import DataFrameUtil

def itsTheWeekend() :
    '''
    This is a hacky thing to take care of (most) non trading days aka Saturday and Sunday and solely for my development environment.
    (if its a holiday you shouldn't be working anyway so it serves you right)
    :Return: The date of the last weekday to have occurred. AKA Friday if today is a weekend day. Otherwise returns today
    '''
    d = datetime.date.today()
    idow = int (d.strftime("%w"))
    subtract =  1 if idow == 6 else 2 if idow == 0 else 0
    td = datetime.timedelta(subtract)
    newdate = d -td  
    return newdate
# itsTheWeekend().strftime("%A, %B %d, %y")

class TestJF(unittest.TestCase):
    
    def test_DefaultCreate(self):
        '''
        The succes of the default case relies on running it from the right directory
        '''
        cwd = os.getcwd()
        os.chdir("..")
        print("cwd:", os.getcwd())
        jf = JournalFiles()
        jf._printValues()
        #Go back to the original location for all the other tests
        os.chdir(cwd)

        self.assertRaises(ValueError)
            
            
    def test_IndirCreate(self):
        f = "TradesExcelEdited.csv"
        jf = JournalFiles(indir = r"..\data", infile=f)
    
        self.assertEqual(os.path.realpath(os.path.join(r'..\data', f)), os.path.realpath(jf.inpathfile), "Structjour failed to correctly set the input file")
        
        
    def testDevelDefaultCreate(self):
        '''Tests the default creation if its Monday to Friday.  Tests the previus Friday's date using param theDate otherwise'''
        
        
        # !!!!!! Change the holiday code back to normal
        if datetime.date.today() == itsTheWeekend() :
#             jf=JournalFiles(mydevel=True)
            jf=JournalFiles(theDate = datetime.date(2018,8,31), mydevel=True)
        else :
            jf = JournalFiles(theDate=itsTheWeekend(), mydevel=True)
        
        
        
        self.assertTrue(os.path.exists(jf.indir), "Have you reset the code the tnormal non-holiday code?")
        self.assertIsInstance(jf.theDate, datetime.date , "Failed to instantiate a the date object")
        #If no exceptions were created we passed
        self.assertIsInstance(jf, JournalFiles, "Failed to create instance of journalFile")
        
    def testDevelOutdirCreate(self):
        ''' 
        Tests the default creation of my development environment on a day that I created a trades file.  It should work Monday 
        thru Friday except on Holidays after the market closes and I have exported the trades window from DAS. The helper method
        itsTheWeekend will help allevaiate some days' failures.
        '''
        dout = r"..\out"
        din = r"..\data"
        
        if datetime.date.today() == itsTheWeekend() :
            jf=JournalFiles(indir = din, outdir=dout, mydevel=True)
        else :
            jf=JournalFiles(theDate=itsTheWeekend(),indir = din, outdir=dout, mydevel=True)
            
        self.assertEqual( os.path.realpath (r'..\out'), os.path.realpath(jf.outdir), "Structjour failed to correctly set the output directory")
        self.assertTrue(os.path.exists(jf.indir))
        self.assertIsInstance(jf.theDate, datetime.date , "Failed to instantiate a the date object")
        #If no exceptions were created we passed
        self.assertIsInstance(jf, JournalFiles, "Failed to create instance of journalFile")
        
        
    def testDevelIndirCreate(self):
        ''' 
        Tests the default creation of my development environment on a day that I created a trades file.  It should work normally 
        Monday and with a hack 'itsTheWeekend for Saturday and Sunday. Tests the explicit indir parameter
        '''
        din = r"..\data"
        
        if datetime.date.today() == itsTheWeekend() :
            jf=JournalFiles(indir=din, mydevel=True)
        else :
            jf=JournalFiles(theDate=itsTheWeekend(),indir=din, mydevel=True)
            
        self.assertEqual( os.path.realpath (din), 
                          os.path.realpath(jf.indir), 
                          "Structjour failed to correctly set the input directory")
        self.assertTrue(os.path.exists(jf.indir))
        self.assertIsInstance(jf.theDate, datetime.date , "Failed to instantiate a the date object")
        #If no exceptions were created we passed
        self.assertIsInstance(jf, JournalFiles, "Failed to create instance of journalFile")
        
        
        
        
        
    def testDevelIndirOutdirCreate(self):
        ''' 
        Tests the default creation of my development environment on a day that I created a trades file.  It should work normally 
        Monday and with a hack 'itsTheWeekend for Saturday and Sunday. Tests the explicit indir parameter
        '''
        dout = r"..\out"
        din = r"..\data"
        fin = 'TradesWithBothHolds.csv'
        
        jf = JournalFiles(indir=din, infile=fin, outdir = dout, mydevel=True)
        jf._printValues()
            
        self.assertEqual( os.path.realpath (r'..\out'), 
                          os.path.realpath(jf.outdir), 
                          "Structjour failed to correctly set the output directory")
        self.assertTrue(os.path.exists(jf.indir))
        self.assertIsInstance(jf.theDate, datetime.date , "Failed to instantiate a the date object")
        #If no exceptions were created we passed
        self.assertIsInstance(jf, JournalFiles, "Failed to create instance of journalFile")    
        
    def testDevelInfileFail(self):
        ''' 
        Tests the default creation of my development environment on a day that I created a trades file.  It should work normally 
        Monday and with a hack 'itsTheWeekend for Saturday and Sunday. Tests the explicit indir parameter
        '''
        dout = r"..\out"
        din = r"..\data"
        fin = 'SchmorgalStein.csv'
        
#         with self.assertRaises(NameError) :
        try :
            JournalFiles(indir=din, infile=fin, outdir = dout, mydevel=True)
        except NameError as ex:
            pass
        except Exception as ex:
            self.fail("Unexpected exception ", ex)
            
        else :
            self.fail("Failed to throw expected exception")       

    def testDevelInDirFail(self):
        ''' 
        Tests the default creation of my development environment on a day that I created a trades file.  It should work normally 
        Monday and with a hack 'itsTheWeekend for Saturday and Sunday. Tests the explicit indir parameter
        '''
        din = r"..\monkeysPaw"
   
        
#         with self.assertRaises(NameError) :
        try :
            JournalFiles(indir=din,  mydevel=True)
        except NameError :
            pass
        except Exception :
            self.fail("Unexpected exception from testDevelInDirFail")
            
        else :
            self.fail("Failed to throw expected exception")       

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
    
    