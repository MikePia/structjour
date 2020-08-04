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
Created on April 17, 2020

@author: Mike Petersen

Change trade_sum.MktVal BLOB to 0.0

In transition to sqlalchemy models. A one-off migration that will introduce sqlalchemy to structjour.
Upon transition to sqlalchemy and second Beta release, one-off migrations will be removed.
'''
import datetime as dt

from structjour.models.trademodels import TradeSum

from structjour.models.meta import ModelBase, MigrateModel
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
    settings = ModelBase.settings
    # db = "sqlite:///" + settings.value('tradeDb')

    @classmethod
    def doUpdate(cls):
        q = ModelBase.session.query(MigrateModel).filter_by(m_id="0003").first()
        if q is not None:
            cls.updated = True
            return

        q = ModelBase.session.query(TradeSum).all()
        maxid = 0
        for qq in q:
            maxid = max(qq.id, maxid)
            if isinstance(qq.mktval, (bytes, str)):
                qq.mktval = 0
        ModelBase.session.commit()

        theDate = dt.datetime.now()
        theDate = theDate.strftime("%Y%m%d")
        _0003migration = MigrateModel(m_id="0003", date=theDate, data_key="tsum_id", data_val=maxid)
        ModelBase.session.add(_0003migration)
        ModelBase.session.commit()
        cls.updated = True

    @classmethod
    def isUpdated(cls):
        return cls.updated


class Migration:
    min_version = '0.9.92a002'
    version = version
    dependencies = [TradeSum, ]

    # Better, more central location to call createAll? Have to accomodate migrations that use Sessions
    # and migrations that use engine.connect
    operations = [ModelBase.connect(new_session=True),
                  ModelBase.createAll(),
                  ModelBase.checkVersion(min_version, version),
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
