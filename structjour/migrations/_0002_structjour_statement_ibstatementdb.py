# Structjour -- a daily trade review helper
# Copyright (C) 2020 Zero Substance Trading
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
Created on march 10, 2020

@author: Mike Petersen

Add RealRR to the trade_sums table.

In prepartion to being django model. Figure out what will need to be done. The important part is to
provide an update path for model changes without breaking anything. Currently its specific to structjour
and sqlite but will evantually adopt django models and we will do less locally. Until the transition, it
will get a bit messy.
'''

# import logging
import os
import sqlite3
from PyQt5.QtCore import QSettings
from structjour.statements.ibstatementdb import StatementDB
from structjour.version import version


# This is the last of the old DBAPI migrations and will update to sqlalchemy
# when it, and my evolving rollyourown migration is better understood, fleshed out, and tested.
# This runs from import before any code is run and causes python to make its own handlers 
# and log to nowhere in particular and it messes with logging.basicConfig. For now logging is 
# removed from migration modules. This is transitional code.
class Migrate(StatementDB):

    settings = QSettings('zero_substance', 'structjour')
    ibdb = None
    conn = None
    cur = None
    updated = False

    @classmethod
    def checkDbStatus(cls):
        if cls.settings.value('tradeDb') is None:
            return
        if not os.path.exists(cls.settings.value('tradeDb')):
            msg = f"Database connection is not setup correctly: {cls.settings.value('tradeDb')}"
            # logging.error(msg)
            print(msg)
            cls.settings.remove('tradeDb')
            # raise ValueError(msg)
        else:
            print(f"Ready to update the database: {cls.settings.value('tradeDb')}")
            # logging.info(f"Ready to update the database: {cls.settings.value('tradeDb')}")

    @classmethod
    def connect(cls):
        if cls.settings.value('tradeDb') is None:
            return
        cls.ibdb = StatementDB(db=cls.settings.value('tradeDb'))
        cls.conn = sqlite3.connect(cls.ibdb.db)
        cls.cur = cls.conn.cursor()

    @classmethod
    def checkVersion(cls, mv, v):
        if v < mv:
            raise ValueError(f'Incorrect version of structjour {v}. This code requires version >= {mv}')

    @classmethod
    def addField(cls, model_name=None, name=None, field=None, dependencies=None):
        if cls.cur is None:
            return
        for dep in dependencies:
            cursor = cls.cur.execute(f'''SELECT name FROM sqlite_master WHERE type='table' AND name = ?''', (dep, ))
            cursor = cursor.fetchone()
            if not cursor:
                print(f'failed to get {dep}')
                raise ValueError(f'Dependency error. Table not found {dep}')
            else:
                assert cursor[0] == dep
                print(f'got {dep}')

        cursor = cls.cur.execute(f'''SELECT COUNT(*) as cnt
            FROM pragma_table_info(?) WHERE name = ?''', (model_name, name, ))

        cursor = cursor.fetchone()
        if cursor[0] == 0:
            alter = f"ALTER TABLE {model_name} ADD COLUMN {name} {field}"
            cursor = cls.cur.execute(alter)
            cls.conn.commit()
            print(f'Added column {name} to table {model_name}.')
            # logging.info(f'Added column {name} to table {model_name}.')
            cls.updated = True
        elif cursor[0] == 1:
            print(f'Table {model_name} already has column {name}')
            # logging.info(f'Table {model_name} already has column {name}')
            cls.updated = True
        else:
            print('Unknown database error. Raising ValueError')
            # logging.error('Unknown database error. Raising ValueError')
            raise ValueError(f'Unknown database error while attempting to add column {name}:{field} to table {model_name}')

    @classmethod
    def isUpdated(cls):
        return cls.updated


class Migration:
    min_version = '0.9.92a0'
    version = version
    dependencies = ['trade_sum']

    # This list functions like a script, calling the given class methods in turn but w/o possibility
    # of interacting with return. Success or ValueError are the options
    operations = [Migrate.checkDbStatus(),
                  Migrate.connect(),
                  Migrate.checkVersion(min_version, version),
                  Migrate.addField(model_name="trade_sum", name="RealRR", field="NUMERIC", dependencies=["trade_sum", ])]


if __name__ == '__main__':
    print('This thing will mostly run just by importing it.')
