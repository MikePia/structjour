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
from structjour.models.meta import ModelBase
from structjour.models.strategymodels import Strategy, Source, Description, Images
from structjour.utilities.backup import Backup
from PyQt5.QtCore import QSettings

class Test_StrategyCrud(TestCase):

    @classmethod
    def setUpClass(cls):
        bu = Backup()
        bu.backup()
        print(f'Files have been backed up. Most recent back is {bu.mostRecent()}')
        settings = QSettings('zero_substance', 'structjour')
        tdb = settings.value('tradeDb')
        if tdb and os.path.exists(tdb):
            os.remove(tdb)
        sdb = settings.value('structjourDb')
        if sdb and os.path.exists(sdb):
            os.remove(sdb)

        # create the schema
        ModelBase.connect(new_session=True, db='structjourDb')
        ModelBase.createAll()

    

    @classmethod
    def tearDownClass(cls):
        bu=Backup()
        bu.restore()



    def test_getid(self):
        '''Local proof of concept'''
        sCrud = StrategyCrud()
        print(sCrud.getId('VWAP Support'))

    def test_setlink(self):
        '''Local proof of concept'''
        sCrud = StrategyCrud()
        sCrud.setLink('VWAP Support', 'https://fictional/web/site')

    def test_getLinks(self):
        '''Local proof of concept'''
        scrud = StrategyCrud()
        print(scrud.getLinks('ABCD'))
        print()

    def test_getimage1(self):
        scrud = StrategyCrud()
        print(scrud.getImage1('ABCD'))


    def test_setimage1(self):
        scrud = StrategyCrud()
        scrud.setImage1("Schnork", '/c/schnork/image/for/chart/1')

    def test_setimage2(self):
        scrud = StrategyCrud()
        scrud.setImage2("Schnork", '/c/schnork/image/for/chart/2')

    def test_removeimage(self):
        scrud = StrategyCrud()
        scrud.removeImage1('Schnork')
        scrud.removeImage2('Schnork')



    def test_removelink(self):
        '''Local proof of concept- removes the link added in setlink'''
        scrud = StrategyCrud()
        scrud.removeLink('VWAP Support', 'https://fictional/web/site')

    
    def test_addstrategy(self):
        '''Local proof of concept'''
        scrud = StrategyCrud()
        try: 
            scrud.addStrategy('Schnork')
        except Exception as ex:
            print(ex)
            print('Schnork already exists')

    def test_getstrategy(self):
        '''Local proof of concept'''
        scrud = StrategyCrud()
        s = scrud.getStrategy(name="ABCD")
        print(s)

    def test_removestrategy(self):
        scrud = StrategyCrud()
        scrud.removeStrategy('Schnork')

    def test_getstrategies(self):
        '''Local proof of concept'''
        scrud = StrategyCrud()
        ss = scrud.getStrategies()
        for s in ss:
            print(s[1])

    def test_getpreferred(self):
        '''Local proof of concept'''
        scrud = StrategyCrud()
        ss = scrud.getPreferred()
        for s in ss:
            print(s[1])

    def setpreferred(self):
        '''Local proof of concept'''
        scrud = StrategyCrud()
        scrud.setPreferred("Schnork",  pref=True)


    def getdescription(self):
        scrud = StrategyCrud()
        print (scrud.getDescription(name = 'Rising Devil'))
        print (scrud.getDescription(name = 'Rising Fred'))

    def setdescription(self):
        name = 'Mistake'
        desc = "The description for the mistake category is don't do that anymore. But still ..."
        scrud = StrategyCrud()
        scrud.setDescription(name, desc)
    scrud.setDescription('schnorrkel2', 'No need to describe schnorkel2. Everyone knows it well')






def notmain():
    Test_StrategyCrud.setUpClass()
    # Test_StrategyCrud.tearDownClass()

if __name__ == '__main__':
    notmain()
        

