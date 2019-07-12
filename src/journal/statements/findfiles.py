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
Find file utilities to locate statements
@author: Mike Petersen
@creation_data: 07/03/19
'''

import os

import pandas as pd
from PyQt5.QtCore import QSettings, QDate, QDateTime
from journal.stock.utilities import qtime2pd
# pylint: disable = C0103



def getBaseDir(nothing=None):
    '''Get the journal base directory using settings'''
    settings = QSettings('zero_substance', 'structjour')
    journal = settings.value('journal')
    return journal

def getMonthDir(daDate=None):
    '''Get the monthe in the journal subdirs that represents the month from daDate '''

    settings = QSettings('zero_substance', 'structjour')
    if daDate:
        d = daDate
    else:
        d = settings.value('theDate')

    scheme = settings.value('scheme')
    journal = settings.value('journal')
    if not scheme or not journal:
        return None
    scheme = scheme.split('/')[0]

    if isinstance(d, (QDate, QDateTime)):
        d = qtime2pd(d)
    Year = d.year
    month = d.strftime('%m')
    MONTH = d.strftime('%B')
    day = d.strftime('%d')
    DAY = d.strftime('%A')
    try:
        schemeFmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
    except KeyError:
        return None
    inpath = os.path.join(journal, schemeFmt)
    return inpath

def getDirectory(daDate=None):
    '''
    Get the directory in the journal subdirs that represent daDate. Relies on
    the naming scheme saved in settings
    '''
    settings = QSettings('zero_substance', 'structjour')
    if daDate:
        d = pd.Timestamp(daDate)
    else:
        d = settings.value('theDate')

    scheme = settings.value('scheme')
    journal = settings.value('journal')
    if not scheme or not journal:
        return None
    # scheme = scheme.split('/')[0]

    if isinstance(d, (QDate, QDateTime)):
        d = qtime2pd(d)
    Year = d.year
    month = d.strftime('%m')
    MONTH = d.strftime('%B')
    day = d.strftime('%d')
    DAY = d.strftime('%A')
    try:
        schemeFmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
    except KeyError:
        return None
    inpath = os.path.join(journal, schemeFmt)
    return inpath

def findFilesInDir(direct, fn, searchParts):
    '''
    Find the files in direct that match fn, either exactly or including the same parts.
    :direct: The directory to search
    :fn: A filename or file pattern with parts seperated by '.'
    :freq: Either DaiyDir or MonthlyDir. DailyDir will search the daily directories and MonthlyDir
            will search the Monthly directories.
    :searchParts: If False, search for the precise filename. If True search parts seperated by
            '.' and ending with the same extension
    '''
    files = os.listdir(direct)
    found = []
    if searchParts:
        fn, ext = os.path.splitext(fn)
        for f in files:
            parts = fn.split('.')
            countparts = 0
            f = f.lower()
            for part in parts:
                part = part.lower()
                if f.find(part) > -1:
                    countparts = countparts + 1
                    if countparts == len(parts) and f.endswith(ext):
                        found.append(os.path.join(direct, f))
                else:
                    break
    else:
        for f in files:
            if fn == f:
                found.append(os.path.join(direct, f))

    return found

def findFilesInMonth(daDate, fn, searchParts):
    '''
    Match the file in the given month that contain the name fn. Relies on
    the naming scheme saved in settings
    :fn: A filename of file pattern with parts seperated by '.'
    :searchParts: If False, search for the precise filename. If True search parts seperated by
            '.' and ending with the same extension
    '''
    m = daDate
    m = pd.Timestamp(m)
    m = pd.Timestamp(m.year, m.month, 1)
    delt = pd.Timedelta(days=1)
    current = m
    files = []
    currentMonth = current.month
    while True:
        if current.month != currentMonth:
            break
        currentMonth = current.month
        theDir = getDirectory(current)

        if current.weekday() > 4:
            current = current + delt
            continue

        addme = []
        if os.path.exists(theDir):
            addme = findFilesInDir(theDir, fn, searchParts)
        if addme:
            files.extend(addme)

        current = current + delt
    return files

def findFilesSinceMonth(daDate, fn, freq='DailyDir', searchParts=True):
    '''
    Collect the all files in the since daDate in the journal directory that match fn. Relies on
    the naming scheme saved in settings
    :fn: A filename or file pattern with parts seperated by '.'
    :freq: Either DaiyDir or MonthlyDir. DailyDir will search the daily directories and MonthlyDir
            will search the Monthly directories.
    :searchParts: If False, search for the precise filename. If True search parts seperated by
            '.' and ending with the same extension
    '''
    assert freq in ['DailyDir', 'MonthlyDir']
    daDate = pd.Timestamp(daDate)
    now = pd.Timestamp.today()
    thisMonth = pd.Timestamp(now.year, now.month, 1)
    current = pd.Timestamp(daDate.year, daDate.month, 1)
    files = []
    addme = []
    while current <= thisMonth:
        if freq == 'DailyDir':
            addme = findFilesInMonth(current, fn, searchParts)
        else:
            addme = findFilesInDir(getMonthDir(current), fn, searchParts)
        if addme:
            files.extend(addme)
        month = current.month
        if month == 12:
            current = pd.Timestamp(current.year+1, 1, 1)
        else:
            current = pd.Timestamp(current.year, month+1, 1)
    return files
