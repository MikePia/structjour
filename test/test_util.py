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
Created on Feb 10, 2020

@author: Mike Petersen
'''

import os
import pandas as pd
from shutil import rmtree
import unittest
from unittest import TestCase

from structjour.utilities.util import autoGenCreateDirs

from PyQt5.QtCore import QSettings


class TestUtil(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestUtil, self).__init__(*args, **kwargs)

    def test_autoGenCreateDirs(self):
        ''' Test structjour.utilities.util.autoGenCreateDirs '''

        settings = QSettings('zero_substance', 'structjour')
        orig_settings = settings.value('directories_autogen')
        if orig_settings == 'false':
            # Temporarily set to true in order to test
            settings.setValue('directories_autogen', 'true')
        theDate = pd.Timestamp.now()
        theDate = pd.Timestamp(theDate.year + 1, theDate.month, 1)
        theDir1, theDir2 = autoGenCreateDirs(settings, theDate)
        self.assertTrue(os.path.exists(theDir1))
        self.assertTrue(os.path.exists(theDir2))
        rmtree(theDir1, ignore_errors=True)
        rmtree(theDir2, ignore_errors=True)
        if orig_settings == 'false':
            settings.setValue('directories_autogen', 'false')


if __name__ == '__main__':
    unittest.main()
