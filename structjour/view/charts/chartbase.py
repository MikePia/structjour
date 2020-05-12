

from structjour.view.charts.chartdatabase import ChartDataBase

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartBase(FigureCanvas):

    def __init__(self, chartData, parent=None, width=15, height=5, dpi=100):
        '''
        A virtual (by agreement) base class for Qt embedded matplot lib charts
        :params chartData: A subclass of ChartDataBase. The data for this particular chart
        :params parent: QWidget parent class
        :params width: matplot lib figure.width
        :params height: matplot lib figure.height
        :params dpi: matplot lib figure.dpi
        '''
        self.chartData = chartData
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.chartData.getChartData()

        self.plot()

    chartData = None

    def setChartData(self, chartData):
        assert isinstance(chartData, ChartDataBase)

        self.chartData = chartData
        return self

    def plot(self):
        self.getChartData(self)
