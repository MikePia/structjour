import sqlite3
from inspiration.inspire import Inspire
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