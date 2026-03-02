import json
import yfinance as yf
import pandas as pd
import numpy as np


with open("pagerank_results.json", "r") as f:
    pagerank_data = json.load(f)

pr_df = pd.DataFrame(pagerank_data)
print(pr_df)
# download nifty 50 as market benchmark
tickers = pr_df["ticker"].tolist()
tickers.append("^NSEI")  # nifty 50

raw = yf.download(tickers, start="2020-01-01", end="2024-12-31")
closes = raw["Close"]
returns = closes.pct_change().dropna()

# compute beta for each stock vs nifty
nifty_returns = returns["^NSEI"]
betas = {}

for ticker in pr_df["ticker"]:
    stock_returns = returns[ticker]
    covariance = np.cov(stock_returns, nifty_returns)[0][1]
    market_variance = np.var(nifty_returns)
    beta = covariance / market_variance
    betas[ticker] = round(beta, 4)

beta_df = pd.DataFrame(list(betas.items()), columns=["ticker", "beta"])

# merge pagerank and beta
merged = pr_df.merge(beta_df, on="ticker")
print(merged.sort_values("pagerank", ascending=False))

#The higher the pagrank score the higher the beta should be higher so we want to test that
#To test that we are going to perform regression

from scipy import stats

x = merged["pagerank"]
y = merged["beta"]

slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

print(f"Slope: {round(slope, 4)}")
print(f"R-squared: {round(r_value**2, 4)}")
print(f"P-value: {round(p_value, 4)}")

# Not significant. 