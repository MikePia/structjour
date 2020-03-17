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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

'''
Created on Mar 17, 2020

@author: Mike Petersen
'''
import logging
import os
from datetime import datetime as dt
import sys

from structjour.utilities.backup import Backup
from structjour.view.backupform import Ui_Dialog as BuDlg
from structjour.view.ejcontrol import EJControl

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QApplication


class BackupControl(QDialog):
    '''
    Backup and restore settings and database
    '''
    def __init__(self, settings):
        super(). __init__()

        self.settings = settings
        if not self.settings.value('journal') or not os.path.exists(self.settings.value('journal')):
            EJControl()
        self.rootdir = os.path.normpath(os.path.join(self.settings.value('journal'), 'backup'))
        # self.rootdir = 'C:/trader/journal/backup'

        self.ui = BuDlg()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))

        self.ui.avail_backups.currentTextChanged.connect(self.showFiles)
        self.ui.select_recent.pressed.connect(self.mostRecent)
        self.ui.backup.pressed.connect(self.backup)
        self.ui.restore.pressed.connect(self.restore)
        self.ui.init_settings.pressed.connect(self.initSettings)
        

        if not os.path.exists(self.rootdir):
            self.ui.avail_backups.addItem('(No available backups)')
        else:
            self.fillAvailBackups()
        self.show()

    def mostRecent(self):
        newest = ''
        avail = [self.ui.avail_backups.itemText(i) for i in range(self.ui.avail_backups.count())]
        for d in avail:
            if d.startswith('backup_2'):
                if d > newest:
                    newest = d
        self.ui.avail_backups.setCurrentText(newest)

        # dirs = self.ui.avail_backups.items

    def fillAvailBackups(self):
        self.ui.avail_backups.clear()
        for d in os.listdir(self.rootdir):
            if d.startswith('backup_2'):
                self.ui.avail_backups.addItem(d)
        self.mostRecent()

    def showFiles(self, fn):
        theDir = os.path.join(self.rootdir, fn)
        self.ui.backup_files.clear()
        for f in os.listdir(theDir):
            mtime = dt.utcfromtimestamp(os.path.getmtime(os.path.join(theDir, f))).strftime("%b %d, %Y %H:%M:%S")
            self.ui.backup_files.addItem(f'{f}   {mtime}')

    def backup(self):
        if not self.settings.value('journal') or not os.path.exists(self.settings.value('journal')):
            EJControl()
            self.rootdir = os.path.normpath(os.path.join(self.settings.value('journal'), 'backup'))
        bu = Backup()
        bu.backup()
        self.fillAvailBackups()

    def restore(self):
        if not self.settings.value('journal') or not os.path.exists(self.settings.value('journal')):
            EJControl()
            jdir = self.settings.value('journal')
            self.rootdir = os.path.normpath(os.path.join(jdir, 'backup'))
            if not jdir or not os.path.exists(jdir):
                self.setStatusTip(f'Invalid journal directory: {jdir}')
                logging.error(f'Invalid journal directory {jdir}')

        bu = Backup()
        theDir = os.path.join(self.rootdir, self.ui.avail_backups.currentText())
        bu.restore(theDir=theDir)

    def initSettings(self):
        bu = Backup(backuploc=self.rootdir)
        bu.initializeSettings()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings = QSettings('zero_substance', 'structjour')
    w = BackupControl(settings)
    sys.exit(app.exec_())
