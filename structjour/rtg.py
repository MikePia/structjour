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
Random Trade Generator for testing only

@re-created_on Feb 24, 2020

@author: Mike Petersen
'''

import logging
import os
import random

import pandas as pd

from PyQt5.QtCore import QSettings

# from structjour.colz.finreqcol import FinReqCol


class RTG:
    def __init__(self, settings=None, db=None, overnight=0):
        '''
        :params overnight:Percentage of trades to include overnight transaction.
        '''
        self.overnight = overnight
        if settings:
            self.settings = settings
        else:
            self.settings = QSettings("zero_substance", "structjour")
        if db is not None:
            self.db = db
        else:
            self.db = self.settings.value('tradeDb')
        self.testfiles = []

    def makeRandomDASImport(self, numTrades, start, outfile=None, strict=False, overwrite=True):
        start = pd.Timestamp(start)
        df = self.getRandomTradeDF(numTrades=numTrades, start=start, strict=strict)

        if outfile:
            outfile, ext = os.path.splitext(outfile)
            outfile = f'''{outfile}_{start.strftime('%Y%m%d')}{ext}'''
            d = os.path.dirname(outfile)
            if not overwrite and os.path.exists(outfile):
                return outfile, df
            if os.path.exists(d):
                df.to_csv(outfile, index=False)
            else:
                logging.error(f'Failed to save file. Directory {d} does not exist')

        return outfile, df

    def makeOvernight(self, df):

        if len(df) > 2 and random.randint(0, 99) < self.overnight:
            r = random.random()
            delrow = df.index[0] if r < .5 else df.index[-1]
            df.drop(delrow, inplace=True)
        return df

    def saveSomeTestFiles(self, dates, outdir, outfile='DASrandomTrades.csv', strict=False, overwrite=False):
        '''
        Create DAS export like random trades.csv files for testing purposes
        :params dates: Create one file for each date. Date will be appended to the name
        :parmas outdir: The directory to place the files
        :params outfile: The name for the file. Date will be appended to each file
        :params outfile: The base name for the files. Final name will be {outfile}_yyyymmdd{ext}
        :params strict: If False, files will include Balance and Date fields
        :params overwrite: If False files already exist will be overwritten. Otherwise writing the file is quietly skipped.
        '''
        savedfiles = []
        for date in dates:
            date = pd.Timestamp(date)
            filename = os.path.join(outdir, outfile)
            filename, df = self.makeRandomDASImport(random.randint(3, 5), date, outfile=filename, strict=strict, overwrite=overwrite)
            savedfiles.append(filename)
        return savedfiles

    def getRandomTradeDF(self, numTrades=None, start='2018-06-06 09:30:00', strict=False):
        '''
        Creates a day of trades in the same form with the required columns from a DAS export
        plus a Balance and Date column. Use strict=True to remove them
        :numTrades: The number of trades in the statemnt
        :start: The earliest possible trade start time.
        '''

        if numTrades is None:
            numTrades = random.randint(1, 10)
        start = pd.Timestamp(start)
        df = pd.DataFrame()
        exclude = []
        for i in range(numTrades):
            tdf, start = self.randomTradeGenerator2(earliest=start,
                                            pdbool=True, exclude=exclude)
            if strict is True:
                tdf = tdf.drop(['Balance', 'Date'], axis=1)
            df = df.append(tdf)
            exclude.append(tdf.Symb.unique()[0])

        df.reset_index(drop=True, inplace=True)
        return df

    def randomTradeGenerator2(self, earliest=pd.Timestamp('2019-01-01 09:30:00'),
                            pdbool=True, exclude=None):
        '''
        Create a passable DAS import
        :params earliest: Transaction progress in time with earliest as the easliest possible trade
                        except for before HOLDs.
        :params pdbool: Setting to True will cause the return to be a DataFrame instead of an array.
                        Deprecated. Changed to allways return a dataframe
        :params exclude: A list of symbols to exclude as candidates for this trade
        :return pd.DataFrame:  DataFrame or list of transactions making up a single trade.
        '''
        earliest = pd.Timestamp(earliest)
        latest = earliest
        start = earliest
        nowtime = start
        numTrades = self.getNumTrades(maxt=10)
        trade = list()
        prevBal = 0
        price = 0
        long = True
        # duration = ''
        sumtotal = 0
        account = self.getAccount()
        # account = 'U000000'
        ticker = self.getTicker(exclude=exclude)
        daDate = pd.Timestamp(start.year, start.month, start.day)
        cloid = -1
        average = 0
        oc = ''

        for i in range(numTrades):
            firsttrade = True if i == 0 else False
            nexttime = self.getRandomFuture(nowtime)
            latest = nexttime
            pl = 0
            side = self.getSide(firsttrade=firsttrade)
            if firsttrade:
                # Note: not using these yet. If we start, may need to add a test identifier and convert to string
                cloid = random.randint(-999999999999, -100000000000)

                if side == 'S' or side.find('-') >= 0:
                    long = False
                price = self.getPrice()
                average = price
                oc = 'O'
            else:
                price = self.getPrice(price, long)

            time = nowtime.strftime("%H:%M:%S")
            daDate = pd.Timestamp(daDate.year, daDate.month, daDate.day, nowtime.hour, nowtime.minute, nowtime.second)
            cloid += 1

            if i == numTrades - 1:
                side = 'S' if prevBal >= 0 else 'B'
                # pl = self.getPL()
                pl = (average - price) * -prevBal
                trade.append([time, ticker, side, price, -prevBal, 0, account, pl, daDate, cloid, average, 'C'])
                sumtotal = sumtotal + pl
                prevBal = 0
                break
            else:
                qty = random.randint(1, 500)
                qty = -qty if (side == 'S' or side == 'HOLD-B') else qty

                # Check for flippers
                if long and (prevBal + qty) < 0:
                    long = False
                elif not long and (prevBal + qty) > 0:
                    long = True
                if (long is True and side == 'B') or (long is not True and side != 'B'):
                    # An opener -- adjust the average
                    # Average = ((PrevAvg * PrevBal) + (Qty * Price))/ Balance
                    average = ((average * prevBal) + (qty * price)) / (prevBal + qty)
                    oc = 'O'

                else:
                    # a closer-- figure the pl
                    #  pl = (average - price) * qty
                    pl = (average - price) * qty
                    oc = 'C'

                trade.append([time, ticker, side, price, qty, prevBal + qty, account, pl, daDate, cloid, average, oc])
                sumtotal = sumtotal + pl
                prevBal = prevBal + qty
                if prevBal == 0:
                    # We are coincidentally at 0 balance. Trade is over. Must be a hotkey mistake ;-)
                    break

            nowtime = nexttime
        # duration = nowtime - start

        tradedf = pd.DataFrame(data=trade, columns=['Time', 'Symb', 'Side', 'Price', 'Qty',
                                                    'Balance', 'Account', 'P / L', 'Date', 'Cloid', 'Average', 'OC'])
        tradedf['Commission'] = float('nan')
        tradedf = self.makeOvernight(tradedf)
        return tradedf, latest

    def getPrice(self, price=None, long=True):
        if price is None:
            price = random.randint(3, 300) + random.randint(0, 99) / 100
            return price

        change = (random.random() / 70)
        upordown = random.random()
        if long and upordown > .62:
            change *= -1
        elif not long and upordown > .38:
            change *= -1

        return price + (price * change)

    def getNumTrades(self, maxt=8):
        '''
        Return a number between 2 and 8 by default
        '''
        t = random.randint(2, maxt)
        return t

    def getAccount(self):
        '''
        Get a randoms account real or sim
        '''
        real = 'U000000'
        sim = 'TRIB0000'
        percentReal = .75
        r = random.random()
        acct = real if r < percentReal else sim
        return acct

    def getTicker(self, exclude=None):
        '''
        Get a random ticker symbol
        :exclude: A list of tickers to exclude from consideration.
        '''
        tickers = ['SQ', 'AAPL', 'TSLA', 'ROKU', 'NVDA', 'NUGT', 'MSFT', 'CAG', 'ACRS', 'FRED', 'PCG',
                'AMD', 'GE', 'NIO', 'AMRN', 'FIVE', 'BABA', 'BPTH', 'Z', ]
        tick = tickers[random.randint(0, len(tickers) - 1)]
        if exclude and tick in exclude:
            if not set(tickers).difference(set(exclude)):
                # We could make up some random letters here if this ever ....-- or include more
                raise ValueError("You have excluded every stock in the method")
            return self.getTicker(exclude=exclude)
        return tick

    def getRandomFuture(self, earliest=pd.Timestamp('2019-01-01 09:30:00')):
        '''
        Get a time that is in the future a random amount of seconds from earliset
        '''
        rsec = random.randint(45, 1500)
        nextt = earliest + pd.Timedelta(seconds=rsec)
        return nextt

    def getSide(self, firsttrade=False):
        '''
        Get a random distribution of 'B', 'S', 'HOLD+', 'HOLD-'. Set the probabilities here.
        HOLDs provide the weirdest exceptions. They should be relatively likely for tests.
        '''
        s = random.random()
        side = 'B'if s < .55 else 'S'
        return side

    def getPL(self):
        '''
        Get a random dollar amount
        '''
        amnt = random.random()
        upordown = random.random()
        upordown = 1 if upordown > .4 else -1
        multiplier = random.randint(2, 200)
        return amnt * upordown * multiplier


def notmain():
    '''Run some local code'''
    pass


def localstuff():
    outdir = 'C:/python/E/structjour/test/out'
    rtg = RTG()
    # rtg.makeRandomDASImport(7, start='20200202', outfile=outfile, strict=True)
    dates = ['20200203 09:35', '20200204 10:02', '20200205 13:59', '20200206 07:30', '20200207 05:58']
    rtg.saveSomeTestFiles(dates, outdir)


def reallylocal():
    rtg = RTG()
    price = None
    for i in range(10):
        price = rtg.getPrice(price=price)
        print(price)


if __name__ == '__main__':
    # notmain()
    localstuff()
    # reallylocal()
