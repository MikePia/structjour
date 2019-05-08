'''
Local utility functions shared by some stock modules and test code.

@author: Mike Petersen

@creation_date: 2019-01-17
'''
import os
import datetime as dt
import sqlite3

from PyQt5.QtCore import QSettings
# pylint: disable = C0103

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
        deltDays = now.weekday() - 3
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
        if 'ib' in pref:
            ibreal = self.apiset.value('ibRealCb', False, bool)
            ibPaper = self.apiset.value('ibPaperCb', False, bool)
            ibpref = self.apiset.value('ibPref')
            self.ibPort = None
            self.ibId = None
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
    mk = ManageKeys(create=True, db='C:\\python\\E\\structjour\\src\\test\\testdb.sqlite')
    mk.updateKey('bc', '''That'll do pig''')
    mk.updateKey('av', '''That'll do.''')
    print(mk.getKey('bc'))
    print(mk.getKey('av'))

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

    print()

if __name__ == '__main__':
    # notmain()
    localstuff()


