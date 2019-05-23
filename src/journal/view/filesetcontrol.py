import os
import re
import sys

import pandas as pd
from PyQt5.QtWidgets import QApplication, QMenu, QMessageBox, QDialog, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSettings, QUrl, QDate, QDateTime, Qt

from journal.xlimage import XLImage
from journal.view.strategybrowser import Ui_Form
from strategy.strategies import Strategy

from journal.view.filesettings import Ui_Dialog as FileSettingsDlg

from journal.stock.utilities import ManageKeys, getMAKeys, qtime2pd, pd2qtime

# pylint: disable = C0103

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
        fui.journal.setText(self.settings.value('journal'))
        fui.scheme.setText(self.settings.value('scheme'))
        fui.dasInfile.setText(self.settings.value('dasInfile'))
        fui.dasInfile2.setText(self.settings.value('dasInfile2'))
        fui.ibInfile.setText(self.settings.value('ibInfile'))

        if self.settings.value('outdirPolicy') == 'static':
            self.fui.outdirStatic.setChecked(True)
        else:
            self.fui.outdirDefault.setChecked(True)
        self.setOutdir()
        fui.outdir.setText(self.settings.value('outdir'))
        state = self.settings.value('setToday')
        state = True if state == "true" else False
        fui.theDateCbox.setChecked(state)
        daDate = self.settings.value('theDate')
        if not daDate:
            daDate = pd.Timestamp.today()
            self.settings.setValue('theDate', daDate)
        fui.theDate.setDate(daDate)

        # Define actions.
        fui.journalBtn.pressed.connect(self.setJournalDlg)
        fui.journal.returnPressed.connect(self.setJournalDir)

        fui.schemeBtn.pressed.connect(self.setSchemeDefault)
        fui.scheme.returnPressed.connect(self.setScheme)

        fui.dasInfileBtn.pressed.connect(self.setDASInfileName)
        fui.dasInfile.returnPressed.connect(self.setDASInfile)

        fui.dasInfile2Btn.pressed.connect(self.setDASInfile2Name)
        fui.dasInfile2.returnPressed.connect(self.setDASInfile2)

        fui.ibInfileBtn.pressed.connect(self.setIBInfileName)
        fui.ibInfile.returnPressed.connect(self.setIBInfile)

        fui.outdirDefault.clicked.connect(self.setOutdir)
        fui.outdirStatic.clicked.connect(self.setOutdir)
        fui.outdir.returnPressed.connect(self.setOutdir)

        fui.theDateCbox.clicked.connect(self.setTodayBool)
        fui.theDateBtn.pressed.connect(self.setToday)
        fui.theDate.dateChanged.connect(self.setDialogDate)

        fui.okBtn.pressed.connect(self.closeit)

        # self.contextMenus()
        # d = self.settings.value()

        self.exec()

    def closeit(self):
        self.close()
        if self.ui.ibImport.isChecked():
            self.ibDefault(True)
        else:
            self.ui.dasImport.setChecked(True)
            self.dasDefault(True)

    def setDialogDate(self, val):
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
        Call only when file settings dialog (self.fui) is active.
        '''
        now = pd.Timestamp.today().date()
        if now.weekday() > 4:
            now = now - pd.Timedelta(days=now.weekday()-4)
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
        indir = self.getDirectory()
        odd = os.path.join(indir, 'out/')
        self.fui.outdir.setText(odd)
        self.settings.setValue('outdir', odd)
        self.fui.outdir.setFocusPolicy(Qt.NoFocus)

    def setOutdir(self):
        '''
        Call only when file settings dialog (self.fui) is active.
        '''
        outdir = self.fui.outdir.text()
        outpathfile = ''
        if self.fui.outdirStatic.isChecked():
            self.settings.setValue('outdirPolicy', 'static')
            outpathfile = self.fui.outdir.text()
            self.settings.setValue('outdir', outpathfile)
            self.fui.outdir.setFocusPolicy(Qt.TabFocus)
        else:
            self.settings.setValue('outdirPolicy', 'default')
            opf = self.getDirectory()

            outpathfile = os.path.join(opf, 'out') if opf else ''
            self.settings.setValue('outdir', 'out/')
            self.fui.outdir.setText('out/')
            self.fui.outdir.setToolTip(outpathfile)
            self.fui.outdir.setFocusPolicy(Qt.NoFocus)

        if os.path.exists(outpathfile):
            self.fui.outdir.setStyleSheet("color: green;")
        else:
            self.fui.outdir.setStyleSheet("color: red;")

    def setIBInfileName(self):
        '''
        Call only when file settings dialog (self.fui) is active.
        Set the default value for ibInfile.
        '''
        defValue = 'Activity{*}.html'
        self.settings.setValue('ibInfile', defValue)
        self.fui.ibInfile.setText(defValue)
        self.fui.ibInfile.setStyleSheet("color: black;")

    def setIBInfile(self):
        '''
        Call only when file settings dialog (self.fui) is active.
        '''
        sedit = self.fui.ibInfile.text()
        sglob = os.path.split(sedit)[1]
        if sglob and sedit and sedit == sglob:
            self.settings.setValue('ibInfile', sglob)
        elif sglob and sedit and len(sedit) > len(sglob):
            sset = self.settings.value('ibInfile')
            if sset:
                self.fui.ibInfile.setText(sset)
                return
        rgx = re.sub('{\*}', '.*', sglob)
        d = self.getDirectory()

        # What should turn red here????
        if not d or not os.path.exists(d):
            print(f'Cannot locate directory "{d}".')
            return
        fs = list()
        for f in os.listdir(d):
            x = re.search((rgx), f)
            if x:
                fs.append(x.string)
        fname = ''
        if len(fs) > 1:
            msg = '<h3>You have matched multiple files:</h3><ul> '
            for name in fs:
                msg = msg + '<li>' + name + '</li>'
            msg = msg + '</ul><p>Displaying the first</p>'
            msgbx = QMessageBox()
            msgbx.setText(msg)
            msgbx.exec()
            fname = fs[0]

        elif len(fs) == 1:
            fname = fs[0]
        else:
            fname = sglob
        fname = os.path.join(d, fname)
        if not os.path.exists(fname):
            self.fui.ibInfile.setStyleSheet("color: red;")
        else:
            self.fui.ibInfile.setStyleSheet("color: green;")
        self.fui.ibInfile.setText(fname)
        self.settings.setValue('ibInfile', sglob)

    def setDASInfile2Name(self):
        '''
        Call only when file settings dialog (self.fui) is active.
        '''
        fname = self.settings.value('dasInfile2')
        self.fui.dasInfile2.setText(fname)
        self.fui.dasInfile2.setStyleSheet("color: black;")

    def setDASInfile2(self):
        '''
        Call only when file settings dialog (self.fui) is active.
        '''
        inpath = self.getDirectory()
        if not inpath:
            return
        infile2 = self.fui.dasInfile2.text()
        infile2 = os.path.split(infile2)[1]
        self.settings.setValue('dasInfile2', infile2)

        self.fui.scheme.setStyleSheet("color: black;")
        inpathfile = os.path.join(inpath, infile2)
        if not os.path.exists(inpathfile):
            self.fui.dasInfile2.setStyleSheet("color: red;")
        else:
            self.fui.dasInfile2.setStyleSheet("color: green;")
        self.fui.dasInfile2.setText(inpathfile)

    def setDASInfileName(self):
        '''
        Call only when file settings dialog (self.fui) is active.
        '''
        fname = self.settings.value('dasInfile')
        self.fui.dasInfile.setText(fname)
        self.fui.dasInfile.setStyleSheet("color: black;")

    def setDASInfile(self):
        '''
        Call only when file settings dialog (self.fui) is active.
        '''
        scheme = self.settings.value('scheme')
        journal = self.settings.value('journal')
        infile = self.fui.dasInfile.text()
        infile = os.path.split(infile)[1]
        self.settings.setValue('dasInfile', infile)
        if not scheme or not journal or not infile:
            return

        d = self.settings.value('theDate')
        if isinstance(d, (QDate, QDateTime)):
            d = qtime2pd(d)
        Year = d.year
        month = d.strftime('%m')
        MONTH = d.strftime('%B')
        day = d.strftime('%d')
        DAY = d.strftime('%A')
        try:
            schemeFmt = scheme.format(
                Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
            self.fui.scheme.setStyleSheet("color: black;")
        except KeyError:
            return
        inpathfile = os.path.join(journal, schemeFmt)
        inpathfile = os.path.join(inpathfile, infile)
        if not os.path.exists(inpathfile):
            self.fui.dasInfile.setStyleSheet("color: red;")
        else:
            self.fui.dasInfile.setStyleSheet("color: green;")
        self.fui.dasInfile.setText(inpathfile)

    def setTheScheme(self, scheme):
        '''
        Button, LineEdit and Label used to set and display a directory naming scheme.
        Call only when file settings dialog (self.fui) is active.
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
            schemeFmt = scheme.format(
                Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
            self.fui.scheme.setStyleSheet("color: black;")
        except (KeyError, ValueError):
            self.fui.scheme.setStyleSheet("color: red;")
            schemeFmt = scheme

        self.fui.schemeLbl.setText(schemeFmt)
        self.fui.scheme.setText(scheme)
        self.settings.setValue('scheme', scheme)

    def setScheme(self):
        '''
        Set the directory naming scheme to the contents of the LineEdit (scheme) 
        Call only when file settings dialog (self.fui) is active.
        '''
        scheme = self.fui.scheme.text()
        self.setTheScheme(scheme)

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
        Call only when file settings dialog (self.fui) is active.
        '''

        path = QFileDialog.getExistingDirectory(None, "Select Directory")
        self.fui.journal.setText(path)
        self.settings.setValue('journal', path)

    def setJournalDir(self):
        path = self.fui.journal.text()
        if not os.path.exists(path):
            self.fui.journal.setStyleSheet("color: red;")
        else:
            self.fui.journal.setStyleSheet("color: green;")
            self.settings.setValue('journal', path)

    #============== DUPLICATED WHILE MOVING STUFF ================== FIX LATER =======

    def getDirectory(self):

        scheme = self.settings.value('scheme')
        journal = self.settings.value('journal')
        if not scheme or not journal:
            return None

        d = self.settings.value('theDate')
        if isinstance(d, (QDate, QDateTime)):
            d = qtime2pd(d)
        Year = d.year
        month = d.strftime('%m')
        MONTH = d.strftime('%B')
        day = d.strftime('%d')
        DAY = d.strftime('%A')
        try:
            schemeFmt = scheme.format(
                Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
        except KeyError:
            return None
        inpath = os.path.join(journal, schemeFmt)
        return inpath

    def getOutdir(self):
        op = self.settings.value('outdirPolicy')
        if op == 'static':
            return self.settings.value('outdir')
        outdir = os.path.join(self.getDirectory(), 'out/')
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        return outdir


if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    apisettings = QSettings('zero_substance', 'structjour')
    w = FileSetCtrl(apisettings)
    sys.exit(app.exec_())