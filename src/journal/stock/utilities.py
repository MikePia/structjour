'''
Local utility functions shared by some stock modules and test code.

@author: Mike Petersen

@creation_date: 2019-01-17
'''

import datetime as dt
from collections import OrderedDict
import os
import random
import sqlite3

import numpy as np
import pandas as pd
from PyQt5.QtCore import QSettings

# pylint: disable = C0103

def getMAKeys():
    cc1 = ['chart1ma1', 'chart1ma2', 'chart1ma3', 'chart1ma4', 'chart1vwap', 'chart1ma1spin',
          'chart1ma2spin', 'chart1ma3spin', 'chart1ma4spin', 'chart1ma1color', 'chart1ma2color',
          'chart1ma3color', 'chart1ma4color', 'chart1vwapcolor']
    cc2 = ['chart2ma1', 'chart2ma2', 'chart2ma3', 'chart2ma4', 'chart2vwap', 'chart2ma1spin',
          'chart2ma2spin', 'chart2ma3spin', 'chart2ma4spin', 'chart2ma1color', 'chart2ma2color',
          'chart2ma3color', 'chart2ma4color', 'chart2vwapcolor']
    cc3  =['chart3ma1', 'chart3ma2', 'chart3ma3', 'chart3ma4', 'chart3vwap', 'chart3ma1spin',
          'chart3ma2spin', 'chart3ma3spin', 'chart3ma4spin', 'chart3ma1color', 'chart3ma2color',
          'chart3ma3color', 'chart3ma4color', 'chart3vwapcolor']
    return cc1, cc2, cc3

def getMASettings():
    chartSet = QSettings('zero_substance/chart', 'structjour')
    mas = chartSet.value('getmas', list)
    maDict = OrderedDict()
    for ma in mas[0]:
        maDict[ma[1]] = [ma[0], ma[2]]
    vwap = []
    if mas[1]:
        vwap.append(['vwap', mas[1][1]])

    return maDict, vwap

def vwap(df, bd=None):
    '''
    I believe the standard version of vwap begins at open and does not include previous MA stuff.
    I retrieved the algo from an SO post. Thankyou for that

    '''
    if not bd:
        # If no day is given, use the end day in df
        bd = df.index[-1]
        bd = pd.Timestamp(bd.year, bd.month, bd.day)
    begin = pd.Timestamp(bd.year, bd.month, bd.day, 9, 30, 0)

    dfv = df.copy(deep=True)
    if begin > df.index[0]:
        dfv = dfv.loc[dfv.index >= begin]

    dfv['Cum_Vol'] = dfv['volume'].cumsum()
    dfv['Cum_Vol_Price'] = (dfv['volume'] * (dfv['high'] + dfv['low'] + dfv['close'] ) /3).cumsum()
    dfv['VWAP'] = dfv['Cum_Vol_Price'] / dfv['Cum_Vol']
    return dfv['VWAP']

def movingAverage(values, df, beginDay=None):
    '''
    Creates a dictionary of moving averages based settings values. All window values in 
    chartSettings will be processed. Returns a dict of MA: SMA for windows of 20 or less
    and EMA for windows greater than 20, and it always process and returns VWAP.
    :values:
    :return: A tuple (maDict, vwap). Keys for maDict are the window val
    '''
    mas = getMASettings()
    windows = list()
    windows = list(mas[0].keys())


    maDict = OrderedDict()

    for ma in windows:
        if ma > 20:

            weights = np.repeat(1.0, ma)/ma
            smas = np.convolve(values, weights, 'valid')
            maDict[ma] = smas
            maDict[ma] = pd.DataFrame(maDict[ma])
            try:
                maDict[ma].index = df.index[ma-1:]
            except ValueError:
                del maDict[ma]
        else:
            dataframe = pd.DataFrame(values)
            dfema = df['close'].ewm(span=ma, adjust=False, min_periods=ma, ignore_na=True).mean()
            maDict[ma] = dfema
            maDict[ma].index = df.index
    if mas[1]:
        maDict['vwap'] = vwap(df, beginDay)


    return maDict

