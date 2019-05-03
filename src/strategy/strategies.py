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
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        if create:
            self.createTables()

    def setLink(self, key, url):
        sid = self.getId(key)
        
        self.conn.execute('''INSERT INTO links (link, strategy_id)
            VALUES(?, ?)''', (url, sid))
        self.conn.commit()

    def getLinks(self, key):
        sid = self.getId(key)
        
        cursor = self.conn.execute('''SELECT link FROM links WHERE strategy_id  = ?''', (sid, ))
        x = cursor.fetchall()
        xlist = [z[0] for z in x]
        return xlist
        
    def removeLink(self, key, url):
        sid = self.getId(key)
        self.conn.execute('''delete from links where link = ? and strategy_id = ?''', (url, sid,))
        self.conn.commit()

    def removeImage(self, key, widget):
        x = self.getId(key)
        cursor = self.conn.execute('''DELETE FROM images
            WHERE strategy_id = ? AND widget = ?;''', (x, widget)    )


    def removeImage1(self, key):
        self.removeImage(key, 'chart1')

    def removeImage2(self, key):
        self.removeImage(key, 'chart2')

    def setImage(self, key, name, widget):
        '''
        Set the one image for chart1 or chart2 and the strategy key. The widget is constrained
        to either chart1 or chart2. Need to manually constrain only one (chart1, chart2) for each
        strategy (sqlite constraints with unique combination of cell contents?)
        '''
        print('setting', key, name)
        sid = self.getId(key)
        cursor = self.conn.execute('''SELECT name FROM images
            WHERE strategy_id = ? and widget = ?''', (sid, widget,))
        if cursor.fetchone():
            self.removeImage(key, widget)
        
        self.conn.execute('''INSERT INTO images (name, widget, strategy_id)
            VALUES(?, ?, ?)''', (name, widget, sid))
        self.conn.commit()

    def setImage1(self, key, name):
        self.setImage(key, name, 'chart1')

    def setImage2(self, key, name):
        self.setImage(key, name, 'chart2')

    def getImage(self, strat, widget):
        cursor = self.conn.execute('''SELECT images.name, strategy.id FROM images
            JOIN strategy
            ON strategy_id = strategy.id
            WHERE strategy.name=? AND widget = ? ''', (strat, widget))
        x = cursor.fetchone()
        if x:
            return x[0]
        else:
            return ''

    def getImage1(self, strat):
        return self.getImage(strat, 'chart1')

    def getImage2(self, strat):
        return self.getImage(strat, 'chart2')

    def getConnection(self):
        return self.conn

    def removeStrategy(self, name):
        '''Remove the strategy entry matched by name'''
        cursor = self.conn.execute('''
            DELETE FROM strategy WHERE name = ?''', (name,))
        return cursor.fetchone()

    def setPreferred(self, name, pref):
        x = self.cur.execute('''UPDATE strategy
            SET preferred = ?
            WHERE name = ?''', (0, name))
    def getId(self, name):
        cursor = self.conn.execute('''
            select id from strategy 
            WHERE name = ?''', (name, ))
        s = cursor.fetchone()
        return s[0] 



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

    def setDescription(self, name, desc):
        sid = self.getId(name)
        # Set source to user
        source = 2 
        cursor = self.conn.execute('''Select description from description
            WHERE strategy_id = ?''', (sid,))
        if not cursor.fetchone():
            self.conn.execute('''INSERT INTO description (description, source_id, strategy_id)
                VALUES(?, ?, ?)''', (desc, source,sid))
        else:
            self.conn.execute("""UPDATE description
                SET description=?, source_id=?
                WHERE strategy_id = ?""", (desc, source, sid))
        self.conn.commit()




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
            # print(key)
            strategy_id = self.cur.fetchone()[0]
            self.cur.execute('''INSERT INTO description(id, description, source_id, strategy_id)
                            VALUES(?, ?, ?, ?)''',
                        (count, tso.strats[key][1], source_id, strategy_id))
            # print(count, key, tso.strats[key])
        self.conn.commit()



    def createTables(self):
        self.cur.execute('''
        CREATE TABLE strategy (
	        id	INTEGER PRIMARY KEY AUTOINCREMENT,
            name	text UNIQUE,
            short_name	text,
            preferred	INTEGER DEFAULT 1);''')

        self.cur.execute('''
        CREATE TABLE source (
            id integer PRIMARY KEY,
            datasource text
        );''')

        self.cur.execute('''
        CREATE TABLE description (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description text,
            source_id integer,
            strategy_id INTEGER UNIQUE,
            FOREIGN KEY (source_id) REFERENCES source(id),
            FOREIGN KEY (strategy_id) REFERENCES strategy(id)
        );''')

        self.cur.execute('''
        CREATE TABLE images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            widget	INTEGER CHECK(widget="chart1" OR widget="chart2"),
            strategy_id	INTEGER,
            FOREIGN KEY(strategy_id) REFERENCES strategy(id)
        );''')

        self.cur.execute('''
        CREATE TABLE links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    x = t.getId('Fallen Angel')
    print(x)


if __name__ == '__main__':
    notmain()
