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
Some barchart calls beginning (and ending now) with getHistory. Note that the docs show SOAP code
to run this in python but as of 12/29/18 the suds module (suds not suds-py3) does not work on my
system. I am goingto implement the straight RESTful free API using request. All we need is
getHistory and to implement the APIChooser interface for it.

@author: Mike Petersen
@creation_data: 12/19/18
'''
import datetime as dt
import logging
import requests
import pandas as pd
from structjour.stock.utilities import ManageKeys, getLastWorkDay, movingAverage, setLimitReached, getLimitReached


def getApiKey():
    '''Returns the key for the barchart API
    '''
    mk = ManageKeys()
    return mk.getKey('bc')


def getLimits():
    '''Some useful info regarding barchart maximum usage.'''
    return '''Every user is able to make 400 getQuote queries and 150 getHistory queries per day.
              Using getQuote, One coud track a single stock for open hours updating once a minute.
              Or one could track a single stock for one hour updating every 9 seconds.
              https://www.barchart.com/ondemand/free-market-data-api/faq.'''


BASE_URL = f'https://marketdata.websol.barchart.com/getHistory.json?'


def getFaq():
    '''Intersting info'''
    faq = '''
        https://www.barchart.com/ondemand/free-market-data-api/faq
        https://www.barchart.com/ondemand/api gives api for several dozen calls.
        The free api is limited to getQuote and getHistory.
            https://www.barchart.com/ondemand/free-market-data-api
        Exchanges iclude AMEX, NYSE, NASDAQ.
        Within the last couple of years, the free API shrunk without warning.
        Every user is able to make 400 getQuote queries and 150 getHistory queries per day.
        When your daily API account query limit is reached, the data will be disabled then
            reset until the next day.
        Pricing info for other apis requires you contact a sales person (shudder).
        '''
    return faq


APIS = {'history': 'getHistory.json?',
        'closeprice': 'getClosePrice.json?'}


PARAMS = {'getHistory': ['apikey', 'symbol', 'type',
                         'startDate', 'maxRecords', 'interval', 'order', 'sessionFilter',
                         'splits', 'dividends', 'volume', 'nearby', 'jerq'],
          'getQuote': ['symbols', 'fields', 'only']
          }


TYPE = ['minutes', 'nearbyMinutes', 'formTMinutes',
        'daily', 'dailyNearest', 'dailyContinue',
        'weekly', 'weeklyNearest', 'weeklyContinue',
        'monthly', 'monthlyNearest', 'monthlyContinue',
        'quarterly', 'quarterlyNearest', 'quarterlyContinue',
        'yearly', 'yearlyNearest', 'yearlyContinue']
ORDER = ['asc', 'desc']
VOLUME = ['total', 'sum', 'contract', 'sumcontract', 'sumtotal']


def setParams(symbol, minutes, startDay, key=None):
    '''Internal utility method'''
    params = {}
    params['apikey'] = key if key else getApiKey()
    params['symbol'] = symbol
    params['type'] = 'minutes'
    params['interval'] = minutes
    params['startDate'] = startDay
    params['order'] = 'asc'
    # params['maxRecords'] = 5
    params['sessionFilter'] = 'EFK'
    params['volume'] = 'sum'
    params['nearby'] = 1
    params['jerq'] = 'true'
    return params


