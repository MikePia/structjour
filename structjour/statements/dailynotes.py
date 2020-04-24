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
DB model for daily notes

Created on April 6, 2020

@author: Mike Petersen
Database model class for the daily notes. This is a relative table for trade_sums
'''
import logging
import os
import sqlite3

import pandas as pd

from structjour.view.ejcontrol import EJControl

from PyQt5.QtCore import QSettings


class DailyNotes:
    def __init__(self, daDate=None, db=None, settings=None):
        self.date = None
        if daDate:
            self.date = pd.Timestamp(daDate)
        settings = QSettings('zero_substance', 'structjour')
        if db:
            self.db = db
        else:
            self.db = settings.value('tradeDb')
            if not self.db:
                j = self.settings.value('journal')
                if not j:
                    logging.info('Please set the location of your journal directory.')
                    EJControl()
                    j = self.settings.value('journal')
                    if not j:
                        return
                self.db = os.path.join(j, 'structjour.sqlite')
                settings.setValue('tradeDb', self.db)

    def createTable(self):
        '''create db table'''

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE if not exists "daily_notes" (
                "date"	INTEGER,
                "note"	TEXT,
                PRIMARY KEY("date"))''')
        conn.commit()

    def dropTable(self):
        '''Drop db table daily_notes'''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''DROP TABLE IF EXISTS daily_notes''')
        conn.commit()

    def commitNote(self, note=None, daDate=None):
        '''
        Save or update the db file for the notes field. If no note is given. will retrieve the text
         from the qt dailyNotes widget. Use setNote for a vanilla db commit
        '''
        if daDate:
            self.date = daDate
        if not self.date:
            logging.info('Cannot save without a date')
            return
        d = self.date.strftime('%Y%m%d')
        d = int(d)
        # if not note:
        #     note = self.ui.dailyNote.toPlainText()

        exist = self.getNote()

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        if exist is not None:
            cur.execute('''UPDATE daily_notes
                SET note = ?
                WHERE date = ?''', (note, d))

        else:
            cur.execute('''INSERT INTO daily_notes (date, note)
                        VALUES(?,?)''', (d, note))
        conn.commit()

    def setNote(self, note):
        '''
        Commit or update the dailyNotes db table with self.date and note
        '''
        if not self.date:
            logging.info('Cannot create note without a date')
            return
        d = self.date.strftime('%Y%m%d')
        d = int(d)

        exist = self.getNote()

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        if exist:
            cur.execute('''UPDATE daily_notes
                SET note = ?
                WHERE date = ?''', (note, d))

        else:
            cur.execute('''INSERT INTO daily_notes (date, note)
                        VALUES(?,?)''', (d, note))
        conn.commit()

    def getNote(self):
        '''
        Retrieve the notes field for the db entry for the date associated with this object. The
        date can be given as an argument or retrieved from the df argument for runDialog.
        '''
        if not self.date:
            logging.info('Cannot retrieve a note without a date')
            return
        d = self.date.strftime('%Y%m%d')
        d = int(d)

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''SELECT * from daily_notes where date = ?''', (d,))
        cursor = cur.fetchone()
        if cursor:
            return cursor[1]
        return cursor

    def saveNotes(self, event):
        '''
        Connected method from a context menu for the dailyNotes widget.
        '''
        self.commitNote()

        self.setWindowTitle('Daily Summary')


def notmain():
    d = pd.Timestamp("20200205")
    dn = DailyNotes(daDate=d)

    x = dn.getNote()
    print(x)


if __name__ == '__main__':
    notmain()
