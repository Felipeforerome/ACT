import os
import pickle

import bs4 as bs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import style
# Import requiered to access Iconomi
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.tickers import prices

style.use('ggplot')


def save_index_tickers():
    """
    Saves the tickers and weights of Iconomi in a pickle
    :return: The tickers and weights of the Iconomi components
    """
    url = 'https://www.iconomi.net/dashboard/#/INDEX'
    # Going to the URL
    driver = webdriver.PhantomJS()
    driver.get(url)
    # waiting for presence of an element
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tableCategoryColumnOnMobile")))

    # Save the data and close the page
    resp = driver.page_source
    driver.close()

    soup = bs.BeautifulSoup(resp, 'html5lib')
    table = soup.findAll('tbody')[2]
    tickers = []
    comps = []
    for row in table.findAll('tr'):
        ticker = row.findAll('td')[0].text
        tickers.append(ticker[ticker.find("(") + 1:ticker.find(")")])
        comp = row.findAll('td')[2].text
        comps.append(float(comp[0:comp.find(" ") - 1]))

    with open('crindex.pickle', 'wb') as f:
        pickle.dump(tickers, f)

    with open('cromposition.pickle', 'wb') as f:
        pickle.dump(comps, f)

    return tickers, comps


def acquire_data(ticker):
    """
    Gets the price history for a given cryptocurrency and saves it in de coins_dfs folder
    :param ticker: Ticker for which price history is being looked
    """
    to = 'BTC'
    if ticker == 'BTC':
        print(to)
        to = 'USD'
        print(to)

    if not os.path.exists('coins_dfs/{}.csv'.format(ticker)):
        print('Getting {}'.format(ticker))
        df = prices(ticker, to)
        print('Got {}'.format(ticker))
        df.to_csv('coins_dfs/{}.csv'.format(ticker))
    else:
        print('Already have {}'.format(ticker))


def get_data(reload_cindex=False):
    """
    Gets the data for de cryptocurrencies included in cindex pickle
    :param reload_cindex:Whether all data should be force reloaded or not
    """
    if reload_cindex:
        tickers = save_index_tickers()
        os.removedirs('coins_dfs')
    else:
        with open('crindex.pickle', 'rb') as f:
            tickers = pickle.load(f)
    print(tickers)
    if not os.path.exists('coins_dfs'):
        os.makedirs('coins_dfs')

    for ticker in tickers:
        acquire_data(ticker)


def compile_data():
    """
    Takes the close values of all the data in coins:dfs and joins it in a single csv
    """
    with open('crindex.pickle', 'rb') as f:
        tickers = pickle.load(f)

    main_df = pd.DataFrame()

    for count, ticker in enumerate(tickers):
        df = pd.read_csv('coins_dfs/{}.csv'.format(ticker))
        df.set_index('time', inplace=True)

        df.rename(columns={'close': ticker}, inplace=True)
        df.drop(['open', 'high', 'low', 'volumefrom', 'volumeto', 'volume'], 1, inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')

        if count % 10 == 0:
            print(count)

    main_df.to_csv('joined_cindex.csv')


def visualize_data():
    """
    Displays a heatmap of correlation between each cryptocurrency (G=1 & R=-1)
    """
    df = pd.read_csv('joined_cindex.csv')
    # df['ETH'].plot()
    # plt.show()
    df_corr = df.corr()
    data = df_corr.values
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0] + 0.5), minor=False)
    ax.set_yticks(np.arange(data.shape[1] + 0.5), minor=False)

    ax.invert_yaxis()
    ax.xaxis.tick_top()

    column_labels = df_corr.columns
    row_labels = df_corr.index

    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap.set_clim(-1, 1)

    plt.tight_layout()
    plt.show()
