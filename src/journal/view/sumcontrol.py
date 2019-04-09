'''
Instantiate the ui form and create all the needed connections to run it.

Created on April 8, 2019

@author: Mike Petersen
'''


from fractions import Fraction
import os
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from journal.view.summaryform import Ui_MainWindow
# pylint: disable = C0103

class SumControl:
    '''
    A control class for summaryform, a class created and maintained by Qt designer
    '''
    def __init__(self, ui):
        self.ui = ui
        self.ui.targ.textEdited.connect(self.diffTarget)
        self.ui.stop.textEdited.connect(self.stopLoss)



        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))

        self.diffTarget(self.ui.targ.text())
        self.stopLoss(self.ui.stop.text())

    def diffTarget(self, val):
        '''
        Set the targDiff to the difference between the target and the actual PL, then 
        call rrCalc
        '''
        diff = 0
        try:
            fval = float(val)
            fpl = float(self.ui.entry1.text())
            diff = fval-fpl
            diff = '{:.02}'.format(diff)
        except ValueError:
            diff = '0'
        self.ui.targDiff.setText(diff)
        self.rrCalc(diff, self.ui.stopDiff.text())

    def stopLoss(self, val):
        '''
        Set the stopDiff to the difference between the stoploss and the actual PL, then 
        call rrCalc
        '''
        diff = 0
        try:
            fval = float(val)
            fpl = float(self.ui.entry1.text())
            diff = fval-fpl
            diff = '{:.02}'.format(diff)
            # diff = str(fval - fpl)
        except ValueError:
            diff = '0'
        self.ui.stopDiff.setText(diff)
        self.rrCalc(self.ui.targDiff.text(), diff)
        self.setMaxLoss()
    
    def rrCalc(self, targDiff = None, slDiff = None):
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

        print(ftarg, fstop)

        dval = abs(ftarg/fstop)

        f = Fraction(dval).limit_denominator(max_denominator=10)
        srr = f'{f.numerator} : {f.denominator}'
        self.ui.rr.setText(srr)

    def setMaxLoss(self):
        slDiff = self.ui.stopDiff.text()
        shares = self.ui.pos.text()
        shares = shares.split(' ')[0]


        try:
            slDiff = float(slDiff)
            shares = int(shares)
        except ValueError:
            return
        
        val = shares * slDiff
        val = '{:.02f}'.format(val)
        self.ui.maxLoss.setText(val)

        # print(ftarg, fstop)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QMainWindow()
    formUi = Ui_MainWindow()
    formUi.setupUi(w)
    sc = SumControl(formUi)
    w.show()
    sys.exit(app.exec_())
    