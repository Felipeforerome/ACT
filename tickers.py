# Importing de requiered libraries
from bittrex.bittrex import Bittrex
import pandas as pd
import requests
import bs4 as bs
import pickle
import datetime

# Keys needed to access Bittrex's API
api_key = 'x'
api_secret = 'x'

# Api Object
api = Bittrex(api_key, api_secret)


# Function that returns the price history from Bittrex for a given market
def prices(market,to):
    ohlc = pd.DataFrame(requests.get(
        'https://min-api.cryptocompare.com/data/histominute?fsym=%s&tsym=%s&limit=168&aggregate=10&e=BitTrex' %
        (market, to)).json().get('Data'))
    ts = ohlc.iloc[0]['time']
    for x in range(0, 5):
        stamp = ts - (x * 100800)
        r = pd.DataFrame(requests.get(
            'https://min-api.cryptocompare.com/data/histominute?fsym=%s&tsym=%s&toTs=%s&limit=168&aggregate=10&e=BitTrex' %
                (market, to, stamp-600)).json().get('Data'))
        r=r.drop(r.shape[0]-1)
        ohlc = pd.concat([r, ohlc], ignore_index=True)

    col_list = list(ohlc)
    col_list[0], col_list[1], col_list[2], col_list[3] = col_list[3], col_list[2], col_list[1], col_list[0]
    ohlc.columns = col_list
    ohlc = ohlc.set_index('time')
    ohlc.index = pd.to_datetime(ohlc.index, unit='s')
    ohlc['volume']= ohlc['volumeto']-ohlc['volumefrom']
    return ohlc

def save_index_tickers():
    resp = requests.get('https://coinmarketcap.com/exchanges/bittrex/')
    soup = bs.BeautifulSoup(resp.text, 'html5lib')
    table = soup.find('table',{'class':'table no-border table-condensed'}).findAll('a',{'target': '_blank'})
    tickers = []
    for row in table:
        market = row.string
        if tickers.__len__()<20:
            if '/BTC' in market:
                ticker=market.split('/')
                tickers.append(ticker[0])
        else:
            break
    with open('cryptoindex.pickle','wb') as f:
        pickle.dump(tickers, f)

    return tickers

