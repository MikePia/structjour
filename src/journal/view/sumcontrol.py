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

class SumControl:
    '''
    A control class for summaryform and its dialogs which are created  maintained by Qt designer.
    The front end object is the ui (self.ui) parameter for SumControl. The file settings dialog
    (fui) is set up in FileSetDlg.
    :Settings-keys: ['theDate', 'setToday', scheme', 'journal', 'dasInfile, 'ibInfile', outdir, 
                     'interval']
    ''' 
    def __init__(self, ui):
        '''
        Retrieve and load settings, and  create action signals for the SumControl Form.
        :params ui: The QT designer object created from summaryform.ui
        '''
        
        self.ui = ui
        self.settings = QSettings('zero_substance', 'structjour')
        now = None
        self.fui = None
        if self.settings.value('setToday') == "true":
            now = pd.Timestamp.today().date()
            if now.weekday() > 4:
                now = now - pd.Timedelta(days=now.weekday()-4)
            now = QDate(now)
            self.settings.setValue('theDate', now)
        intype = self.settings.value('inputType')
        if intype:
            if intype == 'DAS':
                self.ui.dasImport.setChecked(True)
            elif intype == 'IB_HTML':
                self.ui.ibImport.setChecked(True)

        charts = {'1': self.ui.chart1Min, '5': self.ui.chart5Min,
                  '15': self.ui.chart15Min, '60': self.ui.chart60Min}
        for x in self.settings.value('interval'):
            charts[x].setChecked(True)
            


        #Create connections for widgets on this form
        self.ui.targ.textEdited.connect(self.diffTarget)
        self.ui.stop.textEdited.connect(self.stopLoss)
        self.ui.dateEdit.editingFinished.connect(self.setDate)
        self.ui.dasImport.clicked.connect(self.dasDefault)
        self.ui.chart1Min.clicked.connect(self.setCharts1)
        self.ui.chart5Min.clicked.connect(self.setCharts5)
        self.ui.chart15Min.clicked.connect(self.setCharts15)
        self.ui.chart60Min.clicked.connect(self.setCharts60)

        self.ui.ibImport.clicked.connect(self.ibDefault)
        
        self.ui.actionFileSettings.triggered.connect(self.fileSetDlg)

        # Set the file related widgets
        self.ui.dateEdit.setDate(self.settings.value('theDate'))
        self.setDate()
        # self.ui.infileEdit.setText(self.getInfile())

        # These are trade related widgets and won't remain here. These are callback handlers from
        # edit boxes-- calling them manually here.
        self.diffTarget(self.ui.targ.text())
        self.stopLoss(self.ui.stop.text())

    


    #=================================================================
    #==================== Main Form  methods =========================
    #=================================================================

    def setCharts1(self, b):
        self.setCharts((self.ui.chart1Min, b))

    def setCharts5(self, b):
        self.setCharts((self.ui.chart5Min, b))

    def setCharts15(self, b):
        self.setCharts((self.ui.chart15Min, b))

    def setCharts60(self, b):
        self.setCharts((self.ui.chart60Min, b))




    def setCharts(self, val):
        print('This is val', val)
        charts = [self.ui.chart1Min, self.ui.chart5Min,
                  self.ui.chart15Min, self.ui.chart60Min]

        t = list()
        for chart in charts:
            print(chart.checkState())
            if chart.checkState():
                t.append(chart)
        if len(t) == 3:
            widg = set(charts) - set(t)
            widg = widg.pop()
            widg.setChecked(False)
            widg.setEnabled(False)

        elif len(t) >= 4:
            #This should never happen but handle it anyway
            val[0].setChecked(False)
            val[0].setEnabled(False)
        elif len(t) < 3:
            for chart in charts:
                chart.setEnabled(True)
        
        interval = list()
        for w in t:
            interval.append(w.text().split()[0])
        self.settings.setValue('interval', interval)





    def dasDefault(self, b):
        print('DAS', b)
        self.settings.setValue('inputType', 'DAS')
        self.setDate()


    def ibDefault(self, b):
        print('ib', b)
        self.settings.setValue('inputType', 'IB_HTML')
        self.setDate()

    def setDate(self):
        '''
        Callback when dataEdit is changed. Gather the settings and locate whate input files exist.
        Enable/disable radio buttons to choose IB or DAS. Load up the filename in the lineEdit.
        If it exists, green. If not red. If the directory doesn't exist, set blank. If both files
        are available choose DAS (for now--That will be a setting configured in filesettings)
        ['theDate', 'setToday', scheme', 'journal', 'dasInfile, 'ibInfile', outdir]
        '''
        daDate = self.ui.dateEdit.date()
        self.settings.setValue('theDate', daDate)
        indir = self.getDirectory()
        dasinfile = self.settings.value('dasInfile')
        ibinfile = self.settings.value('ibInfile')
        if not indir or (not dasinfile and not ibinfile):
            self.ui.infileEdit.setText('')
            self.ui.infileEdit.setStyleSheet('color: black;')
            return




        sglob = ibinfile
        rgx = re.sub('{\*}', '.*', sglob)
    
        fs = list()
        if os.path.exists(indir):
            for f in os.listdir(indir):
                x = re.search((rgx), f)
                if x:
                    fs.append(x.string)
            if fs:
                ibinfile = fs[0]

        dasinfile = os.path.join(indir, dasinfile) if dasinfile else None
        ibinfile = os.path.join(indir, ibinfile) if ibinfile else None

        infile = None
        inputtype = self.settings.value('inputType')
        if inputtype:
            if inputtype == 'DAS':
                infile = dasinfile
            elif inputtype == 'IB_HTML':
                infile = ibinfile

        if not infile:
            if ibinfile and not dasinfile:
                infile = ibinfile
            else:
                infile = dasinfile
                
        self.ui.infileEdit.setText(infile)
        if os.path.exists(infile):
            self.ui.infileEdit.setStyleSheet('color: green;')
    
        else:
            self.ui.infileEdit.setStyleSheet('color: red;')

        if ibinfile and os.path.exists(ibinfile):
            self.ui.ibImport.setEnabled(True)
        else:
            self.ui.ibImport.setEnabled(False)
        if dasinfile and os.path.exists(dasinfile):
            self.ui.dasImport.setEnabled(True)
        else:
            self.ui.dasImport.setEnabled(False)

        



    def getInfile(self):
        #TODO Need a choosing mechanism for DAS or IB
        d = self.getDirectory()
        infile = self.settings.value('dasInfile')
        if not d or not infile:
            return None
        inpathfile = os.path.join(d, infile)
        if os.path.exists(inpathfile):
            return inpathfile
        return None

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

    #=================================================================
    #==================== End Main Form methods =====================
    #=================================================================

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




    #=================================================================
    #==================== File setting dialog  methods ===============
    #=================================================================

    def fileSetDlg(self):
        '''
        The file settings dialog. Top level dialg triggered by File->FileSettings menu. Display
        the current settings (QSetting), define the dialog actions, and store the new settings.
        '''

        # Create the dialog; retrieve and set the settings
        w = QDialog()
        self.w = w
        fui = FileSettingsDlg()
        fui.setupUi(w)
        self.fui = fui
        fui.journal.setText(self.settings.value('journal'))
        fui.scheme.setText(self.settings.value('scheme'))
        fui.dasInfile.setText(self.settings.value('dasInfile'))
        fui.dasInfile2.setText(self.settings.value('dasInfile2'))
        fui.ibInfile.setText(self.settings.value('ibInfile'))
        fui.outdir.setText(self.settings.value('outdir'))
        print(self.settings.value('theDate'))
        state = self.settings.value('setToday')
        state = True if state == "true" else False
        fui.theDateCbox.setChecked(state)
        daDate = self.settings.value('theDate')
        if daDate:
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

        fui.outdir.returnPressed.connect(self.setOutdir)

        fui.theDateCbox.clicked.connect(self.setTodayBool)
        fui.theDateBtn.pressed.connect(self.setToday)
        fui.theDate.dateChanged.connect(self.setDate)

        fui.okBtn.pressed.connect(self.closeit)


        w.exec()

    def closeit(self):
        self.w.close()


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
        print(val)
        assert isinstance(val, bool)
        # val = True if val =="true" else False
        self.settings.setValue('setToday', val)

    def setOutdir(self):
        '''
        Call only when file settings dialog (self.fui) is active.
        '''
        outdir = self.fui.outdir.text()
        outdir = '' if not outdir else outdir
        self.settings.setValue('outdir', outdir)
        outdir = os.path.join(self.getDirectory(), self.fui.outdir.text())
        # tip = f"<html><head/><body><p><b>{outdir}</b></p></body></html>"
        # self.fui.outdir.setToolTip(tip)
        self.fui.outdirLbl.setText(outdir)
        if os.path.exists(outdir):
            self.fui.outdirLbl.setStyleSheet("color: green;")
        else:
            self.fui.outdirLbl.setStyleSheet("color: red;")


    

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
        d = pd.Timestamp(d.year(), d.month(), d.day())
        Year = d.year
        month = d.strftime('%m')
        MONTH = d.strftime('%B')
        day = d.strftime('%d')
        DAY = d.strftime('%A')
        try:
            schemeFmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
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
        ddate = pd.Timestamp('2019-01-15')
        Year = ddate.year
        month = ddate.strftime('%m')
        MONTH = ddate.strftime('%B')
        day = ddate.strftime('%d')
        DAY = ddate.strftime('%A')
        try:
            schemeFmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)
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
            self.fui.journal.setStyleSheet("color: black;")
            self.settings.setValue('journal', path)

    #=================================================================
    #================ End File setting dialog  methods ===============
    #=================================================================
   

        # print(ftarg, fstop)



if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    w = QMainWindow()
    formUi = Ui_MainWindow()
    formUi.setupUi(w)
    sc = SumControl(formUi)
    w.show()
    sys.exit(app.exec_())
    