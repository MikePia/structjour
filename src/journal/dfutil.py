'''
Created on Oct 19, 2018

@author: Mike Petersen
'''

import pandas as pd


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
    def checkRequiredInputFields(cls, dframe, requiredFields) :
        '''
        Checks that dframe has the fields in the array requiredFields. Also checks that there are no duplicate fields
        Returns True on success. Raises a ValueError on failure.
        :param:dframe:          The DataFrame that is being checked.
        :param:requiredFields:  The fields that are required. 
        '''
        actualFields=dframe.columns
        if len(actualFields) != len(set(actualFields)) :
            err = 'Your DataFrame has duplicate columns'
            raise(ValueError(err))
        if set (requiredFields) <= (set (actualFields)) :
            return True
        else :
            err='Your DataFrame is missing some required fields:\n'
            err += str((set(requiredFields) - set(actualFields)))
            raise ValueError(err)
    
    
    #TODO Change this to create the DataFrame from an array of fields
    @classmethod
    def createDf(cls, dframe, numRow) :
        ''' 
        Creates a new DataFrame with  the length numRow. Each cell is filled with empty string 
        
        :param:dframe:            (Will be) ... An array of the labels to create columns.
        :param:requiredFields:    The number of empty rows to create. 
        :return:                   The new DataFrame objet
        '''
    
        ll=list()
        r=list()
        for _ in range(len(dframe.columns)) :
            r.append('')
            
        for _ in range(numRow) :
            ll.append(r)
        newdf= pd.DataFrame(ll, columns=dframe.columns)
    
        return newdf
    
    @classmethod
    def addRows(cls, dframe, numRow) :
        ''' 
        Adds numRow rows the the DataFrame object dframe'
        
        :param:dframe:            The DataFrame to increase in size 
        :param:requiredFields:    The number of empty rows to create. 
        :return:                   The new DataFrame objet
        '''
        
        newdf= cls.createDf(dframe, numRow)
        dframe = dframe.append(newdf, ignore_index=True, sort=False)
        
        return dframe