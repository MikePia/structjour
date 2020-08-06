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
Test the methods module structjour.models.meta
@author: Mike Petersen

@creation_date: 8/5/20
'''

import os
import unittest
from unittest import TestCase
from structjour.models.meta import ModelBase
from structjour.models.inspiremodel import Inspire

class TestMeta(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestMeta, self).__init__(*args, **kwargs)
        ddiirr = os.path.dirname(__file__)
        testdb = os.path.join(ddiirr, 'test.sqlite')
        self.con_str = 'sqlite:///' + testdb

    def setUp(self):
        '''Remove schema'''
        print(Inspire.__table__)
        
        ModelBase.connect(new_session=True, con_str=self.con_str)
        ModelBase.metadata.drop_all(bind=ModelBase.engine, tables=[Inspire.__table__])
        ModelBase.session.commit()
        ModelBase.session.close()

    def test_connect(self):
        '''Create schema, add, delete. Test the add and the delete'''
        insp = Inspire(
            lname = 'The Dude',
            subject = 'On Peace',
            name = 'The Dude',
            who = 'THE authority on life',
            quote = 'This aggression will not stand, man.'
        )
        ModelBase.connect(new_session=True, con_str=self.con_str)
        ModelBase.createAll()
        session = ModelBase.session
        session.add(insp)
        session.commit()
        session.close()

        ModelBase.connect(new_session=True, con_str=self.con_str)
        session = ModelBase.session
        q = session.query(Inspire).all()
        self.assertEqual(q[0].quote, 'This aggression will not stand, man.')
        self.assertEqual(len(q), 1)
        
        session.delete(q[0])
        session.commit()
        session.close()

        ModelBase.connect(new_session=True, con_str=self.con_str)
        session = ModelBase.session
        q = session.query(Inspire).all()
        self.assertEqual(len(q), 0)
        session.close()
        
        

        


def dostuff():
    t = TestMeta()
    t.setUp()
    t.test_connect()
    # t.test_remove()

if __name__ == '__main__':
    dostuff()

