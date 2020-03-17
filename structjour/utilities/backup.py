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
Created on march 16, 2020

@author: Mike Petersen

Utility to back up database and settings into a dated directory. For now pickle the settings
and copy the sqlite dbs. Will probably have to implement a SQL dump eventually
'''

import logging
import os
import pickle
from shutil import copyfile

import pandas as pd

from PyQt5.QtCore import QSettings


class Backup:
    '''
    A utility to store and restore settings for use in testing. Be careful not to lose data.
    '''
    setname = 'settings.zst'

    def __init__(self, backuploc=None, theDate=None):
        '''
        Store the directory settings in self. The initial strings for the DB are in settings. If initialize is
        called, they are gone. Likeise, restoration will depend on reinitializing settings
        '''

        self.settings = QSettings('zero_substance', 'structjour')
        self.apisettings = QSettings('zero_substance/stockapi', 'structjour')
        self.chartsettings = QSettings('zero_substance/chart', 'structjour')

        if backuploc is None:
            if not os.path.exists(self.settings.value('journal')):
                msg = f"Journal location {self.settings.value('journal')} does not exist"
                logging.error(msg)
                raise ValueError(msg)
            self.rootdir = os.path.normpath(os.path.join(self.settings.value('journal'), 'backup'))
        else:
            self.rootdir = backuploc
        d = pd.Timestamp(theDate) if theDate is not None else pd.Timestamp.now()
        self.bdir = os.path.join(self.rootdir, d.strftime("backup_%Y%m%d_%H.%M.%S"))

        self.bu_settings = os.path.join(self.bdir, self.setname)

        self.dbtrade = self.settings.value('tradeDb')
        self.dbstructjour = self.settings.value('structjourDb')

        self.setkeys = []
        self.setvals = []
        self.apisetkeys = []
        self.apisetvals = []

        # print(self.bu_settings)

    def initializeSettings(self):
        '''
        Remove all settings except zero_substance/structjour/journal
        '''
        for key in self.settings.allKeys():
            if key != 'journal':
                self.settings.remove(key)
        self.apisettings.clear()
        self.chartsettings.clear()
        self.settings.sync()
        self.apisettings.sync()
        self.chartsettings.sync()

    def createDir(self):
        try:
            if not os.path.exists(self.rootdir):
                os.mkdir(self.rootdir)
            if not os.path.exists(self.bdir):
                os.mkdir(self.bdir)
        except Exception as ex:
            logging.error(ex)
            logging.error('Failed to create backup directory. ' + str(ex))
            raise ValueError(ex)
        pass

    def removePickle(self):
        if os.path.exists(self.bu_settings):
            os.remove(self.bu_settings)

    def initializeVars(self):
        self.setkeys = []
        self.setvals = []

        self.apisetkeys = []
        self.apisetvals = []

        self.chartkeys = []
        self.chartvals = []

    def backupDatabase(self, theDir=None):
        '''
        Helper method for restore.
        '''
        self.bdir = self.bdir if theDir is None else theDir
        if not os.path.exists(self.bdir):
            raise ValueError(f'Backup directory {self.bdir} does not exist')

        dbtrade2 = os.path.split(self.dbtrade)[1] 
        dbstructjour2 = os.path.split(self.dbstructjour)[1]
        dbtrade2 = os.path.normpath(os.path.join(self.bdir, dbtrade2))
        dbstructjour2 = os.path.normpath(os.path.join(self.bdir, dbstructjour2))
        copyfile(self.dbtrade, dbtrade2)
        logging.info(f'Trade database has been backed up to {dbtrade2}')
        if dbtrade2 != dbstructjour2:
            copyfile(self.dbstructjour, dbstructjour2)
            logging.info(f'Structjour database has been backed up to {dbstructjour2}')

    def restoreDatabase(self, theDir=None):
        self.bdir = self.bdir if theDir is None else theDir
        if not os.path.exists(self.bdir):
            raise ValueError(f'Backup directory {self.bdir} does not exist.')
        dbtrade = self.settings.value('tradeDb')
        dbstructjour = self.settings.value('structjourDb')

        dbt = os.path.join(self.bdir, os.path.split(dbtrade)[1])
        dbs = os.path.join(self.bdir, os.path.split(dbstructjour)[1])

        if os.path.exists(dbt):
            copyfile(dbt, dbtrade)
            logging.info(f'Db restored {dbt}')
        else:
            logging.error(f'Backup file {dbt} does not exist.')
        if dbs != dbt:
            if os.path.exists(dbs):
                copyfile(dbs, dbstructjour)
                logging.info(f'Db restored {dbs}')
            else:
                logging.error(f'Backup file {dbt} does not exist.')

    def storeSettings(self, replacePickle=False):
        self.createDir()
        if os.path.exists(self.bu_settings):
            if not replacePickle:
                return
        self.initializeVars()
        self.setkeys = self.settings.allKeys()
        for k in self.setkeys:
            self.setvals.append(self.settings.value(k))

        self.apisetkeys = self.apisettings.allKeys()
        for k in self.apisetkeys:
            self.apisetvals.append(self.apisettings.value(k))

        self.chartkeys = self.chartsettings.allKeys()
        for k in self.chartkeys:
            self.chartvals.append(self.chartsettings.value(k))

        setsnkeys = [self.setkeys, self.setvals, self.apisetkeys, self.apisetvals, self.chartkeys, self.chartvals]

        with open(self.bu_settings, "wb") as f:
            '''Cannot pickle qsettings objects- so we pickle a list'''
            pickle.dump((setsnkeys), f)

        logging.info(f'Settings have been backed up to file {self.bu_settings}')

    def restoreSettings(self, theDir=None):
        theDir = self.mostRecent() if theDir is None else theDir
        bu_settings = os.path.join(theDir, self.setname)
        if os.path.exists(bu_settings):
            with open(bu_settings, "rb") as f:
                setsnkeys = pickle.load(f)
                for k, v in zip(setsnkeys[0], setsnkeys[1]):
                    self.settings.setValue(k, v)

                for k2, v2 in zip(setsnkeys[2], setsnkeys[3]):
                    self.apisettings.setValue(k2, v2)

                for k2, v2 in zip(setsnkeys[4], setsnkeys[5]):
                    self.chartsettings.setValue(k2, v2)
            logging.info(f'Settings backed up to file {bu_settings}')

        else:
            logging.error(f'No settings backup found at {bu_settings}')

    def backup(self):
        self.storeSettings()
        self.backupDatabase()

    def restore(self, theDir=None):
        self.bdir = self.mostRecent() if theDir is None else theDir
        self.bdir = os.path.normpath(self.bdir)
        if not os.path.exists(self.bdir):
            raise ValueError(f'Backup directory {self.bdir} does not exist')
        self.restoreSettings(self.bdir)
        self.restoreDatabase(self.bdir)

    def mostRecent(self):

        thedirs = os.listdir(self.rootdir)
        maxdate = ''
        maxdir = None
        for thedir in thedirs:
            if thedir.startswith('backup_2'):
                d = thedir[7:].replace('.', ':')
                if d > maxdate:
                    maxdir = thedir

        return os.path.join(self.rootdir, maxdir) if maxdir is not None else ''


if __name__ == '__main__':
    bu = Backup()
    bu.backup()
    # bu.initialoze()
    # bu.mostRecent()
    # bu.restore('C:\\trader/journal/backup/backup_20200316_12.47.35')
    print()
