def f1(shares, position, justask=False):
    return 10, True

def f2():

    num, stat = f1(0,0,True)
    print("internal ", 'before: ' + num + ': After', stat)
    num, stat = f1(0,0,True)
    print("internal ", 'before: ' + num + ': After', stat)
    num, stat = f1(0,0,True)
    print("internal ", 'before: ' + num + ': After', stat)  
    num, stat = f1(0,0,True)
    print("internal ", 'before: ' + num + ': After', stat)
    num, stat = f1(0,0,True)
    print("internal ", 'before: ' + num + ': After', stat)

    return 'before: ' + num + ': After', stat


if __name__ == '__main__':
    print(f2())
    print(f2())
    print(f2())
    print(f2())
    print()
    