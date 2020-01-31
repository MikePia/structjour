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

Test methods in the class ibstatement.IbStatement
'''
import unittest
from structjour.statements.ibstatement import IbStatement


class Test_StatementDB(unittest.TestCase):
    '''
    Test functions and methods in the ibstatementdb module
    '''
    def __init__(self, *args, **kwargs):
        def test_figureBAPL(self):
            pass

        def test_parseTitle(self):
            pass

        def test_combinePartialsHtml(self):
            pass

        def test_doctorHtmlTables(self):
            pass

        def test_openIBStatementHtml(self):
            pass

        def test_openIbStatement(self):
            pass

        def test_openIbStatementCSV(self):
            pass

        def test_fixNumericTypes(self):
            pass

        def test_unifyDateFormat(self):
            pass

        def test_parseDefaultDSVPeriod(self):
            pass

        def test_combinePartialsDefaultCSV(self):
            pass

        def test_doctorDefaultCSVStatement(self):
            pass

        def test_getTablesFromDefaultStatement(self):
            pass

        def test_combinePartialsFlexTrade(self):
            pass

        def test_cheatForBAPL(self):
            pass

        def test_combineOrdersByTime(self):
            pass

        def test_combinePartialsFlexCSV(self):
            pass

        def test_doctorActivityFlexTrades(self):
            pass

        def test_getFrame(self):
            pass

        def test_doctorFlexTables(self):
            pass

        def test_openActivityFlexCSV(self):
            pass

        def test_getColsByTabid(self):
            pass

        def test_verifyAvailableCols(self):
            pass


if __name__ == '__main__':
    ibs = IbStatement('test/test.db')

