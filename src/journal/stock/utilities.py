'''
Local utility functions shared by some stock modules and test code.

@author: Mike Petersen

@creation_date: 2019-01-17
'''
# pylint: disable = C0103
import datetime as dt
from PyQt5.QtCore import QSettings

def getLastWorkDay(d=None):
    '''
    Retrieve the last biz day from today or from d if the arg is given. Holidays are ignored
    :params d: A datetime object.
    :return: A datetime object of the last biz day.
    '''
    now = dt.datetime.today() if not d else d
    deltDays = 0
    if now.weekday() > 4:
        # deltDays = now.weekday() - 4
        # Just todauy TODO
        deltDays = now.weekday() - 3
    bizday = now - dt.timedelta(deltDays)
    return bizday

def getPrevTuesWed(td):
    '''
    Utility method to get a probable market open day prior to td. The least likely
    closed days are Tuesday and Wednesday. This will occassionally return  a closed
    day but wtf.
    :params td: A Datetime object
    '''
    deltdays = 7
    if td.weekday() == 0:
        deltdays = 5
    elif td.weekday() < 3:
        deltdays = 0
    elif td.weekday() < 5:
        deltdays = 2
    else:
        deltdays = 4
    before = td - dt.timedelta(deltdays)
    return before

class IbSettings:
    def __init__(self):
        self.settings = QSettings('zero_substance/stockapi', 'structjour')
        p = self.settings.value('APIPref')
        if p:
            p = p.replace(' ', '')
            self.preferences = p.split(',')
        else:
            self.preferences = ['ib', 'bc', 'av', 'iex']
        self.setIbStuff()


    def setIbStuff(self):
        pref = self.preferences
        if 'ib' in pref:
            ibreal = self.settings.value('ibRealCb', False, bool)
            ibPaper = self.settings.value('ibPaperCb', False, bool)
            ibpref = self.settings.value('ibPref')
            if ibreal:
                self.ibPort = self.settings.value('ibRealPort', 7496, int)
                self.ibId = self.settings.value('ibRealId', 7878, int)
            elif ibPaper:
                self.ibPort = self.settings.value('ibPaperPort', 4001, int)
                self.ibId = self.settings.value('ibPaperId', 7979, int)

    def getIbSettings(self):
        #TODO abstrast host like port and id-- set it in the stockapi dialog
        d = {'port': self.ibPort,
                'id': self.ibId,
                'host': '127.0.0.1'}
        return d



def notmain():
    '''run some local code'''
    now = dt.datetime.today()
    fmt = "%A, %B %d   %w"
    print()
    for i in range(7):
        d = now - dt.timedelta(i)
        print(f'{d.strftime(fmt)} ... : ... {getLastWorkDay(d).strftime(fmt)}')
        print(d.isoweekday())
if __name__ == '__main__':
    notmain()
