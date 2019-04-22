'''
This is an unimplemented module
'''
from picklekey import getKey

if __name__ == '__main__':
    k = getKey('quandl')
    print()
    print('Your api key is:', k['key'])
    print('docs at:', k['web'])
    print('key is registered to',k['registered'])
