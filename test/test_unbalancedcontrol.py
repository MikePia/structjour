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
Test the module unbalancedcontrol

Created on May 20, 2019

@author: Mike Petersen
'''

import os
import sys
import unittest
from unittest import TestCase

import pandas as pd
from PyQt5 import QtCore
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
from PyQt5 import QtWebEngineWidgets    # noqa:  F401
from PyQt5.QtWidgets import QApplication

from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from structjour.view.unbalancedcontrol import UnbalControl
# pylint: disable = C0103

app = QApplication(sys.argv)


class TestUnbalCtrl(TestCase):
    '''Test the user interaction stuff-- two editable QLineEdits and connections'''

    def __init__(self, *args, **kwargs):
        super(TestUnbalCtrl, self).__init__(*args, **kwargs)

    def setUp(self):

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def justtestit(self, s, a, b, t):
        vals = [s, a, b]
        for i in range(0, 3):
            try:
                vals[i] = float(vals[i])
            except ValueError:
                vals[i] = 0.0
        self.assertTrue(vals[0] + vals[1] - vals[2] == t)

    def test_shares(self):
        '''
        Test
        '''
        self.w = UnbalControl()
        # fn = 'C:/trader/journal/_201904_April/_0403_Wednesday/trades.csv'
        fn = 'C:/trader/journal/_201904_April/_0404_Thursday/trades.csv'
        if not os.path.exists(fn):
            return
        dff = pd.read_csv(fn)

        self.swingTrade = dict()
        self.swingTrade['shares'] = -1000.0
        self.swingTrade['before'] = 0.0
        self.swingTrade['after'] = 0.0

        self.w.runDialog(dff, 'APPL', -1000, self.swingTrade)

        before = self.w.ui.unbalBefore
        after = self.w.ui.unbalAfter
        shares = self.w.ui.unbalShares
        self.balance = -1000
        self.justtestit(shares.text(), after.text(), before.text(), self.balance)

        QTest.keyClick(before, Qt.Key_A, Qt.ControlModifier)
        QTest.keyClicks(before, str(400))
        self.justtestit(shares.text(), after.text(), before.text(), self.balance)

        QTest.keyClick(before, Qt.Key_Enter)
        self.justtestit(shares.text(), after.text(), before.text(), self.balance)

        QTest.keyClick(after, Qt.Key_A, Qt.ControlModifier)
        QTest.keyClicks(after, str(-750))
        self.justtestit(shares.text(), after.text(), before.text(), self.balance)

        QTest.keyClick(after, Qt.Key_Enter)
        self.justtestit(shares.text(), after.text(), before.text(), self.balance)

        QTest.mousePress(self.w.ui.okBtn, Qt.LeftButton)
        self.justtestit(self.swingTrade['shares'], self.swingTrade['after'],
                        -self.swingTrade['before'], self.balance)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
