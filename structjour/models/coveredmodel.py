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
sqlalchemy model for ib_covereed

@author: Mike Petersen
@creation_date: August 19, 2020
'''

import pandas as pd
from sqlalchemy import Column, String
from structjour.models.meta import Base, ModelBase


class Covered(Base):
    __tablename__ = "ib_covered"
    day = Column(String, nullable=False, primary_key=True)
    account = Column(String, nullable=False, primary_key=True)
    covered = Column(String, nullable=False)

    def __repr__(self):
        return f'<covered({self.day}, {self.account}, {self.covered})>'

    @classmethod
    def isDateCovered(cls, account, d, new_session=False):
        '''
        Use an ongoing session
        '''

        d = pd.Timestamp(d)
        d = d.strftime("%Y%m%d")
        if new_session == True:
            ModelBase.connect(new_session=True)
        session = ModelBase.session
        q = session.query(Covered).filter_by(day=d).filter_by(account=account).one_or_none()
        return True if q else False

    @classmethod
    def insertCovered(cls, account, d, covered_b='true', new_session=False):
        if new_session == True:
            ModelBase.connect(new_session=True)
        session = ModelBase.session
        d = pd.Timestamp(d)
        d = d.strftime("%Y%m%d")
        if not Covered.isDateCovered(account, d):
            cov = Covered(day=d, account=account, covered=covered_b)
            session.add(cov)
            if new_session:
                session.commit()

    @classmethod
    def getCoveredDays(cls, account, beg, end):
        session = ModelBase.session
        q = session.query(Covered).filter_by(account=account).filter(Covered.day >= beg).filter(Covered.day <= end).order_by(Covered.day).all()
        return q


