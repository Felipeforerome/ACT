# Importing de requiered libraries

import pandas as pd
import requests


def prices(market, to):
    """
    Gets the Bittrex price history for a week for a given market, usually BTC to something else
    :param market: Cryptocurrency being sold
    :param to: Crytocurrency being bought
    :return: OHLC for a given market
    """
    ohlc = pd.DataFrame(requests.get(
        'https://min-api.cryptocompare.com/data/histominute?fsym=%s&tsym=%s&limit=168&aggregate=10&e=BitTrex' %
        (market, to)).json().get('Data'))
    ts = ohlc.iloc[0]['time']
    for x in range(0, 5):
        stamp = ts - (x * 100800)
        r = pd.DataFrame(requests.get(
            'https://min-api.cryptocompare.com/data/histominute?fsym=%s&tsym=%s&toTs=%s&limit=168&aggregate=10&e=BitTrex' %
            (market, to, stamp - 600)).json().get('Data'))
        r = r.drop(r.shape[0] - 1)
        ohlc = pd.concat([r, ohlc], ignore_index=True)

    col_list = list(ohlc)
    col_list[0], col_list[1], col_list[2], col_list[3] = col_list[3], col_list[2], col_list[1], col_list[0]
    ohlc.columns = col_list
    ohlc = ohlc.set_index('time')
    ohlc.index = pd.to_datetime(ohlc.index, unit='s')
    ohlc['volume'] = ohlc['volumeto'] - ohlc['volumefrom']
    return ohlc
