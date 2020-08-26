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
sqlalchemy model for ib_positions

@author: Mike Petersen
@creation_date: August 26, 2020
This table is deprecated
'''
from sqlalchemy import Column, String, Integer
from structjour.models.meta import Base, ModelBase

class Positions(Base):
    __tablename__ = 'ib_positions'
    id = Column(Integer, primary_key=True)
    account = Column(String)
    symbol = Column(String)
    quantity = Column(Integer)
    date = Column(String)

