from structjour.models.trademodels import TradeSum
from structjour.models.meta import ModelBase


class ChartDataBase:
    '''
    A base class for chart data. The constructor provides the code to handle the user input
    generated from the statisticshub widget. Therefore, this class is tightly coupled with
    the Qt form through the cud (chart_user_dict). Instantiated classes will handle the fields
    that are unique to a particular chart.
    :params cud: A dict containg the usr selections to filter the chart
    :type cud.keys(): symbols: list<str>
                      side: str one of [Both, Long, Short]
                      tags: list<str>
                      inNumSets: int: inNumSets or inTimeGroups can be active, default is inNumSets = (20 or user setting)
                      inTimeGroups: One of [day, week, month, year]
                      strategies: list<str>
                      dates: tuple<pd.Timestamp> (start, end)
                      accounts: str can be 'All Accounts' or an account alias (an entry in TradeSums.account)

    '''
    def __init__(self, cud):
        self.cud = cud
        self.query = None

    def runFilters(self):
        if self.query is None:
            return
        self.filter_by_accounts()
        self.filter_by_dates()
        self.filter_by_side()
        self.filter_by_strategies()
        self.filter_by_symbols()
        self.filter_by_tags()

    def getChartData(self):

        return []

    def filter_by_symbols(self):
        key = 'symbols'
        if key in self.cud:
            print(self.cud[key])
        else:
            print('self.cud is missing key', key)

    def filter_by_side(self):
        key = 'side'
        if key in self.cud:
            print(self.cud[key])
        else:
            print('self.cud is missing key', key)

    def filter_by_tags(self):
        key = 'tags'
        if key in self.cud:
            print(self.cud[key])
        else:
            print('self.cud is missing key', key)

    def view_inNumSets(self):
        key = 'inNumSets'
        if key in self.cud:
            print(self.cud[key])
        else:
            print('self.cud is missing key', key)

    def view_inTimeGroups(self):
        # inTimeGroups
        key = 'inTimeGroups'
        if key in self.cud:
            print(self.cud[key])
        else:
            print('self.cud is missing key', key)

    def filter_by_strategies(self):
        # strategies
        key = 'strategies'
        if key in self.cud:
            print(self.cud[key])
        else:
            print('self.cud is missing key', key)

    def filter_by_dates(self):
        key = 'dates'
        if key in self.cud:
            print(self.cud[key])
        else:
            print('self.cud is missing key', key)

    def filter_by_accounts(self):
        # accounts
        key = 'accounts'
        if key in self.cud and not str(self.cud[key]) in [None, '', 'All Accounts'] and self.query is not None:
            self.query = self.query.filter_by(account=self.cud[key])
            print(self.cud[key])
        else:
            print('self.cud is missing key', key)


class BarchartData(ChartDataBase):
    '''
    Inheritors of this class must:
        1) define the class variables data, names, date
        2) define getChartData and save the result to self.query: a sqlalchemy query object
    Use the ModelBase.session object. Be careful to set session_new only once and call
    session.close after createing the chart
    '''

    data = None
    names = None
    date = None
    neg = None
    pos = None

    def getFormatGraphArray(self):
        '''
        Seperates self.data into two arrays padded with 0s, one for negative values and one for positive.
        '''

        assert self.data is not None
        self.neg = [round(x, 2) if isinstance(x, (float, int)) and x < 0 else 0 for x in self.data]
        self.pos = [round(x, 2) if isinstance(x, (float, int)) and x >= 0 else 0 for x in self.data]

    def getChartData(self):
        '''Abstract method without ABC'''
        assert False, "This method needs to be instantiated by inherited class"
        return []


# These in seperate files
class IntradayProfit_BarchartData(BarchartData):

    def __init__(self, daDate, account):
        self.date = daDate
        self.account = account

    def getChartData(self):
        self.names, self.data = TradeSum.getNamesAndProfits(self.date.strftime("%Y%m%d"))
        self.names = self.names[self.account]
        self.data = self.data[self.account]
        self.getFormatGraphArray()
        self.title = f'Profits in {self.account} account on {self.date.strftime("%B %d, %Y")}'

    def __repr__(self):
        return f'<IntradayProfit_BarchartData({self.date.strftime("%B %d")}, {self.account})>'


class MultiTradeProfit_BarchartData(BarchartData):
    def __init__(self, cud, limit=20, grouptrades=1):
        '''
        Arguments will summarize the user selections
        '''
        super().__init__(cud)

        self.limit = limit

    def getChartData(self):
        ModelBase.connect(new_session=True)
        self.query = ModelBase.session.query(TradeSum).order_by(TradeSum.date.desc(), TradeSum.start.desc())
        self.runFilters()

        self.query = self.query.limit(self.limit)
        self.names = [x.name for x in self.query]

        # Not yet clear the best place to handle this. Its probably not here
        # if grouptrades > 1:
        #     self.names
        self.data = [x.pnl for x in self.query]
        self.getFormatGraphArray()
        self.title = f'Profit from last {self.limit} trades in {self.cud["accounts"]}'
