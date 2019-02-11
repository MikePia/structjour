import datetime as dt
import os
import pandas as pd

 
# pylint: disable = C0103, C0301

# strftime formats:
#   %A  'Monday'
#   %w  '1' (for Monday)
#   %Y  '2018'  (current year)
#   %B  'January
#   %d  day of the month
#   %m  01 (for January)
# def mkdir(name):

# Implementing the following file structure names
# theMonth.strftime("_%Y%m_%B")) // theDate.strftime(_%m%d_%A")

class TimeStuff:
    def __init__(self, theMonth, theDir=r'C:\trader\journa2', theYear=2019, monthformat="_%Y%m_%B", dayformat="_%m%d_%A"):
        self.monthformat = monthformat
        self.dayformat = dayformat
        self.theYear = theYear
        self.theDir = theDir
        self.theMonth = theMonth
        # self.theMonth, self.theDir = getFirstWeekday(self.theMonth, self.theDir)



def createDirs(theDate, theDir, frmt="_%m%d_%A"):
    '''
    In the directory theDir, create 1 month of directories, one for each weekday. Use the date
    theDate to and the format given to create the names.
    :params theDate: A datetime object giving the starting date for the directories.
    :params theDir: The directory in which to create the subdirectories.
    :params frmt: The strftime format used to create the directories.
    '''
    # theDate = dt.datetime(2019, 6, 3)
    cwd = os.getcwd()
    month = theDate.month
    delt = dt.timedelta(1)
    if os.path.exists(theDir):
        raise ValueError('Directory Already exists:', theDir)

    os.mkdir(theDir)
    os.chdir(theDir)

    while True:
        if theDate.isoweekday() < 6:
            # print(theDate.strftime(frmt))
            folder = theDate.strftime(frmt)
            os.mkdir(folder)
        theDate = theDate + delt
        if theDate.month > month:
            break

    os.chdir(cwd)


def getFirstWeekday(theMonth=None, theDir=None):
    '''
    The interactive portion of this method is deprectaed and will be removed at a future time.
    With no paramters, this is a conversation to determine the month and location. This
    conversation should go away.
    With parameterse given, theDir is verified to exist and theDay is returned as the
    first weekday of the given month.
    :params theMonth: A Time string or datetime object for which to create directories. If not
                        given, ask the user.
    :params theDir: The directory to start in. If not given, we use cwd. But if the current dir
                    is not named *journal*, ask the user to continue or not.
    :return (theDay, theDir): A tuple, theDay is the first weekday of the month to create.
                    theDir is the directory to start in.
    '''

    if not theDir:
        d = os.getcwd()
        ds = d.split('/')
        if len(ds) < 1:
            print(" You do not appear to be in your journal directory")
            return -1
        dsw = ds[len(ds)-1]
        if "journal" not in dsw.lower():
            print()
            print(f'''You don't appear to be in a journal folder.
        {d} 
        Would you like to continue any way?  (y/n) : ''')
            r = input()
            if not r.lower().startswith('y'):
                print('Bye!')
                return -1
        theDir = d
    if not os.path.exists(theDir):
        raise ValueError(f'Path not found {theDir}')

    if not theMonth:
        while True:
            r = input("Please enter the month and year. e.g: 2019-03:    ")
            if r.lower().startswith('q'):
                print("Bye!")
                return -1
            try:
                if len(r) < 6 or len(r) > 7:
                    raise ValueError('Please use yyyymm or yyyy-mm')
                r = r + '-01' if r.find('-') > 0 else r + '01'
                theDay = pd.Timestamp(r)
            except  ValueError:
                print("I didn't understand that. (q to quit)")
                continue
    #         r=input(f"{theDay.strftime('%B %Y')} Is this the month?")
            break
    else:
        theMonth = pd.Timestamp(theMonth)
        # print(theMonth)
    advancedays = 8 - theMonth.isoweekday()  if theMonth.isoweekday() > 5 else 0

    day = 1 + advancedays
    theDay = dt.datetime(theMonth.year, theMonth.month, day)

    return theDay, theDir





def main():
    # outdir = os.getcwd()
    journaldir = os.getcwd()
    theDate = pd.Timestamp('2019-06-01')
    theDate, journaldir = getFirstWeekday(theDate, journaldir)

    monthDir = os.path.join(journaldir, theDate.strftime("_%Y%m_%B"))
    createDirs(theDate, monthDir)



# os.chdir(theDir)
# print(os.getcwd())
# print(theDay.strftime("_%m_%B"))

if __name__ == '__main__':
    main()
