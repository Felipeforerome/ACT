import numpy as np
import pandas as pd
import pickle
from collections import Counter
from sklearn import svm, cross_validation, neighbors
from sklearn.ensemble import VotingClassifier, RandomForestClassifier

hm_tenmin = 6

def process_data_for_labels(ticker):
    df = pd.read_csv('joined_cindex.csv', index_col=0)
    tickers = df.columns.values.tolist()
    df.fillna(0, inplace=True)

    for i in range(1, hm_tenmin + 1):
        print(df[ticker].shift(-i))
        print(df[ticker])
        print(df[ticker].shift(-i) - df[ticker])
        df['{}_{}t'.format(ticker, i)] = (df[ticker].shift(-i) - df[ticker]) / df[ticker]

    df.fillna(0, inplace=True)
    print(tickers)
    print(df)
    return tickers, df


def buy_sell_hold(*args):
    cols = [c for c in args]
    requirement = 0.0025
    for col in cols:
        if col > requirement:
            return 1
        if col < -requirement:
            return -1
    return 0


def extract_featuressets(ticker):
    tickers, df = process_data_for_labels(ticker)

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
    X, y, df = extract_featuressets(ticker)

    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X,
                                                                         y,
                                                                         test_size=0.25)

    # clf = neighbors.KNeighborsClassifier()

    clf = VotingClassifier([('lsvc', svm.LinearSVC()),
                            ('knn', neighbors.KNeighborsClassifier()),
                            ('rfor', RandomForestClassifier())])

    clf.fit(X_train, y_train)
    confidence = clf.score(X_test, y_test)
    predictions = clf.predict(X_test)

    print('Prediction:', Counter(predictions))
    print('Accuracy', confidence)

    return confidence


