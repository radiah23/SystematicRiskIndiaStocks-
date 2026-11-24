"""Shared settings for the whole pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
PRICES_FILE = DATA_DIR / "prices.csv"

# 19 NSE large caps, one row per stock, with the sector used for colouring and for
# checking how much of the network is within-sector.
STOCKS = {
    "HDFCBANK.NS": "Banks", "ICICIBANK.NS": "Banks", "SBIN.NS": "Banks", "KOTAKBANK.NS": "Banks",
    "TCS.NS": "IT", "INFY.NS": "IT", "WIPRO.NS": "IT", "HCLTECH.NS": "IT",
    "RELIANCE.NS": "Energy", "ONGC.NS": "Energy", "POWERGRID.NS": "Energy",
    "HINDUNILVR.NS": "FMCG", "ITC.NS": "FMCG", "NESTLEIND.NS": "FMCG",
    "SUNPHARMA.NS": "Pharma", "DRREDDY.NS": "Pharma", "CIPLA.NS": "Pharma",
    "BHARTIARTL.NS": "Telecom", "MARUTI.NS": "Autos",
}
# Banks the Reserve Bank of India designates as domestic systemically important (D-SIBs):
# SBI since 2015, ICICI Bank since 2016, HDFC Bank since 2017. Used as an outside benchmark.
DSIBS = ["SBIN.NS", "ICICIBANK.NS", "HDFCBANK.NS"]

MARKET = "^NSEI"  # NIFTY 50

# Price history. Starting in 2018 gives a two-year pre-COVID window for the out-of-sample test.
START, END = "2018-01-01", "2024-12-31"

# Main (full-sample) estimation window, as in the original project.
MAIN_START, MAIN_END = "2020-01-01", "2024-12-31"

# Pre-crisis window used to estimate every risk measure *before* the COVID crash,
# and the window searched for the NIFTY peak-to-trough crash.
PRE_START, PRE_END = "2018-01-01", "2019-12-31"
CRASH_SEARCH_START, CRASH_SEARCH_END = "2020-01-01", "2020-04-30"

CORR_THRESHOLD = 0.5      # edge kept when |rho| > threshold (raw returns)
RESID_THRESHOLD = 0.2     # same, for market-adjusted residuals, which are far less correlated
TAIL_Q = 0.05             # 5% tail for MES and CoVaR
VAR_LAGS = 1              # VAR order for the spillover model (BIC picks 1 for daily returns)
FEVD_HORIZON = 10         # forecast horizon (days) for the variance decomposition
ROLL_WINDOW = 250         # ~one trading year
ROLL_STEP = 5             # re-estimate weekly

# Dates marked on the rolling connectedness chart.
EVENTS = {
    "2020-03-23": "COVID crash low",
    "2023-01-24": "Hindenburg report on Adani",
    "2024-06-04": "Election result day",
}
