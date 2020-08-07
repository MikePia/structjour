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

TODO:
Several of these methods look for duplicate fields before adding a record. There is probably 
an add_or_ignore solution to slip past unique constraints. Haven't found it.
'''
import logging
from sqlalchemy import (Integer, Column, String, Boolean, ForeignKey, and_)
from sqlalchemy.orm import relationship, backref
from structjour.models.meta import Base, ModelBase


class Source(Base):
    __tablename__ = "source"
    id = Column(Integer, primary_key=True)
    datasource = Column(String)

    def __repr__(self):
        return f'<Source({self.datasource})>'

    @classmethod
    def addSource(cls, name, id=None):
        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        if id:
            source = Source(datasource=name, id=id)
        else:
            source = Source(datasource=name)
        session.add(source)
        session.commit()

    @classmethod
    def getAllSources(cls):
        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        return session.query(Source).all()
        



class Strategy(Base):
    __tablename__ = "strategy"
    id = Column('id', Integer, primary_key=True)
    name = Column(String(108), unique=True)
    short_name = Column(String(54), unique=True)
    preferred = Column(Boolean)

    def __repr__(self):
        return f'<Strategy({self.name})>'

    @classmethod
    def getId(cls, name):
        '''
        Get the id of the strategy named name or return None if not found
        '''
        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        q = session.query(Strategy.id).filter_by(name=name).one_or_none()
        if not q: return None
        return q.id

    @classmethod
    def addStrategy(cls, name, preferred=True):
        if Strategy.getStrategy(name):
            logging.info(f'Strategy {name} already exists. No strategy added')
            return
        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        
        strat = Strategy(name=name, preferred = preferred)
        session.add(strat)
        session.commit()
        return strat

    @classmethod
    def getStrategy(cls, name=None, sid=None):

        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        if name:
            q = session.query(Strategy).filter_by(name=name).one_or_none()
            return q

        return session.query(Strategy).filter_by(id=sid).one_or_none()

    @classmethod
    def removeStrategy(cls, name):
        strat = Strategy.getStrategy(name)
        if strat:
            ModelBase.session.delete(strat)
            ModelBase.session.commit()

    @classmethod
    def getStrategies(cls):
        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        strats = session.query(Strategy).all()
        return strats

    @classmethod
    def getPreferred(cls, pref=1):
        '''Returns all strategies marked preferred'''
        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        pref = session.query(Strategy).filter_by(preferred=True).all()
        return pref

    @classmethod
    def setPreferred(cls, name, pref):
        strat = Strategy.getStrategy(name=name)
        if strat:
            strat.preferred = False
            ModelBase.session.commit()
        

    @classmethod
    def removeStrategy(cls, name):
        '''Uses session from getStrategy'''
        strat = Strategy.getStrategy(name=name)
        if strat:
            ModelBase.session.delete(strat)
            ModelBase.session.commit()


class Description(Base):
    __tablename__ = "description"

    id = Column(Integer, primary_key=True)
    description = Column(String)
    source_id = Column(Integer, ForeignKey('source.id'))

    thesource = relationship('Source', backref='descriptionsource')

    strategy_id = Column(Integer, ForeignKey('strategy.id'))
    thestrategy = relationship('Strategy', 
                  backref=backref('description', cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Description({self.thestrategy})>'

    @classmethod
    def getDescription(cls, name):
        '''Uses session from getId'''
        strat_id = Strategy.getId(name)
        if strat_id:
            desc = ModelBase.session.query(Description).filter_by(strategy_id = strat_id).one_or_none()

            return desc

    @classmethod
    def setDescription(self, name, desc):
        '''
        Update description or add description if it does noe exist.
        If the strategy represented by name does not exist ....
        
        '''
        sid = Strategy.getId(name)
        if not sid:
            # Going to create a new strategy here
            Strategy.addStrategy(name)
            sid = Strategy.getId(name)
        
        session = ModelBase.session
        theDesc = session.query(Description).filter_by(strategy_id=sid).one_or_none()
        if theDesc:
            theDesc.description = desc
        else:
            theDesc = Description(
                description = desc,
                # Set source to user (implementing strat packages?)
                # TODO this is a bit dodgy, get it from the source  table instead
                source_id = 2,
                strategy_id = sid

            )
        session.add(theDesc)
        session.commit()
    @classmethod
    def getAllDescriptions(cls):
        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        return session.query(Description).all()
            

class Images(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    widget = Column(Integer)
    strategy_id = Column(Integer, ForeignKey('strategy.id'))

    strategy = relationship('Strategy', 
                    backref=backref('images', cascade="all, delete-orphan"))
                    
    @classmethod    
    def getImage(cls, strat, widget):
        '''
        :return a list of [<Images>, <Strategy>]
        '''
        # Implicit join retrives a list[image, strategy]
        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        q = session.query(Images, Strategy).filter(and_(
            Strategy.id == Images.strategy_id,
            Strategy.name == strat,
            Images.widget == widget)).one_or_none()
        return q

    @classmethod
    def setImage(cls, strat, name, widget):
        '''
        Uses session created in getImage. 
        :params strat: str: name of strategy
        :params name: str: name of image
        '''
        strat_id = Strategy.getId(strat)
        if not strat_id:
            s = Strategy.addStrategy(strat)
            strat_id =  s.id
            
        img = Images.getImage(strat, widget)
        if img and img[0]:
            img = img[0]
            img.name = name
            ModelBase.session.commit()
        else:
            img = Images(
                name=name,
                widget=widget,
                strategy_id = strat_id
            )
            ModelBase.session.add(img)
            ModelBase.session.commit()
        ModelBase.session.close()
        return img

    @classmethod
    def removeImage(cls, strat, widget):
        img = Images.getImage(strat, widget)
        if img and isinstance(img[0], Images):
            ModelBase.session.delete(img[0])
            ModelBase.session.commit()

    @classmethod
    def getAllImages(cls):
        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        return session.query(Images).all()

class Links(Base):
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    link = Column(String(512), unique=True)
    strategy_id = Column(Integer, ForeignKey('strategy.id'))

    strategy = relationship('Strategy', backref=backref('links', cascade="all, delete-orphan"))
    

    @classmethod
    def setLink(cls, name, url):
        '''Uses session created in getId'''
        sid = Strategy.getId(name)
        if not sid:
            logging.error(f'There is no strategy named {name}. Cannot attach link')
            return
        q = ModelBase.session.query(Links).filter(and_(Links.strategy_id==sid, Links.link==url)).one_or_none()
        if q:
            logging.info('Already have the link. No new link created')
            return
        strat = Links( link=url, strategy_id = sid)

        ModelBase.session.add(strat)
        ModelBase.session.commit()
        ModelBase.session.close()

    @classmethod
    def getLinks(cls, name):
        '''Uses session created in getId'''
        sid = Strategy.getId(name)
        q = ModelBase.session.query(Links).filter_by(strategy_id=sid).all()
        return q

    @classmethod
    def removeLink(cls, name, url):
        '''Uses session created in getId'''
        sid = Strategy.getId(name)
        q = ModelBase.session.query(Links).filter_by(strategy_id=sid, link=url).one_or_none()
        if q:
            ModelBase.session.delete(q)
            ModelBase.session.commit()

    @classmethod
    def getAllLinks(cls):
        ModelBase.connect(new_session=True, db="structjourDb")
        session = ModelBase.session
        return session.query(Links).all()