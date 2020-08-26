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

@creation_date: 8/12/20
'''
import os
import unittest
from unittest import TestCase
from sqlalchemy import MetaData, inspect

from structjour.statements.dailynotescrud import DailyNotesCrud
from structjour.models.meta import ModelBase
from structjour.models.dailynotemodel import DailyNotes
from structjour.utilities.backup import Backup


from PyQt5.QtCore import QSettings

class TestDailyNotesCrud(TestCase):
    @classmethod
    def setUpClass(cls):
        bu = Backup()
        bu.backup()
        if ModelBase.session:
            ModelBase.session.rollback()
        print(f'Files have been backed up. Most recent back is {bu.mostRecent()}')
        settings = QSettings('zero_substance', 'structjour')
        # tdb = settings.value('tradeDb')
        # if tdb and os.path.exists(tdb):
        #     os.remove(tdb)
        # sdb = settings.value('structjourDb')
        # if sdb and os.path.exists(sdb):
        #     os.remove(sdb)

        dcrud = DailyNotesCrud(daDate="20301231")
        dcrud.createTable()
        dcrud.setNote('In the year 2030 on new years eve ...')

    @classmethod
    def tearDownClass(cls):
        bu=Backup()
        bu.restore()

    def test_commitNote(self):
        note1= "a new note and date"
        date1 = "20401231"

        # Update the note made in setUpClass
        note2 = "a new note and for existing date"
        date2 = "20301231"


        dcrud = DailyNotesCrud(daDate=date1)
        dcrud.commitNote(note=note1)
        dcrud.commitNote(note=note2, daDate=date2)

        n1 = DailyNotes.getNote(date1)
        n2 = DailyNotes.getNote(date2)

        self.assertEqual(n1.note, note1)
        self.assertEqual(n2.note, note2)

    def test_setNote(self):
        note1= "another new note and date"
        date1 = "20601231"

        dcrud = DailyNotesCrud(daDate=date1)
        dcrud.setNote(note=note1)

        n1 = DailyNotes.getNote(date1)

        self.assertEqual(n1.note, note1)

    def test_getNote(self):
        date = '20501231'
        note = 'And in the year 2050 on new years eve ...'
        DailyNotes.commitNote(note=note, daDate=date)

        dcrud = DailyNotesCrud(daDate=date)
        n = dcrud.getNote()
        self.assertEqual(n, note)

    def test_removeNote(self):
        
        note1 = 'And in the year 2060 on new years eve ...'
        date1 = '20601231'
        note2 = 'And in the year 2070 on new years eve ...'
        date2 = '20701231'
        DailyNotes.commitNote(note=note1, daDate=date1)
        DailyNotes.commitNote(note=note2, daDate=date2)

        n1 = DailyNotes.getNote(date1)
        n2 = DailyNotes.getNote(date2)

        self.assertEqual(n1.note, note1)
        self.assertEqual(n2.note, note2)

        dcrud = DailyNotesCrud(daDate=date1)
        dcrud.removeNote()
        dcrud.removeNote(date2)

        n1 = DailyNotes.getNote(date1)
        n2 = DailyNotes.getNote(date2)
        self.assertIsNone(n1)
        self.assertIsNone(n2)

    # def test_dropTable(self):
    #     ModelBase.connect(new_session=True)
    #     ins = inspect(ModelBase.engine)
    #     self.assertIn("daily_notes", ins.get_table_names())
        
    #     dcrud = DailyNotesCrud()
    #     dcrud.dropTable()
    #     self.assertNotIn("daily_notes", ins.get_table_names())
        # print()

def dostuff():
    TestDailyNotesCrud.setUpClass()

    t = TestDailyNotesCrud()
    t.test_commitNote()
    # t.test_getNote()
    # t.test_setNote()
    # t.test_removeNote()
    TestDailyNotesCrud.tearDownClass()

if __name__ == '__main__':
    dostuff()



    
