from tickers import prices
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd
import bittrex

# plt.interactive(False)
plt.style.use('ggplot')

# ETH = pd.read_csv('ETH.csv', parse_dates=True, index_col=4)
ETH=prices('ETH')
# ETH['100ma'] = ETH['close'].rolling(window=100,min_periods=0).mean()

ETH_ohlc = ETH['close'].resample('30Min').ohlc()
ETH_volume = ETH['volumefrom'].resample('30Min').sum()

print(ETH_ohlc.head())
print(ETH.head())

ETH_ohlc.reset_index(inplace=True)

ETH_ohlc['time']= ETH_ohlc['time'].map(mdates.date2num)

ax1 = plt.subplot2grid((6,1),(0,0),rowspan=5,colspan=1)
ax2 = plt.subplot2grid((6,1),(5,0),rowspan=1,colspan=1, sharex=ax1)

ax1.xaxis_date()


candlestick_ohlc(ax1, ETH_ohlc.values, width=0.01, colorup='g')
ax2.fill_between(ETH_volume.index.map(mdates.date2num),ETH_volume.values,0)

plt.show()