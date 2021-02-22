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
Created on march 11, 2020

@author: Mike Petersen

import migrations to date and provide success check
'''

import logging
# import structjour.migrations._0002_structjour_statement_ibstatementdb as migrate0002
import structjour.migrations._0003_model_trade_sum_dataonly as migrate0003
import structjour.migrations._0004_addTableInspireQuote as migrate0004


def checkMigration(settings):
    if (migrate0003.Migrate.isUpdated() is True) and(
            migrate0004.Migrate.isUpdated() is True):
        logging.info('Database is up to date')
    else:
        logging.error('Failed to update the database')
        if settings.value('tradeDb') is not None:
            raise ValueError('Failed to update the database')