def makeupEntries(df, minutes):
    start = df.index[0]
    end = df.index[-1]
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    entries = []
    for i in range(random.randint(0, 5)):
        # Make up an entry time
        delta = end - start
        sec = delta.total_seconds()
        earliest = int(sec//10)
        latest = int(sec-earliest)
        secs = random.randint(earliest, latest)
        entry = start + pd.Timedelta(seconds=secs)

        # Figure the candle index for our made up entry
        diff = entry - start
        candleindex = int(diff.total_seconds()/60//minutes)

        #Get the time index of the candle
        # tix = df.index[candleindex]

        # Set a random buy or sell
        side = 'B' if random.random() > .5 else 'S'

        # Set a random price within the chosen candle
        high = df.iloc[candleindex].high
        low = df.iloc[candleindex].low
        price = (random.random() * (high - low)) + low
        
        # [price, candle, side, entry]
        entries.append([price, candleindex, side, entry])

    return entries

def getLastWorkDay(d=None):
    '''
    Retrieve the last biz day from today or from d if the arg is given. Holidays are ignored
    :params d: A datetime object.
    :return: A datetime object of the last biz day.
    '''
    now = dt.datetime.today() if not d else d
    deltDays = 0
    if now.weekday() > 4:
        # deltDays = now.weekday() - 4
        # Just todauy TODO
        # if now.weekday() == 5:
        #     bizday = bizday -dt.timedelta(days=1)
        # elif now.weekday() == 6:
        #     bizday = bizday -dt.timedelta(days=2)

        deltDays = now.weekday() - 4
    bizday = now - dt.timedelta(deltDays)
    return bizday

def getPrevTuesWed(td):
    '''
    Utility method to get a probable market open day prior to td. The least likely
    closed days are Tuesday and Wednesday. This will occassionally return  a closed
    day but wtf.
    :params td: A Datetime object
    '''
    deltdays = 7
    if td.weekday() == 0:
        deltdays = 5
    elif td.weekday() < 3:
        deltdays = 0
    elif td.weekday() < 5:
        deltdays = 2
    else:
        deltdays = 4
    before = td - dt.timedelta(deltdays)
    return before

class ManageKeys:
    def __init__(self, create=False, db=None):
        self.settings = QSettings('zero_substance', 'structjour') 
        self.apiset = QSettings('zero_substance/stockapi', 'structjour')
        self.db = db
        if not self.db:
            self.setDB()
        
        if create and self.db:
            self.createTables()


    def setDB(self, db=None):
        '''
        Set the location of the sqlite db file. Its placed in the apiset but could belong in
        settings. The db does not seem to have a natural place to be excluded from.
        Arbitrarily, its in apiset only. (apiset 'belongs' to the stockapi, but the db has a range
        of things beyond that).
        '''
        o = self.settings.value('journal')
        if not o:
            msg = '\nWARNING: Trying to set the db location.'
            msg = msg +  '\nPlease set the location of your journal directory.\n'
            print(msg)
            return
        self.db = os.path.join(o, 'structjour.sqlite')
        self.apiset.setValue('dbsqlite', self.db)

        if not os.path.exists(self.db):
            msg = 'No db listed-- do we recreate the default and add a setting?- or maybe pop and get the db address'
            # self.createTables()
            # raise ValueError(msg)
    
    def createTables(self):
        '''
        Creates the api_keys if it doesnt exist then adds a row for each api that requires a key
        if they dont exist
        '''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE if not exists api_keys (
            id	INTEGER PRIMARY KEY AUTOINCREMENT,
            api	TEXT NOT NULL UNIQUE,
            key	TEXT);''')
        conn.commit()

        cur.execute('''
            SELECT api from api_keys WHERE api = ?;''', ("bc",))

        cursor = cur.fetchone()
        if not cursor:
            cur.execute('''
                INSERT INTO api_keys(api)VALUES(?);''', ("bc",))

        cur.execute('''
            SELECT api from api_keys WHERE api = ?;''', ("av",))

        cursor = cur.fetchone()
        if not cursor:
            cur.execute('''
                INSERT INTO api_keys(api)VALUES(?);''', ("av",))
        conn.commit()

    def updateKey(self, api, key):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''UPDATE api_keys
            SET key = ?
            WHERE api = ?''', (key, api))
        conn.commit()

    def getKey(self, api):
        if not self.db:
            return
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute('''SELECT key
            FROM api_keys
            WHERE api = ?''', (api, ))
        k = cur.fetchone()
        if k:
            return k[0]
        return k



 


    def getDB(self):
        '''Get the file location of the sqlite database'''
        db = self.apiset.value('dbsqlite')
        if not db:
            print('WARNING: Trying to retrieve db location, the database file location is not set.')
        return db


class IbSettings:
    def __init__(self):
        self.apiset = QSettings('zero_substance/stockapi', 'structjour')
        p = self.apiset.value('APIPref')
        if p:
            p = p.replace(' ', '')
            self.preferences = p.split(',')
        else:
            self.preferences = ['ib', 'bc', 'av', 'iex']
        self.setIbStuff()


    def setIbStuff(self):
        pref = self.preferences
        self.ibPort = None
        self.ibId = None
        if 'ib' in pref:
            ibreal = self.apiset.value('ibRealCb', False, bool)
            ibPaper = self.apiset.value('ibPaperCb', False, bool)
            ibpref = self.apiset.value('ibPref')
            if ibreal:
                self.ibPort = self.apiset.value('ibRealPort', 7496, int)
                self.ibId = self.apiset.value('ibRealId', 7878, int)
            elif ibPaper:
                self.ibPort = self.apiset.value('ibPaperPort', 4001, int)
                self.ibId = self.apiset.value('ibPaperId', 7979, int)

    def getIbSettings(self):
        #TODO abstrast host like port and id-- set it in the stockapi dialog
        if not self.ibPort or not self.ibId:
            return None
        d = {'port': self.ibPort,
                'id': self.ibId,
                'host': '127.0.0.1'}
        return d



def notmain():
    # mk = ManageKeys(create=True, db='C:\\python\\E\\structjour\\src\\test\\testdb.sqlite')
    # mk.updateKey('bc', '''That'll do pig''')
    # mk.updateKey('av', '''That'll do.''')
    # print(mk.getKey('bc'))
    # print(mk.getKey('av'))
    print(getMASettings())
    movingAverage(None, None, None)

def localstuff():
    settings = QSettings('zero_substance', 'structjour') 
    apiset = QSettings('zero_substance/stockapi', 'structjour')
    setkeys = settings.allKeys()
    apikeys = apiset.allKeys()
    setval=list()
    apival=list()
    for k in setkeys:
        setval.append(settings.value(k))
    for k in apikeys:
        apival.append(apiset.value(k))


if __name__ == '__main__':
    notmain()
    # localstuff()
