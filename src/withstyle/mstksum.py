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
        self.numTrades = numTrades


        # Create the data structure to make a styled shape 
        # [key][rng,style]
        mistakeFields = {
            'title'       : [[(1, 1), (8, 2)], 'titleStyle' ],
            'headname'    : [[(1, 3), (2, 3)], 'normStyle'],
            'headpl'      : [(3, 3), 'normalNumber'],
            'headmistake' : [[(4, 3), (8, 3)], 'normStyle'],

            }

        # Dynamically add rows to mistakeFields
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

        # Excel formulas belong in the mstkval and mstknote columns. The cell translation 
        # can't be done till we create and populate the Workbook
        formulas = dict()
        srf=SumReqFields()
        for i in range(numTrades) :

            p = "pl" + str(i + 1)
            formulas[p] = ['={0}', srf.tfcolumns[srf.mstkval][0][0] ]
            m = "mistake" + str(i + 1)
            formulas[m] = ['={0}', srf.tfcolumns[srf.mstknote][0][0] ]
    
        self.formulas = formulas
        self.mistakeFields = mistakeFields

    def mstkSumStyle(self, ws, tf, anchor=(1, 1)):
        
        headers=dict()
        headers['title']       = "Mistake Summary"
        headers['headname']    = "Name"
        headers['headpl']      = "Lost PL"
        headers['headmistake'] = "Mistake"
        
        # Merge the cells, apply the styles, and populate the fields we can--the 
        # fields that don't know any details todays trades (other than how many trades)
        # That includes the non-formula fields and the sum formula below 
        for key in self.mistakeFields.keys() :
            rng = self.mistakeFields[key][0]
            style = self.mistakeFields[key][1]
            anchor = anchor

            if isinstance(self.mistakeFields[key][0], list) :
                tf.mergeStuff(ws, rng[0], rng[1], anchor=anchor)
                ws[tcell(rng[0], anchor=anchor)].style = tf.styles[style]
                mrng = tcell(rng[0], rng[1], anchor=anchor)
                style_range(ws, mrng, border=tf.styles[style].border)
                if key in headers.keys() :
                    ws[tcell(rng[0], anchor=anchor)] = headers[key]

            else:
                ws[tcell(rng, anchor=anchor)].style = tf.styles[style]
                if key in headers.keys() :
                    ws[tcell(rng, anchor=anchor)] = headers[key]
                    
        # The total sum formula is done here. It is self contained to references to the Mistake Summary form
        totcell = self.mistakeFields['total'][0]
        begincell=(totcell[0], totcell[1] - self.numTrades)
        endcell=(totcell[0], totcell[1] - 1)
        rng= tcell(begincell, endcell, anchor = anchor)
        totcell = tcell(totcell, anchor = anchor)
        f = '=SUM({0})'.format(rng)
        ws[totcell] = f
                
                
                
                
                
                
                
                
                
                
                
                
