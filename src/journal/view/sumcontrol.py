'''
Instantiate the ui form and create all the needed connections to run it.

Created on April 8, 2019

@author: Mike Petersen
'''


from fractions import Fraction
import os
import re
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QFileDialog, QMessageBox
from PyQt5.QtCore import QSettings, QDate
from PyQt5.QtGui import QFont

import pandas as pd

from journal.view.summaryform import Ui_MainWindow
from journal.view.filesettings import Ui_Dialog as FileSettingsDlg

# pylint: disable = C0103

class FilesettingsControl:
    '''
    A control class for summaryform which is created  maintained by Qt designer
    :Settings-keys: ['theDate', 'setToday', scheme', 'journal', 'dasInfile, 'ibInfile', outdir]
    ''' 
    def __init__(self, ui):
        
        self.ui = ui
        self.settings = QSettings('zero_substance', 'structjour')
        now = None
        if self.settings.value('setToday') == "true":
            now = pd.Timestamp.today().date()
            if now.weekday() > 4:
                now = now - pd.Timedelta(days=now.weekday()-4)
            now = QDate(now)
            self.settings.setValue('theDate', now)


        self.ui.targ.textEdited.connect(self.diffTarget)
        self.ui.stop.textEdited.connect(self.stopLoss)
        
        self.ui.actionFileSettings.triggered.connect(self.fileSetDlg)
        self.openDirDlg = None




        self.diffTarget(self.ui.targ.text())
        self.stopLoss(self.ui.stop.text())

    def fileSetDlg(self):
        '''
        The file settings dialog. Top level dialg triggered by File->FileSettings menu. Display
        the current settings (QSetting), define the dialog actions, and store the new settings.
        '''

        # Create the dialog; retrieve and set the settings
        w=QDialog()
        ui = FileSettingsDlg()
        ui.setupUi(w)
        ui.journal.setText(self.settings.value('journal'))
        ui.scheme.setText(self.settings.value('scheme'))
        ui.dasInfile.setText(self.settings.value('dasInfile'))
        ui.dasInfile2.setText(self.settings.value('dasInfile2'))
        ui.ibInfile.setText(self.settings.value('ibInfile'))
        ui.outdir.setText(self.settings.value('outdir'))
        print(self.settings.value('theDate'))
        state = self.settings.value('setToday')
        state = True if state == "true" else False
        ui.theDateCbox.setChecked(state)
        daDate = self.settings.value('theDate')
        if daDate:
            ui.theDate.setDate(daDate)
        

        # Define actions. 
        self.openDirDlg = ui
        ui.journalBtn.pressed.connect(self.setJournalDlg)
        ui.journal.editingFinished.connect(self.setJournalDir)

        ui.scheme.returnPressed.connect(self.setScheme)
        ui.schemeBtn.pressed.connect(self.setSchemeDefault)

        ui.dasInfile.returnPressed.connect(self.setDASInfile)
        ui.dasInfileBtn.pressed.connect(self.setDASInfileName)

        ui.dasInfile2.returnPressed.connect(self.setDASInfile2)
        ui.dasInfile2Btn.pressed.connect(self.setDASInfile2Name)

        ui.ibInfile.returnPressed.connect(self.setIBInfile)
        ui.ibInfileBtn.pressed.connect(self.setIBInfileName)

        ui.outdir.returnPressed.connect(self.setOutdir)

        ui.theDateCbox.clicked.connect(self.setTodayBool)
        ui.theDateBtn.pressed.connect(self.setToday)
        ui.theDate.dateChanged.connect(self.setDate)

        w.exec()

    def setDate(self, daDate):
        '''
        Stores the setting daDate to settings. This is called when
        the date widget changes its date
        '''
        self.settings.setValue('theDate', daDate)

    def setToday(self):
        '''
        Sets the date to today and stores the value in settings
        '''
        now = pd.Timestamp.today().date()
        if now.weekday() > 4:
            now = now - pd.Timedelta(days=now.weekday()-4)
        now = QDate(now)
        self.settings.setValue('theDate', now)
        self.openDirDlg.theDate.setDate(now)


    def setTodayBool(self, val):
        '''
        Stores the radio checkbox setting to set the date to today on opening the program
        '''
        print(val)
        assert isinstance(val, bool)
        # val = True if val =="true" else False
        self.settings.setValue('setToday', val)

    def setOutdir(self):
        outdir = self.openDirDlg.outdir.text()
        outdir = '' if not outdir else outdir
        self.settings.setValue('outdir', outdir)
        outdir = os.path.join(self.getDirectory(), self.openDirDlg.outdir.text())
        # tip = f"<html><head/><body><p><b>{outdir}</b></p></body></html>"
        # self.openDirDlg.outdir.setToolTip(tip)
        self.openDirDlg.outdirLbl.setText(outdir)
        if os.path.exists(outdir):
            self.openDirDlg.outdirLbl.setStyleSheet("color: green;")
        else:
            self.openDirDlg.outdirLbl.setStyleSheet("color: red;")


    def getDirectory(self):
        scheme = self.settings.value('scheme')
        journal = self.settings.value('journal')
        if not scheme or not journal:
            return None
    
        d = self.settings.value('theDate')
        d = pd.Timestamp(d.year(), d.month(), d.day())
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

    def setIBInfileName(self):
        '''Set the default value for ibInfile'''
        defValue = 'Activity{*}.html'
        self.settings.setValue('ibInfile', defValue)
        self.openDirDlg.ibInfile.setText(defValue)
        self.openDirDlg.ibInfile.setStyleSheet("color: black;")


    def setIBInfile(self):
        sedit = self.openDirDlg.ibInfile.text()
        sglob = os.path.split(sedit)[1]
        if sglob and sedit and sedit == sglob:
            self.settings.setValue('ibInfile', sglob)
        elif sglob and sedit and len(sedit) > len(sglob):
            sset = self.settings.value('ibInfile')
            if sset:
                self.openDirDlg.ibInfile.setText(sset)
                return
        rgx = re.sub('{\*}', '.*', sglob)
        d = self.getDirectory()
    
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
            self.openDirDlg.ibInfile.setStyleSheet("color: red;")
        else:
            self.openDirDlg.ibInfile.setStyleSheet("color: green;")
        self.openDirDlg.ibInfile.setText(fname)
        self.settings.setValue('ibInfile', sglob)

        


    def setDASInfile2Name(self):
        fname = self.settings.value('dasInfile2')
        self.openDirDlg.dasInfile2.setText(fname)
        self.openDirDlg.dasInfile2.setStyleSheet("color: black;")

    def setDASInfile2(self):
        inpath = self.getDirectory()
        if not inpath:
            return
        infile2 = self.openDirDlg.dasInfile2.text()
        infile2 = os.path.split(infile2)[1]
        self.settings.setValue('dasInfile2', infile2)
    
        self.openDirDlg.scheme.setStyleSheet("color: black;")
        inpathfile = os.path.join(inpath, infile2)
        if not os.path.exists(inpathfile):
            self.openDirDlg.dasInfile2.setStyleSheet("color: red;")
        else:
            self.openDirDlg.dasInfile2.setStyleSheet("color: green;")
        self.openDirDlg.dasInfile2.setText(inpathfile)


    def setDASInfileName(self):
        fname = self.settings.value('dasInfile')
        self.openDirDlg.dasInfile.setText(fname)
        self.openDirDlg.dasInfile.setStyleSheet("color: black;")
        


    def setDASInfile(self):
        scheme = self.settings.value('scheme')
        journal = self.settings.value('journal')
        infile = self.openDirDlg.dasInfile.text()
        infile = os.path.split(infile)[1]
        self.settings.setValue('dasInfile', infile)
        if not scheme or not journal or not infile:
            return
    
        d = self.settings.value('theDate')
        d = pd.Timestamp(d.year(), d.month(), d.day())
        Year = d.year
        month = d.strftime('%m')
        MONTH = d.strftime('%B')
        day = d.strftime('%d')
        DAY = d.strftime('%A')
        try:
            schemeFmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
            self.openDirDlg.scheme.setStyleSheet("color: black;")
        except KeyError:
            return
        inpathfile = os.path.join(journal, schemeFmt)
        inpathfile = os.path.join(inpathfile, infile)
        if not os.path.exists(inpathfile):
            self.openDirDlg.dasInfile.setStyleSheet("color: red;")
        else:
            self.openDirDlg.dasInfile.setStyleSheet("color: green;")
        self.openDirDlg.dasInfile.setText(inpathfile)
        


    def setTheScheme(self, scheme):
        '''
        Button, LineEdit and Label used to set and display a directory naming scheme.
        '''
        ddate = pd.Timestamp('2019-01-15')
        Year = ddate.year
        month = ddate.strftime('%m')
        MONTH = ddate.strftime('%B')
        day = ddate.strftime('%d')
        DAY = ddate.strftime('%A')
        try:
            schemeFmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
            self.openDirDlg.scheme.setStyleSheet("color: black;")
        except KeyError:
            self.openDirDlg.scheme.setStyleSheet("color: red;")
            schemeFmt = scheme
            
        self.openDirDlg.schemeLbl.setText(schemeFmt)
        self.openDirDlg.scheme.setText(scheme)
        self.settings.setValue('scheme', scheme)

    def setScheme(self):
        '''
        Set the directory naming scheme to the contents of the LineEdit (scheme) 
        '''
        scheme = self.openDirDlg.scheme.text()
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
        '''

        path = QFileDialog.getExistingDirectory(None, "Select Directory")
        self.openDirDlg.journal.setText(path) 
        self.settings.setValue('journal', path)

    def setJournalDir(self):
        path = self.openDirDlg.journal.text()
        if not os.path.exists(path):
            self.openDirDlg.journal.setStyleSheet("color: red;")
        else:
            self.openDirDlg.journal.setStyleSheet("color: black;")
            self.settings.setValue('journal', path)

    def diffTarget(self, val):
        '''
        Set the targDiff to the difference between the target and the actual PL, then 
        call rrCalc
        '''
        diff = 0
        try:
            fval = float(val)
            fpl = float(self.ui.entry1.text())
            diff = fval-fpl
            diff = '{:.02}'.format(diff)
        except ValueError:
            diff = '0'
        self.ui.targDiff.setText(diff)
        self.rrCalc(diff, self.ui.stopDiff.text())

    def stopLoss(self, val):
        '''
        Set the stopDiff to the difference between the stoploss and the actual PL, then 
        call rrCalc
        '''
        diff = 0
        try:
            fval = float(val)
            fpl = float(self.ui.entry1.text())
            diff = fval-fpl
            diff = '{:.02}'.format(diff)
            # diff = str(fval - fpl)
        except ValueError:
            diff = '0'
        self.ui.stopDiff.setText(diff)
        self.rrCalc(self.ui.targDiff.text(), diff)
        self.setMaxLoss()
    
    def rrCalc(self, targDiff = None, slDiff = None):
        '''
        Figure and set the Risk:Reward label
        '''
        targDiff = self.ui.targDiff.text() if not targDiff else targDiff
        slDiff = self.ui.stopDiff.text() if not slDiff else slDiff
        

        try:
            ftarg = float(targDiff)
            fstop = float(slDiff)
            if fstop == 0 or ftarg == 0:
                self.ui.rr.setText('')
                return
        except ValueError:
            self.ui.rr.setText('')
            return

        print(ftarg, fstop)

        dval = abs(ftarg/fstop)

        f = Fraction(dval).limit_denominator(max_denominator=10)
        srr = f'{f.numerator} : {f.denominator}'
        self.ui.rr.setText(srr)

    def setMaxLoss(self):
        slDiff = self.ui.stopDiff.text()
        shares = self.ui.pos.text()
        shares = shares.split(' ')[0]


        try:
            slDiff = float(slDiff)
            shares = int(shares)
        except ValueError:
            return
        
        val = shares * slDiff
        val = '{:.02f}'.format(val)
        self.ui.maxLoss.setText(val)

        # print(ftarg, fstop)



if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    w = QMainWindow()
    formUi = Ui_MainWindow()
    formUi.setupUi(w)
    sc = FilesettingsControl(formUi)
    w.show()
    sys.exit(app.exec_())
    