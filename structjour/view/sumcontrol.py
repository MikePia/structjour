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
import logging
import os
import re
import sys
import threading
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QMenu
from PyQt5.QtCore import QSettings, QDate, QDateTime, Qt
from PyQt5.QtGui import QDoubleValidator, QPixmap, QIcon

import pandas as pd

from structjour.inspiration.inspire import Inspire
from structjour.statements.ibstatementdb import StatementDB
from structjour.view.createdirscontrol import CreateDirs
from structjour.view.chartcontrol import ChartControl
from structjour.view.filesetcontrol import FileSetCtrl
from structjour.view.getdatecontrol import GetDate
from structjour.view.ejcontrol import EJControl
from structjour.view.exportexcel import ExportToExcel
from structjour.view.dailycontrol import DailyControl
from structjour.view.sapicontrol import StockApi
from structjour.view.stratcontrol import StratControl
from structjour.view.summaryform import Ui_MainWindow
from structjour.statements.findfiles import checkDateDir, parseDate
from structjour.stock.graphstuff import FinPlot
from structjour.stock.utilities import getMAKeys, qtime2pd, pd2qtime
from structjour.view.duplicatecontrol import DupControl

from structjour.view.disciplinedcontrol import DisciplineControl
from structjour.xlimage import XLImage

from structjour.strategy.strategies import Strategy

# To force the import of the pacakage_data in setup
# from structjour.images import dummy


