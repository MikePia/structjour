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
Created on Apr 1, 2019

@author: Mike Petersen
'''
import os
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtWidgets import QDialog, QApplication

from structjour.view.stockapi import Ui_Dialog as SapiDlg
from structjour.stock.utilities import ManageKeys, checkForIbapi


class StockApi(QDialog):
    '''
    [ibRealPort, ibRealId, ibPaperPort, ibPaperId, ibRealCb, ibPaperCb, bcCb, avCb, iexCb, wtdCb, APIPref]
    The api keys are held in the database
    '''
    def __init__(self, settings):
        super().__init__()

        self.apiset = settings
        self.mk = ManageKeys()
    
        ui = SapiDlg()
        ui.setupUi(self)
        self.ui = ui

        checkForIbapi()

        self.setWindowIcon(QIcon('structjour/images/ZSLogo.png'))

        self.ui.ibRealCb.clicked.connect(self.ibClicked)
        self.ui.ibPaperCb.clicked.connect(self.ibPaperclicked)
        self.ui.ibRealPort.editingFinished.connect(self.setIbRealPort)
        self.ui.ibRealId.editingFinished.connect(self.setIbRealId)
        self.ui.ibPaperPort.editingFinished.connect(self.setIbPaperPort)
        self.ui.ibPaperId.editingFinished.connect(self.setIbPaperId)

        self.ui.bcCb.clicked.connect(self.setBcCb)
        self.ui.bcKey.editingFinished.connect(self.setBcKey)
        
        self.ui.avCb.clicked.connect(self.setAvCb)
        self.ui.avKey.editingFinished.connect(self.setAvKey)

        self.ui.wtdCb.clicked.connect(self.setWtdCb)
        self.ui.wtdKey.editingFinished.connect(self.setWtdKey)

        self.ui.iexCb.clicked.connect(self.setIexCb)

        self.ui.APIPref.textChanged.connect(self.orderApis)

        self.ui.okBtn.pressed.connect(self.okPressed)

        self.ui.APIPref.setStyleSheet('color: black;')
        
        v = QIntValidator()
        self.ui.ibRealPort.setValidator(v)
        self.ui.ibRealId.setValidator(v)
        self.ui.ibPaperPort.setValidator(v)
        self.ui.ibPaperId.setValidator(v)


        self.initFromSettings()
        self.gotibapi = checkForIbapi()
        # self.sortIt(None)
        # self.orderApis()

        self.show()

    # def checkForIbapi(self):
    #     '''
    #     If the ibapi is not installed or available, disable its use.
    #     '''
    #     apisettings = QSettings('zero_substance/stockapi', 'structjour')
    #     try:
    #         import ibapi
    #         gotibapi = True
    #         apisettings.setValue('gotibapi', True)
    #         return True

    #     except ImportError:
    #         apisettings.setValue('gotibapi', False)
    #         return False

    def initFromSettings(self):
        val = self.apiset.value('ibRealPort', '')
        self.ui.ibRealPort.setText(val)

        val = self.apiset.value('ibRealId')
        self.ui.ibRealId.setText(val)

        val = self.apiset.value('ibPaperPort')
        self.ui.ibPaperPort.setText(val)

        val = self.apiset.value('ibPaperId')
        self.ui.ibPaperId.setText(val)

        val = self.apiset.value('ibRealCb', False, bool)
        self.ui.ibRealCb.setChecked(val)

        val = self.apiset.value('ibPaperCb', False, bool)
        self.ui.ibPaperCb.setChecked(val)

        val = self.apiset.value('bcCb', False, bool)
        self.ui.bcCb.setChecked(val)
        
        val = self.mk.getKey('bc')
        self.ui.bcKey.setText(val)

        val = self.apiset.value('avCb', False, bool)
        self.ui.avCb.setChecked(val)
        
        val = self.mk.getKey('av')
        self.ui.avKey.setText(val)

        val = self.apiset.value('wtdCb', False, bool)
        self.ui.wtdCb.setChecked(val)
        
        val = self.mk.getKey('wtd')
        self.ui.wtdKey.setText(val)

        val = self.apiset.value('iexCb', False, bool)
        # self.ui.iexCb.setChecked(val)
        self.ui.iexCb.setChecked(False)

        val = self.apiset.value('APIPref')
        self.ui.APIPref.setText(val)

        self.sortIt(None)



    def setIbRealPort(self):
        text = self.ui.ibRealPort.text()
        self.apiset.setValue('ibRealPort', text)

    def setIbRealId(self):
        text = self.ui.ibRealId.text()
        self.apiset.setValue('ibRealId', text)

    def setIbPaperId(self):
        text = self.ui.ibPaperId.text()
        self.apiset.setValue('ibPaperId', text)

    def setIbPaperPort(self):
        text = self.ui.ibPaperPort.text()
        self.apiset.setValue('ibPaperPort', text)

    def okPressed(self):
        self.orderApis()
        self.close()

    def orderApis(self): 
        val = self.ui.APIPref.text()
        self.apiset.setValue('APIPref', val)
        self.sortIt(None)
    

    def ibClicked(self, b):
        if not self.gotibapi:
            self.apiset.setValue('ibRealCb', False)
            self.apiset.setValue('ibPaperCb', False)
            self.ui.ibRealCb.setChecked(False)
            self.ui.ibPaperCb.setChecked(False)
            return
        # if self.apiset.value()
        self.apiset.setValue('ibRealCb', b)
        if b:
            self.apiset.setValue('ibPaperCb', not b)
            self.ui.ibPaperCb.setChecked(not b)
        self.sortIt('ib')

    def ibPaperclicked(self, b):
        if not self.gotibapi:
            self.apiset.setValue('ibRealCb', False)
            self.apiset.setValue('ibPaperCb', False)
            self.ui.ibRealCb.setChecked(False)
            self.ui.ibPaperCb.setChecked(False)
            return


        # self.ui.ibPaperCb.setChecked(b)
        self.apiset.setValue('ibPaperCb', b)
        if b:
            self.apiset.setValue('ibRealCb', not b)
            self.ui.ibRealCb.setChecked(not b)
        self.sortIt('ib')

    def setBcCb(self, b):
        self.apiset.setValue('bcCb', b)
        self.sortIt('bc')

    def setBcKey(self):
        val = self.ui.bcKey.text()
        self.mk.updateKey('bc', val)

    def setAvCb(self, b):
        self.apiset.setValue('avCb', b)
        self.sortIt('av')

    def setAvKey(self):
        val = self.ui.avKey.text()
        self.mk.updateKey('av', val)

    def setWtdCb(self, b):
        self.apiset.setValue('wtdCb', b)
        self.sortIt('wtd')
    
    def setWtdKey(self):
        val = self.ui.wtdKey.text()
        self.mk.updateKey('wtd', val)


    def setIexCb(self, b):
        # self.apiset.setValue('iexCb', b)
        self.apiset.setValue('iexCb', False)
        self.ui.iexCb.setChecked(False)
        # self.sortIt('iex')

    def reorderAPIPref(self, last):
        ul = self.ui.APIPref.text()
        ulist = ul.replace(' ', '').split(',') if ul else []
        if last and last in ulist:
            ulist.remove(last)
            ulist.append(last)
            newul = ''
            for x in ulist:
                newul = newul + x + ', '
            if newul:
                newul = newul[:-2]
                ul = newul
        self.apiset.setValue('APIPref', ul)
        self.ui.APIPref.setText(ul)
        return ul, ulist

    def sortIt(self, last):
        ul, ulist = self.reorderAPIPref(last)
        compareList = list()

        # If list contains an unchecked API, show error as red
        if 'ib' in ulist:
            if not self.ui.ibRealCb.isChecked() and not self.ui.ibPaperCb.isChecked():
                self.ui.APIPref.setStyleSheet('color: red;')
                return
            compareList.append('ib')
        if 'bc' in ulist:
            if not self.ui.bcCb.isChecked():
                self.ui.APIPref.setStyleSheet('color: red;')
                return
            compareList.append('bc')
        if 'av' in ulist:
            if not self.ui.avCb.isChecked():
                self.ui.APIPref.setStyleSheet('color: red;')
                return
            compareList.append('av')
        if 'wtd' in ulist:
            if not self.ui.wtdCb.isChecked():
                self.ui.APIPref.setStyleSheer('color: red')
            compareList.append('wtd')
        # if 'iex' in ulist:
        #     if not self.ui.iexCb.isChecked():
        #         self.ui.APIPref.setStyleSheet('color: red;')
        #         return
        #     compareList.append('iex')

        # Validate the string as a list and reorder last element
        if len(ulist) > len(compareList):
            self.ui.APIPref.setStyleSheet('color: red;')
            return
        for x in ulist:
            if x not in compareList:
                self.ui.APIPref.setStyleSheet('color: red;')
                return

        self.ui.APIPref.setStyleSheet('color: green;')
        self.ui.APIPref.setText(ul)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    apisettings = QSettings('zero_substance/stockapi', 'structjour')
    w = StockApi(apisettings)
    sys.exit(app.exec_())