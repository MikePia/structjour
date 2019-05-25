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
First try at trade summary using a grid Layout

author: Mike Petersen

created: December 7, 2018
 '''

import sys
from PyQt5.QtWidgets import (QWidget, QApplication, QGridLayout, QLabel, 
                             QLineEdit, QTextEdit, QSizePolicy)
from PyQt5.QtGui import QFont
from journal.thetradeobject import TheTradeObject, SumReqFields
# pylint: disable=C0103
# pylint: disable=C0301

# mod level var

class QtForm(QWidget):
    '''Just the summary part'''

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        '''GUI Constructor'''
        form = dict()
        srf = SumReqFields()

        form[srf.name] = self.labelFactory("Name of stock", "Arial", 16, QFont.Bold, "border: 1px solid black")
        form[srf.acct] = self.labelFactory('live or sim', "Arial", 16, QFont.Bold, "border: 1px solid black")
        form[srf.strat] = self.labelFactory('Strategy', "Arial", 16, QFont.Bold, "border: 1px solid black")
        form[srf.link1] = self.labelFactory('A link to whatever', "Arial", 16, QFont.Bold, "border: 1px solid black")

        form[srf.plhead] = self.labelFactory('P/L', "Arial", 15, QFont.Bold, "border: 1px solid black")
        form[srf.pl] = QLineEdit("P/L")
        form[srf.pl].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        form[srf.starthead] = self.labelFactory('start', "Arial", 15, QFont.Bold, "border: 1px solid black")
        form[srf.start] = QLineEdit("start")
        form[srf.start].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        form[srf.durhead] = self.labelFactory('Pos', "Arial", 15, QFont.Bold, "border: 1px solid black")
        form[srf.dur] = QLineEdit()
        form[srf.dur].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        form[srf.sharehead] = self.labelFactory('Pos', "Arial", 16, QFont.Bold, "border: 1px solid black")
        form[srf.shares] = QLineEdit()
        form[srf.shares].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        form[srf.mkthead] = self.labelFactory('Mkt', "Arial", 15, QFont.Bold, "border: 1px solid black")
        form[srf.mktval] = QLineEdit()
        form[srf.mktval].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        form[srf.targhead] = self.labelFactory('Target', "Arial", 8, QFont.Bold, "border: 1px solid black")
        form[srf.targ] = QLineEdit()
        form[srf.targdiff] = QLineEdit()

        form[srf.stophead] = self.labelFactory('Target', "Arial", 8, QFont.Bold, "border: 1px solid black")
        form[srf.stoploss] = QLineEdit()
        form[srf.sldiff] = QLineEdit()

        form[srf.rrhead] = self.labelFactory('R : R', "Arial", 8, QFont.Bold, "border: 1px solid black")
        form[srf.rr] = QLineEdit()
        form['rrblank'] = self.labelFactory('', "Arial", 8, QFont.Bold, "border: 1px solid black")

        form[srf.maxhead] = self.labelFactory('Max Loss', "Arial", 8, QFont.Bold, "border: 1px solid black")
        form[srf.maxloss] = self.labelFactory('$.50', "Arial", 8, QFont.Bold, "border: 1px solid black")
        form['maxblank'] = self.labelFactory('', "Arial", 8, QFont.Bold, "border: 1px solid black")

        form[srf.mstkhead] = self.labelFactory('Proceeds\nLost', "Arial", 8, QFont.Bold, "border: 1px solid black")
        form[srf.mstkval] = QLineEdit("P/L")
        form[srf.mstkval].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        form[srf.mstknote] = QTextEdit()

        form[srf.entryhead] = self.labelFactory('Entries \nand \nexits', "Arial", 8, QFont.Bold, "border: 1px solid black")

        entry = list()
        for i in range(8):

            entry.append([[self.labelFactory('entry ' + str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"), 'entry' + str(i+1)],
                          [self.labelFactory('exit ' + str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"), 'exit' + str(i+1)],
                          [self.labelFactory('time ' + str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"), 'time' + str(i+1)],
                          [self.labelFactory('eshare ' + str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"), 'eshare' + str(i+1)],
                          [self.labelFactory('diff ' + str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"), 'diff' + str(i+1)],
                          [self.labelFactory('pl ' + str(i+1), "Arial", 8, QFont.Bold, "border: 1px solid black"), 'pl' + str(i+1)],
                          ])
        form['entry'] = entry
        form[srf.explain] = QTextEdit("Description of trade")
        form[srf.notes] = QTextEdit("Analysis of trade")

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(form[srf.name], 1, 0, 1, 3)
        grid.addWidget(form[srf.acct], 1, 3, 1, 3)
        grid.addWidget(form[srf.strat], 1, 6, 1, 3)
        grid.addWidget(form[srf.link1], 1, 9, 1, 3)

        grid.addWidget(form[srf.plhead], 3, 0, 2, 1)
        grid.addWidget(form[srf.pl], 3, 1, 2, 2)

        grid.addWidget(form[srf.starthead], 5, 0, 2, 1)
        grid.addWidget(form[srf.start], 5, 1, 2, 2)

        grid.addWidget(form[srf.durhead], 7, 0, 2, 1)
        grid.addWidget(form[srf.dur], 7, 1, 2, 2)

        grid.addWidget(form[srf.sharehead], 9, 0, 2, 1)
        grid.addWidget(form[srf.shares], 9, 1, 2, 2)

        grid.addWidget(form[srf.mkthead], 11, 0, 2, 1)
        grid.addWidget(form[srf.mktval], 11, 1, 2, 2)

        grid.addWidget(form[srf.targhead], 13, 0, 1, 1)
        grid.addWidget(form[srf.targ], 13, 1, 1, 1)
        grid.addWidget(form[srf.targdiff], 13, 2, 1, 1)

        grid.addWidget(form[srf.stophead], 13, 0, 1, 1)
        grid.addWidget(form[srf.stoploss], 13, 1, 1, 1)
        grid.addWidget(form[srf.sldiff], 13, 2, 1, 1)

        grid.addWidget(form[srf.rrhead], 14, 0, 1, 1)
        grid.addWidget(form[srf.rr], 14, 1, 1, 1)
        grid.addWidget(form['rrblank'], 14, 2, 1, 1)

        grid.addWidget(form[srf.maxhead], 15, 0, 1, 1)
        grid.addWidget(form[srf.maxloss], 15, 1, 1, 1)
        grid.addWidget(form['maxblank'], 15, 2, 1, 1)

        grid.addWidget(form[srf.mstkhead], 16, 0, 2, 1)
        grid.addWidget(form[srf.mktval], 16, 1, 2, 2)
        grid.addWidget(form[srf.mstknote], 18, 0, 2, 3)

        grid.addWidget(form[srf.entryhead], 3, 3, 6, 1)

        for i in range(8):
            for j in range(6):
                grid.addWidget(form['entry'][i][j][0], j+3, 4+i, 1, 1)

        grid.addWidget(form[srf.explain], 9, 3, 6, 9)
        grid.addWidget(form[srf.notes], 15, 3, 6, 9)

        self.form = form

        self.setLayout(grid)

        self.setGeometry(300, 300, 550, 300)
        self.setWindowTitle('Trade Summary')
        self.show()

    def labelFactory(self, text, font, fontsize, flag=None, style=None):
        lbl = QLabel(text)
        lbl.setFont(QFont(font, fontsize, flag))
        if style:
            lbl.setStyleSheet(style)

        return lbl

    def fillForm(self, df):
        '''Fill the qt form from a trade summary dataframe'''
        srf = SumReqFields()

        def getString(val):
            if not isinstance(val, str):
                conv = '{0:0.2f}' if isinstance(val, float) else '{}'
                val = conv.format(val)
            return val


        def fillit(field):

            if isinstance(field, list):
                for i in range(8):
                    for j in range(6):
                        token = field[i][j][1]
                        widget = field[i][j][0]
                        val = df[srf.rc[token]].unique()[0]
                        
                        widget.setText(getString(val))
            else:
                val = df[field].unique()[0]
                self.form[field].setText(getString(val))
        
        fillthese = [srf.name, srf.acct, srf.strat, srf.link1, srf.pl, srf.start, srf.dur, srf.shares, 
        srf.mktval, srf.targ, srf.targhead, srf.targdiff, srf.stoploss, srf.sldiff, srf.rr, srf.maxloss,
        srf.mstkval, srf.mstknote, self.form['entry'], srf.explain, srf.notes ]
        for fld in fillthese:
            fillit(fld)
        # self.form['name'].setText(df[srf.name].unique()[0])
        # self.form['account'].setText(df[srf.acct].unique()[0])
        # self.form['strategy'].setText(df[srf.strat].unique()[0])
        # self.form['link'].setText(df[srf.link1].unique()[0])
        # self.form['pl'].setText('{0:0.2f}'.format(df[srf.pl].unique()[0]))
        # self.form['start'].setText(df[srf.start].unique()[0])
        # self.form['dur'].setText(df[srf.dur].unique()[0])
        # self.form['position'].setText(df[srf.shares].unique()[0])
        # self.form['market'].setText(df[srf.mktval].unique()[0])
        # self.form['target'].setText(df[srf.targ].unique()[0])
        # self.form['targetdiff'].setText(df[srf.targdiff].unique()[0])
        # self.form['stop'].setText(df[srf.stoploss].unique()[0])
        # self.form['stopdiff'].setText(df[srf.sldiff].unique()[0])
        # self.form['rr'].setText(df[srf.rr].unique()[0])
        # self.form['maxloss'].setText(df[srf.maxloss].unique()[0])
        # self.form['mistake'].setText(df[srf.mstkval].unique()[0])
        # self.form['mistakenote'].setText(df[srf.mstknote].unique()[0])

        # e = ['entry', 'exit', 'start', 'eshare', 'diff', 'pl']
        # for i in range(8):
        #     for token in e:
        #         t = token + str(i+1)
        #         self.form[t].setText(df[t].unique()[0])

        # self.form['eplain'].setText(df[srf.explain].unique()[0])
        # self.form['notes'].setText(df[srf.notes].unique()[0])
        



if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = QtForm()
    # sys.exit(app.exec_())
