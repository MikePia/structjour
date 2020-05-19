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
sqlalchemy models for trade tables

@author: Mike Petersen
@creation_date: April 17, 2020
'''


from collections import OrderedDict
import logging
import pandas as pd
from sqlalchemy import (Table, Integer, Text, Column, String, Boolean, Float, ForeignKey,
                        CheckConstraint, func, desc)
from sqlalchemy.orm import relationship
from structjour.models.meta import Base, ModelBase
# from .meta import Base, ModelBase


trade_sum_tags = Table('trade_sum_tags', Base.metadata,
        Column('tags_id', ForeignKey('tags.id'), primary_key=True),
        Column('trade_sum_id', ForeignKey('trade_sum.id'), primary_key=True))


class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    active = Column(Boolean)

    trade_sums = relationship('TradeSum',
                              secondary=trade_sum_tags,
                              back_populates='tags')

    def __repr__(self):
        return f"<Tags({self.name}: active={self.active})>"

    @classmethod
    def getTags(cls):
        '''select *'''
        ModelBase.connect(new_session=True)
        return ModelBase.session.query(Tags).all()

    @classmethod
    def addTag(cls, tag_name):
        '''
        Use only this method to add tags in order to format them uniformly
        :params session:
        :params tag: A Tags object
        '''
        ModelBase.connect(new_session=True)
        session = ModelBase.session
        tag_name = ' '.join([x.capitalize() for x in tag_name.split()])
        tag = Tags(name=tag_name, active=1)
        try:
            session.add(tag)
            session.commit()
        except Exception as ex:
            msg = f'Error while adding tag "{tag.name}": {type(ex)}'
            print(msg)
            session.rollback()

    @classmethod
    def setActive(cls, active, tag_id=None, tag_name=None):
        '''
        :params active: Boolean
        :params tag_id: Either id or name must be given
        :params tag_name:
        '''
        assert tag_id is not None or tag_name is not None
        ModelBase.connect(new_session=True)
        if tag_id:
            q = ModelBase.session.query(Tags).filter_by(id=tag_id).one()
        else:
            q = ModelBase.session.query(Tags).filter_by(name=tag_name).one()
        q.active = active
        ModelBase.session.commit()
    #     ModelBase.session.close()


class TradeSum(Base):
    __tablename__ = 'trade_sum'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    strategy = Column(String)
    link1 = Column(String)
    account = Column(String)
    pnl = Column(Float)
    start = Column(String, nullable=False)
    date = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    shares = Column(String, nullable=False)
    mktval = Column(Float, nullable=False)
    target = Column(Float)
    targdiff = Column(Float)
    stoploss = Column(Float)
    sldiff = Column(Float)
    rr = Column(String(32))
    realrr = Column(Float(32))
    maxloss = Column(Float)
    mstkval = Column(Float)
    mstknote = Column(String)
    explain = Column(String)
    notes = Column(String)
    clean = Column(Text)

    tags = relationship('Tags',
                        secondary=trade_sum_tags,
                        back_populates='trade_sums')

    @classmethod
    def append_tag(cls, trade_sum_id, tag_name=None, tag_id=None):
        if (tag_name is None and tag_id is None):
            return
        ModelBase.connect(new_session=True)
        sess = ModelBase.session
        try:
            assert isinstance(trade_sum_id, int)
            if tag_id:
                assert isinstance(tag_id, int)
                tag = sess.query(Tags).filter_by(id=tag_id).one()
            else:
                tag = sess.query(Tags).filter_by(name=tag_name).one()

            trade = sess.query(TradeSum).filter_by(id=trade_sum_id).one()

            trade.tags.append(tag)
            sess.add(trade)
            sess.commit()
        except Exception as ex:
            msg = f'Failed to connect tag. Exception: {type(ex)}'
            logging.error(msg)
            logging.error(ex)
            sess.rollback()
        sess.close()

    @classmethod
    def release_tag(cls, trade_sum_id, tag_name=None, tag_id=None):
        if (tag_name is None and tag_id is None):
            return
        ModelBase.connect(new_session=True)
        sess = ModelBase.session
        try:
            assert isinstance(trade_sum_id, int)
            if tag_id:
                tag = sess.query(Tags).filter_by(id=tag_id).one()
            else:
                tag = sess.query(Tags).filter_by(name=tag_name).one()

            trade = sess.query(TradeSum).filter_by(id=trade_sum_id).one()
            for atag in trade.tags:
                if atag is tag:
                    trade.tags.remove(tag)
                    sess.commit()
                    break
        except Exception as ex:
            print(type(ex))
        sess.close()

    @classmethod
    def remove_tag(cls, tag_id=None, tag_name=None):
        '''
        Remove the associataion between the given tag and TradeSums
        :params tag_id: int. Either tag_id or tag_name must have a value or method does nothing
        :params tag_name: str
        '''
        if (tag_name is None and tag_id is None):
            return
        try:
            ModelBase.connect(new_session=True)
            sess = ModelBase.session
            if tag_id:
                t = ModelBase.session.query(Tags).filter_by(id=tag_id).one()
            else:
                t = ModelBase.session.query(Tags).filter_by(name=tag_name).one()

            sess.delete(t)
            sess.commit()
        except Exception as ex:
            msg = f'Failed to disconnect tag. Exception: {type(ex)}'
            logging.error(msg)
            sess.rollback()
        sess.close()

    @classmethod
    def getTags(cls, tsum_id):
        '''
        :params tsum_id: int. numpy types may fail(e.g. numpy.int64 fails in filter_by)
        '''
        ModelBase.connect(new_session=True)

        q = ModelBase.session.query(TradeSum).filter_by(id=tsum_id).first()
        return q.tags if q else []

    @classmethod
    def getNamesAndProfits(cls, daDate):
        '''
        :params daDate: A date string in the form yyyymmdd as it is held in the db
        :return: an OrderedDict with keys for the account alias names as held in TradeSum (Currently Live and SIM).
            The values are lists of pnl for the trades on the given date
        '''
        ModelBase.connect(new_session=True)
        names = OrderedDict()
        pnls = OrderedDict()
        for acct in list(ModelBase.session.query(TradeSum.account).distinct().all()):
            q = ModelBase.session.query(TradeSum).filter_by(date=daDate).filter_by(account=acct[0]).order_by(TradeSum.start).all()
            names[acct[0]] = [t.name for t in q]
            pnls[acct[0]] = [t.pnl for t in q]

        return names, pnls

    @classmethod
    def getDistinctStrats(cls):
        '''
        Get a list of the strategies that are in use and the number of trades that use them.
        :return: A python list of tuples (name, count). The name could be ''. Unlike the sql verion
        it does not match the count for NULL or None.
        '''
        ModelBase.connect(new_session=True)
        qq = ModelBase.session.query(TradeSum.strategy, func.count(
                                     TradeSum.strategy)).group_by(
                                     TradeSum.strategy).order_by(
                                     desc(func.count(TradeSum.strategy))).all()
        return qq

    @classmethod
    def getAccounts(cls):
        '''
        Retrieve a list of all accounts that have trades. The entries in the table are account aliases
        :return list<str> of accounts
        '''
        ModelBase.connect(new_session=True)
        q = ModelBase.session.query(TradeSum.account).distinct().all()
        print()
        return [x[0] for x in q]


class Trade(Base):
    __tablename__ = "ib_trades"
    id = Column(Integer, primary_key=True)
    symb = Column(String(10), nullable=False)
    datetime = Column(String(15), nullable=False)
    qty = Column(Integer, CheckConstraint('qty != 0'), nullable=False)
    balance = Column(Integer)
    price = Column(Float, nullable=False)
    average = Column(Float)
    pnl = Column(Float)
    commission = Column(Float)
    oc = Column(String(5))
    das = Column(String(12))
    ib = Column(String(12))
    account = Column(String(56), nullable=False)
    trade_sum_id = Column(Integer, ForeignKey('trade_sum.id'))

    tradesum = relationship('TradeSum', back_populates='ib_trades')

    def __repr__(self):
        return f"<Trade(Symb={self.symb}: Qty={self.qty}: Date={self.datetime})>"

    @classmethod
    def getIntradayTrades(cls, daDate):
        '''
        Retrive all the transactions from a single day
        :params daDate: A time string, datetime or pd.Timestamp
        :return: All the ib_trades transactions in a dict with the account(s) as key(s).
        The keys are the actual account numbers
        '''
        ModelBase.connect(new_session=True)

        daDate1 = pd.Timestamp(daDate).to_pydatetime()
        daDate2 = daDate1 + pd.Timedelta(days=1)
        # sdaDate = daDate.strftime("%Y%m%d")
        pnls = {}
        for account in list(ModelBase.session.query(Trade.account).distinct().all()):
            q = ModelBase.session.query(Trade).filter_by(account=account[0]).filter(
                Trade.datetime > daDate1.strftime("%Y%m%d")).filter(
                Trade.datetime < daDate2.strftime("%Y%m%d")).order_by(Trade.datetime).all()
            if q:
                pnls[account[0]] = q
        return pnls

    @classmethod
    def getAccounts(cls):
        '''
        Retrieve a list of all accounts that have trades. The entries in the table are actual account numbers
        '''
        ModelBase.connect(new_session=True)
        q = ModelBase.session.query(Trade.account).distinct().all()
        print()
        return [x[0] for x in q]


TradeSum.ib_trades = relationship("Trade", order_by=Trade.datetime, back_populates="tradesum")

# ==================== Proof of concept methods-- will generlly be used in Test_Trademodels_MODEL modules ===========


def removeTag():
    '''local proof of concept'''

    try:
        TradeSum.remove_tag(1)
        TradeSum.remove_tag(2)
        TradeSum.remove_tag(3)
        TradeSum.remove_tag(4)
        TradeSum.remove_tag(5)
        TradeSum.remove_tag(6)
        TradeSum.remove_tag(7)
        TradeSum.remove_tag(8)
        TradeSum.remove_tag(9)
        TradeSum.remove_tag(10)
        TradeSum.remove_tag(11)
    except Exception:
        pass


def setActive():
    Tags.setActive(False, tag_id=4)


def appendTags():
    '''local proof of concept stuff'''
    ModelBase.connect(new_session=True)
    trades = ModelBase.session.query(TradeSum).filter(TradeSum.date > "20200131").all()
    tags = ModelBase.session.query(Tags).all()
    print(len(trades), len(tags))
    for i, trade in enumerate(trades):
        # print(f'({trade.id}, {tags[i%11].id}), ', end='')
        TradeSum.append_tag(trade_sum_id=trade.id, tag_id=tags[i % 11].id)
        TradeSum.append_tag(trade_sum_id=trade.id, tag_id=tags[(i + 7) % 11].id)


def releaseTags():
    TradeSum.release_tag(1199, tag_id=10)


def addTags():
    '''local proof of concept stuff'''
    tags = [
            'Well rested',
            'anxious',
            'Cloudy',
            'FOMO',
            'greed',
            'Hot key error',
            'tired',
            'confident',
            'not confident',
            'hesitant',
            'over confident']

    for t in tags:
        Tags.addTag(t)


def getTagsFromTradeSum():
    '''local proof of concept stuff'''

    tags = TradeSum.getTags(1209)
    for tag in tags:
        print(tag.name)


def getTags():
    '''local proof of concept stuff'''
    for tag in Tags.getTags():
        print(tag.name)


def getIntraStuff():
    pnldict = Trade.getIntradayTrades('20200407')
    print(pnldict)
    print()


def getStrategyStuff():
    q = TradeSum.getDistinctStrats()
    for i, qq in enumerate(q):
        print(i + 1, qq)
    print()


def getTradeSumAccounts():
    q = TradeSum.getAccounts()
    print(q)


def dostuff():
    # ModelBase.connect()
    # ModelBase.createAll()

    # addTags()
    # appendTags()
    # releaseTags()
    # setActive()
    # getTagsFromTradeSum()
    # getTags()
    # removeTag()

    # getIntraStuff()
    getTradeSumAccounts()
    # getStrategyStuff()


def notmain():
    names, profits = TradeSum.getNamesAndProfits('20200204')
    print(names)
    print(profits)


if __name__ == '__main__':
    dostuff()
    # notmain()
