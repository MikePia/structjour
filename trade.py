import pandas as pd
ntrade = pd.read_csv('everything.csv')
print(type(ntrade))
# lbls['Tex'] = 1
ntrade['Tindex'] = ''
ntrade['Start'] = ''
ntrade['Balance'] = ''
ntrade['Sum'] = ''
ntrade['Duration'] = ''
ntrade['Name'] = ''
ntrade['Name'] = ''
print(ntrade.columns)

lbls=['Tindex', 'Start', 'Time', 'Symb', 'Side', 'Price', 'Qty','Balance', 'Account', "P / L", 'Sum', 'Duration', 'Name']
for l in lbls :
    if l in ntrade.keys() :
        print ("Got", l)
    else :
        print("!!!!!!     Missing", l)

# #Here are the required columns for review
subset = ntrade[lbls]
deep = subset.copy()
print(deep)
print(deep[lbls])
if deep.Qty >=  0 :
    deep.Balance = deep.Qty
else :
    deep.Balance = - deep.Qty    

# print(deep.columns)
# print(deep.head().to_string())
# for r in deep :
#     print(r)
