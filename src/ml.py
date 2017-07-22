from collections import Counter

import numpy as np
from sklearn import svm, cross_validation, neighbors
from sklearn.ensemble import VotingClassifier, RandomForestClassifier

from src.processes import process_data_pct_change


def buy_sell_hold(*args):
    """
    Tells, based on the percentage change towards the future, whether it should be a buy, sell or hold
    :param args: column of price percentage changes between to moments
    :return: 1, -1, 0 meaning buy, sell, or hols, if the change is higher, lower, of neither in those changes
    """
    cols = [c for c in args]
    requirement = 0.0025
    for col in cols:
        if col > requirement:
            return 1
        if col < -requirement:
            return -1
    return 0


def extract_features_sets(ticker, hm_tenmin=6):
    """
    Extracts the feature sets i.e. values that affect the outcome
    :param ticker: Ticker for which the features are being extracted
    :param hm_tenmin: How many tenths of minutes to group together
    :return: labels, features, and the original dataframe
    """
    tickers, df = process_data_pct_change(ticker)

    df['{}_target'.format(ticker)] = list(
        map(buy_sell_hold, *[df["{}_{}t".format(ticker, i)] for i in range(1, hm_tenmin + 1)]))

    vals = df['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]
    print('Data spread:', Counter(str_vals))

    df.fillna(0, inplace=True)
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(inplace=True)

    df_vals = df[[ticker for ticker in tickers]].pct_change()
    df_vals = df_vals.replace([np.inf, -np.inf], 0)
    df_vals.fillna(0, inplace=True)

    X = df_vals.values
    y = df['{}_target'.format(ticker)].values

    return X, y, df


def do_ml(ticker):
    """
    Runs 3 machine learning algorithm, inside a Voting classifier, to learn when it should buy sell of hold
    :param ticker: Ticker of the Cryptocurrency to undergo this process
    :return: returns the confidence of the model describing the data
    """
    X, y, df = extract_features_sets(ticker)

    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X,
                                                                         y,
                                                                         test_size=0.25)

    clf = VotingClassifier([('lsvc', svm.LinearSVC()),
                            ('knn', neighbors.KNeighborsClassifier()),
                            ('rfor', RandomForestClassifier())])

    clf.fit(X_train, y_train)
    confidence = clf.score(X_test, y_test)
    predictions = clf.predict(X_test)

    print('Prediction:', Counter(predictions))
    print('Accuracy', confidence)

    return confidence
