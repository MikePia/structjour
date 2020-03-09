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
TODO Checkout finnhub from pypi.
This has a generous free with 60 per second throttle. And it goes back 20 years.
@author: Mike Petersen
@creation_date:2018-12-11
(or so)
'''
import logging
import pandas as pd
import numpy as np
import requests

from structjour.stock.utilities import ManageKeys, movingAverage, getNewyorkTZ, excludeAfterHours, setLimitReached, getLimitReached


example = 'https://finnhub.io/api/v1/stock/candle?symbol=AAPL&resolution=1&count=200&token=bm9spbnrh5rb24oaaehg'


def ni(i):
    '''
    Return a usable interval (called resolution in the api). Note that ni accepts D W and M but structjour
    will never put it in a a request.
    :return: The given argument if its supported or 1, enabling resample for all other (int) values
    '''
    # These are the accepted values for the 'resolution' parameter
    supported = [1, 5, 15, 30, 60, 'D', 'W', 'M']
    if i in supported:
        return i
    elif isinstance(i, int):
        return 1
    return 5


def getApiKey():
    mk = ManageKeys()
    key = mk.getKey('fh')
    return key


def getLimits():
    limits = ('Most endpoints will only take up 1 call from your API limit. However, some endpoints\n'
             'might have heavier weight. If your limit is exceeded, you will receive a response with\n'
             'status code 429.\n\n'
             "On top of all plan's limit, there is a 30 API calls/ second limit (this limit is not\n"
             'subjected to Weight count - all calls counted as 1).\n\n'
             'Quote from docs-- see skeptical on my face. Seems way too generous for free')
    return limits

# def getParams(symbol, interfal, numCandles=None, start=None):
    # params = {}


def pd2unix(t):
    t = pd.Timestamp(t)
    epoc = pd.Timestamp('1970-01-01')
    return (t - epoc).total_seconds()


def unix2pd(t):
    assert isinstance(t, (int, np.integer))
    return pd.Timestamp(t * 10**9)


def getStartForRequest(start, end, interval):
    '''
    Method does three things,
        1) gets a start request prior to start (for MA calcs)
        2) Adjusts for user time (NY) to  Grenwich conversion
        3) converts to unix timestamp
    :start: Timestamp-- users requested start
    :end: Timestamp-- users requested end
    :interval: int-- Users requested candle interval
    '''
    delt = pd.Timedelta(minutes=interval * 2000)
    deltzone = pd.Timedelta(hours=-getNewyorkTZ(end))
    rstart = start - delt + deltzone
    rend = end + deltzone
    rstart = int(pd2unix(rstart))
    rend = int(pd2unix(rend))
    return rstart, rend
    pass


def getParams(symbol, start, end, interval):
    '''
    Set the paramaters to send to finnhub. The start will be set back to enable a moving average
    of 200 The interval will be set to one that finnhub accepts. An interval of 1 can be resampled
    to any number 1-60.

    :symbol: The ticker to get
    :start: Timestamp. The user requested start time
    :end: Timestamp. The user requested end time
    :interval: Timestamp. The user requested candle interval
    '''
    rstart, rend = getStartForRequest(start, end, interval)
    interval = ni(interval)
    params = {}
    params['symbol'] = symbol
    params['from'] = rstart
    params['to'] = rend
    params['resolution'] = interval
    params['token'] = getApiKey()
    return params


def getFh_intraday(symbol, start=None, end=None, minutes=5, showUrl=False):
    '''
    Common interface for apiChooser. Timezone is determined by the trade day. If this were used
    for multiday trades spanning DST, the times will be inaccurate before the time change. The
    chooser is desinged for single day trades.
    '''
    if getLimitReached('fh'):
        msg = 'Finnhub limit was reached'
        logging.info(msg)
        return {'code': 666, 'message': msg}, pd.DataFrame(), None

    logging.info('======= Called Finnhub -- no practical limit, 60/minute =======')
    base = 'https://finnhub.io/api/v1/stock/candle?'
    if not start or not end:
        s = pd.Timestamp.today()
        start = pd.Timestamp(s.year, s.month, s.day, 9, 15)
        end = pd.Timestamp(s.year, s.month, s.day, 16, 15)
    else:
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

    if not isinstance(minutes, int):
        minutes = 60
    params = getParams(symbol, start, end, minutes)
    response = requests.get(base, params=params)
    if showUrl:
        logging.info(response.url)

    meta = {'code': response.status_code}
    if response.status_code != 200:
        meta['message'] = response.content
        if response.status_code == 429:
            # 60 calls per minute. Could possibly get called if automatic chart download is
            # put into the program. Set a time in two minutes
            d = pd.Timestamp.now()
            dd = pd.Timestamp(d.year, d.month, d.day, d.hour, d.minute + 2, d.second)
            setLimitReached('fh', dd)
        meta = {'code': response.status_code, 'message': response.content}
        logging.error(meta)
        return meta, pd.DataFrame, None
    j = response.json()
    meta['message'] = j['s']
    if 'o' not in j.keys():
        meta['code'] = 666
        logging.error('Error-- no data')
        return meta, pd.DataFrame(), None
    assert set(['o', 'h', 'l', 'c', 't', 'v', 's']).issubset(set(j.keys()))

    d = {'open': j['o'], 'high': j['h'], 'low': j['l'],
         'close': j['c'], 'timestamp': j['t'], 'volume': j['v']}
    if len(d['open']) == 0:
        meta['code'] = 666
        logging.error('Error-- no data')
        return meta, pd.DataFrame(), None

    df = pd.DataFrame(data=d)
    tradeday = unix2pd(int(df.iloc[-1]['timestamp']))
    tzdelt = getNewyorkTZ(tradeday) * 60 * 60
    df.index = pd.to_datetime(df['timestamp'] + tzdelt, unit='s')

    df = df[['open', 'high', 'low', 'close', 'volume']]

    if minutes != params['resolution']:
        srate = f'{minutes}T'
        df_ohlc = df[['open']].resample(srate).first()
        df_ohlc['high'] = df[['high']].resample(srate).max()
        df_ohlc['low'] = df[['low']].resample(srate).min()
        df_ohlc['close'] = df[['close']].resample(srate).last()
        df_ohlc['volume'] = df[['volume']].resample(srate).sum()
        df = df_ohlc.copy()

    # API retrieves *all* times. Prune out all NaN (from after hours)
    df = df[df['open'] > 0]
    if excludeAfterHours():
        d = df.index[-1]
        o = pd.Timestamp(d.year, d.month, d.day, 9, 30)
        c = pd.Timestamp(d.year, d.month, d.day, 16, 00)
        if df.index[0] < o:
            df = df[df.index >= o]
            df = df[df.index <= c]

    maDict = movingAverage(df.close, df, start)
    if start > df.index[0]:
        df = df[df.index >= start]
        for ma in maDict:
            maDict[ma] = maDict[ma].loc[maDict[ma].index >= start]
        if len(df) == 0:
            msg = f"You have sliced off all the data with the end date {start}"
            logging.warning(msg)
            metaj = {}
            metaj['code'] = 666
            metaj['message'] = msg
            return metaj, pd.DataFrame(), maDict

    if end < df.index[-1]:
        df = df[df.index <= end]
        for ma in maDict:
            maDict[ma] = maDict[ma].loc[maDict[ma].index <= end]
        if len(df) < 1:
            msg = f"Tou have sliced off all the data with the end date {end}"
            logging.warning(msg)
            metaj = {}
            metaj['code'] = 666
            metaj['message'] = msg
            return metaj, pd.DataFrame(), maDict
    # If we don't have a full ma, delete -- Later:, implement a 'delayed start' ma in graphstuff
    deleteMe = []
    for key in maDict.keys():
        if len(df) != len(maDict[key]):
            deleteMe.append(key)
    for k in deleteMe:
        del maDict[k]

    return meta, df, maDict


def notmain():
    symbol = 'ROKU'
    minutes = 2
    start = '2019-10-10 03:15'
    end = '2019-10-10 18:02'
    for i in range(260):
        meta, df, maD = getFh_intraday(symbol, start, end, minutes)
        if not df.empty and i % 7 == 0:
            print('Call number ', i)
            print(df.tail(1))
            print()
            # print(meta)
            # print(df.head(2))
            # print(df.tail(2))
        else:
            if not i % 25:
                print(i)
                print(meta['message'])
        # time.sleep(1)
        # print('next', i)
        # print()
        # print()


if __name__ == '__main__':
    text = b'API limit reached. Please try again later.'
    notmain()
    # print(getApiKey())
