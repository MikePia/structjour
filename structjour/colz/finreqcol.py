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
Created on Sep 8, 2019

@author: Mike Petersen

Moved to its own file to avoid a circular dependency
'''
import logging


class FinReqCol(object):
    '''
    Intended to serve as the adapter class for multiple input files. FinReqCol manages the column
    names for the output file. It includes some of the input columns and additional columns  to
    identify seprate trades and sorting. The columns we add are tix, start, bal, sum, dur, and name
    :SeeAlso: journal.thetradeobject.SumReqFields
    '''

    def __init__(self, source='DAS'):

        if source not in ['DAS', 'IB_HTML', 'IB_CSV', 'DB']:
            logging.error("Only DAS IB_HTML and DB are implemented")
            raise ValueError('ERROR: source is not recognized: {source')

        # frcvals are the actual column titles (to be abstracted when we add new input files)
        # frckeys are the abstracted names for use with all file types
        frcvals = ['Tindex', 'Start', 'Time', 'Symb', 'Side', 'Price', 'Qty', 'Balance', 'Account',
                   "PnL", 'Sum', 'Duration', 'Name', 'Date', 'OC', 'Average', 'Commission']
        frckeys = ['tix', 'start', 'time', 'ticker', 'side', 'price', 'shares', 'bal', 'acct',
                   'PL', 'sum', 'dur', 'name', 'date', 'oc', 'avg', 'comm']
        frc = dict(zip(frckeys, frcvals))

        # Address the columns with these attributes instead of strings in frc.
        self.tix = frc['tix']
        self.start = frc['start']
        self.time = frc['time']
        self.ticker = frc['ticker']
        self.side = frc['side']
        self.price = frc['price']
        self.shares = frc['shares']
        self.bal = frc['bal']
        self.acct = frc['acct']
        self.PL = frc['PL']
        self.sum = frc['sum']
        self.dur = frc['dur']
        self.name = frc['name']
        self.date = frc['date']
        self.oc = frc['oc']
        self.avg = frc['avg']
        self.comm = frc['comm']

        # provided for methods that need a list of columns (using e.g. frc.values())
        self.frc = frc
        self.columns = list(frc.values())
