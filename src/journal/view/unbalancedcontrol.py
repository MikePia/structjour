'''
Instantiate the ui form and create all the needed connections to run it.

Created on April 12, 2019

@author: Mike Petersen
'''

import os
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QDialog, QLCDNumber
from PyQt5.QtGui import QIntValidator

from journal.view.unbalanced import Ui_Dialog
from journal.view.dfmodel import PandasModel
from journal.view.styledhtml import StyledHTML

# pylint: disable = C0301, C0103


class UnbalControl(QDialog):

    def __init__(self):
        super().__init__(parent=None)

    # TODO figure out a way to pre-process the red and green in the unbal dialogue and retain generality with this class.
    def runDialog(self, df, ticker, shares, swingTrade):

        ui = Ui_Dialog()
        ui.setupUi(self)
        slist = [ticker]
        self.shares = shares
        self.ui = ui
        self.swingTrade = swingTrade

        ui.unbalBefore.textChanged.connect(self.setValueB)
        ui.unbalAfter.textChanged.connect(self.setValueA)
        ui.unbalBefore.returnPressed.connect(self.beforePressed)
        ui.unbalAfter.returnPressed.connect(self.afterPressed)
        ui.okBtn.pressed.connect(self.wereDone)


        v = QIntValidator()
        ui.unbalBefore.setValidator(v)
        ui.unbalAfter.setValidator(v)

        ui.unbalShares.setText(str(shares))

        slist.extend(self.getRepl(shares))

        template = '''<h3> <div class="large"> <p>Unbalanced shares of {0} for<span class="blue"> {1} </span>shares</p> </div> </h3> <p class="explain"> Adjust the shares held before and after this statement to bring the unbalanced shares to 0. Solutions might look like one of the following</p> <ul> <li> <span class="red">{2} </span>shares held before and 0 shares held after</li> <li> 0 shares held before and<span class="green"> {1} </span>shares held after</li> <li> <span class="green">{3} </span>shares held before and<span class="green"> {4}.</span> shares held after</li> </ul>'''

        css = '''p,li { white-space: pre-wrap; } h3 { margin-top: 6px; margin-bottom: 12px; margin-left: 0px; margin-right: 0px; text-indent: 0px; } body { font-family: Arial, Helvetica, sans-serif; font-size: 7.8pt; font-weight: 400; font-style: normal; } .large { font-size: large; font-weight: 600; } .blue { font-size: large; font-weight: 600; color: #0000ff; } .red { font-weight: 600; color: #aa0000; } .green { font-weight: 600; color: #00ff00; } .explain { margin-top: 12px; margin-bottom: 12px; margin-left: 0px; margin-right: 0px; text-indent: 10px; } ul { margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; } li { font-size: 8pt; margin-top: 12px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; text-indent: 0px; } .li2 { margin-top: 0px; } .li3 { margin-top: 0px; margin-bottom: 12px; } '''
        x = StyledHTML(css, template, slist)
        h = x.makehtml()
        ui.explain.setHtml(h)
        model = PandasModel(df)
        ui.tradeTable.setModel(model)
        

    def wereDone(self):
        valB = self.ui.unbalBefore.text()
        valA = self.ui.unbalAfter.text()

        valA = '0' if not valA or valA == '-' else valA
        valB = '0' if not valB or valB == '-' else valB

        ivalA = int(valA)
        ivalB = int(valB)
        tval = int(self.shares) if self.shares else 0
        setto = ivalB + tval - ivalA

        if setto == 0:
            self.swingTrade['shares'] = setto
            self.swingTrade['before'] = ivalB
            self.swingTrade['after'] = ivalA

        self.close()
        self.done(0)

    def beforePressed(self):
        valA = self.ui.unbalAfter.text()
        valA = '0' if not valA or valA == '-' else valA
        ivalA = int(valA)

        valB = self.ui.unbalBefore.text()
        valB = '0' if not valB or valB == '-' else valB
        ivalB = int(valB)

        tval = int(self.shares) if self.shares else 0
        
        if not ivalB:
            assert isinstance(self.shares, int)
            ivalB = -self.shares
            ivalA = 0
            setto = 0
        else:
            ivalA = ivalB + tval
        
        self.ui.unbalShares.setText('0')
        self.ui.unbalAfter.setText(str(ivalA))
        self.ui.unbalBefore.setText(str(ivalB))

    def afterPressed(self):
        valA = self.ui.unbalAfter.text()
        valA = '0' if not valA or valA == '-' else valA
        ivalA = int(valA)

        valB = self.ui.unbalBefore.text()
        valB = '0' if not valB or valB == '-' else valB
        ivalB = int(valB)

        tval = int(self.shares) if self.shares else 0
        
        if not ivalA:
            assert isinstance(self.shares, int)
            ivalA = self.shares
            ivalB = 0
            setto = 0
        else:
            ivalB = ivalA - tval
        
        self.ui.unbalShares.setText('0')
        self.ui.unbalAfter.setText(str(ivalA))
        self.ui.unbalBefore.setText(str(ivalB))


    def setValueB(self, val):
        valA = self.ui.unbalAfter.text()
        valA = '0' if not valA or valA == '-' else valA
        ivalA = int(valA)

        valB = '0' if not val or val == '-' else val
        ivalB = int(valB)

        tval = int(self.shares) if self.shares else 0

        setto = ivalB + tval - ivalA
        self.ui.unbalShares.setText(str(setto))


    def setValueA(self, val):
        valA = '0' if not val or val == '-' else val
        ivalA = int(valA)

        valB = self.ui.unbalBefore.text()
        valB = '0' if not valB or valB == '-' else valB
        ivalB = int(valB)

        tval = int(self.shares) if self.shares else 0

        setto = ivalB + tval - ivalA
        self.ui.unbalShares.setText(str(setto))



    def getRepl(self, shares):
        if not shares:
            return None
        fshares1 = int(shares)
        fshares2 = -fshares1
        fshares3 = 100
        fshares4 = fshares1 + 100
        return [str(fshares1), str(fshares2), str(fshares3), str(fshares4)]

if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    w = UnbalControl()
    fn = 'C:/trader/journal/_201904_April/_0403_Wednesday/trades.csv'
    if not os.path.exists(fn):
        sys.exit(app.exec_())
    dff = pd.read_csv(fn)
    print('gotta create swingTrade data type here to run this thing seperately')
    # w.runDialog(dff, 'APPL', -1000)
    sys.exit(app.exec_())
