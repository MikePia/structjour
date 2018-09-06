import datetime, os

# strftime formats:
#   %A  'Monday'
#   %w  '1' (for Monday)
#   %Y  '2018'  (current year)
#   %B  'January
#   %d  day of the month
#   %m  01 (for January)
# def mkdir(name):
    
def createWeeks (month, day) :
    week = 1
    beginDate = datetime.date(2018, month, day)
    idow = int(beginDate.strftime("%w"))
    dow = beginDate.strftime("%A")
    dom = beginDate.strftime("%B")
    printDate = beginDate
    newDate = datetime.date(1,1,1)
    for i in range (1, 6) :
        if i > 4 and int(printDate.strftime("%w")) > 4 :
            return
        wkfldr = "Week_" + str(i)
        os.mkdir(wkfldr)
        os.chdir(wkfldr)
        
        while True :
#             input('')
            fold = printDate.strftime("_%m%d_%A")
            os.mkdir(fold)
            idow = idow + 1 
            day = day + 1
            if idow == 6 :
                day = day+ 2
                idow = 1
                os.chdir("..")
                try :
                    printDate = datetime.date(2018, month,day)
                except  Exception as ex :
                    print(ex)
                    break
                break
            try :
                printDate = datetime.date(2018, month, day)
            except :
                break
            


def beginQ() :
    d = os.getcwd()
    print(d)
    ds = d.split('/')
    print(ds)
    if len(ds) < 1 :
        print(" You do not appear to be in your journal directory")
        quit()
    dsw = ds[len(ds)-1]
    print (dsw)
    if "jour" not in dsw.lower() :
        print()
        print('''You don't appear to be in a journal folder. Would you like to continue any way?  (y/n) : ''')
        r = input()
        if r.lower().startswith('y') == False :
            print('Bye!')
            quit()
    else :
        print("in journal")
         
    return
 
beginQ()
 
# quit()
print ("here we go")
while True:
    r = input ("What Month would you like to create?  (Enter a number from 1-12) ")
    if r.lower().startswith('q') :
        print("Bye!")
        quit()
    try :
        month = int(r)
    except :
        print ("I didn't understand that. (q to quit)")
        continue
    if month < 1 or month > 12 :
        print("That is not between 1 and 12. (q to quit)") 
        continue
    break
print (month)
d = datetime.date(2018, month, 1)
dayOfWeek = int(d.strftime("%w"))
day = 1
if dayOfWeek == 0 :
    day = day + 1
if dayOfWeek== 6 :
    day = day + 2
dd = datetime.date(2018, month, day)
 
# Monday, January 1, 2018
print(dd, dd.strftime("%A, %B %d, %Y"))
curmonth = month
os.mkdir(dd.strftime("_%m_%B")) 
os.chdir(dd.strftime("_%m_%B")) 
 
createWeeks(month, day)
