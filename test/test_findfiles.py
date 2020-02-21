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
@author: Mike Petersen

@creation_date: 2019-07-10

Test functions in the module test.findfiles
'''

import os
from pathlib import Path
import shutil
import unittest

import pandas as pd

from PyQt5.QtCore import QSettings

from structjour.statements import findfiles as ff
# pylint: disable = C0103


class Test_FindFiles(unittest.TestCase):
    '''
    Test functions and methods in the graphstuff module
    '''

    def __init__(self, *args, **kwargs):
        super(Test_FindFiles, self).__init__(*args, **kwargs)
        self.settings = QSettings('zero_substance', 'structjour')

    def tearDown(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))

    def test_getBaseDir(self):
        j = self.settings.value('journal')
        jj = ff.getBaseDir()
        self.assertEqual(j, jj)

    def test_getMonthDir(self):
        d1 = pd.Timestamp('20190115')
        d2 = pd.Timestamp('20190315')

        dadir = ff.getMonthDir(daDate=d1)
        dadir2 = ff.getMonthDir(daDate=d2)
        print(dadir)
        assert dadir.find("201901") > -1
        assert dadir2.find("201903") > -1

    def test_getDirectory(self):
        d1 = "20190304"
        dir1 = ff.getDirectory(d1)
        dir2 = ff.getDirectory()
        os.chdir(dir1)
        os.chdir('../..')
        dir1 = os.getcwd()

        dir1 = os.path.normpath(dir1)
        dir3 = os.path.normpath(ff.getBaseDir())
        self.assertEqual(dir1, dir3)

        os.chdir(dir2)
        os.chdir('../..')
        dir2 = os.getcwd()
        dir2 = os.path.normpath(dir2)
        self.assertEqual(dir2, dir3)

    def test_findFilesInDir(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        # shutil.rmtree('gobble')
        os.mkdir('gobble')
        print(os.getcwd())
        names = ['one', 'two', 'three', 'four', 'five', 'six', 'seven']
        for p1 in names:
            for p2 in names:
                # for p3 in names:
                name = 'gobble/' + '.'.join([p1, p2]) + '.as'
                Path(name).touch()

        x = ff.findFilesInDir('gobble', 'one.two.as', True)
        self.assertTrue(len(x) == 2)

        shutil.rmtree('gobble')

    def test_findFilesInMonth(self):
        d1 = pd.Timestamp('20190303')
        fs = ff.findFilesInMonth(d1, 'trades.csv', True)
        self.assertTrue(len(fs) > 0)

    def test_findFilesSinceMonth(self):
        d1 = pd.Timestamp('20190303')
        fs = ff.findFilesSinceMonth(d1, 'trades.csv')
        self.assertTrue(len(fs) > 0)


def main():
    unittest.main()


def notmain():

    t = Test_FindFiles()
    t.test_getBaseDir()


if __name__ == '__main__':
    # notmain()
    main()
