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
from PyQt5.QtCore import QSettings, QDate, QDateTime, Qt
from PyQt5.QtGui import QDoubleValidator, QPixmap

import pandas as pd

from journal.view.summaryform import Ui_MainWindow
from journal.view.filesettings import Ui_Dialog as FileSettingsDlg
from journal.xlimage import XLImage
from journal.stock.graphstuff import FinPlot
from journal.view.sapicontrol import StockApi

# pylint: disable = C0103


def qtime2pd(qdt):
    '''Return a pandas Timestamp from a QDateTime'''
    d = pd.Timestamp(qdt.date().year(),
                     qdt.date().month(),
                     qdt.date().day(),
                     qdt.time().hour(),
                     qdt.time().minute(),
                     qdt.time().second())
    return d

def pd2qtime(pdt):
    '''Return a QDateTime from a time objet of Timestamp'''
    pdt = pd.Timestamp(pdt)
    return QDateTime(pdt.year, pdt.month, pdt.day, pdt. hour, pdt.minute, pdt.second)

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

        self.defaultImage = 'C:/python/E/structjour/src/images/ZeroSubstanceCreation_500x334.png'
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

        # Create connections for widgets on this form
        self.ui.targ.textEdited.connect(self.diffTarget)
        self.ui.stop.textEdited.connect(self.stopLoss)
        self.ui.dateEdit.dateChanged.connect(self.setFormDate)
        self.ui.dasImport.clicked.connect(self.dasDefault)
        self.ui.ibImport.clicked.connect(self.ibDefault)
        self.ui.tradeList.currentTextChanged.connect(self.loadTrade)
        self.ui.lost.textEdited.connect(self.setMstkVal)
        self.ui.sumNote.textChanged.connect(self.setMstkNote)
        self.ui.explain.textChanged.connect(self.setExplain)
        self.ui.notes.textChanged.connect(self.setNotes)
        self.ui.chart1.clicked.connect(self.loadImage1)
        self.ui.chart2.clicked.connect(self.loadImage1)
        self.ui.chart3.clicked.connect(self.loadImage1)
        self.ui.chart1Btn.pressed.connect(self.chartMagic1)
        self.ui.chart2Btn.pressed.connect(self.chartMagic2)
        self.ui.chart3Btn.pressed.connect(self.chartMagic3)
        self.ui.timeHeadBtn.pressed.connect(self.toggleDate)
        self.ui.saveBtn.pressed.connect(self.saveTradeObject)

        v = QDoubleValidator()
        self.ui.lost.setValidator(v)
        self.ui.targ.setValidator(v)
        self.ui.stop.setValidator(v)

        self.ui.actionFileSettings.triggered.connect(self.fileSetDlg)
        self.ui.actionStock_API.triggered.connect(self.stockAPIDlg)

        # Set the file related widgets
        self.ui.dateEdit.setDate(self.settings.value('theDate'))
        self.setFormDate()
        # self.ui.infileEdit.setText(self.getInfile())

        # These are trade related widgets and won't remain here. These are callback handlers from
        # edit boxes-- calling them manually here.
        self.diffTarget(self.ui.targ.text())
        self.stopLoss(self.ui.stop.text())

    # =================================================================
    # ==================== Main Form  methods =========================
    # =================================================================

    def saveTradeObject(self):
        outpathfile = self.getSaveName()
        if os.path.exists(outpathfile):
            print(
                'Should probably pop up here and warn user they are overwriting a save.')
        print(outpathfile)
        print()
        self.lf.saveTheTradeObject(outpathfile)

    def getSaveName(self):
        '''
        This needs to be a name that can be gleaned from the info on the form and settings
        loaded for each file name
        '''
        outdir = self.getOutdir()
        infile = self.ui.infileEdit.text()
        p, infile = os.path.split(infile)

        outf, ext = os.path.splitext(infile)
        outf = "." + outf + '.zst'
        outpathfile = os.path.join(outdir, outf)
        return outpathfile

    def loadImageFromFile(self, widg, name):
        if not os.path.exists(name):
            name = self.defaultImage
        widg.setPixmap(QPixmap(name))

    def chartMage(self, swidg, ewidg, iwidg, nwidg, widg, c):
        fp = FinPlot()
        fp.randomStyle = True
        begin = qtime2pd(swidg.dateTime())
        end = qtime2pd(ewidg.dateTime())
        (dummy, rules, apilist) = fp.apiChooserList(begin, end, fp.api)
        if apilist:
            fp.api = apilist[0]
        interval = iwidg.value()
        name = nwidg.text()
        outdir = self.getOutdir()
        ticker = self.ui.tradeList.currentText().split(' ')[1]
        pname = os.path.join(outdir, name)

        pname = fp.graph_candlestick(ticker, begin, end, interval, save=pname)
        if pname:
            pixmap = QPixmap(pname)
            widg.setPixmap(pixmap)
            data = [pname, begin, end, interval]
            key = self.ui.tradeList.currentText()
            self.lf.setChartData(key, data, c)
            p, fname = os.path.split(pname)
            nwidg.setText(fname)
            return pname
        return None

    def chartMagic1(self):
        pname = self.chartMage(self.ui.chart1Start, self.ui.chart1End, self.ui.chart1Interval,
                               self.ui.chart1Name, self.ui.chart1, 'chart1')
        if pname:
            self.settings.setValue('chart1', pname)

    def chartMagic2(self):
        pname = self.chartMage(self.ui.chart2Start, self.ui.chart2End, self.ui.chart2Interval,
                               self.ui.chart2Name, self.ui.chart2, 'chart2')
        if pname:
            self.settings.setValue('chart2', pname)

    def chartMagic3(self):
        pname = self.chartMage(self.ui.chart3Start, self.ui.chart3End, self.ui.chart3Interval,
                               self.ui.chart3Name, self.ui.chart3, 'chart3')
        if pname:
            self.settings.setValue('chart3', pname)

    def toggleDate(self):
        '''
        Toggles the inclusion of the date with the time in the 8 time entry widgets
        '''
        if not self.lf:
            return
        if self.lf.timeFormat == '%H:%M:%S':
            self.lf.timeFormat = '%m/%d %H:%M:%S'
        else:
            self.lf.timeFormat = '%H:%M:%S'
        print(self.lf.timeFormat)
        key = self.ui.tradeList.currentText()
        self.lf.reloadTimes(key)

    def mousePressEvent(self, event):
        print('mouse Press', (event.x(), event.y()))

    def loadImage1(self, x, event):
        '''
        A signal from ClickLabel
        :params x: The object origin (a ClickLabel object)
        :params event: QContextMenuEvent object

        :Programming Notes:
        The mapTo thing -- Found no docs or discussions in answers.
        None of the other map{To/From}{Parent/Global}({pos/globalPos}) things mapped correctly. By
        Trial and error I finally tried None. That does not seem like it should be right but its
        the only argument to mapTo() that didn't fail quietly-crashing the program. The fact that
        it failed without comment is weird. I am expecting their undocumented code to change.
        '''
        print('loadIm1ge1', x.objectName(), event.pos(), event.globalPos())
        img = x
        cmenu = QMenu(img)

        pi1 = cmenu.addAction("psych 1")
        pi2 = cmenu.addAction("fractal 2")
        pi3 = cmenu.addAction("starry night 3")
        pi4 = cmenu.addAction("Paste from clipboard")

        # This is the line in question and None arg is the crux
        action = cmenu.exec_(self.mapTo(None, event.globalPos()))

        if action == pi1:
            fn = 'C:/python/E/structjour/src/images/psych.jpg'
            x.setPixmap(QPixmap(fn))

        if action == pi2:
            fn = 'C:/python/E/structjour/src/images/fractal-art-fractals.jpg'
            x.setPixmap(QPixmap(fn))

        if action == pi3:
            fn = 'C:/python/E/structjour/src/images/van_gogh-starry-night.jpg'
            x.setPixmap(QPixmap(fn))
        if action == pi4:
            name = ''
            key = self.ui.tradeList.currentText()
            if self.lf:

                name = self.lf.getImageName(key, x.objectName())
            else:
                name = x.objectName() + '_user'

            pname = self.pasteToLabel(x, name)
            if not pname:
                return
            p, nname = os.path.split(pname)
            if nname != name:
                data = self.lf.getChartData(key, x.objectName())
                print()
                data[0] = nname
                self.lf.setChartData(key, data, x.objectName())
            xn = x.objectName()
            if xn == 'chart1':
                self.ui.chart1Name.setText(nname)
            if xn == 'chart2':
                self.ui.chart2Name.setText(nname)
            if xn == 'chart3':
                self.ui.chart3Name.setText(nname)

    def pasteToLabel(self, widg, name):
        '''
        Rather than paste, we call a method that saves the clipboard to a file, then we open it with QPixmap
        '''
        xlimg = XLImage()
        img, pname = xlimg.getPilImageNoDrama(name, self.getOutdir())
        if not img:
            mbox = QMessageBox()
            msg = pname + " Failed to get an image. Please select and copy an image."
            mbox.setText(msg)
            mbox.exec()
            return

        pixmap = QPixmap(pname)
        widg.setPixmap(pixmap)
        return pname

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

    def loadTrade(self, key):
        '''
        CallBack for tradeList -- the combo box. Callback sends currentText-- which is our key
        loading the trade. Can also call it manually. Loads up the trade values when tradeList
        selection changes
        :params key: The trade name and key for the widget collection in Layout Forms
        :Prerequisites: loadLayoutForm must be called before the box is used
        '''
        if not key:
            print('No Val')
            return
        print(key)
        self.lf.populateTradeSumForms(key)

    def setChartTimes(self):
        '''
        Sets the begin and end times from the trade object data
        '''
        key = self.ui.tradeList.currentText()
        c1 = self.lf.getChartData(key, 'chart1')

        self.ui.chart1Name.setText(c1[0])
        self.ui.chart1Start.setDateTime(pd2qtime(c1[1]))
        self.ui.chart1End.setDateTime(pd2qtime(c1[2]))
        self.ui.chart1Interval.setValue(c1[3])

        c2 = self.lf.getChartData(key, 'chart2')

        self.ui.chart2Name.setText(c2[0])
        self.ui.chart2Start.setDateTime(pd2qtime(c2[1]))
        self.ui.chart2End.setDateTime(pd2qtime(c2[2]))
        self.ui.chart2Interval.setValue(c2[3])

        c3 = self.lf.getChartData(key, 'chart3')

        self.ui.chart3Name.setText(c3[0])
        self.ui.chart3Start.setDateTime(pd2qtime(c3[1]))
        self.ui.chart3End.setDateTime(pd2qtime(c3[2]))
        self.ui.chart3Interval.setValue(c3[3])
        # , self.ui.chart1End),
        #           (self.ui.chart2Start, self.ui.chart2End),
        #           (self.ui.chart3Start, self.ui.chart3End)]
        # fp = FinPlot()
        # # for w, interval in zip(wlist, l):
        #     start, finish = fp.setTimeFrame(begin, end, interval)
        #     w[0].setDateTime(start)
        #     w[1].setDateTime(finish)

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
        Callback when dateEdit is changed. Gather the settings and locate whate input files exist.
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
            self.ui.goBtn.setStyleSheet('color:green')
            if inputtype == 'IB_HtmL':
                self.settings.setValue('ibInfileName', infile)
            savename = self.getSaveName()
            if os.path.exists(savename):
                self.ui.infileEdit.setStyleSheet('color: blue;')
                self.ui.loadBtn.setStyleSheet('color: blue;')
            else:
                self.ui.loadBtn.setStyleSheet('color: black;')

        else:
            self.ui.infileEdit.setStyleSheet('color: red;')
            self.ui.goBtn.setStyleSheet('color:black')

        # if ibinfile and os.path.exists(ibinfile):
        #     self.ui.ibImport.setEnabled(True)
        # else:
        #     self.ui.ibImport.setEnabled(False)
        # if dasinfile and os.path.exists(dasinfile):
        #     self.ui.dasImport.setEnabled(True)
        # else:
        #     self.ui.dasImport.setEnabled(False)

    def getInfile(self):
        # TODO Need a choosing mechanism for DAS or IB
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
            (lost, note, clean) = self.lf.setStopVals(
                key, fval, fdiff, rr, mxloss)
            if lost or clean:
                # Note these widgets are only set if the user has not edited either widget. This is
                # the only place they are 'auto set'
                lost = '{:.02f}'.format(lost)
                self.ui.lost.setText(str(lost))
                self.ui.sumNote.setText(note)

    def rrCalc(self, targDiff=None, slDiff=None):
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

    # =================================================================
    # ==================== End Main Form methods =====================
    # =================================================================

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

    # =================================================================
    # ==================== File setting dialog  methods ===============
    # =================================================================

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
        ddate = pd.Timestamp(d.year(), d.month(), d.day())
        Year = ddate.year
        month = ddate.strftime('%m')
        MONTH = ddate.strftime('%B')
        day = ddate.strftime('%d')
        DAY = ddate.strftime('%A')
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

    # =================================================================
    # ================ End File setting dialog  methods ===============
    # =================================================================

    def stockAPIDlg(self):
        '''Fire up the stock Api settings dialog'''
        sapi = StockApi(self.settings)
        sapi.exec()


if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    win = SumControl()
    win.show()
    sys.exit(app.exec_())
