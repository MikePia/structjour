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
Instantiate the ui form and create all the needed connections to run it.

Created on April 8, 2019

@author: Mike Petersen
'''

import datetime as dt
from fractions import Fraction
import os
import re
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QFileDialog, QMessageBox, QMenu
from PyQt5.QtCore import QSettings, QDate, QDateTime, Qt
from PyQt5.QtGui import QDoubleValidator, QPixmap

import pandas as pd

from journal.view.filesetcontrol import FileSetCtrl
from journal.view.filesettings import Ui_Dialog as FileSettingsDlg
from journal.view.ejcontrol import EJControl
from journal.view.exportexcel import ExportToExcel
from journal.view.dailycontrol import DailyControl
from journal.view.sapicontrol import StockApi
from journal.view.stratcontrol import StratControl
from journal.view.summaryform import Ui_MainWindow
from journal.stock.graphstuff import FinPlot
from journal.stock.utilities import ManageKeys, getMAKeys, qtime2pd, pd2qtime
from journal.xlimage import XLImage

from strategy.strategies import Strategy


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

        self.defaultImage = 'C:/python/E/structjour/src/images/ZeroSubstanceCreation_500x334.png'
        ui = Ui_MainWindow()
        ui.setupUi(self)

        self.lf = None
        self.ui = ui
        self.settings = QSettings('zero_substance', 'structjour')
        mk = ManageKeys(create=True)


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
        self.ui.chart1Interval.editingFinished.connect(self.chart1IntervalChanged)
        self.ui.chart2Interval.editingFinished.connect(self.chart2IntervalChanged)
        self.ui.chart3Interval.editingFinished.connect(self.chart3IntervalChanged)
        self.ui.timeHeadBtn.pressed.connect(self.toggleDate)
        

        self.ui.saveBtn.pressed.connect(self.saveTradeObject)
        self.ui.strategy.currentIndexChanged.connect(self.strategyChanged)

        self.ui.dailySum.pressed.connect(self.showDaily)

        self.ui.exportBtn.pressed.connect(self.exportExcel)

        v = QDoubleValidator()
        self.ui.lost.setValidator(v)
        self.ui.targ.setValidator(v)
        self.ui.stop.setValidator(v)

        self.ui.actionFileSettings.triggered.connect(self.fileSetDlg)
        self.ui.actionStock_API.triggered.connect(self.stockAPIDlg)
        self.ui.actionStrategy_Browser.triggered.connect(self.stratBrowseDlg)

        # Set the file related widgets
        d = pd.Timestamp.today()
        theDate = self.settings.value('theDate', d)
        self.ui.dateEdit.setDate(theDate)
        self.setFormDate()
        # self.ui.infileEdit.setText(self.getInfile())

        # These are trade related widgets and won't remain here. These are callback handlers from
        # edit boxes-- calling them manually here.
        self.diffTarget(self.ui.targ.text())
        self.stopLoss(self.ui.stop.text())

    # =================================================================
    # ==================== Main Form  methods =========================
    # =================================================================


    def exportExcel(self):
        excel = ExportToExcel(self.lf.ts, self.lf.jf, self.lf.df)
        excel.exportExcel()
    
    def showDaily(self):
        if not self.lf or self.lf.df is None:
            print('The input file is not loaded')
            return
        self.dControl = DailyControl()
        self.dControl.runDialog(self.lf.df, self.lf.ts)
        self.dControl.show()

    def strategyChanged(self, index):
        text = self.ui.strategy.currentText()
        if not text:
            return
        strat = Strategy()
        allstrats = strat.getStrategies()
        
        strats = [x[1] for x in allstrats]
        if not text in strats:
            msg = f'Would you like to add the strategy {text} to the database?'
            ok = QMessageBox.question(self, 'New strategy', msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ok == QMessageBox.Yes:
                print('yes clicked.')
            else:
                key = self.ui.tradeList.currentText()
                self.lf.setStrategy(key, text)
                index = self.ui.strategy.findText(text)
                if not index:
                    self.ui.strategy.addItem(text)
                    self.ui.strategy.setCurrentText(text)
    

            self.loadStrategies(text)
        
        key = self.ui.tradeList.currentText()
        self.lf.setStrategy(key, text)

    def saveTradeObject(self):
        if not self.lf:
            print('Nothing to save')
            return
        outpathfile = self.getSaveName()

        self.lf.saveTheTradeObject(outpathfile)
        self.ui.infileEdit.setStyleSheet('color: blue;')

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

        pixmap = QPixmap(name)
        pixmap = pixmap.scaled(widg.width(), widg.height(), Qt.IgnoreAspectRatio)
        widg.setPixmap(pixmap)

    def chartIntervalChanged(self, val, ckey):
        key = self.ui.tradeList.currentText()
        data = self.lf.getChartData(key, ckey)
        data[3] = val
        self.lf.setChartData(key, data, ckey)

    def chart1IntervalChanged(self):
        val = self.ui.chart1Interval.value()
        self.chartIntervalChanged(val, 'chart1')

    def chart2IntervalChanged(self):
        val = self.ui.chart2Interval.value()
        self.chartIntervalChanged(val, 'chart2')

    def chart3IntervalChanged(self):
        val = self.ui.chart3Interval.value()
        self.chartIntervalChanged(val, 'chart3')

    def chartMage(self, swidg, ewidg, iwidg, nwidg, widg, c):
        if not self.lf:
            print('No trade to get chart for')
            return
        chartSet = QSettings('zero_substance/chart', 'structjour')
        makeys = getMAKeys()
        makeys = makeys[0] if c == 'chart1' else makeys[1] if c == 'chart2' else makeys[2]
        mas=list()
        masl=list()
        for i in range(0, 4):
            val = chartSet.value(makeys[i], False, bool)
            if val:
                mas.append(['MA'+str(i+1), chartSet.value(makeys[i+5]), chartSet.value(makeys[i+9])])
        val = chartSet.value(makeys[4], False, bool)
        masl.append(mas)

        if val:
            masl.append(['VWAP', chartSet.value(makeys[13])])
        else:
            masl.append([])
        assert len(masl) == 2
        chartSet.setValue('getmas', masl)


        fp = FinPlot()
        fp.randomStyle = False
        begin = qtime2pd(swidg.dateTime())
        end = qtime2pd(ewidg.dateTime())
        (dummy, rules, apilist) = fp.apiChooserList(begin, end, fp.api)
        if apilist:
            fp.api = apilist[0]
        else:
            print('Another fn pop dialog?. Or pop the dialog here. Please choose a stock api to use. Select stockapi from the file meny.')
            return
        interval = iwidg.value()
        # name = nwidg.text()
        key = self.ui.tradeList.currentText()
        name = self.lf.getImageNameX(key, c)
        outdir = self.getOutdir()
        ticker = self.ui.tradeList.currentText().split(' ')[1]

        pname = os.path.join(outdir, name)

        Long = False
        
        entries = self.lf.getEntries(key)
        fpentries = list()
        for e in entries:
            etime = e[1]
            diff = etime - begin if (etime > begin) else (begin-etime)

            #TODO  Current API all intervals are in minutes. Fix this limitation -- Have to deal
            # with  skipping null after hours data
            candleindex = int(diff.total_seconds()/60//interval)
            candleindex = -candleindex if etime < begin else candleindex
            L_or_S = 'B'
            if e[2] < 0:
                L_or_S = 'S'
            fpentries.append([e[0], candleindex, L_or_S, etime])

        fp.entries = fpentries

        pname = fp.graph_candlestick(ticker, begin, end, interval, save=pname)
        if pname:
            pixmap = QPixmap(pname)
            pixmap = pixmap.scaled(widg.width(), widg.height(), Qt.IgnoreAspectRatio)
            widg.setPixmap(pixmap)
            data = [pname, begin, end, interval]
            self.lf.setChartData(key, data, c)
            p, fname = os.path.split(pname)
            nwidg.setText(fname)
            return pname
        else:
            apiset = QSettings('zero_substance/stockapi', 'structjour')
            errorCode = apiset.value('errorCode')
            errorMessage = apiset.value('errorMessage')
            if not errorMessage:
                errorMessate = "Failed to retrieve data"
            if errorMessage:
                mbox = QMessageBox()
                msg = errorCode + '\n' + errorMessage
                mbox.setText(msg)
                mbox.exec()
                apiset.setValue('code', '')
                apiset.setValue('message', '')

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
        self.lf.toggleTimeFormat(key)

    def mousePressEvent(self, event):
        print('mouse Press', (event.x(), event.y()))

    def getChartWidgets(self, c):
        if c not in ['chart1', 'chart2', 'chart3']:
            return None
        if c == 'chart1':
            widgs = [self.ui.chart1Start, self.ui.chart1End, self.ui.chart1Interval, self.ui.chart1Name]
        elif c == 'chart2':
            widgs = [self.ui.chart2Start, self.ui.chart2End, self.ui.chart2Interval, self.ui.chart2Name]
        if c == 'chart3':
            widgs = [self.ui.chart3Start, self.ui.chart3End, self.ui.chart3Interval, self.ui.chart3Name]
        return widgs
        
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
        key = self.ui.tradeList.currentText()

        pi1 = cmenu.addAction("psych 1")
        pi2 = cmenu.addAction("fractal 2")
        pi3 = cmenu.addAction("starry night 3")
        pi4 = cmenu.addAction("Paste from clipboard")
        browsePic = cmenu.addAction("Browse for chart")

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
            if self.lf:

                name = self.lf.getImageName(key, x.objectName())
            else:
                name = x.objectName() + '_user'

            pname = os.path.join(self.getOutdir(), name)
            pname = self.pasteToLabel(x, pname)
            if not pname:
                return
            p, nname = os.path.split(pname)
            if nname != name:
                data = self.lf.getChartData(key, x.objectName())
                data[0] = nname
                self.lf.setChartData(key, data, x.objectName())
            xn = x.objectName()
            if xn == 'chart1':
                self.ui.chart1Name.setText(nname)
            if xn == 'chart2':
                self.ui.chart2Name.setText(nname)
            if xn == 'chart3':
                self.ui.chart3Name.setText(nname)
        elif action == browsePic:
            if not self.lf:
                print('No trade to chart')
                return
            outdir = self.getOutdir()
            tnum = 'Trade' + key.split(' ')[0] + '*'

            filter = self.settings.value('bfilterpref', 0)
            
            selectedfilter = f'Trade num ({tnum})' if filter else 'Image Files(*.png *.jpg *.bmp)'
            path = QFileDialog.getOpenFileName(self, "Select Chart", outdir, f'Image Files(*.png *.jpg *.bmp);;Trade num ({tnum})', selectedfilter)
            filter = 1 if path[1].startswith('Trade num') else 0
            self.settings.setValue('bfilterpref', filter)
            if path[0]:
                pixmap = QPixmap(path[0])
                pixmap = pixmap.scaled(x.width(), x.height(), Qt.IgnoreAspectRatio)
                x.setPixmap(pixmap)
                d = self.settings.value('theDate')

                data = verifyNameInfo(d, path[0])
                widgs = self.getChartWidgets(x.objectName())
                if data[0]:
                    data[1].insert(0, path[0])
                    data = data[1]
                    widgs[0].setDateTime(pd2qtime(data[1]))
                    widgs[1].setDateTime(pd2qtime(data[2]))
                    widgs[2].setValue(data[3])
                else:
                    data = [path[0], widgs[0].date(), widgs[1].date(), widgs[2].value()]
                

                self.lf.setChartData(key, data, x.objectName())
                # p, fname = os.path.split(pname)
                widgs[3].setText(path[0])

    def pasteToLabel(self, widg, name):
        '''
        Rather than paste, we call a method that saves the clipboard to a file, then we open it with QPixmap
        '''
        xlimg = XLImage()
        img, pname = xlimg.getPilImageNoDramaForReal(name)
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
        if not self.lf:
            print('No trades are loaded. Nothing to explain')
            return
        key = self.ui.tradeList.currentText()
        text = self.ui.explain.toPlainText()
        self.lf.setExplain(key, text)

    def setNotes(self):
        if not self.lf:
            print('No trades are loaded nothing to analyze.')
            return
        key = self.ui.tradeList.currentText()
        text = self.ui.notes.toPlainText()
        self.lf.setNotes(key, text)

    def setMstkVal(self, val):
        if not self.lf:
            print('No trades are loaded.')
            return
        note = self.ui.sumNote.toPlainText()
        key = self.ui.tradeList.currentText()
        if not val:
            if not note:
                self.lf.setClean(key, True)
                self.stopLoss(self.ui.stop.text())
            val = 0.0
        else:
            self.lf.setClean(key, False)
        if val == '-' or val == '':
            return
        fval = float(val)
        self.lf.setMstkVals(key, fval, note)

    def setMstkNote(self):
        if not self.lf:
            print('No trades are loaded. Nothing to summarize.')
            return
        val = self.ui.lost.text()
        note = self.ui.sumNote.toPlainText()
        key = self.ui.tradeList.currentText()
        if note:
            self.lf.setClean(key, False)
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
            return
        self.lf.populateTradeSumForms(key)

    def loadStrategies(self, strat):
        '''
        Load strategies from database into the strategy Combobox. If the tto stored strategy is not
        in the db, then add it too. Call lf.setStrategy to update the tto
        :strat: THe currently stored strat for this trade
        '''
        strats = Strategy()
        stratlist = [x[1] for x in strats.getPreferred()]
        # if strat and not strat in stratlist:
        #     strats.addStrategy(strat)
        #     stratlist = [x[1] for x in strats.getPreferred()]
        self.ui.strategy.clear()
        self.ui.strategy.addItem('')
        for s in stratlist:
            self.ui.strategy.addItem(s)
        if strat:
            index = self.ui.strategy.findText(strat)
            self.ui.strategy.setCurrentIndex(index)

        key = self.ui.tradeList.currentText()
        if self.lf and strat:
            if not key:
                print('I believe this is the right place for the code ')
                return
            self.lf.setStrategy(key, strat)
        if not self.ui.strategy.currentText():
            if strat:
                self.ui.strategy.setCurrentText(strat)
                self.lf.setStrategy(key, strat)
            else:
                val = self.lf.getStrategy(key)
                if val and val != strat:
                    self.ui.strategy.setCurrentText(val)
                    self.lf.setStrategy(key, val)

    def setChartWidgets(self):
        '''
        Sets the begin, end, interval and text widgets for each chart if data found
        '''
        key = self.ui.tradeList.currentText()
        c1 = self.lf.getChartData(key, 'chart1')

        if c1:
            self.ui.chart1Name.setText(c1[0])
            self.ui.chart1Start.setDateTime(pd2qtime(c1[1]))
            self.ui.chart1End.setDateTime(pd2qtime(c1[2]))
            self.ui.chart1Interval.setValue(c1[3])

        c2 = self.lf.getChartData(key, 'chart2')
        if c2:
            self.ui.chart2Name.setText(c2[0])
            self.ui.chart2Start.setDateTime(pd2qtime(c2[1]))
            self.ui.chart2End.setDateTime(pd2qtime(c2[2]))
            self.ui.chart2Interval.setValue(c2[3])

        c3 = self.lf.getChartData(key, 'chart3')
        if c3:
            self.ui.chart3Name.setText(c3[0])
            self.ui.chart3Start.setDateTime(pd2qtime(c3[1]))
            self.ui.chart3End.setDateTime(pd2qtime(c3[2]))
            self.ui.chart3Interval.setValue(c3[3])

    def dasDefault(self, b):
        self.settings.setValue('inputType', 'DAS')
        self.setFormDate()

    def ibDefault(self, b):
        self.settings.setValue('inputType', 'IB_HTML')
        self.setFormDate()

    def setFormDate(self):
        '''
        Callback when dateEdit is changed. Gather the settings and locate what input files exist.
        Enable/disable radio buttons to choose IB or DAS. Load up the filename in the lineEdit.
        If it exists, green. If not red. If the directory doesn't exist, set blank. 
        ['theDate', 'setToday', scheme', 'journal', 'dasInfile, 'ibInfile', outdir]
        '''
        daDate = self.ui.dateEdit.date()
        if isinstance(daDate, (QDate, QDateTime)):
            daDate = qtime2pd(daDate)
        self.settings.setValue('theDate', daDate)
        indir = self.getDirectory()
        dasinfile = self.settings.value('dasInfile')
        ibinfile = self.settings.value('ibInfile')
        if not indir or (not dasinfile and not ibinfile):
            self.ui.infileEdit.setText('')
            self.ui.infileEdit.setStyleSheet('color: black;')
            return
        if ibinfile:
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

        if not infile:
            return

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
        if not self.lf:
            # print('No trade for which to provide a target price')
            return
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
        if not self.lf:
            # print('No trade for which to provide a stop price')
            return
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
                lost = - abs(lost)
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
        return self.settings.value('outdir', '')

    # =================================================================
    # ==================== File setting dialog  methods ===============
    # =================================================================

    def fileSetDlg(self):
        '''
        The file settings dialog. Top level dialg triggered by File->FileSettings menu. Display
        the current settings (QSetting), define the dialog actions, and store the new settings.
        '''
        w = FileSetCtrl(self.settings)
        print('the modal dialog waits to call')
        if not self.lf:
            print('No trades loaded')
            return
        if self.ui.ibImport.isChecked():
            self.ibDefault(True)
        else:
            self.fui.dasImport.setChecked(True)
            self.dasDefault(True)

    def stockAPIDlg(self):
        '''Fire up the stock Api settings dialog'''
        settings = QSettings('zero_substance/stockapi', 'structjour')
        sapi = StockApi(settings)
        sapi.exec()

    def stratBrowseDlg(self):
    
        apiset = QSettings('zero_substance/stockapi', 'structjour')
        if not apiset.value('dbsqlite'):
            j = self.settings.value('journal')
            if not j:
                print('Please set the location of the your journal directory.')
                EJControl()
                j = self.settings.value('journal')
                if not j:
                    return
            db = os.path.join(j, 'structjour.sqlite')
            apiset.setValue('dbsqlite', db)
        stratB = StratControl()
        stratB.show()
        stratB.exec()
        self.loadStrategies(None)

def verifyNameInfo(daDate, s):
    '''
    Test if the chart filename passes this very specific test to verify it has the info required
    in the expected format. No harm no foul if it fails.
    :daDate: The date the chart represents. That info is not in the filename.
    :s: A chart filename.
    :return: (True, [begin, end, interval]) if it passed or (False, []) otherwise.
    '''
    if isinstance(daDate, (QDateTime, QDate)):
        daDate = qtime2pd(daDate)
    if not isinstance(daDate, (pd.Timestamp, dt.datetime)):
        return False, []
    daDate = pd.Timestamp(daDate)
    s = os.path.split(s)[1]
    s = s.split('_')
    if s[0].startswith('Trade') and len(s) > 6:
        if s[2].lower() in ['long', 'short'] and s[5] == 'days' and len(s[3]) == 6:
            tsplit = s[6].split('.')
            if len(tsplit) == 3 and s[7].find('min') >=0:
                try:
                    int(s[3])
                    int(s[4])
                    int(tsplit[0])
                    int(tsplit[1])
                    int(tsplit[2])
                    int(s[7].split('min')[0])

                except ValueError:
                    return False, []
                begin = s[3]
                hour = begin[:2]
                minute = begin[2:4]
                second = begin[-2:]
                d = daDate
                start = pd.Timestamp(d.year, d.month, d.day, int(hour), int(minute), int(second))
                days = s[4]
                delt = pd.Timedelta(days=int(days),
                                    hours=int(tsplit[0]),
                                    minutes=int(tsplit[1]),
                                    seconds=int(tsplit[2]))
                end = start + delt
                interval = int(s[7].split('min')[0])
                
                return True, [start, end, interval]
    return False, []



if __name__ == '__main__':

    # s = 'Trade1_SE_Short_093123_0_days_00.35.37_1min.png'
    # stng = QSettings('zero_substance', 'structjour')
    # ddate = pd.Timestamp('2019-05-24')
    # verifyNameInfo(ddate, s)
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    win = SumControl()
    win.show()
    print(win.getOutdir())
    sys.exit(app.exec_())
