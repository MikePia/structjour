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
API interface for dailynotes. Reimplemented in SA from the original DBAPI
'''
import logging
import os

import pandas as pd

from structjour.models.meta import ModelBase
from structjour.models.dailynotemodel import DailyNotes

from structjour.view.ejcontrol import EJControl

from PyQt5.QtCore import QSettings


class DailyNotesCrud:
    def __init__(self, daDate=None, db=None, settings=None):
        self.date = None
        if daDate:
            self.date = pd.Timestamp(daDate)
            self.date = self.date.strftime('%Y%m%d')
        settings = QSettings('zero_substance', 'structjour')
        if db:
            self.db = db
        else:
            if settings.value('tradeDb'):
                self.db = 'tradeDb'
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
        ModelBase.connect(new_session=True, db=self.db)
        ModelBase.createAll()

    # def dropTable(self):
    #     '''Drop db table daily_notes'''
    #     if not ModelBase.session:
    #         ModelBase.connect(new_session=True)
    #     DailyNotes.__table__.drop(ModelBase.engine)
    #     ModelBase.session.commit()

    def commitNote(self, note='', daDate=None):
        '''
        Save or update the db file for the notes field. If no note is given. will retrieve the text
         from the qt dailyNotes widget. Use setNote for a vanilla db commit
        '''
        if daDate:
            daDate = pd.Timestamp(daDate)
            self.date = daDate.strftime("%Y%m%d")
        self.note = note
            
        DailyNotes.commitNote(note=self.note, daDate=self.date)

    def setNote(self, note):
        '''
        Commit or update the dailyNotes db table with self.date and note
        A redundant method that was in the api
        '''
        if note:
            self.note=note
            self.commitNote(note=self.note, daDate=self.date)

    def removeNote(self, date=None):
        daDate = date
        if daDate == None:
            daDate = self.date
        if daDate == None:
            logging.info('A date must be supplied to removeNote')
            return
        self.date = pd.Timestamp(daDate)
        self.date = self.date.strftime("%Y%m%d")
        DailyNotes.removeNote(date=self.date)

    def getNote(self):
        '''
        Retrieve the notes field for the db entry for the date associated with this object. The
        date can be given as an argument or retrieved from the df argument for runDialog.
        '''
        if not self.date:
            logging.info('Cannot retrieve a note without a date')
            return None
        n =  DailyNotes.getNote(self.date)
        return n.note if n else None



def createnote():
    d = pd.Timestamp("20300205")
    dn = DailyNotesCrud(daDate=d)
    note='This is a note for the 5th of Feb in 2030'
    dn.commitNote(note=note)

    x = dn.getNote()
    print(x)

def removenote():
    d = pd.Timestamp("20300205")
    dn = DailyNotesCrud(daDate=d)
    dn.removeNote(date=d)

def notmain():
    # createote()
    removenote()


if __name__ == '__main__':
    notmain()
