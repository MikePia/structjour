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
Updating this module from an outside utility to a tool that structjour uses.
By default strategies are empty for new users. All strategies must be added
by the user using the strategy browser. Note that the strategies in statisticsHub
are generated from the strategies named in tradeObjects only
'''
from structjour.models.meta import ModelBase
from structjour.models.strategymodels import Source, Strategy, Description, Images, Links

class StrategyCrud:
    '''
    Implement the required methods of structjour.strategy.strategies.Strategy with SA.
    '''
    def getId(self, name):
        if not name: return []
        q = Strategy.getId(name)
        return q

    def addStrategy(self, name, preferred=1):
        Strategy.addStrategy(name, preferred)

    def getStrategy(self, name=None, id=None):
        s = Strategy.getStrategy(name, id)
        if not s:
            return None
        return s.name

    def removeStrategy(self, name):
        Strategy.removeStrategy(name)

    def getStrategies(self):
        strats = Strategy.getStrategies()
        # manipulate this to match the return from the old DBAPI method
        strats = [[x.id, x.name, x.preferred] for x in strats]
        return strats

    def getPreferred(self, pref=1):
        strats = Strategy.getPreferred(pref)
        # Manipulate results to match DBAPI method
        strats = [[x.id, x.name, x.preferred] for x in strats]
        return strats

    def setPreferred(self, name, pref):
        Strategy.setPreferred(name, pref)

    def setLink(self, name, url):
        return Links.setLink(name, url)

    def getLinks(self, name):
        '''
        Get links for the strategey 'name'
        :return: list<string>: Get a list of urls
        '''
        if not name: return []
        links=Links.getLinks(name)
        xlist = [link.link for link in links]
        return xlist

    def removeLink(self, name, url):
        Links.removeLink(name, url)

    def getImage(self, strat, widget):
        obj =  Images.getImage(strat, widget)
        return obj[0].name if obj else None

    def getImage1(self, strat):
        return self.getImage(strat, 'chart1')

    def getImage2(self, strat):
        return self.getImage(strat, 'chart2')

    def setImage1(self, strat, name):
        Images.setImage(strat, name, 'chart1')

    def setImage2(self, strat, name):
        Images.setImage(strat, name, 'chart2')

    def removeImage1(self, strat):
        Images.removeImage(strat, 'chart1')

    def removeImage2(self, strat):
        Images.removeImage(strat, 'chart2')

    def getDescription(self, name):
        desc =  Description.getDescription(name)
        return desc.description if desc else None


    def setDescription(self, name, desc):
        Description.setDescription(name, desc)


def getid():
    '''Local proof of concept'''
    sCrud = StrategyCrud()
    print(sCrud.getId('VWAP Support'))

def setlink():
    '''Local proof of concept'''
    sCrud = StrategyCrud()
    sCrud.setLink('VWAP Support', 'https://fictional/web/site')

def getLinks():
    '''Local proof of concept'''
    scrud = StrategyCrud()
    print(scrud.getLinks('ABCD'))
    print()

def getimage1():
    scrud = StrategyCrud()
    print(scrud.getImage1('ABCD'))


def setimage1():
    scrud = StrategyCrud()
    scrud.setImage1("Schnork", '/c/schnork/image/for/chart/1')

def setimage2():
    scrud = StrategyCrud()
    scrud.setImage2("Schnork", '/c/schnork/image/for/chart/2')

def removeimage():
    scrud = StrategyCrud()
    scrud.removeImage1('Schnork')
    scrud.removeImage2('Schnork')



def removelink():
    '''Local proof of concept- removes the link added in setlink'''
    scrud = StrategyCrud()
    scrud.removeLink('VWAP Support', 'https://fictional/web/site')

 
def addstrategy():
    '''Local proof of concept'''
    scrud = StrategyCrud()
    try: 
        scrud.addStrategy('Schnork')
    except Exception as ex:
        print(ex)
        print('Schnork already exists')

def getstrategy():
    '''Local proof of concept'''
    scrud = StrategyCrud()
    s = scrud.getStrategy(name="ABCD")
    print(s)

def removestrategy():
    scrud = StrategyCrud()
    scrud.removeStrategy('Schnork')

def getstrategies():
    '''Local proof of concept'''
    scrud = StrategyCrud()
    ss = scrud.getStrategies()
    for s in ss:
        print(s[1])

def getpreferred():
    '''Local proof of concept'''
    scrud = StrategyCrud()
    ss = scrud.getPreferred()
    for s in ss:
        print(s[1])

def setpreferred():
    '''Local proof of concept'''
    scrud = StrategyCrud()
    scrud.setPreferred("Schnork",  pref=True)


def getdescription():
    scrud = StrategyCrud()
    print (scrud.getDescription(name = 'Rising Devil'))
    print (scrud.getDescription(name = 'Rising Fred'))

def setdescription():
    name = 'Mistake'
    desc = "The description for the mistake category is don't do that anymore. But still ..."
    scrud = StrategyCrud()
    scrud.setDescription(name, desc)
    scrud.setDescription('schnorrkel2', 'No need to describe schnorkel2. Everyone knows it well')


if __name__ == '__main__':
    # getid()
    # setlink()
    # getLinks()
    # removelink()
    # getimage1()
    # setimage1()
    # setimage2()
    # removeimage()
    # addstrategy()
    # getstrategy()
    removestrategy()
    # getstrategies()
    # getpreferred()
    # setpreferred()
    # getdescription()
    # setdescription()


