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
Alphavantage  stuff using their own intraday RESTful  API. Only implemented TIME_SERIES_INTRADAY.
Need to check TIME_SERIES_INTRADAY_EXTENDED. Not sure if it is free. (It may require polygon account?)
Getting a precise historical time may be weird. They give 2 yrs data in 24 slices.
@author: Mike Petersen
@creation_date:2018-12-11
Calls the RESTapi for intraday. There is a limit on the free API of 5 calls per minute
    500 calls per day. But the data is good. The Premium option is rather pricey.
    Note that the 500 limit is really difficult reach with the 5 per minute throttle.
        Free for 5/min  (1 every 12 seconds)
        $20 for 15/min  (1 every 4 seconds)
        $100 for 120/min
        $250 for 600/min
        As of 1/9/19
'''
import datetime as dt
import logging
import time
import requests
import pandas as pd
from structjour.stock.utilities import ManageKeys, movingAverage, setLimitReached, getLimitReached

BASE_URL = 'https://www.alphavantage.co/query?'
EXAMPLES = {
    'api1': 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min&apikey={key}',
    'api2': 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min&outputsize=full&apikey={key}',
    'api3': 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey={key}',
    'api4': 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&outputsize=full&apikey={key}',
    'api5': 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey={key}',
    'web_site': 'https://www.alphavantage.co/documentation/#intraday'}

FUNCTION = {'intraday': 'TIME_SERIES_INTRADAY',
            'daily': 'TIME_SERIES_DAILY',
            'dailyadj': 'TIME_SERIES_DAILY_ADJUSTED',
            'weekly': 'TIME_SERIES_WEEKLY',
            'weeklyadj': 'TIME_SERIES_WEEKLY_ADJUSTED',
            'monthly': 'TIME_SERIES_MONTHLY',
            'monthlyadj': 'TIME_SERIES_MONTHLY_ADJUSTED',
            'quote': 'GLOBAL_QUOTE',
            'search': 'SYMBOL_SEARCH',
            'sma': 'SMA',
            'ema': 'EMA',
            'atr': 'ATR'
            }

PARAMS = {'intraday': ['symbol', 'datatype', 'apikey', 'outputsize', 'interval'],
          'daily': ['symbol', 'datatype', 'apikey', 'outputsize'],
          'dailyadj': ['symbol', 'datatype', 'apikey', 'outputsize'],
          'weekly': ['symbol', 'datatype', 'apikey'],
          'weeklyadj': ['symbol', 'datatype', 'apikey'],
          'monthly': ['symbol', 'datatype', 'apikey'],
          'monthlyadj': ['symbol', 'datatype', 'apikey'],
          'quote': ['symbol', 'datatype', 'apikey'],
          'search': ['keywords', 'datatype', 'apikey'],
          'sma': ['symbol', 'datatype', 'apikey', 'interval', 'time_period', 'series_type'],
          'ema': ['symbol', 'datatype', 'apikey', 'interval', 'time_period', 'series_type'],
          'atr': ['symbol', 'datatype', 'apikey', 'interval', 'time_period']
          }

DATATYPES = ('json', 'csv')       # json is default
OUTPUTSIZE = ('compact', 'full')  # compact is default
INTERVAL = ('1min', '5min', '15min', '30min',
            '60min', 'daily', 'weekly', 'monthly')


def getKey():
    mk = ManageKeys()
    return mk.getKey('av')


def getapis():
    '''some RESTful APIS'''
    mk = ManageKeys()
    key = mk.getKey('av')
    return (EXAMPLES['api1'].format(key=key),
            EXAMPLES['api2'].format(key=key),
            EXAMPLES['api3'].format(key=key),
            EXAMPLES['api4'].format(key=key),
            EXAMPLES['api5'].format(key=key))


def getLimits():
    '''alphavantage limits on usage'''
    print(__doc__)


def ni(i):
    '''
    Retrieve the correct interval param for Alphavantage, a str like '1min'. Limited to minute
    charts up to 60 minute candle.
    :return: (resamp(a,b,c))
        :resamp: a bool indicating the requested interval will need to be resampled
        :a: A str with the av param for the api like '1min'
        :params b: An int -- representing the av interval to be used in the request
        :params c: an int -- the requested interval in the arg
    '''

    # OK something very weird.  i > 1 was caused an exception when running unittest discover and
    # at no other time.  I placed this baby sitter here and the error disappeared. The exception
    # was comparison of str and int. I could not trigger the exception or find a str instance error
    # It never happened for running unittest test_mav
    if isinstance(i, str):
        pass
        # logging.info(':::::::::::::::::\n', i, '::::::::::::::::::\n')
    if i < 1:
        i = 1
    elif i > 120:
        i = 60

    resamp = False
    if i in [1, 5, 15, 30, 60]:
        return resamp, {1: ('1min', 1, 1), 5: ('5min', 5, 5), 15: ('15min', 15, 15), 30: ('30min', 30, 30), 60: ('60min', 60, 60)}[i]
    resamp = True
    if isinstance(i, int):
        ret = '60min', 60, i
        if i < 5:
            ret = ('1min', 1, i)
        elif i < 15:
            ret = ('5min', 5, i)
        elif i < 30:
            ret = ('15min', 15, i)
        elif i < 60:
            ret = ('30min', 30, i)
        return resamp, ret
    logging.warning(
        f"interval={i} is not supported by alphavantage. Setting to 1min candle as if it were requested")
    return False, ('1min', 1, 1)


RETRY = 3


class Retries:
    '''Number of retries when AV returns a 1 minute violation'''
    def __init__(self):
        self.retries = RETRY
        self.setTime = time.time()


R = None


def getmav_intraday(symbol, start=None, end=None, minutes=None, showUrl=False, key=None):
    '''
    Limited to getting minute data intended to chart day trades. Note that start and end are not
    sent to the api request.
    :params symb: The stock ticker
    :params start: A date time string or datetime object to indicate the beginning time.
    :params end: A datetime string or datetime object to indicate the end time.
    :params minutes: An int for the candle time, 5 minute, 15 minute etc. If minutes is not one of
        Alphavantage's accepted times, we will resample.

    :returns: (status, df, maDict) The DataFrame has minute data indexed by time with columns open, high, low
         low, close, volume and indexed by pd timestamp. If not specified, this
         will return a weeks data.
    '''
    if getLimitReached('av'):
        msg = 'AlphaVantage limit was reached'
        logging.info(msg)
        return {'code': 666, 'message': msg}, pd.DataFrame(), None

    logging.info('======= Called alpha 500 calls per day limit, 5/minute =======')
    start = pd.to_datetime(start) if start else None
    end = pd.to_datetime(end) if end else None
    if not minutes:
        minutes = 1

    original_minutes = minutes
    resamp, (minutes, interval, original_minutes) = ni(minutes)

    params = {}
    params['function'] = FUNCTION['intraday']
    if minutes:
        params['interval'] = minutes
    params['symbol'] = symbol
    params['outputsize'] = 'full'
    params['datatype'] = DATATYPES[0]
    # params['apikey'] = APIKEY
    params['apikey'] = key if key else getKey()

    request_url = f"{BASE_URL}"
    response = requests.get(request_url, params=params)
    if showUrl:
        logging.info(response.url)

    if response.status_code != 200:
        raise Exception(
            f"{response.status_code}: {response.content.decode('utf-8')}")
    result = response.json()
    keys = list(result.keys())

    msg = f'{keys[0]}: {result[keys[0]]}'
    metaj = {'code': 200, 'message': msg}
    if len(keys) == 1:
        d = pd.Timestamp.now()
        dd = pd.Timestamp(d.year, d.month, d.day, d.hour, d.minute + 2, d.second)
        setLimitReached('av', dd)

        logging.warning(msg)
        return metaj, pd.DataFrame(), None

    dataJson = result[keys[1]]

    df = pd.DataFrame(dataJson).T

    df.index = pd.to_datetime(df.index)

    if df.index[0] > df.index[-1]:
        df.sort_index(inplace=True)

    if end:
        if end < df.index[0]:
            msg = 'WARNING: You have requested data that is unavailable:'
            msg = msg + f'\nYour end date ({end}) is before the earliest first date ({df.index[0]}).'
            logging.warning(msg)
            metaj['code'] = 666
            metaj['message'] = msg

            return metaj, pd.DataFrame(), None

    df.rename(columns={'1. open': 'open',
                       '2. high': 'high',
                       '3. low': 'low',
                       '4. close': 'close',
                       '5. volume': 'volume'}, inplace=True)

    df.open = pd.to_numeric(df.open)
    df.high = pd.to_numeric(df.high)
    df.low = pd.to_numeric(df.low)
    df.close = pd.to_numeric(df.close)
    df.volume = pd.to_numeric(df.volume)

    # Alphavantage indexes the candle ends as a time index. So the beginninng of the daay is 9:31
    # I think that makes them off by one when processing forward. IB, and others, index candle
    # beginnings. To make the APIs harmonious, we will transalte the index time down by
    # one interval. I think the translation will always be the interval sent to mav. So
    # '1min' will translate down 1 minute etc. We saved the translation as a return
    # from ni().
    # for i, row in df.iterrows():
    delt = pd.Timedelta(minutes=interval)
    df.index = df.index - delt
    #     df.index[i] = df.index[i] - delt

    if resamp:
        srate = f'{original_minutes}T'
        df_ohlc = df[['open']].resample(srate).first()
        df_ohlc['high'] = df[['high']].resample(srate).max()
        df_ohlc['low'] = df[['low']].resample(srate).min()
        df_ohlc['close'] = df[['close']].resample(srate).last()
        df_ohlc['volume'] = df[['volume']].resample(srate).sum()
        df = df_ohlc.copy()

    maDict = movingAverage(df.close, df, start)

    # Trim the data to the requested time frame. If we slice it all off set status message and return
    if start:
        # Remove preemarket hours from the start variable
        starttime = start.time()
        opening = dt.time(9, 30)
        if opening > starttime:
            start = pd.Timestamp(start.year, start.month, start.day, 9, 30)
        if start > df.index[0]:
            df = df[df.index >= start]
            for ma in maDict:
                maDict[ma] = maDict[ma].loc[maDict[ma].index >= start]
            if len(df) == 0:
                msg = f"\nWARNING: you have sliced off all the data with the end date {start}"
                logging.warning(msg)
                metaj['code'] = 666
                metaj['message'] = msg
                return metaj, pd.DataFrame(), maDict

    if end:
        if end < df.index[-1]:
            df = df[df.index <= end]
            for ma in maDict:
                maDict[ma] = maDict[ma].loc[maDict[ma].index <= end]
            if len(df) < 1:
                msg = f"\nWARNING: you have sliced off all the data with the end date {end}"
                logging.warning(msg)
                metaj['code'] = 666
                metaj['message'] = msg
                return metaj, pd.DataFrame(), maDict
    # If we don't have a full ma, delete -- Later:, implement a 'delayed start' ma in graphstuff
    keys = list(maDict.keys())
    for key in keys:
        if len(df) != len(maDict[key]):
            del maDict[key]

    return metaj, df, maDict


def notmain():
    for ex in getapis():
        print(ex)


if __name__ == '__main__':
    theDate = pd.Timestamp.today().date()
    metaj, df, maDict = getmav_intraday('ROKU', minutes=5, start=theDate)
    if not df.empty:
        print(df.tail(2))
    else:
        print(metaj)
    # text1 = '''Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day.
    # Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency.'''
