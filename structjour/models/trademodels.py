import logging
from sqlalchemy import (Table, Integer, Text, Column, String, Boolean, Float, ForeignKey)
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
        return q.tags


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


def dostuff():
    # ModelBase.connect()
    # ModelBase.createAll()

    addTags()
    appendTags()
    # releaseTags()
    # setActive()
    # getTagsFromTradeSum()
    # getTags()
    # removeTag()


if __name__ == '__main__':
    dostuff()
