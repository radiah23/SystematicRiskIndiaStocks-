import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402


def synthetic_prices(seed: int = 0) -> pd.DataFrame:
    """Factor-model prices for the real tickers: market + sector factors + noise, with a
    sharp market crash in Feb-Mar 2020 so the crash window is detectable."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(config.START, config.END)
    n = len(dates)
    mkt = rng.normal(0.0004, 0.010, n)
    crash = (dates >= "2020-02-20") & (dates <= "2020-03-23")
    mkt[crash] -= 0.012
    rebound = (dates > "2020-03-23") & (dates <= "2020-05-15")
    mkt[rebound] += 0.012
    sectors = sorted(set(config.STOCKS.values()))
    sec_f = {s: rng.normal(0, 0.008, n) for s in sectors}
    cols = {}
    for i, (t, s) in enumerate(config.STOCKS.items()):
        beta = 0.6 + 0.05 * i
        r = beta * mkt + sec_f[s] + rng.normal(0, 0.009, n)
        cols[t] = 100 * np.exp(np.cumsum(r))
    cols[config.MARKET] = 10000 * np.exp(np.cumsum(mkt))
    return pd.DataFrame(cols, index=dates.rename("Date"))


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Point the pipeline at a temp folder holding synthetic prices."""
    data, res = tmp_path / "data", tmp_path / "results"
    data.mkdir()
    monkeypatch.setattr(config, "DATA_DIR", data)
    monkeypatch.setattr(config, "RESULTS_DIR", res)
    monkeypatch.setattr(config, "PRICES_FILE", data / "prices.csv")
    monkeypatch.setattr(config, "ROLL_STEP", 60)   # keep the test fast
    synthetic_prices().to_csv(data / "prices.csv")
    return tmp_path
