
import os
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog, QApplication
from journal.view.stockapi import Ui_Dialog as SapiDlg

class StockApi(QDialog):
    def __init__(self, settings):
        super().__init__()

        self.settings = settings
    
        ui = SapiDlg()
        ui.setupUi(self)
        self.ui = ui

        self.ui.ibRealCb.clicked.connect(self.ibClicked)
        self.ui.ibPaperCb.clicked.connect(self.ibPaperclicked)
        self.ui.bcCb.clicked.connect(self.bcClicked)
        self.ui.avCb.clicked.connect(self.avClicked)
        self.ui.iexCb.clicked.connect(self.iexClicked)
        self.ui.APIPref.editingFinished.connect(self.orderApis)
        self.ui.okBtn.pressed.connect(self.okPressed)

        self.ui.APIPref.setStyleSheet('color: black;')

        pref = self.settings.value('APIPref')
        self.ui.APIPref.setText(pref)
        self.orderApis()

        self.show()

    def okPressed(self):
        self.orderApis()
        self.close()


    def orderApis(self):
        t = self.ui.APIPref.text()
        count = 0
        if 'ib' in t:
            count = count + 1
            if not self.ui.ibRealCb.checkState() or not self.ui.ibPaperCb.checkState():
                self.ui.ibRealCb.setChecked(True)
        else:
            self.ui.ibRealCb.setChecked(False)
            self.ui.ibPaperCb.setChecked(False)
        if 'bc' in t:
            count = count + 1
            self.ui.bcCb.setChecked(True)
        else:
            self.ui.bcCb.setChecked(False)
        if 'av' in t:
            count = count + 1
            self.ui.avCb.setChecked(True)
        else:
            self.ui.avCb.setChecked(False)
        if 'iex' in t:
            count = count+1
            self.ui.iexCb.setChecked(True)
        else:
            self.ui.iexCb.setChecked(False)

        t = t.replace(' ', '')
        tlist = t.split(',')
        if len(tlist) != count:
            self.ui.APIPref.setStyleSheet('color: red;')
            return
        for api in tlist:
            if api not in ['ib', 'bc', 'av', 'iex']:
                self.ui.APIPref.setStyleSheet('color: red;')
                return
        self.ui.APIPref.setStyleSheet('color: green;')
        self.settings.setValue('APIPref', t)


        





    def ibClicked(self, b):
        print('here we are', b)
        self.ui.ibRealCb.setChecked(b)
        if b:
            self.ui.ibPaperCb.setChecked(not b)
        self.sortIt('ib', b)

    def ibPaperclicked(self, b):
        self.ui.ibPaperCb.setChecked(b)
        if b:
            self.ui.ibRealCb.setChecked(not b)
        self.sortIt('ibp', b)

    def bcClicked(self, b):
        self.sortIt('bc', b)

    def avClicked(self, b):
        self.sortIt('av', b)

    def iexClicked(self, b):
        self.sortIt('iex', b)


    def sortIt(self, last, b):
        wl = [self.ui.ibRealCb, self.ui.ibPaperCb, self.ui.bcCb, self.ui.avCb, self.ui.iexCb]
        sl = ['ib', 'ibp', 'bc', 'av', 'iex']
        ul = ''
        if self.ui.ibRealCb.checkState() or self.ui.ibPaperCb.checkState():
            ul = 'ib'
        if self.ui.bcCb.checkState():
            if ul:
                ul = ul + ', bc'
            else:
                ul = 'bc' 
        if self.ui.avCb.checkState():
            if ul:
                ul = ul + ', av'
            else:
                ul = 'av'
        if self.ui.iexCb.checkState():
            if ul:
                ul = ul + ', iex'
            else:
                ul = 'iex'

        self.ui.APIPref.setText(ul)


if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    settings = QSettings('zero_substance', 'structjour')
    w = StockApi(settings)
    sys.exit(app.exec_())