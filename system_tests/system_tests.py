'''
Running unittest changes the way QtWebEngine loads. I am sure there is a way to make it play nice
with the unittest suite but this is easier. Anything that will eventually load QtWebEngine in the
strategy object will be problematic

It works out that the code that requires this stuff is the code that interacts. The tests are far
more complicated than unittests. Setting them aside is better organization and a step towards
simplification.
'''
from test_dailycontrol_system import notmain as dailycontrol_notmain


if __name__ == '__main__':
    dailycontrol_notmain()
