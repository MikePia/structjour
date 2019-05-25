# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

'''
This is a temporary version of this file. It loads the strategies entirely from The StrategyObject as the default
descriptions. Before release, and depending on if this is a webapp, Django, Drupal or standalone, do the right thing.
'''
import sqlite3
from strategy.strat import TheStrategyObject
# import pandas as pd

conn = sqlite3.connect('t1.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS strategy')
cur.execute('DROP TABLE IF EXISTS description')
cur.execute('DROP TABLE IF EXISTS source')
cur.execute('DROP TABLE IF EXISTS images')
cur.execute('DROP TABLE IF EXISTS links')

cur.execute('''
    CREATE TABLE strategy (
        id	INTEGER PRIMARY KEY AUTOINCREMENT,
        name	text UNIQUE,
        short_name	text,
        preferred	INTEGER DEFAULT 1);''')








cur.execute('''
CREATE TABLE source (
	id integer PRIMARY KEY,
	datasource text
);''')

cur.execute('''
CREATE TABLE description (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description text,
            source_id integer,
            strategy_id INTEGER UNIQUE,
            FOREIGN KEY (source_id) REFERENCES source(id),
            FOREIGN KEY (strategy_id) REFERENCES strategy(id)
);''')

cur.execute('''
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
	name    TEXT UNIQUE,
	widget	INTEGER CHECK(widget="chart1" OR widget="chart2"),
	strategy_id	INTEGER,
	FOREIGN KEY(strategy_id) REFERENCES strategy(id)
);''')

cur.execute('''
CREATE TABLE links (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	link text,
	strategy_id integer,
    FOREIGN  KEY (strategy_id) REFERENCES strategy(id)
);''')
conn.commit()

#  Cannot get the FOREIGN KEY constraints to run-- whats wrong?
#  FOREIGN KEY (strategy_id) REFERENCES strategy(strategy.id)


# These three entries are required before adding any strategies
# I should not have to supply the ID but I get this error without:
# Incorrect number of bindings supplied. The current statement uses 1, and there are 13 supplied.
entries = ['default', 'user', 'contrib']
for i in range(len(entries)):
    cur.execute('''INSERT INTO source (id, datasource)
                VALUES(?, ?)''',
                (i+1, entries[i]))

tso = TheStrategyObject()
for strat, count in zip(tso.s1, range(len(tso.s1))):
    count = count + 1
    if len(strat) > 1:
        cur.execute('''INSERT INTO strategy(id, name, short_name, preferred)
				VALUES(?, ?, ?, ?)''',
                    (count, strat[0], strat[1], 1))
    else:
        cur.execute('''INSERT INTO strategy(id, name, preferred)
				VALUES(?, ?, ?)''',
                    (count, strat[0], 1))

cur.execute('SELECT id FROM source WHERE datasource = ?', ('default',))
source_id = cur.fetchone()[0]
# cur.execute('SELECT id FROM strategy WHERE name = ?', ('default',))
conn.commit()

for key, count in zip(tso.strats.keys(), range(len(tso.strats.keys()))):
    cur.execute('SELECT id FROM strategy WHERE name = ?', (key,))
    print(key)
    strategy_id = cur.fetchone()[0]
    cur.execute('''INSERT INTO description(id, description, source_id, strategy_id)
					VALUES(?, ?, ?, ?)''',
                (count, tso.strats[key][1], source_id, strategy_id))
    # print(count, key, tso.strats[key])
conn.commit()


conn.commit()
