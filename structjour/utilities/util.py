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
import math
import numpy as np
import os

import pandas as pd
from pandas.tseries.offsets import MonthEnd
from structjour.time import createDirsStructjour


def autoGenCreateDirs(settings, testDate=None):
    '''
    Create the journal directories for the current month and next month. The QSettings
    value journal must exist and the value for directories_autogen must not be false or
    just return quietly.
    :params testDate: Override the date. Intended for testing only
    '''
    if settings.value('tradeDb') is None or not settings.value('directories_autogen', True, bool) or not settings.value('journal'):
        return None, None
    theDate = pd.Timestamp.now()
    if testDate:
        theDate = testDate
    nextMonth = pd.Timestamp(theDate.year, theDate.month + 1, 1)
    jdir = settings.value('journal')
    scheme = settings.value('scheme')
    schemex = scheme.format(Year='%Y', month='%m', MONTH='%B', day='%d', DAY='%A').split('/')

    theDir1 = theDate.strftime(schemex[0])
    theDir2 = nextMonth.strftime(schemex[0])

    theDir1 = os.path.join(jdir, theDir1)
    theDir2 = os.path.join(jdir, theDir2)
    if not os.path.exists(theDir1):
        createDirsStructjour(theDate)
    if not os.path.exists(theDir2):
        createDirsStructjour(nextMonth)
    settings.setValue('lastDirCreated', nextMonth.strftime('%Y%m01'))
    return theDir1, theDir2


def advanceMonth(d, numMonths=1):
    '''
    Take a date and advance a number of months up to 12. The returned date's day is the same as the argument's unless
    it is >= 28 when it returns the last day of the month
    :params d: A time string, pd Timstamp or datetime
    :params numMoths: the number of months to advance
    :return: A pd Timestamp advanced by numMonths.
    :raise ValueError: if numMonths is not with 1~12
    '''
    if numMonths > 112 and numMonths > 0:
        raise ValueError(f'Invalid argument for numMonths: {numMonths}')
    d = pd.Timestamp(d)

    month = (d.month + numMonths) % 12
    if month == 0: month = 12
    year = d.year if month > numMonths else d.year + 1
    day = d.day

    if day >= 28:
        return pd.Timestamp(year, month, 1) + MonthEnd(1)
    else:
        return pd.Timestamp(year, month, day)


def fc(val):
    '''formatCurrency'''
    if not isinstance(val, (float, np.floating)):
        return str(val)
    if val >= 0:
        val = '${:.02f}'.format(val)
    else:
        val = '(${:.02f})'.format(val).replace('-', '')

    return val


def isNumeric(l):
    '''
    Not to be confused with str.isnumeric. Takes an arg or a list and tests if all members are
    numeric types and not NAN.
    '''
    ll = list()
    if not isinstance(l, list):
        ll.append(l)
    else:
        ll = l
    for t in ll:
        if t is None or not isinstance(t, (int, float, np.integer)) or math.isnan(t):
            return False
    return True
