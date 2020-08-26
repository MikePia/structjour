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
Test the methods module structjour.models.meta
@author: Mike Petersen

@creation_date: 8/6/20

Planning notes:
Spinning wheels here. I created the StrategyCrud class with connect(db='structjourDb') calls to ModelBase.
All methods in ModelBase and StratgyCrud are classmethod. I need to use connect(con_str='...') and hand it 
a str but they are class methods. How can I provide an initializtion string to each of the class methods. 
Could add an arg to every signature -- really hacky
Alternately, could backup db, delete db, run tests, restore db but seems like a bad design.

ARGH too much spinning -- choosing Hack B-- backup and restore-- leaving db name intact
'''
import os

import unittest
from unittest import TestCase
from structjour.strategy.strategycrud import StrategyCrud
from structjour.models.meta import ModelBase
from structjour.models.strategymodels import Strategy, Source, Description, Images, Links
from structjour.utilities.backup import Backup
from PyQt5.QtCore import QSettings


class Test_StrategyCrud(TestCase):

    @classmethod
    def setUpClass(cls):
        bu = Backup()
        bu.backup()
        if ModelBase.session:
            ModelBase.session.rollback()
        print(f'Files have been backed up. Most recent back is {bu.mostRecent()}')
        settings = QSettings('zero_substance', 'structjour')
        tdb = settings.value('tradeDb')
        # if tdb and os.path.exists(tdb):
        #     os.remove(tdb)
        # sdb = settings.value('structjourDb')
        # if sdb and os.path.exists(sdb):
        #     os.remove(sdb)

        # create the schema
        scrud = StrategyCrud()
        scrud.createTables()
        scrud.addStrategy('VWAP Support')

    @classmethod
    def tearDownClass(cls):
        bu=Backup()
        bu.restore()

    def test_getid(self):
        '''Local proof of concept'''
        sCrud = StrategyCrud()
        id =  sCrud.getId('VWAP Support')
        self.assertIsNotNone(id)
        self.assertGreaterEqual(id, 1)

    def test_setlink(self):
        sCrud = StrategyCrud()
        dalink = 'https://fictional/web/site'
        strat = 'VWAP Support'
        sCrud.setLink(strat, dalink)
        links = sCrud.getLinks(strat)
        self.assertIn(dalink, links)

    def test_getLinks(self):

        scrud = StrategyCrud()
        strat = 'ABCD'
        link = 'https://A/website/explaining/ABCD'
        scrud.addStrategy(strat)
        scrud.setLink(strat, link)
        links = scrud.getLinks('ABCD')
        self.assertIn(link, links)

    def test_removelink(self):
        '''Exercises all Link methods'''
        scrud = StrategyCrud()
        strat = 'VWAP Support'
        link = 'https://A/website/explaining/Everything/and/VWAPD'
        link2 = 'https://A/website/explaining/Everything/else/and/VWAPD'
        scrud.setLink(strat, link)
        res = scrud.getLinks(strat)
        self.assertIn(link, res)

        scrud.setLink(strat, link2)
        res2 = scrud.getLinks(strat)
        self.assertIn(link2, res2)
        self.assertTrue(len(res2) == len(res)+1)

        scrud.setLink(strat, link)
        res3 = scrud.getLinks(strat)
        self.assertEqual(len(res2), len(res3))

        scrud.removeLink(strat, link)
        scrud.removeLink(strat, link2)

        res4 = scrud.getLinks(strat)
        if res4:
            self.assertNotIn(link, res4)
            self.assertNotIn(link2, res4)

        scrud.removeLink('VWAP Support', 'https://fictional/web/site')

    def test_setimage1(self):
        '''
        Tests getImage1 and setImage1
        '''
        scrud = StrategyCrud()
        img = '/c/schnork/image/for/chart/1'
        scrud.setImage1("Schnork", img)
        res = scrud.getImage1("Schnork")
        self.assertEqual(img, res)

    def test_setimage2(self):
        scrud = StrategyCrud()
        img = '/c/schnork/image/for/chart/2'
        scrud.setImage2("Schnork", img)
        res = scrud.getImage2("Schnork")
        self.assertEqual(img, res)
        
    def test_removeimage(self):
        '''
        Exercise all the image get set and remove functions
        '''
        scrud = StrategyCrud()
        img1 = '/c/schnork/image/or/q/for/chart/1'
        img2 = '/c/schnork/image/or/q/for/chart/2'
        scrud.setImage1("Schnork", img1)
        scrud.setImage2("Schnork", img2)
        res1 = scrud.getImage1("Schnork")
        res2 = scrud.getImage2("Schnork")
        self.assertIn(img1, res1)
        self.assertIn(img2, res2)

        scrud.removeImage1('Schnork')
        scrud.removeImage2('Schnork')
        res1 = scrud.getImage1("Schnork")
        res2 = scrud.getImage2("Schnork")
        self.assertIsNone(res1)
        self.assertIsNone(res2)

    
    def test_getstrategy(self):
        '''Local proof of concept'''
        scrud = StrategyCrud()
        strat = 'Buy Lower'
        scrud.addStrategy('Buy Lower')
        s = scrud.getStrategy(name="Buy Lower")
        self.assertEqual(strat, s.name)

    def test_getstrategies(self):
        '''
        Exercises addStratege and getStrategies. Get strategies gets a list of lists.
        TODO: 
        It gets the format the the DBAPI got. Fix it later
        '''
        scrud = StrategyCrud()
        strat1 = 'Buy Lower than that'
        strat2 = 'Sell higher'

        scrud.addStrategy(strat1)
        res1 = scrud.getStrategies()

        scrud.addStrategy(strat2)
        res2 = scrud.getStrategies()

        self.assertIn(strat1, [x[1] for x in res1])
        self.assertIn(strat2, [x[1] for x in res2])
        self.assertEqual(len(res2), len(res1)+1)

        scrud.addStrategy(strat1)
        res3 = scrud.getStrategies()
        self.assertEqual(len(res2), len(res3))


    def test_removestrategy(self):
        '''
        Demonstrates Strategies relationship with Images, Description and Links and cascacde delete for each
        Not sure if the relationships work for creation (through a Strategy object) But then there is no 
        call for it in the structjour strategy browser; each of the fields are created from a different button
        '''
        scrud = StrategyCrud()

        stratName = 'Schnork'
        img = '/c/an/image/for/schnork.gif'
        desc = "Schnork is a strategy of percentages."
        link = 'https://A/thorough/description/of/the percentages/of/schnork.html'

        scrud.addStrategy(stratName)
        scrud.setImage1(stratName, img)
        scrud.setDescription(stratName, desc)
        scrud.setLink(stratName, link)
        strat = Strategy.getStrategy(stratName)

        self.assertIn(img,  [x.name for x in strat.images])
        self.assertIn(desc,  [x.description for x in strat.description])
        self.assertIn(link,  [x.link for x in strat.links])
        
        scrud.removeStrategy(stratName)
        strat = Strategy.getStrategy(stratName)

        # Tests have to get all links, descriptions, and images from their own table to test they were deleted
        links = Links.getAllLinks()
        descriptions = Description.getAllDescriptions()
        images = Images.getAllImages()

        self.assertIsNone(strat)
        self.assertNotIn(img, [x.name for x in images])
        self.assertNotIn(img, [x.description for x in descriptions])
        self.assertNotIn(img, [x.link for x in links])

    def test_getpreferred(self):
        scrud = StrategyCrud()
        strat1 = 'A great strategy'
        strat2 = 'A questionable strategy'
        scrud.addStrategy(strat1, preferred=True)
        scrud.addStrategy(strat2, preferred=False)
        prefs = scrud.getPreferred()
        self.assertIn(strat1, [x[1] for x in prefs])
        self.assertNotIn(strat2, [x[1] for x in prefs])


    def test_setpreferred(self):
        scrud = StrategyCrud()
        strat = 'THE strategy for consistency'

        scrud.addStrategy(strat)
        prefs = scrud.getPreferred()
        self.assertIn(strat, [x[1] for x in prefs])

        scrud.setPreferred(strat,  pref=False)
        prefs = scrud.getPreferred()
        self.assertNotIn(strat, [x[1] for x in prefs])

    def test_getdescription(self):
        scrud = StrategyCrud()
        strat1 =  'Rising Devil'
        strat2 =  'Rising Fred'
        scrud.addStrategy(strat1)
        scrud.addStrategy(strat2)
        desc = 'Stock is in uptrend for days-gaps down - falls to open - ...'
        scrud.setDescription(strat1, desc)

        d1 = scrud.getDescription(strat1)
        d2 = scrud.getDescription(strat2)
        self.assertEqual(d1.description, desc)
        self.assertIsNone(d2)


    def test_setdescription(self):
        name = 'Mistake'
        desc1 = "The description for the mistake category is don't do that anymore. But still ..."
        scrud = StrategyCrud()
        scrud.setDescription(name, desc1)

        strat = Strategy.getStrategy(name)
        self.assertIsNotNone(strat)
        self.assertEqual(desc1, strat.description[0].description)

        desc2 = "The description for the mistake category is don't do that anymore. But still, everyone has some."
        scrud.setDescription(name, desc2)
        strat = Strategy.getStrategy(name)
        self.assertEqual(desc2, strat.description[0].description)
        
        descriptions = Description.getAllDescriptions()
        self.assertNotIn(desc1, [x.description for x in descriptions])

    def test_sourceEntries(self):
        sources = Source.getAllSources()
        self.assertIn('default', [x.datasource for x in sources])
        self.assertIn('user', [x.datasource for x in sources])
        self.assertIn('contrib', [x.datasource for x in sources])

def notmain():
    Test_StrategyCrud.setUpClass()
    t = Test_StrategyCrud()
    # t.test_getid()
    # t.test_setlink()
    # t.test_getLinks()
    # t.test_removelink()
    # t.test_setimage1()
    # t.test_setimage2()
    # t.test_removeimage()
    # t.test_getstrategy()
    # t.test_getstrategies()
    # t.test_removestrategy()
    # t.test_getpreferred()
    # t.test_setpreferred()
    t.test_getdescription()
    # t.test_setdescription()
    # t.test_sourceEntries()

    Test_StrategyCrud.tearDownClass()

if __name__ == '__main__':
    unittest.main()
    # notmain()
        

