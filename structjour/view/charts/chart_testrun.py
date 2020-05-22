import sys

# import pandas as pd
# from structjour.view.charts.intradayprofit_barchart import Canvas as CanvasDP

# from structjour.view.charts.generic_barchart import BarChart
from structjour.view.charts.generic_piechart_legend import Piechart
# from structjour.view.charts.chartdatabase import IntradayProfit_BarchartData as BarchartData
# from structjour.view.charts.chartdatabase import MultiTradeProfit_BarchartData
from structjour.view.charts.chartdatabase import StrategyPercentages_PiechartData
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy
from PyQt5.QtCore import QDate


class chartTestRun(QMainWindow):

    def __init__(self):
        super().__init__()
        # date = pd.Timestamp('20200102')
        # TradeSum uses the account alias (currently Live or SIM)

        cud = {'inTimeGroups': None,
               'accounts': None,
               'dates': (QDate(2020, 7, 11), QDate(2020, 7, 11)),
               'inNumSets': 21,
               'side': 'Both',
               'strategies': [],
               'symbols': [],
               'tags': []}

        chartData = StrategyPercentages_PiechartData(cud)
        pc = Piechart(chartData)

        pc.setSizePolicy((QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)))
        pc.setMinimumSize(300, 300)
        self.setCentralWidget(pc)
        pc.plot()

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = chartTestRun()
    sys.exit(app.exec())
