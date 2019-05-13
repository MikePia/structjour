'''
@author: Mike Petersen

@creation_date: 2019-01-17
'''
import datetime as dt
import os
import pickle
import types
import unittest

from PyQt5.QtCore import QSettings

from journal.stock import utilities as util
# pylint: disable = C0103


class PickleSettings:
    '''A utility to store and restore settings for use in testing. Be careful not to lose data.'''
    def __init__(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        self.settings = QSettings('zero_substance', 'structjour') 
        self.apiset = QSettings('zero_substance/stockapi', 'structjour')
        self.setkeys = []
        self.setvals = []
        self.apisetkeys = []
        self.apisetvals = []

        self.name = os.path.join(ddiirr, 'pickleset.zst')
        print(self.name)

    def initializeSettings(self):
        self.settings.clear()
        self.apiset.clear()

    def removePickle(self):
        if os.path.exists(self.name):
            os.remove(self.name)

    def initializeVars(self):
        self.setkeys = []
        self.setvals = []
        self.apisetkeys = []
        self.apisetvals = []


    def storeSettings(self, replacePickle=False):
        if os.path.exists(self.name):
            if not replacePickle:
                return
        self.initializeVars()
        self.setkeys = self.settings.allKeys()
        for k in self.setkeys:
            self.setvals.append(self.settings.value(k))

        self.apisetkeys = self.apiset.allKeys()
        for k in self.apisetkeys:
            self.apisetvals.append(self.apiset.value(k))

        setsnkeys = [self.setkeys, self.setvals, self.apisetkeys, self.apisetvals]

        with open(self.name, "wb") as f:
            '''Cannot pickle qsettings objects- so we pickle a list'''
            pickle.dump((setsnkeys), f)

    def restoreSettings(self):
        if os.path.exists(self.name):
            with open(self.name, "rb") as f:
                setsnkeys = pickle.load(f)
                for k, v in zip(setsnkeys[0], setsnkeys[1]):
                    self.settings.setValue(k, v)
            
                for k2, v2 in zip(setsnkeys[2], setsnkeys[3]):
                    self.apiset.setValue(k2, v2)

            os.remove(self.name)
        else:
            print(f'No pickle found at {self.name}')

class TestUtilities(unittest.TestCase):
    '''Test functions in the stock.utilities module'''

    def __init__(self,  *args, **kwargs):
        super(TestUtilities, self).__init__(*args, **kwargs)
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        self.p = os.path.realpath(ddiirr)

    def test_getLastWorkDay(self):
        '''run some local code'''
        now = dt.datetime.today()
        fmt = "%a, %B %d"
        
        print()
        for i in range(7):
            d = now - dt.timedelta(i)
            dd = util.getLastWorkDay(d)

            print(f'{d.strftime(fmt)} ... : ... {util.getLastWorkDay(d).strftime(fmt)}')
            self.assertTrue(dd.isoweekday() < 6)
            self.assertTrue(dd.isoweekday() > 0)

    def test_setDB(self):
        '''
        Test the method ManageKeys.setDB. The location depends on having the journal location set.
        This method is called by init y default.
        '''
        t = PickleSettings()
        t.storeSettings()
        t.initializeSettings()
        settings = QSettings('zero_substance', 'structjour')
        apiset = QSettings('zero_substance/stockapi', 'structjour')

        settings.setValue('journal', self.p)
        mk = util.ManageKeys(create=True)
        l = apiset.value('dbsqlite')
        self.assertTrue(os.path.exists(l))
        os.remove(l)

        t.initializeSettings()
        settings.setValue('journal', self.p)
        mk = util.ManageKeys(create=True)
        ll = apiset.value('dbsqlite')
        self.assertTrue(l == ll)
        os.remove(ll)
        # self.assertEqual(l, ll)

        t.initializeSettings()
        # settings.setValue('journal', self.p)
        mk = util.ManageKeys(create=True)
        lll = apiset.value('dbsqlite')
        self.assertFalse(lll)

        t.restoreSettings()
        print(apiset.allKeys())
        print(settings.allKeys())
        # self.assertTrue(os)
        print()

    def test_updateKey(self):
        t = PickleSettings()
        t.storeSettings()
        t.initializeSettings()
        settings = QSettings('zero_substance', 'structjour')
        apiset = QSettings('zero_substance/stockapi', 'structjour')

        settings.setValue('journal', self.p)
        mk = util.ManageKeys(create=True)
        mk.updateKey('bc', 'Its the end of the world')
        mk.updateKey('av', 'as we know it')
        bck = mk.getKey('bc')
        avk = mk.getKey('av')
        self.assertTrue(bck == 'Its the end of the world')
        self.assertTrue(avk == 'as we know it')

        l = apiset.value('dbsqlite')

        t.restoreSettings()
        print(apiset.allKeys())
        print(settings.allKeys())
        os.remove(l)

        # self.assertTrue(os)
        mk = util.ManageKeys()
        print(mk.getKey('bc'))

    def test_ibSettings(self):
        t = PickleSettings()
        t.storeSettings()
        t.initializeSettings()

        apiset = QSettings('zero_substance/stockapi', 'structjour')
        apiset.setValue('ibRealCb', True)
        apiset.setValue('ibPaperCb', False)
        ibs = util.IbSettings()
        defport = 7496
        defid = 7878
        defhost = '127.0.0.1'
        p = ibs.getIbSettings()
        self.assertEqual(defhost, p['host'])
        self.assertEqual(defid, p['id'])
        self.assertEqual(defport, p['port'])

        t.restoreSettings()
        print(apiset.allKeys())


def notmain():
    '''Run some local code'''
    # t = TestUtilities()
    # t.test_getLastWorkDay()
    # t.test_setDB()
    # t.test_updateKey()
    # t.test_ibSettings()
    # t = PickleSettings()
    # t.storeSettings()
    # t.initializeSettings()
    # t.restoreSettings()
    # t.removePickle()
    t = PickleSettings()
    # t.storeSettings()
    # t.initializeSettings()
    t.restoreSettings()

def main():
    '''
    test discovery is not working in vscode. Use this for debugging. Then run cl python -m unittest
    discovery
    '''
    f = TestUtilities()
    for name in dir(f):
        if name.startswith('test'):
            attr = getattr(f, name)
            if isinstance(attr, types.MethodType):
                attr()

if __name__ == '__main__':
    notmain()
    # main()
