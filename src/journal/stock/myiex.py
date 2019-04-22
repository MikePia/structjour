'''
A module to access iex API. From the REStful source. No wrapeere packages
@author: Mike Petersen
@creation_date: 12/20/18
'''
# import datetime as dt
import pandas as pd
import requests
# pylint: disable=C0103


apiurl = 'https://api.iextrading.com/1.0/stock/aapl/chart/5y?format=json'
newsurl = 'https://api.iextrading.com/1.0/stock/aapl/batch?types=quote,news,chart&range=1m&last=10'
apidocs = 'https://iextrading.com/developer/docs/#getting-started'
termsofuse = 'https://iextrading.com/api-exhibit-a/'

BASE_URL = 'https://api.iextrading.com/1.0'

# Follows the Chart API
# API = f"/stock/{symbol}/{range}/"
RANGE = ['5y', '2y', '1y', 'ytd', '6m', '3m',
         '1m', '1d', 'date/{date}', 'dynamic']
# Minute data is only provided by 1d, assumed by a given date/YYYYMMdd,
# or determined by dynamic, and is only available for a trailing 30 days

# Provided as documentation in code. Could use it to validate key if provided by user.
PARAMS = {'chartReset': True,                           # Default False
          'chartSimplify': True,                        # Default False
          'chartInterval': [1, 2, 5, 10, 15, 30, 60],    # Will accept any int
          'changeFromClose': True,                      # Default False
          'chartLast': 100                               # Will accept any int
          }

DAY_COLUMNS = ['minute', 'marketAverage', 'marketNotional', 'marketNumberOfTrades', 'marketOpen',
               'marketClose', 'marketHigh', 'marketLow', 'marketVolume', 'marketChangeOverTime',
               'average', 'notional', 'numberOfTrades', 'simplifyFactor']

ALL_COLUMNS = ['high', 'low', 'volume', 'label',
               'changeOverTime', 'date', 'open', 'close']

# vwap here makes no sen=se as it has no meaning except on the intraday chart. Do they provide
# a single vwap value for each day?

XDAY_COLUMNS = ['unadjustedVolume', 'change', 'changePercent', 'vwap']


def validateTimeString(start, end):
    '''
    Validates the HH:MM time strings
    :raise: ValueError on bad string.
    '''
    msg = 'The start and end paramaters must be formatted HH:MM'
    for token in (start, end):
        if token:
            try:
                assert len(token) == 5
                h, m = token.split(':')
                h = int(h)
                m = int(m)
                assert h < 24
                assert h > -1
                assert m < 60
                assert m > -1
            except Exception as ex:
                print(f"{ex.__class__.__name__}: {ex}")
                raise ValueError(msg)


def getiex_intraday(symbol, start=None, end=None, minutes=None, showUrl=False):
    '''
    An interface wrapper to the IEX intraday 1d API. Retrieves minute data for one of
    the last 30 days
    :params symbol: The ticker to get
    :params start: A datetime object or time string for beginning of the chart. Start and end must
        be on the same day.
    :params start: A datetime object or time string for end of the chart. Start and end must be on
        the same day.
    :params minutes: The length of the candle to retrieve.
    :params showUrl: If true, will print the URL before calling the API
    :return: A DataFrame with [minutes, open, high, low, close, volume] candles.
    :raise: ValueError if start and end day are different.
    :raise: Exception if the API return's status is not 200
    '''
    startday = endday = None
    if start:
        start = pd.Timestamp(start)
        startday = pd.Timestamp(start.year, start.month, start.day)
        # starttime = start.strftime("%H:%M")
    if end:
        end = pd.Timestamp(end)
        endday = pd.Timestamp(end.year, end.month, end.day)
        # endtime = end.strftime("%H:%M")
        if not start:
            startday = endday
    elif start:
        endday = startday

    if startday != endday:
        raise ValueError(
            'start and end parameters must be on the same day for IEX intraday API')
    df = get_trading_chart(symbol, start=start, end=end,
                           minutes=minutes, showUrl=showUrl)
    if not df.empty:
        # Put then in the expected order
        df = df[['open', 'high', 'low', 'close', 'volume']].copy(deep=True)

    # HACK, reurning a tuple to have the same method signature as the others-- some redesign comin
    return len(df), df

# TODO combine these two methods on this page


