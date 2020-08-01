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
Created on August 1, 2020

@author: Mike Petersen

Create a table for quotes
'''
import datetime as dt
from structjour.inspiration.inspire import Inspire as InspireQuote
import pandas as pd
from structjour.version import version

from structjour.models.meta import ModelBase, MigrateModel
from structjour.models.inspiremodel import Inspire


class Migrate():
    '''
    A permanent required migration. Create a table for quotes and populate it with the quotes in
    the module structjour.inspiration.inspire.Inspire.df
    '''
    __tablename__ = "inspire"
    updated = False
    settings = ModelBase.settings

    @classmethod
    def doUpdate(cls):
        q = ModelBase.session.query(MigrateModel).filter_by(m_id="0004").first()
        if q is not None:
            cls.updated = True
            return
        iq = InspireQuote()
        Inspire.loadQuotes(iq)

        # Record migration done in MigrateModel
        theDate = dt.datetime.now().strftime("%Y%m%d")
        _0004migration = MigrateModel(m_id="0004", date=theDate, data_key='', data_val=0)
        ModelBase.session.add(_0004migration)
        ModelBase.session.commit()
        cls.updated = True

    @classmethod
    def isUpdated(cls):
        return cls.updated

class Migration:
    min_version = '0.9.93a7'
    operations = [ ModelBase.connect(new_session=True),
        ModelBase.checkVersion(min_version, version),
        Migrate.doUpdate()]
