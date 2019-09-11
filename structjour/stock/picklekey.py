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
Pickle keys to the file system.
Add to .gitignore pickle.py and keys.pickle
Replaced with db storage

@author: Mike Petersen

@creation_date: 20181222
'''
import pickle
# pylint: disable = C0103

PFILE = 'C:\\\\python\\E\\stock\\keys.pickle'


class PickleKeys(object):
    '''Pickle and retrieve the keys'''

    keys = ['alphavantage', 'quandl', 'barchart']

    def __init__(self):
        # with open(PFILE, "wb") as f:
        #     pickle.dump(PickleKeys.apikeys, f)
        pass


def getKey(api):
    '''retrieve info from keys.pickle'''
    if api not in PickleKeys.keys:
        print("Please designate api from these choices{}".format(PickleKeys.keys))
        return None
    with open(PFILE, "rb") as f:
        keys = pickle.load(f)
    return keys[api]


# print (PickleKeys.keys)
# x = PickleKeys()
# k = getKey('barchart')
# print(type(k), len(k))
# print(getKey('barchart')['key'])
# getKey('goblledegook')
# print(k['web'])
# print(k['date'])
# print(k['registered'])
# print()