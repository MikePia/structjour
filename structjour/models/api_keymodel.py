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
@creation_date: /8/2020

the tokens for REST access to stock data
'''
import logging
from sqlalchemy import Column, String, Integer
from structjour.models.meta import Base, ModelBase

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    api = Column(String, unique=True, nullable=False)
    key = Column(String)

    @classmethod
    def getKey(cls, api, keyonly=True):
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        q = session.query(ApiKey).filter_by(api=api).one_or_none()
        if keyonly:
            return q.key if q else None
        return q

    @classmethod
    def updateKey(cls, api, key):
        return cls.addKey(api, key)

    @classmethod
    def addKey(self, api, key=''):
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        q = session.query(ApiKey).filter_by(api=api).one_or_none()
        if q:
            q.key = key
            session.add(q)
            session.commit()
            session.close()
            return
        
        newkey = ApiKey(api=api, key=key)
        session.add(newkey)
        session.commit()
        session.close()

    @classmethod
    def removeKey(cls, api):
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        q = session.query(ApiKey).filter_by(api=api).one_or_none()
        if q:
            ModelBase.session.delete(q)
            ModelBase.session.commit()
            ModelBase.session.close()

def removekey():
    a = ApiKey()
    a.removeKey('freddy')
    a.removeKey('flintstone')
    a.removeKey('george')
    a.removeKey('hasaneweverything')

def updatekey():
    a = ApiKey()
    a.updateKey('freddy', 'hasaneweverything')
    a.updateKey('george', 'hasanewkey')

def addkey():
    a = ApiKey()
    a.addKey('george')
    a.addKey('flintstone', 'isTheKey')
    print(a.getKey('flintstone'))
    print(a.getKey('george'))

def getkey():
    a = ApiKey()
    print (a.getKey('fh'))
    print (a.getKey('bc'))
    print (a.getKey('av'))
    print (a.getKey('fred'))

def dostuff():
    # getkey()
    # addkey()
    # updatekey()
    removekey()


if __name__ == '__main__':
    dostuff()

