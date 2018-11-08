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


        # Create the data structure to make a styled shape for the Mistake Summary Form
        # [key][rng,style]
        mistakeFields = {
            'title'       : [[(1, 1), (12, 2)], 'titleStyle' ],
            'headname'    : [[(1, 3), (2, 3)], 'normStyle'],
            'headpl'      : [(3, 3), 'normStyle'],
            'headLossPL'  : [(4, 3), 'normStyle'],
            'headmistake' : [[(5, 3), (12, 3)], 'normStyle'],

            }
        

        # Create the data structure to create a styled shape for the Daily Summary Form
        dailySummaryFields = {
            'title'       : [[(1, 1), (12, 2)], 'titleStyle' ],
            'headlivetot' : [[(1, 3), (2, 3)], 'normStyle'],
            'headsimtot'  : [[(1, 4), (2, 4)], 'normStyle'],
            'headhighest' : [[(1, 5), (2, 5)], 'normStyle'],
            'headlowest'  : [[(1, 6), (2, 6)], 'normStyle'],
            'headavgwin'  : [[(1, 7), (2, 7)], 'normStyle'],
            'headavgloss' : [[(1, 8), (2, 8)], 'normStyle'],
            'livetot'     : [(3, 3), 'normalNumber'],
            'simtot'      : [(3, 4), 'normalNumber'],
            'highest'     : [(3, 5), 'normalNumber'],
            'lowest'      : [(3, 6), 'normalNumber'],
            'avgwin'      : [(3, 7), 'normalNumber'],
            'avgloss'     : [(3, 8), 'normalNumber'],
            'livetotnote' : [[(4, 3), (12, 3)], 'normStyle'],
            'simtotnote'  : [[(4, 4), (12, 4)], 'normStyle'],
            'highestnote' : [[(4, 5), (12, 5)], 'normStyle'],
            'lowestnote'  : [[(4, 6), (12, 6)], 'normStyle'],
            'avgwinnote'  : [[(4, 7), (12, 7)], 'normStyle'],
            'avglossnote' : [[(4, 8), (12, 8)], 'normStyle'],



            
            }

        # Dynamically add rows to mistakeFields
        for i in range(numTrades) :
            n = "name" + str(i + 1)
            tp = "tpl" + str(i + 1)
            p = "pl" + str(i + 1)
            m = "mistake" + str(i + 1)
            ncells = [(1, 4 + i), (2, 4 + i)]  # [(1,4), (2,4)]
            tpcells =(3, 4 + i)
            pcells = (4, 4 + i)
            mcells = [(5, 4 + i), (12, 4 + i)]
            mistakeFields[n] = [ncells, 'normStyle']
            mistakeFields[tp]= [tpcells, 'normalNumber']
            mistakeFields[p] = [pcells, 'normalNumber']
            mistakeFields[m] = [mcells, 'finalNoteStyle']

        mistakeFields['blank1'] = [[(1, 4 + numTrades), (2, 4 + numTrades)], 'normStyle']
        mistakeFields['blank3'] = [(3, 4 + numTrades), 'normalNumber']
        mistakeFields['total'] = [(4, 4 + numTrades), 'normalNumber']
        mistakeFields['blank2'] = [[(5, 4 + numTrades), (12, 4 + numTrades)], 'normStyle']

        # Excel formulas belong in the mstkval and mstknote columns. The cell translation 
        # takes place when we create and populate the Workbook
        formulas = dict()
        srf=SumReqFields()
        for i in range(numTrades) :

            tp = "tpl" + str(i+1)
            formulas[tp] =['={0}', srf.tfcolumns[srf.pl][0][0] ]
            p = "pl" + str(i + 1)
            formulas[p] = ['={0}', srf.tfcolumns[srf.mstkval][0][0] ]
            m = "mistake" + str(i + 1)
            formulas[m] = ['={0}', srf.tfcolumns[srf.mstknote][0][0] ]
    
        self.formulas = formulas
        self.mistakeFields = mistakeFields
        self.dailySummaryFields = dailySummaryFields

    def mstkSumStyle(self, ws, tf, anchor=(1, 1)):
        
        headers=dict()
        headers['title']       = "Mistake Summary"
        headers['headname']    = "Name"
        headers['headpl']      = "Lost PL"
        headers['headmistake'] = "Mistake or pertinent feature of trade."
        
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
        
    def dailySumStyle(self, ws, tf, listOfTrades, anchor=(1,1)):
        '''
        Create the shape and populate the daily Summary Form
        :params:ws: The openpyxl Worksheet object
        :parmas:tf: The TradeFormat object. It holds the styles used.
        :params:listOfTrade: A python list of DataFrames, each one a trade with multiple tickets
        :params:anchor: The location of the top left corner of the form
        TODO: This is probably better placed in layoutSheet -- similar to LayoutSheet.createMistakeForm() and
        using the Trade Summaries object instead of the trades object... may do that later, but now-- I'm
        going to finish this version-- momentum and all.
        '''
#         srf=SumReqFields()
#         liveTotal = 0
#         simTotal = 0
#         highestProfit = 0
#         largestLoss = 0
#         countLive=0
#         countSim=0
#         totalWins = 0
#         totalLosses = 0
#         numWins = 0
#         numLosses = 0
#         
#         
#         for tdf in listOfTrades :
#             pl = tdf[srf.pl].unique()[-1]
#             live = True if tdf[srf.acct].unique()[0].startswith("U") else False
#             if live:
#                 liveTotal = pl + liveTotal
#                 countLive = countLive + 1
#             else :
#                 simTotal = pl + simTotal
#                 countSim = countSim + 1
#             if pl > 0 :
#                 numWins = numWins + 1
#                 totalWins = pl + totalWins
#                 if pl > highestProfit :
#                     highestProfit = pl
#             else :
#                 numLosses = numLosses + 1
#                 totalLosses = pl + totalLosses
#                 if pl < largestLoss :
#                     largestLoss = pl
#         avgWin = 0 if numWins == 0 else totalWins / numWins
#         avgLoss = 0 if numLosses == 0 else totalLosses / numLosses
                    
        headers=dict()
        headers['title']       = "Daily P / L Summary"
        headers['headlivetot'] = "Live Total"       
        headers['headsimtot']  = "Sim Total"       
        headers['headhighest'] = "Highest Profit"       
        headers['headlowest']  = "Largest Loss"       
        headers['headavgwin']  = "Average Win"       
        headers['headavgloss'] = "Average Loss"       
        anchor = (anchor[0], anchor[1] + self.numTrades + 5)       
#         self.dailySummaryFields['livetot'][2] = liveTotal
#         s=""
#         if countLive == 0 : s = "0 Trades"
#         else :
#             s = "{0} Trade{1}, {2} Winner{3}, {4}, Loser{5}".format(countLive, "" if countLive  == 1 else "s", 
#                                               totalWins, "" if totalWins == 1 else "s",
#                                               totalLosses, "" if totalLosses == 1 else "s")      #4 trades, 1 Winner, 3 Losers
#         self.dailySummaryFields['livetotnote'][2] = s                            
        for key in self.dailySummaryFields :
            rng = self.dailySummaryFields[key][0]
            style = self.dailySummaryFields[key][1]
            if isinstance(self.dailySummaryFields[key][0], list) :
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
#             if len(self.dailySummaryFields[key] > 2) :
#                 ws[tcell(rng, anchor=anchor)] = self.dailySummaryFields[key][2] 
#                 

                
# 

        