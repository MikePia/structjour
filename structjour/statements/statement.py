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
Module to open any file and return the right statement type

@author: Mike Petersen
@creation_data: 08/26/19
'''
import os
import pandas as pd
# import re

from bs4 import BeautifulSoup

# from PyQt5.QtCore import QSettings
from structjour.dfutil import DataFrameUtil

from structjour.statements.findfiles import findFilesSinceMonth
# from structjour.statements.dasstatement import DasStatement
from structjour.statements.findfiles import checkDateDir
from structjour.statements.ibstatement import readit
from structjour.definetrades import ReqCol


def getStatementType(infile):
    '''
    Determine if infile is a statement. If it is return a tuple (data, type) TODO: Not doing what I said...
    If it is a DAS statement, determine if it matches the current date. As DAS statements do not
    include dates, the date in structjour and the directory structure date must match.
    If they don't match, the program, at a higher level, will pop a query to get the date of the
    statement.
    '''
    file, ext = os.path.splitext(infile)
    if not os.path.exists(infile) or (
            ext.lower() != '.csv' and not ext.lower().startswith('.htm')):
        return None, None
    if ext.lower() == '.csv':
        df = pd.read_csv(infile, names=[x for x in range(0, 100)])
        if df.iloc[0][0] == 'BOF' or df.iloc[0][0] == 'HEADER' or (
                df.iloc[0][0] == 'ClientAccountID') or (
                df.iloc[0][0] == 'Statement'):
            return df, "IB_CSV"
        df = pd.read_csv(infile)
        if not df.empty:
            requiredFields = list(ReqCol().columns)
            requiredFields.remove('Date')

            # A small hack to allow tradesByTickets to pass as a DAS export
            if 'PnL' not in df.columns:
                requiredFields.remove('PnL')
                requiredFields.append('P / L')
            try:
                if DataFrameUtil.checkRequiredInputFields(df, requiredFields):
                    if not checkDateDir(infile):
                        return None, 'DAS'
                    return df, 'DAS'
            except ValueError:
                pass

    elif ext.lower().startswith('.htm'):
        soup = BeautifulSoup(readit(infile), 'html.parser')
        tbldivs = soup.find_all("div", id=lambda x: x and x.startswith('tbl'))
        if tbldivs:
            return tbldivs, 'IB_HTML'
    return None, None


def notmain():
    d = '20190601'
    fs = findFilesSinceMonth(d, '', searchParts=True, DAS=True)
    for f, dd in fs:
        x, inputtype = getStatementType(f)
        print(f, inputtype)
        if inputtype == 'DAS':
            if x is None:
                print('     We got mismatching dates here')


if __name__ == '__main__':
    notmain()
