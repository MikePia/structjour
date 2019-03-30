'''
Created on Sep 2, 2018

@author: Mike Petersen
'''
import pandas as pd

from journal.definetrades import ReqCol
from journal.dfutil import DataFrameUtil
from journal.statement import Statement_IBActivity, Statement_DAS
from journalfiles import JournalFiles

# pylint: disable = C0103


def askUser(shares, question):
    '''
    Ask the user a question regarding how many shares they are holding.
    :params:shares: The number of shares outof balance. Its inserted into the question and
                    used as a default response.
    :return: The number response for the number of shares.
    '''
    while True:
        try:
            response = input(question)
            if not response:
                response = shares
            else:
                response = int(response)
        except ValueError as ex:
            print(ex)
            print()
            print("please enter a number")
            response = 0
            continue

        return response


class InputDataFrame(object):
    '''Manipulation of the original import of the trade transactions. Abstract the label schema
    to a dictionary. Import from all soures is equalized here.'''

    def __init__(self, source="DAS"):
        '''Set the required columns in the import file.'''
        if source != 'DAS':
            print("Only DAS is currently supported")
            raise ValueError

    def processInputFile(self, trades, theDate=None, jf=None):
        '''
        Run the methods for this object
        '''
        reqCol = ReqCol()

        DataFrameUtil.checkRequiredInputFields(trades, reqCol.columns)
        trades = self.zeroPadTimeStr(trades)
        trades = trades.sort_values([reqCol.acct, reqCol.ticker, reqCol.date, reqCol.time])
        trades = self.mkShortsNegative(trades)
        swingTrade = self.getOvernightTrades(trades)
        swingTrade = self.figureOvernightTransactions(trades, jf)
        trades = self.insertOvernightRow(trades, swingTrade)
        trades = self.addDateField(trades, theDate)
        return trades

    def addDateField(self, trades, theDate):
        '''
        Add the date column if it does not already exist and fill it with the date/time from the
        given date or today and the time column
        :params trades:
        '''
        c = ReqCol()
        if not 'Date' in trades.columns:
            if theDate:
                theDate = pd.Timestamp(theDate)
            else:
                theDate = pd.Timestamp.today()

            trades['Date'] = theDate.strftime("%Y-%m-%d ") + trades['Time']
        else:
            # We need to make up a date for Hold rows. Before holds were assigned an early AM time
            # and after holds a late PM time. The times were assigned for sorting. Before holds
            # will be given a date before a second trade date identified because they have been
            # sorted by [account, ticker, time]. Likewise an an after hold will be given the next
            # day after the previous trade. There should not be any single hold entries without an
            # actual trade from this input file but we will assert that fact in order to find
            # unaccountable weirdnesses.

            for i, row in trades.iterrows():
                if row[c.side].lower().startswith('hold'):

                    # Currently c.time a time string with no date. Compare early and late times
                    datime = row[c.time]
                    d = pd.Timestamp(datime)

                    early = pd.Timestamp(d.year, d.month, d.day, 3, 0, 0)
                    late = pd.Timestamp(d.year, d.month, d.day, 10, 59, 0)
                    delt = pd.Timedelta(days=1)
                    if d < early:
                        assert row[c.side] in ['HOLD+B', 'HOLD-B']
                        assert len(trades) > i + 1
                        assert trades.at[i,
                                         c.ticker] == trades.at[i+1, c.ticker]

                        # Create the made up date- the day before the first tx from this input for
                        # this trade.
                        tradeday = trades.at[i+1, c.date]
                        tradeday = pd.Timestamp(tradeday)
                        holdday = tradeday-delt
                        holdtime = pd.Timestamp(
                            holdday.year, holdday.month, holdday.day,  d.hour, d.minute, d.second)
                        trades.at[i, 'Date'] = holdtime

                    elif d > late:
                        assert row[c.side] in ['HOLD+', 'HOLD-']
                        assert i > 0
                        assert trades.at[i,
                                         c.ticker] == trades.at[i-1, c.ticker]

                        tradeday = trades.at[i-1, c.date]
                        tradeday = pd.Timestamp(tradeday)

                        holdtime = tradeday + delt
                        holdtime = pd.Timestamp(
                            holdtime.year, holdtime.month, holdtime.day, d.hour, d.minute, d.second)
                        # holdtime = holdtime.strftime('%Y-%m-%d %H:%M:%S')
                        trades.at[i, c.date] = holdtime

        return trades

    def zeroPadTimeStr(self, dframe):
        '''
        Guarantee that the time format xx:xx:xx
        '''

        rc = ReqCol()
        #         time = rc.time
        for i, row in dframe.iterrows():
            tm = row[rc.time]
            tms = tm.split(":")
            if int(len(tms[0]) < 2):
                if not tms[0].startswith("0"):
                    tm = "0" + tm
                    dframe.at[i, rc.time] = tm
        return dframe

    # Todo.  Doctor an input csv file to include fractional numer of shares for testing.
    #        Make it more modular by checking for 'HOLD'.
    #        It might be useful in a windowed version with menus to do things seperately.
    #        Currently relying on values of side as 'B' , 'S', 'SS'
    def mkShortsNegative(self, dframe):
        ''' Fix the shares sold to be negative values.
        @testpu'''

        rc = ReqCol()

        for i, row in dframe.iterrows():
            if row[rc.side] != 'B' and row[rc.shares] > 0:
                dframe.at[i, rc.shares] = ((dframe.at[i, rc.shares]) * -1)
        return dframe

    def getListTickerDF(self, dframe):
        '''
        Returns a python list of all tickers/account traded in todays input file.
        :params dframe: The DataFrame with the days trades that includes the column tickCol
                        (Symb by default and in DAS).
        :return: The list of tickers in the days trades represented by the DataFrame
        '''
        rc = ReqCol()

        listOfTickers = list()
        for symb in dframe[rc.ticker].unique():
            for acct in dframe[rc.acct][dframe[rc.ticker] == symb].unique():

                # ldf = dframe[dframe[rc.ticker]==symb][dframe[rc.acct]==acct]
                ldf = dframe[dframe[rc.ticker] == symb]
                ldf = ldf[ldf[rc.acct] == acct]

                listOfTickers.append(ldf)

        # This code is too interdependent. gtoOvernightTrade, figureOvernightTrades, askUser
        # and insertOvernightRow combined with the data
        return listOfTickers

    def getOvernightTrades(self, dframe):
        '''
        Create the overnightTrade (aka swingTrade data structure) from the list of overnight holds.
                Overnight holds are inferred from an unbalanced number of shares. Until we ask the
                user, we won't know whether before or after or both
        :params dframe: The Original unaltered input file with the days trades that includes the
                columns rc.ticker and rc.share
        :return: overnightTrades, a list of dict The dict has the keys (ticker, shares, before,
                after, acct) Elsewhere in the program the variable is referred to as swingTrade
                or swtrade. We do not have the info whether there was shares held before open or
                shares are held after close or both.
        '''
        rc = ReqCol()

        ldf_tick = self.getListTickerDF(dframe)
        overnightTrade = list()
        i = 0
        for ticker in ldf_tick:
            if ticker[rc.shares].sum() != 0:
                overnightTrade.append(dict())
                overnightTrade[i]['ticker'] = ticker[rc.ticker].unique()[0]
                overnightTrade[i]['shares'] = ticker[rc.shares].sum()
                overnightTrade[i]['before'] = 0
                overnightTrade[i]['after'] = 0
                overnightTrade[i]['acct'] = ticker[rc.acct].unique()[0]
                i = i + 1
        return overnightTrade

    def getOvernightTrades_DAS(self, swingTrade, pos_df):
        '''
        Get overnight trades sorted from a statement or DAS positions export-now a DataFrame
        :params swingTrade: The data structure holding information on unbalanced shares for tickers
        :params pos_df: The DataFrame with the positions information.
        '''
        # for i in range(len(swingTrade)):
        for t in swingTrade:
            if t['ticker'] in list(pos_df.Symb) and (t['acct'] == pos_df[pos_df.Symb == t['ticker']].Account.unique()[0]):
                # Some shares were held after close
                t['after'] = t['shares']

                t['before'] = t['shares'] - int(pos_df[pos_df.Symb == t['ticker']].Shares.unique()[0])
                t['shares'] = 0
            else:
                t['before'] = t['shares']
                t['shares'] = 0
        return swingTrade

    def getPositions(self, jf):
        '''
        Open the positions csv. It is either a DAS export or a file created to the same specs.
        Currently, this file is only used when using a DAS export from the trades window and is
        only necessary if any trades in the input file have balance trades before or after.
        :params jf: The JournalFiles object. It may be None and the variable for the location at
                    jf.inpathfile2 may also be None.
        :return: A DataFrame. If no results were retrieved, return an empty DataFrame.
        :TODO: getPositions should be a virtual method--not sure how to implement it best
        This aint java. For now just kludge solidly.
        '''
        if jf and jf.inputType == JournalFiles.InputType['das'] and jf.inpathfile2:
            st = Statement_DAS(jf)
            df = st.getPositions()
            return df
        elif jf and jf.inputType == JournalFiles.InputType['ib']:
            st = Statement_IBActivity(jf)
            df = st.getPositions()
            return df
        return pd.DataFrame()

    def figureOvernightTransactions(self, dframe, jf):
        '''
        Determine how of the unbalanced shares were held:  before, after or both. We have to ask.
        FIX THIS (Won't be so bad in the Windowed version) (Could get it from exporting position
        window in addition Or maybe from using IBs input files instead.)
        '''

        # rc = ReqCol()

        swingTrade = self.getOvernightTrades(dframe)
        pos = self.getPositions(jf)
        reqcol = set(['Symb', 'Account', 'Shares'])
        if not pos.empty:
            if len(set(reqcol) & set(pos.columns)) == len(set(reqcol)):
                return self.getOvernightTrades_DAS(swingTrade, pos)
            else:
                msg = '\nthe positions file lacks the correct headings. Required headings are:\n'
                msg += f'{reqcol}\n'
                raise ValueError(msg)
        for i in range(len(swingTrade)):
            tryAgain = True
            while tryAgain:

                question = '''There is an unbalanced amount of shares of {0} in the amount of {1}
                    in the account {2}. How many shares of {0} are you holding now? 
                    (Enter for {1}) '''.format(swingTrade[i]['ticker'],
                                               swingTrade[i]['shares'],
                                               swingTrade[i]['acct'])

                swingTrade[i]['after'] = askUser(
                    swingTrade[i]['shares'], question)
                swingTrade[i]['shares'] = swingTrade[i]['shares'] - \
                    swingTrade[i]['after']

                if swingTrade[i]['shares'] != 0:

                    question = '''There is now a prior unbalanced amount of shares of {0} amount
                    of {1} in the account {2}. How many shares of {0} were you holding before? 
                    (Enter for {1}) '''.format(swingTrade[i]['ticker'],
                                               -swingTrade[i]['shares'],
                                               swingTrade[i]['acct'])

                    swingTrade[i]['before'] = askUser(
                        swingTrade[i]['shares'], question)
                    swingTrade[i]['shares'] = swingTrade[i]['shares'] - \
                        swingTrade[i]['before']

                if swingTrade[i]['shares'] == 0:
                    # print("That works.")
                    tryAgain = False
                else:
                    print()
                    print("There are {1} unaccounted for shares in {0}".format(
                        swingTrade[i]['ticker'], swingTrade[i]['shares']))
                    print()
                    print("That does not add up. Starting over ...")
                    print()
                    print("Prior to reset version ", i, swingTrade)
                    swingTrade[i] = self.getOvernightTrades(dframe)[i]
                    print("reset version ", i, swingTrade)
        # print(swingTrade)
        return swingTrade

    def insertOvernightRow(self, dframe, swTrade):
        '''
        Insert non-transaction rows that show overnight transactions. Set Side to one of:
        HOLD+, HOLD-, HOLD+B, HOLD_B
        :params dframe: The trades dataframe.
        :params swTrade: A data structure holding information about tickers with unbalanced shares.
        '''

        rc = ReqCol()

        newdf = DataFrameUtil.createDf(dframe, 0)

        for ldf in self.getListTickerDF(dframe):
            # print(ldf[rc.ticker].unique()[0], ldf[rc.acct].unique()[0])
            for trade in swTrade:
                if (trade['ticker'] == ldf[rc.ticker].unique()[0] and (
                        trade['acct'] == ldf[rc.acct].unique()[0])):
                    # msg = "Got {0} with the balance {1}, before {2} and after {3} in {4}"
                    # print(msg.format(trade['ticker'], trade['shares'], trade['before'],
                    #       trade['after'], trade['acct']))

                    # insert a non transaction HOLD row before transactions of the same ticker

                    if trade['before'] != 0:
                        newldf = DataFrameUtil.createDf(dframe, 1)
                        for j, dummy in newldf.iterrows():

                            if j == len(newldf) - 1:
                                newldf.at[j, rc.time] = '00:00:01'
                                newldf.at[j, rc.ticker] = trade['ticker']
                                if trade['before'] > 0:
                                    newldf.at[j, rc.side] = "HOLD-B"
                                else:
                                    newldf.at[j, rc.side] = "HOLD+B"
                                newldf.at[j, rc.price] = float(0.0)
                                newldf.at[j, rc.shares] = -trade['before']
                                # ZeroSubstance'
                                newldf.at[j, rc.acct] = trade['acct']
                                newldf.at[j, rc.PL] = 0

                                ldf = newldf.append(ldf, ignore_index=True)
                            break

                    # Insert a non-transaction HOLD row after transactions from the same ticker
                    # Reusing ldf for something different here...bad form ... maybe ...
                    # adding columns then appending and starting over
                    if trade['after'] != 0:
                        # print("Are we good?")
                        ldf = DataFrameUtil.addRows(ldf, 1)

                        for j, dummy in ldf.iterrows():

                            if j == len(ldf) - 1:
                                ldf.at[j, rc.time] = '23:59:59'
                                ldf.at[j, rc.ticker] = trade['ticker']

                                if trade['after'] > 0:
                                    ldf.at[j, rc.side] = "HOLD+"
                                else:
                                    ldf.at[j, rc.side] = "HOLD-"
                                ldf.at[j, rc.price] = float(0.0)

                                # -trade makes the share balance work in excel
                                # for shares held after close
                                ldf.at[j, rc.shares] = 0  # -trade['after']
                                # 'ZeroSubstance'
                                ldf.at[j, rc.acct] = trade['acct']
                                ldf.at[j, rc.PL] = 0

            newdf = newdf.append(ldf, ignore_index=True, sort=False)
        return newdf
