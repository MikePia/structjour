
import os
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog, QApplication
from journal.view.stockapi import Ui_Dialog as SapiDlg

class StockApi(QDialog):
    '''
    [APIPref, ibPort, ibId, ibPaperPort, ibPaperId, ibRealPref]
    '''
    def __init__(self, settings):
        super().__init__()

        self.settings = settings
    
        ui = SapiDlg()
        ui.setupUi(self)
        self.ui = ui

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

        self.ui.iexCb.clicked.connect(self.setIexCb)

        self.ui.APIPref.textChanged.connect(self.orderApis)

        self.ui.okBtn.pressed.connect(self.okPressed)

        self.ui.APIPref.setStyleSheet('color: black;')

        self.initFromSettings()
        # self.sortIt(None)
        # self.orderApis()

        self.show()

    def initFromSettings(self):
        val = self.settings.value('ibPort', '')
        self.ui.ibRealPort.setText(val)

        val = self.settings.value('ibId')
        self.ui.ibRealId.setText(val)

        val = self.settings.value('ibPaperPort')
        self.ui.ibPaperPort.setText(val)

        val = self.settings.value('ibPaperId')
        self.ui.ibPaperId.setText(val)

        val = self.settings.value('ibRealCb', False, bool)
        self.ui.ibRealCb.setChecked(val)

        val = self.settings.value('ibPaperCb', False, bool)
        self.ui.ibPaperCb.setChecked(val)

        val = self.settings.value('bcCb', False, bool)
        self.ui.bcCb.setChecked(val)
        
        val = self.settings.value('bcKey', '')
        self.ui.bcKey.setText(val)

        val = self.settings.value('avCb', False, bool)
        self.ui.avCb.setChecked(val)
        
        val = self.settings.value('avKey', '')
        self.ui.avKey.setText(val)

        val = self.settings.value('iexCb', False, bool)
        self.ui.iexCb.setChecked(val)

        val = self.settings.value('APIPref')
        self.ui.APIPref.setText(val)

        self.sortIt(None)



    def setIbRealPort(self):
        text = self.ui.ibRealPort.text()
        print('real', text)
        self.settings.setValue('ibPort', text)

    def setIbRealId(self):
        text = self.ui.ibRealId.text()
        print('real', text)
        self.settings.setValue('ibId', text)

    def setIbPaperId(self):
        text = self.ui.ibPaperId.text()
        print('real', text)
        self.settings.setValue('ibPaperId', text)

    def setIbPaperPort(self):
        text = self.ui.ibPaperPort.text()
        print('real', text)
        self.settings.setValue('ibPaperPort', text)

    def okPressed(self):
        self.orderApis()
        self.close()

    def orderApis(self):
        val = self.ui.APIPref.text()
        self.settings.setValue('APIPref', val)
        self.sortIt(None)
    

    def ibClicked(self, b):
        print('real clicked')
        self.settings.setValue('ibRealPref', b)
        self.settings.setValue('ibRealCb', b)
        if b:
            self.settings.setValue('ibPaperCb', not b)
            self.ui.ibPaperCb.setChecked(not b)
        self.sortIt('ib')

    def ibPaperclicked(self, b):
        print('paper clicked')
        # self.ui.ibPaperCb.setChecked(b)
        self.settings.setValue('ibRealPref', not b)
        self.settings.setValue('ibPaperCb', b)
        if b:
            self.settings.setValue('ibRealCb', not b)
            self.ui.ibRealCb.setChecked(not b)
        self.sortIt('ib')

    def setBcCb(self, b):
        self.settings.setValue('bcCb', b)
        self.sortIt('bc')

    def setBcKey(self):
        val = self.ui.bcKey.text()
        self.settings.setValue('bcKey', val)

    def setAvCb(self, b):
        self.settings.setValue('avCb', b)
        self.sortIt('av')

    def setAvKey(self):
        val = self.ui.avKey.text()
        self.settings.setValue('avKey', val)

    def setIexCb(self, b):
        self.settings.setValue('iexCb', b)
        self.sortIt('iex')

    def reorderAPIPref(self, last):
        ul = self.ui.APIPref.text()
        ulist = ul.replace(' ', '').split(',')
        if last and last in ulist:
            ulist.remove(last)
            ulist.append(last)
            newul = ''
            for x in ulist:
                newul = newul + x + ', '
            if newul:
                newul = newul[:-2]
                ul = newul
        self.settings.setValue('APIPref', ul)
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
        if 'iex' in ulist:
            if not self.ui.iexCb.isChecked():
                self.ui.APIPref.setStyleSheet('color: red;')
                return
            compareList.append('iex')

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
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    settings = QSettings('zero_substance', 'structjour')
    w = StockApi(settings)
    sys.exit(app.exec_())