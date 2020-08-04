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
Test the createdirscontrol module.

Created on Feb 10, 2020

@author: Mike Petersen
'''
import os
import sys
from shutil import rmtree
import unittest
from unittest import TestCase
from PyQt5 import QtCore
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
from PyQt5 import QtWebEngineWidgets    # noqa:  F401
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QSettings
from structjour.view.createdirscontrol import CreateDirs

app = QApplication(sys.argv)


class TestCreateDirsControl(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestCreateDirsControl, self).__init__(*args, **kwargs)
        self.regkey = 'zero_substance/test'
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def setUp(self):
        self.settings = QSettings(self.regkey, 'structjour')
        realSettings = QSettings('zero_substance', 'structjour')
        # This setting required in createDirs
        self.settings.setValue('scheme', realSettings.value('scheme'))
        self.settings.setValue('directories_autogen', 'true')
        cwd = os.getcwd()
        self.test_jdir = os.path.join(cwd, 'test/journal_test')
        self.settings.setValue('journal', self.test_jdir)
        self.w = CreateDirs(testSettings=self.settings)
        self.w.debug = True

    def tearDown(self):
        # pass
        self.settings.clear()
        self.settings.sync()
        if os.path.exists(self.test_jdir):
            rmtree(self.test_jdir)
        # self.settings.remove(self.regkey)

    def test_enableAutoGen(self):
        QTest.mouseClick(self.w.ui.disabledRb, Qt.LeftButton)
        QTest.mouseClick(self.w.ui.enabledRb, Qt.LeftButton)
        self.assertEqual(self.settings.value('directories_autogen'), 'true')

    def test_disableAutoGen(self):
        QTest.mouseClick(self.w.ui.enabledRb, Qt.LeftButton)
        QTest.mouseClick(self.w.ui.disabledRb, Qt.LeftButton)
        self.assertEqual(self.settings.value('directories_autogen'), 'false')

    def testCreateDirs(self):
        if not os.path.exists(self.test_jdir):
            os.makedirs(self.test_jdir)
        cb_year = self.w.ui.createDirsYear
        cb_month = self.w.ui.createDirsMonth
        cb_year.setCurrentIndex(cb_year.count() - 1)
        cb_month.setCurrentIndex(cb_month.count() - 1)
        # m = pd.Timestamp(f'{cb_year.currentText()} {cb_month.currentText()}')

        theDir = self.w.createDirs()
        self.assertTrue(os.path.exists(theDir))

    def test_CreateDirs_fail(self):
        self.settings.setValue('journal', "")
        theDir = self.w.createDirs()
        self.assertEqual(theDir, "")
        self.settings.setValue('journal', self.test_jdir)


if __name__ == '__main__':
    unittest.main()
