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

Created on May 14, 2019

@author: Mike Petersen
'''

import os
import sys

from matplotlib import style, colors as mplcolors
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QDoubleValidator, QIcon
from PyQt5.QtWidgets import QDialog, QApplication, QLineEdit, QCheckBox, QSpinBox, QComboBox

from structjour.view.chartform import Ui_Form as ChartDlg

class ChartControl(QDialog):
    '''
    [list of settings]
    '''
    def __init__(self, settings):
        super().__init__()

        self.chartSet = settings
    
        ui = ChartDlg()
        ui.setupUi(self)
        self.ui = ui
        self.widgDict = None
        self.mplcolors = None
        self.loadStyles()

        self.setWindowIcon(QIcon("images/ZSLogo.png"))

        self.ui.styleCb.currentTextChanged.connect(self.setStyle)
        self.ui.gridhCb.clicked.connect(self.setGridh)
        self.ui.gridvCb.clicked.connect(self.setGridv)
        self.ui.markerColorUp.textChanged.connect(self.setMarkerColorUp)
        self.ui.markerColorDown.textChanged.connect(self.setMarkerColorDown)
        self.ui.markerEdgeColor.textChanged.connect(self.setMarkerEdgeColor)
        self.ui.markerAlpha.textChanged.connect(self.setMarkerAlpha)
        self.ui.markerSize.valueChanged.connect(self.setMarkerSize)
        self.ui.colorUp.textChanged.connect(self.setColorUp)
        self.ui.colorDown.textChanged.connect(self.setColorDown)
        self.ui.interactiveCb.clicked.connect(self.setInteractive)
        self.ui.showLegendCb.clicked.connect(self.setLegend)

        self.ui.chart1MA1.clicked.connect(self.setChart1MA1)
        self.ui.chart1MA1Spin.valueChanged.connect(self.setChart1MA1Spin)
        self.ui.chart1MA1Color.textChanged.connect(self.setChart1MA1Color)

        self.ui.chart1MA2.clicked.connect(self.setChart1MA2)
        self.ui.chart1MA2Spin.valueChanged.connect(self.setChart1MA2Spin)
        self.ui.chart1MA2Color.textChanged.connect(self.setChart1MA2Color)

        self.ui.chart1MA3.clicked.connect(self.setChart1MA3)
        self.ui.chart1MA3Spin.valueChanged.connect(self.setChart1MA3Spin)
        self.ui.chart1MA3Color.textChanged.connect(self.setChart1MA3Color)

        self.ui.chart1MA4.clicked.connect(self.setChart1MA4)
        self.ui.chart1MA4Spin.valueChanged.connect(self.setChart1MA4Spin)
        self.ui.chart1MA4Color.textChanged.connect(self.setChart1MA4Color)

        self.ui.chart1VWAP.clicked.connect(self.setChart1VWAP)
        self.ui.chart1VWAPColor.textChanged.connect(self.setChart1VWAPColor)

        #chart2
        self.ui.chart2MA1.clicked.connect(self.setChart2MA1)
        self.ui.chart2MA1Spin.valueChanged.connect(self.setChart2MA1Spin)
        self.ui.chart2MA1Color.textChanged.connect(self.setChart2MA1Color)

        self.ui.chart2MA2.clicked.connect(self.setChart2MA2)
        self.ui.chart2MA2Spin.valueChanged.connect(self.setChart2MA2Spin)
        self.ui.chart2MA2Color.textChanged.connect(self.setChart2MA2Color)

        self.ui.chart2MA3.clicked.connect(self.setChart2MA3)
        self.ui.chart2MA3Spin.valueChanged.connect(self.setChart2MA3Spin)
        self.ui.chart2MA3Color.textChanged.connect(self.setChart2MA3Color)

        self.ui.chart2MA4.clicked.connect(self.setChart2MA4)
        self.ui.chart2MA4Spin.valueChanged.connect(self.setChart2MA4Spin)
        self.ui.chart2MA4Color.textChanged.connect(self.setChart2MA4Color)

        self.ui.chart2VWAP.clicked.connect(self.setChart2VWAP)
        self.ui.chart2VWAPColor.textChanged.connect(self.setChart2VWAPColor)


         #chart3
        self.ui.chart3MA1.clicked.connect(self.setChart3MA1)
        self.ui.chart3MA1Spin.valueChanged.connect(self.setChart3MA1Spin)
        self.ui.chart3MA1Color.textChanged.connect(self.setChart3MA1Color)

        self.ui.chart3MA2.clicked.connect(self.setChart3MA2)
        self.ui.chart3MA2Spin.valueChanged.connect(self.setChart3MA2Spin)
        self.ui.chart3MA2Color.textChanged.connect(self.setChart3MA2Color)

        self.ui.chart3MA3.clicked.connect(self.setChart3MA3)
        self.ui.chart3MA3Spin.valueChanged.connect(self.setChart3MA3Spin)
        self.ui.chart3MA3Color.textChanged.connect(self.setChart3MA3Color)

        self.ui.chart3MA4.clicked.connect(self.setChart3MA4)
        self.ui.chart3MA4Spin.valueChanged.connect(self.setChart3MA4Spin)
        self.ui.chart3MA4Color.textChanged.connect(self.setChart3MA4Color)

        self.ui.chart3VWAP.clicked.connect(self.setChart3VWAP)
        self.ui.chart3VWAPColor.textChanged.connect(self.setChart3VWAPColor)
        

        v = QDoubleValidator()
        v.setRange(0.0, 1.0, 7)
        self.ui.markerAlpha.setValidator(v)

        self.initFromSettings()
        self.validateColors()
        self.show()

    ####### chart3 #######

    def validateColors(self):
        '''
        Check that the color names in each QlineEdit widget for a color has a legit mpl color
        Otherwise, set it to black. This is currently called on initiation of the dialog.
        '''
        # val = val.strip()
        x = mplcolors.cnames
        x['b'] = x['blue']
        x['g'] = x['green']
        x['r'] = x['red']
        x['c'] = x['cyan']
        x['m'] = x['magenta']
        x['y'] = x['yellow']
        x['b'] = x['black']
        x['w'] = x['white']
        self.mplcolors = x

        for key in self.widgDict:
            widg = self.widgDict[key]
            if isinstance(widg, QLineEdit) and 'color' in widg.objectName().lower():
                val = widg.text()
                origval = val
                val = val.strip()
                if not val.startswith('#'):
                    if val not in x.keys():
                        val = 'b'
                if not val == origval:
                    widg.setText(val)
        

    def setChart3VWAPColor(self, val):
        self.chartSet.setValue('chart3vwapcolor', val)

    def setChart3VWAP(self, val):
        self.chartSet.setValue('chart3vwap', val)    


    def setChart3MA4Color(self, val):
        self.chartSet.setValue('chart3ma4color', val)

    def setChart3MA4Spin(self, val):
        self.chartSet.setValue('chart3ma4spin', val)
        self.setCbLabel(val, self.ui.chart3MA4)

    def setChart3MA4(self, val):
        self.chartSet.setValue('chart3ma4', val)

    def setChart3MA3Color(self, val):
        self.chartSet.setValue('chart3ma3color', val)

    def setChart3MA3Spin(self, val):
        self.chartSet.setValue('chart3ma3spin', val)
        self.setCbLabel(val, self.ui.chart3MA3)

    def setChart3MA3(self, val):
        self.chartSet.setValue('chart3ma3', val)


    def setChart3MA2Color(self, val):
        self.chartSet.setValue('chart3ma2color', val)

    def setChart3MA2Spin(self, val):
        self.chartSet.setValue('chart3ma2spin', val)
        self.setCbLabel(val, self.ui.chart3MA2)

    def setChart3MA2(self, val):
        self.chartSet.setValue('chart3ma2', val)    

    def setChart3MA1Color(self, val):
        self.chartSet.setValue('chart3ma1color', val)

    def setChart3MA1Spin(self, val):
        self.chartSet.setValue('chart3ma1spin', val)
        self.setCbLabel(val, self.ui.chart3MA1)

    def setChart3MA1(self, val):
        self.chartSet.setValue('chart3ma1', val)


    ####### chart2 #######

    def setChart2VWAPColor(self, val):
        self.chartSet.setValue('chart2vwapcolor', val)

    def setChart2VWAP(self, val):
        self.chartSet.setValue('chart2vwap', val)    


    def setChart2MA4Color(self, val):
        self.chartSet.setValue('chart2ma4color', val)

    def setChart2MA4Spin(self, val):
        self.chartSet.setValue('chart2ma4spin', val)
        self.setCbLabel(val, self.ui.chart2MA4)

    def setChart2MA4(self, val):
        self.chartSet.setValue('chart2ma4', val)



    def setChart2MA3Color(self, val):
        self.chartSet.setValue('chart2ma3color', val)

    def setChart2MA3Spin(self, val):
        self.chartSet.setValue('chart2ma3spin', val)
        self.setCbLabel(val, self.ui.chart2MA3)

    def setChart2MA3(self, val):
        self.chartSet.setValue('chart2ma3', val)


    def setChart2MA2Color(self, val):
        self.chartSet.setValue('chart2ma2color', val)

    def setChart2MA2Spin(self, val):
        self.chartSet.setValue('chart2ma2spin', val)
        self.setCbLabel(val, self.ui.chart2MA2)

    def setChart2MA2(self, val):
        self.chartSet.setValue('chart2ma2', val)    




    def setChart2MA1Color(self, val):
        self.chartSet.setValue('chart2ma1color', val)

    def setChart2MA1Spin(self, val):
        self.chartSet.setValue('chart2ma1spin', val)
        self.setCbLabel(val, self.ui.chart2MA1)

    def setChart2MA1(self, val):
        self.chartSet.setValue('chart2ma1', val)

    ####### chart1 #######

    def setChart1VWAPColor(self, val):
        self.chartSet.setValue('chart1vwapcolor', val)

    def setChart1VWAP(self, val):
        self.chartSet.setValue('chart1vwap', val)    


    def setChart1MA4Color(self, val):
        self.chartSet.setValue('chart1ma4color', val)

    def setChart1MA4Spin(self, val):
        self.chartSet.setValue('chart1ma4spin', val)
        self.setCbLabel(val, self.ui.chart1MA4)

    def setChart1MA4(self, val):
        self.chartSet.setValue('chart1ma4', val)



    def setChart1MA3Color(self, val):
        self.chartSet.setValue('chart1ma3color', val)

    def setChart1MA3Spin(self, val):
        self.chartSet.setValue('chart1ma3spin', val)
        self.setCbLabel(val, self.ui.chart1MA3)

    def setChart1MA3(self, val):
        self.chartSet.setValue('chart1ma3', val)


    def setChart1MA2Color(self, val):
        self.chartSet.setValue('chart1ma2color', val)

    def setChart1MA2Spin(self, val):
        self.chartSet.setValue('chart1ma2spin', val)
        self.setCbLabel(val, self.ui.chart1MA2)

    def setChart1MA2(self, val):
        self.chartSet.setValue('chart1ma2', val)    

    def setChart1MA1Color(self, val):
        self.chartSet.setValue('chart1ma1color', val)

    def setChart1MA1Spin(self, val):
        self.chartSet.setValue('chart1ma1spin', val)
        self.setCbLabel(val, self.ui.chart1MA1)

    def setChart1MA1(self, val):
        self.chartSet.setValue('chart1ma1', val)

    def setCbLabel(self, val, widg):
        if val <= 20:
            widg.setText(f'{val} EMA')
        else:
            widg.setText(f'{val} SMA')

    def setLegend(self, val):
        self.chartSet.setValue('showlegend', val)

    def setInteractive(self, val):
        self.chartSet.setValue('interactive', val)

    def setColorDown(self, val):
        self.chartSet.setValue('colordown', val)

    def setColorUp(self, val):
        self.chartSet.setValue('colorup', val)

    def setMarkerSize(self, val):
        self.chartSet.setValue('markersize', val)

    def setMarkerAlpha(self, val):
        self.chartSet.setValue('markeralpha', val)

    def setMarkerEdgeColor(self, val):
        self.chartSet.setValue('markeredgecolor', val)

    def setMarkerColorUp(self, val):
        self.chartSet.setValue('markercolorup', val)

    def setMarkerColorDown(self, val):
        self.chartSet.setValue('markercolordown', val)

    def setGridv(self, b):
        self.chartSet.setValue('gridv', b)

    def setGridh(self, b):
        self.chartSet.setValue('gridh', b)

    def setStyle(self, key):
        self.chartSet.setValue('chart', key)

    def loadStyles(self):
        self.ui.styleCb.clear()
        self.ui.styleCb.addItem('No style')
        self.ui.styleCb.addItems(style.available)

    def initFromSettings(self):
        widgDict = {'chart': self.ui.styleCb, 
                'gridv': self.ui.gridvCb,
                'gridh': self.ui.gridhCb,
                'markercolorup': self.ui.markerColorUp,
                'markercolordown': self.ui.markerColorDown,
                'markeredgecolor': self.ui.markerEdgeColor,
                'markeralpha': self.ui.markerAlpha,
                'markersize': self.ui.markerSize,
                'colorup': self.ui.colorUp,
                'colordown': self.ui.colorDown,
                'interactive': self.ui.interactiveCb,
                'showlegend': self.ui.showLegendCb,
                'chart1ma1': self.ui.chart1MA1,
                'chart1ma2': self.ui.chart1MA2,
                'chart1ma3': self.ui.chart1MA3,
                'chart1ma4': self.ui.chart1MA4,
                'chart1vwap': self.ui.chart1VWAP,
                'chart1ma1spin': self.ui.chart1MA1Spin,
                'chart1ma2spin': self.ui.chart1MA2Spin,
                'chart1ma3spin': self.ui.chart1MA3Spin,
                'chart1ma4spin':self.ui.chart1MA4Spin,
                'chart1ma1color': self.ui.chart1MA1Color,
                'chart1ma2color': self.ui.chart1MA2Color,
                'chart1ma3color': self.ui.chart1MA3Color,
                'chart1ma4color':self.ui.chart1MA4Color,
                'chart1vwapcolor': self.ui.chart1VWAPColor,
                'chart2ma1': self.ui.chart2MA1,
                'chart2ma2': self.ui.chart2MA2,
                'chart2ma3': self.ui.chart2MA3,
                'chart2ma4': self.ui.chart2MA4,
                'chart2vwap': self.ui.chart2VWAP,
                'chart2ma1spin': self.ui.chart2MA1Spin,
                'chart2ma2spin': self.ui.chart2MA2Spin,
                'chart2ma3spin': self.ui.chart2MA3Spin,
                'chart2ma4spin':self.ui.chart2MA4Spin,
                'chart2ma1color': self.ui.chart2MA1Color,
                'chart2ma2color': self.ui.chart2MA2Color,
                'chart2ma3color': self.ui.chart2MA3Color,
                'chart2ma4color':self.ui.chart2MA4Color,
                'chart2vwapcolor': self.ui.chart2VWAPColor,
                'chart3ma1': self.ui.chart3MA1,
                'chart3ma2': self.ui.chart3MA2,
                'chart3ma3': self.ui.chart3MA3,
                'chart3ma4': self.ui.chart3MA4,
                'chart3vwap': self.ui.chart3VWAP,
                'chart3ma1spin': self.ui.chart3MA1Spin,
                'chart3ma2spin': self.ui.chart3MA2Spin,
                'chart3ma3spin': self.ui.chart3MA3Spin,
                'chart3ma4spin':self.ui.chart3MA4Spin,
                'chart3ma1color': self.ui.chart3MA1Color,
                'chart3ma2color': self.ui.chart3MA2Color,
                'chart3ma3color': self.ui.chart3MA3Color,
                'chart3ma4color': self.ui.chart3MA4Color,
                'chart3vwapcolor': self.ui.chart3VWAPColor}
        for key in widgDict:
            val = self.chartSet.value(key)
            if not val:
                continue
            widg = widgDict[key]
            if isinstance(widg, QLineEdit):
                widg.setText(val)
            elif isinstance(widg, QCheckBox):
                val =True if val == 'true' else False
                widg.setChecked(val)
            elif isinstance(widg, QSpinBox):
                widg.setValue(val)
            elif isinstance(widg, QComboBox):
                index = widg.findText(val)
                widg.setCurrentIndex(index)
        self.widgDict = widgDict



if __name__ == '__main__':
    app = QApplication(sys.argv)
    chartsettings = QSettings('zero_substance/chart', 'structjour')
    w = ChartControl(chartsettings)
    sys.exit(app.exec_())