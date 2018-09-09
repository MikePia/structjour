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

    #Redundant
    def test_whichWeekFromWeekend(self):
        '''Testing beginning day on the weekend using Sept of 2018 9/1 thru 9/16'''
        jf = JournalFiles(indir="../data", mydevel=True)
        jf._printValues()
        for i in range(1,10) :
            x = jf._whichWeek(9,i)
            self.assertEqual(1,x,"whichWeek is wrong! for September {0}".format(i))
        for i in range(10,17) :
            x = jf._whichWeek(9,i)
            self.assertEqual(2,x,"whichWeek is wrong! for September {0}".format(i))

        for i in range(17,24) :
            x = jf._whichWeek(9,i)
            self.assertEqual(3,x,"whichWeek is wrong! for September {0}".format(i))
    #Redundant
    def test_whichWeekFromMonday(self):
        '''Testing beginning day on the weekend using Oct 2018'''
        jf = JournalFiles(indir="../data", mydevel=True)
        jf._printValues()
        for i in range(1,8) :
            x = jf._whichWeek(10,i)
            self.assertEqual(1,x,"whichWeek is wrong! for October {0}".format(i))
        for i in range(8,15) :
            x = jf._whichWeek(10,i)
            self.assertEqual(2,x,"whichWeek is wrong! for September {0}".format(i))

        for i in range(15,22) :
            x = jf._whichWeek(10,i)
            self.assertEqual(3,x,"whichWeek is wrong! for September {0}".format(i))

    #Redundant
    def test_whichWeekFromThursday(self):
        '''Testing beginning day on the Thursday using Nov 2018'''
        jf = JournalFiles(indir="../data", mydevel=True)
        jf._printValues()
        for i in range(1,5) :
            x = jf._whichWeek(11,i)
            self.assertEqual(1,x,"whichWeek is wrong! for October {0}".format(i))
        for i in range(5,12) :
            x = jf._whichWeek(11,i)
            self.assertEqual(2,x,"whichWeek is wrong! for September {0}".format(i))

        for i in range(12,19) :
            x = jf._whichWeek(11,i)
            self.assertEqual(3,x,"whichWeek is wrong! for September {0}".format(i))            
            
    def test_whichWeek(self) :
        '''Testing beginning day on the Thursday using Nov 2018'''
        #TODO check isocalendar for a less convoluted version of this method
        #But right now, I think, ... finally ... its bullet proof ... i hope (but hacky with those string comparisons)
        jf = JournalFiles(indir="../data", mydevel=True)
        
        dj1 = datetime.date(2018,1,1)
        dj1ord = dj1.toordinal()
        week = 0
        oldMonth = 'January'
        for dord in range(dj1ord, dj1ord+365) :
            cdate = datetime.date.fromordinal(dord)
            dow = cdate.strftime('%A')+ ','
            mon = cdate.strftime('%B')
            day = cdate.strftime('%d')+ ','
    
            if dow.startswith("Monday") and not day.startswith('02') and not day.startswith('03'):
                week = week + 1
            if oldMonth != mon :
                week = 1
            if not dow.startswith('Saturday') and not dow.startswith('Sunday') :
                if day.startswith('01') or dow.startswith('Monday') or dow.startswith('Friday') :
                    jfweek = jf._whichWeek(cdate.month, cdate.day)
                    self.assertEqual(jfweek, week)
#                     print("{0:10}{1:10}{2:4}week {3:4} == {4}".format(dow, mon, day,week, jfweek))
            oldMonth = mon
#             if dow == "Sunday," :
#                 print()
        









