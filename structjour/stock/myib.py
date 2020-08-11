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
Implement historicalData method from the IB API
@author: Mike Petersen
@creation_date: 1/2/19
'''

# import sys
import datetime as dt
import logging
from threading import Thread
import queue
import pandas as pd

from PyQt5.QtCore import QSettings

from structjour.stock.utilities import checkForIbapi, excludeAfterHours
if checkForIbapi():

    from ibapi import wrapper
    from ibapi.client import EClient

    # from ibapi.wrapper import EWrapper
    from ibapi.common import TickerId
    from ibapi.contract import Contract
else:
    raise ImportError('\nIBAPI is not installed. The module myib cannot run.\n')

from structjour.stock.utilities import getLastWorkDay, IbSettings, movingAverage


# import time
# pylint: disable = W0613, C0103, R0903, R0913, R0914


BAR_SIZE = ['1 sec', '5 secs', '10 secs', '15 secs', '30 secs',
            '1 min', '2 mins', '3 mins', '5 mins', '10 mins', '15 mins', '20 mins', '30 mins',
            '1 hour', '2 hours', '3 hours', '4 hours', '8 hours',
            '1 day', '1 week', '1 month']

# Needs to be a string in the form '3 D'
DURATION_STRING = ['S', 'D', 'W', 'M', 'Y']


def getLimits():
    '''
    Tell a little bit about the getHistory call
    '''
    lmt = ''.join(['We are only interested, in this app, in chart info, aka historical data.\n',
                 'IB will issue a Pacing violation when:...\n',
                 '       Making identical historical data requests within 15 seconds.\n',
                 '       Making six or more historical data requests for the same Contract',
                 '       Exchange and Tick Type within two seconds.\n',
                 '       Making more than 60 requests within any ten minute period.\n\n',
                 'Data older than 6 months for candles of 1 minute or less in unavailable.\n',
                 '      No hard limit for older data for intervals greater than 1 min (so they',
                 '      say in spite of the docs)\n'])
    return lmt


def ni(i, minutes='minutes'):
    '''
    Utility to normalize the the interval parameter.
    :params i:
    '''

    # Setting the unpython like baby sitter because I am changing this method and I need to
    # find any discrepencies
    if not isinstance(i, int):
        raise ValueError('For ib.ni minutes must be an int')
    durdict = {1: '1 min', 2: '2 mins', 3: '3 mins', 5: '5 mins', 10: '10 mins',
               15: '15 mins', 20: '20 mins', 30: '30 mins', 60: '1 hour'}
    resamp = False
    if i in durdict.keys():
        return (resamp, (durdict[i], i, i))
    resamp = True
    if isinstance(i, int):
        return (resamp, ('1 min', 1, i))
    return (False, ('', 0, 0))


def validateDurString(s):
    '''
    Utility method to enforce an IB requirement.
    '''
    d = ['S', 'D', 'W', 'M', 'Y']
    sp = s.split()
    if len(sp) != 2:
        return False
    if sp[1] not in d:
        return False
    try:
        int(sp[0])
    except ValueError:
        return False
    return True


class TestClient(EClient):
    '''
    Inherit from the sample code
    '''

    def __init__(self, wrapprr):
        EClient.__init__(self, wrapprr)
        self.storage = queue.Queue()


class TestWrapper(wrapper.EWrapper):
    '''
    Inherit from the sample code.
    '''
    def __init__(self):
        wrapper.EWrapper.__init__(self)

        self.counter = 0
        self.data = []

    def contractDetails(self, reqId, contractDetails):
        '''
        Overriden method that returns to us all the contract details from the instrument.
        I think if we receive this without asking for it, it means IB failed to locate a single
        match for a requested instrument
        '''
        pass

    def error(self, reqId: TickerId, errorCode: list, errorString: str):
        '''
        Overriden method to return all errors to us
        '''
        if reqId != -1:
            logging.error(f"Error: {reqId} {errorCode} {errorString}")

    def historicalData(self, reqId: int, bar):
        '''
        Overriden Callback from EWrapper. Drops off data 1 bar at a time in each call.
        '''
        if self.counter == 0:
            dat = []
            dat.append(bar)
        self.counter = self.counter + 1
        self.data.append([bar.date, bar.open, bar.high,
                          bar.low, bar.close, bar.volume])

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        '''
        Overriden callback is called when all bars have been delivered to historicalData provided
        keepUpToDate=False, parameter in reqHistoricalData.
        '''

        super().historicalDataEnd(reqId, start, end)
        df = pd.DataFrame(self.data,
                          columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        self.storage.put(df)


class TestApp(TestWrapper, TestClient):
    '''
    My very own double
    '''
    def __init__(self, port, cid, host):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapprr=self)
        self.port = port
        self.cid = cid
        self.host = host
        # ! [socket_init]

        self.started = False

    def start(self):
        '''
        Run the thread
        '''
        if self.started:
            return
        self.started = True

        self.historicalDataOperations_req()

    def historicalDataOperations_req(self):
        '''Overridder'''
        # self.reqHistoricalData(4103, ContractSamples.EuropeanStock(), queryTime,
        #                        "10 D", "1 min", "TRADES", 1, 1, False, [])

    def getHistorical(self, symbol, end, dur, interval, exchange='NASDAQ'):
        '''
        :params end: datetime object for the end time requested
        :params dur: a string for how long before end should the chart begin "1 D"
        :params interval: candle len
        '''
        # get value for exclue afterhours, 1==RTH only
        AFTERHOURS = 1 if excludeAfterHours() else 0

        if not validateDurString(dur):
            logging.warning("Duration must be formatted like '3 D' using S, D, W, M, or Y")
            return pd.DataFrame()

        if not isinstance(end, dt.datetime):
            logging.warning("end must be formatted as a datetime object")
            return pd.DataFrame()

        if interval not in BAR_SIZE:
            logging.warning('Bar size ({}) must be one of: {}'.format(interval, BAR_SIZE))
            return pd.DataFrame()

        # app = Ib()
        host = "127.0.0.1"
        port = self.port
        clientId = self.cid
        self.connect(host, port, clientId)

        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.primaryExchange = exchange

        # app.reqContractDetails(10, contract)

        timeStr = end.strftime('%Y%m%d %H:%M:%S')
        # self.reqHistoricalData(18002, ContractSamples.ContFut(), timeStr,
        #                        "1 Y", "1 month", "TRADES", 0, 1, False, []);
        # queryTime = DateTime.Now.AddMonths(-6).ToString("yyyyMMdd HH:mm:ss");
        self.reqHistoricalData(port, contract, timeStr, dur,
                               interval, "TRADES", AFTERHOURS, 1, False, [])
        # client.reqHistoricalData(4002, ContractSamples.EuropeanStock(), queryTime,
        #                          "10 D", "1 min", "TRADES", 1, 1, false, null);

        # self.run()
        thread = Thread(target=self.run)
        thread.start()

        setattr(self, "_thread", thread)

        try:
            x = self.storage.get(timeout=10)
            x.set_index('date', inplace=True)
            return x
        except queue.Empty as ex:
            logging.error(f"Request came back empty {ex.__class__.__name__}")
            logging.error(ex)
            return pd.DataFrame()


def getib_intraday(symbol, start=None, end=None, minutes=1, showUrl='dummy', key=None):
    '''
    An interface API to match the other getters. In this case its a substantial
    dumbing down of the capabilities to our one specific need. Output will be resampled
    if necessary to return a df with intervals 1~60 minutes
    :params symbol: The stock to get
    :params start: A timedate object or time string for when to start. Defaults to the most recent
        weekday at open.
    :params end: A timedate object or time string for when to end. Defaults to the most recent biz
        day at close
    :params minutes: The length of the candle, 1~60 minutes. Defaults to 1 minute
    :return (length, df):A DataFrame of the requested stuff and its length
    '''
    apiset = QSettings('zero_substance/stockapi', 'structjour')
    if not apiset.value('gotibapi', type=bool):
        return {'message': 'ibapi is not installed', 'code': 666}, pd.DataFrame(), None
    logging.info('***** IB *****')
    biz = getLastWorkDay()
    if not end:
        end = pd.Timestamp(biz.year, biz.month, biz.day, 16, 0)
    if not start:
        start = pd.Timestamp(biz.year, biz.month, biz.day, 9, 30)
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    dur = ''
    fullstart = end
    fullstart = fullstart - pd.Timedelta(days=5)
    if start < fullstart:
        delt = end - start
        fullstart = end - delt

    if (end - fullstart).days < 1:
        if ((end - fullstart).seconds // 3600) > 8:
            dur = '2 D'
        else:
            dur = f'{(end-fullstart).seconds} S'
    elif (end - fullstart).days < 7:
        dur = f'{(end-fullstart).days + 1} D'
    else:
        dur = f'{(end-fullstart).days} D'
        # return 0, pd.DataFrame([], [])

    # if the end = 9:31 and dur = 3 minutes, ib will retrieve a start of the preceding day @ 15:58
    # This is unique behavior in implemeted apis. We will just let ib do whatever and cut off any
    # data prior to the requested data. In that we get no after hours, a request for 7 will begin
    # at 9:30 (instead of the previous day at 1330)

    symb = symbol
    (resamp, (interval, minutes, origminutes)) = ni(minutes)

    # ib = TestApp(7496, 7878, '127.0.0.1')
    # ib = TestApp(4002, 7979, '127.0.0.1')
    x = IbSettings()
    ibs = x.getIbSettings()
    if not ibs:
        return 0, pd.DataFrame(), None
    ib = TestApp(ibs['port'], ibs['id'], ibs['host'])
    df = ib.getHistorical(symb, end=end, dur=dur, interval=interval, exchange='NASDAQ')
    lendf = len(df)
    if lendf == 0:
        return 0, df, None

    # Normalize the date to our favorite format
    df.index = pd.to_datetime(df.index)
    if resamp:
        srate = f'{origminutes}T'
        df_ohlc = df[['open']].resample(srate).first()
        df_ohlc['high'] = df[['high']].resample(srate).max()
        df_ohlc['low'] = df[['low']].resample(srate).min()
        df_ohlc['close'] = df[['close']].resample(srate).last()
        df_ohlc['volume'] = df[['volume']].resample(srate).sum()
        df = df_ohlc.copy()

    maDict = movingAverage(df.close, df, end)

    if start > df.index[0]:
        msg = f"Cutting off beginning: {df.index[0]} to begin at {start}"
        logging.info(msg)
        df = df.loc[df.index >= start]
        if not df.high.any():
            logging.warning('All data has been removed')
            return 0, pd.DataFrame(), None
        for ma in maDict:
            maDict[ma] = maDict[ma].loc[maDict[ma].index >= start]
    removeMe = list()
    for key in maDict:
        # VWAP is a reference that begins at market open. If the open trade precedes VWAP
        # we will exclude it from the chart. Other possibilities: give VWAP a start time or
        # pick an arbitrary premarket time to begin it. The former would be havoc to implement
        # the latter probably better but inaccurate; would not reflect what the trader was using
        # Better suggestions?
        if key == 'vwap':
            if len(maDict['vwap']) < 1 or (df.index[0] < maDict['vwap'].index[0]):
                removeMe.append(key)
                # del maDict['vwap']
        else:
            if len(df) != len(maDict[key]):
                removeMe.append(key)
                # del maDict[key]
    for key in removeMe:
        del maDict[key]

    ib.disconnect()
    return len(df), df, maDict


def isConnected():
    '''Call TestApp.isConnected and return result'''
    x = IbSettings()
    ibs = x.getIbSettings()
    if not ibs:
        return None
    host = ibs['host']
    port = ibs['port']
    clientId = ibs['id']
    ib = TestApp(port, clientId, host)
    ib.connect(host, port, clientId)
    connected = ib.isConnected()
    if connected:
        ib.disconnect()
    return connected


def main():
    '''test run'''
    start = dt.datetime(2019, 10, 10, 7, 0)
    end = dt.datetime(2019, 10, 10, 17, 0)
    minutes = 15
    x, ddf, maDict = getib_intraday('ROKU', start, end, minutes)
    print(x, ddf)


def notmain():
    '''Run some local code'''
    print("We are connected? ", isConnected())


if __name__ == '__main__':
    main()
    # notmain()
    # print(isConnected())
