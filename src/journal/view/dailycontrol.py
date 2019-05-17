import os
import random
import sys

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QAbstractItemView
from PyQt5.QtGui import QIntValidator, QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import Qt

from journal.view.dailyform import  Ui_Form as DailyForm
from journal.view.dfmodel import PandasModel
from journal.dailysumforms import MistakeSummary





class DailyControl(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.ui = DailyForm()
        self.ui.setupUi(self)

    def runDialog(self, df, tradeSum=None):
        self.ts = tradeSum
        self.modelT = PandasModel(df)
        self.ui.tradeTable.setModel(self.modelT)

        self.modelM = QStandardItemModel(self)
        self.ui.tradeTable.resizeColumnsToContents()
        self.ui.mstkForm.setModel(self.modelM)
        self.ui.mstkForm.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.populate()
        self.show()

    def populate(self):
        cell = QStandardItem('Mistake Summary')
        cell.setTextAlignment(Qt.AlignCenter)
        cell.setFont(QFont('Arial Rounded MT Bold', pointSize=24))
        row = [cell]
        self.modelM.appendRow(row)
        row = []
        for d in ['Name', 'P / L', 'Lost P/L', 'Mistake or pertinent feature of trade']:
            cell = QStandardItem(d)
            cell.setFont(QFont('Arial Narrow', pointSize=16, weight=63))
            row.append(cell)
        self.modelM.appendRow(row)

        for trade in self.ts:
            row = []
            row.append(QStandardItem(trade))

            pl = self.ts[trade]['P / L'].unique()[0]
            if pl and isinstance(pl, (np.floating, float)):
                pl = '${:.02f}'.format(pl)
            row.append(QStandardItem(pl))

            mVal = self.ts[trade]['MstkVal'].unique()[0]
            if mVal and isinstance(mVal, (np.floating, float)):
                mVal = '${:.02f}'.format(mVal)
            row.append(QStandardItem(mVal))
            
            row.append(QStandardItem(self.ts[trade]['MstkNote'].unique()[0]))
            self.modelM.appendRow(row)
        self.ui.mstkForm.setSpan(0, 0, 1, 4)
        self.ui.mstkForm.setRowHeight(0, 50)
        # self.ui.mstkForm.resizeColumnToContents(0)
        self.ui.mstkForm.resizeColumnToContents(1)
        self.ui.mstkForm.resizeColumnToContents(2)
        self.mistSum = MistakeSummary(4)
        print(self.mistSum.mistakeFields)
        print()




from journal.thetradeobject import SumReqFields
# pylint: disable = C0103


class MistakeSummaryQ:
    '''
    Coordinates and style info for the two daily forms. Coordinates are intended for qt. Unfortunately
    the excel coorinates in Mistake Summary are unusable because of the merge cells which allows
    multiple forms to exist in single page. Here we use the same keys so we can address the data
    in theTradeObject with the same keys..
    '''

    def __init__(self, numTrades, anchor=(1, 1)):

        self.anchor = anchor
        self.numTrades = numTrades

        # Create the data structure to make a styled shape for the Mistake Summary Form
        # 'key':[rng,style, value]
        mistakeFields = {
            'title': [[(0, 0), (0, 4)], 'titleStyle', 'Mistake Summary'],
            'headname': [(1, 1), 'normStyle', 'Name'],
            'headpl': [(1, 2), 'normStyle', "P / L"],
            'headLossPL': [(1, 3), 'normStyle', "Lost P/L"],
            'headmistake': [(1, 4), 'normStyle',
                            "Mistake or pertinent feature of trade."],

        }
        # Dynamically add rows to mistakeFields
        for i in range(numTrades):
            n = "name" + str(i + 1)
            tp = "tpl" + str(i + 1)
            p = "pl" + str(i + 1)
            m = "mistake" + str(i + 1)
            ncells = (1 + i, 0),  # [(1,4), (2,4)]
            tpcells = (2 + i, 0)
            pcells = (4, 4 + i)
            mcells = [(5, 4 + i), (12, 4 + i)]
            mistakeFields[n] = [ncells, 'normStyle']
            mistakeFields[tp] = [tpcells, 'normalNumber']
            mistakeFields[p] = [pcells, 'normalNumber']
            mistakeFields[m] = [mcells, 'finalNoteStyle']

        mistakeFields['blank1'] = [
            [(1, 4 + numTrades), (2, 4 + numTrades)], 'normStyle']
        mistakeFields['blank3'] = [(3, 4 + numTrades), 'normalNumber']
        mistakeFields['total'] = [(4, 4 + numTrades), 'normalNumber']
        mistakeFields['blank2'] = [
            [(5, 4 + numTrades), (12, 4 + numTrades)], 'normStyle']

        # Create the data structure to create a styled shape for the Daily Summary Form
        # 'key':[rng, style, value] 
        dailySummaryFields = {
            'title': [[(0, 0), (0, 3)], 'titleStyle', "Daily P / L Summary"],
            'headlivetot': [(1, 0), 'normStyle', "Live Total"],
            'headsimtot': [(2, 0),  'normStyle', "Sim Total"],
            'headhighest': [(3, 0), 'normStyle', "Highest Profit"],
            'headlowest': [ (4, 0), 'normStyle', "Largest Loss"],
            'headavgwin': [ (5, 0), 'normStyle', "Average Win"],
            'headavgloss': [ (6, 0), 'normStyle', "Average Loss"],

            'livetot': [(1, 1), 'normalNumber'],
            'simtot': [(2, 1), 'normalNumber'],
            'highest': [(3, 1), 'normalNumber'],
            'lowest': [(4, 1), 'normalNumber'],
            'avgwin': [(5, 1), 'normalNumber'],
            'avgloss': [(6, 1), 'normalNumber'],

            'livetotnote': [(1, 2), 'normStyle'],
            'simtotnote': [(2, 2), 'normStyle'],
            'highestnote': [(3, 2), 'normStyle'],
            'lowestnote': [(4, 2), 'normStyle'],
            'avgwinnote': [(5, 2), 'normStyle'],
            'avglossnote': [(6, 2), 'normStyle'],
        }


        # Excel formulas belong in the mstkval and mstknote columns. The srf.tfcolumns bit
        # are the target addresses for the Excel formula. The cell translation
        # takes place when we create and populate the Workbook.
        formulas = dict()
        srf = SumReqFields()
        for i in range(numTrades):

            tp = "tpl" + str(i+1)
            formulas[tp] = ['={0}', srf.tfcolumns[srf.pl][0][0]]
            p = "pl" + str(i + 1)
            formulas[p] = ['={0}', srf.tfcolumns[srf.mstkval][0][0]]
            m = "mistake" + str(i + 1)
            formulas[m] = ['={0}', srf.tfcolumns[srf.mstknote][0][0]]

        self.formulas = formulas
        self.mistakeFields = mistakeFields
        self.dailySummaryFields = dailySummaryFields


    # def mstkSumStyle(self, ws, tf, anchor=(1, 1)):
    #     '''
    #     Create the shape and stye for the Mistake summary form, populate the static values.
    #     The rest is done in layoutsheet including formulas (with cell translation) and the
    #     names, each with a hyperinks to the Trade Summary form.
    #     :params ws: The openpyx worksheet object
    #     :params tf: The TradeFormat object which has the styles
    #     :params anchor: The cell value at the Top left of the form in tuple form.
    #     '''
    #     a = anchor

    #     # Merge the cells, apply the styles, and populate the fields we can--the
    #     # fields that don't know any details todays trades (other than how many trades)
    #     # That includes the non-formula fields and the sum formula below
    #     for key in self.mistakeFields:
    #         rng = self.mistakeFields[key][0]
    #         style = self.mistakeFields[key][1]

    #         if isinstance(self.mistakeFields[key][0], list):
    #             tf.mergeStuff(ws, rng[0], rng[1], anchor=a)
    #             ws[tcell(rng[0], anchor=a)].style = tf.styles[style]
    #             mrng = tcell(rng[0], rng[1], anchor=a)
    #             style_range(ws, mrng, border=tf.styles[style].border)
    #             if len(self.mistakeFields[key]) == 3:
    #                 ws[tcell(rng[0], anchor=a)] = self.mistakeFields[key][2]

    #         else:
    #             ws[tcell(rng, anchor=a)].style = tf.styles[style]
    #             if len(self.mistakeFields[key]) == 3:
    #                 # ws[tcell(rng, anchor=a)] = headers[key]
    #                 ws[tcell(rng, anchor=a)] = self.mistakeFields[key][2]

    #     # The total sum formula is done here. It is self contained to references to the Mistake
    #     # Summary form
    #     totcell = self.mistakeFields['total'][0]
    #     begincell = (totcell[0], totcell[1] - self.numTrades)
    #     endcell = (totcell[0], totcell[1] - 1)
    #     rng = tcell(begincell, endcell, anchor=a)
    #     totcell = tcell(totcell, anchor=a)
    #     f = '=SUM({0})'.format(rng)
    #     ws[totcell] = f

    # def dailySumStyle(self, ws, tf, anchor=(1, 1)):
    #     '''
    #     Create the shape and populate the daily Summary Form
    #     :params:ws: The openpyxl Worksheet object
    #     :parmas:tf: The TradeFormat object. It holds the styles used.
    #     :params:listOfTrade: A python list of DataFrames, each one a trade with multiple tickets
    #     :params:anchor: The location of the top left corner of the form
    #     TODO: This is probably better placed in layoutSheet -- similar to
    #           LayoutSheet.populateMistakeForm() and using the Trade Summaries object instead of the
    #           trades object... may do that later, but now-- I'm going to finish this version --
    #           momentum and all.
    #     '''

    #     # Alter the anchor to place this form below the (dynamically sized) Mistake form
    #     anchor = (anchor[0], anchor[1] + self.numTrades + 5)

    #     for key in self.dailySummaryFields:
    #         rng = self.dailySummaryFields[key][0]
    #         style = self.dailySummaryFields[key][1]
    #         if isinstance(rng, list):
    #             tf.mergeStuff(ws, rng[0], rng[1], anchor=anchor)
    #             ws[tcell(rng[0], anchor=anchor)].style = tf.styles[style]
    #             mrng = tcell(rng[0], rng[1], anchor=anchor)
    #             style_range(ws, mrng, border=tf.styles[style].border)
    #             # if key in headers:
    #             if len(self.dailySummaryFields[key]) == 3:

    #                 ws[tcell(rng[0], anchor=anchor)] = self.dailySummaryFields[key][2]

    #         else:
    #             ws[tcell(rng, anchor=anchor)].style = tf.styles[style]
    #             # if key in headers:
    #             if len(self.dailySummaryFields[key]) == 3:
    #                 ws[tcell(rng, anchor=anchor)] = self.dailySummaryFields[key][2]
    #         # if len(self.dailySummaryFields[key] > 2) :
    #             # ws[tcell(rng, anchor=anchor)] = self.dailySummaryFields[key][2]






if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    app = QApplication(sys.argv)
    w = DailyControl()
    fn = 'C:/trader/journal/_201904_April/_0403_Wednesday/trades.csv'
    if not os.path.exists(fn):
        sys.exit(app.exec_())
    dff = pd.read_csv(fn)
    print('gotta create swingTrade data type here to run this thing seperately')
    w.runDialog(dff)
    w.show()
    sys.exit(app.exec_())
