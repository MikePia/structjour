# Structjour -- a daily trade review helper
# Copyright (C) 2020 Zero Substance Trading
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
Updating this module from outside utility to a tool that structjour uses.
Load all the quotes in structjour.inspiration.inspire.Inspire.df
Migration 0004 was created to load the quotes into a sqlite db. This module will be rewritten
using sqlalchemy to:
1) reload all quotes if requested
2) add a quote (presumable not in the file)
3) delete a quote
4) update a quote

'''
from structjour.inspiration.inspire import Inspire as InspireQuote
import pandas as pd

from structjour.models.meta import ModelBase
from structjour.models.inspiremodel import Inspire

class InspireCrud:
    '''
    Mostly just wraps Inspire class methods using an instance of InspireCrud. But getRandom and update
    decorate with added functionality.
    '''
    def reloadAll(self, update=True):
        '''
        Reload all the quotes in the InspireQuote.df object. By default only add quotes.
        If update is set to False, replace the entire contents with the contents in InspireQuotes.df
        '''
        if not update:
            Inspire.clear()
        Inspire.loadQuotes()

    def add(self, lname='', subject='', name='', who='', quote=''):
        Inspire.add(lname=lname, subject=subject, name=name, who=who, quote=quote)

    def getQuote(self, id=-1, name=''):
        return Inspire.getQuote(id=id, name=name)

    def delete(self, id=-1, obj=None):
        Inspire.delete(id=id, obj=obj)

    def update(self, id=-1, obj=None, **kwargs):
        '''
        Update the db with obj. Either id or obj must be provided. 
        :params id: int: Id of object to update
        :params obj: Model: The object to update
        :params kwargs: string args. Update the given keys with values provided. If no
            kwargs are provided the given obj is updated. Fields not in obj are ignored
            id cannot be updated..
        :raise: ValueError if neither id or obj are provided
        '''
        if id == -1 and not obj:
            msg = "ERROR: Either id or obj must be supplied"
            logging.error(msg)
            raise valueError(msg)
        if id > -1:
            obj = Inspire.getQuote(id=id)
        switcher = [x.key for x in obj.__table__.c]
        switcher.remove('id')
        for k, v in kwargs.items():
            if k in switcher:
                obj.__setattr__(k, v)
        Inspire.update(obj)

    def getrandom(self):
        '''
        Utility to retrieve a random quote
        :return: string.  formatted quote
        '''
        q = Inspire.getRandom()
        quote =  q.quote.replace('\n', ' ')
        return f"{q.lname}, {q.subject}\n{quote}\n\t-{q.name}, {q.who}"

def getr():
    q = InspireCrud()
    print(q.getrandom())

def add():
    '''Local proof of concept'''
    icrud = InspireCrud()
    try:
        icrud.add(lname='Brown')
    except ValueError:
        print ('This is supposed to happend')
    x = icrud.add(lname="Brown", subject="On Happiness", name="Charlie Brown", who="fictional authority", 
                quote="Happiness is kicking the football")
    print()


def delete():
    '''
    Local proof of concept. Will delete the first Charilie Brown quote or do nothing.
    '''
    icrud = InspireCrud()
    x = icrud.getQuote(name='Charlie Brown')
    if x:
        icrud.delete(obj=x[0])

def update():
    icrud = InspireCrud()
    qte = icrud.getQuote(name='Charlie Brown')
    quote = 'Happiness is two kinds of ice cream'
    icrud.update(obj=qte[0], quote=quote)

if __name__ == '__main__':
    # getr()
    add()
    update()
    delete()
    



