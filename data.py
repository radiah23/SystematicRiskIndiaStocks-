"""Download adjusted prices once and cache them, so every later step uses identical data.

Run:  python data.py            (use --refresh to re-download)
"""
import sys

import numpy as np
import pandas as pd

import config


def download_prices() -> pd.DataFrame:
    import yfinance as yf

    tickers = list(config.STOCKS) + [config.MARKET]
    # auto_adjust=True: prices adjusted for splits and dividends, so returns are total returns.
    raw = yf.download(tickers, start=config.START, end=config.END,
                      auto_adjust=True, progress=False)
    closes = raw["Close"][tickers]
    missing = [t for t in tickers if closes[t].dropna().empty]
    if missing:
        raise RuntimeError(f"No data returned for {missing}")
    return closes


def load_prices(refresh: bool = False) -> pd.DataFrame:
    if refresh or not config.PRICES_FILE.exists():
        config.DATA_DIR.mkdir(exist_ok=True)
        prices = download_prices()
        prices.to_csv(config.PRICES_FILE)
        print(f"Saved {prices.shape[0]} days x {prices.shape[1]} series to {config.PRICES_FILE}")
    return pd.read_csv(config.PRICES_FILE, index_col=0, parse_dates=True)


def log_returns(prices: pd.DataFrame, start=None, end=None) -> pd.DataFrame:
    """Daily log returns on days where every series traded (drops holidays / gaps jointly)."""
    p = prices.loc[start:end]
    return np.log(p).diff().dropna(how="any")


if __name__ == "__main__":
    px = load_prices(refresh="--refresh" in sys.argv)
    print(px.tail())
