import sys

# import pandas as pd
# from structjour.view.charts.intradayprofit_barchart import Canvas as CanvasDP

from structjour.view.charts.generic_barchart import BarChart
from structjour.view.charts.generic_piechart_legend import Piechart
# from structjour.view.charts.chartdatabase import IntradayProfit_BarchartData as BarchartData
from structjour.view.charts.multitradeprofit_barchartdata import MultiTradeProfit_BarchartData
# from structjour.view.charts.strategypercentages_piechartdata import StrategyPercentages_PiechartData
# from structjour.view.charts.strategyaverage_barchartdata import StrategyAverage_BarchartData
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy
from PyQt5.QtCore import QDate
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolBar


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
               'strategies2': [],
               'symbols': [],
               'tags': []}

        # chartData = StrategyAverage_BarchartData(cud)
        chartData = MultiTradeProfit_BarchartData(cud)
        bc = BarChart(chartData)
        # bc = BarChart(chartData)

        bc.setSizePolicy((QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)))
        bc.setMinimumSize(300, 300)
        self.addToolBar(NavToolBar(bc, self))

        self.setCentralWidget(bc)
        # bc.plot()
        bc.plot()

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = chartTestRun()
    sys.exit(app.exec())
