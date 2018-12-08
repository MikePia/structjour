
'''
First try at trade summary using a grid Layout

author: Mike Petersen

created: December 7, 2018
 '''

import sys
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLabel, QLineEdit, QTextEdit, QSizePolicy
from PyQt5.QtGui import QFont
# pylint: disable=C0103


class QtForm(QWidget):
    '''Just the summary part'''

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        '''GUI Constructor'''

        title = self.labelFactory("Name of stock", "Arial", 16, QFont.Bold, "border: 1px solid black")
        account = self.labelFactory('live or sim', "Arial", 16, QFont.Bold, "border: 1px solid black")
        strategy = self.labelFactory('Strategy', "Arial", 16, QFont.Bold, "border: 1px solid black")
        link = self.labelFactory('A link to whatever', "Arial", 16, QFont.Bold, "border: 1px solid black")
        
        plhead = self.labelFactory('P/L', "Arial", 15, QFont.Bold, "border: 1px solid black")
        pl = QLineEdit("P/L")
        pl.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        starthead = self.labelFactory('start', "Arial", 15, QFont.Bold, "border: 1px solid black")
        start = QLineEdit("start")
        start.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        
        durhead = self.labelFactory('Pos', "Arial", 15, QFont.Bold, "border: 1px solid black")
        dur = QLineEdit()
        dur.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        positionhead =  self.labelFactory('Pos', "Arial", 16, QFont.Bold, "border: 1px solid black")
        position = QLineEdit()
        position.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        
        markethead = self.labelFactory('Mkt', "Arial", 15, QFont.Bold, "border: 1px solid black")
        market = QLineEdit()
        market.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        targethead = self.labelFactory('Target', "Arial", 8, QFont.Bold, "border: 1px solid black")
        target = QLineEdit()
        targetdiff = QLineEdit()

        stophead = self.labelFactory('Target', "Arial", 8, QFont.Bold, "border: 1px solid black")
        stop = QLineEdit()
        stopdiff = QLineEdit()

        rrhead = self.labelFactory('R : R', "Arial", 8, QFont.Bold, "border: 1px solid black")
        rr = QLineEdit()
        rrblank = self.labelFactory('', "Arial", 8, QFont.Bold, "border: 1px solid black")

        maxhead = self.labelFactory('Max Loss', "Arial", 8, QFont.Bold, "border: 1px solid black")
        maxloss = self.labelFactory('$.50', "Arial", 8, QFont.Bold, "border: 1px solid black")
        maxblank = self.labelFactory('', "Arial", 8, QFont.Bold, "border: 1px solid black")

        mistakehead = self.labelFactory('Proceeds\nLost', "Arial", 8, QFont.Bold, "border: 1px solid black")
        mistake = QLineEdit("P/L")
        mistake.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        mistakenote = QTextEdit()

        entriesHead = self.labelFactory('Entries \nand \nexits', "Arial", 8, QFont.Bold, "border: 1px solid black")

        entry= list()
        for i in range(8) :
            entry.append([self.labelFactory('entry ' + str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"  ),
                          self.labelFactory('exit ' +  str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"  ),
                          self.labelFactory('start ' +  str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"  ),
                          self.labelFactory('share ' +  str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"  ),
                          self.labelFactory('diff ' +  str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"  ),
                          self.labelFactory('pl ' +  str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"  ),

            ])
            explain = QTextEdit("Description of trade")
            notes = QTextEdit("Analysis of trade")

        
        
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0, 1, 3)
        grid.addWidget(account,  1, 3, 1, 3)
        grid.addWidget(strategy, 1, 6, 1, 3)
        grid.addWidget(link, 1, 9, 1, 3)

        grid.addWidget(plhead, 3, 0, 2, 1)
        grid.addWidget(pl, 3, 1, 2, 2)

        grid.addWidget(starthead, 5, 0, 2, 1)
        grid.addWidget(start, 5, 1, 2, 2)

        grid.addWidget(durhead, 7, 0, 2, 1)
        grid.addWidget(dur,7, 1, 2, 2)

        grid.addWidget(positionhead, 9, 0, 2, 1)
        grid.addWidget(position, 9, 1, 2, 2)

        grid.addWidget(markethead, 11, 0, 2, 1)
        grid.addWidget(market, 11, 1, 2, 2)

        grid.addWidget(targethead, 13, 0, 1, 1)
        grid.addWidget(target, 13, 1, 1, 1)
        grid.addWidget(targetdiff, 13, 2, 1, 1)


        grid.addWidget(targethead, 13, 0, 1, 1)
        grid.addWidget(target, 13, 1, 1, 1)
        grid.addWidget(targetdiff, 13, 2, 1, 1)

        grid.addWidget(stophead, 13, 0, 1, 1)
        grid.addWidget(stop, 13, 1, 1, 1)
        grid.addWidget(targetdiff, 13, 2, 1, 1)

        grid.addWidget(rrhead, 14, 0, 1, 1)
        grid.addWidget(rr, 14, 1, 1, 1)
        grid.addWidget(rrblank, 14, 2, 1, 1)

        grid.addWidget(maxhead, 15, 0, 1, 1)
        grid.addWidget(maxloss, 15, 1, 1, 1)
        grid.addWidget(maxblank, 15, 2, 1, 1)

        grid.addWidget(mistakehead, 16, 0, 2, 1)
        grid.addWidget(mistake, 16, 1, 2, 2)
        grid.addWidget(mistakenote, 18, 0, 2, 3)


        grid.addWidget(entriesHead, 3, 3, 6, 1)

        for i in range(8):
            for j in range(6) :
                grid.addWidget(entry[i][j], j+3, 4+i, 1, 1)

        grid.addWidget(explain, 9, 3, 6, 9)
        grid.addWidget(notes, 15, 3, 6, 9)
 

        self.setLayout(grid)

        self.setGeometry(300, 300, 550, 300)
        self.setWindowTitle('Trade Summary')
        self.show()

    def labelFactory(self, text, font, fontsize, flag=None, style=None) :
        lbl = QLabel(text)
        lbl.setFont(QFont(font, fontsize, flag) )
        if style:
            lbl.setStyleSheet(style);

        return lbl
        

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = QtFormExample()
    sys.exit(app.exec_())
