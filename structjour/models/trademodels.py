from sqlalchemy import (Table, Integer, Text, Column, String, Boolean, Float, ForeignKey)
from sqlalchemy.orm import relationship
from structjour.models.meta import Base


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
