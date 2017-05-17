import requests
import json
from pprint import pprint
from slacker import Slacker

# get pair data from Poloniex API
rawPoloData = json.loads(requests.get("https://poloniex.com/public?command=returnTicker").text)

# reformat Poloniex pair names to match format on liqui i.e. eth_btc instead of BTC_ETH
# only include pairs for ETH and BTC as these are the only trades you can make on liqui
poloData = {'%s_%s' % (pair[4:].lower(), pair[:3].lower()) : pairData 
            for pair, pairData in rawPoloData.iteritems() 
            if pair.startswith('BTC') or pair.startswith('ETH')}

# generate string for liqui API call by concatenating pair names in poloData
liquiPairString = '-'.join([pair for pair in poloData])

# get pair data from liqui API
liquiData = json.loads(requests.get("https://api.liqui.io/api/3/ticker/%s?ignore_invalid=1" % liquiPairString).text)


 # join both data sets on pair name
joinedData = []
for pair, pairData in liquiData.iteritems():
    record = {'pair' : pair.upper()}
    record['liquiBuy'] = float(pairData['buy'])
    record['liquiSell'] = float(pairData['sell'])
    record['poloBuy'] = float(poloData[pair]['lowestAsk'])
    record['poloSell'] = float(poloData[pair]['highestBid'])
    record['hasPriceOnBoth'] = record['liquiBuy'] and record['liquiSell'] and record['poloBuy'] and record['poloSell'] 
    # calculate ratios across exchanges
    record['liquiBuyPoloSell'] = record['liquiBuy'] * 1/record['poloSell'] if record['hasPriceOnBoth'] else 'N/A'
    record['poloBuyLiquiSell'] = record['poloBuy'] * 1/record['liquiSell'] if record['hasPriceOnBoth'] else 'N/A'
    joinedData.append(record)


# define Slack API connection
slackToken = open('slackToken.txt').read()
slack = Slacker(slackToken)
slackChannel = '#arbitrage_opps'
slack.chat.post_message(slackChannel, '*Checking Poloniex vs Liqui...*')

# define variance over which we see a pairing as potentially profitable
profitable_variance = 0.025

# check all pairs for profitable variance
for pair in joinedData:
    if pair['hasPriceOnBoth']:
        # get coin names from pair code i.e. spit ETH_BTC in ETH and BTC
        coinA = pair['pair'][:pair['pair'].find('_')].upper()
        coinB = pair['pair'][pair['pair'].find('_')+1:].upper()
        # check ratio buying on exchange A selling on exchange B
        if abs(pair['liquiBuyPoloSell'] - 1) > profitable_variance:
            # Define message for Slack
            message =  ">Arbritage opportunity on *%s*, buy *%s* on liqui at *%s %s*, sell on polo at *%s %s* (ratio = *%s*)" % (pair['pair'], coinA, pair['liquiBuy'], coinB, pair['poloSell'], coinB, pair['liquiBuyPoloSell'])
            # post message to Slack
            slack.chat.post_message(slackChannel, message)
        # check ratio buying on exchange B selling on exchange A
        elif abs(pair['poloBuyLiquiSell'] - 1) > profitable_variance:
            # define message for Slack
            message =  ">Arbritage opportunity on *%s*, buy *%s* on polo at *%s %s*, sell on liqui at *%s %s* (ratio = *%s*)" % (pair['pair'], coinA, pair['poloBuy'], coinB, pair['liquiSell'], coinB, pair['poloBuyLiquiSell'])
            # post message to Slack
            slack.chat.post_message(slackChannel, message)
            

