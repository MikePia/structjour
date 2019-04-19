'''
Instantiate the ui form and create all the needed connections to run it.

Created on April 8, 2019

@author: Mike Petersen
'''


from fractions import Fraction
import os
import re
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QFileDialog, QMessageBox, QMenu
from PyQt5.QtCore import QSettings, QDate, Qt
from PyQt5.QtGui import QFont, QDoubleValidator

import pandas as pd

from journal.view.summaryform import Ui_MainWindow
from journal.view.filesettings import Ui_Dialog as FileSettingsDlg
from journal.view.layoutforms import LayoutForms

# pylint: disable = C0103

class SumControl(QMainWindow):
    '''
    A control class for summaryform and its dialogs which are created  maintained by Qt designer.
    The front end object is the ui (self.ui) parameter for SumControl. The file settings dialog
    (fui) is set up in FileSetDlg.
    :Settings-keys: ['theDate', 'setToday', scheme', 'journal', 'dasInfile', 'dasInfile2',
                     'ibInfile', ibInfileName', outdir, 'interval', inputType]
    ''' 
    def __init__(self):
        '''
        Retrieve and load settings, and  create action signals for the SumControl Form.
        :params ui: The QT designer object created from summaryform.ui
        '''
        super().__init__()


        ui = Ui_MainWindow()
        ui.setupUi(self)

        self.lf = None
        self.ui = ui
        self.settings = QSettings('zero_substance', 'structjour')
        self.settings.setValue('runType', 'QT')
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
        self.ui.dateEdit.dateChanged.connect(self.setFormDate)
        self.ui.dasImport.clicked.connect(self.dasDefault)
        self.ui.ibImport.clicked.connect(self.ibDefault)
        self.ui.chart1Min.clicked.connect(self.setCharts1)
        self.ui.chart5Min.clicked.connect(self.setCharts5)
        self.ui.chart15Min.clicked.connect(self.setCharts15)
        self.ui.chart60Min.clicked.connect(self.setCharts60)
        self.ui.tradeList.currentTextChanged.connect(self.loadTrade)
        self.ui.lost.textEdited.connect(self.setMstkVal)
        self.ui.sumNote.textChanged.connect(self.setMstkNote)
        self.ui.explain.textChanged.connect(self.setExplain)
        self.ui.notes.textChanged.connect(self.setNotes)

        v = QDoubleValidator()
        self.ui.lost.setValidator(v)
        self.ui.targ.setValidator(v)
        self.ui.stop.setValidator(v)

        

        
        self.ui.actionFileSettings.triggered.connect(self.fileSetDlg)

        # Set the file related widgets
        self.ui.dateEdit.setDate(self.settings.value('theDate'))
        self.setFormDate()
        # self.ui.infileEdit.setText(self.getInfile())

        # These are trade related widgets and won't remain here. These are callback handlers from
        # edit boxes-- calling them manually here.
        self.diffTarget(self.ui.targ.text())
        self.stopLoss(self.ui.stop.text())

    


    #=================================================================
    #==================== Main Form  methods =========================
    #=================================================================

    def setExplain(self):
       key = self.ui.tradeList.currentText()
       text = self.ui.explain.toPlainText()
       print(text)
       self.lf.setExplain(key, text)

    def setNotes(self):
        key = self.ui.tradeList.currentText()
        text = self.ui.notes.toPlainText()
        print(text)
        self.lf.setNotes(key, text)

    def setMstkVal(self, val):
        note = self.ui.sumNote.toPlainText()
        key = self.ui.tradeList.currentText()
        if not val:
            if not note:
                self.lf.setClean(key, True)
                self.stopLoss(self.ui.stop.text())
            val = 0.0
        else:
            self.lf.setClean(key, False)
        fval = float(val)
        self.lf.setMstkVals(key, fval, note)


    def setMstkNote(self):
        val = self.ui.lost.text()
        note = self.ui.sumNote.toPlainText()
        key = self.ui.tradeList.currentText()
        if not val:
            if not note:
                self.lf.setClean(key, True)
                self.stopLoss(val)
            val = '0.0'
        fval = float(val)
        self.lf.setMstkVals(key, fval, note)
            
    def loadLayoutForms(self, lf):
        self.lf = lf

    def loadTrade(self, val):
        '''
        CallBack for tradeList -- the combo box
        Loads up the trade values when tradeList changes
        :params val: The trade name and key for the widget collection in Layout Forms
        :Prerequisites: loadLayoutForm must be called before the box is used
        '''
        if not val:
            print('No Val')
            return
        print(val)
        self.lf.populateTradeSumForms(val)

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
        self.setFormDate()


    def ibDefault(self, b):
        print('ib', b)
        self.settings.setValue('inputType', 'IB_HTML')
        self.setFormDate()

    def setFormDate(self):
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

        self.settings.setValue('ibInfileName', ibinfile)

        dasinfile = os.path.join(indir, dasinfile) if dasinfile else None
        ibinfile = os.path.join(indir, ibinfile) if ibinfile else None

        infile = None
        inputtype = self.settings.value('inputType')
        if inputtype:
            if inputtype == 'DAS':
                infile = dasinfile
            elif inputtype == 'IB_HTML':
                infile = ibinfile

        # if not infile:
        #     if ibinfile and not dasinfile:
        #         infile = ibinfile
        #     else:
        #         infile = dasinfile
                
        self.ui.infileEdit.setText(infile)
        if os.path.exists(infile):
            self.ui.infileEdit.setStyleSheet('color: green;')
    
        else:
            self.ui.infileEdit.setStyleSheet('color: red;')

        # if ibinfile and os.path.exists(ibinfile):
        #     self.ui.ibImport.setEnabled(True)
        # else:
        #     self.ui.ibImport.setEnabled(False)
        # if dasinfile and os.path.exists(dasinfile):
        #     self.ui.dasImport.setEnabled(True)
        # else:
        #     self.ui.dasImport.setEnabled(False)

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
        Triggered when the targ value changes, set targ, tarDiff and rr. Then store vals in tto
        '''
        # Set the targ, targDiff and rr widgets
        diff = 0
        try:
            fval = float(val)
            fpl = float(self.ui.entry1.text())
            
            fdiff = fval-fpl
            diff = '{:.02f}'.format(fdiff)
        except ValueError:
            diff = '0'
            fdiff = 0.0
            fval = 0.0
        self.ui.targDiff.setText(diff)
        rr = self.rrCalc(fdiff, self.ui.stopDiff.text())

        # Store the values in the trade object
        if self.lf:
            key = self.ui.tradeList.currentText()
            self.lf.setTargVals(key, fval, fdiff, rr)

    def stopLoss(self, val):
        '''
        Set the stopDiff to the difference between the stoploss and the actual PL, then 
        call rrCalc
        '''
        diff = 0
        try:
            fval = float(val)
            fpl = float(self.ui.entry1.text())
            fdiff = fval-fpl
            diff = '{:.02f}'.format(fdiff)
        except ValueError:
            diff = '0'
            fdiff = 0.0
            fval = 0.0
        self.ui.stopDiff.setText(diff)
        rr = self.rrCalc(self.ui.targDiff.text(), fdiff)
        mxloss = self.setMaxLoss()

        if self.lf:
            key = self.ui.tradeList.currentText()
            (lost, note, clean) = self.lf.setStopVals(key, fval, fdiff, rr, mxloss)
            if lost or clean:
                # Note these widgets are only set if the user has not edited either widget. This is
                # the only place they are 'auto set'
                lost = '{:.02f}'.format(lost)
                self.ui.lost.setText(str(lost))
                self.ui.sumNote.setText(note)

    
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
        return srr

    def setMaxLoss(self):
        '''
        Called (manually) when the stop loss is edited, calculate the max loss from the sldiff and
        the number of shares. Not exact--the shares is the max number in the trade, not necessarily
        the initial value. Second opens may or may not increase risk.
        '''

        slDiff = self.ui.stopDiff.text()
        shares = self.ui.pos.text()
        shares = shares.split(' ')[0]
            


        try:
            slDiff = float(slDiff)
            shares = int(shares)
        except ValueError:
            return
        if 'long' in self.ui.tradeList.currentText().lower():
            assert shares > 0
            if slDiff >= 0:
                self.ui.maxLoss.setText('')
                return 0.0
        elif 'short' in self.ui.tradeList.currentText().lower():
            assert shares < 0
            if slDiff <= 0:
                self.ui.maxLoss.setText('')
                return 0.0

        sval = shares * slDiff
        val = '{:.02f}'.format(sval)
        self.ui.maxLoss.setText(val)

        return sval

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

        if self.settings.value('outdirPolicy') == 'static':
            self.fui.outdirStatic.setChecked(True)
        else:
            self.fui.outdirDefault.setChecked(True)
        fui.outdir.setText(self.settings.value('outdir'))
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

        fui.outdirDefault.clicked.connect(self.setOutdir) 
        fui.outdirStatic.clicked.connect(self.setOutdir)
        fui.outdir.returnPressed.connect(self.setOutdir)

        fui.theDateCbox.clicked.connect(self.setTodayBool)
        fui.theDateBtn.pressed.connect(self.setToday)
        fui.theDate.dateChanged.connect(self.setDialogDate)

        fui.okBtn.pressed.connect(self.closeit)

        # self.contextMenus()

        w.exec()

    def contextMenuEvent(self, event):
        img = self.ui.image1
        cmenu = QMenu(img)

        newAct = cmenu.addAction("New")
        opnAct = cmenu.addAction("Open")
        quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == quitAct:
            print('just kidding')

    def closeit(self):
        self.w.close()

    def setDialogDate(self, val):
        print(val)
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
        print(val)
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

            outpathfile = os.path.join(self.getDirectory(), 'out')
            self.settings.setValue('outdir', outpathfile)
            self.fui.outdir.setText(outpathfile)
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
        if not os.path.exists(d):
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
        d = self.settings.value('theDate')
        ddate = pd.Timestamp(d.year(), d.month(), d.day())
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
            self.fui.journal.setStyleSheet("color: green;")
            self.settings.setValue('journal', path)

    #=================================================================
    #================ End File setting dialog  methods ===============
    #=================================================================
   

        # print(ftarg, fstop)



if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    w = SumControl()
    w.show()
    sys.exit(app.exec_())
    