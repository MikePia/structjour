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
import sqlite3
from structjour.inspiration.inspire import Inspire
# import pandas as pd

conn = sqlite3.connect('t1.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Inspire')
cur.execute('DROP TABLE IF EXISTS Name')
cur.execute('''
CREATE TABLE Inspire(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
    lname  TEXT, 
    subject TEXT, 
    name TEXT, 
    who TEXT, 
    quote TEXT UNIQUE)''')


i = Inspire()
whos=list()
count=0
for i, row in i.df.iterrows():
    lname    = row['name']
    subject = row['on']
    quote   = row['quote']
    name, who = row['who'].split(", ")
    print ("{},  {},  {}, {}".format(lname, subject, name, who))
    cur.execute('''INSERT INTO Inspire (id, lname, subject, name, who, quote)
                VALUES(?,?, ?, ?, ?, ?)''',
                (count, lname, subject, name, who, quote))
    count = count + 1
conn.commit()
#     if len(whos[-1]) < 2 :
#         whos[-1] = whos[-1][0].split("-")

print()
print()
# for who in whos:
#     print("{0:35}{1}".format(who[0], who[1]))
# #         who = who.split("-")