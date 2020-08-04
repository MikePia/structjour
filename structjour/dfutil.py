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
Created on Oct 19, 2018

@author: Mike Petersen
'''

import pandas as pd
# pylint: disable=C0103


class DataFrameUtil(object):
    '''
    A group of utilities to work with data frames. Methods are class methods and can be used
    without regard to instance.
    '''

    def __init__(self, params):
        '''
        Constructor which may never be used. (but it could be)
        '''

    @classmethod
    def checkRequiredInputFields(cls, dframe, requiredFields):
        '''
        Checks that dframe has the fields in the array requiredFields. Also checks that there are
        no duplicate fields Returns True on success. Raises a ValueError on failure.
        :params dframe: The DataFrame that is being checked.
        :paras requiredFields: The fields that are required.
        '''
        actualFields = dframe.columns
        if len(actualFields) != len(set(actualFields)):
            err = 'Your DataFrame has duplicate columns'
            raise ValueError(err)
        if set(requiredFields) <= (set(actualFields)):
            return True

        else:
            err = '\n\nYour DataFrame is missing some required fields ... Including:\n     '
            err += str((set(requiredFields) - set(actualFields)))
            if 'Date' in str((set(requiredFields) - set(actualFields))):
                err += '\nNote that DAS exports lack a Date field and it must be supplied. \n'
            raise ValueError(err)

    @classmethod
    def createDf(cls, cols, numRow, fill=''):
        '''
        Creates a new DataFrame with the length numRow. Each cell is filled with empty string
        :param cols:  An array or DataFrame to use as the column headers.
        :param numRow:  The number of empty rows to create.
        :params fill: Each cell will be filled with fill.
        :return:        The new DataFrame objet
        '''

        ll = list()
        r = list()

        if isinstance(cols, type(pd.DataFrame())):
            cols = cols.columns
        for _ in range(len(cols)):
            r.append(fill)

        for _ in range(numRow):
            ll.append(r)
        newdf = pd.DataFrame(ll, columns=cols)

        return newdf

    @classmethod
    def addRows(cls, dframe, numRow, fill=''):
        '''
        Adds numRow rows to the end of the DataFrame object dframe'
        :params dframe: A DataFrame to increase in size.
        :params numRow: he number of empty rows to create.
        :params fill: Each cell wil be filled with fill.
        :return: The new DataFrame objet
        '''

        newdf = cls.createDf(dframe, numRow, fill)
        dframe = dframe.append(newdf, ignore_index=True, sort=False)

        return dframe