class SumControl(QMainWindow):
    '''
    A control class for summaryform and its dialogs which are created  maintained by Qt designer.
    The front end object is the ui (self.ui) parameter for SumControl. The file settings dialog
    (fui) is set up in FileSetDlg.
    :Settings-keys: ['theDate', 'setToday', scheme', 'journal', 'dasInfile', 'dasInfile2',
                     'ibInfile', ibInfileName', outdir, 'interval', inputType]
    '''

    def __init__(self, level=logging.DEBUG):
        '''
        Retrieve and load settings, and  create action signals for the SumControl Form.
        :params ui: The QT designer object created from summaryform.ui
        '''
        self.oldDate = None
        super().__init__()

        self.settings = QSettings('zero_substance', 'structjour')
        self.chartSet = QSettings('zero_substance/chart', 'structjour')
        # self.setuplog()
        while(not self.settings.value('journal') or not self.settings.value('structjourDb') or not self.settings.value('tradeDb')):
            self.fileSetDlg()

        self.defaultImage = 'structjour/images/ZeroSubstanceCreation.png'
        ui = Ui_MainWindow()
        ui.setupUi(self)
        self.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))

        self.baseWindowTitle = 'Structjour -- Daily trade review'
        self.lf = None
        self.ui = ui

        self.settings.setValue('runType', 'QT')
        now = None
        self.fui = None
        if self.settings.value('setToday') == "true":
            now = pd.Timestamp.today().date()
            if now.weekday() > 4:
                now = now - pd.Timedelta(days=now.weekday() - 4)
            now = QDate(now)
            self.settings.setValue('theDate', now)
        intype = self.settings.value('inputType')
        if intype:
            if intype == 'DAS':
                self.ui.dasImport.setChecked(True)
            elif intype == 'IB_HTML':
                self.ui.ibImport.setChecked(True)
            elif intype == 'DB' or intype == 'IB_CSV':
                self.ui.useDatabase.setChecked(True)

        pixmap = QPixmap(self.defaultImage)
        self.ui.chart1.setPixmap(pixmap)
        self.ui.chart2.setPixmap(pixmap)
        self.ui.chart3.setPixmap(pixmap)
        # Minimal implementation
        inspire = Inspire()
        quote = inspire.getrandom().replace("\t", "        ")
        self.ui.inspireQuote.setText(quote)
        # Create connections for widgets on this form
        self.ui.inFileBtn.pressed.connect(self.browseInfile)
        self.ui.targ.textEdited.connect(self.diffTarget)
        self.ui.stop.textEdited.connect(self.stopLoss)
        self.ui.dateEdit.dateChanged.connect(self.theDateChanged)
        # self.ui.dateEdit.dateChanged.connect(self.loadFromDate)
        self.ui.dasImport.clicked.connect(self.dasDefault)
        self.ui.ibImport.clicked.connect(self.ibDefault)
        self.ui.useDatabase.clicked.connect(self.useDatabase)

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

        self.ui.inspireQuote.clicked.connect(self.loadInspireQuote)

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
        self.ui.actionDB_Doctor.triggered.connect(self.dbDoctor)
        self.ui.actionChart_Settings.triggered.connect(self.chartSetDlg)
        self.ui.actionExport_TradeLog.triggered.connect(self.disciplineTradeLog)
        self.ui.actionCreate_Directories.triggered.connect(self.createDirDlg)

        # Set the file related widgets
        d = pd.Timestamp.today()
        theDate = self.settings.value('theDate', d)
        self.ui.dateEdit.setDate(theDate)
        self.loadFromDate()

        # These are trade related widgets and won't remain here. These are callback handlers from
        # edit boxes-- calling them manually here.
        self.diffTarget(self.ui.targ.text())
        self.stopLoss(self.ui.stop.text())

    # =================================================================
    # ==================== Main Form  methods =========================
    # =================================================================

    def markDataChanged(self):
        t = self.windowTitle()
        if not t[-1] == '*':
            t += '***'
            self.setWindowTitle(t)

    def browseInfile(self):
        indir = self.getDirectory()
        path = QFileDialog.getOpenFileName(self, "Select Chart", indir,
                                           f'Statements(*.html *.csv))')
        if path[0]:
            self.ui.infileEdit.setText(path[0])
            self.ui.infileEdit.setStyleSheet('color: green;')
            if not checkDateDir(path[0]):
                jdir = self.settings.value('journal')
                jdir = os.path.normpath(jdir)
                infile = os.path.normpath(path[0])
                if not infile.startswith(jdir):
                    getdate = GetDate()
                    getdate.exec()
                    self.ui.dateEdit.setDate(pd2qtime(self.settings.value('theDate'), qdate=True))
                    self.ui.infileEdit.setText(path[0])
                    return

                scheme = self.settings.value('scheme')
                if not jdir or not scheme:
                    return
                d = parseDate(path[0], len(jdir), scheme)
                self.ui.dateEdit.setDate(pd2qtime(d, qdate=True))
                self.ui.infileEdit.setText(path[0])

    def exportExcel(self):
        ''' Signal callback when the exportBtn is pressed. Initiates an export to excel.'''
        if not self.lf:
            logging.info('Nothing to export')
            return
        excel = ExportToExcel(self.lf.ts, self.lf.jf, self.lf.df)
        excel.exportExcel()

    def showDaily(self):
        '''Display the DailyControl form'''
        if not self.lf or self.lf.df is None:
            logging.info('The input file is not loaded')
            return

        # Some programming weirdness here. This dialog was working, then it stopped working. From
        # SO, a modeless dialog needs to be called as self.dialog rather than just dialog. Kind of
        # makes sense and adding self fixed the behavior but does not explain why it used to work.
        self.dControl = DailyControl()
        self.dControl.setModal(False)
        self.dControl.runDialog(self.lf.df, self.lf.ts)
        self.dControl.show()

    def strategyChanged(self, index):
        '''Signal callback when user chooses a strtegy in the strategy combo box'''
        text = self.ui.strategy.currentText()
        if not text:
            return
        self.markDataChanged()
        strat = Strategy()
        allstrats = strat.getStrategies()

        strats = [x[1] for x in allstrats]
        if text not in strats:
            msg = f'Would you like to add the strategy {text} to the database?'
            ok = QMessageBox.question(self, 'New strategy', msg,
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ok == QMessageBox.Yes:
                strat.addStrategy(text)

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

    def saveTradeObject(self, oldDate=None):
        '''Signal call back from saveBtn. Initiates saving the data.'''
        if not self.lf:
            logging.info('Nothing to save')
            return
        outpathfile = self.getSaveName(oldDate)

        self.lf.saveTheTradeObject(outpathfile)
        self.ui.infileEdit.setStyleSheet('color: blue;')
        t = self.windowTitle()
        if t[-1] == '*':
            t = t[:-3]
            self.setWindowTitle(t)

    def getSaveName(self, oldDate=None):
        '''
        This needs to be a name that can be gleaned from the info on the form and settings
        loaded for each file name
        '''
        outdir = self.getOutdir()
        infile = self.ui.infileEdit.text()
        p, infile = os.path.split(infile)

        savename, ext = os.path.splitext(infile)
        d = self.settings.value('theDate')
        d = qtime2pd(d)
        d = pd.Timestamp(d)

        savename = f'''.{savename}{d.strftime('%A_%m%d')}.zst'''
        outpathfile = os.path.join(outdir, savename)
        return outpathfile

    def loadImageFromFile(self, widg, name):
        '''
        Load the image named name into the QLable widget widg. Loads a default image if name does
        not exist. Used to initialize the form.
        '''
        if not os.path.exists(name) or not os.path.isfile(name):
            name = self.defaultImage

        pixmap = QPixmap(name)
        pixmap = pixmap.scaled(widg.width(), widg.height(), Qt.IgnoreAspectRatio)
        widg.setPixmap(pixmap)

    def chartIntervalChanged(self, val, ckey):
        '''Implementation for signals from interval widgets'''
        key = self.ui.tradeList.currentText()
        data = self.lf.getChartData(key, ckey)
        data[3] = val
        self.lf.setChartData(key, data, ckey)

    def chart1IntervalChanged(self):
        '''Signal call back for chart1Interval widget'''
        val = self.ui.chart1Interval.value()
        self.chartIntervalChanged(val, 'chart1')

    def chart2IntervalChanged(self):
        '''Signal call back for chart2Interval widget'''
        val = self.ui.chart2Interval.value()
        self.chartIntervalChanged(val, 'chart2')

    def chart3IntervalChanged(self):
        '''Signal call back for chart3Interval widget'''
        val = self.ui.chart3Interval.value()
        self.chartIntervalChanged(val, 'chart3')

    def resetChartTimes(self, key, swidg, ewidg):
        entries = self.lf.getEntries(key)
        begin = entries[0][3]
        end = entries[-1][3]

        # TODO Remove these arter a month or 2 (2/7/19). In the meantime, open all the
        # imported/updated files (laod files from 10/25/18 on)and update some inserted images on each
        # Or write yet another date babysitter here
        daDate = qtime2pd(self.settings.value('TheDate'))
        datestring = daDate.strftime('%Y-%m-%d')
        if isinstance(begin, str):
            assert len(begin.split(':')) == 3
            # begin = pd.Timestamp(daDate.strftime('%Y-%m-%d ') + begin)
            # end = pd.Timestamp(daDate.strftime('%Y-%m-%d ') + end)
        elif isinstance(begin, pd.Timestamp):
            begin = begin.strftime('%H:%M:%S')
            end = end.strftime('%H:%M:%S')
        else:
            raise ValueError('Programmer alert, add more babysitters here')
        begin = pd.Timestamp(f'{datestring} {begin}')
        end = pd.Timestamp(f'{datestring} {end}')
        swidg.setDateTime(begin)
        ewidg.setDateTime(end)
        return begin, end

    def chartMage(self, swidg, ewidg, iwidg, nwidg, widg, c):
        '''
        Implment the chart retrieval for one of chart1, chart2, or chart3
        :swidg: The start widget for c
        :ewidg: The end widget for c
        :iwidg: The interval widget for c
        :nwidg: The name widget for c
        :widg: The QLabel widget for c
        :c: A string, one of 'chart1, chart2 or chart3'
        '''
        if not self.lf:
            logging.info('No trade to get chart for')
            return None
        key = self.ui.tradeList.currentText()
        if key not in self.lf.ts.keys():
            # Catch pressing update before loading a statement
            return None
        makeys = getMAKeys()
        makeys = makeys[0] if c == 'chart1' else makeys[1] if c == 'chart2' else makeys[2]
        mas = list()
        masl = list()
        for i in range(0, 4):
            val = self.chartSet.value(makeys[i], False, bool)
            if val:
                mas.append(['MA' + str(i + 1), self.chartSet.value(makeys[i + 5]),
                            self.chartSet.value(makeys[i + 9])])
        val = self.chartSet.value(makeys[4], False, bool)
        masl.append(mas)

        if val:
            masl.append(['VWAP', self.chartSet.value(makeys[13])])
        else:
            masl.append([])
        assert len(masl) == 2
        self.chartSet.setValue('getmas', masl)

        fp = FinPlot()
        fp.randomStyle = False
        begin = qtime2pd(swidg.dateTime())
        end = qtime2pd(ewidg.dateTime())
        if qtime2pd(self.settings.value('TheDate')).date() != begin.date():
            begin, end = self.resetChartTimes(key, swidg, ewidg)
        (dummy, rules, apilist) = fp.apiChooserList(begin, end, fp.api)
        if apilist:
            fp.api = apilist[0]
        else:
            # TODO for some reason I cannot figure out, this message box does not work-- it just hangs w/o returning
            # Test it by unchecking all stock apis

            # msg = '<h3>No stock api is selected</h3><ul> '
            msg = ''
            for rule in rules:
                msg = msg + f'<div><strong>Violated rule: {rule}</strong></div>'
            # if not rule:
            #     msg = msg + '<div>Please select Chart API from the menu</div>'

            # title = 'Warning'
            # msgbx = QMessageBox(QMessageBox.Warning, title, msg, QMessageBox.Ok)
            # # msgbx.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))
            # msgbx.exec()
            logging.info(msg)
            return None

        interval = iwidg.value()
        # name = nwidg.text()
        name = self.lf.getImageNameX(key, c)
        outdir = self.getOutdir()
        ticker = self.ui.tradeList.currentText().split(' ')[1]

        pname = os.path.join(outdir, name)

        entries = self.lf.getEntries(key)
        fpentries = list()
        if entries and len(entries[0]) == 6:
            for e in entries:
                etime = e[1]
                diff = etime - begin if (etime > begin) else (begin - etime)

                candleindex = int(diff.total_seconds() / 60 // interval)
                candleindex = -candleindex if etime < begin else candleindex
                L_or_S = 'B'
                if e[2] < 0:
                    L_or_S = 'S'

            fpentries.append([e[0], candleindex, L_or_S, etime])
        else:
            if entries:
                assert len(entries[0]) == 4
            fpentries = entries

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
            # self.markDataChanged()
            self.settings.setValue(c, pname)
            logging.info('Thread returning successful')
            return pname

        apiset = QSettings('zero_substance/stockapi', 'structjour')
        errorCode = apiset.value('errorCode')
        errorMessage = apiset.value('errorMessage')
        if errorMessage:
            mbox = QMessageBox()
            msg = errorCode + '\n' + errorMessage
            mbox.setText(msg)
            mbox.exec()
            apiset.setValue('code', '')
            apiset.setValue('message', '')

        logging.info('Thread returning failed')
        return None

    def chartMagic1(self):
        '''Update button was pressed for chart1. We will get a chart using a stock api'''
        # if not self.lf.ts

        # interactive = self.chartSet.value('interactive', False, type=bool)
        # import matplotlib

        # OK... putting this in a thread caused the runtime error thing tom tkinter
        # (backend for matplotlib at the time). It won't let me load tkagg after qt
        # is loaded.ChartControl. QtAgg works for file but it freezes for interactive

        # self.chartMage(self.ui.chart1Start, self.ui.chart1End, self.ui.chart1Interval,
        #                     self.ui.chart1Name, self.ui.chart1, 'chart1')
        x = threading.Thread(target=self.chartMage,
                            args=(self.ui.chart1Start, self.ui.chart1End, self.ui.chart1Interval,
                            self.ui.chart1Name, self.ui.chart1, 'chart1', ))
        x.start()
        x.join()
        self.markDataChanged()

    def chartMagic2(self):
        '''Update button was pressed for chart2. We will get a chart using a stock api'''
        x = threading.Thread(target=self.chartMage,
                             args=(self.ui.chart2Start, self.ui.chart2End, self.ui.chart2Interval,
                               self.ui.chart2Name, self.ui.chart2, 'chart2'))
        x.start()
        x.join()
        self.markDataChanged()

    def chartMagic3(self):
        '''Update button was pressed for chart3. We will get a chart using a stock api'''
        x = threading.Thread(target=self.chartMage,
                             args=(self.ui.chart3Start, self.ui.chart3End, self.ui.chart3Interval,
                               self.ui.chart3Name, self.ui.chart3, 'chart3'))
        x.start()
        x.join()
        self.markDataChanged()

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
        key = self.ui.tradeList.currentText()
        self.lf.toggleTimeFormat(key)

    def mousePressEvent(self, event):
        '''Overridden'''
        pass

    def getChartWidgets(self, c):
        '''
        Get the associated widgets for c one of chart1, chart2 or chart3. That includes the widgets
        for start, end, interval and name.
        '''
        if c not in ['chart1', 'chart2', 'chart3']:
            return None
        if c == 'chart1':
            widgs = [self.ui.chart1Start, self.ui.chart1End,
                     self.ui.chart1Interval, self.ui.chart1Name]
        elif c == 'chart2':
            widgs = [self.ui.chart2Start, self.ui.chart2End,
                     self.ui.chart2Interval, self.ui.chart2Name]
        elif c == 'chart3':
            widgs = [self.ui.chart3Start, self.ui.chart3End,
                     self.ui.chart3Interval, self.ui.chart3Name]
        return widgs

    def loadInspireQuote(self, x, event):

        img = x
        cmenu = QMenu(img)
        fred = cmenu.addAction('Get a random quote')

        # This is the line in question and None arg is the crux
        action = cmenu.exec_(self.mapTo(None, event.globalPos()))
        if action == fred:
            # self.markDataChanged()
            inspire = Inspire()
            quote = inspire.getrandom().replace("\t", "        ")
            self.ui.inspireQuote.setText(quote)

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
        img = x
        cmenu = QMenu(img)
        key = self.ui.tradeList.currentText()

        # pi1 = cmenu.addAction("psych 1")
        # pi2 = cmenu.addAction("fractal 2")
        # pi3 = cmenu.addAction("starry night 3")
        pastePic = cmenu.addAction("Paste from clipboard")
        browsePic = cmenu.addAction("Browse for chart")
        resetTimes = cmenu.addAction("Reset chart times")

        # This is the line in question and None arg is the crux
        action = cmenu.exec_(self.mapTo(None, event.globalPos()))

        if action in [pastePic, browsePic]:
            self.markDataChanged()

        if action == pastePic:
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
                logging.info('No trade to chart')
                return
            outdir = self.getOutdir()
            tnum = 'Trade' + key.split(' ')[0] + '*'

            filt = self.settings.value('bfilterpref', 0)
            selectedfilter = f'Trade num ({tnum})' if filt else 'Image Files(*.png *.jpg *.jpeg *.bmp)'
            path = QFileDialog.getOpenFileName(self, "Select Chart", outdir,
                                               f'Image Files(*.png *.jpg *.jpeg *.bmp);;Trade num ({tnum})',
                                               selectedfilter)
            filt = 1 if path[1].startswith('Trade num') else 0
            self.settings.setValue('bfilterpref', filt)

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
        elif action == resetTimes:
            entries = self.lf.getEntries(key)
            start = entries[0][3]
            end = entries[-1][3]

            widgs = self.getChartWidgets(x.objectName())
            widgs[0].setDateTime(pd2qtime(start))
            widgs[1].setDateTime(pd2qtime(end))
            self.lf.setChartTimes(key, x.objectName(), [start, end])

    def pasteToLabel(self, widg, name):
        '''Set the given name, to the  QLabel widg. Rather than actually paste, we open the an
        image file as a Qpixmap and set it to the QLabel.
        :widg: A QLabel. It must be one of chart1, chart2 or chart3.
        :name: The name of an image file.
        :return: The name that was set
         '''
        xlimg = XLImage()
        img, pname = xlimg.getPilImageNoDramaForReal(name)
        if not img:
            mbox = QMessageBox()
            msg = pname + " Failed to get an image. Please select and copy an image."
            mbox.setText(msg)
            mbox.exec()
            return None

        pixmap = QPixmap(pname)
        widg.setPixmap(pixmap)
        return pname

    def setExplain(self):
        '''Update self.lf from the explain widget'''
        if not self.lf:
            logging.info('No trades are loaded. Nothing to explain')
            return
        self.markDataChanged()
        key = self.ui.tradeList.currentText()
        text = self.ui.explain.toPlainText()
        self.lf.setExplain(key, text)

    def setNotes(self):
        '''Update self.lf from the notes widget'''
        if not self.lf:
            logging.info('No trades are loaded nothing to analyze.')
            return
        self.markDataChanged()
        key = self.ui.tradeList.currentText()
        text = self.ui.notes.toPlainText()
        self.lf.setNotes(key, text)

    def setMstkVal(self, val):
        if not self.lf:
            logging.info('No trades are loaded.')
            return
        self.markDataChanged()
        note = self.ui.sumNote.toPlainText()
        key = self.ui.tradeList.currentText()
        if not val:
            if not note:
                self.lf.setClean(key, True)
                self.stopLoss(self.ui.stop.text())
            val = 0.0
        else:
            self.lf.setClean(key, False)
        if val in ('-', ''):
            return
        fval = float(val)
        self.lf.setMstkVals(key, fval, note)

    def setMstkNote(self):
        # TODO bug? setting stopLoss
        if not self.lf:
            logging.info('No trades are loaded. Nothing to summarize.')
            return
        self.markDataChanged()
        lostval = self.ui.lost.text()
        note = self.ui.sumNote.toPlainText()
        key = self.ui.tradeList.currentText()
        stopval = self.ui.stop.text()
        if note:
            self.lf.setClean(key, False)
        if not lostval:
            if not note:
                self.lf.setClean(key, True)
                self.stopLoss(stopval)

        try:
            fval = float(lostval)
        except ValueError:
            fval = None
        self.lf.setMstkVals(key, fval, note)

    def loadLayoutForms(self, lf):
        '''Add the layoutForms object to self'''
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

        title = self.windowTitle()
        self.lf.populateTradeSumForms(key)
        self.setWindowTitle(title)

    def loadStrategies(self, strat):
        '''
        Load strategies from database into the strategy Combobox. If the tto stored strategy is not
        in the db, then add it too. Call lf.setStrategy to update the tto
        :strat: THe currently stored strat for this trade
        '''
        if not self.settings.value('structjourDb'):
            logging.info('Cannot load strategies right now')
            return
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
        if not self.lf:
            return
        if strat:
            if not key:
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
        '''Set the self.settings value for input type to DAS'''
        self.ui.infileEdit.setText('')
        self.settings.setValue('inputType', 'DAS')
        self.loadFromDate()

    def ibDefault(self, b):
        '''Set the self.settings value for input type to IB'''
        self.ui.infileEdit.setText('')
        self.settings.setValue('inputType', 'IB_HTML')
        self.loadFromDate()

    def useDatabase(self, b):
        self.settings.setValue('dboutput', 'on')
        self.settings.setValue('inputType', 'DB')
        self.loadFromDate()

        self.settings.setValue('dboutput', 'on')
        self.loadFromDate()

    # def getDBInfileEdTxt(self):

    def saveTradesQuestion(self, oldDate):
        msgBox = QMessageBox()
        msgBox.setIconPixmap(QPixmap("structjour/images/ZSLogo.png"))
        name = self.ui.tradeList.currentText()  # + oldDate.
        oldDate = qtime2pd(oldDate)
        msgBox.setText(f"User data for {name}  on {oldDate.strftime('%A %B %d')} has been modified.")
        msgBox.setInformativeText("Do you want to commit your changes?")
        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Save)
        ret = msgBox.exec()

        if ret == QMessageBox.Save:
            self.saveTradeObject(oldDate)

    def doWeSave(self, yes=False):
        t = self.windowTitle()
        if t[-1] == '*':
            if yes is True:
                self.saveTradeObject(self.oldDate)
            else:
                self.saveTradesQuestion(self.oldDate)

    def theDateChanged(self, val):

        self.doWeSave()

        if self.oldDate and val != self.oldDate:
            self.ui.infileEdit.setText('')
        self.oldDate = val
        self.loadFromDate()

    def loadFromDate(self):
        '''
        Callback when dateEdit is changed. Gather the settings and locate what input files exist.
        Enable/disable radio buttons to choose IB or DAS. Load up the filename in the lineEdit.
        If it exists, green. If not red. If the directory doesn't exist, set blank. If Saved
        file exists override it to blue
        ['theDate', 'setToday', scheme', 'journal', 'dasInfile, 'ibInfile', outdir]
        '''
        if not self.getDirectory():
            # Nothing to load
            return
        infile = None
        daDate = self.ui.dateEdit.date()
        if isinstance(daDate, (QDate, QDateTime)):
            daDate = qtime2pd(daDate)
        self.settings.setValue('theDate', daDate)
        indir = self.getDirectory()
        inputType = self.settings.value('inputType')
        if inputType == 'DAS':
            self.ui.goBtn.setText('Read File')
            lineName = self.ui.infileEdit.text()
            if os.path.exists(lineName):
                self.settings.setValue('dasInfil', lineName)
                infile = lineName
            else:
                infile = self.settings.value('dasInfile')
        elif inputType == 'IB_HTML' or inputType == 'IB_CSV':
            self.ui.goBtn.setText('Read File')
            lineName = self.ui.infileEdit.text()
            if os.path.exists(lineName):
                self.settings.setValue('ibInfileName', lineName)
                infile = lineName
            else:
                ibinfile = self.settings.value('ibInfile')
                infile = self.settings.value('ibInfile')
                sglob = ibinfile
                rgx = re.sub('{\\*}', '.*', sglob)

                fs = list()
                if os.path.exists(indir):
                    for f in os.listdir(indir):
                        x = re.search((rgx), f)
                        if x:
                            fs.append(x.string)
                    if fs:
                        ibinfile = fs[0]
                        infile = fs[0]
                        self.settings.setValue('ibInfileName', ibinfile)
        elif inputType == 'DB':
            infile = 'DB'
            self.ui.goBtn.setText('Read DB Data')
            # dbDate = daDate.strftime('%Y%m%d')
            statementDb = StatementDB()
            count, t_count = statementDb.getNumTicketsforDay(daDate)
            if t_count:
                s = f"{count} DB tickets in {t_count} trades for {daDate.strftime('%A, %B %d, %Y')}"
            else:
                s = f"{count} DB tickets for {daDate.strftime('%A, %B %d, %Y')}"
            self.ui.infileEdit.setText(s)
            if t_count:
                self.ui.infileEdit.setStyleSheet('color: blue;')
                self.ui.loadBtn.setStyleSheet('color: blue;')
                statusstring = "Ready to load trades (press load or change the date)"
            elif count:
                self.ui.infileEdit.setStyleSheet('color: green;')
                self.ui.goBtn.setStyleSheet('color: green;')
                statusstring = "Ready to process transactions (press go or change the date)"
            else:
                self.ui.infileEdit.setStyleSheet('color: red;')
                self.ui.loadBtn.setStyleSheet('color: black;')
                self.ui.goBtn.setStyleSheet('color: black;')
                statusstring = "No tickets or trades have been saved to the DB for this date"
            # statement = statementDb.getStatementDays(account, beg=daDate)
            self.setStatusTip(statusstring)
            self.ui.dateEdit.setToolTip(statusstring)
            self.ui.infileEdit.setToolTip(statusstring)
            return

        if not indir or not infile:
            self.ui.infileEdit.setStyleSheet('color: black;')
            return

        inpathfile = os.path.join(indir, infile) if infile else None
        # dasinfile = os.path.join(indir, dasinfile) if dasinfile else None
        # ibinfile = os.path.join(indir, ibinfile) if ibinfile else None

        # infile = None?
        # if inputtype:
        #     if inputtype == 'DAS':
        #         infile = dasinfile
        #     elif inputtype == 'IB_HTML':
        #         infile = ibinfile

        if not infile:
            return
        self.setColorsAndLabels(inpathfile)

    def setColorsAndLabels(self, infile):
        inputtype = self.settings.value('inputType')
        if inputtype != "DB":
            self.ui.infileEdit.setText(infile)

        statusstring = ''
        if os.path.exists(infile):
            self.ui.infileEdit.setStyleSheet('color: green;')
            self.ui.goBtn.setStyleSheet('color:green')
            if inputtype == 'IB_HtmL':
                self.settings.setValue('ibInfileName', infile)
            savename = self.getSaveName()
            statusstring = 'File ready to open'

            if os.path.exists(savename):
                self.ui.infileEdit.setStyleSheet('color: blue;')
                tm = os.path.getmtime(savename)
                modstring = dt.datetime.fromtimestamp(tm).strftime('%d/%m/%y %H:%M')
                statusstring = f'[{os.path.split(savename)[1]} ({modstring})]   '
                self.ui.loadBtn.setStyleSheet('color: blue;')
                statusstring = statusstring + ' or saved object ready to load.'
            else:
                statusstring = statusstring + '.'
                self.ui.loadBtn.setStyleSheet('color: black;')
                self.ui.loadBtn.setStyleSheet('color: black;')

            d, xlname = os.path.split(savename)
            xlname = os.path.splitext(xlname)[0]
            xlname = xlname[1:] + '.xlsx'
            xlname = os.path.join(d, xlname)
            if os.path.exists(xlname):
                tm = os.path.getmtime(xlname)
                modstring = dt.datetime.fromtimestamp(tm).strftime('%d/%m/%y %H:%M')
                statusstring = statusstring + f'Excel file is saved: {os.path.split(xlname)[1]} ({modstring})]'

        else:
            self.ui.infileEdit.setStyleSheet('color: red;')
            self.ui.goBtn.setStyleSheet('color:black')
            statusstring = f'File {infile} does not exist.'

        self.setStatusTip(statusstring)
        self.ui.dateEdit.setToolTip(statusstring)
        if self.settings.value('outdirPolicy') == 'default':
            outdir = self.getDirectory()
            outdir = os.path.join(outdir, 'out/')
            self.settings.setValue('outdir', outdir)

    def getInfile(self):
        '''Currently unused. If that changes, look for errors'''
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
            logging.info('No trade for which to provide a target price')
            return
        self.markDataChanged()
        diff = 0
        try:
            fval = float(val)
            fpl = float(self.ui.entry1.text())

            fdiff = fval - fpl
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
            logging.info('No trade for which to provide a stop price')
            return
        self.markDataChanged()
        diff = 0
        try:
            fval = float(val)
            fpl = float(self.ui.entry1.text())
            fdiff = fval - fpl
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
                return ''
        except ValueError:
            self.ui.rr.setText('')
            return ''

        dval = abs(ftarg / fstop)

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
            return 0.0
        if 'long' in self.ui.tradeList.currentText().lower():
            # Still not confident in how to treat flipped positions.

            if shares < 0:
                msg = f'Flipped trade retaining long maxLoss attributes {self.ui.tradeList.currentText()}'
                logging.info(msg)
            if slDiff >= 0:
                self.ui.maxLoss.setText('')
                return 0.0
        elif 'short' in self.ui.tradeList.currentText().lower():
            if shares > 0:
                msg = 'Flipped trade retaining short maxLoss attributes', self.ui.tradeList.currentText()
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
        '''
        Get the location of the current input directory. This should correspond to the values
        found in selected date, input file type, journal location and the scheme (from the
        filesettings dlg)
        '''

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
        if self.settings.value('outdirPolicy') == 'default':
            self.settings.setValue('outdir', os.path.join(inpath, 'out/'))
        return inpath

    def getOutdir(self):
        '''Return the location of outdir as found in self.settings'''
        return self.settings.value('outdir', '')

    # =================================================================
    # ==================== File setting dialog  methods ===============
    # =================================================================

    def fileSetDlg(self):
        '''
        The file settings dialog. Top level dialg triggered by File->FileSettings menu. Display
        the current settings (QSetting), define the dialog actions, and store the new settings.
        '''
        w = FileSetCtrl(self.settings)      # noqa:  F841
        try:
            if not self.lf:
                logging.info('No trades loaded')
                return
        except AttributeError:
            logging.info('Fileset Dialog called before setup')
            return
        if self.ui.ibImport.isChecked():
            self.ibDefault(True)
        else:
            self.ui.dasImport.setChecked(True)
            self.dasDefault(True)

    def stockAPIDlg(self):
        '''Fire up the stock Api settings dialog'''
        settings = QSettings('zero_substance/stockapi', 'structjour')
        sapi = StockApi(settings)
        sapi.exec()

    def dbDoctor(self):
        # app = QApplication(sys.argv)
        w = DupControl()
        w.exec()

    def stratBrowseDlg(self):
        '''Show the strategy dialog'''

        # apiset = QSettings('zero_substance/stockapi', 'structjour')
        if not self.settings.value('structjourDb'):
            j = self.settings.value('journal')
            if not j:
                print('Please set the location of the your journal directory.')
                logging.info('Please set the location of the your journal directory.')
                EJControl()
                j = self.settings.value('journal')
                if not j:
                    return
            db = os.path.join(j, 'structjour.sqlite')
            self.settings.setValue('structjourDb', db)
        stratB = StratControl()
        stratB.show()
        stratB.exec()
        self.loadStrategies(None)

    def chartSetDlg(self):
        self.chartDlg = ChartControl(self.chartSet)

    def disciplineTradeLog(self):
        self.w = DisciplineControl()
        self.w.show()

    def createDirDlg(self):
        self.w = CreateDirs()


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
            if len(tsplit) == 3 and s[7].find('min') >= 0:
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
    app = QApplication(sys.argv)
    win = SumControl()
    win.show()
    print(win.getOutdir())
    sys.exit(app.exec_())
