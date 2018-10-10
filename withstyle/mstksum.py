'''
Created on Oct 10, 2018

@author: Mike Petersen
'''

from withstyle.tradestyle import style_range, SumReqFields, c as tcell


class MistakeSummary(object):
    '''
    This class will handle the named styles, location, headers and excel formulas. All of the data in the form
    is either header or formula. The user class is responsible for the cell translation coordinates in the formulas.
    '''

    def __init__(self, numTrades, anchor=(1, 1)):

        self.anchor = anchor



        mistakeFields = {
            'title'       : [[(1, 1), (8, 2)], 'titleStyle' ],
            'headname'    : [[(1, 3), (2, 3)], 'normStyle'],
            'headpl'      : [(3, 3), 'normalNumber'],
            'headmistake' : [[(4, 3), (8, 3)], 'normStyle'],

            }

        for i in range(numTrades) :
            n = "name" + str(i + 1)
            p = "pl" + str(i + 1)
            m = "mistake" + str(i + 1)
            ncells = [(1, 4 + i), (2, 4 + i)]  # [(1,4), (2,4)]
            pcells = (3, 4 + i)
            mcells = [(4, 4 + i), (8, 4 + i)]
            mistakeFields[n] = [ncells, 'normStyle']
            mistakeFields[p] = [pcells, 'normalNumber']
            mistakeFields[m] = [mcells, 'normStyle']

        mistakeFields['blank1'] = [[(1, 4 + numTrades), (2, 4 + numTrades)], 'normStyle']
        mistakeFields['total'] = [(3, 4 + numTrades), 'normalNumber']
        mistakeFields['blank2'] = [[(4, 4 + numTrades), (8, 4 + numTrades)], 'normStyle']

        formulas = dict()
        srf=SumReqFields()
        for i in range(numTrades) :
#             t="=" +str(i+1) + " "
            f ='=CONCAT("{0} ",'.format(str(i+1))
            f = f  + '{0}," ",{1})'
            n = "name" + str(i + 1)
            formulas[n] = [f,
               srf.tfcolumns[srf.name][0][0],
               srf.tfcolumns[srf.acct][0][0]
               ]
            p = "pl" + str(i + 1)
            formulas[p] = ['={0}', srf.tfcolumns[srf.mstkval][0][0] ]
            m = "mistake" + str(i + 1)
            formulas[m] = ['={0}', srf.tfcolumns[srf.mstknote][0][0] ]

        self.formulas = formulas
        self.mistakeFields = mistakeFields

    def mstkSumStyle(self, ws, tf, anchor=(1, 1)):
        for key in self.mistakeFields.keys() :
            rng = self.mistakeFields[key][0]
            style = self.mistakeFields[key][1]
            anchor = anchor

            if isinstance(self.mistakeFields[key][0], list) :
                tf.mergeStuff(ws, rng[0], rng[1], anchor=anchor)
                ws[tcell(rng[0], anchor=anchor)].style = tf.styles[style]
                mrng = tcell(rng[0], rng[1], anchor=anchor)
                style_range(ws, mrng, border=tf.styles[style].border)

            else:
                ws[tcell(rng, anchor=anchor)].style = tf.styles[style]
