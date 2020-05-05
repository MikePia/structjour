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

from structjour.models.trademodels import Tags

from structjour.view.forms.statisticshub import Ui_Form as StatHub
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QSpinBox, QHBoxLayout, QComboBox
from PyQt5.QtGui import QFont


class StatitisticsHubControl(QDialog):

    def __init__(self):
        super().__init__()
        self.ui = StatHub()
        self.ui.setupUi(self)

        self.ui.symbolEdit.editingFinished.connect(self.selectSymbols)
        self.ui.sideCB.currentTextChanged.connect(self.selectSide)
        self.ui.tagsListWidget.itemPressed.connect(self.selectTag)
        self.ui.tradesBySetsRB.clicked.connect(self.tradesBySetClicked)
        self.ui.tradesByTimeRB.clicked.connect(self.tradesByTimeClicked)

        self.tradeLayout = QHBoxLayout(self.ui.groupTradesWidget)
        # self.currentGroupWidget = None
        self.populateTags()
        self.show()

    # #### Callbacks #####

    def groupByTime(self, val):
        print(val)

    def groupByNumTrades(self, val):
        print(val)

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
        spin.valueChanged.connect(self.groupByNumTrades)
        self.tradeLayout.addWidget(label)
        self.tradeLayout.addWidget(spin)
        spin.show
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
        print('Gotta create the model here')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = StatitisticsHubControl()
    sys.exit(app.exec_())