def get_trading_chart(symb, start=None, end=None, minutes=None, filt=False, showUrl=False):
    '''
    Limited to getting minute data intended to chart day trades. The API has
    stock/{symb}/1d/date/theDate     The '1d' determines some behavior. Minute charts
        are only available for one day and must provide 'date/yyyymmdd' to the url.
    :params symb: The stock ticker
    :parms start: A datetime object or time string indicating the beginning of the requested data.
                    When set to none, will retrieve the today or the most recent bizday.
    :params end:  A datetime object or time string indicating the beginning of the requested data
    :params minutes: An int for the candle time, 5 minute, 15 minute etc. Any int is accepted.
    :params filt: Represents the columns to include. With no entry, all columns. filt=default will
        return ohlcv.  A comma seperated list will retrive those columns.
    :returns: A DataFrame from within a single day indexed by minutes.
    :raise: Exception is the call return status != 200.
    '''
    url = "chart"
    rng = "1d"

    # Validate start and end time string will raise ValueError on bad time string
    # validateTimeString(start, end)

    start = pd.Timestamp(start) if start else None
    end = pd.Timestamp(end) if end else None
    theDate = start.strftime("%Y%m%d") if start else None
    if theDate:
        ts = pd.Timestamp(theDate)
        now = pd.Timestamp.today()
        now = pd.Timestamp(now.year, now.month, now.day)
        if ts > now:
            print('\nWARNING: you have requested a day in the future. Call cancelled.\n')
            return pd.DataFrame()

        rng = f"date/{theDate}"
    params = {}
    if minutes:

        params['chartInterval'] = minutes
    # We need to get a couple extra fields to set a Timestamp index. Take tham back out below
    removeFilt = []
    if filt:
        if filt == 'default':
            params['filter'] = 'date,minute,open,high,low,close, volume'
        else:
            # User has asked for specific fields only. If minute and date are not among them, we
            # need add them now and remove them after they have outlived their usefulness below.
            # For now we need the minute and date fields to create a new index datetime
            if filt.find('minute') < 0:
                filt = filt + ', minute'
                removeFilt.append('minute')
            if filt.find('date') < 0:
                filt = filt + ', date'
                removeFilt.append('date')
            params['filter'] = filt

    request_url = f"{BASE_URL}/stock/{symb}/{url}/{rng}"

    response = requests.get(request_url, params=params)

    if showUrl:
        print(response.url)

    if response.status_code != 200:
        raise Exception(
            f"{response.status_code}: {response.content.decode('utf-8')}")
    result = response.json()
    if not result:
        # DataFrames cannot be checked for None !?!
        return pd.DataFrame()

    df = pd.DataFrame(result)

    df['newcolumn'] = df['date'] + ' ' + df['minute']
    df.set_index('newcolumn', inplace=True)
    df.index = pd.to_datetime(df.index)
    if filt:
        if filt == 'default':
            df = df[['open', 'high', 'low', 'close', 'volume']].copy(deep=True)

    for col in removeFilt:
        df.drop(col, axis=1, inplace=True)

    df = df.loc[df.index >= start] if start else df
    df = df.loc[df.index <= end] if end else df
    return df


BASE_URL = 'https://api.iextrading.com/1.0'


def get_historical_chart(symb, start=None, end=None, showUrl=False, filt=False):
    '''
    Gets end of day daily information from journal.stock ticker symb.
    :parmas symb: The stock ticker
    :params:start: Starting Date time. A Datetime object or string.
    :params:end: Ending date time. A Datetime object or string.
    :params  filt: Return only date ohlcv -whic is the default for this endpoint anyway
    :return: A DataFrame with an index of date->timestamp and numpy.float values on ohlcv
    :raise: Exception if the API call returns a status other than 200
    '''
    # now = dt.datetime.today()

    # This should be transparent for the user. We will calculate based on start and end
    rng_d = {'5y': 60, '2y': 24, '1y': 12,
             '6m': 6, '3m': 3, '1m': 1}

    params = {}
    url = "chart"

    # Set the default to 2 years
    rng = '5y'
    # months = 60
    if start:
        # This will round up to get an extra month (or less) when we are close to the 5 year limit
        now = pd.Timestamp.today()
        start = pd.to_datetime(start)
        reqmonths = (((now - start).days)/30) + 1
        if reqmonths > 60:
            print('You have requested data beginning {}'.format(
                start.strftime("%B,%Y")))
            print('This API is limited to 5 years historical data.')
        for key in rng_d:
            if rng_d[key] > reqmonths:
                rng = key
            else:
                break

    if filt:
        params['filter'] = 'date,minute,open,high,low,close,average,volume'

    request_url = f"{BASE_URL}/stock/{symb}/{url}/{rng}"

    response = requests.get(request_url, params=params)
    if response.status_code != 200:
        raise Exception(
            f"{response.status_code}: {response.content.decode('utf-8')}")
    if showUrl:
        print(response.url)

    result = response.json()
    if not result:
        return None

    df = pd.DataFrame(result)

    df.open = pd.to_numeric(df.open)
    df.high = pd.to_numeric(df.high)
    df.low = pd.to_numeric(df.low)
    df.close = pd.to_numeric(df.close)
    df.volume = pd.to_numeric(df.volume)

    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    if start:
        start = pd.to_datetime(start)
        # start = start.strftime("%Y-%m-%d")
        df = df.loc[df.index >= start]
    if end:
        end = pd.to_datetime(end)
        # end = end.strftime("%Y-%m-%d")
        df = df.loc[df.index <= end]
    return df  # [['open', 'high', 'low', 'close', 'volume' ]].copy(deep=True)


def main():
    '''Run code locally for testing n stuff'''
    # df = get_historical_chart('AAPL', dt.datetime(2017,6,6), dt.datetime(2018,10,4), showUrl=True)
    # print (type(df.index[0]))
    # print (type(df.close[0]))
    # print (df.tail(5))

    start = '2018-12-31 11:30'
    end = '2018-12-31 16:05'
    dummy, df = getiex_intraday('AAPL', start, end, minutes=1, showUrl=True)
    print(df)


if __name__ == "__main__":
    main()
