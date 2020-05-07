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

from structjour.models.trademodels import Tags, TradeSum, Trade
from structjour.view.calendarcontrol import CalendarControl
from structjour.view.charts.dailyprofit_barchart import Canvas as CanvasDP
from structjour.view.flowlayout import FlowLayout

from structjour.view.forms.statisticshub import Ui_Form as StatHub
from PyQt5.QtCore import QSettings, QDate, Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QLabel, QSpinBox, QHBoxLayout, QGridLayout,
                             QVBoxLayout, QScrollArea, QComboBox, QWidget, QSizePolicy)
from PyQt5.QtGui import QFont


class StatitisticsHubControl(QDialog):

    def __init__(self):
        super().__init__()
        self.ui = StatHub()
        self.ui.setupUi(self)
        self.dynamicWidget = None
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)

        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self.ui.symbolEdit.editingFinished.connect(self.selectSymbols)
        self.ui.sideCB.currentTextChanged.connect(self.selectSide)
        self.ui.tagsListWidget.itemPressed.connect(self.selectTag)
        self.ui.tradesBySetsRB.clicked.connect(self.tradesBySetClicked)
        self.ui.tradesByTimeRB.clicked.connect(self.tradesByTimeClicked)
        self.ui.strategyListWidget.itemPressed.connect(self.selectStrategy)

        self.ui.dateRange30RB.pressed.connect(self.set30Days)
        self.ui.dateRange60RB.pressed.connect(self.set60Days)
        self.ui.dateRange90RB.pressed.connect(self.set90Days)
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
        self.populateCharts()

        self.ui.selectStartBtn.setFocusPolicy(Qt.NoFocus)
        self.ui.selectEndBtn.setFocusPolicy(Qt.NoFocus)
        self.show()

    # #### Callbacks #####

    def set30Days(self):
        self.setXDays(1)

    def set60Days(self):
        self.setXDays(2)

    def set90Days(self):
        self.setXDays(3)

    def setXDays(self, months):
        now = QDate.currentDate()
        before = now.addMonths(-months)
        self.ui.selectStartDate.setDate(before)
        self.ui.selectEndDate.setDate(now)
        self.setStartEndTimes()

    def setStartTime(self):
        settings = QSettings('zero_substance', 'structjour')
        saveit = []
        CalendarControl(settings, parent=self, btn_widg=self.ui.selectStartBtn, passme=saveit)
        self.ui.selectStartDate.setDate(saveit[0])
        self.setStartEndTimes()

    def setEndTime(self):
        settings = QSettings('zero_substance', 'structjour')
        saveit = []
        CalendarControl(settings, parent=self, btn_widg=self.ui.selectStartBtn, passme=saveit)
        self.ui.selectEndDate.setDate(saveit[0])
        self.setStartEndTimes()

    def setStartEndTimes(self):
        start = self.ui.selectStartDate.date()
        end = self.ui.selectEndDate.date()
        if start > end:
            print('start is greater than end')
        else:
            print('filter charts by date start:', start, "end:", end)

    def selectStrategy(self):
        selected = [x.text() for x in self.ui.strategyListWidget.selectedItems()]

        print('Update the charts for the strategies:', selected)

    def groupByTime(self, val):
        print(val)

    def groupByNumTrades(self):
        print('Group trades in sets of ', self.dynamicWidget.value())
        print()

    def selectSymbols(self):
        t = self.ui.symbolEdit.text()
        t = t.replace(" ", "").strip().upper().split(',')
        print("Update the data to filter only these symbols:", t)

    def selectSide(self, val):
        print('update chart for sides:', val)

    def selectTag(self, val):
        # justclicked = val.text()
        selected = [x.text() for x in self.ui.tagsListWidget.selectedItems()]
        print('update the charts for selected tags', selected)

    def setAccount(self):
        account = self.ui.selectAccount.currentText()
        if account == 'All Accounts':
            print('remove account filter')
        elif account:
            print('filter account to ', account)

    # ##### Dynamic groups by widget #####
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
        for t in ['Group by Day', 'Group By Week', 'Group By Month', 'Group By Year']:
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
        accounts = Trade.getAccounts()
        self.ui.selectAccount.clear()
        self.ui.selectAccount.addItem('All Accounts')
        for account in accounts:
            self.ui.selectAccount.addItem(account)

    def getNamesNProfits(self, date):
        '''
        Just temp
        '''
        return TradeSum.getNamesAndProfits(date.strftime("%Y%m%d"))

    def populateCharts(self):
        # for i in range(50):
        # self.topgrid = QGridLayout(self.ui.scrollArea)
        # self.topgrid.addWidget(self.ui.scrollArea)
        # # content_widget = QWidget()
        flow = FlowLayout(self.ui.content_widget)
        # self.ui.content_widget.setLayout(flow)
        # flow.addWidget(self.ui.scrollArea)
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