# Not getting the current date-- maybe after the market closes?
def getbc_intraday(symbol, start=None, end=None, minutes=5, showUrl=False, key=None):
    '''
    Note that getHistory will return previous day's prices until 15 minutes after the market
        closes. We will generate a warning if our start or end date differ from the date of the
        response. Given todays date at 14:00, it will retrive the previous business days stuff.
        Given not start parameter, we will return data for the last weekday. Today or earlier.
        We will return everything we between start and end. It may be incomplete.
        Its now limiting yesterdays data. At 3:00, the latest I get is yesterday
        up to 12 noon.
    Retrieve candle data measured in minutes as given in the minutes parameter
    :params start: A datetime object or time string to indicate the begin time for the data. By
        default, start will be set to the most recent weekday at market open.
    :params end: A datetime object or time string to indicate the end time for the data
    :params minutes: An int for the candle time, 5 minute, 15 minute etc
    :return (status, data): A tuple of (status as dictionary, data as a DataFrame ) This status is
        seperate from request status_code.
    :raise: ValueError if response.status_code is not 200.
    '''
    if getLimitReached('bc'):
        msg = 'BarChart limit was reached'
        logging.info(msg)
        return {'code': 666, 'message': msg}, pd.DataFrame(), None

    logging.info('======= Called Barchart -- 150 call limit, data available after market close =======')
    if not end:
        tdy = dt.datetime.today()
        end = dt.datetime(tdy.year, tdy.month, tdy.day, 17, 0)
    # end

    if not start:
        tdy = dt.datetime.today()
        start = dt.datetime(tdy.year, tdy.month, tdy.day, 6, 0)
        start = getLastWorkDay(start)
    end = pd.to_datetime(end)
    start = pd.to_datetime(start)
    # startDay = start.strftime("%Y%m%d")

    # Get the maximum data in order to set the 200 MA on a 60 minute chart
    fullstart = pd.Timestamp.today()
    fullstart = fullstart - pd.Timedelta(days=40)
    fullstart = fullstart.strftime("%Y%m%d")

    params = setParams(symbol, minutes, fullstart, key=key)

    response = requests.get(BASE_URL, params=params)
    if showUrl:
        logging.info(response.url)

    if response.status_code != 200:
        raise Exception(
            f"{response.status_code}: {response.content.decode('utf-8')}")
    meta = {'code': 200}
    if (response.text and isinstance(response.text, str) and response.text.startswith('You have reached')):
        d = pd.Timestamp.now()
        dd = pd.Timestamp(d.year, d.month, d.day + 1, 3, 0, 0)
        setLimitReached('bc', dd)

        logging.warning(f'API max queries: {response.text}')
        meta['message'] = response.text
        return meta, pd.DataFrame(), None

    result = response.json()
    if not result['results']:
        logging.warning('''Failed to retrieve any data. Barchart sends the following greeting: {result['status']}''')
        return result['status'], pd.DataFrame(), None

    meta['message'] = result['status']['message']
    df = pd.DataFrame(result['results'])

    for i, row in df.iterrows():
        d = pd.Timestamp(row['timestamp'])
        newd = pd.Timestamp(d.year, d.month, d.day, d.hour, d.minute, d.second)
        df.at[i, 'timestamp'] = newd

    df.set_index(df.timestamp, inplace=True)
    df.index.rename('date', inplace=True)
    maDict = movingAverage(df.close, df, start)

    if start > df.index[0]:
        rstart = df.index[0]
        rend = df.index[-1]
        df = df.loc[df.index >= start]
        for ma in maDict:
            maDict[ma] = maDict[ma].loc[maDict[ma].index >= start]

        lendf = len(df)
        if lendf == 0:
            msg = '\nWARNING: all data has been removed.'
            msg = msg + f'\nThe Requested start was({start}).'
            msg = msg + f'\nBarchart returned data beginning {rstart} and ending {rend}'
            msg += '''If you are seeking a chart from today, its possible Barchart has not made'''
            msg += 'the data available yet. (Should be available by 4:45PM but they are occasionally late)'
            msg += 'You can copy the image yourself, wait, or try a different API. Open File->StockAPI'
            logging.warning(msg)
            meta['code2'] = 199
            meta['message'] = meta['message'] + msg
            return meta, df, maDict

    if end < df.index[-1]:
        df = df.loc[df.index <= end]
        for ma in maDict:
            maDict[ma] = maDict[ma].loc[maDict[ma].index <= end]

        # If we just sliced off all our data. Set warning message
        lendf = len(df)
        if lendf == 0:
            msg = '\nWARNING: all data has been removed.'
            msg = msg + f'\nThe Requested end was({end}).'
            meta['code2'] = 199
            meta['message'] = meta['message'] + msg
            logging.warning(f'{meta}')
            return meta, df, maDict

    deleteMe = list()
    for key in maDict:
        if key == 'vwap':
            continue
        if len(df) != len(maDict[key]):
            deleteMe.append(key)
    for key in deleteMe:
        del maDict[key]

    # Note we are dropping columns  ['symbol', 'timestamp', 'tradingDay[] in favor of ohlcv
    df = df[['open', 'high', 'low', 'close', 'volume']].copy(deep=True)
    return meta, df, maDict


def main():
    '''Local runs for debugging'''
    symbol = 'SQ'
    showUrl = True
    end = pd.Timestamp.today() - pd.Timedelta(days=1)
    start = end - pd.Timedelta(days=7)

    minutes = 1
    meta, d, daMas = getbc_intraday(symbol, start=start, end=end, minutes=minutes, showUrl=showUrl)
    print(len(d))
    print(meta)


def notmain():

    print(getApiKey())


if __name__ == '__main__':
    main()
    # notmain()
