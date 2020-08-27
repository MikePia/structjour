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
sqlalchemy model for holiday

@author: Mike Petersen
@creation_date: August 19, 2020
'''

import pandas as pd
from sqlalchemy import Column, String
from structjour.models.meta import Base, ModelBase

class Holidays(Base):
    __tablename__ = "holidays"
    day = Column(String, nullable=False, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f'<holidays({self.name})>'

    @classmethod 
    def insertHoliday(cls, day, name, commit=False):
        if commit:
            ModelBase.connect(new_session=True)
        session = ModelBase.session
        q = session.query(Holidays).filter_by(day=day).filter_by(name=name).one_or_none()
        if not q:
             h = Holidays(day=day, name=name)
             session.add(h)
             if commit:
                 session.commit()
                 session.close()


    @classmethod
    def isHoliday(self, d, new_session=False):
        d = pd.Timestamp(d)
        d = d.strftime("%Y%m%d")
        
        if new_session == True:
            ModelBase.connect(new_session)
        session = ModelBase.session
        q = session.query(Holidays).filter_by(day=d).one_or_none()
        return True if q else False


