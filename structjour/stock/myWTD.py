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
Site is relaunched and it does not work for us. It only suppors the EOD end point for free
Key = 
0548796cf6534349cb04c33afaaa4575
0548796cf6534349cb04c33afaaa4575
https://marketstack.com/dashboard  Requires you have already logged in. Can change key here
https://marketstack.com/documentation
0548796cf6534349cb04c33afaaa4575
exampleEndPoint =  "http://api.marketstack.com/v1/eod?access_key=0548796cf6534349cb04c33afaaa4575&symbols=AAPL"
A module to access WorldTradingData API. From the REStful source. This looks like an amazing addition to structjour
@author: Mike Petersen
@creation_date: 9/30/19
WorldTradingData.
'''

import logging
import requests
import pandas as pd


from structjour.stock.utilities import ManageKeys, movingAverage, getLastWorkDay, setLimitReached, getLimitReached


base_wtd = 'https://api.worldtradingdata.com/api/v1/'


def getExamples():
    eod = f'http://api.marketstack.com/v1/eod?access_key={getApiKey()}&symbols=AAPL'
    # intraday = f'https://intraday.worldtradingdata.com/api/v1/intraday?symbol=BBBY&range=10&interval=60&api_token={getApiKey()}'
    # realTime = f'https://api.worldtradingdata.com/api/v1/stock?symbol=AAPL,MSFT,HSBA.L&api_token={getApiKey()}'
    # histOHLCV = f'https://api.worldtradingdata.com/api/v1/history?symbol=AAPL&sort=newest&api_token={getApiKey()}'
    # fullHistory = f'https://api.worldtradingdata.com/api/v1/history?symbol=SQ&api_token={getApiKey()}&output=csv&sort=oldest'
    return [intraday, realTime, histOHLCV, fullHistory]


# For structjour intraday is all we need. A Full history can be retrieved as a download from the members area

def getApiKey():
    mk = ManageKeys()
    key = mk.getKey('wtd')
    return key


def getLimits():
    '''
    Some useful info
    '''
    return ('\nThis is a very simple API that provides 25 intraday daily requests.\n'
            'For Structjour, we need only the intraday endpoint.\n'
            'https://www.worldtradingdata.com/documentation#intraday-market-data\n'
            'It provides data from market open to close. WTD can retrieve 1 minute historical\n'
            'days up to 7 days. And 30 days for candle intervals [2, 5, 15, 60] days.\n'
            'This is complicated for APIChooser. The current signature does not include interval size\n'
            'And it probably should not change. Its not encouraging that the\n'
            'docs say "what is currently available" to describe it.\n\n'
            'Structjour provides resampling to get intervals 1-60 for 7 days (same in all apis)\n'
            'The dashboard is informative.\n'
            'https://www.worldtradingdata.com  and login\n\n')


def getParams(symbol, interval, daRange):
    '''
    Get a dictionary of parameters
    '''
    params = {}
    if interval not in [1, 2, 5, 15, 60]:
        pass
    if interval == 1:
        if daRange > 7:
            daRange = 7
    elif daRange > 30:
        daRange = 30
    params['symbol'] = symbol
    params['range'] = daRange
    params['interval'] = interval
    params['sort'] = 'asc'
    params['api_token'] = getApiKey()
    return params


def ni(i):
    '''
    Return a usable interval. Note that ni accepts D W and M but we are not  going
    to use them in structjour.
    :return: The given argument if its supported or 1, enabling resample for all other (int) values
    '''
    # These are the accepted values for the 'resolution' parameter
    supported = [1, 2, 5, 15, 60]
    if i in supported:
        return i

    elif isinstance(i, int):
        return 1
    return 5


# Implement the common interface for the api chooser
def getWTD_intraday(symbol, start=None, end=None, minutes=5, showUrl=False):
    '''
    Implement the interface to retrieve intraday data. showUrl is not part of this api.
    Note that the requested range will always be the maximum to get the maximum size MA.
    :symbol: The ticker symbol
    :start: Timestamp or time string. The beginning of requested data
    :end: Timestamp or time string. The end of requested data
    :minutes: int between 1 and 60
    :showUrl: not used
    :return: meta, df, maDict
    :depends: On the settings of 'zero_substance/chart' for moving average settings
    '''
    # Intraday base differs from others. It has the intrday subdomain instead of api subdomain
    if getLimitReached('wtd'):
        msg = 'World Trade Data limit was reached'
        logging.info(msg)
        return {'code': 666, 'message': msg}, pd.DataFrame(), None

    logging.info('======= called WorldTradingData. 25 calls per day limit =======')
    base = 'https://intraday.worldtradingdata.com/api/v1/intraday?'

    original_minutes = minutes
    if not isinstance(original_minutes, int):
        original_minutes = 5
    minutes = ni(minutes)
    if not isinstance(minutes, int) or minutes < 0 or minutes > 60:
        raise ValueError('Only candle intervals between 1 and 60 are supported')

    if not start:
        tdy = pd.Timestamp.now()
        tdy = getLastWorkDay(tdy)
        start = pd.Timestamp(tdy.year, tdy.month, tdy.day, 9, 25)
    else:
        start = pd.Timestamp(start)

    if not end:
        tdy = pd.Timestamp.now()
        tdy = getLastWorkDay(tdy)
        end = pd.Timestamp(tdy.year, tdy.month, tdy.day, 16, 5)
    else:
        end = pd.Timestamp(end)

    # Retrieve the maximum data to get the longest possible moving averages
    daRange = 30
    if minutes == 1:
        daRange = 7
    params = getParams(symbol, minutes, daRange)
    response = requests.get(base, params=params)

    meta = {'code': response.status_code}
    if response.status_code != 200:
        meta = {'code': 666, 'message': response.text}
        return meta, pd.DataFrame(), None
    result = response.json()
    if 'intraday' not in result.keys():
        if 'message' in result.keys():
            d = pd.Timestamp.now()
            dd = pd.Timestamp(d.year, d.month, d.day + 1, 3, 0, 0)
            setLimitReached('wtd', dd)
            logging.warning(f"WorldTradeData limit reached: {result['message']}")
            meta['message'] = result['message']
        else:
            meta['message'] = 'Failed to retrieve data from WorldTradingData'
        return meta, pd.DataFrame(), None

    if result['timezone_name'] != 'America/New_York':
        msg = f'''Time zone returned a non EST zone: {result['timezone_name']}'''
        raise ValueError(msg)
    meta['message'] = result['symbol'] + ': ' + result['stock_exchange_short'] + ': ' + result['timezone_name']
    df = pd.DataFrame(data=result['intraday'].values(), index=result['intraday'].keys())

    df.open = pd.to_numeric(df.open)
    df.high = pd.to_numeric(df.high)
    df.low = pd.to_numeric(df.low)
    df.close = pd.to_numeric(df.close)
    df.volume = pd.to_numeric(df.volume)

    df.index = pd.to_datetime(df.index)
    # resample for requested interval if necessary

    if original_minutes != minutes:
        srate = f'{original_minutes}T'
        df_ohlc = df[['open']].resample(srate).first()
        df_ohlc['high'] = df[['high']].resample(srate).max()
        df_ohlc['low'] = df[['low']].resample(srate).min()
        df_ohlc['close'] = df[['close']].resample(srate).last()
        df_ohlc['volume'] = df[['volume']].resample(srate).sum()
        df = df_ohlc.copy()

    # Get requested moving averages
    maDict = movingAverage(df.close, df, start)

    # Trim off times not requested
    if start > pd.Timestamp(df.index[0]):
        # rstart = df.index[0]
        # rend = df.index[-1]
        df = df.loc[df.index >= start]
        for ma in maDict:
            maDict[ma] = maDict[ma].loc[maDict[ma].index >= start]

        lendf = len(df)
        if lendf == 0:
            msg = '\nWARNING: all data has been removed.'
            msg += f'\nThe Requested start was({start}).'

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
            logging.error(f'{meta}')
            return meta, df, maDict

    # If we don't have a full ma, delete -- Later:, implement a 'delayed start' ma in graphstuff and remove this stuff
    keys = list(maDict.keys())
    for key in keys:
        if len(df) != len(maDict[key]):
            del maDict[key]

    # Note we are dropping columns  ['symbol', 'timestamp', 'tradingDay[] in favor of ohlcv
    df = df.copy(deep=True)
    return meta, df, maDict


def notmain():
    for u in getExamples():
        print(u)


def main():
    symbol = 'ROKU'
    start = '20200220'
    end = None
    minutes = 2

    meta, df, maDict = getWTD_intraday(symbol, start, end, minutes, False)
    if not df.empty:
        print(meta)
        print(df.head(2))
        print(df.tail(2))
    else:
        print(meta['message'])
def relaunch():
    print(getApiKey())

if __name__ == '__main__':
    relaunch()
    # notmain()
    # text = 'You have reached your request limit for the day. Upgrade to get more daily requests.'
    # main()
