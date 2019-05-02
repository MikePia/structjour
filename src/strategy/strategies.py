'''
Manage strategy stuff

Created on April 30, 2019

@author: Mike Petersen
'''
import os
import sqlite3
from strategy.strat import TheStrategyObject

# pylint: disable = C0103


class Strategy:
    '''
    Methods to retrieve, add and remove items ffrom the database for strategies
    '''


    def __init__(self, create=False, db='C:/python/E/structjour/src/strategy/t1.sqlite'):

        if not os.path.exists(db):
            msg = 'No db listed-- do we recreate the default and add a setting?'
            raise ValueError(msg)
        self.conn = sqlite3.connect('C:/python/E/structjour/src/strategy/t1.sqlite')
        self.cur = self.conn.cursor()
        if create:
            self.createTables()

    def getConnection(self):
        return self.conn

    def removeStrategy(self, name):
        '''Remove the strategy entry matched by name'''
        cursor = self.conn.execute('''
            DELETE FROM strategy WHERE name = ?''', (name,))
        return cursor.fetchone()

    def addStrategy(self, name, preferred=1):
        '''Add the strategy name to table strategy'''
        try:
            x = self.cur.execute('''INSERT INTO strategy(name, preferred)
	    			VALUES(?, ?)''', (name, preferred))
        except sqlite3.IntegrityError as e:
            print(f'{name} already exists in DB. No action taken:', e)
            return
        except sqlite3.OperationalError as e:
            print('Close the database browser please:', e)
            return
        self.conn.commit()
        return x

    def getStrategy(self, name=None, sid=None):
        '''Get the strategy using id or name'''
        if name:
            cursor = self.conn.execute('''
            select name, preferred from strategy 
	            WHERE name = ?''', (name,))
        elif sid:
            cursor = self.conn.execute('SELECT * FROM strategy WHERE id = ?', (sid,))
        return cursor.fetchone()

    def getDescription(self, name):
        '''Get the description for strategy.name'''
        cursor = self.conn.execute('''SELECT strategy.name, description.description FROM strategy
            LEFT OUTER JOIN description 
            ON strategy.id = description.strategy_id 
            WHERE name = ?''', (name, ))
        return cursor.fetchone()


    def getStrategies(self):
        cursor = self.conn.execute('SELECT * FROM strategy')
        return(cursor.fetchall())

    def dropTables(self):
        self.cur.execute('DROP TABLE IF EXISTS strategy')
        self.cur.execute('DROP TABLE IF EXISTS description')
        self.cur.execute('DROP TABLE IF EXISTS source')
        self.cur.execute('DROP TABLE IF EXISTS images')
        self.cur.execute('DROP TABLE IF EXISTS links')

    def loadDefault(self):
     #####

        #  These three entries are required before adding any strategies
        # I should not have to supply the ID but I get this error without:
        # Incorrect number of bindings supplied. The current statement uses 1, and there are 13 supplied.
        entries = ['default', 'user', 'contrib']
        for i in range(len(entries)):
            self.cur.execute('''INSERT INTO source (id, datasource)
                        VALUES(?, ?)''',
                        (i+1, entries[i]))

        tso = TheStrategyObject()
        for strat, count in zip(tso.s1, range(len(tso.s1))):
            count = count + 1
            if len(strat) > 1:
                self.cur.execute('''INSERT INTO strategy(id, name, short_name, preferred)
                        VALUES(?, ?, ?, ?)''',
                            (count, strat[0], strat[1], 1))
            else:
                self.cur.execute('''INSERT INTO strategy(id, name, preferred)
                        VALUES(?, ?, ?)''',
                            (count, strat[0], 1))

        self.cur.execute('SELECT id FROM source WHERE datasource = ?', ('default',))
        source_id = self.cur.fetchone()[0]
        # cur.execute('SELECT id FROM strategy WHERE name = ?', ('default',))
        self.conn.commit()

        for key, count in zip(tso.strats.keys(), range(len(tso.strats.keys()))):
            self.cur.execute('SELECT id FROM strategy WHERE name = ?', (key,))
            print(key)
            strategy_id = self.cur.fetchone()[0]
            self.cur.execute('''INSERT INTO description(id, description, source_id, strategy_id)
                            VALUES(?, ?, ?, ?)''',
                        (count, tso.strats[key][1], source_id, strategy_id))
            # print(count, key, tso.strats[key])
        self.conn.commit()



    def createTables(self):
        self.cur.execute('''
        CREATE TABLE strategy (
            id	integer,
            name	text UNIQUE,
            short_name	text,
            preferred	INTEGER,
            PRIMARY KEY(id)
        );''')

        self.cur.execute('''
        CREATE TABLE source (
            id integer PRIMARY KEY,
            datasource text
        );''')

        self.cur.execute('''
        CREATE TABLE description (
            id integer PRIMARY KEY,
            description text,
            source_id integer,
            strategy_id integer,
            FOREIGN KEY (source_id) REFERENCES source(id),
            FOREIGN KEY (strategy_id) REFERENCES strategy(id)
        );''')

        self.cur.execute('''
        CREATE TABLE images (
            id integer PRIMARY KEY,
            image text,
            source_id integer,
            strategy_id integer,
            FOREIGN KEY (source_id) REFERENCES source(id),
            FOREIGN KEY (strategy_id) REFERENCES strategy(id)
        );''')

        self.cur.execute('''
        CREATE TABLE links (
            id integer PRIMARY KEY,
            link text,
            strategy_id integer,
            FOREIGN  KEY (strategy_id) REFERENCES strategy(id)
        );''')
        self.conn.commit()

    

def notmain():
    t = Strategy()
    # x = t.getDescription('Fallen Angel')
    t.dropTables()
    t.createTables()
    t.loadDefault()


if __name__ == '__main__':
    notmain()
