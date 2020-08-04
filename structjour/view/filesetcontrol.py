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
Created on April 1, 2019

@author: Mike Petersen
'''
import logging
import os
import re
import sys

import pandas as pd
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QFileDialog
from PyQt5.QtCore import QSettings, QDate, QDateTime

from structjour.view.forms.filesettings import Ui_Dialog as FileSettingsDlg

from structjour.stock.utilities import qtime2pd


class FileSetCtrl(QDialog):
    '''
    The file settings dialog. Top level dialg triggered by File->FileSettings menu. Display
    the current settings (QSetting), define the dialog actions, and store the new settings.
    '''
    def __init__(self, settings):
        super().__init__(parent=None)

        self.settings = settings

        # Create the dialog; retrieve and set the settings
        fui = FileSettingsDlg()
        fui.setupUi(self)
        self.fui = fui

        self.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))

        # Define actions.
        fui.journalBtn.pressed.connect(self.setJournalDlg)
        fui.journal.textChanged.connect(self.setJournalDir)

        fui.dasInfileBtn.pressed.connect(self.setDASInfileDefault)
        fui.dasInfile.textChanged.connect(self.setDASInfile)

        fui.dasInfile2Btn.pressed.connect(self.setDASInfile2Default)
        fui.dasInfile2.textChanged.connect(self.setDASInfile2)

        fui.ibInfileBtn.pressed.connect(self.setIBInfileName)
        fui.ibInfile.editingFinished.connect(self.setIBInfile)

        fui.disciplinedBtn.pressed.connect(self.setDisciplinedBrowse)
        fui.disciplinedEdit.textChanged.connect(self.setDisciplined)

        fui.theDateCbox.clicked.connect(self.setTodayBool)
        fui.theDateBtn.pressed.connect(self.setToday)
        fui.theDate.dateChanged.connect(self.setDialogDate)

        fui.okBtn.pressed.connect(self.closeit)

        fui.structjourDbBtn.pressed.connect(self.structjourDbBrowse)
        fui.structjourDbEdit.textChanged.connect(self.structjourDb)
        fui.tradeDbBtn.pressed.connect(self.tradeDbBrowse)
        fui.tradeDbEdit.textChanged.connect(self.tradeDb)

        fui.logfile_browse.pressed.connect(self.logfile_browse)
        fui.logfile_edit.textChanged.connect(self.logfile_edit)

        fui.logfile_level_cb.currentIndexChanged.connect(self.logfile_level)

        fui.journal.setText(self.settings.value('journal'))
        self.setJournalDir()

        self.setScheme()

        fui.dasInfile.setText(self.settings.value('dasInfile'))
        self.setDASInfile()

        fui.dasInfile2.setText(self.settings.value('dasInfile2'))
        self.setDASInfile2()

        fui.ibInfile.setText(self.settings.value('ibInfile'))
        self.setIBInfile()

        fui.disciplinedEdit.setText(self.settings.value('disciplined'))
        self.setDisciplined()

        fui.structjourDbEdit.setText(self.settings.value('structjourDb'))
        self.structjourDb()

        fui.tradeDbEdit.setText(self.settings.value('tradeDb'))
        self.tradeDb()

        fui.logfile_edit.setText(self.settings.value('logfile'))
        self.logfile_edit()

        fui.logfile_level_cb.setCurrentText(self.settings.value('logfile_level', 'Debug'))

        self.setOutdirDefault()
        self.setOutdir()

        state = self.settings.value('setToday')
        state = True if state == "true" else False
        fui.theDateCbox.setChecked(state)
        daDate = self.settings.value('theDate')
        if not daDate:
            daDate = pd.Timestamp.today()
            self.settings.setValue('theDate', daDate)
        fui.theDate.setDate(daDate)

        self.exec()

    def logfile_level(self, x):
        self.settings.setValue('logfile_level', self.fui.logfile_level_cb.currentText())

    def logfile_browse(self):
        '''
        Open a file dialog and set the results to the structjourDbEdit
        '''
        jdir = self.settings.value('journal')
        path = QFileDialog.getSaveFileName(self, "Select structjour db", jdir,
                                           options=QFileDialog.DontConfirmOverwrite)
        if path[0]:
            self.fui.logfile_edit.setText(path[0])
        # self.settings.setValue('structjourDb', path[0])

    def logfile_edit(self):
        '''
        Set the logfile settings from the widget and color the widget text showing existance/not.
        '''
        path = self.fui.logfile_edit.text()
        if not os.path.exists(path):
            self.fui.logfile_edit.setStyleSheet("color: red;")
        else:
            self.fui.logfile_edit.setStyleSheet("color: green;")

        self.settings.setValue('logfile', path)

    def structjourDbBrowse(self):
        '''
        Open a file dialog and set the results to the structjourDbEdit
        '''
        jdir = self.settings.value('journal')
        path = QFileDialog.getSaveFileName(self, "Select structjour db", jdir,
                                           f'Sqlite db(*.db *.sqlite *.sqlite3 *.db3))',
                                           options=QFileDialog.DontConfirmOverwrite)
        if path[0]:
            self.fui.structjourDbEdit.setText(path[0])
        # self.settings.setValue('structjourDb', path[0])

    def structjourDb(self):
        '''
        Set the structjourDB settings from the widget and color the widget text showing existance/not.
        '''
        path = self.fui.structjourDbEdit.text()
        if not os.path.exists(path):
            self.fui.structjourDbEdit.setStyleSheet("color: red;")
        else:
            self.fui.structjourDbEdit.setStyleSheet("color: green;")

        self.settings.setValue('structjourDb', path)

    def tradeDbBrowse(self):
        '''
        Open a file dialog and set the results to the tradeDbEdit
        '''
        jdir = self.settings.value('journal')
        path = QFileDialog.getSaveFileName(self, "Select trade db", jdir,
                                           f'Sqlite db(*db *.sqlite *.sqlite3 *.db3))',
                                           options=QFileDialog.DontConfirmOverwrite)
        if path[0]:
            self.fui.tradeDbEdit.setText(path[0])
        # self.settings.setValue('tradeDb', path[0])

    def tradeDb(self):
        '''
        Set the tradeDB settings from the widget and color the widget text showing existance/not.
        '''
        path = self.fui.tradeDbEdit.text()
        if not os.path.exists(path):
            self.fui.tradeDbEdit.setStyleSheet("color: red;")
        else:
            self.fui.tradeDbEdit.setStyleSheet("color: green;")

        self.settings.setValue('tradeDb', path)

    def setDisciplinedBrowse(self):
        '''
        Open a file browse dialog and set the results to 'disciplinedEdit'.
        '''

        # path = QFileDialog.getExistingDirectory(None, "Select Directory")
        jdir = self.settings.value('journal')
        path = QFileDialog.getOpenFileName(self, "Select Disciplined", jdir, f'Excel(*xlsx))')
        self.fui.disciplinedEdit.setText(path[0])
        self.settings.setValue('disciplined', path[0])

    def setDisciplined(self):
        '''
        Set the disciplined settings from the widget and color the widget text showing existance/not.
        '''
        path = self.fui.disciplinedEdit.text()
        if not os.path.exists(path):
            self.fui.disciplinedEdit.setStyleSheet("color: red;")
        else:
            self.fui.disciplinedEdit.setStyleSheet("color: green;")
            self.settings.setValue('disciplined', path)

    def closeit(self):
        '''Nothing done here'''
        # What needs to be done is in SumControl  -- check either ibImport or dasImport
        self.close()

    def setDialogDate(self, val):
        '''
        Set theDate in settings to the widget value and update everything in the form.
        '''
        self.settings.setValue('theDate', val)
        self.setJournalDir()
        self.setTheScheme(self.settings.value('scheme'))
        self.setDASInfile()
        self.setDASInfile2()
        self.setIBInfile()
        self.setOutdir()

    def setToday(self):
        '''
        Sets the date to today and stores the value in settings
        '''
        now = pd.Timestamp.today().date()
        if now.weekday() > 4:
            now = now - pd.Timedelta(days=now.weekday() - 4)
        now = QDate(now)
        self.settings.setValue('theDate', now)
        self.fui.theDate.setDate(now)

    def setTodayBool(self, val):
        '''
        Stores the radio checkbox setting to set the date to today on opening the program
        '''
        assert isinstance(val, bool)
        # val = True if val =="true" else False
        self.settings.setValue('setToday', val)

    def setOutdirDefault(self):
        '''
        Set the outdir directory for the default outdir. If it exists, set the appropriate label
        green. If not, red. Store the values in settings. Update the widgets.
        '''
        indir = self.getDirectory()
        odd = os.path.join(indir, 'out/')
        self.settings.setValue('outdir', odd)

    def setOutdir(self):
        '''
        Set the outdir and outdir policy settings using the policy and text widgets. Set the label
        color to show existance/not
        '''
        outdir = os.path.join(self.getDirectory(), 'out')
        outdirpath = os.path.abspath(outdir)
        self.settings.setValue('outdir', outdirpath)

    def setIBInfileName(self):
        '''
        Set the default value for ibInfile.
        '''
        defValue = '{*}Activity{*}.csv'
        self.settings.setValue('ibInfile', defValue)
        self.fui.ibInfile.setText(defValue)
        self.fui.ibInfile.setStyleSheet("color: black;")

    def setIBInfile(self):
        '''
        Use the glob in the text widget to find a list of matched input files. Set the settings
        variable to the first one, but warn the user if there are multiple input files.
        '''
        sedit = self.fui.ibInfile.text()
        sglob = os.path.split(sedit)[1]
        self.fui.ibInfile.setStyleSheet("color: black;")
        if not sglob:

            self.fui.ibInfileLbl.setText(self.getDirectory())
            self.fui.ibInfileLbl.setStyleSheet("color: red;")
            self.fui.ibInfile.setStyleSheet("color: red;")
            return
        if sglob and sedit and sedit == sglob:
            self.settings.setValue('ibInfile', sglob)
        elif sglob and sedit and len(sedit) > len(sglob):
            sset = self.settings.value('ibInfile')
            if sset:
                self.fui.ibInfile.setText(sset)
                return
        rgx = re.sub('{\\*}', '.*', sglob)
        rgx = rgx + '$'
        d = self.getDirectory()

        # What should turn red here????
        if not d or not os.path.exists(d):
            logging.warning(f'Cannot locate directory "{d}".')
            self.fui.ibInfileLbl.setText(sedit)
            self.fui.ibInfileLbl.setStyleSheet("color: red;")
            return
        fs = list()
        for f in os.listdir(d):
            x = re.search((rgx), f)
            if x:
                fs.append(x.string)
        fname = ''
        if len(fs) > 1:
            title = 'Matched Files'
            msg = '<h3>You have matched multiple files:</h3><ul> '
            for name in fs:
                msg = msg + '<li>' + name + '</li>'
            msg = msg + '</ul><p>Displaying the first</p>'
            msgbx = QMessageBox(QMessageBox.Information, title, msg, QMessageBox.Ok)
            msgbx.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))
            # msgbx.setText(msg)
            msgbx.exec()
            fname = fs[0]

        elif len(fs) == 1:
            fname = fs[0]
        else:
            fname = sglob
        fpathname = os.path.join(d, fname)
        if not os.path.exists(fpathname):
            self.fui.ibInfileLbl.setStyleSheet("color: red;")
        else:
            self.fui.ibInfileLbl.setStyleSheet("color: green;")
        self.fui.ibInfileLbl.setText(fpathname)
        self.settings.setValue('ibInfile', sglob)

    def setDASInfile2Name(self):
        '''
       dasinfile2 refers to the positions csv file exported from DAS Trader Pro. Set the settings
       from the widget.
        '''
        fname = self.settings.value('dasInfile2')
        self.fui.dasInfile2.setText(fname)
        self.fui.dasInfile2.setStyleSheet("color: black;")

    def setDASInfile2Default(self):
        '''Set the default name of 'positions.csv'''
        self.fui.dasInfile2.setText('positions.csv')

    def setDASInfile2(self):
        '''Set the default name of positions.csv'''
        fname = self.fui.dasInfile2.text()
        dasInfile2Lbl = os.path.join(self.getDirectory(), fname)
        self.fui.dasInfile2Lbl.setText(dasInfile2Lbl)
        if os.path.exists(dasInfile2Lbl):
            self.fui.dasInfile2Lbl.setStyleSheet("color: green;")
        else:
            self.fui.dasInfile2Lbl.setStyleSheet("color: red;")
        self.settings.setValue('dasInfile2', fname)

    def setDASInfileDefault(self):
        '''Set the default name of trades.csv'''
        self.fui.dasInfile.setText('trades.csv')

    def setDASInfile(self):
        '''
        Set the lable widget from the text widget and color the label to show existance/not
        '''
        fname = self.fui.dasInfile.text()
        # if not self.getDirectory():
        #     return
        dasInfileLbl = os.path.join(self.getDirectory(), fname)
        self.fui.dasInfileLbl.setText(dasInfileLbl)
        if os.path.exists(dasInfileLbl):
            self.fui.dasInfileLbl.setStyleSheet("color: green;")
        else:
            self.fui.dasInfileLbl.setStyleSheet("color: red;")
        self.settings.setValue('dasInfile', fname)

    def setTheScheme(self, scheme):
        '''
        Button, LineEdit and Label used to set and display a directory naming scheme.
        '''
        d = self.settings.value('theDate')
        if not d:
            d = pd.Timestamp.today()
        elif isinstance(d, (QDate, QDateTime)):
            d = qtime2pd(d)

        Year = d.year
        month = d.strftime('%m')
        MONTH = d.strftime('%B')
        day = d.strftime('%d')
        DAY = d.strftime('%A')
        try:
            schemeFmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        except (KeyError, ValueError):
            schemeFmt = scheme

        indir = self.fui.journal.text()
        schemeFmt = os.path.join(indir, schemeFmt)
        self.settings.setValue('scheme', scheme)

    def setScheme(self):
        ''' Set the directory naming scheme to the contents of the LineEdit (scheme)'''
        self.setSchemeDefault()

    def setSchemeDefault(self):
        '''
        Set the directory naming scheme to the default value defined here.
        '''
        default = '_{Year}{month}_{MONTH}/_{month}{day}_{DAY}/'
        self.setTheScheme(default)

    def setJournalDlg(self):
        '''
        Open a file dialog and set the results to the QLineEdit 'journal'. Triggered by its
        neighboring button
        '''
        path = QFileDialog.getExistingDirectory(None, "Select Directory")
        self.fui.journal.setText(path)
        self.settings.setValue('journal', path)
        self.setSchemeDefault()

    def setJournalDir(self):
        '''
        Set the journal settings from the widget and color the widget text showing existance/not.
        '''
        path = self.fui.journal.text()
        if not os.path.exists(path):
            self.fui.journal.setStyleSheet("color: red;")
        else:
            self.fui.journal.setStyleSheet("color: green;")
            self.settings.setValue('journal', path)

    # ============== DUPLICATED WHILE MOVING STUFF ================== FIX LATER  or not =======
    # It is convenient having these two nudgy accessors in a more central object. duplication
    # smooplication. Its not that hard or time consuming as long as it is clear.

    def getDirectory(self):
        '''
        Put together the settings for scheme (realized here), journal and theDate to get the indir
        '''

        scheme = self.settings.value('scheme')
        journal = self.settings.value('journal')
        if not scheme or not journal:
            return ''

        d = self.settings.value('theDate')
        if d is None:
            return ''
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

    def getOutdir(self):
        '''
        Retrieve either the static outdir named in settings or get the dynamic defalut directory
        depending on the outdirPolicyin settings.
        '''
        op = self.settings.value('outdirPolicy')
        if op == 'static':
            return self.settings.value('outdir')
        outdir = os.path.join(self.getDirectory(), 'out/')
        if not os.path.exists(outdir):
            os.mkdir(outdir)
            try:
                os.makedirs(outdir)
            except (IOError, OSError) as ex:
                # LOG THIS
                logging.error(ex)
        return outdir


if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings = QSettings('zero_substance', 'structjour')
    w = FileSetCtrl(settings)
    sys.exit(app.exec_())
