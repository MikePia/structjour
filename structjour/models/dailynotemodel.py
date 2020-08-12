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
sqlalchemy models for inspire quotes

@author: Mike Petersen
@creation_date: 8/11/2020

Hold the daily note model. Each note belongs to a single day and has a one to 
many relationship with the trades of that day but currently the relationship is
manual
'''
import logging
import pandas as pd
from sqlalchemy import Column, String, Integer
from structjour.models.meta import Base, ModelBase

class DailyNotes(Base):
    '''
    TODO
    Why did I create the date as an Integer???. 
    Translate it to SA for now. Maybe change it later
    '''
    __tablename__ = "daily_notes"
    date = Column(Integer, primary_key=True)
    note = Column (String)

    def __repr__(self):
        return f'<Daily note for {self.date}>'

    @classmethod
    def commitNote(cls, note=None, daDate=None):
        if not daDate:
            logging.info('Cannot save daily note without a date')
            return

        d  = pd.Timestamp(daDate)
        d = d.strftime('%Y%m%d')

        # getNote will create the session to use for add
        exist = DailyNotes.getNote(d)
        session = ModelBase.session
        if exist and exist.date:
            exist.note = note
            session.add(exist)
        else:
            session.add(DailyNotes(date= int(d), note=note))
        session.commit()

    @classmethod
    def getNote(cls, date):
        '''
        Retrieve the object for the record associated with date.
        :return: None if the record does not exist.
        '''
        if not date:
            logging.info('A Date must be provided to DailyNotes.getNote')
            return None
        date = pd.Timestamp(date)
        date = int(date.strftime("%Y%m%d"))

        ModelBase.connect(new_session=True)
        session = ModelBase.session

        q = session.query(DailyNotes).filter_by(date=int(date)).one_or_none()
        return q

    @classmethod
    def removeNote(cls, date):
        q = DailyNotes.getNote(date)
        if q:
            ModelBase.session.delete(q)
            ModelBase.session.commit()



            


        
    

