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
@creation_date: 5/5/2020

@ Programming Notes:
The strategy table has no relationship with TradeSums.strategy column which is a string so that
one-off # strategies can be named by the user without adding them to the database
### The strangeness ...
of having the seperate table for description, which is one to one, was a plan to allow user
created 'strategy packages' that could be exchanged.  That was a while ago and I don't know
if I will implement the strategy packages. My thinking now is that if I do implement it, there
is a better abstraction (at a higher level with a 'strategy_packages' table) and description
should probably be a column in strategy-- that means migration. (But after sa transition is
complete)
'''

from sqlalchemy import (Integer, Column, String, Boolean, ForeignKey)
from sqlalchemy.orm import relationship
from structjour.models.meta import Base


class Source(Base):
    __tablename__ = "source"
    id = Column(Integer, primary_key=True)
    datasource = Column(String)

    def __repr__(self):
        return f'<Source({self.datasource})>'


class Strategy(Base):
    __tablename__ = "strategy"
    id = Column('id', Integer, primary_key=True)
    name = Column(String(108))
    short_name = Column(String(54))
    preferred = Column(Boolean)

    def __repr__(self):
        return f'<Strategy({self.name})>'


class Description(Base):
    __tablename__ = "description"

    id = Column(Integer, primary_key=True)
    description = Column(String)
    source_id = Column(Integer, ForeignKey('source.id'))

    thesource = relationship('Source', backref='descriptionsource')

    strategy_id = Column(Integer, ForeignKey('strategy.id'))
    thestrategy = relationship('Strategy', backref='description')

    def __repr__(self):
        return f'<Description({self.thestrategy})>'


class Images(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    widget = Column(Integer)
    strategy_id = Column(Integer, ForeignKey('strategy.id'))

    strategy = relationship('Strategy', backref='images')


class Links(Base):
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    link = Column(String(512))
    strategy_id = Column(Integer, ForeignKey('strategy.id'))

    strategy = relationship('Strategy', backref='links')
