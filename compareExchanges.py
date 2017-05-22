"""
Accesses data from multiple exchanges and outputs tabular data with ratios calculated.

Doesn't do much else yet.

Written to be scalable, so that new exchanges can be added by adding a new key, value pair to the exchanges dictionary.
"""

from getExchangeData import *


# build data structure
exchanges = {
             'polo' : {
                       'dataFrame' : getPoloData(),
                       'makerFee' : 0.99,
                       'takerFee' : 0.9975
                       },
             'kraken' : {
                         'dataFrame' : getKrakenData(),
                         'makerFee' : 0.99,
                         'takerFee' : 0.9975
                         },
             'liqui' : {
                         'dataFrame' : getLiquiData(),
                         'makerFee' : 0.99,
                         'takerFee' : 0.9975
                        }
             }


# joined data frame
jdf = pd.DataFrame([])
for exchange, exchangeData in exchanges.iteritems():
    jdf = jdf.join(exchangeData['dataFrame'], how = 'outer')


# calculate ratios 
for ex1, ex1Data in exchanges.iteritems():
    for ex2, ex2Data in exchanges.iteritems():
        if ex1 <> ex2:
            jdf['buy%sSell%s' % (ex1.title(), ex2.title())] = jdf['%sSellBase' % ex2] / jdf['%sBuyBase' % ex1] * ex1Data['takerFee'] * ex2Data['takerFee']


jdf.to_csv('joinedData.csv')














    
    

