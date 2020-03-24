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
