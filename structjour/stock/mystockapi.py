import logging
import pandas as pd


class StockApi:
    def trimit(self, df, maDict, start, end, meta):
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
                msg = f"You have sliced off all the data with the end date {end}"
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