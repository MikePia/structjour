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
Instantiate the ui form and create all the needed connections to run it.

Created on May 19, 2019

@author: Mike Petersen
'''

import os
import sys
import unittest
from unittest import TestCase
from PyQt5 import QtCore
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
from PyQt5 import QtWebEngineWidgets    # noqa:  F401
from PyQt5.QtWidgets import QApplication, QLineEdit, QCheckBox
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QSettings

from structjour.view.sapicontrol import StockApi

# pylint: disable = C0103

app = QApplication(sys.argv)


class TestSapi(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestSapi, self).__init__(*args, **kwargs)

    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

        apisettings = QSettings('zero_substance/stockapi/test', 'structjour')
        testSet = {'ibRealPort': '1234',
                   'ibRealId': '5678',
                   'ibPaperPort': '8765',
                   'ibPaperId': '4321',
                   'ibRealCb': True,
                   'ibPaperCb': False,
                   'bcCb': True,
                   'avCb': False,
                   'fhCb': False,
                   'APIPref': 'abc, cde, fg'}

        apisettings.setValue('ibRealPort', '6789')
        for key in testSet:
            apisettings.setValue(key, testSet[key])
        self.w = StockApi(apisettings)
        testWidgets = {'ibRealPort': self.w.ui.ibRealPort,
                   'ibRealId': self.w.ui.ibRealId,
                   'ibPaperPort': self.w.ui.ibPaperPort,
                   'ibPaperId': self.w.ui.ibPaperId,
                   'ibRealCb': self.w.ui.ibRealCb,
                   'ibPaperCb': self.w.ui.ibPaperCb,
                   'bcCb': self.w.ui.bcCb,
                   'avCb': self.w.ui.avCb,
                   'fhCb': self.w.ui.fhCb,
                   'APIPref': self.w.ui.APIPref}
        self.testWidgets = testWidgets
        self.testSet = testSet
        self.apiSet = apisettings

    def test_initFromSettings(self):
        '''[ibRealPort, ibRealId, ibPaperPort, ibPaperId,
        ibRealCb, ibPaperCb,
        bcCb, avCb, fhCb,
        APIPref]'''
        for key in self.testWidgets:
            widg = self.testWidgets[key]
            if isinstance(widg, QLineEdit):
                val = self.apiSet.value(key)
                self.assertEqual(widg.text(), val)
            elif isinstance(widg, QCheckBox):
                val = self.apiSet.value(key, False, bool)
                self.assertEqual(widg.isChecked(), val)

    def test_sortIt(self):
        '''
        Test sortIt and reorderAPIPref
        '''
        self.apiSet.setValue('ibRealCb', True)
        self.apiSet.setValue('ibPaperCb', False)
        self.apiSet.setValue('bcCb', True)
        self.apiSet.setValue('avCb', False)
        self.apiSet.setValue('fhCb', False)
        self.w.ui.APIPref.setText('ib, bc')

        s = self.w.ui.APIPref.styleSheet()
        self.assertTrue(s.find('green') > 0)
        self.w.ui.APIPref.setText('ib, bc, av')
        s = self.w.ui.APIPref.styleSheet()
        self.assertTrue(s.find('red') > 0)

        QTest.mouseClick(self.w.ui.avCb, Qt.LeftButton)
        QTest.mouseClick(self.w.ui.ibRealCb, Qt.LeftButton)
        QTest.mouseClick(self.w.ui.ibRealCb, Qt.LeftButton)
        self.assertEqual(self.w.ui.APIPref.text(), 'bc, av, ib')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
