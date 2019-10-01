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
A module to access WorldTradingData API. From the REStful source. This looks like an amazing addition to structjour
@author: Mike Petersen
@creation_date: 9/30/19
WorldTradingData. 
'''

import requests
import pandas as pd

from structjour.stock.utilities import ManageKeys, movingAverage, getLastWorkDay


# Example-- open postman to play with them. We only need intraday here



base_intraday = 'https://intraday.worldtradingdata.com/api/v1/intraday?'
base_wtd = 'https://api.worldtradingdata.com/api/v1/'


def getExamples():
    intraday = f'https://intraday.worldtradingdata.com/api/v1/intraday?symbol=BBBY&range=10&interval=60&api_token={getApiKey()}'
    realTime = f'https://api.worldtradingdata.com/api/v1/stock?symbol=AAPL,MSFT,HSBA.L&api_token={getApiKey()}'
    histOHLCV = f'https://api.worldtradingdata.com/api/v1/history?symbol=AAPL&sort=newest&api_token={getApiKey()}'
    fullHistory = f'https://api.worldtradingdata.com/api/v1/history?symbol=SQ&api_token={getApiKey()}&output=csv&sort=oldest'
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
    return ('\nThis is a very simple API that provides 250 daily requests.\n'
            'For Structjour, we need only the intraday endpoint. It provides data from market\n'
            'open to close. Can retrieve 1 minute historical days up to 7 and 30 days for\n'
            '[2, 5, 15, 60] days by providing the range parameter. Its not encouraging that the\n'
            'docs say "what is currently available" to describe it.  You can customize the\n'
            'interval within [1,2,5,15,60]. We will provide resampling to get intervasl 1-60.\n'
            'See the number of daily requests (of 250) made today at\n'
            'https://www.worldtradingdata.com/home  aka the members area\n\n')

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
    global base_intraday
    base = base_intraday


    if not start:
        tdy = pd.Timestamp.now()
        tdy = getLastWorkDay(tdy)
        start = pd.Timestamp(tdy.year, tdy.month, tdy.day, 9, 30)
    else:
        start = pd.Timestamp(start)
    
    if not end:
        tdy = pd.Timestamp.now()
        tdy = getLastWorkDay(tdy)
        end = pd.Timestamp(tdy.year, tdy.month, tdy.day, 16, 00)
    else:
        end = pd.Timestamp(end)
    
    

    # Retrieve the maximum data to get the longest possible moving averages
    daRange = 30
    if minutes == 1:
        daRange = 7
    params = getParams(symbol, minutes, daRange)
    response = requests.get(base, params=params)
    print (response)
    if response.status_code != 200:
        # TODO get the message they send for reaching data limit
        meta = {'code': 666, 'message': response.text}
        return meta, pd.DataFrame(), None
    result = response.json()
    if result['timezone_name'] != 'America/New_York':
        msg = f'''Time zone returned a non EST zone: {result['timezone_name']}'''
        raise ValueError(msg)
    meta = result['symbol'] + ': ' + result['stock_exchange_short'] + ': ' + result['timezone_name']
    df = pd.DataFrame(data=result['intraday'].values(), index=result['intraday'].keys())

    df.open = pd.to_numeric(df.open)
    df.high = pd.to_numeric(df.high)
    df.low = pd.to_numeric(df.low)
    df.close = pd.to_numeric(df.close)
    df.volume = pd.to_numeric(df.volume)

    df.index = pd.to_datetime(df.index)
    # resample for requested interval if necessary
    values = df.close

    # for i, row in df.iterrows():
    #     d = pd.Timestamp(row['timestamp'])
    #     newd = pd.Timestamp(d.year, d.month, d.day, d.hour, d.minute, d.second)
    #     df.at[i, 'timestamp'] = newd

    maDict = movingAverage(values, df, start)
    # Get requested moving averages
    # Trim off times not requested
    if start > pd.Timestamp(df.index[0]):
        rstart = df.index[0]
        rend = df.index[-1]
        df = df.loc[df.index >= start]
        for ma in maDict:
            maDict[ma] = maDict[ma].loc[maDict[ma].index >= start]

        lendf = len(df)
        if lendf == 0:
            msg = '\nWARNING: all data has been removed.'
            msg += f'\nThe Requested start was({start}).'
            
            print(msg)
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
            msg =  '\nWARNING: all data has been removed.'
            msg = msg + f'\nThe Requested end was({end}).'
            meta['code2'] = 199
            meta['message'] = meta['message'] + msg
            print(meta)
            return meta, df, maDict

    for key in maDict:
        if key == 'vwap':
            continue
        assert len(df) == len(maDict[key])

    # Note we are dropping columns  ['symbol', 'timestamp', 'tradingDay[] in favor of ohlcv 
    df = df.copy(deep=True)
    return meta, df, maDict





    return meta, df, maDict




def notmain():
    # print(getLimits())
    # print(getApiKey())
    for u in getExamples():
        print(u)

def main():
    symbol = 'AAPL'
    start = None
    end = None
    minutes = 1

    meta, df, maDict = getWTD_intraday(symbol, start, end, minutes, False)
    print(df.head)

if __name__ == '__main__':
    notmain()
    # main()


