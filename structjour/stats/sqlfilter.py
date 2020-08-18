'''
This was the beginning of a sql query manager. It barely begins to do what sqlalchemy does so much better.
The directory has no __init__.py file so its not included in the setup build.
'''
# from structjour.colz.finreqcol import FinReqCol
import pandas as pd
import sqlite3
from structjour.thetradeobject import SumReqFields

from PyQt5.QtCore import QSettings


class WhereClause:
    def __init__(self, method, args):
        self.method = method
        self.args = args

    def getClause(self):
        return self.method(*self.args)


class DbFilter:
    def __init__(self, settings=None, db=None, db2=None):

        self.settings = settings if settings is not None else QSettings('zero_substance', 'structjour')
        self.db = db if db is not None else settings.value('tradeDb')
        self.db2 = db2 if db2 is not None else settings.value('structjourDb')
        self.wheres = []

    def query(self, table, wheres=None, fields=None):
        fields = fields if fields is not None else "*"
        q = f"Select {fields} from {table}"
        if wheres is not None:
            q += " WHERE "
        for i, w in enumerate(wheres):
            q += w.method(*w.args)
            if i < len(wheres) - 1:
                q += " AND "

        return q

    def getDynamicInterface(self):
        '''
        Get a list of names to dynamacally generate an interface for user input of arguments
        '''
        wheres = {'date': ['Datetime', whereDateTime, [pd.Timestamp, pd.Timestamp]],
                  'day': ['Day', whereDay, [pd.Timestamp, pd.Timestamp]],
                  'time': ['Time of day', whereTimeOfDay, [pd.Timestamp]],
                  'strat': ['Strategy', whereStrat, [str]]}
        return wheres

    def addWhere(self, where):
        self.wheres.append(where)

    def runQuery(self):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        # x = self.query('trade_sum', self.wheres)
        # print(x)
        cursor = cur.execute(self.query('trade_sum', self.wheres))
        cursor = cursor.fetchall()
        return cursor

    def getListOfStrat(self):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cursor = cur.execute('''SELECT DISTINCT Strategy From Trade_sum Order By Strategy''')
        cursor = cursor.fetchall()
        return [x[0] for x in cursor]

    def getListOfPreferredStrats(self):
        conn = sqlite3.connect(self.db2)
        cur = conn.cursor()
        cursor = cur.execute('''SELECT name FROM strategy WHERE preferred = 1 Order By name''')
        cursor = cursor.fetchall()
        return [x[0] for x in cursor]


def whereDateTime(before=None, after=None):
    sf = SumReqFields()
    s = ''
    if before is not None:
        d = pd.Timestamp(before)
        dbef = d.strftime('%Y%m%d')
        tbef = d.strftime('%H:%M:%S')
        s = f'{sf.date} >= "{dbef}" AND {sf.start} >= "{tbef}"'
        if after is not None:
            s += ' AND '
    if after is not None:
        d = pd.Timestamp(after)
        daft = d.strftime('%Y%m%d')
        taft = d.strftime('%H:%M:%S')
        s += f'{sf.date} <= "{daft}" and {sf.start} <= "{taft}"'
    return s


def whereStrat(strategy):
    strategy = "" if strategy is None else strategy
    s = f'Strategy = "{strategy}"'
    return s


def whereDay(after=None, before=None):
    '''
    Return a WHERE clause for dates of a trade.  If both parameters are None, return an empty string
    :params after: Timestamp or str. The earliest day of a trade.
    :params before: Timestamp or str. The latest day of a trade.
    :return: A where clause for earliest and/or latest day of a trade.
    '''
    sf = SumReqFields()
    s = ''
    if before is not None:
        d = pd.Timestamp(before)
        dbef = d.strftime('%Y%m%d')
        s = f'{sf.date} <= {dbef}'
        if after is not None:
            s += ' AND '
    if after is not None:
        d = pd.Timestamp(after)
        daft = d.strftime('%Y%m%d')
        s += f'{sf.date} >= {daft}'
    return s


def whereTimeOfDay(bstart=None, estart=None):
    '''
    Return a WHERE clause for the start time of a trade.  If both parameters are None, return an empty string
    :params bstart: Timestamp or str. The earliest time of day to start
    :params estart: Timestamp or str. The latest time of day to start
    :return: A where clause for beginning and/or end start time
    '''
    sf = SumReqFields()
    s = ''
    if bstart is not None:
        d = pd.Timestamp(bstart)
        dstart = d.strftime("%H:%S:%M")
        s = f'{sf.start} >= {dstart}'
        if estart is not None:
            s += ' AND'
    if estart is not None:
        d = pd.Timestamp(estart)
        dstart = d.strftime("%H:%S:%M")
        s = f'{sf.start} <= {dstart}'

    return s


def wherePnL(boolstring):
    '''
    boolstring must start with one of: > < = <= <= !=
    TODO: Consider an Enum to generate an interface that restricts the possibilities using wherePnL(op:operator, val:int)
    '''
    return f'PnL {boolstring}'


from enum import Enum


class operator(Enum):
    GT = ">"
    GE = '>='
    LT = '<'
    LE = '<='
    ET = '='
    NE = '!='


def example():
    for vals in operator.__members__:
        print(operator[vals])

    print('Member of class operator: ', isinstance(operator.GE, operator))
    print('Member of class Enum: ', isinstance(operator.GE, Enum))


def local():
    dbf = DbFilter(settings=QSettings('zero_substance', 'structjour'))
    # for strat in dbf.getListOfPreferredStrats():
    for strat in dbf.getListOfStrat():
        qdbf = DbFilter(settings=QSettings('zero_substance', 'structjour'))

        # qdbf.addWhere(WhereClause(whereDateTime, ['20200101 07:30:00', '20200201 19:00:00']))
        qdbf.addWhere(WhereClause(whereStrat, [strat]))
        x = qdbf.runQuery()
        strat = 'None' if strat is None else strat
        print('{0:25s}: {1:5d}'.format(strat, len(x)), end='')
        
        qdbf.addWhere(WhereClause(wherePnL, ["> 0"]))
        x = qdbf.runQuery()
        print(f'     {len(x)} were winners')


def notmain():
    dbf = DbFilter(settings=QSettings('zero_substance', 'structjour'))
    dbf.addWhere(WhereClause(whereDateTime, ['20190101 07:30:00', '20200201 19:00:00']))
    dbf.addWhere(WhereClause(whereStrat, ['Momentum']))
    x = dbf.runQuery()
    # x = dbf.getListOfStrat()
    print(x)


if __name__ == '__main__':
    # checkit()
    # notmain()
    local()
    # example()
