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
Created on Apr 1, 2019

@author: Mike Petersen
'''


import os
import sys

from PyQt5.QtWidgets import QApplication, QStyleFactory
from structjour.view.runtrade import runController
from structjour.view.sumcontrol import SumControl

# pylint: disable = C0103




def main():
    ddiirr = os.path.dirname(__file__)

    # Paths used in summaryform.ui rely on cwd .
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    s = QStyleFactory.create('Fusion')
    app.setStyle(s)
    w = SumControl()
    rc = runController(w)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()