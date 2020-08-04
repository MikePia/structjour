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
Created on Aug 30, 2018

@author: Mike Petersen
'''
import unittest
import datetime as dt
import os
import types
from structjour.journalfiles import JournalFiles
# pylint: disable = C0103, W0703, E1121


def itsTheWeekend():
    '''
    This is a hacky thing to take care of (most) non trading days aka Saturday and Sunday and
    solely for my development environment. (if its a holiday you shouldn't be working anyway so it
    serves you right). Errors occur because on the weekend no trades.csv file was created. I don't
    want to alter the code to test the dynamic file selection on weekends so I will change the day.
    :return: The date of the last weekday to have occurred. AKA Friday if today is a weekend day.
            Otherwise returns today
    '''
    d = dt.date.today()
    idow = int(d.strftime("%w"))
    subtract = 1 if idow == 6 else 2 if idow == 0 else 0
    td = dt.timedelta(subtract)
    newdate = d - td
    return newdate
# itsTheWeekend().strftime("%A, %B %d, %y")


class TestJF(unittest.TestCase):
    '''
    Test the methods in JournalFiles
    '''

    def __init__(self, *args, **kwargs):
        '''
        When we initialze the object, ensure that we always run from src as the cwd
        '''
        super(TestJF, self).__init__(*args, **kwargs)

    def setUp(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))

    def test_IndirCreate(self):
        '''
        Test JournalFiles. Explicit setting of an infile
        '''
        f = "Trades.8.ExcelEdited.csv"
        jf = JournalFiles(indir="data/", infile=f)

        self.assertEqual(os.path.realpath(os.path.join('data/', f)), os.path.realpath(
            jf.inpathfile), "Structjour failed to correctly set the input file")


def main():
    '''
    Run code outside of unittest framework
    Then run cl python -m unittest discovery
    '''
    f = TestJF()
    for name in dir(f):
        if name.startswith('test'):
            attr = getattr(f, name)

            if isinstance(attr, types.MethodType):
                attr()


def notmain():
    '''Run some local code'''
    t = TestJF()
    # t.test_DefaultCreate()
    t.test_DevelDefaultCreate()


def clstyle():
    '''Run unittests cl style. Can debug'''
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


if __name__ == "__main__":
    # notmain()
    # main()
    clstyle()
