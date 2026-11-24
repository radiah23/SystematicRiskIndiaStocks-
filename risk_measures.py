"""Standard market-based systemic-risk measures from the finance literature.

- CAPM beta with Newey-West standard errors (daily returns are autocorrelated and
  heteroskedastic, so plain OLS errors are too small).
- Marginal Expected Shortfall, MES (Acharya, Pedersen, Philippon & Richardson, 2017):
  a stock's average return on the market's worst q% of days. How much it loses when the
  market crashes.
- Delta-CoVaR (Adrian & Brunnermeier, 2016): how much the market's q-quantile return worsens
  when the stock moves from its median to its own q-quantile, from a quantile regression of the
  market on the stock. How much the stock's distress adds to market tail risk. This is the
  unconditional version (no macro state variables).
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm


def capm_beta(r: pd.Series, m: pd.Series, nw_lags: int = 5) -> tuple[float, float]:
    """Return (beta, Newey-West t-statistic)."""
    fit = sm.OLS(r.values, sm.add_constant(m.values)).fit(
        cov_type="HAC", cov_kwds={"maxlags": nw_lags})
    return float(fit.params[1]), float(fit.tvalues[1])


def mes(r: pd.Series, m: pd.Series, q: float = 0.05) -> float:
    """Average stock return on days the market is in its bottom q tail (negative = loses more)."""
    cutoff = m.quantile(q)
    return float(r[m <= cutoff].mean())


def delta_covar(r: pd.Series, m: pd.Series, q: float = 0.05) -> float:
    """Delta-CoVaR_q = gamma_q * (VaR_q(r) - median(r)), with gamma_q from the quantile
    regression m_t = alpha_q + gamma_q * r_t. More negative = the stock's distress drags the
    market tail further down."""
    X = sm.add_constant(r.values)
    gamma = sm.QuantReg(m.values, X).fit(q=q).params[1]
    return float(gamma * (r.quantile(q) - r.median()))


def risk_table(stock_rets: pd.DataFrame, mkt: pd.Series, q: float = 0.05) -> pd.DataFrame:
    rows = []
    for t in stock_rets.columns:
        r = stock_rets[t]
        b, bt = capm_beta(r, mkt)
        rows.append({
            "ticker": t,
            "beta": b,
            "beta_t_nw": bt,
            "mes": mes(r, mkt, q),
            "delta_covar": delta_covar(r, mkt, q),
            "ann_vol": float(r.std() * np.sqrt(252)),
        })
    return pd.DataFrame(rows).set_index("ticker")


def crash_window(market_prices: pd.Series, start, end) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Peak-to-trough dates of the market inside [start, end]: the trough is the lowest close,
    the peak is the highest close before it."""
    p = market_prices.loc[start:end].dropna()
    trough = p.idxmin()
    peak = p.loc[:trough].idxmax()
    return peak, trough


def crash_returns(prices: pd.DataFrame, peak, trough) -> pd.Series:
    """Simple cumulative return of each series from peak close to trough close."""
    return prices.loc[trough] / prices.loc[peak] - 1
