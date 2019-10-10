import pandas as pd
import numpy as np
import requests
import datetime, pytz

from structjour.stock.utilities import ManageKeys, movingAverage, getNewyorkTZ, excludeAfterHours
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
    Method does three things, 
        1) gets a start request prior to start (for MA calcs)
        2) Adjusts for user time (NY) to  Grenwich conversion
        3) converts to unix timestamp
    :start: Timestamp-- users requested start
    :end: Timestamp-- users requested end
    :interval: int-- Users requested candle interval
    '''
    delt = pd.Timedelta(minutes=interval*2000)
    deltzone = pd.Timedelta(hours=-getNewyorkTZ(end)) 
    rstart = start - delt + deltzone
    rend =  end + deltzone
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
    print('======= Called Finnhub -- no practical limit, 60/minute =======')
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
        print(response.url)
    j = response.json()
    if 'o' not in j.keys():
        meta = {'code': 666, 'message': j['s']}
        return meta, pd.DataFrame, None
    assert set(['o', 'h', 'l', 'c', 't', 'v', 's']).issubset(set(j.keys()))
    meta = {'message': j['s'], 'code': 199}
    if j['s'] == 'no_data':
        print('WTF')

    d = {'open': j['o'], 'high': j['h'], 'low':j['l'],
         'close': j['c'], 'timestamp': j['t'], 'volume': j['v']}
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
        l = len(df)
        if l == 0:
            msg = f"\nWARNING: you have sliced off all the data with the end date {start}"
            print(msg)
            metaj={}
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
    # print(pd2unix('2019-09-30 09:30'), pd2unix('2019-09-30 10:30'))
    # print(unix2pd(1569988860), unix2pd(1570037220))
    symbol = 'ROKU'
    count = 500
    minutes = 2
    start = '2019-10-10 03:15'
    end = '2019-10-10 18:02'
    meta, df, maD  = getFh_intraday(symbol, start, end,  minutes)
    print(df.head())
    print(df.tail())
    print()

if __name__ == '__main__':
    notmain()

