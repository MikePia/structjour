import pandas as pd
from structjour.models.trademodels import TradeSum
from structjour.models.meta import ModelBase
from structjour.stock.utilities import qtime2pd
from structjour.utilities.util import advanceMonth

from sqlalchemy import or_, and_


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
                      inTimeGroups: An integer:
                            < 1 will be inactive
                            1~29 will be interpreted as days
                            >29 will be changed to a number of months.
                            > 360 raise ValueError
                      strategies: list<str>
                      dates: tuple<pd.Timestamp> (start, end)
                      accounts: str can be 'All Accounts' or an account alias (an entry in TradeSums.account)

    '''
    def __init__(self, cud, maxbars=99):
        self.cud = cud
        self.query = None

        # Initialze the chart with the max num of candles
        self.names = pd.date_range(start='1/1/2020', end='7/15/2021')
        self.maxbars = maxbars
        self.names = self.names[:self.maxbars]
        self.data = [-(x - (self.maxbars // 2)) for x in list(range(self.maxbars))]
        self.title = 'Initialaze chart'
        self.chartInitialized = False
        self.getFormatGraphArray()

    def runFilters(self):
        if self.query is None:
            return
        self.filter_by_accounts()
        self.filter_by_dates()
        self.filter_by_side()
        self.filter_by_strategies()
        self.filter_by_symbols()
        self.filter_by_tags()

    def getChartUserData(self):
        raise ValueError('This method, ChartDataBase.getChartUserData, needs to be overridden by an inherited class')

    def filter_by_symbols(self):
        key = 'symbols'
        if key in self.cud and self.cud[key] and self.query is not None:
            likes = [TradeSum.name.like(x + "%") for x in self.cud[key]]
            self.query = self.query.filter(or_(*likes))
        else:
            print('self.cud is missing key', key)

    def filter_by_side(self):
        key = 'side'
        if key in self.cud and self.query is not None and self.cud[key] != "Both":
            self.query = self.filter(TradeSum.name.like(f"%{self.cud['side']}%"))
        else:
            print('self.cud is missing key', key)

    def filter_by_tags(self):
        key = 'tags'
        if key in self.cud and self.cud[key] and self.query is not None:
            anytags = [TradeSum.tags.any(name=x) for x in self.cud[key]]
            self.query = self.query.filter(or_(*anytags))
        else:
            print('self.cud is missing key', key)

    def filter_by_strategies(self):
        # strategies
        key = 'strategies'
        if key in self.cud and self.cud[key] and self.query is not None:
            self.query = self.query.filter(TradeSum.strategy.in_(self.cud[key]))
        else:
            print('self.cud is missing key', key)

    def filter_by_dates(self):
        key = 'dates'
        if key in self.cud and self.query is not None and self.cud['dates'][0] and self.cud['dates'][1]:
            start, end = qtime2pd(self.cud[key][0]), qtime2pd(self.cud[key][1])
            now = pd.Timestamp.now().date()
            if now >= start:
                self.query = self.query.filter(and_(TradeSum.date >= start.strftime("%Y%m%d"), TradeSum.date < end.strftime("%Y%m%d")))
        else:
            print('self.cud is missing key', key)

    def filter_by_accounts(self):
        '''Adds a filter to a query on the TradeSum table'''
        # accounts
        key = 'accounts'
        if key in self.cud and not str(self.cud[key]) in ['None', '', 'All Accounts'] and self.query is not None:
            self.query = self.query.filter_by(account=self.cud[key])
            print(self.cud[key])
        else:
            print('self.cud or no query is missing key', key)

    # Here group into sets of n.
    def getProfitInNumGroups(self, trades, num):
        '''
        Takes a query realized result, groups the trades and returns
        summarized pnl with data
        '''

        gnum = []
        g = []
        endingdates = []

        for i, t in enumerate(trades):
            # remove bad data-- byte strings or Null entries
            if not isinstance(t.pnl, (int, float)):
                t.pnl = 0
            g.append(t)
            if i and not i % num or i == len(trades) - 1:
                gnum.append(g)
                endingdates.append(pd.Timestamp(f'{trades[i].date} {trades[i].start}'))
                g = []
        pnls = [sum([x.pnl for x in gnum[i]]) for i in range(len(gnum))]
        endingdates.reverse(),
        pnls.reverse()
        return pnls, endingdates

    def view_inNumSets(self):
        '''
        Store the value for inNumSets. The Views are run after the query has been realized
        '''
        key = 'inNumSets'
        if key in self.cud and self.query is not None:
            trades = self.query.all()
            pnls, dates = self.getProfitInNumGroups(trades, self.cud[key])
            self.data = pnls
            self.names = dates

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

    def groupByTime(self, trades, numdays=None, begindate=None, enddate=None):
        '''
        Group the trades into arrays grouped by number of days or number of months. And then create
            pnls, an array or the summarized pnl for group. and endingdates, an array of a represetative
            date for each array based on the first date in the group
        :params trades: A sqlalchemy query result (.all() has been called) with a date column.
        :params numdays: Acceptible values: < 1 is inactive:
                                            1~29 days
                                            30~360 will be divided by 30 and advance as months
                                            max nummonths is 12
        result in a AssertionError
        :return: A Tuple of arrays: (pnls, endingdates )
        '''
        nummonths = -1
        if numdays < 1:
            return
        elif numdays > 29:
            nummonths = numdays // 30
            numdays = -1
            nummonths = min(nummonths, 12)

        bytime = []
        currdate = pd.Timestamp(trades[0].date)
        if begindate:
            currdate = pd.Timestamp(begindate)
        if enddate:
            enddate = pd.Timestamp(enddate)
            if currdate > enddate:
                return []
        else:
            enddate = pd.Timestamp(trades[-1].date)

        if numdays > 0:
            delt = pd.Timedelta(days=numdays)
            danext = currdate + delt

        else:
            danext = advanceMonth(currdate, nummonths)
        if danext > enddate:
            danext = enddate

        tday = []
        for t in trades:
            # remove bad data-- byte strings or Null entries
            if not isinstance(t.pnl, (int, float)):
                t.pnl = 0
            currdate = pd.Timestamp(t.date)
            if currdate > enddate:
                if tday:
                    bytime.append(tday)
                break

            if currdate >= danext:
                if numdays > 0:
                    danext = currdate + delt
                else:
                    danext = advanceMonth(currdate, nummonths)

                if tday:
                    bytime.append(tday)
                tday = []
            tday.append(t)
        # End part one. TODO: Store the bytime array to enable drill down when user clicks on a bar
        # Part two extracts a summary of pnl and a date from each array
        pnls = [sum([x.pnl for x in bytime[i]]) for i in range(len(bytime))]
        openingdates = [pd.Timestamp(f'{x[0].date}') for x in bytime]

        # endingdates.append(pd.Timestamp(f'{trades[i].date} {trades[i].start}'))
        
        return pnls, openingdates


class BarchartData(ChartDataBase):
    '''
    Inheritors of this class must:
        1) define the class variables data, names, date
        2) define getChartUserData and save the result to self.query: 
        TODO: Define the obligations of this method here
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

    def getChartUserData(self):
        '''Abstract method without ABC'''
        raise ValueError("This method, BarChartData.getChartUserData, needs to be instantiated by an inherited class")


