'''
Created on Aug 30, 2018

@author: Mike Petersen
'''
import unittest
from CSV.pandas.TradeReview.JournalFiles import JournalFiles

class TestJF(unittest.TestCase):
    
    def testCreate(self):
        jf = JournalFiles(mydevel = True)
        
        #If no exceptions were created we passed
        self.assertIsInstance(jf, JournalFiles, "Failed to create instance of journalFile")
        
        
    
    
    