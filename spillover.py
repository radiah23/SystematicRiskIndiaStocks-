"""Diebold-Yilmaz (2012, 2014) connectedness from a VAR's generalized variance decomposition.

Correlation is symmetric, so it cannot say who moves whom. Diebold-Yilmaz fits a VAR to all
19 return series and asks: of the H-day-ahead forecast error variance of stock i, what share
is due to shocks to stock j? That share, theta_ij, is a directed, weighted link j -> i.

  FROM_i = sum_{j != i} theta_ij     share of i's risk that comes from the others
  TO_j   = sum_{i != j} theta_ij     how much j's shocks explain the others
  NET_j  = TO_j - FROM_j             > 0: net transmitter of shocks, < 0: net receiver
  TCI    = mean_i FROM_i             total connectedness of the market, 0-100

The generalized decomposition (Koop, Pesaran & Potter 1996; Pesaran & Shin 1998) does not
depend on the ordering of the variables, unlike a Cholesky decomposition.
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR


def generalized_fevd(ma: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    """Row-normalized generalized FEVD.

    ma    : (H, k, k) moving-average matrices A_0 = I, A_1, ..., A_{H-1}
    sigma : (k, k) residual covariance
    returns theta (k, k) with rows summing to 1; theta[i, j] = share of i's variance from j.
    """
    # numerator_ij = sigma_jj^-1 * sum_h (e_i' A_h Sigma e_j)^2
    a_sig = ma @ sigma                                     # (H, k, k)
    num = (a_sig ** 2).sum(axis=0) / np.diag(sigma)[None, :]
    # denominator_i = sum_h e_i' A_h Sigma A_h' e_i
    den = np.einsum("hij,jk,hik->i", ma, sigma, ma)
    theta = num / den[:, None]
    return theta / theta.sum(axis=1, keepdims=True)


def fit_theta(returns: pd.DataFrame, lags: int, horizon: int) -> np.ndarray:
    res = VAR(returns.values * 100).fit(lags, trend="c")  # percent returns: numerically nicer
    return generalized_fevd(res.ma_rep(horizon - 1), np.asarray(res.sigma_u))


def connectedness(returns: pd.DataFrame, lags: int = 1, horizon: int = 10):
    """Returns (theta DataFrame, per-stock table with TO/FROM/NET, TCI)."""
    theta = fit_theta(returns, lags, horizon)
    k = theta.shape[0]
    off = theta - np.diag(np.diag(theta))
    table = pd.DataFrame({
        "from_others": off.sum(axis=1) * 100,
        "to_others": off.sum(axis=0) * 100,
    }, index=returns.columns)
    table["net"] = table["to_others"] - table["from_others"]
    tci = off.sum() / k * 100
    return pd.DataFrame(theta, index=returns.columns, columns=returns.columns), table, float(tci)


def spillover_edges(theta: pd.DataFrame, min_share: float = 0.0) -> pd.DataFrame:
    """Directed edges for PageRank: receiver i -> transmitter j with weight theta_ij.

    Pointing from receiver to transmitter (like a citation) makes PageRank reward the stocks
    whose shocks explain the variance of other important stocks."""
    rows = []
    for i in theta.index:
        for j in theta.columns:
            if i != j and theta.at[i, j] > min_share:
                rows.append((i, j, round(float(theta.at[i, j]), 8)))
    return pd.DataFrame(rows, columns=["source", "target", "weight"])


def rolling_tci(returns: pd.DataFrame, window: int, step: int, lags: int = 1,
                horizon: int = 10) -> pd.Series:
    """Total connectedness re-estimated on a rolling window; dated at each window's last day."""
    out = {}
    k = returns.shape[1]
    for end in range(window, len(returns) + 1, step):
        chunk = returns.iloc[end - window:end]
        theta = fit_theta(chunk, lags, horizon)
        out[chunk.index[-1]] = (theta.sum() - np.trace(theta)) / k * 100
    return pd.Series(out, name="tci")
