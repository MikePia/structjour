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
Test the methods in th module journal.dfutil
Created on Aug 13, 2020

@author: Mike Petersen
Test the methods in db access methods DbDoctor
'''

import unittest
import os

from structjour.models.meta import ModelBase
from structjour.models.trademodels import Trade, TradeSum, Tags
from structjour.statements.dbdoctor import DbDoctorCrud
from structjour.utilities.backup import Backup

from PyQt5.QtCore import QSettings

class Test_StrategyCrud(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bu = Backup()
        bu.backup()
        print(f'Files have been backed up. Most recent back is {bu.mostRecent()}')
        settings = QSettings('zero_substance', 'structjour')
        tdb = settings.value('tradeDb')
        # if tdb and os.path.exists(tdb):
        #     os.remove(tdb)
        # sdb = settings.value('structjourDb')
        # if sdb and os.path.exists(sdb):
        #     os.remove(sdb)

        ModelBase.connect(new_session=True)
        ModelBase.createAll()

    @classmethod
    def tearDownClass(cls):
        bu=Backup()
        bu.restore()

    def test_deleteTradeById(self):
        pass

    def test_deleteTradeSumById(self):
        pass

    def test_doDups(self):
        pass

    def test_getDuplicateTrades(self):
        pass

    def test_getTradesById(self):
        pass

    def test_getTradesBySumId(self):
        pass

    def test_makeDupDict(self):
        pass


def dostuff():
    t = Test_StrategyCrud()
    # t.setUpClass()
    t.tearDownClass()
    print()

if __name__ == '__main__':
    dostuff()

