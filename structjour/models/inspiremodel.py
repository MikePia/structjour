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
@creation_date: 7/31/2020

A Single table to hold quotes. Its use expanded to include a json output unrelated to structjour
'''
from sqlalchemy import Column, String, Integer, Boolean
from structjour.models.meta import Base, ModelBase

class Inspire(Base):
    __tablename__ = "inspire"
    id = Column(Integer, primary_key=True)
    lname = Column(String)
    subject = Column(String)
    name = Column(String)
    who = Column(String)
    quote = Column(String, unique=True)
    active = Column(Boolean, default=True)
    # active 

    def __repr__(self):
        return f'<Inspire({self.name})>'

    @classmethod
    def loadQuotes(cls, inspireQuote):
        '''
        This is a one-off to load the quotes in the inspiration.inspire.Inspire class.
        Its a one-off becasue we have to seperate 2 fields from one
        '''
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        ModelBase.createAll()
        for i, row in inspireQuote.df.iterrows():
            # print(row['name'])
            test = row['who'].split(", ")
            if len(test) != 2:
                msg = f"ERROR: bad data in quote: {row}"
                logging.error(msg)
                print(msg)
                continue
            name, who = test
            
            q = ModelBase.session.query(Inspire).filter_by(quote=row['quote']).first()
            if q:
                print(f'found a duplicate for quote: {q.quote}')
                continue
            qte = Inspire(lname = row['name'],
                  subject=row['on'],
                  name=name,
                  who = who, quote=row['quote'])
            
            session.add(qte)

            try:
                session.commit()
            except:
                pass
            



def loadQuotes():
    from structjour.inspiration.inspire import Inspire as InspireQuote
    import pandas as pd
    iq = InspireQuote()
    Inspire.loadQuotes(iq)


def doStuff():
    loadQuotes()

    pass

if __name__ == '__main__':
    doStuff()