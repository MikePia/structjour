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
TODO: Checkout finnhub from pypi.
TODO: excludeAfterHours removed 4/29/20. All requests will include afterHours data. fix later. 
This has a generous free with 60 per second throttle. And it goes back 20 years.
@author: Mike Petersen
@creation_date:2018-12-11
(or so)
'''
from dateutil.tz import gettz
import datetime as dt
import logging
import pandas as pd
import numpy as np
import requests

from structjour.stock.utilities import ManageKeys, movingAverage, setLimitReached, getLimitReached, getTzAware


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
    '''
    :params t: a tz aware datetime object
    :exception: Will raise an assertion error if t is not datetime or has no tzinfo assoatiated.
    '''
    assert isinstance(t, dt.datetime)
    # assert t.tzinfo is not None

    epoc = dt.datetime(1970, 1, 1, tzinfo=t.tzinfo)
    return (t - epoc).total_seconds()


def unix2pd(t, tzstring="US/Eastern"):
    assert isinstance(t, (int, np.integer))
    eastern = gettz(tzstring)
    return dt.datetime.fromtimestamp(t, eastern)


def getStartForRequest(start, end, interval):
    '''
    Method does two things,
        1) gets a start request prior to start (for MA calcs)
        3) converts to unix timestamp
    :start: Tz Aweare datetime object
    :interval: int-- Users requested candle interval
    :return: A uniz epoch that will request enough data to calculate a 200 MA for the given interval
    '''

    delt = pd.Timedelta(minutes=interval * 2000)

    rstart = start - delt
    rstart = int(pd2unix(rstart))
    rend = int(pd2unix(end))
    return rstart, rend


# def getParams(symbol, start, end, resolution):
def fh_intraday(base, symbol, start, end, resolution, showUrl=False):
    '''
    Set the paramaters and send to finnhub. (The requesed start time should allow for moving average calculations.)

    :symbol: The ticker to get
    :start: Unixtime. The requested start time for finnhub data.
    :end: Unixtime. The requested end time for finnhbub data.
    :interval: The candle interval. Must be one of [1, 5, 15, 30, 60, 'D', 'W', 'M']
    '''

    params = {}
    params['symbol'] = symbol
    params['from'] = start
    params['to'] = end
    params['resolution'] = resolution
    params['token'] = getApiKey()
    
    response = requests.get(base, params=params)
    if showUrl:
        logging.info(response.url)

    meta = {'code': response.status_code}
    if response.status_code != 200:
        meta['message'] = response.content
        if response.status_code == 429:
            # 60 calls per minute. Could possibly get called if automatic chart download is
            # put into the program. Allow a retry in two minutes. getLimitReached is the gatekeeper method.
            d = pd.Timestamp.now()
            dd = pd.Timestamp(d.year, d.month, d.day, d.hour, d.minute + 2, d.second)
            setLimitReached('fh', dd)
        meta = {'code': response.status_code, 'message': response.content}
        logging.error(meta)
        return meta, {}
    j = response.json()
    meta['message'] = j['s']
    if 'o' not in j.keys():
        meta['code'] = 666
        logging.error('Error-- no data')
    return meta, j


def getdf(j):
    '''
    Create a df from the json. convert the unixtime to a timezone aware datetime set to New York time
    and set it as index in the df.
    :params j: The json object from request. j['t'] is the unix time array
    '''
    j['time'] = []
    for v in j['t']:
        j['time'].append(dt.datetime.fromtimestamp(v, gettz("utc")))

    d = {'timestamp': j['time'], 'open': j['o'], 'high': j['h'], 'low': j['l'],
         'close': j['c'], 'volume': j['v']}

    df = pd.DataFrame(data=d)
    df.set_index('timestamp', inplace=True)

    df = df[['open', 'high', 'low', 'close', 'volume']]
    return df


def resample(df, minutes, resolution):
    if minutes != resolution:
        srate = f'{minutes}T'
        df_ohlc = df[['open']].resample(srate).first()
        df_ohlc['high'] = df[['high']].resample(srate).max()
        df_ohlc['low'] = df[['low']].resample(srate).min()
        df_ohlc['close'] = df[['close']].resample(srate).last()
        df_ohlc['volume'] = df[['volume']].resample(srate).sum()
        df = df_ohlc.copy()
    return df


def trimit(df, maDict, start, end, meta):
    start = pd.Timestamp(start).tz_localize(df.index[0].tzinfo)
    end = pd.Timestamp(end).tz_localize(df.index[0].tzinfo)
    if start > df.index[0]:
        df = df[df.index >= start]
        for ma in maDict:
            maDict[ma] = maDict[ma].loc[maDict[ma].index >= start]
        if len(df) == 0:
            msg = f"You have sliced off all the data with the end date {start}"
            logging.warning(msg)
            meta['code'] = 666
            meta['message'] = msg
            return meta, pd.DataFrame(), maDict

    if end < df.index[-1]:
        df = df[df.index <= end]
        for ma in maDict:
            maDict[ma] = maDict[ma].loc[maDict[ma].index <= end]
        if len(df) < 1:
            msg = f"Tou have sliced off all the data with the end date {end}"
            logging.warning(msg)
            meta = {}
            meta['code'] = 666
            meta['message'] = msg
            return meta, pd.DataFrame(), maDict
    # If we don't have a full ma, delete -- Later:, implement a 'delayed start' ma in graphstuff
    deleteMe = []
    for key in maDict.keys():
        if len(df) != len(maDict[key]):
            deleteMe.append(key)
    for k in deleteMe:
        del maDict[k]
    return meta, df, maDict


def getDaTime(datime, isStart=True):
    '''
    Probaly place in utilities. Will returne a tz aware datetime object. If datime is None, will coerce
    a start or end date that is either 9:15 or 16:15 depending on isStart parameter
    '''

    if not datime:
        s = dt.datetime.now()
        hour = 9 if isStart else 16
        datime = dt.datetime(s.year, s.month, s.day, hour, 15)
    else:
        datime = pd.Timestamp(datime).to_pydatetime()
    return datime


def getFh_intraday(symbol, start=None, end=None, minutes=5, showUrl=False):
    '''
    Common interface for apiChooser.
    :params start: Time string or naive pandas timestamp or naive datetime object.
    :params end: Time string or naive pandas timestamp or naive datetime object.
    '''
    if getLimitReached('fh'):
        msg = 'Finnhub limit was reached'
        logging.info(msg)
        return {'code': 666, 'message': msg}, pd.DataFrame(), None

    logging.info('======= Called Finnhub -- no practical limit, 60/minute =======')
    base = 'https://finnhub.io/api/v1/stock/candle?'

    start = getDaTime(start, isStart=True)
    end = getDaTime(end, isStart=False)

    if not isinstance(minutes, int):
        minutes = 60
    resolution = ni(minutes)
    rstart, rend = getStartForRequest(start, end, minutes)

    meta, j = fh_intraday(base, symbol, rstart, rend, resolution)
    if meta['code'] != 200:
        return meta, pd.DataFrame(), None

    assert set(['o', 'h', 'l', 'c', 't', 'v', 's']).issubset(set(j.keys()))
    if len(j['o']) == 0:
        meta['code'] = 666
        logging.error('Error-- no data')
        return meta, pd.DataFrame(), None

    df = getdf(j)
    df = resample(df, minutes, resolution)
    # remove candles that lack data
    df = df[df['open'] > 0]

    maDict = movingAverage(df.close, df, start)
    meta, df, maDict = trimit(df, maDict, start, end, meta)

    return meta, df, maDict


def notmain():
    symbol = 'TSLA'
    minutes = 2
    start = '2019-10-10 09:15'
    end = '2019-10-10 12:00'
    # for i in range(260):
    meta, df, maD = getFh_intraday(symbol, start, end, minutes, showUrl=True)
    if not df.empty:
        print(df.tail())
    else:
        print(meta['message'])


if __name__ == '__main__':
    text = b'API limit reached. Please try again later.'
    notmain()
    # print(getApiKey())
