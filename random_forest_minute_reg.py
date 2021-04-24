#!/usr/bin/python
# RANDOM FOREST REGRESSOR FROM BITTREX 1MINUTE DATA
# SSchott 24.04.2021

import pandas as pd
import numpy as np
import os, sys, requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import matplotlib.pyplot as plt
from sklearn.metrics import matthews_corrcoef, confusion_matrix

r=requests.get('https://api.bittrex.com/v3/markets/ETH-USD/candles/TRADE/MINUTE_1/recent')
data = pd.DataFrame(r.json())

numeric = data.keys()[1:5]
data = data[numeric].astype(float)

n        = 60     # Use last n minutes
m        = n-1    
sma      = 20     # SMA interval

data_sma20 = data.rolling(window=sma).mean().add_suffix("_SMA20")
data_bol20 = data.rolling(window=sma).std().add_suffix("_STD")*2

data = pd.concat([data,data_sma20,data_bol20], axis=1) # Concatenate original data with SMA derived 

X = []
y = []

lag = 60

for i in range(sma,len(data)-n-lag+1, n-m):
    features = data[i:i+n].values
    X.append(features.flatten().astype(float))
    y.append(data[i+n:i+n+lag]["close_SMA20"].values)

X, y = np.array(X), np.array(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

print(X_train.shape,X_test.shape)

rf = RandomForestRegressor(n_estimators = 1000, random_state = 42)

rf.fit(X_train, y_train)

importances = rf.feature_importances_.reshape(n,-1)

print(np.sum(importances))
print(importances.shape)
print(importances.argmax(0),importances.argmax(1))

columns = enumerate(data.keys())
rows    = range(-n,0)

imp = []
for i, col in columns:
    for j, t in enumerate(rows):
        
        imp.append([col, t, importances[j,i]*100])

imp.sort(key=lambda x: x[2])
for i in imp:
    print(i)


predictions = rf.predict(X_test)

for p in predictions:
    plt.plot(p)

plt.savefig("predictions.png")
plt.close()

for p in predictions:
    plt.plot((p-p[0])/p[0])

plt.savefig("predictions_change.png")
plt.close()

diff      = (predictions-y_test)/y_test
diff_avg  = np.mean(diff, axis=0)
diff_sem  = np.std(diff, axis=0)

for d in diff:
    plt.plot(d)

plt.savefig("predictions_diff.png")
plt.close()
plt.fill_between(range(len(predictions[0])),diff_avg-diff_sem,diff_avg+diff_sem, alpha=0.3)
plt.plot(diff_avg)
plt.savefig("predictions_diffavg.png")
plt.close()