# These in seperate files
class IntradayProfit_BarchartData(BarchartData):

    def __init__(self, daDate, account):
        self.date = daDate
        self.account = account

    def getChartUserData(self):
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

    def getChartUserData(self):
        if self.chartInitialized is False:
            self.chartInitialized = True
            return
        ModelBase.connect(new_session=True)
        self.query = ModelBase.session.query(TradeSum).order_by(TradeSum.date.asc(), TradeSum.start.asc())
        self.runFilters()
        # self.query = self.query.all()

        # self.query = self.query.limit(self.limit)
        accounts = self.cud['accounts'] if self.cud['accounts'] else 'All'
        if self.cud['inNumSets'] > 0:
            pnls, dates = self.getProfitInNumGroups(self.query.all(), self.cud['inNumSets'])
            self.title = f'Trades in groups of {self.cud["inNumSets"]} trades in {accounts} accounts'
        elif self.cud['inTimeGroups'] is not None:
            pnls, dates = self.groupByTime(self.query.all(), self.cud['inTimeGroups'])
            self.title = f'Trades: {self.cud["titleBit"]} in {accounts} accounts'

        # self.names = [pd.Timestamp(x.date) for x in self.query]
        self.names = dates

        # Not yet clear the best place to handle this. Its probably not here
        # if grouptrades > 1:
        self.data = pnls
        # self.data = [x.pnl for x in self.query]
        self.getFormatGraphArray()
