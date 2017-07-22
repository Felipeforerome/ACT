import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.interactive(False)


def bbands(ticker, length=14, numsd=2):
    """
    Calculates de Bollinger Bands for some length and standard deviation given and returns the three relevant bands
    :param ticker: Ticker for the cryptocurrency
    :param length: length of the simple moving average
    :param numsd: number of standard deviations added to the SMA to get the upper and lower bands
    :return: returns the SMA, upper and lower bands
    """
    ave = ticker.rolling(window=length, center=False, min_periods=0).mean()
    sd = ticker.rolling(window=length, center=False, min_periods=0).std()
    upband = ave + (sd * numsd)
    dnband = ave - (sd * numsd)
    return np.round(ave, 10), np.round(upband, 10), np.round(dnband, 10)


def visualize_bbands(sp, ohlc=True):
    """
    Displays a graph of the close values, SMA, upper and lower Bollinger Bands across time
    :param sp: price history in dataframe
    :param ohlc: Whether the incoming sp is in ohlc of just the close values
    """
    if ohlc:
        sp['ave'], sp['up'], sp['lower'] = bbands(sp.close)
        sp.pop('open')
        sp.pop('high')
        sp.pop('low')
        sp.pop('volume')
        sp.pop('volumefrom')
        sp.pop('volumeto')
    else:
        sp['ave'], sp['up'], sp['lower'] = bbands(sp)

    sp.plot()
    plt.show()


def process_data_pct_change(ticker, hm_tenmin=6):
    """
    Processes the data to add the corresponding percentage change in th end of the interval
    :param ticker: Ticker to be processed
    :param hm_tenmin: How many tenths of minutes to group together
    :return: returns the tickers in the joined cindex and the joined index with percent change between tenths of minutes for the given ticker
    """
    df = pd.read_csv('joined_cindex.csv', index_col=0)
    tickers = df.columns.values.tolist()
    df.fillna(0, inplace=True)

    for i in range(1, hm_tenmin + 1):
        df['{}_{}t'.format(ticker, i)] = (df[ticker].shift(-i) - df[ticker]) / df[ticker]

    df.fillna(0, inplace=True)
    return tickers, df
