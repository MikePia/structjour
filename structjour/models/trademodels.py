from sqlalchemy import (Table, Numeric, Integer, Text, Column, String, Boolean)
from structjour.models.meta import Base


def getTradeSumTable(metadata):
    return Table('trade_sum', metadata,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('Name', Text, nullable=False),
        Column('Strategy', Text),
        Column('Link1', Text),
        Column('Account', Text),
        Column('PnL', Numeric),
        Column('Start', Text, nullable=False),
        Column('Date', Text, nullable=False),
        Column('Duration', Text, nullable=False),
        Column('Shares', Integer, nullable=False),
        Column('MktVal', Numeric, nullable=True),
        Column('Target', Numeric),
        Column('TargDiff', Numeric),
        Column('StopLoss', Numeric),
        Column('SLDiff', Numeric),
        Column('RR', Numeric),
        Column('MaxLoss', Numeric),
        Column('MstkVal', Numeric),
        Column('MstkNote', Text),
        Column('Explain', Text),
        Column('Notes', Text),
        Column('clean', Text),
        Column('RealRR', Numeric),
        extend_existing=True
    )


class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    active = Column(Boolean)


# class TsumsTabs(Base):
#     id = Column(Integer, primary_key=True)
#     tags_id = Column(Integer, ForeignKey('tags.id'))
#     trade_sum_id = Column(Integer, ForeignKey('trade_sum.id'))


class TradeSum(Base):
    __tablename__ = 'trade_sum'
    id = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)
    strategy = Column(String)
    link1 = Column(String)
    account = Column(String)
    pnl = Column(Numeric)
    start = Column(String, nullable=False)
    date = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    shares = Column(Integer, nullable=False)
    mktVal = Column(Numeric, nullable=False)
    target = Column(Numeric)
    targDiff = Column(Numeric)
    stoploss = Column(Numeric)
    sldiff = Column(Numeric)
    rr = Column(Numeric)
    realrr = Column(Numeric)
    maxloss = Column(Numeric)
    mstkval = Column(Numeric)
    mstknote = Column(String)
    explain = Column(String)
    notes = Column(String)
    clean = Column()
