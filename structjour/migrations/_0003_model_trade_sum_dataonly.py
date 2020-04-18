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
Created on April 17, 2020

@author: Mike Petersen

Change trade_sum.MktVal BLOB to 0.0

In transition to sqlalchemy models. A one-off migration that will introduce sqlalchemy to structjour.
Upon transition to sqlalchemy and second Beta release, one-off migrations will be removed.

HACK ALERT. I can't figure this out and I am 99% sure its possible. See the ipynb notebooks
I want to use an ORM class object. The query requires a cast or it
blows up when you look at it.
The method that works is using a Table query and engine.connect--
and not any version of the Base table class (and not the TradeSums.__table__ which
still which requires session.query and not engine.connect).

Similarly, reflection works if you reflect a Table and not if you reflect a class
using sqlalchemy.ext.automap import automap_base version of Base
sogotp time. If I figure it out update later ...
'''
import math

from structjour.models.trademodels import getTradeSumTable
from sqlalchemy import create_engine, cast, select, Numeric


class Migrate():
    __tablename__ = "trade_sum"

    def __init__(self, db_string, metadata):
        '''
        :params db_string: The sqlalchemy connection string. e.g. 'sqlite:///some.db'
        :params metada: sqlalchemy MetaData
        '''
        self.db = db_string

        self.trade_sum = getTradeSumTable(metadata)

    def doUpdate(self):
        s = select(([cast(self.trade_sum.c.MktVal, Numeric), self.trade_sum.c.id]))
        engine = create_engine(self.db)
        conn = engine.connect()
        result = conn.execute(s)
        row = result.fetchone()
        while row is not None:
            if math.isclose(row[0], 0, abs_tol=1e-5):
                print(row)
                stmt = self.trade_sum.update().values(MktVal=0).where(self.trade_sum.c.id == row.id)
                conn.execute(stmt)
            row = result.fetchone()


def dostuff():
    from sqlalchemy import MetaData
    import os

    s = 'c:/python/minituts/SQL/sqlalchemy/official_tut/tradeDb_0417.sqlite'
    print(os.path.exists(s))
    s = "sqlite:///" + s

    metadata = MetaData()
    mig = Migrate(s, metadata)
    mig.doUpdate()


if __name__ == '__main__':
    dostuff()
