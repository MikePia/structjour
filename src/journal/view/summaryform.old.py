
'''
First try at trade summary using a grid Layout

author: Mike Petersen

created: December 7, 2018
 '''

import os
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLabel, QLineEdit, QTextEdit, QSizePolicy
from PyQt5.QtGui import QFont
# pylint: disable=C0103


class SummaryForm(QWidget):
    '''Just the summary part'''

    def __init__(self):
        super().__init__()
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))

        self.initExample()


    def initExample(self):
        '''GUI Constructor'''

        title = self.labelFactory("SQ Long", "Arial", 16, QFont.Bold)
        account = self.labelFactory('Live', "Arial", 16, QFont.Bold)
        strategy = self.labelFactory('Strategy', "Arial", 16, QFont.Bold)
        link = self.labelFactory('A link', "Arial", 16, QFont.Bold)
        
        plhead = self.labelFactory('P/L', "Arial", 15, QFont.Bold)
        
        pl = self.labelFactory('831.96', 'Droid Sans', 16, QFont.Bold)

        starthead = self.labelFactory('start', "Arial", 15, QFont.Bold)
        start = self.labelFactory('start' ,'Droid Sans', 16, QFont.Bold)
        
        durhead = self.labelFactory('Pos', "Arial", 15, QFont.Bold)
        dur = self.labelFactory('3 hours 16:42', 'DroidSans', 12, QFont.Bold)

        positionhead =  self.labelFactory('Pos', "Arial", 16, QFont.Bold)
        position = self.labelFactory('750 shares', 'DroidSans', 16, QFont.Bold)
        
        markethead = self.labelFactory('Mkt', "Arial", 15, QFont.Bold)
        market = self.labelFactory('25881.50', 'DroidSans', 16, QFont.Bold)

        targethead = self.labelFactory('target', 'DroidSans', 8, QFont.Bold)
        target = self.lineEditFactory('34.51', 'DroidSans', 8, QFont.Bold)
        targetdiff = self.labelFactory('1.01', 'DroidSans', 8, QFont.Bold)


        stophead = self.labelFactory('Stop Loss', "Arial", 8, QFont.Bold)
        stop = self.lineEditFactory('32.75', 'DroidSans', 8, QFont.Bold)
        stopdiff = self.labelFactory('-0.75', 'DroidSans', 8, QFont.Bold)

        rrhead = self.labelFactory('R : R', "Arial", 8, QFont.Bold)
        rr = self.labelFactory('1.5 : 1', 'DroidSans', 8, QFont.Bold)
        rrblank = self.labelFactory('', "Arial", 8, QFont.Bold)

        maxhead = self.labelFactory('Max Loss', "Arial", 8, QFont.Bold)
        maxloss = self.labelFactory('562', "DroidSans", 8, QFont.Bold)
        maxblank = self.labelFactory('', "Arial", 8, QFont.Bold)

        mistakehead = self.labelFactory('Proceeds\nLost', "Arial", 8, QFont.Bold)
        mistake = self.lineEditFactory('', 'DroidSans', 8, QFont.Bold)
        mistakenote = QTextEdit('Summary note')

        entryhead = self.labelFactory('entry:', "DroidSans", 8, QFont.Bold, style="border: 0px solid blue")
        exithead = self.labelFactory('exit:', "DroidSans", 8, QFont.Bold, style="border: 0px solid blue")
        timehead = self.labelFactory('time:', "DroidSans", 8, QFont.Bold, style="border: 0px solid blue")
        sharehead = self.labelFactory('share:', "DroidSans", 8, QFont.Bold, style="border: 0px solid blue")
        diffhead = self.labelFactory('diff:', "DroidSans", 8, QFont.Bold, style="border: 0px solid blue")
        tplhead = self.labelFactory('pl:', "DroidSans", 8, QFont.Bold, style="border: 0px solid blue")

        entry = list()
        entries = ['$33.50', '', '', '', '', '', '', '']
        exits = ['', '$32.43', '', '', '', '', '', '']
        starts = ['09:34:21', '09:39:01', '', '', '', '', '', '']
        shares = ['750', '-750', '', '', '', '', '', '']
        diffs = ['', '$1.07', '', '', '', '', '', '']
        pls = ['', '$547.50', '', '', '', '', '', '']
        for i in range(8):
            entry.append([self.labelFactory(entries[i], "Arial", 8, QFont.Bold  ),
                          self.labelFactory(exits[i], "Arial", 8, QFont.Bold  ),
                          self.labelFactory(starts[i], "Arial", 8, QFont.Bold  ),
                          self.labelFactory(shares[i], "Arial", 8, QFont.Bold  ),
                          self.labelFactory(diffs[i], "Arial", 8, QFont.Bold  ),
                          self.labelFactory(pls[i], "Arial", 8, QFont.Bold  ),

            ])
            explain = QTextEdit("Description of trade")
            notes = QTextEdit("Analysis of trade")

        
        
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0, 1, 3)
        grid.addWidget(account, 1, 3, 1, 3)
        grid.addWidget(strategy, 1, 6, 1, 3)
        grid.addWidget(link, 1, 9, 1, 3)

        grid.addWidget(plhead, 3, 0, 2, 1)
        grid.addWidget(pl, 3, 1, 2, 2)

        grid.addWidget(starthead, 5, 0, 2, 1)
        grid.addWidget(start, 5, 1, 2, 2)

        grid.addWidget(durhead, 7, 0, 2, 1)
        grid.addWidget(dur, 7, 1, 2, 2)

        grid.addWidget(positionhead, 9, 0, 2, 1)
        grid.addWidget(position, 9, 1, 2, 2)

        grid.addWidget(markethead, 11, 0, 2, 1)
        grid.addWidget(market, 11, 1, 2, 2)

        grid.addWidget(targethead, 13, 0, 1, 1)
        grid.addWidget(target, 13, 1, 1, 1)
        grid.addWidget(targetdiff, 13, 2, 1, 1)


        # grid.addWidget(targethead, 13, 0, 1, 1)
        # grid.addWidget(target, 13, 1, 1, 1)
        # grid.addWidget(targetdiff, 13, 2, 1, 1)

        grid.addWidget(stophead, 14, 0, 1, 1)
        grid.addWidget(stop, 14, 1, 1, 1)
        grid.addWidget(stopdiff, 14, 2, 1, 1)

        grid.addWidget(rrhead, 15, 0, 1, 1)
        grid.addWidget(rr, 15, 1, 1, 1)
        grid.addWidget(rrblank, 15, 2, 1, 1)

        grid.addWidget(maxhead, 16, 0, 1, 1)
        grid.addWidget(maxloss, 16, 1, 1, 1)
        grid.addWidget(maxblank, 16, 2, 1, 1)

        grid.addWidget(mistakehead, 17, 0, 2, 1)
        grid.addWidget(mistake, 17, 1, 2, 2)
        grid.addWidget(mistakenote, 19, 0, 2, 3)


        grid.addWidget(entryhead, 3, 3, 1, 1)
        grid.addWidget(exithead, 4, 3, 1, 1)
        grid.addWidget(timehead, 5, 3, 1, 1)
        grid.addWidget(sharehead, 6, 3, 1, 1)
        grid.addWidget(diffhead, 7, 3, 1, 1)
        grid.addWidget(tplhead, 8, 3, 1, 1)
        

        for i in range(8):
            for j in range(6) :
                grid.addWidget(entry[i][j], j+3, 4+i, 1, 1)

        grid.addWidget(explain, 9, 3, 6, 9)
        grid.addWidget(notes, 15, 3, 6, 9)
 

        self.setLayout(grid)

        self.setGeometry(300, 300, 550, 300)
        self.setWindowTitle('Trade Summary')
        self.show()

    def labelFactory(self, text, font, fontsize, flag=None, style=None, policy=None) :
        lbl = QLabel(text)
        lbl.setFont(QFont(font, fontsize, flag) )
        if not style:
            style = "border: 1px solid black"
        lbl.setStyleSheet(style)
        if policy:
            lbl.setSizePolicy(*policy)

        return lbl

    def lineEditFactory(self, text, font, fontsize, flag=None, style=None, policy=None):
        le = QLineEdit(text)
        le.setFont(QFont(font, fontsize, flag))
        if style:
            le.setStyleSheet(style);
        if policy == None:
            policy = [QSizePolicy.Minimum, QSizePolicy.Preferred]
        # le.setSizePolicy(*policy)
        return le

        

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = SummaryForm()
    sys.exit(app.exec_())
