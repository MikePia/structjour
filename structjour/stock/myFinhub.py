import pandas as pd
import numpy as np
import requests

from structjour.stock.utilities import ManageKeys, movingAverage
APIKEY = 'bm9spbnrh5rb24oaaehg'


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
    limits= ('Most endpoints will have a limit of 60 requests per minute per api key. However,\n'
             '//scan endpoint have a limit of 10 requests per minute. If your limit is exceeded,\n'
             'you will receive a response with status code 429.\n\n'
             'Quote from docs-- see skeptical on my face')

# def getParams(symbol, interfal, numCandles=None, start=None):
    # params = {}
    
def pd2unix(t):
    t = pd.Timestamp(t)
    epoc = pd.Timestamp('1970-01-01')
    return (t-epoc).total_seconds()

def unix2pd(t):
    assert isinstance (t, (int, np.integer))
    return pd.Timestamp(t*10**9)

def getStartForRequest(start, end, interval):
    '''
    Method does two things, gets a start request prior to start to get enough data to calculate
    a 200 MA. Finnhub seems to get data from 8AM to 12PM Mon-Fri. (Havn't seen it in docs). But 
    here we will just get enough data to succeed and adjust it (Trying 1000 intervals)
    '''
    delt = pd.Timedelta(minutes=interval*1000)
    rstart = start - delt
    rstart = int(pd2unix(rstart))
    rend = int(pd2unix(end))
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
    print('======= Called Finnhub -- no practical limit, 60/minute =======')
    rstart, rend = getStartForRequest(start, end, interval)
    interval = ni(interval)
    params = {}
    params['symbol'] = symbol
    params['from'] = rstart
    params['to'] = rend
    params['resolution'] = interval
    params['token'] = getApiKey()
    return params

def getFh_intraday(symbol, start=None, end = None, minutes=5):
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
    j = response.json()
    if 'o' not in j.keys():
        return j, pd.DataFrame, None
    assert set(['o', 'h', 'l', 'c', 't', 'v', 's']).issubset(set(j.keys()))
    meta = j['s']

    d = {'open': j['o'], 'high': j['h'], 'low':j['l'],
         'close': j['c'], 'timestamp': j['t'], 'volume': j['v']}
    status = j['s']
    df = pd.DataFrame(data=d)
    df.index = pd.to_datetime(df['timestamp'],unit='s')

    df = df[['open', 'high', 'low', 'close', 'volume']]

    if minutes != params['resolution']:
        srate = f'{minutes}T'
        df_ohlc = df[['open']].resample(srate).first()
        df_ohlc['high'] = df[['high']].resample(srate).max()
        df_ohlc['low'] = df[['low']].resample(srate).min()
        df_ohlc['close'] = df[['close']].resample(srate).last()
        df_ohlc['volume'] = df[['volume']].resample(srate).sum()
        df = df_ohlc.copy()

    maDict = movingAverage(df.close, df, start)
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
    # If we don't have a full ma, delete -- Later:, implement a 'delayed start' ma in graphstuff
    keys = maDict.keys()
    for key in keys:
        if len(df) != len(maDict[key]):
            del maDict[key]




    return meta, df, None





def notmain():
    # print(pd2unix('2019-09-30 09:30'), pd2unix('2019-09-30 10:30'))
    # print(unix2pd(1569988860), unix2pd(1570037220))
    symbol = 'AAPL'
    count = 500
    minutes = 15
    start = '2019-10-02 10:45'
    end = '2019-10-02 15:45'
    meta, df, maD = getFh_intraday(symbol, start, end,  minutes)
    print(df.head())
    print(df.tail())
    print()

if __name__ == '__main__':
    notmain()

