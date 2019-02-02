def f1():
    return 10, True

def f2():
    num, stat = f1()
    return 'before: ' + num + ': After', stat


if __name__ == '__main__':
    print(f2())
    print(f2())
    