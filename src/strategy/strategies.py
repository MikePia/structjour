'''
Manage strategy stuff

Created on April 30, 2019

@author: Mike Petersen
'''
import os
import sqlite3


class Strategy:
    '''
    Methods to retrieve, add and remove items ffrom the database for strategies
    '''


    def __init__(self, create=False):

        db = 'C:/python/E/structjour/src/strategy/t1.sqlite'
        if os.path.exists(db):
            print('yaya')
        self.conn = sqlite3.connect('C:/python/E/structjour/src/strategy/t1.sqlite')
        self.cur = self.conn.cursor()
        if create == True:
            self.createTables()

    def removeStrategy(self, name):
        cursor = self.conn.execute('''
            DELETE FROM strategy WHERE name = ?''', (name,) )
        return cursor.fetchone()

    def addStrategy(self, name, preferred=1):
        try:
            x = self.cur.execute('''INSERT INTO strategy(name, preferred)
	    			VALUES(?, ?)''', (name, 1))
        except sqlite3.IntegrityError as e:
            print(f'{name} already exists in DB. No action taken:', e)
            return
        except sqlite3.OperationalError as e:
            print('Close the database browser please:', e)
            return
        for xx in x:
            print(x)
        self.conn.commit()

    def getDescription(self, name):
        cursor = self.conn.execute('''
            select name, description from strategy 
	            Join description 
	            ON description.strategy_id = strategy.id 
	            AND name = ?''', (name))
        

    def getStrategy(self, name=None, sid=None):
        if name:
            cursor = self.conn.execute('''
            select name, preferred, description from strategy 
	            Join description 
	            ON description.strategy_id = strategy.id 
	            AND name = ?''', (name,))
        elif id:
            cursor = self.conn.execute('SELECT * FROM strategy WHERE id = ?', (sid,))
        return cursor

    def getStrategies(self):
        cursor = self.conn.execute('SELECT * FROM strategy')
        # for row in cursor:
        #     print(row)
        return(cursor)

    def dropTables(self):
        self.cur.execute('DROP TABLE IF EXISTS strategy')
        self.cur.execute('DROP TABLE IF EXISTS description')
        self.cur.execute('DROP TABLE IF EXISTS source')
        self.cur.execute('DROP TABLE IF EXISTS images')
        self.cur.execute('DROP TABLE IF EXISTS links')


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
    cur = t.getStrategies()
    # cur = t.getStrategy(name='Other')
    for row in cur:
        # print(row[0])
        print('name:', row[1], end='')
        # print(row[2])
        p = "" if row[3] == 1 else "Not preferred"
        print("  ", p)


if __name__ == '__main__':
    notmain()
