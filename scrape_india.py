import yfinance as yf
import pandas as pd
import numpy as np

#importing the stocks we want to see
tickers = [
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS",
    "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS",
    "RELIANCE.NS", "ONGC.NS", "POWERGRID.NS",
    "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS",
    "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS",
    "BHARTIARTL.NS","MARUTI.NS"
]
#downloading the 5 yrs of data
raw = yf.download(tickers, start="2020-01-01", end="2024-12-31")
closes = raw["Close"]

#computing the daily return and not having the nulls 
returns = closes.pct_change().dropna()

#this is to come up with the correlation between the stocks 
correlation_matrix = returns.corr()
print(correlation_matrix)

threshold = 0.5
#we want to collect the edges 
edges = []

for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        stock_a = correlation_matrix.columns[i]
        stock_b = correlation_matrix.columns[j]
        weight = correlation_matrix.iloc[i, j]
        if abs(weight) > threshold:
            edges.append((stock_a, stock_b, round(weight, 4)))

print(f"Total edges: {len(edges)}")
print(edges[:10])

import csv

with open("edges.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["stock_a", "stock_b", "weight"])
    for edge in edges:
        writer.writerow(edge)
