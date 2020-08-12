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
sqlalchemy models for strategy tables

@author: Mike Petersen
@creation_date: April 17, 2020
'''

# import logging

from PyQt5.QtCore import QSettings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, create_engine, Column, Integer, String, Sequence
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker()


class MigrateModel(Base):
    '''
    A table to keep track of migrations that have run so that we may skip or
    partially run as needed.
    '''
    __tablename__ = 'migrate_model'
    id = Column(Integer, Sequence('migrate_model_id_seq'), primary_key=True)
    m_id = Column(String(4), nullable=False)
    date = Column(String(6), nullable=False)
    data_key = Column(String)
    data_val = Column(Integer)

    def __repr__(self):
        return f"<MigrateModel({self.m_id})>"


class ModelBase:
    '''
    Contains common methods for and static variables used by sqlalchemy stuff. 
    '''

    settings = QSettings('zero_substance', 'structjour')
    metadata = MetaData()
    db = None
    session = None
    engine = None

    @classmethod
    def connect(cls, new_session=False, con_str=None, db='tradeDb'):
        '''
        Create the engine and bind the session to a database
        :params new_session: Bind to a new session if True
        :params con_str: Use this variable to supply a database url. Using con_str
        will override the db argument.
        :params db: A QSettings key to provide a file url to a sqlite db.
        '''
        if con_str is None:
            if cls.settings.value(db) is None:
                cls.engine = None
                cls.session = None
                return
            else:
                cls.db = "sqlite:///" + cls.settings.value(db)
        else:
            cls.db = con_str

        if cls.engine is None:
            cls.engine = create_engine(cls.db)
        if new_session:
            if str(cls.engine.url) != cls.db:
                cls.engine = create_engine(cls.db)
            Session.configure(bind=cls.engine)
            cls.session = Session()

    @classmethod
    def close(cls):
        cls.session.close()

    @classmethod
    def checkVersion(cls, mv, v):
        if v < mv:
            raise ValueError(f'Incorrect version of structjour {v}. This code requires version >= {mv}')

    @classmethod
    def createAll(cls):
        if cls.engine is None:
            raise ValueError('ModelBase.connect() must be called prior to createAll()')
        Base.metadata.create_all(cls.engine)
