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
Created on Apr 4, 2020

@author: Mike Petersen
'''
import sys
import pandas as pd

from structjour.models.trademodels import Tags, TradeSum
from structjour.stock.utilities import pd2qtime
from structjour.view.calendarcontrol import CalendarControl
from structjour.view.charts.chartdatabase import MultiTradeProfit_BarchartData
from structjour.view.charts.generic_barchart import BarChart
from structjour.view.charts.intradayprofit_barchart import Canvas as CanvasDP
from structjour.view.flowlayout import FlowLayout

from structjour.view.forms.statisticshub import Ui_Form as StatHub
from PyQt5.QtCore import QSettings, QDate, Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QLabel, QSpinBox, QHBoxLayout,
                             QComboBox, QSizePolicy)
from PyQt5.QtGui import QFont


class StatitisticsHubControl(QDialog):

    def __init__(self):
        super().__init__()
        self.ui = StatHub()
        self.ui.setupUi(self)
        self.dynamicWidget = None
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)

        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self.cud = {}
        self.initializing = True

        self.ui.symbolEdit.editingFinished.connect(self.selectSymbols)
        self.ui.sideCB.currentTextChanged.connect(self.selectSide)
        self.ui.tagsListWidget.itemPressed.connect(self.selectTag)
        self.ui.tradesBySetsRB.clicked.connect(self.tradesBySetClicked)
        self.ui.tradesByTimeRB.clicked.connect(self.tradesByTimeClicked)
        self.ui.strategyListWidget.itemPressed.connect(self.selectStrategy)

        self.ui.dateRange30Cbox.clicked.connect(self.set30Days)
        self.ui.dateRange60Cbox.clicked.connect(self.set60Days)
        self.ui.dateRange90Cbox.clicked.connect(self.set90Days)
        self.ui.selectStartBtn.pressed.connect(self.setStartTime)
        self.ui.selectEndBtn.pressed.connect(self.setEndTime)
        self.ui.selectStartDate.editingFinished.connect(self.setStartEndTimes)
        self.ui.selectEndDate.editingFinished.connect(self.setStartEndTimes)
        self.ui.selectAccount.currentTextChanged.connect(self.setAccount)

        self.tradeLayout = QHBoxLayout(self.ui.groupTradesWidget)
        # self.currentGroupWidget = None
        self.populateTags()
        self.populateStrategies()
        self.populateAccounts()
        self.initializeCud()
        self.populateCharts()

        self.ui.selectStartBtn.setFocusPolicy(Qt.NoFocus)
        self.ui.selectEndBtn.setFocusPolicy(Qt.NoFocus)
        self.initializing = False
        self.show()

    def initializeCud(self):
        '''
        Set cud (chart_user_dict) settings from the current state of all the widgets
        '''
        self.selectSymbols()
        self.selectSide()
        self.selectTag()
        self.setStartEndInactive()
        self.setTimeOrNumTrades()
        self.cud['titleBit'] = None

    def getSymbolsAsList(self):
        t = self.ui.symbolEdit.text()
        t = t.replace(" ", "").strip().upper().split(',')
        t = [x for x in t if x]
        return t

    # #### Callbacks and methods to collect user input data and set self.cud #####

    # Regarding the noodly self handling of exclusivity of the checkboxes. The options need to be
    # 1 checked or none checked. The radio button is the right widget except the autoexclusivity
    # wont allow turning off all buttons. The suggested fix (turning off and on autoexclusivity)
    # doesn't work. This works and is still easily understandable.

    def set30Days(self, val):
        print('===== In set30Days===== ')
        months = 0
        if val:
            self.ui.dateRange60Cbox.setChecked(False)
            self.ui.dateRange90Cbox.setChecked(False)
            months = 1

        elif self.ui.dateRange60Cbox.isChecked():
            months = 2
        elif self.ui.dateRange90Cbox.isChecked():
            months = 3
        self.setXMonths(months)

    def set60Days(self, val):
        print('===== In set60Days===== ')
        months = 0
        if val:
            self.ui.dateRange30Cbox.setChecked(False)
            self.ui.dateRange90Cbox.setChecked(False)
            months = 2

        elif self.ui.dateRange30Cbox.isChecked():
            months = 1
        elif self.ui.dateRange90Cbox.isChecked():
            months = 3
        self.setXMonths(months)

    def set90Days(self, val):
        print('===== In set90Days===== ')
        months = 0
        if val:
            self.ui.dateRange30Cbox.setChecked(False)
            self.ui.dateRange60Cbox.setChecked(False)
            months = 3

        elif self.ui.dateRange30Cbox.isChecked():
            months = 1
        elif self.ui.dateRange60Cbox.isChecked():
            months = 2
        self.setXMonths(months)

    def setXMonths(self, months):
        if months == 0:
            self.setStartEndInactive()
            self.cud['dates'] = (None, None)
            return
        now = QDate.currentDate()
        before = now.addMonths(-months)
        self.ui.selectStartDate.setDate(before)
        self.ui.selectEndDate.setDate(now)
        self.setStartEndTimes()

    def setDaysOff(self):
        '''
        Uncheck the 30 60 and 90 day checkboxes
        '''
        self.ui.dateRange30Cbox.setChecked(False)
        self.ui.dateRange60Cbox.setChecked(False)
        self.ui.dateRange90Cbox.setChecked(False)

    def setStartEndInactive(self):
        '''
        The checkboxes (30 60, 90 days) are short cuts to fill in the start and end dates. Un checking
        all three will also trigger this method. For start end, we achieve inactivity by setting the
        start date to the future. Date widgets will be set initailly inactive. The start and end will
        become active only if the user checks a box or changes the dates.
        '''
        d = pd.Timestamp.now() + pd.Timedelta(days=1)
        d = pd2qtime(d, qdate=True)
        self.ui.selectStartDate.setDate(d)
        self.ui.selectEndDate.setDate(d)
        self.cud['dates'] = (None, None)

    def setStartTime(self):
        settings = QSettings('zero_substance', 'structjour')
        saveit = []
        initialdate = self.ui.selectStartDate.date()
        CalendarControl(settings, parent=self, btn_widg=self.ui.selectStartBtn, passme=saveit, initialDate=initialdate)
        self.ui.selectStartDate.setDate(saveit[0])
        self.setStartEndTimes()
        self.setDaysOff()

    def setEndTime(self):
        settings = QSettings('zero_substance', 'structjour')
        saveit = []
        initialdate = self.ui.selectEndDate.date()
        CalendarControl(settings, parent=self, btn_widg=self.ui.selectStartBtn, passme=saveit, initialDate=initialdate)
        self.ui.selectEndDate.setDate(saveit[0])
        self.setStartEndTimes()
        self.setDaysOff()

    def setStartEndTimes(self):
        '''
        Retrieve the dates from the widgets and place them in the self.cud dict.
        If they are not ordered (start > end), set the dict to None and inactivate
        the dates.
        Note that self.cud['date'] will be a tuple of QDates (start, end)

        '''
        start = self.ui.selectStartDate.date()
        end = self.ui.selectEndDate.date()
        if start > end:
            self.setStartEndInactive()
            self.cud['dates'] = (None, None)
            print('Set cud.dates to:', self.cud['dates'])
        else:
            self.cud['dates'] = (start, end)
            print('Setting cud.dates to:', (start, end))
            if not self.initializing:
                for chart in self.charts:
                    chart.plot()

    def selectStrategy(self):
        selected = [x.text() for x in self.ui.strategyListWidget.selectedItems()]
        self.cud['strategies'] = selected

        print('Set cud.strategies:', selected)

    def setTimeOrNumTrades(self):
        if self.ui.tradesBySetsRB.isChecked():
            self.groupByNumTrades(self)
        elif self.ui.tradesByTimeRB.isChecked():
            self.groupByTime()
        else:
            self.ui.tradesBySetsRB.setChecked(True)
            self.tradesBySetClicked(True)
            # Settingf a default value for the numtrades spin box
            self.dynamicWidget.setValue(20)
            self.groupByNumTrades()
            print()

    def groupByTime(self, val):

        # When using this data, the chartDataBase class will use actual months instead of 30, 60 90 ...
        vals = {'Group by Day': 1,
                'Group By Week': 7,
                'Group By Month': 30,
                'Group by 2 Months': 60,
                'Group by 3 Months': 90,
                'Group by 4 Months': 120,
                'Group by 6 Months': 180,
                'Group By Year': 360}

        assert val in vals
        self.cud['inTimeGroups'] = vals[val]
        self.cud['inNumSets'] = -1
        self.cud['titleBit'] = val
        print('Set cud.inTimeGroups: ', self.cud['inTimeGroups'])
        if not self.initializing:
            for chart in self.charts:
                chart.plot()

    def groupByNumTrades(self):
        self.cud['inNumSets'] = self.dynamicWidget.value()
        self.cud['inTimeGroups'] = None
        print('set cud.inNumSet ', self.cud['inNumSets'])
        if not self.initializing:
            for chart in self.charts:
                chart.plot()

    def selectSymbols(self):
        '''
        Set cud to reflect the latest edits to the Symbol edit
        '''
        self.cud['symbols'] = self.getSymbolsAsList()
        print("Set cud.symbolsr:", self.cud['symbols'])
        if not self.initializing:
            for chart in self.charts:
                chart.plot()

    def selectSide(self):
        '''
        Set cud to reflect the last selection in the Side combo box
        '''
        self.cud['side'] = self.ui.sideCB.currentText()
        print('Set cud.side:', self.cud['side'])

    def selectTag(self):
        '''
        Set cud to reflect the latest tag selection
        '''
        # justclicked = val.text()
        selected = [x.text() for x in self.ui.tagsListWidget.selectedItems()]
        self.cud['tags'] = selected
        print('set cud.tags', self.cud['tags'])

    def setAccount(self):
        account = self.ui.selectAccount.currentText()
        if account is None or account == 'All Accounts' or account == '':
            self.cud['accounts'] = None
        else:
            self.cud['accounts'] = account

        print('Set cud.account ', self.cud['accounts'])
        if not self.initializing:
            for chart in self.charts:
                chart.plot()

    # ##### Load a dynamic widget for inNumTrades or inTimeGroups #####
    def tradesBySetClicked(self, val):
        if self.tradeLayout is not None:
            for i in reversed(range(self.tradeLayout.count())):
                self.tradeLayout.itemAt(i).widget().setParent(None)
        label = QLabel("Group Trades")
        label.setFont(QFont('Arial Rounded MT Bold', pointSize=12))
        label.setStyleSheet('background-color: #eeeeaa')
        label.setMaximumHeight(35)

        spin = QSpinBox()
        spin.setMinimum(1)
        spin.setMaximum(1000)
        spin.setStyleSheet('background-color: #eeeeaa')
        spin.setFont(QFont('Arial Rounded MT Bold', pointSize=12))
        spin.editingFinished.connect(self.groupByNumTrades)
        self.tradeLayout.addWidget(label)
        self.tradeLayout.addWidget(spin)
        spin.show
        self.dynamicWidget = spin
        label.show()

        grpnum = spin.value()
        print('Update data to view trades in groups of:', grpnum)

    def tradesByTimeClicked(self, val):
        print(val)
        if self.tradeLayout is not None:
            for i in reversed(range(self.tradeLayout.count())):
                self.tradeLayout.itemAt(i).widget().setParent(None)
        label = QLabel("Select Time")
        label.setFont(QFont('Arial Rounded MT Bold', pointSize=12))
        label.setStyleSheet('background-color: #eeeeaa')
        label.setMaximumHeight(35)
        cbox = QComboBox()
        cbox.setStyleSheet('background-color: #eeeeaa')
        for t in ['Group by Day', 'Group By Week', 'Group By Month', 'Group by 2 Months',
                  'Group by 3 Months', 'Group by 4 Months', 'Group by 6 Months', 'Group By Year']:
            cbox.addItem(t)
        cbox.setFont(QFont('Arial Rounded MT Bold', pointSize=12))
        cbox.currentTextChanged.connect(self.groupByTime)
        self.tradeLayout.addWidget(label)
        self.tradeLayout.addWidget(cbox)
        cbox.show()
        label.show()

        selectedTime = cbox.currentText()
        print('Update charts to view trades in groups of:', selectedTime)

    # ##### Initialize methods #####
    def populateTags(self):
        tags = [x.name for x in Tags.getTags() if x.active is True]
        self.ui.tagsListWidget.clear()
        self.ui.tagsListWidget.addItems(tags)

    def populateStrategies(self):
        '''
        Populate the listwidget from every strategy that has been named in a trade. This will
        include every strategy that has been named by the user in a trade (for this database
        table).
        Reiterate, unnecessarily, that the TradeSum.strategy is a string and has no relationship
        with the strategy tables
        '''
        strats = TradeSum.getDistinctStrats()
        self.ui.strategyListWidget.clear()
        for strat in strats:
            if strat[0] == '':
                self.ui.strategyListWidget.addItem(f'(No Strategy) ({strat[1]})')
            else:
                self.ui.strategyListWidget.addItem(f'{strat[0]} ({strat[1]})')

    def populateAccounts(self):
        accounts = TradeSum.getAccounts()
        self.ui.selectAccount.clear()
        self.ui.selectAccount.addItem('All Accounts')
        for account in accounts:
            self.ui.selectAccount.addItem(account)
        if 'SIM' in accounts:
            self.ui.selectAccount.setCurrentText('SIM')

    def getNamesNProfits(self, date):
        '''
        Just temp
        '''
        return TradeSum.getNamesAndProfits(date.strftime("%Y%m%d"))

    def populateCharts(self):
        flow = FlowLayout(self.ui.content_widget)
        self.ui.scrollArea.setWidget(self.ui.content_widget)
        self.ui.content_widget.setStyleSheet('background-color: #yellow;')

        # date = pd.Timestamp('20200102')
        # delt = pd.Timedelta(days=1)
        # flowlayout = FlowLayout(chartArea)
        chartData = MultiTradeProfit_BarchartData(self.cud, limit=30)
        bc = BarChart(chartData, parent=self)
        bc.setSizePolicy((QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)))
        bc.setMinimumSize(300, 300)
        self.charts = []
        # count = 0
        self.charts.append(bc)
        flow.addWidget(self.charts[0])

    def populateChartsOLD(self):
        flow = FlowLayout(self.ui.content_widget)
        self.ui.scrollArea.setWidget(self.ui.content_widget)
        self.ui.content_widget.setStyleSheet('background-color: #yellow;')

        date = pd.Timestamp('20200102')
        delt = pd.Timedelta(days=1)
        # flowlayout = FlowLayout(chartArea)

        self.charts = []
        count = 0
        for i in range(50):
            names, profits = self.getNamesNProfits(date)
            for account in names:
                if len(names[account]) == 0:
                    continue
                canvas = CanvasDP(date.strftime("%Y%m%d"), account)
                canvas.setSizePolicy((QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)))
                canvas.setMinimumSize(300, 300)
                self.charts.append(canvas)
                flow.addWidget(self.charts[count])
                count += 1
            date = date + delt


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = StatitisticsHubControl()
    sys.exit(app.exec_())
