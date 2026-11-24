import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR

import risk_measures as rm
import spillover as sp


def test_gfevd_rows_sum_to_one_and_tci_in_range():
    rng = np.random.default_rng(1)
    X = pd.DataFrame(rng.normal(size=(800, 5)), columns=list("abcde"))
    theta, table, tci = sp.connectedness(X, 1, 10)
    assert np.allclose(theta.sum(axis=1), 1)
    assert 0 <= tci <= 100
    assert np.isclose(table["net"].sum(), 0, atol=1e-8)   # spillovers net to zero


def test_independent_series_have_low_connectedness():
    rng = np.random.default_rng(2)
    X = pd.DataFrame(rng.normal(size=(3000, 4)), columns=list("abcd"))
    _, _, tci = sp.connectedness(X, 1, 10)
    assert tci < 2


def test_leader_is_top_net_transmitter():
    """'a' drives everyone else with a one-day lag, so it must be the top net transmitter."""
    rng = np.random.default_rng(3)
    n = 3000
    e = rng.normal(size=(n, 4))
    X = np.zeros((n, 4))
    X[:, 0] = e[:, 0]
    for t in range(1, n):
        X[t, 1:] = 0.6 * X[t - 1, 0] + e[t, 1:]
    df = pd.DataFrame(X, columns=list("abcd"))
    _, table, _ = sp.connectedness(df, 1, 10)
    assert table["net"].idxmax() == "a"
    assert table.loc["a", "net"] > 0


def test_gfevd_matches_cholesky_when_shocks_uncorrelated():
    """With a diagonal residual covariance, the generalized and Cholesky FEVDs coincide."""
    rng = np.random.default_rng(4)
    n = 4000
    X = np.zeros((n, 3))
    for t in range(1, n):
        X[t] = np.array([[0.3, 0.2, 0], [0, 0.3, 0.2], [0.1, 0, 0.3]]) @ X[t - 1] + rng.normal(size=3)
    res = VAR(X).fit(1)
    sigma = np.diag(np.diag(res.sigma_u))
    ma = res.ma_rep(9)
    g = sp.generalized_fevd(ma, sigma)
    P = np.linalg.cholesky(sigma)
    orth = np.array([m @ P for m in ma])
    chol = (orth ** 2).sum(0)
    chol = chol / chol.sum(1, keepdims=True)
    assert np.allclose(g, chol, atol=1e-10)


def test_beta_mes_covar_on_known_model():
    rng = np.random.default_rng(5)
    m = pd.Series(rng.normal(0, 0.01, 20000))
    r = pd.Series(1.5 * m + rng.normal(0, 0.005, 20000))
    beta, t = rm.capm_beta(r, m)
    assert abs(beta - 1.5) < 0.02 and t > 50
    # MES = 1.5 * E[m | m <= q05] for this model
    expected = 1.5 * m[m <= m.quantile(0.05)].mean()
    assert np.isclose(rm.mes(r, m), expected, rtol=0.05)
    assert rm.delta_covar(r, m) < 0
    # an independent stock adds ~nothing to market tail risk
    z = pd.Series(rng.normal(0, 0.01, 20000))
    assert abs(rm.delta_covar(z, m)) < abs(rm.delta_covar(r, m)) / 5


def test_crash_window_finds_peak_before_trough():
    idx = pd.bdate_range("2020-01-01", "2020-04-30")
    p = pd.Series(100.0, index=idx)
    p["2020-01-20"] = 120
    p["2020-03-23"] = 60
    p["2020-04-20"] = 130          # recovery high after the trough must be ignored
    peak, trough = rm.crash_window(p, "2020-01-01", "2020-04-30")
    assert str(peak.date()) == "2020-01-20" and str(trough.date()) == "2020-03-23"
