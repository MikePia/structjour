# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

'''
Test the methods in the module strategies

Created on Mar 30, 2019

@author: Mike Petersen
'''

import os
import sqlite3
from unittest import TestCase
import unittest
from structjour.strategy.strategies import Strategy

class TestStrategy(TestCase):
    '''
    Test Strategy object
    '''

    def __init__(self, *args, **kwargs):
        super(TestStrategy, self).__init__(*args, **kwargs)

        self.somestrats = ['ABCD', 'Bull Flag', 'Fallen Angel', 'VWAP Support', 'VWAP Reversal']
        self.strat = Strategy(create=True, testdb='C:/python/E/structjour/test/testdb.sqlite')

    def setUp(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def test_removeLink(self):
        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()
        addme = 'CUT LOSERS'
        strat.addStrategy(addme)

        link = 'http:/the/strategy/w/site.html'
        link2 = 'http:/the/strategy/x/site.html'
        link3 = 'http:/the/strategy/y/site.html'
        link4 = 'http:/the/strategy/z/site.html'
        
        links = [link, link2, link3, link4]
        for l in links:
            strat.setLink(addme, l)
        for l in links:
            strat.removeLink(addme, l)
        x = strat.getLinks(addme)
        self.assertTrue(not x)

    def test_setLink(self):
        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()
        addme = 'CUT LOSERS'
        strat.addStrategy(addme)

        link = 'http:/the/strategy/w/site.html'
        link2 = 'http:/the/strategy/x/site.html'
        link3 = 'http:/the/strategy/y/site.html'
        link4 = 'http:/the/strategy/z/site.html'
        
        links = [link, link2, link3, link4]
        for l in links:
            strat.setLink(addme, l)

        dblinks = strat.getLinks(addme)

        for l in links:
            self.assertIn(l, dblinks)

    def test_removeImage(self):
        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()
        addme = 'WINNERS RUN'
        strat.addStrategy(addme)

        imagename = 'C:/the/end/of/all/time.png'
        strat.setImage1(addme, imagename)
        im = strat.getImage1(addme)
        self.assertEqual(imagename, im)

        imagename2 = 'C:/and/its/waypast/due.png'
        strat.setImage2(addme, imagename2)
        im = strat.getImage2(addme)
        self.assertEqual(imagename2, im)

        strat.removeImage1(addme)
        im = strat.getImage1(addme)
        self.assertTrue(not im)

        strat.removeImage2(addme)
        im = strat.getImage2(addme)
        self.assertTrue(not im)



    def test_setImage1(self):

        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()
        addme = 'BUY LOWER'
        strat.addStrategy(addme)

        imagename = 'C:/the/end/of/all/time.png'
        strat.setImage1(addme, imagename)
        im = strat.getImage1(addme)
        self.assertEqual(imagename, im)



        imagename = 'C:/the/beginning/of/no/time.png'
        strat.setImage1(addme, imagename)
        im = strat.getImage1(addme)
        self.assertEqual(imagename, im)

        imagename = 'C:/and/all/the/rest.png'
        strat.setImage2(addme, imagename)
        im = strat.getImage2(addme)
        self.assertEqual(imagename, im)
        

    def test_setDescription(self):
        desc = "Its the end of the world as we know it"
        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()
        addme = 'SELL HIGHER'
        strat.addStrategy(addme)
        strat.setDescription(addme, desc)
        d = strat.getDescription(addme)
        self.assertEqual(desc, d[1])
        desc = desc + " and its about time."
        strat.setDescription(addme, desc)
        d = strat.getDescription(addme)
        self.assertEqual(desc, d[1])

    def test_setPreferred(self):
        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()
        addme = 'SELL HIGHER'
        strat.addStrategy(addme)
        s = strat.getStrategy(addme)
        pref = s[1]
        self.assertEqual(pref, 1)
        strat.setPreferred(addme, 0)
        s = strat.getStrategy(addme)
        pref = s[1]
        self.assertEqual(pref, 0)

    def test_addStrategy(self):
        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()
        strat.addStrategy("SELL HIGHER")
        x = strat.getStrategy("SELL HIGHER")
        self.assertEqual(x[0], "SELL HIGHER")

    def test_removeStrategy(self):
        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()

        for s in self.somestrats:
            x = strat.getStrategy(s)
            self.assertEqual(x[0], s)
            strat.removeStrategy(s)
            xx = strat.getStrategy(s)
            self.assertTrue(not xx)

    def test_getStrategy(self):
        pass

    def test_getStrategies(self):
        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()
        strats = strat.getStrategies()
        slist = [s[1] for s in strats]
        for s in self.somestrats:
            self.assertIn(s, slist)

    def test_getDescription(self):
        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()

        # three strats that have written descriptions in strat.py
        strats = ['ORBU', 'ABCD', 'booty']
        for s in strats:
            ss = strat.getDescription(s)
            self.assertEqual(s, ss[0])
            self.assertGreater(len(ss[1]), 100)
    
    def test_droptables(self):
        '''test Strategy.dropTables'''
        strat = self.strat
        strat.dropTables()
        strat.createTables()
        strat.loadDefault()
        x = strat.getStrategies()
        slist = list()

        self.assertGreater(len(x), 3)
        
        for s in x:
            slist.append(s[1])
        self.assertIn('ABCD', slist)
        self.assertIn('ORBU', slist)
        self.assertIn('Fallen Angel', slist)

        strat.dropTables()

        try:
            tested = False
            strat.getStrategy('ABCD')
        except sqlite3.OperationalError:
            tested = True
        self.assertTrue(tested, 'Failed to drop tables')


    def test_createTables(self):
        '''Test Strategy.createTables'''
        strat = self.strat
        strat.dropTables()

        strat.createTables()
        conn = strat.getConnection()

        cursor = conn.execute('''SELECT name FROM sqlite_master 
                                WHERE type ='table' 
                                AND name NOT LIKE 'sqlite_%';''')
        slist = list()
        for row in cursor:
            slist.append(row[0])

        tablist = ['strategy', 'description', 'source', 'links']
        for t in tablist:
            self.assertIn(t, slist)

    def test_loadDefault(self):
        strat = self.strat
        strat.dropTables()

        strat.createTables()
        strat.loadDefault()
        d = strat.getDescription('booty')
        self.assertEqual('booty', d[0])
        self.assertGreater(len(d[1]), 100)


def main():
    unittest.main()

def notmain():
    t = TestStrategy()
    t.test_createTables()
    t.test_loadDefault()
    t.test_getDescription()
    t.test_removeStrategy()
    t.test_addStrategy()
    t.test_getStrategies()
    t.test_setPreferred()
    t.test_setDescription()
    t.test_setImage1()
    t.test_removeImage()
    t.test_setLink()
    t.test_removeLink()

if __name__ == '__main__':
    # notmain()
    main()
    