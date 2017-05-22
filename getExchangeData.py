"""
Generally contains two functions for each exchange:

1) Parent Function - getXxxxxData(): Contains high level logic to access the exchange API and return pairs data
2) Child Function - convertXxxxxPair(): Contains low-level logic to process data for a specific pair e.g. ETH_BTC

All getXxxxData() functions return a similar data structure to be used in compareExchanges.py
"""

import json
import pandas as pd
import sys
import requests


pd.set_option('display.width', 1000)


def getPoloData():
    poloCols = ['alphaCode', 'poloBaseCoin', 'poloQuoteCoin', 'poloBuyBase', 'poloSellBase']
    rawPoloData = json.loads(requests.get("https://poloniex.com/public?command=returnTicker").text)
    return pd.DataFrame([convertPoloPair(pair, pairData) for pair, pairData in rawPoloData.iteritems()])[poloCols].set_index('alphaCode')


def convertPoloPair(pair, pairData):
    separator = pair.find('_')
    record = {}
    record['poloBaseCoin'] = pair[:separator]
    record['poloQuoteCoin'] = pair[separator+1:]
    record['poloBuyBase'] = float(pairData['lowestAsk'])
    record['poloSellBase'] = float(pairData['highestBid'])
    record['alphaCode'] = ''.join(sorted([record['poloBaseCoin'], record['poloQuoteCoin']]))
    return record


def getKrakenData():
    krakenCols = ['alphaCode', 'krakenBaseCoin', 'krakenQuoteCoin', 'krakenBuyBase', 'krakenSellBase']
    krakenAssets = json.loads(requests.get("https://api.kraken.com/0/public/Assets").text)['result']
    krakenPairString = ','.join([pair for pair in json.loads(requests.get("https://api.kraken.com/0/public/AssetPairs").text)['result']])
    rawKrakenData = json.loads(requests.get("https://api.kraken.com/0/public/Ticker?pair=%s" % krakenPairString).text)['result']
    return pd.DataFrame([convertKrakenPair(pair, pairData, krakenAssets) for pair, pairData in rawKrakenData.iteritems() if convertKrakenPair(pair, pairData, krakenAssets)])[krakenCols].set_index('alphaCode')


def convertKrakenPair(pair, pairData, krakenAssets):
    if pair[:3] in krakenAssets:
        separator = 3
    elif pair[:4] in krakenAssets:
        separator = 4
    else:
        sys.exit()
    record = {}
    softBaseCoin = pair[separator:]
    softQuoteCoin = pair[:separator]
    record['krakenBaseCoin'] = 'BTC' if softBaseCoin in ('XXBT', 'XBT') else krakenAssets[softBaseCoin]['altname'] if softBaseCoin in krakenAssets else softBaseCoin
    record['krakenQuoteCoin'] = 'BTC' if softQuoteCoin in ('XXBT', 'XBT') else krakenAssets[softQuoteCoin]['altname'] if softQuoteCoin in krakenAssets else softQuoteCoin
    record['krakenSellBase'] = float(pairData['b'][0])
    record['krakenBuyBase'] = float(pairData['a'][0])
    record['alphaCode'] = ''.join(sorted([record['krakenBaseCoin'], record['krakenQuoteCoin']]))
    return record if record['krakenBaseCoin'] in ('BTC', 'ETH') else None


def getLiquiData():
    liquiCols = ['alphaCode', 'liquiBaseCoin', 'liquiQuoteCoin', 'liquiBuyBase', 'liquiSellBase']
    liquiPairString = '-'.join([pair for pair in json.loads(requests.get("https://api.liqui.io/api/3/info").text)['pairs']])
    rawLiquiData = json.loads(requests.get("https://api.liqui.io/api/3/ticker/%s?ignore_invalid=1" % liquiPairString).text)
    return pd.DataFrame([convertLiquiPair(pair, pairData) for pair, pairData in rawLiquiData.iteritems()])[liquiCols].set_index('alphaCode')


def convertLiquiPair(pair, pairData):
    separator = pair.find('_')
    record = {}
    record['liquiBaseCoin'] = pair[separator+1:].upper()
    record['liquiQuoteCoin'] = pair[:separator].upper()
    record['liquiSellBase'] = float(pairData['buy'])
    record['liquiBuyBase'] = float(pairData['sell'])
    record['alphaCode'] = ''.join(sorted([record['liquiBaseCoin'], record['liquiQuoteCoin']]))
    return record


def convertBtrexPair(pair):
    separator = pair['MarketName'].find('-')
    record = {}
    record['btrexBaseCoin'] = pair['MarketName'][:separator]
    record['btrexQuoteCoin'] = pair['MarketName'][separator+1:]
    record['btrexBuyBase'] = pair['Ask']
    record['btrexSellBase'] = pair['Bid']
    record['alphaCode'] = ''.join(sorted([record['btrexBaseCoin'], record['btrexQuoteCoin']]))
    return record


def getBtrexData():
    btrexCols = ['alphaCode', 'btrexBaseCoin', 'btrexQuoteCoin', 'btrexBuyBase', 'btrexSellBase']
    rawBtrexData = json.loads(requests.get("https://bittrex.com/api/v1.1/public/getmarketsummaries").text)['result']
    return pd.DataFrame([convertBtrexPair(pair) for pair in rawBtrexData])[btrexCols].set_index('alphaCode')