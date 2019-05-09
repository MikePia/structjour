'''
Instantiate the ui form and create all the needed connections to run it.

Created on May 8, 2019

@author: Mike Petersen
'''

import os
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.QtCore import QSettings

from journal.view.enterjournal import Ui_Dialog as EjDlg

# pylint: disable = C0301, C0103


class EJControl(QDialog):
    '''
    Pop up and request the journal directory
    '''
    def __init__(self):
        super().__init__()


        ui = EjDlg()
        ui.setupUi(self)
        self.ui = ui
        self.ui.browseBtn.pressed.connect(self.browse)
        self.settings = QSettings('zero_substance', 'structjour')

        ok = self.exec()
        if ok:
            j = self.ui.journalEdit.text()
            if os.path.exists(j):
                self.settings.setValue('journal', j)
                print('\n\nSUCCESS!!\n\n')
                return
        print('FAILURE')

    def browse(self):
        '''
        Open a file dialog and set the results to the QLineEdit 'journalEdit'. Triggered by its
        neighboring button.
        '''

        path = QFileDialog.getExistingDirectory(None, "Select Directory")
        self.ui.journalEdit.setText(path)
        # self.settings.setValue('journal', path)


if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    w = EJControl()
    # sys.exit(app.exec_())
    