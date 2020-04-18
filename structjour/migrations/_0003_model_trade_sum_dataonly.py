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
I want to use an ORM class object. The query to find BLOBs requires a cast to Numeric or it
blows up when you look at it.
The method that works is using a Table query and engine.connect--
and not any version of the Base table class (and not the TradeSums.__table__ which
still which requires session.query and not engine.connect).

Similarly, reflection works if you reflect a Table and not if you reflect a class
using automap_base version of Base
sogotp time. If I figure it out update later ...
'''
import datetime as dt
import math

from structjour.models.trademodels import getTradeSumTable
from sqlalchemy import cast, select, Numeric

from structjour.models.meta import MigrateBase, MigrateModel
from structjour.version import version

# from PyQt5.QtCore import QSettings


class Migrate():
    '''
    A data migration to change trade_sum.MktVal entries from BLOB type to 0.
    This pre-release migration will be removed at Beta 2. It is necessary to play
    nice with sqlalchemy and to be compatible with other (future) databases.
    Its also the first use of sa in structjour
    '''
    __tablename__ = "trade_sum"
    updated = False
    settings = MigrateBase.settings

    trade_sum = getTradeSumTable(MigrateBase.metadata)
    # db = "sqlite:///" + settings.value('tradeDb')

    @classmethod
    def doUpdate(cls):
        q = MigrateBase.session.query(MigrateModel).filter_by(m_id="0003").first()
        if q is not None:
            cls.updated = True
            return
        s = select(([cast(cls.trade_sum.c.MktVal, Numeric), cls.trade_sum.c.id]))
        # engine = create_engine(cls.db)
        conn = MigrateBase.engine.connect()
        result = conn.execute(s)
        row = result.fetchone()
        maxid = 0
        while row is not None:
            if row.id > maxid:
                maxid = row.id
            if math.isclose(row[0], 0, abs_tol=1e-5):
                stmt = cls.trade_sum.update().values(MktVal=0).where(cls.trade_sum.c.id == row.id)
                conn.execute(stmt)
            row = result.fetchone()

        theDate = dt.datetime.now()
        theDate = theDate.strftime("%Y%m%d")
        _0003migration = MigrateModel(m_id="0003", date=theDate, data_key="tsum_id", data_val=maxid)
        MigrateBase.session.add(_0003migration)
        MigrateBase.session.commit()
        cls.updated = True

    @classmethod
    def isUpdated(cls):
        return cls.updated


class Migration:
    min_version = '0.9.92a002'
    version = version
    dependencies = [getTradeSumTable(MigrateBase.metadata), ]

    # Better, more central location to call createAll? Have to accomodate migrations that use Sessions
    # and migrations that use engine.connect
    operations = [MigrateBase.connect(new_session=True),
                  MigrateBase.createAll(),
                  MigrateBase.checkVersion(min_version, version),
                  Migrate.doUpdate()]


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
    # dostuff()
    print('This thing will run by importing it')
