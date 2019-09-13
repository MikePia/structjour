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
@author: Mike Petersen
@creation_date:2018-12-11
Calls the RESTapi for intraday. There is a limit on the free API of 5 calls per minute
    500 calls per day. But the data is good. The Premium option is rather pricey.
        Free for 5/min  1 every 12 seconds.  Write a API chooser, maybe cache the data
        $20 for 15/min  1 every 4 seconds

        $100 for 120/min
        $250 for 600/min
        As of 1/9/19
'''
# pylint: disable = C0103
# pylint: disable = C0301

import datetime as dt
import time
import requests
import pandas as pd
from structjour.stock.picklekey import getKey as getPickledKey
from structjour.stock.utilities import ManageKeys, movingAverage
# import pickle

BASE_URL = 'https://www.alphavantage.co/query?'
EXAMPLES = {
    'api1': 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min&apikey=VPQRQR8VUQ8PFX5B',
    'api2': 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min&outputsize=full&apikey=VPQRQR8VUQ8PFX5B',
    'api3': 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=VPQRQR8VUQ8PFX5B',
    'api4': 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&outputsize=full&apikey=VPQRQR8VUQ8PFX5B',
    'api5': 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=VPQRQR8VUQ8PFX5B',
'web_site': 'https://www.alphavantage.co/documentation/#intraday'
    }
FUNCTION = {'intraday':  'TIME_SERIES_INTRADAY',
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

PARAMS = {'intraday':  ['symbol', 'datatype', 'apikey', 'outputsize', 'interval'],
          'daily':  ['symbol', 'datatype', 'apikey', 'outputsize'],
          'dailyadj':  ['symbol', 'datatype', 'apikey', 'outputsize'],
          'weekly':  ['symbol', 'datatype', 'apikey'],
          'weeklyadj':  ['symbol', 'datatype', 'apikey'],
          'monthly':  ['symbol', 'datatype', 'apikey'],
          'monthlyadj':  ['symbol', 'datatype', 'apikey'],
          'quote':  ['symbol', 'datatype', 'apikey'],
          'search':  ['keywords', 'datatype', 'apikey'],
          'sma':  ['symbol', 'datatype', 'apikey', 'interval', 'time_period', 'series_type'],
          'ema':  ['symbol', 'datatype', 'apikey', 'interval', 'time_period', 'series_type'],
          'atr':  ['symbol', 'datatype', 'apikey', 'interval', 'time_period']
          }

DATATYPES = ('json', 'csv')       # json is default
OUTPUTSIZE = ('compact', 'full')  # compact is default
INTERVAL = ('1min', '5min', '15min', '30min',
            '60min', 'daily', 'weekly', 'monthly')

# Deprecated
APIKEY = getPickledKey('alphavantage')['key']

def getKey():
    mk=ManageKeys()
    return mk.getKey('av')


def getkeyPickled():
    '''My Personal key'''
    k = getPickledKey('alphavantage')
    return k

def getapis():
    '''some RESTful APIS'''
    return[EXAMPLES['api1'], EXAMPLES['api2'], EXAMPLES['api3'], EXAMPLES['api4'], EXAMPLES['api5']]



def getLimits():
    '''alphavantage limits on usage'''
    print()
    # print('Your api key is:', getKey('alphavantage')['key'])
    print('Limits 5 calls per minute, 500 per day. (Is it time to implement caching?')
    print("They say these are realtime. Need to test it against ib api.")
    print("Intraday goes back 1 week.")
    print("Strangely, currently I find 1 min data goes 1 week")
    print("5 min data goes back about 25 days")
    print("15 and 40 min data goes to the beginning of last month or say 50 days")
    print("60 minute goes back about 3 months")
    print("There is no guarantee, I think maybe the 1 week is the only guarantee.")
    print(__doc__)


def ni(i):
    '''
    Retrieve the correct param for Alphavantage. Limited to minute charts up to 60 minute candle.
    Return also the int values for the request for resampling and the candle interval as an int
    :params i: an int representing a  requested candle size. If i is below 1 or above 120 return
        '1min' and '60min' and no resampling
    :return (bresample, (a,b,c)): (bool, (str, int, int)).
        :params bresample: a bool indicating the requested interval will need to be resampled
        :params a: A str with the av param for the REST api
        :params b: An int representing the av interval
        :params c: an int representing the requested interval
    '''
    resamp = False

    # OK something very weird.  i > 1 was caused an exception when running unittest discover and
    # at no other time.  I placed this baby sitter here and the error disappeared. The exception
    # was comparison of str and int. I could not trigger the exception or find a str instance error
    # It never happened for running unittest test_mav
    if isinstance(i, str):
        print(':::::::::::::::::\n', i, '::::::::::::::::::\n')
    if i < 1:
        i = 1
    elif i > 120:
        i = 60
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
    print(
        f"interval={i} is not supported by alphavantage. Setting to 1min candle as if it were requested")
    return False, ('1min', 1, 1)

RETRY = 3
class Retries:
    '''Number of retries when AV returns a 1 minute violation'''
    def __init__(self):
        self.retries = RETRY
        self.setTime = time.time()
R = None

# TODO Could increase the number of avalable free calls by caching the data. Don't ever call
# 5,15,30, or 60 min (at least for data in the last week) and use resample to get them. For
# charting, 500 calls would go a long way. It could translate to having all the data I need for
# 500 stocks. that might just cover all the stocks traded in a day by all BearBulls traders.
# Combined with the other free APIS, and I would likely have enough data to cover the day.
# Just keep specialized in minute charts for daily review.
def getmav_intraday(symbol, start=None, end=None, minutes=None, showUrl=False):
    '''
    Limited to getting minute data intended to chart day trades
    :params symb: The stock ticker
    :params start: A date time string or datetime object to indicate the beginning time.
    :params end: A datetime string or datetime object to indicate the end time.
    :params minutes: An int for the candle time, 5 minute, 15 minute etc. If minutes is not one of
        Alphavantage's accepted times, we will resample.

    :returns: (status, df, maDict) The DataFrame has minute data indexed by time with columns open, high, low
         low, close, volume and indexed by pd timestamp. If not specified, this
         will return a weeks data. 
    '''
    print('======= Called alpha =======')
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
    params['apikey'] = getKey()

    request_url = f"{BASE_URL}"
    response = requests.get(request_url, params=params)
    if showUrl:
        print(response.url)

    if response.status_code != 200:
        raise Exception(
            f"{response.status_code}: {response.content.decode('utf-8')}")
    result = response.json()
    # tsj = dict()
    keys = list(result.keys())

    if 'Error Message' in keys:
        raise Exception(f"{result['Error Message']}")

    # If we exceed the requests/min, we get a friendly html string sales pitch.
    metaj = result[keys[0]]
    if len(keys) < 2:
        global R            # pylint: disable = W0603
        if not R:
            R = 1
            r = Retries()
        if r.retries > 0:
            print(metaj)
            print(f'Will retry in 60 seconds: {RETRY - r.retries + 1} of {RETRY} tries.')
            r.retries = r.retries - 1

            time.sleep(60)
            return getmav_intraday(symbol, start=start, end=end, minutes=minutes, showUrl=showUrl)
        # This tells us we have exceeded the limit and gives the premium link. AARRGH. Yahoo come back
        return None, None, None

    dataJson = result[keys[1]]

    df = pd.DataFrame(dataJson).T

    df.index = pd.to_datetime(df.index)

    if df.index[0] > df.index[-1]:
        df.sort_index(inplace=True)

    if end:
        if end < df.index[0]:
            msg = 'WARNING: You have requested data that is unavailable:'
            msg = msg + f'\Your end date ({end}) is before the earliest first date ({df.index[0]}).'
            print(msg)
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

    # Alphavantage indexes the candle ends as a time index. The JSON times are backwards.
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
            l = len(df)
            if l == 0:
                msg = f"\nWARNING: you have sliced off all the data with the end date {start}"
                print(msg)
                metaj['code'] = 666
                metaj['message'] = msg
                return metaj, pd.DataFrame(), maDict

    if end:
        if end < df.index[-1]:
            df = df[df.index <= end]
            for ma in maDict:
                maDict[ma] = maDict[ma].loc[maDict[ma].index <= end]
            l = len(df)
            if l < 1:
                msg = f"\nWARNING: you have sliced off all the data with the end date {end}"
                print(msg)
                metaj['code'] = 666
                metaj['message'] = msg
                return metaj, pd.DataFrame(), maDict
    # I expect this to fail soon- when this is called with no start or end
    # This code will not stand either through implementing user control over MAs. Its just good for today
    for key in maDict:
        if len(df) != len(maDict[key]):
            del maDict[key]

    return metaj, df, maDict

def notmain():
    print (APIKEY)
    print(getKey())

if __name__ == '__main__':
    # df = getmav_intraday('SQ')
    # print(df.head())
    notmain()

    # dastart = "2019-01-11 11:30"
    # daend = "2019-01-14 18:40"
    # d = dt.datetime(2018, 12, 20)
    # x, ddf = getmav_intraday("SPY", start=dastart, end=daend, minutes='60min')
    # print(ddf.head(2))
    # print(ddf.tail(2))
