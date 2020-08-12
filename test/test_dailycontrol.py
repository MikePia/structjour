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
Test the module dailycontrol

Created on May 22, 2019

@author: Mike Petersen
'''
import os
import sys
import unittest
import sqlite3
from unittest import TestCase
import pandas as pd


# from PyQt5 import QtCore, QtWebEngineWidgets
from PyQt5 import QtCore
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
from PyQt5 import QtWebEngineWidgets    # noqa:  F401
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication
# from PyQt5.QtTest import QTest


from structjour.view.dailycontrol import DailyControl

app = QApplication(sys.argv)


class TestDailyCtrl(TestCase):
    '''
    Test the db calls and the user interaction stuff. The DailyCtrl form has a daily summary table, generated from 
    the summary form  and daily trades table, generated-not saved.
    '''

    def __init__(self, *args, **kwargs):
        super(TestDailyCtrl, self).__init__(*args, **kwargs)
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))

        self.testdb = 'test/testdb.sqlite'
        self.apiset = QSettings('zero_substance/stockapi', 'structjour')
        self.realdb = self.apiset.value('dbsqlite')

    def test_DailyControl(self):
        '''
        Test class creation using a test database. Test that we have set the db
        '''

        dc = DailyControl(pd.Timestamp.now(), self.testdb)
        self.assertEqual(self.testdb, dc.db)

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_populateStuff(self):
        pass

    def test_populateM(self):
        pass


def main():
    unittest.main()


def notmain():
    t = TestDailyCtrl()


if __name__ == '__main__':
    main()
    # notmain()
