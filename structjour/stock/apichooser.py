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
Choose which API intraday call to get chart data based on rules
@author: Mike Petersen

@creation_date: 3/3/20
'''
import datetime as dt
import logging
import pandas as pd
import requests
from structjour.stock.utilities import checkForIbapi, getLimitReached, ManageKeys
from structjour.stock import myalphavantage as mav
from structjour.stock import mybarchart as bc
from structjour.stock import myFinhub as fh
from structjour.stock.mytiingo import get_intraday as get_tgo_intraday
if checkForIbapi():
    from structjour.stock import myib as ib


class APIChooser:
    def __init__(self, apiset, orprefs=None, keydict={}):
        '''
        The currenly supported apis are barchart, alphavantage, finnhub,
        tiingo and ibapi
        These are represented by the tokens bc, av, fh, tgo and ib
        :params apiset: QSettings with key 'APIPref'
        :params orprefs: List: Override the api prefs in settings
        '''
        self.apiset = apiset
        self.orprefs = orprefs
        self.preferences = self.getPreferences()
        self.api = self.preferences[0]
        self.keydict = keydict
        if len(self.keydict) == 0:
            mk = ManageKeys()

            self.keydict = mk.getKeyDict()


    def getPreferences(self):
        if self.orprefs:
            return self.orprefs.copy()
        p = self.apiset.value('APIPref')
        if p:
            p = p.replace(' ', '')
            p = p.split(',')
        else:
            p = [None]
        return p

    def apiChooserList(self, start, end, api=None):
        '''
        Given the current list of apis as av, bc, fh and ib, determine if the given api will
            likely return data for the given times.
        :params start: A datetime object or time stamp indicating the intended start of the chart.
        :params end: A datetime object or time stamp indicating the intended end of the chart.
        :params api: Param must be one of mav, bc, fh or ib. If given, the return value in
            (api, x, x)[0] will reflect the bool result of the api
        :return: (bool, rulesviolated, suggestedStocks) The first entry is only valid if api is
            an argument.

        '''
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        # Need a naive time showing NewYorkTime right now
        ne = pd.Timestamp.now("US/Eastern")
        n = pd.Timestamp(ne.year, ne.month, ne.day, ne.hour, ne.minute, ne.second)

        violatedRules = []
        suggestedApis = self.getPreferences()
        if len(suggestedApis) == 0:
            self.api = None
            return (False, ['No stock Api is selected'], [])
        # nopen = dt.datetime(n.year, n.month, n.day, 9, 30)
        nclose = dt.datetime(n.year, n.month, n.day, 16, 30)

        # Rule 1 Barchart will not return todays data till 16:30
        # Rule 1a Barchart will not return yesterdays data after 12 till 1630
        tradeday = pd.Timestamp(start.year, start.month, start.day)
        todayday = pd.Timestamp(n.year, n.month, n.day)
        yday = todayday - pd.Timedelta(days=1)
        y = pd.Timestamp(yday.year, yday.month, yday.day, 11, 59)
        if tradeday == todayday and n < nclose and 'bc' in suggestedApis:
            suggestedApis.remove('bc')
            violatedRules.append(
                'Barchart free data will not return todays data till 16:30')
        if tradeday == yday and end > y and n < nclose and 'bc' in suggestedApis:
            suggestedApis.remove('bc')
            violatedRules.append(
                'Barchart free data will not yesterdays data after 12 till today at  16:30')

        # Rule 2 No support any charts greater than 7 days prior to today for Alphavantage
        # Rule 2 No support any charts greated than 7 days prior to tody for World Trade Data
        # Rule 2 No support any charts greater than 30 days for Barchart
        if n > start:
            delt = n - start
            if delt.days > 31 and 'bc' in suggestedApis:
                suggestedApis.remove('bc')
                lastday = n - pd.Timedelta(days=31)
                violatedRules.append('Barchart data before {} is unavailable.'.format(lastday.strftime("%b %d")))
            if delt.days > 6 and 'av' in suggestedApis:
                suggestedApis.remove('av')
                lastday = n - pd.Timedelta(days=6)
                violatedRules.append('AlphaVantage data before {} is unavailable.'.format(
                    lastday.strftime("%b %d")))

        # Rule 3 Don't call ib if the library is not installed
        # Rule 4 Don't call ib if its not connected
        if self.apiset.value('gotibapi', type=bool):
            if 'ib' in suggestedApis and not ib.isConnected():
                suggestedApis.remove('ib')
                violatedRules.append('IBAPI is not connected.')
        elif 'ib' in suggestedApis:
            suggestedApis.remove('ib')
            violatedRules.append('IBAPI is not installed')

        # Rule 5 No data is available for the future
        if start > n:
            suggestedApis = []
            violatedRules.append('No data is available for the future.')
        # Rule No 6 Don't call barchart if there is no apikey in settings
        # Rule No 6 Don't call alphavantage if there is no apikey in settings
        # Rule No 6 Don't call finnhub if there is no api key in settings
        # Rule No 6 Don't call tiingo if there is no api key in settings
        # mk = ManageKeys()
        # bc_key = mk.getKey('bc')
        # av_key = mk.getKey('av')
        # fh_key = mk.getKey('fh')
        if not self.keydict['bc'] and 'bc' in suggestedApis:
            suggestedApis.remove('bc')
            violatedRules.append('There is no apikey in the database for barchart')
        if not self.keydict['av'] and 'av' in suggestedApis:
            suggestedApis.remove('av')
            violatedRules.append('There is no apikey in the database for alphavantage')

        if not self.keydict['fh'] and 'fh' in suggestedApis:
            suggestedApis.remove('fh')
            violatedRules.append('There is no apikey in the database for finnhub')
        if not self.keydict['tgo'] and 'tgo' in suggestedApis:
            suggestedApis.remove('tgo')
            violatedRules.append('There is no apikey in the database for tiingo')

        # Rule No 7 API limit has been reached [bc, av, fh]
        deleteme = []
        for token in suggestedApis:
            if token == 'ib' or token is None:
                continue
            if getLimitReached(token, self.apiset):
                deleteme.append(token)
                violatedRules.append(f'You have reached your quota for {token}')
        for token in deleteme:
            suggestedApis.remove(token)
        api = api in suggestedApis if api else False

        self.api = suggestedApis[0] if suggestedApis else None
        self.violatedRules = violatedRules

        return(api, violatedRules, suggestedApis)

    def apiChooser(self):
        '''
        Get a data method as set in self.api
        :return the method
        '''
        # self.api = api
        if self.api == 'bc':
            # retrieves previous biz day until about 16:30
            return bc.getbc_intraday
        if self.api == 'av':
            return mav.getmav_intraday
        if self.api == 'ib':
            return ib.getib_intraday
        if self.api == 'fh':
            return fh.getFh_intraday
        if self.api == 'tgo':
            return get_tgo_intraday

        return None

    def get_intraday(self, symbol, start=None, end=None, minutes=5, showUrl=False):
        api, vr, suggested = self.apiChooserList(start, end)
        for token in suggested:
            self.api = token
            try:
                dakey = self.keydict[self.api] if self.api in self.keydict else None
                meta, df, ma = self.apiChooser()(symbol, start, end, minutes, key=dakey)
            except requests.exceptions.ConnectionError as ex:
                message = "Please check your internet connection\n" + str(ex)

                meta = {'code': 666, 'message': message}
                logging.error(message)
                return meta, pd.DataFrame, None
            if not df.empty:
                return meta, df, ma
        msg = f'Failed to retrieve data from APIS: {self.preferences}'
        return {'code': 666, 'message': msg}, pd.DataFrame(), None
