# from structjour.colz.finreqcol import FinReqCol
import pandas as pd

from structjour.thetradeobject import SumReqFields

from PyQt5.QtCore import QSettings


class WhereClause:
    def __init__(self, method, args):
        self.method = method
        self.args = args

    def getClause(self):
        return self.method(*self.args)


class DbFilter:
    def __init__(self, settings=None, db=None):

        self.settings = settings if settings is not None else QSettings('zero_substance', 'structjour')
        self.db = db if db is not None else settings.value('tradeDb')

    def query(self, wheres=None):
        q = "Select * from trade_sum"
        if wheres is not None:
            q += " WHERE "
        for w in wheres:
            q += w.method(*w.args)

        return q


def whereDateTime(before=None, after=None):
    sf = SumReqFields()
    s = ''
    if before is not None:
        d = pd.Timestamp(before)
        dbef = d.strftime('%Y %m%d')
        tbef = d.strftime('%H:%M:%S')
        s = f'{sf.date} <= {dbef} AND {sf.start} <= {tbef}'
        if after is not None:
            s += ' AND '
    if after is not None:
        d = pd.Timestamp(after)
        daft = d.strftime('%Y%m%d')
        taft = d.strftime('%H:%M:%S')
        s += f'{sf.date} >= {daft} and {sf.start} >= {taft}'
    return s


def whereDay(before=None, after=None):
    sf = SumReqFields()
    s = ''
    if before is not None:
        d = pd.Timestamp(before)
        dbef = d.strftime('%Y %m%d')
        s = f'{sf.date} <= {dbef}'
        if after is not None:
            s += ' AND '
    if after is not None:
        d = pd.Timestamp(after)
        daft = d.strftime('%Y%m%d')
        s += f'{sf.date} >= {daft}'
    return s


def whereTimeOfDay():
    pass


if __name__ == '__main__':
    dbf = DbFilter(settings=QSettings('zero_substance', 'structjour'))
    wheres = []

    wheres.append(WhereClause(whereDateTime, ['20200101 07:30:00', '20200201 19:00:00']))
    print(dbf.query(wheres))
