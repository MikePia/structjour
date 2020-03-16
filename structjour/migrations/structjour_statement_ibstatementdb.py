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
Created on march 10, 2020

@author: Mike Petersen

Add RealRR to the trade_sums table.
In prepartion to being django model. Figure out what will need to be done. The important part is to
provide an update path for model changes without breaking anything. Currently its specific to structjour
and sqlite but will evantually adopt django models and we will do less locally. Until the transition, it
will get a bit messy.
'''

import logging
import sqlite3
from PyQt5.QtCore import QSettings
from structjour.statements.ibstatementdb import StatementDB
from structjour.version import version


class Migrate(StatementDB):

    settings = QSettings('zero_substance', 'structjour')
    ibdb = StatementDB(db=settings.value('tradeDb'))
    conn = sqlite3.connect(ibdb.db)
    cur = conn.cursor()

    @classmethod
    def checkVersion(cls, mv, v):
        if v < mv:
            raise ValueError(f'Incorrect version of structjour {v}. This code requires version >= {mv}')

    @classmethod
    def addField(cls, model_name=None, name=None, field=None, dependencies=None):
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
            logging.info(f'Added column {name} to table {model_name}.')
        elif cursor[0] == 1:
            logging.info(f'Table {model_name} already has column {name}')
        else:
            logging.error('Unknown database error. Raising ValueError')
            raise ValueError(f'Unknown database error while attempting to add column {name}:{field} to table {model_name}')


class Migration:
    min_version = '0.9.92a0'
    version = version
    dependencies = ['trade_sum']

    # This list functions like a script, calling the given class methods in turn
    operations = [Migrate.checkVersion(min_version, version),
                  Migrate.addField(model_name="trade_sum", name="RealRR", field="NUMERIC", dependencies=["trade_sum", ])]

    @classmethod
    def trigger(cls):
        print('consider it triggered')


def relavantCodeDoneLocally():
    # Migration.trigger()
    return ('Success means it (quietly) didnt blow up')


if __name__ == '__main__':
    success = relavantCodeDoneLocally()
    print(success)
