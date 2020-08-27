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
import logging
from sqlalchemy import Column, String, Integer, Boolean, func
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
        Its a one-off becasue we have to seperate 2 fields from one. If the quote
        already exists, leave it and skip it.
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
        session.close()
        
    @classmethod
    def clear(cls):
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        session.query(Inspire).delete()
        session.commit()
        session.close()

    @classmethod
    def add(cls, lname='', subject='', name='', who='', quote=''):
        '''
         :raises: ValueError if all arguments are not supplied
        '''
        if not (lname and subject and name and who and quote):
            msg = 'All parameters are required to have data'
            logging.error(msg)
            raise ValueError(msg)
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        insp = Inspire(
            lname = lname,
            subject=subject,
            name=name,
            who=who,
            quote=quote
        )
        session.add(insp)
        session.commit()
        session.close()

    @classmethod
    def getQuote(cls, id=-1, name=''):
        '''
        Get a quote by id or  name 
        :return: list
        :raises: ValueError if neither id or name are supplied
        '''
        if id == -1  and not name:
            msg = 'either id or name needs to be supplied'
            logging.error(msg)
            raise ValueError(msg)
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        if id > -1:
            q = session.query(Inspire).filter_by(id=id).one_or_none()
            if q:
                return [q]
            return []
        q = session.query(Inspire).filter_by(name=name).all()
        return q

    @classmethod
    def delete(cls, id=-1, obj=None):
        new_session = True
        if id == -1:
            new_session = False
        ModelBase.connect(new_session=new_session)
        session = ModelBase.session
        if id == -1:
            session.delete(obj)
            session.commit()
            session.close()
            return
        q = session.query(Inspire).filter_by(id=id).one_or_none()
        if not q:
            return
        session.delete(q)
        session.commit()
        session.close()

    @classmethod
    def update(cls, obj):
        '''
        Commit obj to database
        :params obj: <Inspire>  An updated obj to commit
        '''
        # ModelBase.connect()
        if isinstance(obj, Inspire):
            session = ModelBase.session
            session.commit()
            session.close()

    @classmethod
    def getRandom(cls):
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        q = session.query(Inspire).order_by(func.random()).first()
        print(q)
        return q
    

            
def clearQuotes():
    '''
    Local proof of concept
    '''
    # from structjour.inspiration.inspire import Inspire as InspireQuote
    Inspire.clear()

def add():
    '''Local proof of concept'''
    try:
        Inspire.add(lname='Brown')
    except ValueError:
        print ('This is supposed to happend')
    x = Inspire.add(lname="Brown", subject="On Happiness", name="Charlie Brown", who="fictional authority", 
                quote="Happiness is kicking the football")
    print()

def getQuote():
    x = Inspire.getQuote(id=239)
    if x:
        print(x[0].quote)
    x = Inspire.getQuote(name="Michael Jordan")
    if x:
        print(x[0].quote)
    print()

def delete():
    '''
    Local proof of concept. Will delete the first Charilie Brown quote or do nothing.
    '''
    x = Inspire.getQuote(name='Charlie Brown')
    if x:
        Inspire.delete(obj=x[0])

def update():
    qte = Inspire.getQuote(name='Charlie Brown')
    qte[0].quote = 'Happiness is two kinds of ice cream'
    Inspire.update(qte[0])

def getRandom():
    return Inspire.getRandom()



def loadQuotes():
    '''
    Local proof of concept
    '''
    from structjour.inspiration.inspire import Inspire as InspireQuote
    import pandas as pd
    iq = InspireQuote()
    Inspire.loadQuotes(iq)


def doStuff():
    # loadQuotes()
    # clearQuotes()
    # try:
    #     add()
    # except:
    #     pass
    # update()
    # getQuote()
    # delete()
    getRandom()

if __name__ == '__main__':
    doStuff()