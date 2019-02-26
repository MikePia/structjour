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
            err = 'Your DataFrame is missing some required fields ... Including:\n     '
            err += str((set(requiredFields) - set(actualFields)))
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
