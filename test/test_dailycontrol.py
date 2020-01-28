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
import sys
import unittest
import sqlite3
from unittest import TestCase
import pandas as pd


# from PyQt5 import QtCore, QtWebEngineWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication
# from PyQt5.QtTest import QTest


from structjour.view.dailycontrol import DailyControl

app = QApplication(sys.argv)


class TestDailyCtrl(TestCase):
    '''
    Test the db calls and the user interaction stuff. The DailyNotes form has the daily note- saved in db,
    a daily summary table, generated from the summary form  and daily trades table, not saved
    '''

    def __init__(self, *args, **kwargs):
        super(TestDailyCtrl, self).__init__(*args, **kwargs)

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

    def test_drop_createTable(self):
        '''Test the creation and drop of the daily notes table'''
        dc = DailyControl(pd.Timestamp.now(), self.testdb)

        con = sqlite3.connect(self.testdb)
        mycur = con.cursor()

        dc.dropTable()
        mycur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        available_tables = [x[0] for x in mycur.fetchall()]
        self.assertNotIn("daily_notes", available_tables)

        dc.createTable()
        mycur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        available_tables = [x[0] for x in mycur.fetchall()]
        self.assertIn("daily_notes", available_tables)

        dc.dropTable()
        mycur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        available_tables = [x[0] for x in mycur.fetchall()]
        self.assertNotIn("daily_notes", available_tables)

    def test_commitNote(self):
        '''
        Tests commitNote with an argument for note for creating new note
        '''
        daDate = pd.Timestamp('2021-06-06')
        dc = DailyControl(daDate, db=self.testdb)
        # dc.runDialog(self.df, tradeSum=self.ts)
        dc.dropTable()
        dc.createTable()
        note = '''Twas all hallow's  eve and all throug the grove
                  jabberwock trounced his thro boro-dove'''
        # dc.ui.dailyNotes.setText(note)
        dc.commitNote(note=note)
        xnote = dc.getNote()
        self.assertEqual(note, xnote)

    def test_commitNote_update(self):
        '''
        Tests commitNote with an argument for note for creating new note
        '''
        daDate = pd.Timestamp('2021-06-06')
        dc = DailyControl(daDate, db=self.testdb)
        # dc.runDialog(self.df, tradeSum=self.ts)
        dc.dropTable()
        dc.createTable()
        note = '''Twas all hallow's  eve and all throug the grove
                  jabberwock trounced his thro boro-dove'''
        dc.commitNote(note=note)
        note = '''Forget all that'''
        dc.commitNote(note=note)
        xnote = dc.getNote()
        self.assertEqual(note, xnote)

    def test_getnote(self):
        pass  # test is covered in commitNote tests

    def test_populateNotes(self):
        pass

    def test_populateStuff(self):
        pass

    def test_populateM(self):
        pass


def main():
    unittest.main()


def notmain():
    t = TestDailyCtrl()
    # t.test_DailyControl()
    # t.test_drop_createTable()
    # t.test_commitNote()
    t.test_commitNote_update()
    # t.setUp()


if __name__ == '__main__':
    # main()
    notmain()
